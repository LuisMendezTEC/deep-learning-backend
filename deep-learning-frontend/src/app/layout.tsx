import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { ThemeProvider } from '@/components/ui/ThemeProvider'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Deep Learning · TEC',
  description: 'Segmentación de tumores MRI y reconocimiento automático de voz con Deep Learning',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        {/* Prevent flash of wrong theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var t=localStorage.getItem('theme');if(t==='dark'||(t===null&&matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.classList.add('dark')}}catch(e){}`,
          }}
        />
      </head>
      <body className={`${inter.className} bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100 transition-colors duration-200`}>
        <ThemeProvider>
          <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/95">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#1E3A5F] text-xs font-bold text-white tracking-tight dark:bg-blue-700">
                  DL
                </div>
                <span className="text-sm font-semibold text-slate-800 tracking-tight dark:text-slate-100">
                  Deep Learning · TEC
                </span>
              </Link>
              <nav className="flex items-center gap-1">
                <Link
                  href="/vision"
                  className="rounded-lg px-3 py-1.5 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
                >
                  Vision
                </Link>
                <Link
                  href="/asr"
                  className="rounded-lg px-3 py-1.5 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
                >
                  ASR
                </Link>
                <div className="ml-2 border-l border-slate-200 pl-2 dark:border-slate-700">
                  <ThemeToggle />
                </div>
              </nav>
            </div>
          </header>

          <main className="min-h-screen">{children}</main>

          <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-400 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-600">
            Proyecto Programado II — Instituto Tecnológico de Costa Rica · 2026
          </footer>
        </ThemeProvider>
      </body>
    </html>
  )
}
