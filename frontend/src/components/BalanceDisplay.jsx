/**
 * What this file does: Shows USDC balance and yield growth in real-time
 * What it receives as input: Wallet address and balance data from hooks
 * What it returns as output: Visual display of current balances and earned yield
 */

import React from 'react'

const BalanceDisplay = ({ usdcBalance, aaveDeposit, yieldEarned }) => {
  return (
    <div className="balance-display p-4 border rounded-lg">
      <h3 className="text-lg font-bold mb-4">Your Wealth</h3>
      <div className="balance-grid grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="balance-item p-3 bg-blue-50 rounded">
          <div className="text-sm text-gray-600">Available USDC</div>
          <div className="text-2xl font-bold text-blue-600">
            ${usdcBalance || '0.00'}
          </div>
        </div>
        <div className="balance-item p-3 bg-green-50 rounded">
          <div className="text-sm text-gray-600">In Aave</div>
          <div className="text-2xl font-bold text-green-600">
            ${aaveDeposit || '0.00'}
          </div>
        </div>
        <div className="balance-item p-3 bg-yellow-50 rounded">
          <div className="text-sm text-gray-600">Yield Earned</div>
          <div className="text-2xl font-bold text-yellow-600">
            ${yieldEarned || '0.00'}
          </div>
        </div>
      </div>
    </div>
  )
}

export default BalanceDisplay
