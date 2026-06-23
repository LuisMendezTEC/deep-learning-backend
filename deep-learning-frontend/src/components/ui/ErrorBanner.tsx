'use client'

import { APIError } from '@/lib/api'

interface ErrorBannerProps {
  error: Error | null
  onDismiss?: () => void
}

export default function ErrorBanner({ error, onDismiss }: ErrorBannerProps) {
  if (!error) return null

  const code   = error instanceof APIError ? error.code : 'ERROR'
  const status = error instanceof APIError ? ` · HTTP ${error.httpStatus}` : ''

  return (
    <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900/50 dark:bg-red-900/10">
      <svg className="mt-0.5 shrink-0 text-red-500 dark:text-red-400" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>
      </svg>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-red-700 dark:text-red-400">
          {code}<span className="font-normal text-red-400 dark:text-red-600">{status}</span>
        </p>
        <p className="mt-0.5 text-sm text-red-600/80 dark:text-red-400/70">{error.message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 text-red-400 transition-colors hover:text-red-600 dark:text-red-600 dark:hover:text-red-400" aria-label="Cerrar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6 6 18M6 6l12 12"/>
          </svg>
        </button>
      )}
    </div>
  )
}
