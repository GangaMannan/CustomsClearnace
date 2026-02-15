// scripts/deploy.js
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  // 1) Tell Hardhat which contract to deploy
  const Customs = await hre.ethers.getContractFactory("CustomsClearance");

  // 2) Deploy it
  const customs = await Customs.deploy();

  // 3) Wait for deployment
  await customs.waitForDeployment();

  // 4) Get deployed contract address (Hardhat/Ethers v6)
  const address = customs.target;

  // 5) Log it
  console.log("Contract deployed to:", address);

  // 6) Save it for Streamlit (in project root)
  const outPath = path.join(__dirname, "..", "deployedAddress.json");

  const payload = {
    contractName: "CustomsClearance",
    contractAddress: address,
    network: hre.network.name,
    deployedAt: new Date().toISOString(),
  };

  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2));
  console.log("Saved deployed address to:", outPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
