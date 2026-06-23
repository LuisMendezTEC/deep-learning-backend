'use client'

import { useState, useRef, useEffect } from 'react'

interface AudioRecorderProps {
  onAudioReady: (file: File) => void
  disabled?: boolean
}

const MAX_SIZE_MB      = 25
const MAX_DURATION_SEC = 30
const ACCEPTED_EXTENSIONS = '.wav,.mp3,.flac,.ogg'
const TARGET_SAMPLE_RATE  = 16_000

async function encodeWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer()
  const audioCtx = new AudioContext({ sampleRate: TARGET_SAMPLE_RATE })
  const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer)
  await audioCtx.close()

  const numFrames  = audioBuffer.length
  const wavBytes   = new ArrayBuffer(44 + numFrames * 2)
  const view       = new DataView(wavBytes)

  const writeStr = (offset: number, s: string) => {
    for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i))
  }

  writeStr(0,  'RIFF')
  view.setUint32(4,  36 + numFrames * 2, true)
  writeStr(8,  'WAVE')
  writeStr(12, 'fmt ')
  view.setUint32(16, 16,                    true)
  view.setUint16(20, 1,                     true)  // PCM
  view.setUint16(22, 1,                     true)  // mono
  view.setUint32(24, TARGET_SAMPLE_RATE,    true)
  view.setUint32(28, TARGET_SAMPLE_RATE * 2, true) // byte rate
  view.setUint16(32, 2,                     true)  // block align
  view.setUint16(34, 16,                    true)  // bits per sample
  writeStr(36, 'data')
  view.setUint32(40, numFrames * 2,         true)

  // Mix all channels to mono and quantize to 16-bit PCM
  const numCh   = audioBuffer.numberOfChannels
  const channels = Array.from({ length: numCh }, (_, i) => audioBuffer.getChannelData(i))
  const out      = new DataView(wavBytes, 44)
  for (let i = 0; i < numFrames; i++) {
    let sample = 0
    for (const ch of channels) sample += ch[i]
    sample = Math.max(-1, Math.min(1, sample / numCh))
    const pcm = sample < 0 ? sample * 0x8000 : sample * 0x7fff
    out.setInt16(i * 2, pcm, true)
  }

  return new Blob([wavBytes], { type: 'audio/wav' })
}

