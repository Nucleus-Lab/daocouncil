import requests
import logging
import re
from typing import Optional
from pydantic import BaseModel
from web3 import Web3
import datetime
import json
import time

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

    def initialize_debate(self, max_retries: int = 3, retry_delay: float = 2.0) -> dict:
        """Initialize a new debate with wallet creation and funding.
        
        Args:
            max_retries (int): Maximum number of retry attempts for faucet requests
            retry_delay (float): Delay in seconds between retries
        """
        try:
            results = {}
            
            # 1. Create a new Privy wallet
            logger.info("Creating new Privy wallet...")
            message = "Create a new Privy wallet for this debate. This will be the vault for the debate."
            results['wallet_creation'] = self.chat_with_agent(self.debate_id, message)

            # 2. Request faucet funds to CDP wallet with retry
            logger.info("Requesting faucet funds...")
            faucet_message = (
                "Request funds from the faucet to get test tokens for your CDP wallet. "
                "These funds will later be transferred to the Privy vault."
            )
            
            for attempt in range(max_retries):
                try:
                    results['faucet_request'] = self.chat_with_agent(self.debate_id, faucet_message)
                    if "error" not in results['faucet_request'].lower() and "unable to request" not in results['faucet_request'].lower():
                        break
                    logger.warning(f"Faucet request failed (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(retry_delay)
                except Exception as e:
                    logger.error(f"Error in faucet request attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay)

            # 3. Transfer initial funds to Privy vault
            logger.info("Transferring initial funds to vault...")
            message = (
                "Transfer 0.000099 ETH from your CDP wallet to the Privy vault using the normal transfer tool. "
                "This will serve as the funding for the debate operations."
            )
            results['initial_transfer'] = self.chat_with_agent(self.debate_id, message)

            # 4. Request more faucet funds for gas with retry
            logger.info("Requesting additional faucet funds for gas...")
            gas_faucet_message = "Request more funds from the faucet for your CDP wallet for gas fees"
            
            for attempt in range(max_retries):
                try:
                    results['additional_faucet'] = self.chat_with_agent(self.debate_id, gas_faucet_message)
                    if "error" not in results['additional_faucet'].lower() and "unable to request" not in results['additional_faucet'].lower():
                        break
                    logger.warning(f"Additional faucet request failed (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(retry_delay)
                except Exception as e:
                    logger.error(f"Error in additional faucet request attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:  # Last attempt
                        raise
                    time.sleep(retry_delay)

            # 5. Check funding status
            logger.info("Checking funding status...")
            results['funding_status'] = self.check_vault_funding_status()

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

def main():
    """Test the debate flow."""
    try:
        # Test debate parameters
        debate_id = "test_debate_001"
        funding_amount_eth = 0.000003
        target_address = "0xBd606164D19e32474CCBda3012783B218E10E52e"
        
        # Initialize debate manager
        manager = DebateManager(debate_id, funding_amount_eth, target_address)
        
        
        
        # Initialize debate
        print("\n=== Initializing Debate ===")
        init_results = manager.initialize_debate()
        for key, value in init_results.items():
            print(f"\n{key.replace('_', ' ').title()}:")
            print(value)

            
        if init_results['funding_status']:
            # Simulate debate history
            debate_history = """
            Participant 1: I propose we allocate funds for project X
            Participant 2: What are the expected returns?
            Participant 1: We expect 20% ROI in 6 months

            Participant 2: That sounds reasonable, I support this
            Moderator: The proposal has received majority support
            """
            
            # Process debate result (assuming approved)
            print("\n=== Processing Debate Result ===")
            result_results = manager.process_debate_result(
                debate_id=debate_id,
                debate_history=debate_history,
                debate_result=True,
                target_address=target_address
            )
            for key, value in result_results.items():
                print(f"\n{key.replace('_', ' ').title()}:")
                print(value)
                
        else:
            print("Debate is not started because funding isn't deposited into vault!")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
