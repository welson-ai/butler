/**
 * What this file does: Defines all Base Sepolia contract addresses and ABIs
 * What it receives as input: No direct inputs - exports constants
 * What it returns as output: Contract addresses and configuration for Base Sepolia
 */

export const BASE_SEPOLIA_USDC = '0x036CbD53842c5426634e7929541eC2318f3dCF7e'
export const AAVE_POOL = '0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b'
export const AUSDC_TOKEN = '0x96C8394a3D1B80b07A4a614C2B2A5e8BF6b9DEF'

export const USDC_ABI = [
  {
    constant: true,
    inputs: [{ name: '_owner', type: 'address' }],
    name: 'balanceOf',
    outputs: [{ name: 'balance', type: 'uint256' }],
    type: 'function',
  },
  {
    constant: true,
    inputs: [],
    name: 'decimals',
    outputs: [{ name: '', type: 'uint8' }],
    type: 'function',
  }
]

export const AAVE_POOL_ABI = [
  {
    inputs: [{ internalType: 'address', name: 'asset', type: 'address' }],
    name: 'getReserveData',
    outputs: [{ internalType: 'uint256', name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function',
  }
]
