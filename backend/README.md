# Modulo B - Backend FastAPI

Backend de inferencia para el proyecto **Deep Learning Backend**. Implementa solo el Modulo B de la guia: endpoints FastAPI, carga de modelos en `lifespan`, preprocesamiento de entrada, postprocesamiento y respuestas JSON compatibles con los contratos del documento.

## Estructura

```text
backend/
  app/
    api/routes/
      health.py
      vision.py
      asr.py
    core/
      config.py
      errors.py
      logging.py
    models/
      unet.py
      ctc_audio.py
    schemas/
      vision.py
      asr.py
      common.py
    services/
      vision_service.py
      audio_service.py
      metrics.py
    main.py
  data/models/
    cv/
    asr/
  tests/
```

## Contratos implementados

### Vision

`POST /api/v1/vision/segment`

Campos `multipart/form-data`:

- `image`: archivo PNG, JPG o TIFF. Maximo 10 MB.
- `backbone`: `resnet50` o `efficientnet-b4`. Default: `resnet50`.
- `overlay`: boolean. Default: `true`.

Respuesta exitosa:

```json
{
  "status": "success",
  "backbone": "resnet50",
  "inference_time_ms": 142.3,
  "metrics": {
    "iou": -1,
    "dice_score": -1
  },
  "mask_base64": "<png base64>",
  "overlay_base64": "<png base64>",
  "tumor_area_percentage": 4.73
}
```

El preprocesamiento usa escala de grises, resize `256x256`, normalizacion `(pixel / 255 - 0.5) / 0.5` y tensor `[1, 1, 256, 256]`.

### ASR

`POST /api/v1/asr/transcribe`

Campos `multipart/form-data`:

- `audio`: WAV, MP3, FLAC u OGG. Maximo 25 MB y 30 segundos.
- `reference`: texto de referencia opcional para WER/CER.
- `language`: solo `es`. Default: `es`.

El preprocesamiento usa mono, resample a `16000 Hz`, Mel Spectrogram con `n_mels=80`, `n_fft=400`, `hop_length=160` y normalizacion `(spec - mean) / (std + 1e-8)`.

## Artefactos requeridos del Modulo A

Colocar estos archivos cuando el equipo de datos los entregue:

```text
backend/data/models/cv/unet_resnet50_best.pth
backend/data/models/cv/unet_efficientnetb4_best.pth
backend/data/models/asr/ctc_bilstm_best.pth
backend/data/models/asr/vocab.json
```

Mientras falten, la app inicia correctamente y los endpoints devuelven `503 MODEL_NOT_LOADED`, respetando el contrato de errores.

## Instalacion

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ejecutar

```bash
uvicorn app.main:app --reload --port 8000
```

OpenAPI queda disponible en:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Comandos de prueba manual

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/gpu
```

```bash
curl -X POST http://localhost:8000/api/v1/vision/segment \
  -F 'image=@test_brain.png' \
  -F 'backbone=resnet50' \
  -F 'overlay=true'
```

```bash
curl -X POST http://localhost:8000/api/v1/asr/transcribe \
  -F 'audio=@test_audio.wav' \
  -F 'reference=el nino corre por el parque' \
  -F 'language=es'
```

## Tests

```bash
pytest tests/ -v --tb=short
```

