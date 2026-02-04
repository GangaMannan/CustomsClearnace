const hre = require("hardhat");

async function main() {
  // 1. Tell Hardhat which contract to find
  const Customs = await hre.ethers.getContractFactory("CustomsClearance");

  // 2. Deploy it to the network
  const customs = await Customs.deploy();

  // 3. Wait for the deployment to finish
  await customs.waitForDeployment();

  // 4. Log the address so you can find it later
  console.log("Contract deployed to:", customs.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});