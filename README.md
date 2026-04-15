# Crypto Butler - Autonomous DeFi Wealth Management Agent

Crypto Butler is an intelligent, autonomous DeFi wealth management agent that revolutionizes how users interact with decentralized finance. By leveraging natural language processing and smart contract automation, Crypto Butler connects to any Web3 wallet, optimizes USDC yields across DeFi protocols, compounds earnings automatically, and executes scheduled payments — all without human intervention after the initial setup.

## 🎯 Problem Statement

### Current DeFi Challenges
- **Complex User Experience**: DeFi requires deep technical knowledge and constant monitoring
- **Time-Intensive Management**: Users must manually track yields, rebalance portfolios, and execute transactions
- **Suboptimal Yield Optimization**: Most users lack the tools to maximize returns across multiple protocols
- **Payment Automation Gaps**: No easy way to set up recurring cryptocurrency payments with yield optimization
- **Risk Management**: Users struggle to balance yield generation with appropriate risk levels

### Our Solution
Crypto Butler addresses these challenges by providing:
- **Natural Language Interface**: Users simply tell the Butler their financial goals in plain English
- **Autonomous Execution**: The Butler handles all technical complexity automatically
- **Intelligent Yield Optimization**: Continuously monitors and reallocates funds to the best-yielding protocols
- **Scheduled Financial Operations**: Automated payments, savings, and investment strategies
- **Real-time Transparency**: Complete visibility into all operations through an intuitive dashboard

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CRYPTO BUTLER                            │
├─────────────────────────────────────────────────────────────────┤
│                         FRONTEND                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Wallet    │ │    Chat     │ │   Live      │              │
│  │ Connection  │ │ Interface   │ │ Dashboard   │              │
│  │  (Rainbow)  │ │   (NLP)     │ │   (Realtime)│              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                         BACKEND                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Agent     │ │  Scheduler  │ │   Protocol  │              │
│  │   Brain     │ │   (APSD)    │ │  Adapters   │              │
│  │  (Claude)   │ │             │ │ (Aave,etc.) │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Rules     │ │   Storage   │ │   Yield     │              │
│  │   Engine    │ │   (JSON)    │ │   Monitor   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                     BLOCKCHAIN LAYER                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Butler    │ │     USDC    │ │     Aave    │              │
│  │    Vault    │ │   (ERC20)   │ │   (Pool)    │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```
<<<<<<< HEAD

## 📁 Project Structure

```
crypto-butler/
├── 📄 README.md
├── 📄 LICENSE
├── 📁 frontend/                    # React + Vite Frontend
│   ├── 📁 src/
│   │   ├── 📄 App.jsx              # Main React component
│   │   ├── 📄 main.jsx             # React entry point
│   │   ├── 📁 config/              # Wagmi & RainbowKit config
│   │   │   └── 📄 wagmi.js
│   │   └── 📁 styles/              # CSS & Tailwind
│   ├── 📄 package.json
│   ├── 📄 vite.config.js
│   └── 📄 .env                     # Frontend env vars
├── 📁 backend/                     # Python Flask Backend
│   ├── 📄 main.py                  # Flask app entry point
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 .env                     # Backend env vars
│   ├── 📁 api/                     # REST API endpoints
│   │   ├── 📄 routes.py            # API route definitions
│   │   └── 📄 websocket.py         # WebSocket handlers
│   ├── 📁 agent/                   # AI Agent Core
│   │   ├── 📄 brain.py             # Claude integration & NLP
│   │   └── 📄 scheduler.py         # Task scheduling (APScheduler)
│   ├── 📁 protocols/               # DeFi Protocol Adapters
│   │   ├── 📄 aave.py              # Aave integration
│   │   ├── 📄 vault.py             # ButlerVault contract
│   │   ├── 📄 mock_yields.py       # Yield data providers
│   │   └── 📄 protocol_factory.py  # Protocol factory pattern
│   ├── 📁 users/                   # User Management
│   │   ├── 📄 rules_engine.py      # Financial rule processing
│   │   ├── 📄 user_store.py        # User data storage
│   │   └── 📄 payment_rules.py     # Payment scheduling
│   ├── 📁 wallets/                 # Wallet Integration
│   │   ├── 📄 wallet_manager.py    # Multi-wallet support
│   │   └── 📄 transaction_signer.py # Transaction signing
│   ├── 📁 data/                    # Data Storage
│   │   ├── 📁 users/               # User profiles & plans
│   │   ├── 📁 transactions/        # Transaction history
│   │   └── 📁 logs/                # System logs
│   └── 📁 utils/                   # Utilities
│       ├── 📄 logger.py            # Logging system
│       └── 📄 helpers.py           # Helper functions
├── 📁 contracts/                   # Smart Contracts
│   ├── 📁 contracts/
│   │   ├── 📄 ButlerVault.sol       # Main vault contract
│   │   ├── 📄 MockYieldEngine.sol   # Yield testing contract
│   │   └── 📄 PaymentRule.sol       # Payment rule contract
│   ├── 📁 scripts/
│   │   ├── 📄 deploy.js            # Deployment script
│   │   └── 📄 interact.js          # Contract interaction script
│   ├── 📁 test/
│   │   └── 📄 ButlerVault.test.js  # Contract tests
│   └── 📄 hardhat.config.js        # Hardhat configuration
└── 📁 docs/                        # Documentation
    ├── 📄 API.md                   # API documentation
    ├── 📄 DEPLOYMENT.md            # Deployment guide
    └── 📄 SECURITY.md              # Security considerations
