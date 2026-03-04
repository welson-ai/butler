import React, { useState, useEffect } from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { parseUnits } from 'viem'
import axios from 'axios'

const API_BASE = 'http://localhost:5001'
const VAULT_ADDRESS = import.meta.env.VITE_BUTLER_VAULT_ADDRESS
const USDC_ADDRESS = import.meta.env.VITE_USDC_ADDRESS || '0x036CbD53842c5426634e7929541eC2318f3dCF7e'

const VAULT_ABI = [
  {
    name: 'deposit',
    type: 'function',
    inputs: [{ name: 'amount', type: 'uint256' }],
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
  const [balance, setBalance] = useState(null)
  const [chatHistory, setChatHistory] = useState([])
  const [activity, setActivity] = useState([])
  const [yields, setYields] = useState({})
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentPlan, setCurrentPlan] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [messages, setMessages] = useState([])

  // Register wallet on connect
  useEffect(() => {
    if (isConnected && connectedAddress) {
      axios.post(`${API_BASE}/api/users/register`, {
        wallet_address: connectedAddress
      }).catch(error => {
        console.error('Error registering wallet:', error)
      })
    }
  }, [isConnected, connectedAddress])

  // Fetch balance every 30 seconds
  useEffect(() => {
    if (!isConnected || !connectedAddress) return

    const fetchBalance = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/balance/${connectedAddress}`)
        setBalance(response.data)
      } catch (error) {
        console.error('Error fetching balance:', error)
      }
    }

    fetchBalance()
    const interval = setInterval(fetchBalance, 30000)
    return () => clearInterval(interval)
  }, [isConnected, connectedAddress])

  // Fetch activity every 10 seconds
  useEffect(() => {
    if (!isConnected || !connectedAddress) return

    const fetchActivity = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/activity/${connectedAddress}`)
        setActivity(response.data.transactions || [])
      } catch (error) {
        console.error('Error fetching activity:', error)
      }
    }

    fetchActivity()
    const interval = setInterval(fetchActivity, 10000)
    return () => clearInterval(interval)
  }, [isConnected, connectedAddress])

  // Fetch yields on mount
  useEffect(() => {
    const fetchYields = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/yields`)
        setYields(response.data)
      } catch (error) {
        console.error('Error fetching yields:', error)
      }
    }

    fetchYields()
  }, [])

  // Initialize chat with Butler greeting
  useEffect(() => {
    if (isConnected) {
      setChatHistory([{
        type: 'butler',
        message: 'Hello! I am your Crypto Butler. Tell me how you would like to manage your USDC. For example: I have 20 USDC. Send 5 to wallet 0xABC every Friday and grow the rest safely.',
        time: new Date().toISOString()
      }])
    }
  }, [isConnected])

  const { writeContractAsync } = useWriteContract()

  const activateButler = async (plan) => {
    try {
      setIsLoading(true)
      const amount = parseUnits(plan.usdc_total.toString(), 6)

      // Step 1 — approve vault to spend USDC
      await writeContractAsync({
        address: USDC_ADDRESS,
        abi: ERC20_ABI,
        functionName: 'approve',
        args: [VAULT_ADDRESS, amount]
      })

      setMessages(prev => [...prev, {
        role: 'butler',
        content: 'USDC approved ✅ Now depositing into vault...'
      }])

      // Step 2 — deposit into vault
      await writeContractAsync({
        address: VAULT_ADDRESS,
        abi: VAULT_ABI,
        functionName: 'deposit',
        args: [amount]
      })

      setMessages(prev => [...prev, {
        role: 'butler',
        content: '🎉 Your funds are in the vault. Your Butler is now fully active and autonomous. You can close this app — I will keep working.'
      }])

      setCurrentPlan(null)
      fetchBalance()
    } catch (error) {
      console.error('Activation error:', error)
      setMessages(prev => [...prev, {
        role: 'butler',
        content: 'Something went wrong with the deposit. Please try again.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!message.trim() || loading || !connectedAddress) return

    const userMessage = message.trim()
    setMessage('')
    setLoading(true)

    // Add user message to chat
    setChatHistory(prev => [...prev, {
      type: 'user',
      message: userMessage,
      time: new Date().toISOString()
    }])

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        wallet_address: connectedAddress,
        message: userMessage
      })

      const reply = response.data.reply
      const plan = response.data.plan

      // Set current plan if available
      if (plan && plan.status === 'active') {
        setCurrentPlan(plan)
      }

      // Add Butler response to chat
      setChatHistory(prev => [...prev, {
        type: 'butler',
        message: reply || 'I understand your request. Let me process that for you.',
        time: new Date().toISOString()
      }])
    } catch (error) {
      setChatHistory(prev => [...prev, {
        type: 'butler',
        message: 'Sorry, I encountered an error processing your request. Please try again.',
        time: new Date().toISOString()
      }])
    } finally {
      setLoading(false)
    }
  }

  const getActivityColor = (type) => {
    switch (type) {
      case 'deposit': return 'text-green-400'
      case 'payment': return 'text-blue-400'
      case 'withdrawal': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getActivityEmoji = (type) => {
    switch (type) {
      case 'deposit': return '📈'
      case 'payment': return '💸'
      case 'withdrawal': return '📉'
      default: return 'ℹ️'
    }
  }

  const formatAddress = (addr) => {
    if (!addr) return ''
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }

  const formatTime = (time) => {
    return new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
      {/* Header */}
      <div className="bg-[#12121a] border-b border-gray-800 px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">CRYPTO BUTLER</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm">Powered by x402 on Base</span>
            <ConnectButton />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Wallet & Balance */}
        <div className="w-1/3 border-r border-gray-800 p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Wallet</h2>
            <div className="bg-[#12121a] p-4 rounded-xl">
              <p className="text-gray-400 text-sm">Connected Address</p>
              <p className="font-mono text-[#7c3aed]">{formatAddress(connectedAddress)}</p>
            </div>
          </div>

          {balance && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Balance</h2>
              
              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">USDC Balance</p>
                <p className="text-2xl font-bold">${balance.usdc_balance?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Aave Deposit</p>
                <p className="text-xl font-semibold text-green-400">${balance.aave_deposit?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Payment Reserve</p>
                <p className="text-xl font-semibold text-blue-400">${balance.payment_reserve?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Buffer</p>
                <p className="text-xl font-semibold text-purple-400">${balance.buffer?.toFixed(2) || '0.00'}</p>
              </div>

              <div className="bg-[#12121a] p-4 rounded-xl">
                <p className="text-gray-400 text-sm">Yield Earned</p>
                <p className="text-xl font-semibold text-yellow-400">${balance.yield_earned?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          )}
        </div>

        {/* Center Panel - Chat */}
        <div className="w-1/3 border-r border-gray-800 flex flex-col">
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#7c3aed] rounded-full flex items-center justify-center">
                🤵
              </div>
              <h2 className="text-lg font-semibold">Butler</h2>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {chatHistory.map((msg, index) => (
              <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl ${
                  msg.type === 'user' 
                    ? 'bg-[#7c3aed] text-white' 
                    : 'bg-[#1e1e2a] text-gray-200'
                }`}>
                  <p className="text-sm">{msg.message}</p>
                  <p className="text-xs opacity-70 mt-1">{formatTime(msg.time)}</p>
                </div>
              </div>
            ))}
            
            {/* Butler Activation Card */}
            {currentPlan && (
              <div style={{
                background: 'linear-gradient(135deg, #1a1a2e, #12122a)',
                padding: '20px',
                borderRadius: '16px',
                border: '1px solid #7c3aed',
                marginTop: '12px'
              }}>
                <div style={{color: '#a78bfa', fontWeight: 'bold', marginBottom: '12px'}}>
                  ⚡ Butler Activation
                </div>
                <div style={{color: '#e5e7eb', fontSize: '14px', marginBottom: '16px'}}>
                  <div>💰 Deposit into vault: <strong>{currentPlan.usdc_total} USDC</strong></div>
                  <div>📈 Deploy to Aave: <strong>{currentPlan.aave_deposit} USDC</strong></div>
                  <div>💸 Payment reserve: <strong>{currentPlan.payment_reserve} USDC</strong></div>
                  <div>🛡️ Safety buffer: <strong>{currentPlan.buffer} USDC</strong></div>
                </div>
                <button
                  onClick={() => activateButler(currentPlan)}
                  disabled={isLoading}
                  style={{
                    background: isLoading ? '#4b5563' : 'linear-gradient(135deg, #7c3aed, #6d28d9)',
                    color: 'white',
                    padding: '14px',
                    borderRadius: '10px',
                    border: 'none',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    fontWeight: 'bold',
                    width: '100%',
                    fontSize: '16px'
                  }}
                >
                  {isLoading ? '⏳ Processing...' : '✅ Activate Butler — Deposit Now'}
                </button>
                <div style={{color: '#6b7280', fontSize: '11px', marginTop: '8px', textAlign: 'center'}}>
                  Two MetaMask popups — approve then deposit. One time only.
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-800">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                className="flex-1 bg-[#12121a] text-white px-4 py-3 rounded-xl border border-gray-700 focus:border-[#7c3aed] focus:outline-none"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !message.trim() || !connectedAddress}
                className="bg-[#7c3aed] text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#6d28d9] transition-colors"
              >
                {loading ? '...' : 'Send'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Activity Feed */}
        <div className="w-1/3 p-6 flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Live Activity</h2>
          
          <div className="flex-1 overflow-y-auto space-y-3 mb-6">
            {activity.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No activity yet</p>
            ) : (
              activity.map((item, index) => (
                <div key={index} className="bg-[#12121a] p-3 rounded-xl">
                  <div className="flex items-start gap-3">
                    <span className="text-lg">{getActivityEmoji(item.tx_type)}</span>
                    <div className="flex-1">
                      <p className={`text-sm ${getActivityColor(item.tx_type)}`}>
                        {item.tx_type === 'deposit' && `Deposited $${item.amount} to Aave`}
                        {item.tx_type === 'payment' && `Sent $${item.amount} to ${formatAddress(item.to_address)}`}
                        {item.tx_type === 'withdrawal' && `Withdrew $${item.amount} from Aave`}
                        {item.tx_type !== 'deposit' && item.tx_type !== 'payment' && item.tx_type !== 'withdrawal' && `${item.tx_type}: $${item.amount}`}
                      </p>
                      <p className="text-xs text-gray-500">{formatTime(item.timestamp)}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Current Yields */}
          <div className="border-t border-gray-800 pt-4">
            <h3 className="text-sm font-semibold mb-3 text-gray-400">Current Yields</h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-[#12121a] p-2 rounded-lg">
                <p className="text-xs text-gray-400">Aave</p>
                <p className="text-sm font-semibold text-green-400">{yields.aave?.toFixed(2) || '0.00'}%</p>
              </div>
              <div className="bg-[#12121a] p-2 rounded-lg">
                <p className="text-xs text-gray-400">Compound</p>
                <p className="text-sm font-semibold text-green-400">{yields.compound?.toFixed(2) || '0.00'}%</p>
              </div>
              <div className="bg-[#12121a] p-2 rounded-lg">
                <p className="text-xs text-gray-400">Curve</p>
                <p className="text-sm font-semibold text-green-400">{yields.curve?.toFixed(2) || '0.00'}%</p>
              </div>
              <div className="bg-[#12121a] p-2 rounded-lg">
                <p className="text-xs text-gray-400">Pendle</p>
                <p className="text-sm font-semibold text-green-400">{yields.pendle?.toFixed(2) || '0.00'}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
