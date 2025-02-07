import requests
import logging
import re
from web3 import Web3
import datetime
import json
import time
import os

# Add RPC URL configurations
NETWORK_RPC_URLS = {
    "base-sepolia": "https://sepolia.base.org",
    "base": "https://mainnet.base.org",
    "ethereum": "https://mainnet.ethereum.org",
    "sepolia": "https://rpc.sepolia.org"
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebateManager:
    def __init__(self, debate_id: str, funding_amount_eth: float, target_address: str, api_url: str = "http://localhost:8000"):
        self.debate_id = debate_id
        self.funding_amount_eth = funding_amount_eth
        self.target_address = target_address
        self.api_url = api_url
        self.chat_endpoint = f"{api_url}/chat"


    def chat_with_agent(self, debate_id: str, message: str) -> str:
        """Send a chat message to the judge agent."""
        try:
            response = requests.post(
                self.chat_endpoint,
                json={
                    "debate_id": debate_id,
                    "message": message
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error in chat with agent: {str(e)}")
            raise

    def initialize_debate(self) -> dict:
        """Initialize a new debate with wallet creation and funding.
        
        Returns:
            dict: A dictionary containing the results of the debate initialization
        """
        try:
            results = {}
            
            # 1. Create a new Privy wallet
            logger.info("Creating new Privy wallet...")
            message = "Create a new Privy wallet for this debate. This will be the vault for the debate."
            results['wallet_creation'] = self.chat_with_agent(self.debate_id, message)
                        
            # Extract the Privy wallet address
            results['wallet_address'] = self.get_wallet_address()
            
            return results
            
        except Exception as e:
            logger.error(f"Error initializing debate: {str(e)}")
            raise
        
        
    def get_wallet_address(self) -> str:
        """Get the address of the Privy wallet."""
        try:
            # Ask the agent for the vault address
            message = "What is my Privy vault wallet address for this debate?"
            response = self.chat_with_agent(self.debate_id, message)
            
            # Extract address using regex
            address_match = re.search(r'0x[a-fA-F0-9]{40}', response)
            if not address_match:
                raise ValueError(f"Could not find wallet address in response: {response}")
            
            wallet_address = address_match.group(0)
            logger.info(f"Retrieved vault wallet address: {wallet_address}")
            return wallet_address
            
        except Exception as e:
            logger.error(f"Error getting vault wallet address: {str(e)}")
            raise

    def check_vault_funding_status(self) -> bool:
        """Check if the vault wallet has the required funding amount using Web3.
        
        Returns:
            bool: True if the required funding is available, False otherwise
        """
        try:
            # Get vault wallet address
            vault_address = self.get_wallet_address()
            logger.info(f"Checking balance for vault wallet: {vault_address}")
            
            # Initialize Web3 with Base Sepolia RPC URL
            w3 = Web3(Web3.HTTPProvider(NETWORK_RPC_URLS["base-sepolia"]))
            
            # Check if connection is successful
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to Base Sepolia network")
            
            # Get balance in Wei
            balance_wei = w3.eth.get_balance(vault_address)
            balance_eth = Web3.from_wei(balance_wei, 'ether')
            
            # Convert required funding to Wei for comparison
            required_wei = Web3.to_wei(self.funding_amount_eth, 'ether')
            
            # Check if balance is sufficient
            has_sufficient_funds = balance_wei >= required_wei
            
            # Log the balance information
            logger.info(f"Vault wallet balance: {balance_eth} ETH")
            logger.info(f"Required balance: {self.funding_amount_eth} ETH")
            if has_sufficient_funds:
                logger.info("Sufficient funds available in vault")
            else:
                logger.warning(f"Insufficient funds in vault. Required: {self.funding_amount_eth} ETH, Available: {balance_eth} ETH")

            return has_sufficient_funds
                
        except Exception as e:
            logger.error(f"Error checking vault funding status: {str(e)}")
            raise

    def process_debate_result(self, 
                            debate_id: str, 
                            debate_history: str, 
                            debate_result: bool,
                            target_address: str) -> dict:
        """Process the result of a debate, including fund transfer and NFT creation."""
        try:
            results = {}
            
            if debate_result:
                # 1. Transfer funds to target address
                logger.info("Processing fund transfer...")
                message = (
                    f"Transfer the debate funds {self.funding_amount_eth} ETH from the Privy vault to "
                    f"target address {target_address}"
                )
                results['transfer'] = self.chat_with_agent(debate_id, message)
                
            else:
                results['status'] = "Debate rejected, no funds transferred"
                
            # Create metadata JSON
            metadata = {
                "name": f"Debate NFT {debate_id}",
                "description": "NFT representing a DAO debate result",
                "debate_id": debate_id,
                "debate_history": debate_history,
                "result": debate_result,
                "funding_amount": str(self.funding_amount_eth),
                "target_address": target_address,
                "timestamp": str(datetime.datetime.now().isoformat())
            }
            
            # 2. Deploy NFT contract with metadata
            logger.info("Deploying NFT contract...")
            message = (
                f"Deploy a new NFT contract with the following parameters:\n"
                f"- name: 'Debate NFT {debate_id}'\n"
                f"- symbol: 'DEBATE'\n"
                f"- metadata: {json.dumps(metadata, indent=2)}\n"
                f"Please deploy the contract with this metadata structure."
            )
            deploy_response = self.chat_with_agent(debate_id, message)
            results['nft_deployment'] = deploy_response
            
            # Extract contract address
            contract_address_match = re.search(r'0x[a-fA-F0-9]{40}', deploy_response)
            if not contract_address_match:
                raise ValueError("Could not extract contract address from deployment response")
            contract_address = contract_address_match.group(0)
            
            # 3. Mint NFT with same metadata
            logger.info("Minting NFT...")
            message = (
                f"Mint an NFT from contract {contract_address} to the Privy vault with the following metadata:\n"
                f"{json.dumps(metadata, indent=2)}\n"
                f"Make sure to use the same metadata structure as in the contract deployment."
            )
            results['nft_minting'] = self.chat_with_agent(debate_id, message)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing debate result: {str(e)}")
            raise