```

## Core Components

### Frontend Architecture

**React + Vite + TailwindCSS + RainbowKit**

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   LEFT      │  │   CENTER    │  │   RIGHT     │    │
│  │   PANEL     │  │   PANEL     │  │   PANEL     │    │
│  │             │  │             │  │             │    │
│  │ • Wallet    │  │ • Butler    │  │ • Live      │    │
│  │ • Connect   │  │   Chat      │  │   Activity  │    │
│  │ • Balances  │  │ • Messages  │  │ • Yields    │    │
│  │ • Emergency │  │ • Input     │  │ • Status    │    │
│  │ • Withdraw  │  │ • Modal     │  │ • Ticker    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              MODAL POPUP SYSTEM                 │    │
│  │  • Butler Activation                            │    │
│  │  • Plan Review                                  │    │
│  │  • Transaction Confirmation                     │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                    TECH STACK                           │
│                                                         │
│  • React 18           • Vite 5.4                      │
│  • RainbowKit         • Wagmi                         │
│  • TailwindCSS        • Axios                         │
│  • Viem               • WebSocket                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Backend Architecture

**Python + Flask + APScheduler + Web3.py**

```
┌─────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  FLASK APP                      │    │
│  │                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │     API     │  │  WebSocket  │  │  Auth   │ │    │
│  │  │   Routes    │  │  Server     │  │ Layer   │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 AGENT CORE                       │    │
│  │                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │   Agent     │  │  Scheduler  │  │ Rules   │ │    │
│  │  │   Brain     │  │   (APSD)    │  │ Engine  │ │    │
│  │  │  (Claude)    │  │             │  │         │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              PROTOCOL LAYER                      │    │
│  │                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │    Aave     │  │   Butler    │  │   USDC  │ │    │
│  │  │   Pool      │  │   Vault     │  │  Token  │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                    TECH STACK                           │
│                                                         │
│  • Python 3.9+        • Flask                        │
│  • APScheduler         • Web3.py                      │
│  • Claude API          • SQLite/JSON                 │
│  • WebSocket           • pytest                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   USER      │───▶│  FRONTEND   │───▶│  BACKEND    │
│   INPUT     │    │    (React)  │    │   (Flask)   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │   STATE     │    │   AGENT     │
                    │ MANAGEMENT  │    │   BRAIN     │
                    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │    UI       │    │  SCHEDULER  │
                    │  UPDATES    │    │   (TASKS)   │
                    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                    ┌─────────────┐
                                    │  BLOCKCHAIN  │
                                    │ INTERACTION │
                                    └─────────────┘
                                             │
                                             ▼
                                    ┌─────────────┐
                                    │   REALTIME   │
                                    │   FEEDBACK   │
                                    └─────────────┘
