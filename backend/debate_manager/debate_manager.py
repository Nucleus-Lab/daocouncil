import requests
import logging
import re
from web3 import Web3
import datetime
import json
from typing import Dict, Tuple
from .wallet_storage import store_debate_wallets, get_debate_wallets


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
    def __init__(self, debate_id: str, api_url: str):
        """Initialize the DebateManager.
        
        Args:
            debate_id (str): Unique identifier for the debate
            api_url (str): Base URL for the judge agent API
        """
        self.debate_id = debate_id
        self.api_url = api_url
        self.chat_endpoint = f"{api_url}/chat"
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(NETWORK_RPC_URLS["base-sepolia"]))
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Base Sepolia network")

    def chat_with_agent(self, message: str) -> str:
        """Send a chat message to the judge agent.
        
        Args:
            message (str): Message to send to the judge
            
        Returns:
            str: Agent's response
        """
        try:
            response = requests.post(
                self.chat_endpoint,
                json={
                    "debate_id": self.debate_id,
                    "message": message
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error in chat with agent: {str(e)}")
            raise

    def initialize_debate(self) -> Dict[str, str]:
        """Initialize a new debate by creating wallets and storing their information.
        
        Returns:
            Dict containing:
                - cdp_wallet_address: The CDP wallet address
                - privy_wallet_address: The Privy vault wallet address
                - privy_wallet_id: The Privy wallet ID
        """
        try:
            results = {}
            
            # 1. Get CDP wallet address
            logger.info("Getting CDP wallet address...")
            message = "What is your CDP wallet address?"
            cdp_response = self.chat_with_agent(message)
            cdp_match = re.search(r'0x[a-fA-F0-9]{40}', cdp_response)
            if not cdp_match:
                raise ValueError(f"Could not find CDP wallet address in response: {cdp_response}")
            results['cdp_wallet_address'] = cdp_match.group(0)
            
            # 2. Create Privy wallet
            logger.info("Creating Privy wallet...")
            message = "Create a new Privy wallet for this debate. This will be the vault for the debate."
            privy_response = self.chat_with_agent(message)
            
            # Extract Privy wallet address and ID from response
            privy_addr_match = re.search(r'\*\*Wallet Address:\*\* (0x[a-fA-F0-9]{40})', privy_response)
            privy_id_match = re.search(r'\*\*Wallet ID:\*\* ([a-zA-Z0-9]+)', privy_response)
            
            if not (privy_addr_match and privy_id_match):
                logger.error(f"Response format: {privy_response}")
                raise ValueError("Could not extract Privy wallet details. Expected format with '**Wallet ID:**' and '**Wallet Address:**'")
                
            results['privy_wallet_address'] = privy_addr_match.group(1)
            results['privy_wallet_id'] = privy_id_match.group(1)
            
            # Store wallet information in JSON file
            # TODO: store in database
            store_debate_wallets(
                debate_id=self.debate_id,
                cdp_wallet_address=results['cdp_wallet_address'],
                privy_wallet_address=results['privy_wallet_address'],
                privy_wallet_id=results['privy_wallet_id']
            )
            
            logger.info("Debate initialization completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error initializing debate: {str(e)}")
            raise

    def check_funding_status(self, wallet_address: str, required_amount_eth: float) -> Tuple[bool, float]:
        """Check if the specified wallet has the required funding.
        
        Args:
            wallet_address (str): The wallet address to check
            required_amount_eth (float): Required amount in ETH
            
        Returns:
            Tuple[bool, float]: (has_sufficient_funds, current_balance_eth)
        """
        try:
            logger.info(f"Checking balance for wallet: {wallet_address}")
            
            # Get balance
            balance_wei = self.w3.eth.get_balance(wallet_address)
            balance_eth = float(Web3.from_wei(balance_wei, 'ether'))
            
            # Check if balance is sufficient
            required_wei = Web3.to_wei(required_amount_eth, 'ether')
            has_sufficient_funds = balance_wei >= required_wei
            
            logger.info(f"Wallet balance: {balance_eth} ETH")
            logger.info(f"Required amount: {required_amount_eth} ETH")
            
            return has_sufficient_funds, balance_eth
            
        except Exception as e:
            logger.error(f"Error checking funding status: {str(e)}")
            raise

    def process_debate_result(self, 
                            debate_history: str,
                            ai_votes: Dict[str, bool],
                            ai_reasoning: Dict[str, str],
                            action_prompt: str) -> Dict[str, str]:
        """Process debate result and execute the specified action.
        
        Args:
            debate_history (str): Complete debate conversation history
            ai_votes (Dict[str, bool]): Dictionary of AI agent IDs and their votes
            ai_reasoning (Dict[str, str]): Dictionary of AI agent IDs and their reasoning
            action_prompt (str): The action to be executed if debate is approved
            
        Returns:
            Dict containing operation results
        """
        try:
            results = {}
            
            # Get wallet information from JSON storage
            wallet_info = get_debate_wallets(self.debate_id)
            if not wallet_info:
                raise ValueError(f"No wallet information found for debate {self.debate_id}")
            
            # Create metadata for NFT
            metadata = {
                "name": f"Debate NFT {self.debate_id}",
                "description": "NFT representing a DAO debate result",
                "debate_id": self.debate_id,
                "debate_history": debate_history,
                "ai_votes": ai_votes,
                "ai_reasoning": ai_reasoning,
                "privy_wallet_id": wallet_info['privy_wallet_id'],
                "timestamp": str(datetime.datetime.now().isoformat())
            }
            
            # 1. Deploy NFT contract with metadata
            logger.info("Deploying NFT contract...")
            deploy_message = (
                f"Deploy a new NFT contract with the following parameters:\n"
                f"- name: 'Debate NFT {self.debate_id}'\n"
                f"- symbol: 'DEBATE'\n"
                f"- metadata: {json.dumps(metadata, indent=2)}\n"
                f"Please deploy the contract with this metadata structure."
            )
            deploy_response = self.chat_with_agent(deploy_message)
            results['nft_deployment'] = deploy_response
            
            # Extract contract address
            contract_address_match = re.search(r'0x[a-fA-F0-9]{40}', deploy_response)
            if not contract_address_match:
                raise ValueError("Could not extract contract address from deployment response")
            contract_address = contract_address_match.group(0)
            
            # 2. Mint NFT
            logger.info("Minting NFT...")
            mint_message = (
                f"Mint an NFT from contract {contract_address} to the Privy vault with the following metadata:\n"
                f"{json.dumps(metadata, indent=2)}"
            )
            results['nft_minting'] = self.chat_with_agent(mint_message)
            
            # 3. Execute action if debate is approved
            approved = sum(ai_votes.values()) > len(ai_votes) / 2
            if approved:
                logger.info("Debate approved, executing action...")
                action_message = (
                    f"The debate has been approved. Please execute the following action:"
                    f"{action_prompt}\n\n"
                    f"Note: If this action involves transferring funding, please use the privy_transfer tool "
                    f"with the Privy wallet ID provided (Wallet ID: {wallet_info['privy_wallet_id']})."
                )
                results['action_execution'] = self.chat_with_agent(action_message)
            else:
                logger.info("Debate rejected, no action taken")
                results['action_execution'] = "Debate rejected, no action taken"
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing debate result: {str(e)}")
            raise