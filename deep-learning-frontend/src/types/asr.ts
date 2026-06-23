export interface ASRResponse {
  transcription: string
  normalized_transcription: string
  duration_s: number
  latency_ms: number
  confidence: number
  model: string
}

export interface ASRError {
  status: 'error'
  code: string
  message: string
  detail: string | null
}