```

## Key Features

### Autonomous Intelligence
- **Natural Language Processing**: Users communicate in plain English
- **Intent Recognition**: Claude AI parses complex financial instructions
- **Rule Generation**: Automatically converts user goals into executable rules
- **Adaptive Learning**: System learns from user preferences and behaviors

###  Yield Optimization
- **Multi-Protocol Support**: Aave, Compound, Curve, and more
- **Real-Time Monitoring**: Continuous yield rate tracking
- **Automatic Rebalancing**: Moves funds to highest-yielding protocols
- **Risk-Adjusted Returns**: Balances APY against risk factors

###  Scheduled Operations
- **Recurring Payments**: Weekly, monthly, or custom payment schedules
- **Yield Compounding**: Automatic reinvestment of earned yield
- **Buffer Management**: Maintains safety buffers for payments
- **Smart Execution**: Optimizes transaction timing and gas costs

### 📊 Real-Time Transparency
- **Live Dashboard**: Real-time balance and transaction updates
- **Activity Feed**: Detailed transaction history with explanations
- **Performance Metrics**: Yield performance, ROI tracking
- **Alert System**: Notifications for important events

###  Security & Risk Management
- **Multi-Signature Support**: Additional security layers for large transactions
- **Spending Limits**: Configurable daily/weekly transaction limits
- **Risk Profiles**: Conservative, moderate, and aggressive risk levels
- **Emergency Controls**: Instant fund withdrawal and plan cancellation

## Use Cases

###  Personal Finance Automation
- **Automated Savings**: "Save $100 every month and grow it safely"
- **Bill Payments**: "Pay $500 for rent on the 1st of every month"
- **Investment Growth**: "Invest 50% of my income in the highest-yielding protocol"

### Business Treasury Management
- **Payroll Automation**: "Pay employee salaries on the 15th and 30th"
- **Vendor Payments**: "Pay $2000 to supplier wallet every Monday"
- **Yield Optimization**: "Maximize returns on company treasury while maintaining liquidity"

### Educational & Non-Profit
- **Scholarship Disbursements**: "Send $250 to student wallets monthly"
- **Grant Management**: "Distribute grant funds according to schedule"
- **Endowment Growth**: "Grow endowment while making annual distributions"

## Technology Stack

### Frontend Technologies
- **React 18**: Modern UI framework with hooks and concurrent features
- **Vite 5.4**: Lightning-fast build tool and development server
- **RainbowKit**: Best-in-class Web3 wallet connection library
- **Wagmi**: React hooks for Ethereum interactions
- **TailwindCSS**: Utility-first CSS framework for rapid styling
- **Viem**: TypeScript library for Ethereum with excellent performance

### Backend Technologies
- **Python 3.9+**: Modern Python with async/await support
- **Flask**: Lightweight, flexible web framework
- **APScheduler**: Advanced task scheduling with cron-like expressions
- **Web3.py**: Python library for Ethereum interaction
- **Claude API**: Advanced AI for natural language processing
- **WebSocket**: Real-time bidirectional communication

### Blockchain & DeFi
- **Base Sepolia**: Ethereum L2 testnet with low gas fees
- **USDC**: Stablecoin for value storage and transfers
- **Aave Protocol**: Leading DeFi lending and borrowing platform
- **Smart Contracts**: Solidity contracts for vault management
- **ERC20 Standards**: Standardized token interfaces

### Infrastructure & DevOps
- **Hardhat**: Ethereum development environment
- **pytest**: Python testing framework
- **JSON Storage**: Lightweight, human-readable data persistence
- **Environment Variables**: Secure configuration management
- **Git Version Control**: Track changes and collaboration

## 📁 Project Structure

```
crypto-butler/
├── 📄 README.md
├── 📄 LICENSE
├── 📁 frontend/                    # React + Vite Frontend
│   ├── 📁 src/
│   │   ├── 📄 App.jsx              # Main React component
│   │   ├── 📄 main.jsx             # React entry point
│   │   ├── 📁 config/              # Wagmi & RainbowKit config
│   │   │   └── 📄 wagmi.js
│   │   └── 📁 styles/              # CSS & Tailwind
│   ├── 📄 package.json
│   ├── 📄 vite.config.js
│   └── 📄 .env                     # Frontend env vars
├── 📁 backend/                     # Python Flask Backend
│   ├── 📄 main.py                  # Flask app entry point
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 .env                     # Backend env vars
│   ├── 📁 api/                     # REST API endpoints
│   │   ├── 📄 routes.py            # API route definitions
│   │   └── 📄 websocket.py         # WebSocket handlers
│   ├── 📁 agent/                   # AI Agent Core
│   │   ├── 📄 brain.py             # Claude integration & NLP
│   │   └── 📄 scheduler.py         # Task scheduling (APScheduler)
│   ├── 📁 protocols/               # DeFi Protocol Adapters
│   │   ├── 📄 aave.py              # Aave integration
│   │   ├── 📄 vault.py             # ButlerVault contract
│   │   ├── 📄 mock_yields.py       # Yield data providers
│   │   └── 📄 protocol_factory.py  # Protocol factory pattern
│   ├── 📁 users/                   # User Management
│   │   ├── 📄 rules_engine.py      # Financial rule processing
│   │   ├── 📄 user_store.py        # User data storage
│   │   └── 📄 payment_rules.py     # Payment scheduling
│   ├── 📁 wallets/                 # Wallet Integration
│   │   ├── 📄 wallet_manager.py    # Multi-wallet support
│   │   └── 📄 transaction_signer.py # Transaction signing
│   ├── 📁 data/                    # Data Storage
│   │   ├── 📁 users/               # User profiles & plans
│   │   ├── 📁 transactions/        # Transaction history
│   │   └── 📁 logs/                # System logs
│   └── 📁 utils/                   # Utilities
│       ├── 📄 logger.py            # Logging system
│       └── 📄 helpers.py           # Helper functions
├── 📁 contracts/                   # Smart Contracts
│   ├── 📁 contracts/
│   │   ├── 📄 ButlerVault.sol       # Main vault contract
│   │   ├── 📄 MockYieldEngine.sol   # Yield testing contract
│   │   └── 📄 PaymentRule.sol       # Payment rule contract
│   ├── 📁 scripts/
│   │   ├── 📄 deploy.js            # Deployment script
│   │   └── 📄 interact.js          # Contract interaction script
│   ├── 📁 test/
│   │   └── 📄 ButlerVault.test.js  # Contract tests
│   └── 📄 hardhat.config.js        # Hardhat configuration
└── 📁 docs/                        # Documentation
    ├── 📄 API.md                   # API documentation
    ├── 📄 DEPLOYMENT.md            # Deployment guide
    └── 📄 SECURITY.md              # Security considerations
