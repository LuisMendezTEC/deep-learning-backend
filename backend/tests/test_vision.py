from fastapi.testclient import TestClient


def test_vision_returns_model_not_loaded_until_checkpoint_exists(
    client: TestClient,
    png_image_bytes: bytes,
) -> None:
    response = client.post(
        "/api/v1/vision/segment",
        files={"image": ("brain.png", png_image_bytes, "image/png")},
        data={"backbone": "resnet50", "overlay": "true"},
    )

    assert response.status_code == 503
    assert response.json()["code"] == "MODEL_NOT_LOADED"


def test_vision_rejects_unknown_backbone(client: TestClient, png_image_bytes: bytes) -> None:
    response = client.post(
        "/api/v1/vision/segment",
        files={"image": ("brain.png", png_image_bytes, "image/png")},
        data={"backbone": "mobilenet", "overlay": "true"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_BACKBONE"
