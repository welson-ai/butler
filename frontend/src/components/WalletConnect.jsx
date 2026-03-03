/**
 * What this file does: Handles wallet connection using RainbowKit
 * What it receives as input: Wallet connection events and user interactions
 * What it returns as output: Connect wallet button and wallet status display
 */

import React from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit'

const WalletConnect = () => {
  return (
    <div className="wallet-connect">
      <ConnectButton
        showBalance={false}
        chainStatus="icon"
        accountStatus={{
          smallScreen: 'avatar',
          largeScreen: 'full',
        }}
      />
    </div>
  )
}

export default WalletConnect