```

## 🧠 Core Components

### Frontend Architecture

**React + Vite + TailwindCSS + RainbowKit**

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   LEFT      │  │   CENTER    │  │   RIGHT     │    │
│  │   PANEL     │  │   PANEL     │  │   PANEL     │    │
│  │             │  │             │  │             │    │
│  │ • Wallet    │  │ • Butler    │  │ • Live      │    │
│  │ • Connect   │  │   Chat      │  │   Activity  │    │
│  │ • Balances  │  │ • Messages  │  │ • Yields    │    │
│  │ • Emergency │  │ • Input     │  │ • Status    │    │
│  │ • Withdraw  │  │ • Modal     │  │ • Ticker    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              MODAL POPUP SYSTEM                 │    │
│  │  • Butler Activation                            │    │
│  │  • Plan Review                                  │    │
│  │  • Transaction Confirmation                     │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                    TECH STACK                           │
│                                                         │
│  • React 18           • Vite 5.4                      │
│  • RainbowKit         • Wagmi                         │
│  • TailwindCSS        • Axios                         │
│  • Viem               • WebSocket                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Backend Architecture

**Python + Flask + APScheduler + Web3.py**

```
┌─────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  FLASK APP                      │    │
│  │                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │     API     │  │  WebSocket  │  │  Auth   │ │    │
│  │  │   Routes    │  │  Server     │  │ Layer   │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 AGENT CORE                       │    │
│  │                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │   Agent     │  │  Scheduler  │  │ Rules   │ │    │
│  │  │   Brain     │  │   (APSD)    │  │ Engine  │ │    │
│  │  │  (Claude)    │  │             │  │         │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              PROTOCOL LAYER                      │    │
│  │                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │    │
│  │  │    Aave     │  │   Butler    │  │   USDC  │ │    │
│  │  │   Pool      │  │   Vault     │  │  Token  │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                    TECH STACK                           │
│                                                         │
│  • Python 3.9+        • Flask                        │
│  • APScheduler         • Web3.py                      │
│  • Claude API          • SQLite/JSON                 │
│  • WebSocket           • pytest                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   USER      │───▶│  FRONTEND   │───▶│  BACKEND    │
│   INPUT     │    │    (React)  │    │   (Flask)   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │   STATE     │    │   AGENT     │
                    │ MANAGEMENT  │    │   BRAIN     │
                    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │    UI       │    │  SCHEDULER  │
                    │  UPDATES    │    │   (TASKS)   │
                    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                    ┌─────────────┐
                                    │  BLOCKCHAIN  │
                                    │ INTERACTION │
                                    └─────────────┘
                                             │
                                             ▼
                                    ┌─────────────┐
                                    │   REALTIME   │
                                    │   FEEDBACK   │
                                    └─────────────┘
