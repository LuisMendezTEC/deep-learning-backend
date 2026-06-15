from fastapi.testclient import TestClient


def test_vision_uses_expected_model_artifact_and_returns_503_until_real_checkpoint_exists(
    client: TestClient,
    png_image_bytes: bytes,
) -> None:
    response = client.post(
        "/api/v1/vision/segment",
        files={"image": ("brain.png", png_image_bytes, "image/png")},
    )

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert body["code"] == "MODEL_NOT_LOADED"
    assert "unet_efficientnetb4_best.pth" in body["detail"]
