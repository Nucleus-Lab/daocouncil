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
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DebateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, debate_id: str = None, api_url: str = None):
        """Initialize the DebateManager singleton.
        
        Args:
            debate_id (str, optional): Unique identifier for the debate
            api_url (str, optional): Base URL for the judge agent API
        """
        # Only initialize once
        if self._initialized:
            if debate_id is not None:
                self.debate_id = debate_id
            return
            
        self.debate_id = debate_id
        self.api_url = api_url
        self.chat_endpoint = f"{api_url}/chat" if api_url else None
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(NETWORK_RPC_URLS["base-sepolia"]))
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Base Sepolia network")
            
        self._initialized = True
    
    @property
    def debate_id(self):
        return self._debate_id
        
    @debate_id.setter
    def debate_id(self, value):
        self._debate_id = value
        if value is not None:
            logger.info(f"DebateManager now handling debate: {value}")

    def chat_with_agent(self, message: str) -> str:
        """Send a chat message to the judge agent.
        
        Args:
            message (str): Message to send to the judge
            
        Returns:
            str: Agent's response
        """
        try:
            logger.info(f"Sending message to judge agent at {self.chat_endpoint}")
            logger.info(f"Request payload: {json.dumps({'debate_id': self.debate_id, 'message': message})}")
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
            
            logger.info(f"CDP response: {cdp_response}")
            
            cdp_match = re.search(r'0x[a-fA-F0-9]{40}', cdp_response)
            if not cdp_match:
                raise ValueError(f"Could not find CDP wallet address in response: {cdp_response}")
            results['cdp_wallet_address'] = cdp_match.group(0)
            
            # 2. Create Privy wallet
            logger.info("Creating Privy wallet...")
            message = "Create a new Privy wallet for this debate. This will be the vault for the debate. Please return the wallet address and ID in this json format: example: {'wallet_address': '0x1234567890123456789012345678901234567890', 'wallet_id': '1234567890'}"
            privy_response = self.chat_with_agent(message)
            
            logger.info(f"Privy response: {privy_response}")
            
            # First try to parse as JSON
            try:
                # Try to find JSON content between triple backticks if present
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', privy_response, re.DOTALL)
                if json_match:
                    privy_response = json_match.group(1)
                
                # Try to parse the JSON
                json_data = json.loads(privy_response)
                if 'wallet_address' in json_data and 'wallet_id' in json_data:
                    addr = json_data['wallet_address']
                    wallet_id = json_data['wallet_id']
                    # Add 0x prefix if not present
                    addr = addr if addr.startswith('0x') else f'0x{addr}'
                    results['privy_wallet_address'] = addr
                    results['privy_wallet_id'] = wallet_id
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not parse JSON response, falling back to regex: {e}")
            
            # Fallback to regex if JSON parsing fails
            # Extract Privy wallet address and ID from response using flexible pattern matching
            privy_addr_match = re.search(
                r'["\']?wallet_address["\']?\s*:\s*["\']?(0x[0-9a-fA-F]{40})["\']?',
                privy_response,
                re.IGNORECASE
            )
            
            privy_id_match = re.search(
                r'["\']?wallet_id["\']?\s*:\s*["\']?([a-zA-Z0-9]+)["\']?',
                privy_response,
                re.IGNORECASE
            )
            
            if not (privy_addr_match and privy_id_match):
                logger.error(f"Response format: {privy_response}")
                raise ValueError(
                    "Could not extract Privy wallet details. "
                    "Expected response to contain 'Wallet ID' and 'Wallet Address' information."
                )
            
            # Add 0x prefix if not present
            addr = privy_addr_match.group(1)
            addr = addr if addr.startswith('0x') else f'0x{addr}'
            results['privy_wallet_address'] = addr
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

    def deploy_nft(self, metadata_uri: str) -> Tuple[str, str]:
        """Deploy NFT contract with metadata URI.
        
        Args:
            metadata_uri (str): URI pointing to the debate metadata
            
        Returns:
            Tuple[str, str]: (contract_address, deployment_response)
        """
        logger.info("Deploying NFT contract...")
        deploy_message = (
            f"Deploy a new NFT contract with the following parameters:\n"
            f"- name: 'Debate NFT {self.debate_id}'\n"
            f"- symbol: 'DEBATE'\n"
            f"- baseURI: '{metadata_uri}'\n"
            f"Please deploy the contract with this base URI."
        )
        deploy_response = self.chat_with_agent(deploy_message)
        logger.info(f"NFT deployment response: {deploy_response}")
        
        # Extract contract address with flexible pattern matching
        contract_address_match = re.search(
            r'(?:contract\s*(?:address|at|deployed\s*to)?)[^\w\n]*[`\s]*([0-9a-fA-F]{40}|0x[0-9a-fA-F]{40})[`\s]*',
            deploy_response,
            re.IGNORECASE
        )
        if not contract_address_match:
            logger.error(f"Could not extract contract address from deployment response: {deploy_response}")
            raise ValueError(f"Could not extract contract address from deployment response. Full response: {deploy_response}")
            
        # Add 0x prefix if not present
        addr = contract_address_match.group(1)
        addr = addr if addr.startswith('0x') else f'0x{addr}'
        
        return addr, deploy_response
        
    def mint_nft(self, contract_address: str, target_address: str) -> str:
        """Mint NFT to the specified address.
        
        Args:
            contract_address (str): Deployed contract address
            target_address (str): Address to mint the NFT to
            
        Returns:
            str: Minting response
        """
        logger.info(f"Minting NFT to address: {target_address}...")
        mint_message = f"Mint an NFT from contract {contract_address} to the address {target_address}"
        mint_response = self.chat_with_agent(mint_message)
        logger.info(f"NFT minting response: {mint_response}")
        return mint_response
        
    def execute_action(self, action_prompt: str, privy_wallet_id: str) -> str:
        """Execute the specified action if debate is approved.
        
        Args:
            action_prompt (str): Action to execute
            privy_wallet_id (str): Privy wallet ID for fund transfers
            
        Returns:
            str: Action execution response
        """
        logger.info("Executing action...")
        action_message = (
            f"{action_prompt}\n\n"
            f"Note: If this action involves transferring funding, please use the privy_transfer tool "
            f"with the Privy wallet ID provided (Wallet ID: {privy_wallet_id})."
        )
        action_response = self.chat_with_agent(action_message)
        logger.info(f"Action execution response: {action_response}")
        return action_response

    def process_debate_result(self, 
                            debate_history: str,
                            ai_votes: Dict[str, bool],
                            ai_reasoning: Dict[str, str],
                            action_prompt: str) -> Dict[str, str]:
        """Process debate result and execute necessary actions.
        
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
            
            # 1. Deploy NFT contract
            contract_address, deploy_response = self.deploy_nft(metadata)
            results['nft_deployment'] = deploy_response
            
            # 2. Mint NFT
            results['nft_minting'] = self.mint_nft(contract_address, wallet_info['privy_wallet_address'])
            
            # 3. Execute action if debate is approved
            results['action_execution'] = self.execute_action(
                    action_prompt,
                    wallet_info['privy_wallet_id']
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing debate result: {str(e)}")
            raise