```

## 🚀 Key Features

### 🤖 Autonomous Intelligence
- **Natural Language Processing**: Users communicate in plain English
- **Intent Recognition**: Claude AI parses complex financial instructions
- **Rule Generation**: Automatically converts user goals into executable rules
- **Adaptive Learning**: System learns from user preferences and behaviors

### 💰 Yield Optimization
- **Multi-Protocol Support**: Aave, Compound, Curve, and more
- **Real-Time Monitoring**: Continuous yield rate tracking
- **Automatic Rebalancing**: Moves funds to highest-yielding protocols
- **Risk-Adjusted Returns**: Balances APY against risk factors

### ⏰ Scheduled Operations
- **Recurring Payments**: Weekly, monthly, or custom payment schedules
- **Yield Compounding**: Automatic reinvestment of earned yield
- **Buffer Management**: Maintains safety buffers for payments
- **Smart Execution**: Optimizes transaction timing and gas costs

### 📊 Real-Time Transparency
- **Live Dashboard**: Real-time balance and transaction updates
- **Activity Feed**: Detailed transaction history with explanations
- **Performance Metrics**: Yield performance, ROI tracking
- **Alert System**: Notifications for important events

### 🛡️ Security & Risk Management
- **Multi-Signature Support**: Additional security layers for large transactions
- **Spending Limits**: Configurable daily/weekly transaction limits
- **Risk Profiles**: Conservative, moderate, and aggressive risk levels
- **Emergency Controls**: Instant fund withdrawal and plan cancellation

## 🎯 Use Cases

### 🏠 Personal Finance Automation
- **Automated Savings**: "Save $100 every month and grow it safely"
- **Bill Payments**: "Pay $500 for rent on the 1st of every month"
- **Investment Growth**: "Invest 50% of my income in the highest-yielding protocol"

### 💼 Business Treasury Management
- **Payroll Automation**: "Pay employee salaries on the 15th and 30th"
- **Vendor Payments**: "Pay $2000 to supplier wallet every Monday"
- **Yield Optimization**: "Maximize returns on company treasury while maintaining liquidity"

### 🎓 Educational & Non-Profit
- **Scholarship Disbursements**: "Send $250 to student wallets monthly"
- **Grant Management**: "Distribute grant funds according to schedule"
- **Endowment Growth**: "Grow endowment while making annual distributions"

## 🛠️ Technology Stack

### Frontend Technologies
- **React 18**: Modern UI framework with hooks and concurrent features
- **Vite 5.4**: Lightning-fast build tool and development server
- **RainbowKit**: Best-in-class Web3 wallet connection library
- **Wagmi**: React hooks for Ethereum interactions
- **TailwindCSS**: Utility-first CSS framework for rapid styling
- **Viem**: TypeScript library for Ethereum with excellent performance

### Backend Technologies
- **Python 3.9+**: Modern Python with async/await support
- **Flask**: Lightweight, flexible web framework
- **APScheduler**: Advanced task scheduling with cron-like expressions
- **Web3.py**: Python library for Ethereum interaction
- **Claude API**: Advanced AI for natural language processing
- **WebSocket**: Real-time bidirectional communication

### Blockchain & DeFi
- **Base Sepolia**: Ethereum L2 testnet with low gas fees
- **USDC**: Stablecoin for value storage and transfers
- **Aave Protocol**: Leading DeFi lending and borrowing platform
- **Smart Contracts**: Solidity contracts for vault management
- **ERC20 Standards**: Standardized token interfaces

### Infrastructure & DevOps
- **Hardhat**: Ethereum development environment
- **pytest**: Python testing framework
- **JSON Storage**: Lightweight, human-readable data persistence
- **Environment Variables**: Secure configuration management
- **Git Version Control**: Track changes and collaboration

## 📋 Setup Instructions

### Prerequisites
- **Node.js 18+**: JavaScript runtime for frontend
- **Python 3.9+**: Backend runtime environment
- **MetaMask**: Web3 wallet for blockchain interactions
- **Base Sepolia ETH**: For gas fees on testnet
- **USDC on Base Sepolia**: For testing deposits and yields

### 🚀 Quick Start

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/crypto-butler.git
cd crypto-butler
```

#### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Add your WalletConnect Project ID
echo "VITE_WALLETCONNECT_PROJECT_ID=your_project_id_here" >> .env

# Start development server
npm run dev
```

#### 3. Backend Setup
```bash
# Navigate to backend
cd ../backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Add your API keys
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env
echo "BASE_SEPOLIA_RPC_URL=https://sepolia.base.org" >> .env

# Start backend server
python main.py
```

#### 4. Contract Deployment
```bash
# Navigate to contracts
cd ../contracts

# Install dependencies
npm install

# Deploy contracts (requires testnet ETH)
npx hardhat run scripts/deploy.js --network baseSepolia

# Update environment variables with deployed addresses
```

### 🔧 Environment Configuration
#### Frontend (.env)
```env
VITE_WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
VITE_BUTLER_VAULT_ADDRESS=0x...
VITE_USDC_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
```

#### Backend (.env)
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
USDC_SEPOLIA_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
AAVE_POOL_SEPOLIA_ADDRESS=0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b
AUSDC_SEPOLIA_ADDRESS=0x96C8394a3D1B80b07A4a614C2B2A5e8BF6b9DEF
BUTLER_VAULT_ADDRESS=0x...
TEST_CLOCK_INTERVAL=180  # 3 minutes = 1 day for testing
```

## 🎮 Usage Guide

### 1. **Wallet Connection**
- Click "Connect Wallet" in the top-left corner
- Choose your preferred wallet (MetaMask, Coinbase, Rainbow, etc.)
- Switch to Base Sepolia network
- Ensure you have testnet ETH for gas fees

### 2. **Fund Your Wallet**
- Get testnet ETH from Base Sepolia faucet
- Obtain USDC on Base Sepolia for testing
- Your balances will appear in the left panel