export default function AudioRecorder({ onAudioReady, disabled = false }: AudioRecorderProps) {
  const [mode, setMode]             = useState<'idle' | 'recording' | 'done'>('idle')
  const [elapsed, setElapsed]       = useState(0)
  const [fileName, setFileName]     = useState<string | null>(null)
  const [audioUrl, setAudioUrl]     = useState<string | null>(null)
  const [localError, setLocalError] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef        = useRef<Blob[]>([])
  const timerRef         = useRef<ReturnType<typeof setInterval> | null>(null)
  const elapsedRef       = useRef(0)
  const streamRef        = useRef<MediaStream | null>(null)
  const inputRef         = useRef<HTMLInputElement>(null)

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      streamRef.current?.getTracks().forEach((t) => t.stop())
    }
  }, [])

  const finishRecording = async (chunks: Blob[]) => {
    const mimeType = mediaRecorderRef.current?.mimeType ?? 'audio/webm'
    const raw = new Blob(chunks, { type: mimeType })
    try {
      const wav = await encodeWav(raw)
      const url = URL.createObjectURL(wav)
      const file = new File([wav], 'grabacion.wav', { type: 'audio/wav' })
      setAudioUrl(url); setFileName('grabacion.wav'); setMode('done')
      onAudioReady(file)
    } catch {
      setLocalError('No se pudo convertir la grabacion a WAV. Intenta subir un archivo directamente.')
      setMode('idle')
    }
  }

  const stopRecording = () => {
    if (timerRef.current) clearInterval(timerRef.current)
    mediaRecorderRef.current?.stop()
  }

  const startRecording = async () => {
    try {
      setLocalError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const mr = new MediaRecorder(stream)
      mediaRecorderRef.current = mr
      chunksRef.current = []
      elapsedRef.current = 0
      mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data) }
      mr.onstop = () => { streamRef.current?.getTracks().forEach((t) => t.stop()); void finishRecording(chunksRef.current) }
      mr.start()
      setElapsed(0); setMode('recording')
      timerRef.current = setInterval(() => {
        elapsedRef.current += 1
        setElapsed(elapsedRef.current)
        if (elapsedRef.current >= MAX_DURATION_SEC) { clearInterval(timerRef.current!); mr.stop() }
      }, 1000)
    } catch {
      setLocalError('No se pudo acceder al microfono. Verifica los permisos del navegador.')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalError(null)
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > MAX_SIZE_MB * 1024 * 1024) { setLocalError(`El archivo supera el limite de ${MAX_SIZE_MB} MB.`); return }
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    const url = URL.createObjectURL(file)
    setAudioUrl(url); setFileName(file.name); setMode('done')
    onAudioReady(file)
  }

  const reset = () => {
    if (timerRef.current) clearInterval(timerRef.current)
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    setMode('idle'); setElapsed(0); setFileName(null); setAudioUrl(null); setLocalError(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  const fmt = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  return (
    <div className="space-y-4">

      {mode === 'idle' && (
        <div className="space-y-3">
          <button
            onClick={startRecording}
            disabled={disabled}
            className="flex w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-8 text-slate-600 transition-colors hover:border-[#1E3A5F]/40 hover:bg-blue-50/40 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-600 dark:bg-slate-700/50 dark:text-slate-400 dark:hover:border-blue-600/40 dark:hover:bg-blue-900/10"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-600">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Grabar desde microfono</span>
            <span className="text-xs text-slate-400 dark:text-slate-500">Max. {MAX_DURATION_SEC} segundos</span>
          </button>

          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
            <span className="text-xs text-slate-400 dark:text-slate-500">o</span>
            <div className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
          </div>

          <button
            onClick={() => !disabled && inputRef.current?.click()}
            disabled={disabled}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-600 dark:bg-slate-700/50 dark:text-slate-400 dark:hover:border-slate-500 dark:hover:bg-slate-700"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>
            </svg>
            <span>Subir archivo de audio</span>
          </button>

          <input ref={inputRef} type="file" accept={ACCEPTED_EXTENSIONS} onChange={handleFileChange} disabled={disabled} className="hidden" />
          <p className="text-center text-xs text-slate-300 dark:text-slate-600">WAV · MP3 · FLAC · OGG — Max. 25 MB</p>
        </div>
      )}

      {mode === 'recording' && (
        <div className="flex flex-col items-center gap-4 rounded-xl border border-red-200 bg-red-50 p-8 dark:border-red-900/50 dark:bg-red-900/10">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-red-500" />
            <span className="text-sm font-medium text-red-700 dark:text-red-400">Grabando</span>
          </div>
          <p className="font-mono text-3xl font-semibold text-slate-800 dark:text-slate-100">{fmt(elapsed)}</p>
          <div className="w-full overflow-hidden rounded-full bg-red-100 h-1 dark:bg-red-900/30">
            <div className="h-1 rounded-full bg-red-500 transition-all duration-1000" style={{ width: `${(elapsed / MAX_DURATION_SEC) * 100}%` }} />
          </div>
          <button
            onClick={stopRecording}
            className="rounded-lg border border-red-300 bg-white px-6 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-50 dark:border-red-800 dark:bg-slate-800 dark:text-red-400 dark:hover:bg-red-900/20"
          >
            Detener grabacion
          </button>
        </div>
      )}

      {mode === 'done' && audioUrl && (
        <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-600 dark:bg-slate-700/50">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">{fileName}</p>
            <button onClick={reset} className="ml-3 shrink-0 text-xs text-slate-400 transition-colors hover:text-slate-700 dark:hover:text-slate-200">
              Cambiar
            </button>
          </div>
          <audio controls src={audioUrl} className="w-full" />
        </div>
      )}

      {localError && (
        <p className="text-center text-xs text-red-500 dark:text-red-400">{localError}</p>
      )}
    </div>
  )
}
