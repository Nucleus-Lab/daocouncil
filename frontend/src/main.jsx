import './polyfills'  // 必须在最前面导入
import React from 'react'
import { createRoot } from 'react-dom/client'
import { PrivyProvider } from '@privy-io/react-auth'
import './index.css'
import App from './App.jsx'

// Debug Privy configuration
const privyAppId = import.meta.env.VITE_PRIVY_APP_ID
console.log('Debug Privy Configuration:')
console.log('- App ID:', privyAppId)
console.log('- App ID type:', typeof privyAppId)
console.log('- App ID length:', privyAppId?.length)
console.log('- Raw env value:', process.env.VITE_PRIVY_APP_ID)
console.log('- All env variables:', import.meta.env)

// Validate app ID
if (!privyAppId) {
  console.error('Error: VITE_PRIVY_APP_ID is undefined')
} else if (typeof privyAppId !== 'string') {
  console.error('Error: VITE_PRIVY_APP_ID is not a string')
} else if (privyAppId.includes('"') || privyAppId.includes("'")) {
  console.error('Error: VITE_PRIVY_APP_ID contains quotes - please remove them')
}

const root = createRoot(document.getElementById('root'))

root.render(
  <React.StrictMode>
    <PrivyProvider 
      appId={privyAppId}
      config={{
        loginMethods: ['wallet', 'email', 'google'],
        embeddedWallets: {
          ethereum: {
            createOnLogin: 'users-without-wallets'
          }
        }
      }}
    >
      <App />
    </PrivyProvider>
  </React.StrictMode>
)