### 3. **Configure Your Butler**
- Type natural language instructions in the chat
- Examples:
  - "I have $50 USDC. Send $10 to my friend every Friday and grow the rest"
  - "Save $20 monthly for 6 months and maximize yield"
  - "Pay $500 rent on the 1st of each month, invest the rest safely"

### 4. **Review and Activate**
- Butler will show you a detailed plan in a modal popup
- Review the allocation: yield earning, payment reserve, safety buffer
- Click "Yes — Activate Butler" to confirm
- Two MetaMask confirmations required: approve USDC, then deposit

### 5. **Monitor Performance**
- Watch live activity in the right panel
- Track yield accumulation in real-time
- Monitor scheduled payments and transactions
- Use emergency withdraw if needed

## 🧪 Testing & Development

### Test Users
The system includes pre-configured test users:
- **john_001**: $20 USDC, moderate risk, Friday payments
- **amina_002**: $50 USDC, conservative risk, Monday payments  
- **brian_003**: $100 USDC, aggressive risk, monthly payments

### Test Clock
For development, the scheduler uses accelerated time:
- **3 minutes = 1 day** (24x speed)
- **21 minutes = 1 week**
- **84 minutes = 1 month**

This allows rapid testing of scheduled operations without waiting for real-time periods.

### Mock Data
- **Mock Yields**: Simulated yield rates for multiple protocols
- **Mock Transactions**: Pre-populated transaction history
- **Mock Users**: Test user profiles with different scenarios

<<<<<<< HEAD
##  Security Considerations

###  Private Key Security
- **No Key Storage**: Private keys never stored in application
- **Wallet-Only Signing**: All transactions signed in user wallet
- **Hardware Wallet Support**: Compatible with Ledger and Trezor

###  Risk Management
- **Spending Limits**: Configurable daily/weekly limits
- **Multi-Signature**: Optional multi-sig for large transactions
- **Emergency Controls**: Instant stop and withdraw capabilities
- **Audit Trail**: Complete transaction history and logging

### Smart Contract Security
- **Open Source**: All contracts auditable and verified
- **Standard Interfaces**: ERC20 and established DeFi patterns
- **Upgrade Safe**: Proxy patterns for safe contract upgrades
- **Test Coverage**: Comprehensive test suite

##  Performance Metrics

###  Yield Optimization
- **Protocol Switching**: Automatic rebalancing to highest APY
- **Gas Optimization**: Batch transactions and optimal timing
- **Compound Frequency**: Daily, weekly, or monthly compounding
- **Risk-Adjusted Returns**: Balance yield generation vs risk

### System Performance
- **Real-Time Updates**: <100ms UI refresh rates
- **API Response**: <200ms average response time
- **WebSocket Latency**: <50ms message delivery
- **Transaction Speed**: Optimized for Base L2 performance

### Analytics & Monitoring
- **ROI Tracking**: Real-time return on investment calculation
- **Yield Attribution**: Protocol-specific yield breakdown
- **Transaction Analytics**: Gas costs, success rates, timing
- **User Behavior**: Interaction patterns and preferences

## Roadmap

### 📅 Phase 1 (Current)
- ✅ Basic Butler functionality
- ✅ Aave integration
- ✅ Natural language processing
- ✅ Real-time dashboard
- ✅ Emergency controls

### 📅 Phase 2 (Q2 2024)
- 🔄 Multi-protocol support (Compound, Curve)
- 🔄 Advanced yield strategies
- 🔄 Mobile responsive design
- 🔄 Enhanced security features
- 🔄 Performance analytics

### 📅 Phase 3 (Q3 2024)
- 📋 Cross-chain support (Polygon, Arbitrum)
- 📋 Advanced AI strategies
- 📋 Institutional features
- 📋 Compliance tools
- 📋 White-label solutions

### 📅 Phase 4 (Q4 2024)
- 🎯 Mainnet deployment
- 🎯 Governance token
- 🎯 DAO integration
- 🎯 Insurance products
- 🎯 Advanced analytics

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

###  Bug Reports
- Use GitHub Issues for bug reports
- Include detailed reproduction steps
- Provide environment details

