from fastapi.testclient import TestClient


def test_asr_uses_expected_artifacts_and_returns_503_until_real_checkpoint_exists(
    client: TestClient,
    wav_audio_bytes: bytes,
) -> None:
    response = client.post(
        "/api/v1/asr/transcribe",
        files={"audio": ("sample.wav", wav_audio_bytes, "audio/wav")},
    )

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert body["code"] == "MODEL_NOT_LOADED"
    assert "ctc_bilstm_best.pth" in body["detail"]
