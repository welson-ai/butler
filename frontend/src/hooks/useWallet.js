/**
 * What this file does: Manages wallet connection and state
 * What it receives as input: Wagmi hooks and wallet events
 * What it returns as output: Wallet connection state and management functions
 */

import { useAccount, useConnect, useDisconnect } from 'wagmi'

const useWallet = () => {
  const { address, isConnected, chain } = useAccount()
  const { connect, connectors, error: connectError } = useConnect()
  const { disconnect } = useDisconnect()

  const connectWallet = (connector) => {
    connect({ connector })
  }

  const disconnectWallet = () => {
    disconnect()
  }

  const getWalletInfo = () => {
    if (!isConnected || !address) return null
    
    return {
      address,
      truncatedAddress: `${address.slice(0, 6)}...${address.slice(-4)}`,
      chainId: chain?.id,
      chainName: chain?.name
    }
  }

  return {
    address,
    isConnected,
    chain,
    connectors,
    connectWallet,
    disconnectWallet,
    getWalletInfo,
    connectError
  }
}

export default useWallet
