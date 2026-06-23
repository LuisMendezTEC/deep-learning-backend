export type BackboneType = 'resnet50' | 'efficientnet-b4'

export interface VisionResponse {
  has_tumor: boolean
  segmented_image: string
  mask: string
  model: string
  tumor_area_percentage: number
  average_tumor_probability: number
  latency_ms: number
}

export interface VisionError {
  status: 'error'
  code: string
  message: string
  detail: string | null
}
