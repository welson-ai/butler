/**
 * What this file does: Fetches and manages real-time USDC balance updates
 * What it receives as input: Wallet address and contract interactions
 * What it returns as output: Current balances and balance update functions
 */

import { useState, useEffect } from 'react'
import { useReadContract } from 'wagmi'
import { BASE_SEPOLIA_USDC, USDC_ABI } from '../config/contracts'

const useBalance = (address) => {
  const [balances, setBalances] = useState({
    usdc: 0,
    aaveUsdc: 0,
    yieldEarned: 0
  })

  // TODO: Add Aave aUSDC contract read
  const { data: usdcBalance, error: usdcError } = useReadContract({
    address: BASE_SEPOLIA_USDC,
    abi: USDC_ABI,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    watch: true,
  })

  useEffect(() => {
    if (usdcBalance) {
      // Convert from wei to USDC (6 decimals)
      const formattedBalance = Number(usdcBalance) / 1e6
      setBalances(prev => ({
        ...prev,
        usdc: formattedBalance
      }))
    }
  }, [usdcBalance])

  const refreshBalances = () => {
    // TODO: Implement manual balance refresh
    console.log('Refreshing balances')
  }

  return {
    balances,
    usdcError,
    refreshBalances
  }
}

export default useBalance
