/**
 * What this file does: Shows transaction history with links to Basescan
 * What it receives as input: Transaction data from backend API
 * What it returns as output: List of transactions with Basescan links
 */

import React, { useState, useEffect } from 'react'

const TransactionLog = () => {
  const [transactions, setTransactions] = useState([])

  useEffect(() => {
    // TODO: Fetch transaction history from backend
    console.log('Fetching transaction history')
  }, [])

  const getBasescanUrl = (txHash) => {
    return `https://sepolia.basescan.org/tx/${txHash}`
  }

  return (
    <div className="transaction-log p-4 border rounded-lg">
      <h3 className="text-lg font-bold mb-4">Transaction History</h3>
      <div className="transaction-list space-y-2">
        {transactions.length === 0 ? (
          <p className="text-gray-500">No transactions yet</p>
        ) : (
          transactions.map((tx, index) => (
            <div key={index} className="transaction-item p-3 bg-gray-50 rounded flex justify-between items-center">
              <div>
                <div className="font-medium">{tx.type}</div>
                <div className="text-sm text-gray-600">{tx.timestamp}</div>
                <div className="text-sm">{tx.amount} USDC</div>
              </div>
              <a
                href={getBasescanUrl(tx.hash)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:text-blue-700 text-sm"
              >
                View on Basescan
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default TransactionLog
