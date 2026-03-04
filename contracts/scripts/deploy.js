const { ethers } = require("hardhat");

async function main() {
  const USDC_ADDRESS = "0x036CbD53842c5426634f303028093Edf63909008"; // USDC on Base Sepolia
  
  console.log("Deploying ButlerVault...");
  
  const ButlerVault = await ethers.getContractFactory("ButlerVault");
  const butlerVault = await ButlerVault.deploy(USDC_ADDRESS);
  
  await butlerVault.deployed();
  
  console.log("ButlerVault deployed to:", butlerVault.address);
  console.log("USDC address:", USDC_ADDRESS);
  
  // Save deployment info
  const deploymentInfo = {
    contractAddress: butlerVault.address,
    usdcAddress: USDC_ADDRESS,
    network: hre.network.name,
    deployedAt: new Date().toISOString()
  };
  
  const fs = require("fs");
  fs.writeFileSync(
    "deployment.json", 
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("Deployment info saved to deployment.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
