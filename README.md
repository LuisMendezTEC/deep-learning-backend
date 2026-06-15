# Modulo B - Backend FastAPI

Backend de inferencia para consumir los modelos entrenados por el Modulo A.

El frontend nunca llama directamente a los modelos. El flujo es:

1. El frontend envia una imagen o audio por HTTP.
2. FastAPI valida y recibe el archivo.
3. El backend aplica el mismo preprocesamiento usado en entrenamiento.
4. El modelo entrenado hace inferencia.
5. El backend convierte la salida a JSON para el frontend.

## Ejecutar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Endpoints

## Regla de JSON

El backend acepta campos en `snake_case` en todos los endpoints JSON. El frontend puede usar modelos en `camelCase`, pero antes de enviar la request debe mapearlos a `snake_case`.

Ejemplo:

```ts
const registerPayload = {
  first_name: user.firstName,
  last_name: user.lastName,
  email: user.email,
  password: user.password,
};
```

Si llega un campo como `firstName`, el backend responde `422 NON_SNAKE_CASE_FIELD` con el campo sugerido.

### Vision

`POST /api/v1/vision/segment`

Recibe `multipart/form-data`:

- `image`: imagen MRI en PNG, JPG o TIFF.

Usa solo el checkpoint indicado por la guia:

```text
data/models/cv/unet_efficientnetb4_best.pth
```

Preprocesamiento:

- escala de grises,
- resize `256 x 256`,
- normalizacion con `data/processed/lgg_mri/norm_stats.json`,
- tensor `[1, 1, 256, 256]`,
- sigmoid + umbral `0.5`.

Respuesta:

```json
{
  "has_tumor": true,
  "segmented_image": "<overlay png base64>",
  "mask": "<mask png base64>",
  "model": "unet_efficientnet-b4",
  "tumor_area_percentage": 4.73,
  "average_tumor_probability": 0.91,
  "latency_ms": 120.5
}
```

### ASR

`POST /api/v1/asr/transcribe`

Recibe `multipart/form-data`:

- `audio`: WAV, MP3, FLAC u OGG.

Usa:

```text
data/models/asr/ctc_bilstm_best.pth
data/models/asr/vocab.json
data/models/asr/idx2char.json
docs/asr_preprocessing_params.json
```

Preprocesamiento:

- waveform,
- mono,
- resample a 16 kHz,
- Mel Spectrogram,
- normalizacion por instancia,
- tensor `[1, n_mels, T]`,
- CTC greedy decode.

Respuesta:

```json
{
  "transcription": "texto reconocido",
  "normalized_transcription": "texto reconocido",
  "duration_s": 3.2,
  "latency_ms": 120,
  "confidence": 0.91,
  "model": "cnn_bilstm_ctc"
}
```

## Artefactos del Modulo A

Los `.pth` incluidos son placeholders vacios. El Modulo A debe reemplazarlos por checkpoints reales:

```text
data/models/cv/unet_efficientnetb4_best.pth
data/models/asr/ctc_bilstm_best.pth
```

Tambien debe confirmar o reemplazar:

```text
data/processed/lgg_mri/norm_stats.json
docs/asr_preprocessing_params.json
data/models/asr/vocab.json
data/models/asr/idx2char.json
```

Mientras falten artefactos reales, los endpoints devuelven `503 MODEL_NOT_LOADED`.

## Tests

```bash
pytest tests/ -v --tb=short
```
