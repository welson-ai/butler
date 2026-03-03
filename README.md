# Crypto Butler - Autonomous DeFi Wealth Management Agent

Crypto Butler is an autonomous DeFi wealth management agent that connects to any Web3 wallet, deposits USDC into Aave on Base Sepolia, compounds yield automatically, and sends scheduled payments to wallet addresses — all without human intervention after setup.

## Features

- **Autonomous Wealth Management**: Automatically manages USDC deposits across DeFi protocols
- **Yield Optimization**: Monitors and optimizes yields across multiple protocols
- **Scheduled Payments**: Set up recurring payments to any wallet address
- **Real-time Monitoring**: Live dashboard showing balances, transactions, and agent activity
- **Multi-wallet Support**: Manage multiple wallets with different permission levels
- **Risk Management**: Configurable risk levels and spending limits

## Architecture

### Frontend (React + Vite)
- **Wallet Connection**: RainbowKit integration for MetaMask, Coinbase, Rainbow, and WalletConnect
- **Real-time UI**: Live updates via WebSocket
- **Dashboard**: Balance display, activity feed, transaction history
- **Chat Interface**: Natural language commands to the Butler agent

### Backend (Python + Flask)
- **Agent Brain**: Claude API integration for processing user instructions
- **Transaction Executor**: Handles blockchain transactions via Web3.py
- **Scheduler**: APScheduler for automated tasks (test clock: 3 minutes = 1 day)
- **Yield Monitor**: Real-time yield tracking across protocols
- **WebSocket Server**: Real-time communication with frontend

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- MetaMask or other Web3 wallet

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd crypto-butler/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Add your WalletConnect Project ID to `.env`:
```
VITE_WALLETCONNECT_PROJECT_ID=your_project_id_here
```

5. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Backend Setup

1. Navigate to backend directory:
```bash
cd crypto-butler/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```
ANTHROPIC_API_KEY=your_anthropic_api_key
WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
USDC_SEPOLIA_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
AAVE_POOL_SEPOLIA_ADDRESS=0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b
TEST_CLOCK_INTERVAL=180
```

5. Start backend server:
```bash
python main.py
```

Backend API will be available at `http://localhost:5000`

## Usage

1. **Connect Wallet**: Use the RainbowKit connect button to connect your Web3 wallet to Base Sepolia
2. **Fund Wallet**: Ensure you have USDC on Base Sepolia for testing
3. **Set Rules**: Configure your automation rules through the chat interface
4. **Monitor**: Watch the Butler agent work autonomously in real-time

## Test Data

The system includes three mock users for testing:
- **john_001**: $20 USDC, moderate risk, Friday payments
- **amina_002**: $50 USDC, conservative risk, Monday payments  
- **brian_003**: $100 USDC, aggressive risk, monthly payments

## Contract Addresses (Base Sepolia)

- **USDC**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- **Aave Pool**: `0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b`
- **aUSDC**: `0x96C8394a3D1B80b07A4a614C2B2A5e8BF6b9DEF`

## Development

### Test Clock
For development, the scheduler runs on a test clock where 3 minutes = 1 day to accelerate testing of scheduled tasks.

### Mock Yields
The system includes mock yield data providers for demonstration purposes when real protocol data is unavailable.

### Logging
All agent actions, transactions, and errors are logged for debugging and monitoring.

## Security Notes

- Private keys are never stored in the application
- All transactions require explicit user permission setup
- Spending limits and risk levels provide additional safety layers
- All blockchain interactions are logged and auditable

## License

MIT License - see LICENSE file for details
