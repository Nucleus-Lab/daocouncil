import os
import logging
import json
import hashlib
import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.agent_toolkits import CdpToolkit
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from decimal import Decimal
import requests
from web3 import Web3
from custom_tools import get_privy_tools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add RPC URL configurations
NETWORK_RPC_URLS = {
    "base sepolia": "https://sepolia.base.org",
    "base": "https://mainnet.base.org",
    "ethereum": "https://mainnet.ethereum.org",
    "sepolia": "https://rpc.sepolia.org"
}

class ResponseCache:
    def __init__(self, cache_dir: str = ".response_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            logger.info(f"Created cache directory: {cache_dir}")

    def _get_cache_key(self, function_name: str, **kwargs) -> str:
        """Generate a unique cache key based on function name and parameters."""
        # Convert kwargs to a sorted string representation for consistent hashing
        kwargs_str = json.dumps(kwargs, sort_keys=True)
        key = f"{function_name}:{kwargs_str}"
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, function_name: str, **kwargs) -> Optional[str]:
        """Get cached response if it exists."""
        cache_key = self._get_cache_key(function_name, **kwargs)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                logger.info(f"Cache hit for {function_name}")
                return cached_data['response']
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
        return None

    def set(self, function_name: str, response: str, **kwargs) -> None:
        """Cache a response."""
        cache_key = self._get_cache_key(function_name, **kwargs)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'function': function_name,
                    'params': kwargs,
                    'response': response
                }, f, indent=2)
            logger.info(f"Cached response for {function_name}")
        except Exception as e:
            logger.error(f"Error writing cache: {str(e)}")

class PrivyServerWallet:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.privy_app_id = os.getenv('PRIVY_APP_ID')
        self.privy_app_secret = os.getenv('PRIVY_APP_SECRET')
        self.base_url = "https://api.privy.io/v1"
        
        # Verify credentials are available
        if not self.privy_app_id or not self.privy_app_secret:
            raise ValueError("PRIVY_APP_ID and PRIVY_APP_SECRET must be set in .env file")
        
        logger.info("Privy Server Wallet initialized successfully")

    def create_wallet(self, chain_type: str):
        """Create a new server wallet"""
        endpoint = f"{self.base_url}/wallets"
        
        headers = {
            'Content-Type': 'application/json',
            'privy-app-id': self.privy_app_id
        }
        
        data = {
            'chain_type': chain_type
        }
        
        logger.info("Creating new Privy server wallet...")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                auth=(self.privy_app_id, self.privy_app_secret)
            )
            
            response.raise_for_status()
            
            wallet_data = response.json()
            logger.info(f"Successfully created Privy wallet with address: {wallet_data.get('address')}")
            return wallet_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Privy wallet: {str(e)}")
            if hasattr(e.response, 'json'):
                logger.error(f"Error details: {e.response.json()}")
            raise

