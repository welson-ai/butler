const hre = require("hardhat")

async function main() {
  const USDC = process.env.USDC_ADDRESS
  const AAVE_POOL = process.env.AAVE_POOL

  const [deployer] = await hre.ethers.getSigners()
  console.log("Deploying with:", deployer.address)

  const ButlerVault = await hre.ethers.getContractFactory("ButlerVault")
  const vault = await ButlerVault.deploy(
    USDC,
    AAVE_POOL,
    deployer.address  // Butler agent = deployer for now
  )

  await vault.waitForDeployment()
  const address = await vault.getAddress()
  
  console.log("ButlerVault deployed to:", address)
  console.log("Save this address in your .env files")
}

main().catch(console.error)
