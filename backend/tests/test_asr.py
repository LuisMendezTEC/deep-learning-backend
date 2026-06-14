from fastapi.testclient import TestClient


def test_asr_returns_model_not_loaded_until_checkpoint_exists(client: TestClient, wav_audio_bytes: bytes) -> None:
    response = client.post(
        "/api/v1/asr/transcribe",
        files={"audio": ("sample.wav", wav_audio_bytes, "audio/wav")},
        data={"language": "es"},
    )

    assert response.status_code == 503
    assert response.json()["code"] == "MODEL_NOT_LOADED"


def test_asr_rejects_unsupported_language(client: TestClient) -> None:
    response = client.post(
        "/api/v1/asr/transcribe",
        files={"audio": ("sample.wav", b"not-a-real-audio", "audio/wav")},
        data={"language": "en"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_LANGUAGE"
