/**
 * What this file does: Main application component that orchestrates all UI elements
 * What it receives as input: Web3 provider and user interactions
 * What it returns as output: Complete Crypto Butler interface
 */

import React from 'react'
import { WagmiProvider } from 'wagmi'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RainbowKitProvider } from '@rainbow-me/rainbowkit'
import { config } from './config/wagmi'
import '@rainbow-me/rainbowkit/styles.css'

import WalletConnect from './components/WalletConnect'
import ChatInterface from './components/ChatInterface'
import ActivityFeed from './components/ActivityFeed'
import BalanceDisplay from './components/BalanceDisplay'
import TransactionLog from './components/TransactionLog'
import useWallet from './hooks/useWallet'
import useBalance from './hooks/useBalance'

const queryClient = new QueryClient()

function AppContent() {
  const { address, isConnected } = useWallet()
  const { balances } = useBalance(address)

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Crypto Butler</h1>
            <WalletConnect />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isConnected ? (
          <div className="text-center py-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to Crypto Butler
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Your autonomous DeFi wealth management agent
            </p>
            <p className="text-gray-500">
              Connect your wallet to get started
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <BalanceDisplay
                usdcBalance={balances.usdc}
                aaveDeposit={balances.aaveUsdc}
                yieldEarned={balances.yieldEarned}
              />
              <ChatInterface />
            </div>
            <div className="space-y-6">
              <ActivityFeed />
              <TransactionLog />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          <AppContent />
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  )
}

export default App