### Feature Requests
- Open an issue with "Feature Request" label
- Describe the use case and benefits
- Consider implementation complexity

### Code Contributions
- Fork the repository
- Create a feature branch
- Add tests for new functionality
- Submit a pull request

##  Support & Community

- **Discord**: [Join our Discord](https://discord.gg/crypto-butler)
- **Twitter**: [@CryptoButlerAI](https://twitter.com/CryptoButlerAI)
- **Documentation**: [docs.crypto-butler.com](https://docs.crypto-butler.com)
- **Support**: support@crypto-butler.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Claude AI**: For natural language processing capabilities
- **Aave**: For providing excellent DeFi infrastructure
- **Base**: For the efficient L2 blockchain
- **RainbowKit**: For elegant wallet integration
- **OpenZeppelin**: For secure smart contract standards

---
### ⚡ Smart Contract Security
- **Open Source**: All contracts auditable and verified
- **Standard Interfaces**: ERC20 and established DeFi patterns
- **Upgrade Safe**: Proxy patterns for safe contract upgrades
- **Test Coverage**: Comprehensive test suite

## 📈 Performance Metrics

### 🎯 Yield Optimization
- **Protocol Switching**: Automatic rebalancing to highest APY
- **Gas Optimization**: Batch transactions and optimal timing
- **Compound Frequency**: Daily, weekly, or monthly compounding
- **Risk-Adjusted Returns**: Balance yield generation vs risk

### ⚡ System Performance
- **Real-Time Updates**: <100ms UI refresh rates
- **API Response**: <200ms average response time
- **WebSocket Latency**: <50ms message delivery
- **Transaction Speed**: Optimized for Base L2 performance

### 📊 Analytics & Monitoring
- **ROI Tracking**: Real-time return on investment calculation
- **Yield Attribution**: Protocol-specific yield breakdown
- **Transaction Analytics**: Gas costs, success rates, timing
- **User Behavior**: Interaction patterns and preferences

## 🚀 Roadmap

### 📅 Phase 1 (Current)
- ✅ Basic Butler functionality
- ✅ Aave integration
- ✅ Natural language processing
- ✅ Real-time dashboard
- ✅ Emergency controls

### 📅 Phase 2 (Q2 2024)
- 🔄 Multi-protocol support (Compound, Curve)
- 🔄 Advanced yield strategies
- 🔄 Mobile responsive design
- 🔄 Enhanced security features
- 🔄 Performance analytics

### 📅 Phase 3 (Q3 2024)
- 📋 Cross-chain support (Polygon, Arbitrum)
- 📋 Advanced AI strategies
- 📋 Institutional features
- 📋 Compliance tools
- 📋 White-label solutions

### 📅 Phase 4 (Q4 2024)
- 🎯 Mainnet deployment
- 🎯 Governance token
- 🎯 DAO integration
- 🎯 Insurance products
- 🎯 Advanced analytics

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 🐛 Bug Reports
- Use GitHub Issues for bug reports
- Include detailed reproduction steps
- Provide environment details

### 💡 Feature Requests
- Open an issue with "Feature Request" label
- Describe the use case and benefits
- Consider implementation complexity

### 🔧 Code Contributions
- Fork the repository
- Create a feature branch
- Add tests for new functionality
- Submit a pull request

## 📞 Support & Community

- **Discord**: [Join our Discord](https://discord.gg/crypto-butler)
- **Twitter**: [@CryptoButlerAI](https://twitter.com/CryptoButlerAI)
- **Documentation**: [docs.crypto-butler.com](https://docs.crypto-butler.com)
- **Support**: support@crypto-butler.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude AI**: For natural language processing capabilities
- **Aave**: For providing excellent DeFi infrastructure
- **Base**: For the efficient L2 blockchain
- **RainbowKit**: For elegant wallet integration
- **OpenZeppelin**: For secure smart contract standards

---

**Built with ❤️ by the Crypto Butler Team**

*Autonomous DeFi Wealth Management for Everyone*
