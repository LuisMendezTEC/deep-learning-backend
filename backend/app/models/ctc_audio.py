import json
import logging
import time
from pathlib import Path

import torch
from torch import nn

logger = logging.getLogger(__name__)


class CTCNetwork(nn.Module):
    """CNN + BiLSTM CTC model matching the architecture required by Module A."""

    def __init__(self, n_mels: int, num_classes: int) -> None:
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv1d(n_mels, 256, kernel_size=5, padding=2),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(256, 256, kernel_size=5, padding=2),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm1d(512),
            nn.ReLU(),
        )
        self.rnn = nn.LSTM(
            input_size=512,
            hidden_size=512,
            num_layers=3,
            batch_first=True,
            bidirectional=True,
            dropout=0.2,
        )
        self.classifier = nn.Linear(1024, num_classes)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        x = self.cnn(features)
        x = x.transpose(1, 2)
        x, _ = self.rnn(x)
        return self.classifier(x)


class CTCInferenceModel:
    """Inference wrapper for Spanish ASR CTC checkpoints."""

    def __init__(self, checkpoint_path: Path, vocab_path: Path, device: str) -> None:
        self.checkpoint_path = checkpoint_path
        self.vocab_path = vocab_path
        self.device = torch.device(device)
        self.model: CTCNetwork | nn.Module | None = None
        self.index_to_char: dict[int, str] = {}
        self.load_error: str | None = None
        self._load()

    @property
    def is_loaded(self) -> bool:
        return self.model is not None and bool(self.index_to_char)

    def _load(self) -> None:
        missing = [str(path) for path in (self.checkpoint_path, self.vocab_path) if not path.exists()]
        if missing:
            self.load_error = "Missing model artifact(s): " + ", ".join(missing)
            logger.warning(self.load_error)
            return

        try:
            self.index_to_char = self._load_vocab()
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            if isinstance(checkpoint, nn.Module):
                model = checkpoint
            else:
                model = CTCNetwork(n_mels=80, num_classes=max(self.index_to_char.keys()) + 1)
                state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
                model.load_state_dict(state_dict)

            model.to(self.device)
            model.eval()
            self.model = model
            logger.info("Loaded ASR checkpoint from %s", self.checkpoint_path)
        except Exception as exc:  # noqa: BLE001
            self.load_error = str(exc)
            logger.exception("Failed loading ASR checkpoint %s", self.checkpoint_path)

    def _load_vocab(self) -> dict[int, str]:
        raw = json.loads(self.vocab_path.read_text(encoding="utf-8"))
        if "idx_to_char" in raw:
            raw_vocab = raw["idx_to_char"]
        elif "index_to_char" in raw:
            raw_vocab = raw["index_to_char"]
        else:
            raw_vocab = raw
        return {int(index): char for index, char in raw_vocab.items()}

    def predict(self, features: torch.Tensor) -> tuple[torch.Tensor, float]:
        if self.model is None:
            raise RuntimeError(self.load_error or "ASR model is not loaded.")

        started = time.perf_counter()
        with torch.no_grad():
            logits = self.model(features.to(self.device))
        inference_time_ms = (time.perf_counter() - started) * 1000
        return logits, inference_time_ms

    def greedy_decode(self, logits: torch.Tensor) -> tuple[str, float]:
        probabilities = torch.softmax(logits, dim=-1)
        token_probs, token_ids = torch.max(probabilities, dim=-1)
        token_ids = token_ids.squeeze(0).detach().cpu().tolist()
        token_probs = token_probs.squeeze(0).detach().cpu().tolist()

        chars: list[str] = []
        confidence_values: list[float] = []
        previous_id: int | None = None
        for token_id, token_prob in zip(token_ids, token_probs, strict=False):
            if token_id != 0 and token_id != previous_id:
                chars.append(self.index_to_char.get(token_id, ""))
                confidence_values.append(float(token_prob))
            previous_id = token_id

        confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        return "".join(chars).strip().lower(), round(confidence, 4)
