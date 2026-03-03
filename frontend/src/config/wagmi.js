import { baseSepolia } from 'wagmi/chains'
import { http, createConfig } from 'wagmi'
import { rainbowWallet, metaMaskWallet, coinbaseWallet, walletConnectWallet } from 'wagmi/connectors'

export const projectId = import.meta.env.VITE_WALLETCONNECT_PROJECT_ID || 'your-project-id'

export const config = createConfig({
  chains: [baseSepolia],
  transports: {
    [baseSepolia.id]: http(),
  },
  connectors: [
    rainbowWallet({
      projectId,
    }),
    metaMaskWallet(),
    coinbaseWallet({
      appName: 'Crypto Butler',
    }),
    walletConnectWallet({
      projectId,
    }),
  ],
})