class JudgeAgent:
    def __init__(self, debate_id: str, target_address: str, funding_amount_eth: float, use_cache: bool = True):
        """Initialize a judge agent for a specific debate.
        
        Args:
            debate_id (str): Unique identifier for the debate
            target_address (str): The wallet address that will receive funds if debate passes
            funding_amount_eth (float): Amount of ETH required for the debate
            use_cache (bool): Whether to use response caching
        """
        self.debate_id = debate_id
        self.target_address = target_address
        self.funding_amount_eth = funding_amount_eth
        self.wallet_data_file = f"wallet_data_{debate_id}.txt"
        self.use_cache = use_cache
        self.cache = ResponseCache() if use_cache else None
        self.privy_wallet = None  # Will be set during initialization
        self.wallet_id = None     # Will be set during initialization
        load_dotenv()
        
        logger.info(f"Initializing JudgeAgent for debate: {debate_id}")
        logger.info(f"Target address: {target_address}")
        logger.info(f"Required funding: {funding_amount_eth} ETH")
        logger.info(f"Cache enabled: {use_cache}")
        
        # Initialize the agent and get the debate vault wallet
        self.agent_executor, self.config = self._initialize_agent()
        self._get_or_create_debate_vault()

    def _get_or_create_debate_vault(self):
        """Get existing or create new Privy wallet for this debate."""
        try:
            message = (
                f"Use the privy_get_or_create_wallet tool to get or create a wallet "
                f"for debate ID: {self.debate_id}. This will be our vault for the debate funds."
                f"Return the wallet data in the format of Wallet data: <wallet_data>."
            )
            
            logger.info("Getting/Creating Privy wallet for debate...")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    if "Wallet data:" in response:
                        # Extract wallet data from response
                        import json
                        wallet_str = response.split("Wallet data: ")[1]
                        self.privy_wallet = json.loads(wallet_str.replace("'", '"'))
                        self.wallet_id = self.privy_wallet['id']
                        logger.info(f"Retrieved/Created Privy wallet with ID: {self.wallet_id}")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                
        except Exception as e:
            logger.error(f"Failed to get/create debate vault: {str(e)}")
            raise

    def _initialize_agent(self):
        """Initialize the CDP agent with wallet and tools."""
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            # openai_api_base=os.getenv("DEEPSEEK_BASE_URL"),
            # openai_api_key=os.getenv("DEEPSEEK_API_KEY")
            openai_api_base=os.getenv("GPTUS_BASE_URL"),
            openai_api_key=os.getenv("GPTUS_API_KEY")
        )

        # Initialize CDP Agentkit without Privy wallet data - let it use its own wallet
        agentkit = CdpAgentkitWrapper()

        # Initialize toolkit and tools
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()

        # Add Privy tools
        privy_tools = get_privy_tools(agentkit)
        tools.extend(privy_tools)

        # Set up memory and config
        memory = MemorySaver()
        config = {"configurable": {"thread_id": f"DAO_Judge_{self.debate_id}"}}

        # Create ReAct Agent with updated state modifier
        return create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=(
                "You are a responsible judge AI agent for a DAO debate. "
                "You have two wallets: your CDP wallet for agent operations and "
                f"a Privy wallet (ID: {self.wallet_id}) that acts as a vault for debate funds. "
                "Your workflow is:\n"
                "1. Get funds from faucet to your CDP wallet\n"
                "2. Transfer funds from CDP wallet to Privy vault\n"
                "3. After debate completion, transfer from Privy vault to target address\n"
                "Always verify wallet balances before transactions and maintain detailed logs."
            ),
        ), config

    def _get_cached_response(self, function_name: str, **kwargs) -> Optional[str]:
        """Get cached response if caching is enabled."""
        if self.use_cache and self.cache:
            return self.cache.get(function_name, **kwargs)
        return None

    def _set_cached_response(self, function_name: str, response: str, **kwargs) -> None:
        """Cache response if caching is enabled."""
        if self.use_cache and self.cache:
            self.cache.set(function_name, response, **kwargs)

    def get_wallet_address(self) -> str:
        """Get the vault wallet address for this debate."""
        try:
            return self.privy_wallet['address']
        except Exception as e:
            logger.error(f"Error getting vault wallet address: {str(e)}")
            raise

    def check_funding_status(self) -> bool:
        """Check if the vault wallet has the required funding amount using Web3.
        
        Returns:
            bool: True if the required funding is available, False otherwise
        """
        try:
            # Check cache first
            cached_response = self._get_cached_response("check_funding_status", 
                debate_id=self.debate_id, 
                funding_amount_eth=self.funding_amount_eth
            )
            if cached_response is not None:
                logger.info("Using cached balance check response")
                return cached_response.lower() == 'true'

            # Get vault wallet address
            vault_address = self.get_wallet_address()
            logger.info(f"Checking balance for vault wallet: {vault_address}")
            
            # Initialize Web3 with Base Sepolia RPC URL
            w3 = Web3(Web3.HTTPProvider(NETWORK_RPC_URLS["base sepolia"]))
            
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
            
            # Create detailed response
            response = str(has_sufficient_funds)
            
            # Log the balance information
            logger.info(f"Vault wallet balance: {balance_eth} ETH")
            logger.info(f"Required balance: {self.funding_amount_eth} ETH")
            if has_sufficient_funds:
                logger.info("Sufficient funds available in vault")
            else:
                logger.warning(f"Insufficient funds in vault. Required: {self.funding_amount_eth} ETH, Available: {balance_eth} ETH")
            
            # Cache the response
            self._set_cached_response("check_funding_status", response,
                debate_id=self.debate_id,
                funding_amount_eth=self.funding_amount_eth
            )
            
            return has_sufficient_funds
                
        except Exception as e:
            logger.error(f"Error checking vault funding status: {str(e)}")
            raise

    def request_faucet(self) -> str:
        """Request funds from the faucet to the CDP wallet."""
        try:
            # Check cache first
            cached_response = self._get_cached_response("request_faucet", debate_id=self.debate_id)
            if cached_response is not None:
                logger.info("Using cached faucet request response")
                return cached_response

            message = (
                "Request funds from the faucet to get test tokens for your CDP wallet. "
                "These funds will later be transferred to the Privy vault."
            )
            response = None
            logger.info("Requesting faucet funds to CDP wallet...")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("Faucet request response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("request_faucet", response, debate_id=self.debate_id)
            
            return response
        except Exception as e:
            logger.error(f"Error requesting faucet funds: {str(e)}")
            raise

    def deploy_nft_contract(self) -> str:
        """Deploy a new NFT contract for the debate.
        
        Returns:
            str: The deployed contract address
        """
        try:
            # Check cache first
            cached_response = self._get_cached_response("deploy_nft_contract", 
                debate_id=self.debate_id,
                contract_name=f"Debate NFT {self.debate_id}"
            )
            if cached_response is not None:
                logger.info("Using cached NFT contract deployment response")
                return cached_response

            message = f"Deploy a new NFT contract with name 'Debate NFT {self.debate_id}' and symbol 'DEBATE'"
            response = None
            logger.info("Deploying NFT contract...")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("NFT contract deployment response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("deploy_nft_contract", response,
                    debate_id=self.debate_id,
                    contract_name=f"Debate NFT {self.debate_id}"
                )
            
            return response
        except Exception as e:
            logger.error(f"Error deploying NFT contract: {str(e)}")
            raise

    def mint_nft(self, contract_address: str, debate_history: str, debate_result: bool) -> str:
        """Mint an NFT from an existing contract to the debate vault address.
        
        Args:
            contract_address (str): The address of the NFT contract
            debate_history (str): The history of the debate discussion
            debate_result (bool): The result of the debate
            
        Returns:
            str: Response from the minting operation
        """
        try:
            # Get the vault wallet address
            vault_address = self.get_wallet_address()
            logger.info(f"Using vault wallet address for NFT minting: {vault_address}")
            
            # Create metadata including funding details and debate history
            metadata = (
                f"data:application/json,{{\"name\":\"Debate NFT\","
                f"\"description\":\"NFT for debate {self.debate_id}\","
                f"\"debate_id\":\"{self.debate_id}\","
                f"\"funding_amount_eth\":\"{self.funding_amount_eth}\","
                f"\"target_address\":\"{self.target_address}\","
                f"\"debate_history\":\"{debate_history}\","
                f"\"debate_result\":\"{debate_result}\","
                f"\"vault_address\":\"{vault_address}\","
                f"\"timestamp\":\"{datetime.datetime.now().isoformat()}\"}}"
            )
            
            # Check cache first
            cached_response = self._get_cached_response("mint_nft", 
                debate_id=self.debate_id,
                contract_address=contract_address,
                vault_address=vault_address,
                metadata=metadata
            )
            if cached_response is not None:
                logger.info("Using cached NFT minting response")
                return cached_response
            
            message = (
                f"Mint an NFT from contract {contract_address} to the debate vault "
                f"address {vault_address} with token ID 1 and token URI {metadata}. "
                f"This NFT will serve as a permanent record of debate {self.debate_id}."
            )
            response = None
            logger.info(f"Minting NFT from contract: {contract_address} to vault address: {vault_address}")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("NFT minting response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("mint_nft", response,
                    debate_id=self.debate_id,
                    contract_address=contract_address,
                    vault_address=vault_address,
                    metadata=metadata
                )
            
            return response
        except Exception as e:
            logger.error(f"Error minting NFT to vault: {str(e)}")
            raise

    def transfer_funds_if_approved(self, debate_result: bool) -> Optional[str]:
        """Transfer funds to target address if debate result is approved."""
        try:
            if not debate_result:
                logger.info("Debate was rejected, no funds will be transferred")
                return None

            # Check cache first
            cached_response = self._get_cached_response("transfer_funds_if_approved", 
                debate_id=self.debate_id,
                target_address=self.target_address,
                funding_amount_eth=self.funding_amount_eth
            )
            if cached_response is not None:
                logger.info("Using cached transfer response")
                return cached_response

            # First verify we have sufficient funds
            if not self.check_funding_status():
                raise ValueError(f"Insufficient funds to transfer {self.funding_amount_eth} ETH")

            # Construct transfer message using the new Privy transfer tool
            message = (
                f"Use the privy_transfer tool to send {self.funding_amount_eth} ETH from "
                f"my Privy wallet (ID: {self.wallet_id}) to address {self.target_address} "
                f"on the base sepolia network."
            )
            response = None
            logger.info(f"Initiating Privy transfer of {self.funding_amount_eth} ETH to {self.target_address}")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("Transfer response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("transfer_funds_if_approved", response,
                    debate_id=self.debate_id,
                    target_address=self.target_address,
                    funding_amount_eth=self.funding_amount_eth
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error transferring funds: {str(e)}")
            raise

    def transfer_initial_funds(self, amount_eth: float = 0.000099) -> str:
        """Transfer initial funds from CDP wallet to the debate's vault wallet.
        
        Args:
            amount_eth (float): Amount of ETH to transfer (default: 0.000099 ETH)
            
        Returns:
            str: Response from the transfer operation
        """
        try:
            # Get the vault wallet address
            vault_address = self.get_wallet_address()
            logger.info(f"Preparing to transfer {amount_eth} ETH from CDP wallet to debate vault: {vault_address}")
            
            # Check cache first
            cached_response = self._get_cached_response("transfer_initial_funds", 
                debate_id=self.debate_id,
                amount_eth=amount_eth,
                vault_address=vault_address
            )
            if cached_response is not None:
                logger.info("Using cached transfer response")
                return cached_response

            # Construct transfer message for CDP agent
            message = (
                f"Transfer {amount_eth} ETH from your CDP wallet to the debate vault address {vault_address}. "
                f"This will serve as the funding for debate {self.debate_id}. "
                "Use your CDP wallet's own funds for this transfer, not the Privy wallet."
            )
            response = None
            logger.info("Initiating transfer from CDP wallet to debate vault...")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("Transfer response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("transfer_initial_funds", response,
                    debate_id=self.debate_id,
                    amount_eth=amount_eth,
                    vault_address=vault_address
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error transferring initial funds to debate vault: {str(e)}")
            raise


def main():
    """Test the JudgeAgent implementation."""
    try:
        # 1. Create a judge agent for a test debate
        debate_id = "test_debate_001"
        target_address = "0xBd606164D19e32474CCBda3012783B218E10E52e"
        funding_amount_eth = 0.00003
        
        logger.info("Creating judge agent...")
        judge = JudgeAgent(
            debate_id=debate_id,
            target_address=target_address,
            funding_amount_eth=funding_amount_eth,
            use_cache=True
        )
        
        # 2. Get and print the wallet addresses
        logger.info("Getting wallet addresses...")
        privy_address = judge.get_wallet_address()
        print(f"\nPrivy Vault Address: {privy_address}")
        
        # 3. Get faucet funds to CDP wallet
        logger.info("Requesting faucet funds to CDP wallet...")
        faucet_response = judge.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # 4. Transfer funds from CDP wallet to Privy vault
        logger.info("Transferring funds from CDP wallet to Privy vault...")
        transfer_response = judge.transfer_initial_funds()
        print(f"\nInitial Fund Transfer Response: {transfer_response}")
        
        # 5. Get faucet funds to CDP wallet for gas
        logger.info("Requesting faucet funds to CDP wallet...")
        faucet_response = judge.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # 6. Check funding status
        logger.info("Checking funding status...")
        funding_status = judge.check_funding_status()
        print(f"\nFunding Status: {'Funds Available' if funding_status else 'Insufficient Funds'}")
        
        # 6. Check if funding is available, debate can be started
        if funding_status:
            print("\nDebate can be started!")
            
            # Simulate debate history (in real implementation, this would come from the debate system)
            debate_history = """
            Participant 1: I propose we allocate funds for project X
            Participant 2: What are the expected returns?
            Participant 1: We expect 20% ROI in 6 months
            Participant 2: That sounds reasonable, I support this
            Moderator: The proposal has received majority support
            """
            
            # Simulate debate result (in real implementation, this would come from the debate system)
            debate_result = True  # For testing, assume debate was approved
            
            # 7. Transfer funds if debate was approved
            logger.info("Processing debate result...")
            transfer_response = judge.transfer_funds_if_approved(debate_result)
            if transfer_response:
                print(f"\nTransfer Response: {transfer_response}")
                print("\nFunds have been transferred to the target address!")
                
                # 8. Deploy NFT contract
                logger.info("Deploying NFT contract...")
                deploy_response = judge.deploy_nft_contract()
                print(f"\nNFT Contract Deployment Response: {deploy_response}")
                
                # Extract NFT contract address from deployment response
                import re
                contract_address_match = re.search(r'0x[a-fA-F0-9]{40}', deploy_response)
                if not contract_address_match:
                    raise ValueError("Could not extract contract address from deployment response")
                contract_address = contract_address_match.group(0)
                logger.info(f"Extracted contract address: {contract_address}")
                
                # 9. Mint NFT after successful transfer with debate history
                logger.info("Minting NFT with debate results...")
                mint_response = judge.mint_nft(contract_address, debate_history, debate_result)
                print(f"\nNFT Minting Response: {mint_response}")
            else:
                print("\nNo funds were transferred (debate was rejected)")
        else:
            print("\nDebate cannot be started due to insufficient funds.")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
