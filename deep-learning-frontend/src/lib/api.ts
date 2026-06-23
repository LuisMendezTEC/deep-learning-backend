import type { VisionResponse, BackboneType } from '@/types/vision'
import type { ASRResponse } from '@/types/asr'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export class APIError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly httpStatus: number,
  ) {
    super(message)
    this.name = 'APIError'
  }
}

export async function segmentImage(
  file: File,
  backbone: BackboneType = 'resnet50',
  overlay = true,
): Promise<VisionResponse> {
  const formData = new FormData()
  formData.append('image', file)
  formData.append('backbone', backbone)
  formData.append('overlay', String(overlay))

  const res = await fetch(`${API_URL}/api/v1/vision/segment`, {
    method: 'POST',
    body: formData,
  })

  const data = await res.json()

  if (!res.ok) {
    throw new APIError(
      data.code ?? 'UNKNOWN_ERROR',
      data.message ?? 'Error desconocido al procesar la imagen.',
      res.status,
    )
  }

  return data as VisionResponse
}

export async function transcribeAudio(
  audio: File,
  reference?: string,
  language = 'es',
): Promise<ASRResponse> {
  const formData = new FormData()
  formData.append('audio', audio)
  if (reference) formData.append('reference', reference)
  formData.append('language', language)

  const res = await fetch(`${API_URL}/api/v1/asr/transcribe`, {
    method: 'POST',
    body: formData,
  })

  const data = await res.json()

  if (!res.ok) {
    throw new APIError(
      data.code ?? 'UNKNOWN_ERROR',
      data.message ?? 'Error desconocido al transcribir el audio.',
      res.status,
    )
  }

  return data as ASRResponse
}
