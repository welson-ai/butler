// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract ButlerVault is Ownable, ReentrancyGuard {
    IERC20 public usdcToken;
    
    struct PaymentPlan {
        uint256 amount;
        address recipient;
        uint256 lastPayment;
        uint256 frequency; // 1 = daily, 7 = weekly, 30 = monthly
        bool active;
    }
    
    mapping(address => PaymentPlan) public paymentPlans;
    address[] public users;
    
    event PaymentMade(address indexed user, address indexed recipient, uint256 amount);
    event PlanUpdated(address indexed user, uint256 amount, address recipient, uint256 frequency);
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    
    constructor(address _usdcToken) {
        usdcToken = IERC20(_usdcToken);
    }
    
    function deposit(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        require(usdcToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        emit Deposited(msg.sender, amount);
    }
    
    function withdraw(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        require(usdcToken.balanceOf(address(this)) >= amount, "Insufficient vault balance");
        
        uint256 userBalance = getUserBalance(msg.sender);
        require(userBalance >= amount, "Insufficient user balance");
        
        require(usdcToken.transfer(msg.sender, amount), "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }
    
    function setPaymentPlan(
        uint256 amount,
        address recipient,
        uint256 frequency
    ) external {
        require(amount > 0, "Amount must be greater than 0");
        require(recipient != address(0), "Invalid recipient");
        require(frequency > 0, "Invalid frequency");
        
        if (paymentPlans[msg.sender].amount == 0) {
            users.push(msg.sender);
        }
        
        paymentPlans[msg.sender] = PaymentPlan({
            amount: amount,
            recipient: recipient,
            lastPayment: block.timestamp,
            frequency: frequency,
            active: true
        });
        
        emit PlanUpdated(msg.sender, amount, recipient, frequency);
    }
    
    function executePayment(address user) external nonReentrant {
        PaymentPlan storage plan = paymentPlans[user];
        require(plan.active, "No active payment plan");
        
        uint256 timeSinceLastPayment = block.timestamp - plan.lastPayment;
        require(timeSinceLastPayment >= plan.frequency * 1 days, "Payment not due yet");
        
        uint256 userBalance = getUserBalance(user);
        require(userBalance >= plan.amount, "Insufficient balance for payment");
        
        require(usdcToken.transfer(plan.recipient, plan.amount), "Transfer failed");
        
        plan.lastPayment = block.timestamp;
        emit PaymentMade(user, plan.recipient, plan.amount);
    }
    
    function getUserBalance(address user) public view returns (uint256) {
        // This would typically track per-user deposits
        // For simplicity, we'll use the total vault balance divided by number of users
        if (users.length == 0) return 0;
        return usdcToken.balanceOf(address(this)) / users.length;
    }
    
    function getPaymentPlan(address user) external view returns (PaymentPlan memory) {
        return paymentPlans[user];
    }
    
    function getAllUsers() external view returns (address[] memory) {
        return users;
    }
    
    function getVaultBalance() external view returns (uint256) {
        return usdcToken.balanceOf(address(this));
    }
}
