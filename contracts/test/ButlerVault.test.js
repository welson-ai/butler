const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ButlerVault", function () {
  let butlerVault;
  let usdcToken;
  let owner;
  let user1;
  let user2;
  let recipient;

  beforeEach(async function () {
    [owner, user1, user2, recipient] = await ethers.getSigners();
    
    // Deploy mock USDC
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    usdcToken = await MockERC20.deploy("USD Coin", "USDC", 6);
    await usdcToken.deployed();
    
    // Deploy ButlerVault
    const ButlerVault = await ethers.getContractFactory("ButlerVault");
    butlerVault = await ButlerVault.deploy(usdcToken.address);
    await butlerVault.deployed();
    
    // Mint and transfer USDC to users
    await usdcToken.mint(user1.address, ethers.utils.parseUnits("1000", 6));
    await usdcToken.mint(user2.address, ethers.utils.parseUnits("1000", 6));
    
    await usdcToken.connect(user1).approve(butlerVault.address, ethers.utils.parseUnits("500", 6));
    await usdcToken.connect(user2).approve(butlerVault.address, ethers.utils.parseUnits("500", 6));
  });

  describe("Deployment", function () {
    it("Should set the right USDC token address", async function () {
      expect(await butlerVault.usdcToken()).to.equal(usdcToken.address);
    });
  });

  describe("Deposits", function () {
    it("Should allow users to deposit USDC", async function () {
      const depositAmount = ethers.utils.parseUnits("100", 6);
      
      await expect(butlerVault.connect(user1).deposit(depositAmount))
        .to.emit(butlerVault, "Deposited")
        .withArgs(user1.address, depositAmount);
      
      expect(await usdcToken.balanceOf(butlerVault.address)).to.equal(depositAmount);
    });

    it("Should reject zero amount deposits", async function () {
      await expect(butlerVault.connect(user1).deposit(0))
        .to.be.revertedWith("Amount must be greater than 0");
    });
  });

  describe("Payment Plans", function () {
    it("Should allow users to set payment plans", async function () {
      const paymentAmount = ethers.utils.parseUnits("10", 6);
      const frequency = 7; // weekly
      
      await expect(butlerVault.connect(user1).setPaymentPlan(
        paymentAmount,
        recipient.address,
        frequency
      ))
        .to.emit(butlerVault, "PlanUpdated")
        .withArgs(user1.address, paymentAmount, recipient.address, frequency);
      
      const plan = await butlerVault.getPaymentPlan(user1.address);
      expect(plan.amount).to.equal(paymentAmount);
      expect(plan.recipient).to.equal(recipient.address);
      expect(plan.frequency).to.equal(frequency);
      expect(plan.active).to.be.true;
    });

    it("Should reject invalid payment plans", async function () {
      await expect(butlerVault.connect(user1).setPaymentPlan(0, recipient.address, 7))
        .to.be.revertedWith("Amount must be greater than 0");
      
      await expect(butlerVault.connect(user1).setPaymentPlan(
        ethers.utils.parseUnits("10", 6),
        ethers.constants.AddressZero,
        7
      ))
        .to.be.revertedWith("Invalid recipient");
    });
  });

  describe("Payments", function () {
    beforeEach(async function () {
      // Deposit funds
      await butlerVault.connect(user1).deposit(ethers.utils.parseUnits("100", 6));
      
      // Set payment plan
      await butlerVault.connect(user1).setPaymentPlan(
        ethers.utils.parseUnits("10", 6),
        recipient.address,
        1 // daily for testing
      );
    });

    it("Should execute payments when due", async function () {
      const paymentAmount = ethers.utils.parseUnits("10", 6);
      
      // Fast forward time
      await ethers.provider.send("evm_increaseTime", [24 * 60 * 60]); // 1 day
      await ethers.provider.send("evm_mine");
      
      const initialRecipientBalance = await usdcToken.balanceOf(recipient.address);
      
      await expect(butlerVault.executePayment(user1.address))
        .to.emit(butlerVault, "PaymentMade")
        .withArgs(user1.address, recipient.address, paymentAmount);
      
      const finalRecipientBalance = await usdcToken.balanceOf(recipient.address);
      expect(finalRecipientBalance.sub(initialRecipientBalance)).to.equal(paymentAmount);
    });

    it("Should not execute payments before due", async function () {
      await expect(butlerVault.executePayment(user1.address))
        .to.be.revertedWith("Payment not due yet");
    });
  });

  describe("Withdrawals", function () {
    beforeEach(async function () {
      await butlerVault.connect(user1).deposit(ethers.utils.parseUnits("100", 6));
    });

    it("Should allow users to withdraw their funds", async function () {
      const withdrawAmount = ethers.utils.parseUnits("50", 6);
      const initialBalance = await usdcToken.balanceOf(user1.address);
      
      await expect(butlerVault.connect(user1).withdraw(withdrawAmount))
        .to.emit(butlerVault, "Withdrawn")
        .withArgs(user1.address, withdrawAmount);
      
      const finalBalance = await usdcToken.balanceOf(user1.address);
      expect(finalBalance.sub(initialBalance)).to.equal(withdrawAmount);
    });

    it("Should reject zero amount withdrawals", async function () {
      await expect(butlerVault.connect(user1).withdraw(0))
        .to.be.revertedWith("Amount must be greater than 0");
    });
  });
});
