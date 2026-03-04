// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IAavePool {
    function supply(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
    ) external;

    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external returns (uint256);
}

contract ButlerVault is ReentrancyGuard {

    // ─────────────────────────────────────────
    // State Variables
    // ─────────────────────────────────────────

    IERC20 public immutable usdc;
    IAavePool public immutable aavePool;
    address public butlerAgent;
    address public owner;

    // Each user's deposited balance
    mapping(address => uint256) public deposits;

    // Each user's Aave deposit
    mapping(address => uint256) public aaveDeposits;

    // Each user's payment reserve
    mapping(address => uint256) public paymentReserves;

    // Whether user has active butler
    mapping(address => bool) public butlerActive;

    // Payment rules per user
    struct PaymentRule {
        address recipient;
        uint256 amount;
        string schedule;
        bool active;
    }
    mapping(address => PaymentRule) public paymentRules;

    // ─────────────────────────────────────────
    // Events
    // ─────────────────────────────────────────

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event DeployedToAave(address indexed user, uint256 amount);
    event WithdrawnFromAave(address indexed user, uint256 amount);
    event PaymentSent(address indexed from, address indexed to, uint256 amount);
    event ButlerActivated(address indexed user);
    event ButlerRevoked(address indexed user);
    event RuleSet(address indexed user, address recipient, uint256 amount, string schedule);

    // ─────────────────────────────────────────
    // Modifiers
    // ─────────────────────────────────────────

    modifier onlyButler() {
        require(msg.sender == butlerAgent, "Only butler agent can call this");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    modifier butlerEnabled(address user) {
        require(butlerActive[user], "Butler not active for this user");
        _;
    }

    // ─────────────────────────────────────────
    // Constructor
    // ─────────────────────────────────────────

    constructor(
        address _usdc,
        address _aavePool,
        address _butlerAgent
    ) {
        usdc = IERC20(_usdc);
        aavePool = IAavePool(_aavePool);
        butlerAgent = _butlerAgent;
        owner = msg.sender;
    }

    // ─────────────────────────────────────────
    // User Functions
    // ─────────────────────────────────────────

    // User deposits USDC once and activates butler
    function deposit(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be greater than zero");

        usdc.transferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
        butlerActive[msg.sender] = true;

        emit Deposited(msg.sender, amount);
        emit ButlerActivated(msg.sender);
    }

    // User sets payment rules
    function setPaymentRule(
        address recipient,
        uint256 amount,
        string calldata schedule
    ) external {
        require(butlerActive[msg.sender], "Deposit first to activate butler");
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Amount must be greater than zero");

        paymentRules[msg.sender] = PaymentRule({
            recipient: recipient,
            amount: amount,
            schedule: schedule,
            active: true
        });

        // Reserve payment amount from deposit
        require(deposits[msg.sender] >= amount, "Insufficient balance for reserve");
        paymentReserves[msg.sender] = amount;

        emit RuleSet(msg.sender, recipient, amount, schedule);
    }

    // User can always withdraw everything directly
    function emergencyWithdraw() external nonReentrant {
        uint256 vaultBalance = deposits[msg.sender];
        uint256 aaveBalance = aaveDeposits[msg.sender];

        require(vaultBalance > 0 || aaveBalance > 0, "Nothing to withdraw");

        // Withdraw from Aave first if deployed
        if (aaveBalance > 0) {
            usdc.approve(address(aavePool), aaveBalance);
            aavePool.withdraw(address(usdc), aaveBalance, address(this));
            aaveDeposits[msg.sender] = 0;
        }

        // Return everything
        uint256 totalBalance = usdc.balanceOf(address(this));
        uint256 userShare = vaultBalance + aaveBalance;

        deposits[msg.sender] = 0;
        paymentReserves[msg.sender] = 0;
        butlerActive[msg.sender] = false;

        usdc.transfer(msg.sender, userShare);

        emit Withdrawn(msg.sender, userShare);
        emit ButlerRevoked(msg.sender);
    }

    // User revokes butler without withdrawing
    function revokeButler() external {
        butlerActive[msg.sender] = false;
        emit ButlerRevoked(msg.sender);
    }

    // ─────────────────────────────────────────
    // Butler Agent Functions
    // Only the AI agent can call these
    // ─────────────────────────────────────────

    // Deploy user funds to Aave
    function deployToAave(
        address user,
        uint256 amount
    ) external onlyButler butlerEnabled(user) nonReentrant {
        require(deposits[user] >= amount, "Insufficient vault balance");
        require(amount > 0, "Amount must be greater than zero");

        deposits[user] -= amount;
        aaveDeposits[user] += amount;

        usdc.approve(address(aavePool), amount);
        aavePool.supply(address(usdc), amount, address(this), 0);

        emit DeployedToAave(user, amount);
    }

    // Withdraw user funds from Aave
    function withdrawFromAave(
        address user,
        uint256 amount
    ) external onlyButler butlerEnabled(user) nonReentrant {
        require(aaveDeposits[user] >= amount, "Insufficient Aave balance");

        aaveDeposits[user] -= amount;
        deposits[user] += amount;

        aavePool.withdraw(address(usdc), amount, address(this));

        emit WithdrawnFromAave(user, amount);
    }

    // Send scheduled payment on behalf of user
    function executePayment(
        address user
    ) external onlyButler butlerEnabled(user) nonReentrant {
        PaymentRule memory rule = paymentRules[user];
        require(rule.active, "No active payment rule");
        require(rule.amount > 0, "Invalid payment amount");
        require(deposits[user] >= rule.amount, "Insufficient balance for payment");

        deposits[user] -= rule.amount;
        usdc.transfer(rule.recipient, rule.amount);

        // Refill payment reserve from Aave if needed
        if (deposits[user] < rule.amount && aaveDeposits[user] >= rule.amount) {
            aaveDeposits[user] -= rule.amount;
            deposits[user] += rule.amount;
            aavePool.withdraw(address(usdc), rule.amount, address(this));
        }

        emit PaymentSent(user, rule.recipient, rule.amount);
    }

    // ─────────────────────────────────────────
    // View Functions
    // ─────────────────────────────────────────

    function getUserBalance(address user) external view returns (
        uint256 vaultBalance,
        uint256 aaveBalance,
        uint256 paymentReserve,
        bool isActive
    ) {
        return (
            deposits[user],
            aaveDeposits[user],
            paymentReserves[user],
            butlerActive[user]
        );
    }

    function getPaymentRule(address user) external view returns (
        address recipient,
        uint256 amount,
        string memory schedule,
        bool active
    ) {
        PaymentRule memory rule = paymentRules[user];
        return (rule.recipient, rule.amount, rule.schedule, rule.active);
    }

    // ─────────────────────────────────────────
    // Owner Functions
    // ─────────────────────────────────────────

    function updateButlerAgent(address newAgent) external onlyOwner {
        butlerAgent = newAgent;
    }
}
