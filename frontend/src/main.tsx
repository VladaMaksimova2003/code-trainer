import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/toxic-pulse.css'
import App from '@/app/App'
import { QueryProvider } from '@/shared/providers/QueryProvider'
import { LanguagesBootstrap } from '@/shared/providers/LanguagesBootstrap'
import AppErrorBoundary from '@/shared/ui/AppErrorBoundary'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppErrorBoundary>
      <QueryProvider>
        <LanguagesBootstrap>
          <App />
        </LanguagesBootstrap>
      </QueryProvider>
    </AppErrorBoundary>
  </StrictMode>,
)
