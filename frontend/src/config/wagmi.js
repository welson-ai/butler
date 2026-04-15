import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { base } from 'wagmi/chains'

export const config = getDefaultConfig({
  appName: 'Crypto Butler',
  projectId: import.meta.env.VITE_WALLETCONNECT_PROJECT_ID || 'demo',
  chains: [base],
  ssr: false
})
