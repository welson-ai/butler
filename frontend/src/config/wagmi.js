/**
 * What this file does: Configures Wagmi and RainbowKit for Web3 wallet connections
 * What it receives as input: No direct inputs - exports configuration objects
 * What it returns as output: Wagmi and RainbowKit configuration for Base Sepolia
 */

import { baseSepolia } from 'wagmi/chains'
import { http, createConfig } from 'wagmi'
import { rainbowWallet, metaMaskWallet, coinbaseWallet } from 'wagmi/connectors'

export const projectId = process.env.VITE_WALLETCONNECT_PROJECT_ID || 'your-project-id'

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
  ],
})
