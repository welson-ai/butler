import React, { useState, useEffect } from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount, useWriteContract } from 'wagmi'
import { parseUnits } from 'viem'
import axios from 'axios'

const API_BASE = 'http://localhost:5001'
const VAULT_ADDRESS = import.meta.env.VITE_BUTLER_VAULT_ADDRESS
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'

const VAULT_ABI = [
  {
    name: 'deposit',
    type: 'function',
    inputs: [{ name: 'amount', type: 'uint256' }],
    outputs: [],
    stateMutability: 'nonpayable'
  },
  {
    name: 'emergencyWithdraw',
    type: 'function',
    inputs: [],
    outputs: [],
    stateMutability: 'nonpayable'
  }
]

const ERC20_ABI = [
  {
    name: 'approve',
    type: 'function',
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' }
    ],
    outputs: [{ name: '', type: 'bool' }],
    stateMutability: 'nonpayable'
  }
]

export default function App() {
  const { address: connectedAddress, isConnected } = useAccount()
  const { writeContractAsync } = useWriteContract()
  
  // State variables
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [currentPlan, setCurrentPlan] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [vaultBalance, setVaultBalance] = useState(null)
  const [yields, setYields] = useState({})
  const [yieldStatus, setYieldStatus] = useState(null)
  const [sessionYield, setSessionYield] = useState(0)
  const [isWithdrawing, setIsWithdrawing] = useState(false)
  const [activity, setActivity] = useState([])

  // Initialize chat with Butler greeting
  useEffect(() => {
    if (isConnected) {
      setMessages([{
        role: 'butler',
        content: 'Hello! I am your Crypto Butler. Tell me how you would like to manage your USDC.',
        time: new Date().toISOString()
      }])
    }
  }, [isConnected])

  // Fetch vault balance
  const fetchBalance = async () => {
    if (!connectedAddress) return
    try {
      const response = await axios.get(`${API_BASE}/api/balance/${connectedAddress}`)
      setVaultBalance(response.data)
    } catch (error) {
      console.error('Error fetching balance:', error)
    }
  }

  // Fetch activity feed
  const fetchActivity = async () => {
    if (!connectedAddress) return
    try {
      const response = await axios.get(`${API_BASE}/api/activity/${connectedAddress}`)
      setActivity(response.data.transactions || [])
    } catch (error) {
      console.error('Error fetching activity:', error)
    }
  }

  // Fetch yields
  const fetchYields = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/yields`)
      setYields(response.data)
    } catch (error) {
      console.error('Error fetching yields:', error)
    }
  }

  // Fetch yield status
  const fetchYieldStatus = async () => {
    if (!connectedAddress) return
    try {
      const response = await axios.get(`${API_BASE}/api/yield-status/${connectedAddress}`)
      setYieldStatus(response.data)
    } catch (error) {
      console.error('Error fetching yield status:', error)
    }
  }

  // Set up intervals for data fetching
  useEffect(() => {
    if (!isConnected) return

    fetchBalance()
    fetchActivity()
    fetchYields()
    fetchYieldStatus()

    const balanceInterval = setInterval(fetchBalance, 30000)
    const activityInterval = setInterval(fetchActivity, 5000)
    const yieldsInterval = setInterval(fetchYields, 30000)
    const yieldStatusInterval = setInterval(fetchYieldStatus, 10000)

    return () => {
      clearInterval(balanceInterval)
      clearInterval(activityInterval)
      clearInterval(yieldsInterval)
      clearInterval(yieldStatusInterval)
    }
  }, [isConnected, connectedAddress])

  // Session yield ticker
  useEffect(() => {
    if (!yieldStatus?.per_second) return
    const interval = setInterval(() => {
      setSessionYield(prev => prev + yieldStatus.per_second)
    }, 1000)
    return () => clearInterval(interval)
  }, [yieldStatus?.per_second])

  // Send message to Butler
  const sendMessage = async () => {
    if (!inputMessage.trim() || !connectedAddress) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    
    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      time: new Date().toISOString()
    }])

    try {
      // Check vault balance first
      const balanceRes = await axios.get(`${API_BASE}/api/balance/${connectedAddress}`)
      const vaultBalance = balanceRes.data?.vault_balance || 0

      const response = await axios.post(`${API_BASE}/api/chat`, {
        wallet_address: connectedAddress,
        message: userMessage
      })

      const plan = response.data.plan
      const reply = response.data.reply
      const action = response.data.action

      // Extract the correct message content - handle both old and new response formats
      let messageContent = reply || response.data.message || 'I understand your request. Let me process that for you.'
      
      // Handle structured action responses (new format)
      if (response.data.action) {
        // Add action confirmation button
        setMessages(prev => [...prev, {
          role: 'butler',
          content: messageContent,
          action: response.data.action,
          time: new Date().toISOString(),
          hasAction: true
        }])
        
        // Auto-trigger MetaMask for deposit actions
        if (response.data.action.type === 'deposit_yield') {
          setTimeout(() => {
            executeDepositAction(response.data.action)
          }, 1000) // Delay 1 second to show message first
        }
      } else if (response.data.message && response.data.message.includes('Please approve deposit')) {
        // Handle wallet approval response from backend
        const walletAction = {
          type: 'deposit',
          amount: extractAmountFromMessage(response.data.message),
          protocol: 'Aave',
          apy: 6.2
        }
        
        setTimeout(() => {
          executeDepositAction(walletAction)
        }, 1000)
      } else {
        // Regular text response (old format)
        setMessages(prev => [...prev, {
          role: 'butler',
          content: messageContent,
          time: new Date().toISOString()
        }])
      }

      if (plan) {
        // Check if vault already has enough
        if (vaultBalance >= plan.usdc_total) {
          setMessages(prev => [...prev, {
            role: 'butler',
            content: `✅ I can see ${vaultBalance} USDC already in your vault. Activating your plan now without a new deposit.`,
            time: new Date().toISOString()
          }])
          setCurrentPlan({ ...plan, already_funded: true })
        } else {
          setCurrentPlan(plan)
        }
      }

      fetchBalance()
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, {
        role: 'butler',
        content: 'Sorry something went wrong. Please try again.',
        time: new Date().toISOString()
      }])
    }
  }

  // Activate Butler
  const activateButler = async (plan) => {
    try {
      setIsLoading(true)

      if (!plan.already_funded) {
        const amount = parseUnits(plan.usdc_total.toString(), 6)

        // Approve USDC
        await writeContractAsync({
          address: USDC_ADDRESS,
          abi: ERC20_ABI,
          functionName: 'approve',
          args: [VAULT_ADDRESS, amount]
        })

        // Deposit into vault
        await writeContractAsync({
          address: VAULT_ADDRESS,
          abi: VAULT_ABI,
          functionName: 'deposit',
          args: [amount]
        })
      }

      setCurrentPlan(null)
      fetchBalance()
    } catch (error) {
      console.error('Activation error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Emergency withdraw
  const emergencyWithdraw = async () => {
    if (!confirm('Withdraw all funds from vault back to your wallet?')) return
    try {
      setIsWithdrawing(true)
      await writeContractAsync({
        address: VAULT_ADDRESS,
        abi: VAULT_ABI,
        functionName: 'emergencyWithdraw'
      })
      fetchBalance()
    } catch (error) {
      console.error('Withdraw error:', error)
    } finally {
      setIsWithdrawing(false)
    }
  }

  const formatAddress = (addr) => {
    if (!addr) return ''
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }

  const formatTime = (time) => {
    return new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  // Extract amount from Butler message
  const extractAmountFromMessage = (message) => {
    const match = message.match(/(\d+\.?\d*)\s*USDC/i)
    return match ? parseFloat(match[1]) : 0.1
  }

  // Execute deposit action via MetaMask
  const executeDepositAction = async (action) => {
    try {
      console.log('🔥 Executing deposit action:', action)
      
      const amount = parseUnits(action.amount.toString(), 6)
      console.log('🔥 Amount parsed:', amount.toString())
      
      // Add processing message
      setMessages(prev => [...prev, {
        role: 'butler',
        content: `🔄 Processing deposit of ${action.amount} USDC to ${action.protocol}...`,
        time: new Date().toISOString()
      }])
      
      // Approve USDC first
      console.log('🔥 Approving USDC...')
      const approveTx = await writeContractAsync({
        address: USDC_ADDRESS,
        abi: ERC20_ABI,
        functionName: 'approve',
        args: [VAULT_ADDRESS, amount]
      })
      console.log('🔥 USDC approved:', approveTx)
      
      // Then deposit to vault
      console.log('🔥 Depositing to vault...')
      const depositTx = await writeContractAsync({
        address: VAULT_ADDRESS,
        abi: VAULT_ABI,
        functionName: 'deposit',
        args: [amount]
      })
      console.log('🔥 Vault deposited:', depositTx)
      
      // Success message
      setMessages(prev => [...prev, {
        role: 'butler',
        content: `✅ Done! ${action.amount} USDC is now earning ${action.apy}% APY in ${action.protocol}`,
        time: new Date().toISOString()
      }])
      
      // Refresh balance
      fetchBalance()
      
    } catch (error) {
      console.error('🔥 Deposit error:', error)
      setMessages(prev => [...prev, {
        role: 'butler',
        content: '❌ Transaction failed or rejected. Try again.',
        time: new Date().toISOString()
      }])
    }
  }

  // Handle action confirmation
  const handleActionConfirmation = async (action) => {
    try {
      console.log('🔥 Action confirmation triggered with action:', action)
      setIsLoading(true)
      
      const response = await axios.post(`${API_BASE}/api/execute-action`, {
        wallet_address: connectedAddress,
        action: action
      })

      console.log('🔥 Backend response:', response.data)
      console.log('🔥 Requires wallet approval:', response.data.requires_wallet_approval)

      if (response.data.requires_wallet_approval) {
        console.log('🔥 Processing wallet approval...')
        // Show wallet approval message
        setMessages(prev => [...prev, {
          role: 'butler',
          content: response.data.message,
          time: new Date().toISOString(),
          walletAction: response.data.wallet_action,
          requiresWalletApproval: true
        }])
        
        // Trigger MetaMask transaction
        console.log('🔥 About to execute wallet action:', response.data.wallet_action)
        await executeWalletAction(response.data.wallet_action)
      } else if (response.data.status === 'action_executed') {
        // Success message (for non-wallet actions)
        setMessages(prev => [...prev, {
          role: 'butler',
          content: `Success! ${response.data.message}`,
          time: new Date().toISOString()
        }])
        
        // Refresh balance
        fetchBalance()
      } else {
        // Error message
        setMessages(prev => [...prev, {
          role: 'butler',
          content: `Error: ${response.data.message}`,
          time: new Date().toISOString()
        }])
      }
    } catch (error) {
      console.error('Action execution error:', error)
      setMessages(prev => [...prev, {
        role: 'butler',
        content: 'Sorry, something went wrong executing the action.',
        time: new Date().toISOString()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Execute wallet action via MetaMask
  const executeWalletAction = async (walletAction) => {
    try {
      console.log('🔥 Executing wallet action:', walletAction)
      console.log('🔥 Connected address:', connectedAddress)
      console.log('🔥 USDC Address:', USDC_ADDRESS)
      console.log('🔥 Vault Address:', VAULT_ADDRESS)
      
      const amount = parseUnits(walletAction.amount.toString(), 6)
      console.log('🔥 Parsed amount:', amount.toString())
      
      if (walletAction.type === 'deposit') {
        console.log('🔥 Starting USDC approval...')
        
        // Approve USDC
        const approveTx = await writeContractAsync({
          address: USDC_ADDRESS,
          abi: ERC20_ABI,
          functionName: 'approve',
          args: [VAULT_ADDRESS, amount]
        })
        console.log('🔥 USDC approved:', approveTx)
        
        // Deposit into vault
        console.log('🔥 Starting vault deposit...')
        const txHash = await writeContractAsync({
          address: VAULT_ADDRESS,
          abi: VAULT_ABI,
          functionName: 'deposit',
          args: [amount]
        })
        console.log('🔥 Vault deposited:', txHash)
        
        // Success message
        setMessages(prev => [...prev, {
          role: 'butler',
          content: `Success! Deposited ${walletAction.amount} USDC to ${walletAction.protocol}. Transaction: ${txHash}`,
          time: new Date().toISOString()
        }])
        
        fetchBalance()
      } else if (walletAction.type === 'withdraw') {
        // Withdraw from vault
        const txHash = await writeContractAsync({
          address: VAULT_ADDRESS,
          abi: VAULT_ABI,
          functionName: 'emergencyWithdraw'
        })
        
        // Success message
        setMessages(prev => [...prev, {
          role: 'butler',
          content: `Success! Withdrew ${walletAction.amount} USDC from ${walletAction.protocol}. Transaction: ${txHash}`,
          time: new Date().toISOString()
        }])
        
        fetchBalance()
      }
    } catch (error) {
      console.error('Wallet action error:', error)
      setMessages(prev => [...prev, {
        role: 'butler',
        content: `Error executing wallet action: ${error.message}`,
        time: new Date().toISOString()
      }])
    }
  }

  // Get action button text based on action type
  const getActionButtonText = (action) => {
    switch (action.type) {
      case 'deposit_yield':
        return `Deposit ${action.amount} USDC to ${action.protocol}`
      case 'withdraw':
        return `Withdraw ${action.amount} USDC from ${action.protocol}`
      case 'send_payment':
        return `Send ${action.amount} USDC`
      default:
        return 'Confirm Action'
    }
  }

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">CRYPTO BUTLER</h1>
          <p className="text-gray-400 mb-8">Powered by x402 on Base</p>
          <div className="bg-[#12121a] p-8 rounded-2xl">
            <p className="text-gray-300 mb-6">Connect your wallet to get started</p>
            <ConnectButton />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="flex h-screen">
        {/* LEFT PANEL */}
        <div className="w-1/3 border-r border-gray-800 p-6 flex flex-col">
          {/* RainbowKit ConnectButton */}
          <div className="mb-6">
            <ConnectButton />
          </div>

          {/* Connected wallet address */}
          {connectedAddress && (
            <div className="bg-[#12121a] p-4 rounded-xl mb-4">
              <p className="text-gray-400 text-sm mb-1">Connected Wallet</p>
              <p className="text-sm font-mono text-white">{formatAddress(connectedAddress)}</p>
            </div>
          )}

          {/* Balance cards */}
          {vaultBalance && (
            <div className="space-y-3 flex-1">
              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Wallet USDC</p>
                <p className="text-2xl font-bold">${vaultBalance.usdc_balance?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Vault Balance</p>
                <p className="text-xl font-semibold text-blue-400">${vaultBalance.vault_balance?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Aave Deposit</p>
                <p className="text-xl font-semibold text-green-400">${vaultBalance.aave_deposit?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Payment Reserve</p>
                <p className="text-xl font-semibold text-purple-400">${vaultBalance.payment_reserve?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          )}

          {/* Emergency withdraw button */}
          <div className="mt-6">
            <button
              onClick={emergencyWithdraw}
              disabled={isWithdrawing}
              style={{
                background: 'transparent',
                border: '1px solid #ef4444',
                color: '#ef4444',
                padding: '10px',
                borderRadius: '8px',
                cursor: 'pointer',
                width: '100%',
                fontSize: '13px'
              }}
            >
              {isWithdrawing ? '⏳ Withdrawing...' : '🚨 Emergency Withdraw All'}
            </button>
          </div>
        </div>

        {/* CENTER PANEL */}
        <div className="w-1/3 border-r border-gray-800 flex flex-col">
          {/* Butler avatar and title */}
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed] rounded-full flex items-center justify-center">
                🤵
              </div>
              <h2 className="text-lg font-semibold">CRYPTO BUTLER</h2>
            </div>
          </div>

          {/* Chat messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-[#7c3aed] text-white' 
                    : 'bg-[#1e1e2a] text-gray-200'
                }`}>
                  <p className="text-sm">{typeof msg.content === 'object' 
  ? msg.content.message || msg.content.reply || JSON.stringify(msg.content)
  : msg.content}</p>
                  
                  {/* Action confirmation button */}
                  {msg.hasAction && msg.action && (
                    <div className="mt-3 pt-3 border-t border-gray-600">
                      <button
                        onClick={() => handleActionConfirmation(msg.action)}
                        className="bg-[#7c3aed] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#6d28d9] transition-colors"
                      >
                        {getActionButtonText(msg.action)}
                      </button>
                    </div>
                  )}
                  
                  <p className="text-xs opacity-70 mt-1">{formatTime(msg.time)}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Text input and send button */}
          <div className="p-4 border-t border-gray-800">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                className="flex-1 bg-[#12121a] text-white px-4 py-3 rounded-xl border border-gray-700 focus:border-[#7c3aed] focus:outline-none"
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || !connectedAddress}
                className="bg-[#7c3aed] text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#6d28d9] transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="w-1/3 p-6 flex flex-col overflow-y-auto">
          {/* Live Activity feed */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">Live Activity</h2>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {activity.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No activity yet</p>
              ) : (
                activity.map((item, index) => (
                  <div key={index} className="bg-[#12121a] p-3 rounded-xl">
                    <div className="flex items-start gap-3">
                      <span className="text-lg">📄</span>
                      <div className="flex-1">
                        <p className="text-sm text-gray-300">{item.tx_type}: ${item.amount}</p>
                        <p className="text-xs text-gray-500">{formatTime(item.timestamp)}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Current yields */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">Current Yields</h2>
            <div className="space-y-2">
              {Object.entries(yields).map(([protocol, apy]) => (
                <div key={protocol} className="bg-[#12121a] p-3 rounded-lg flex justify-between items-center">
                  <span className="text-gray-400 capitalize">{protocol}</span>
                  <span className="text-green-400 font-bold">{parseFloat(apy).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Yield status */}
          {yieldStatus && (
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-4">Yield Status</h2>
              <div className="bg-[#12121a] p-4 rounded-xl">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Protocol</span>
                  <span className="text-white capitalize">{yieldStatus.protocol}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">APY</span>
                  <span className="text-green-400">{yieldStatus.apy}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Deployed</span>
                  <span className="text-white">${yieldStatus.deployed_capital}</span>
                </div>
              </div>
            </div>
          )}

          {/* Session yield ticker */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">Session Yield</h2>
            <div className="bg-[#12121a] p-4 rounded-xl text-center">
              <div className="text-gray-400 text-sm mb-2">Projected Yield (since activation)</div>
              <div className="text-green-400 text-2xl font-bold">
                +{sessionYield.toFixed(8)} USDC
              </div>
              <div className="text-gray-500 text-xs mt-2">
                Based on {yieldStatus?.apy}% APY — updates on compound
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* MODAL POPUP */}
      {currentPlan && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#12121a',
            border: '1px solid #7c3aed',
            borderRadius: '20px',
            padding: '32px',
            maxWidth: '420px',
            width: '90%',
            boxShadow: '0 0 60px rgba(124,58,237,0.3)'
          }}>
            <div style={{textAlign: 'center', marginBottom: '24px'}}>
              <div style={{fontSize: '40px', marginBottom: '8px'}}>🤵</div>
              <div style={{color: 'white', fontSize: '20px', fontWeight: 'bold'}}>
                Butler Activation
              </div>
              <div style={{color: '#9ca3af', fontSize: '14px', marginTop: '4px'}}>
                Review your plan before activating
              </div>
            </div>

            <div style={{
              background: '#0a0a0f',
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '20px'
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                <span style={{color: '#9ca3af'}}>Total USDC</span>
                <span style={{color: 'white', fontWeight: 'bold'}}>{currentPlan.usdc_total} USDC</span>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                <span style={{color: '#9ca3af'}}>📈 Earning Yield</span>
                <span style={{color: '#22c55e', fontWeight: 'bold'}}>{currentPlan.aave_deposit} USDC</span>
              </div>
              {currentPlan.payment_reserve > 0 && (
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                  <span style={{color: '#9ca3af'}}>💸 Payment Reserve</span>
                  <span style={{color: '#3b82f6', fontWeight: 'bold'}}>{currentPlan.payment_reserve} USDC</span>
                </div>
              )}
              {currentPlan.buffer > 0 && (
                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span style={{color: '#9ca3af'}}>🛡️ Safety Buffer</span>
                  <span style={{color: '#f59e0b', fontWeight: 'bold'}}>{currentPlan.buffer} USDC</span>
                </div>
              )}
            </div>

            <div style={{
              background: '#0d1f0d',
              border: '1px solid #22c55e33',
              borderRadius: '8px',
              padding: '10px 14px',
              marginBottom: '20px',
              fontSize: '12px',
              color: '#9ca3af'
            }}>
              ✅ Two MetaMask confirmations required — approve USDC then deposit into vault. One time only.
            </div>

            <div style={{display: 'flex', gap: '12px'}}>
              <button
                onClick={() => setCurrentPlan(null)}
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: '1px solid #4b5563',
                  color: '#9ca3af',
                  padding: '14px',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '15px'
                }}
              >
                ✕ Cancel
              </button>
              <button
                onClick={() => activateButler(currentPlan)}
                disabled={isLoading}
                style={{
                  flex: 2,
                  background: isLoading ? '#4b5563' : 'linear-gradient(135deg, #7c3aed, #6d28d9)',
                  color: 'white',
                  padding: '14px',
                  borderRadius: '10px',
                  border: 'none',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '15px'
                }}
              >
                {isLoading ? '⏳ Processing...' : '✅ Yes — Activate Butler'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
