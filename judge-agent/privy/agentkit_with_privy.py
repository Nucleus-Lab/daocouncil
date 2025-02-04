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
from .custom_tools import get_privy_transfer_tool

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

    def create_wallet(self):
        """Create a new server wallet"""
        endpoint = f"{self.base_url}/wallets"
        
        headers = {
            'Content-Type': 'application/json',
            'privy-app-id': self.privy_app_id
        }
        
        data = {
            'chain_type': 'ethereum'
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
        self.privy_wallet = None  # Will store the Privy wallet data
        self.wallet_id = None     # Will store the Privy wallet ID
        load_dotenv()
        
        logger.info(f"Initializing JudgeAgent for debate: {debate_id}")
        logger.info(f"Target address: {target_address}")
        logger.info(f"Required funding: {funding_amount_eth} ETH")
        logger.info(f"Cache enabled: {use_cache}")
        
        # Create a new Privy wallet for this debate
        self._create_privy_wallet()
        
        # Initialize the agent with the new wallet
        self.agent_executor, self.config = self._initialize_agent()

    def _create_privy_wallet(self):
        """Create a new Privy server wallet for this debate."""
        try:
            privy = PrivyServerWallet()
            wallet_data = privy.create_wallet()
            
            self.privy_wallet = wallet_data
            self.wallet_id = wallet_data['id']
            
            # Save wallet data to file
            with open(self.wallet_data_file, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            
            logger.info(f"Created new Privy wallet for debate {self.debate_id}")
            logger.info(f"Wallet ID: {self.wallet_id}")
            logger.info(f"Wallet Address: {wallet_data['address']}")
            
        except Exception as e:
            logger.error(f"Failed to create Privy wallet: {str(e)}")
            raise

    def _initialize_agent(self):
        """Initialize the CDP agent with wallet and tools."""
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            # openai_api_base=os.getenv("DEEPSEEK_BASE_URL"),
            # openai_api_key=os.getenv("DEEPSEEK_API_KEY")
            openai_api_base=os.getenv("GPTUS_BASE_URL"),
            openai_api_key=os.getenv("GPTUS_API_KEY")
        )

        # Load the Privy wallet data
        wallet_data = None
        if os.path.exists(self.wallet_data_file):
            logger.info(f"Loading Privy wallet data for debate: {self.debate_id}")
            with open(self.wallet_data_file) as f:
                wallet_data = json.load(f)

        # Configure CDP Agentkit with Privy wallet data
        values = {}
        if wallet_data is not None:
            values = {
                "cdp_wallet_data": json.dumps(wallet_data),
                "wallet_id": wallet_data['id']
            }

        agentkit = CdpAgentkitWrapper(**values)

        # Initialize toolkit and tools
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()

        # Add Privy transfer tool
        privy_transfer_tool = get_privy_transfer_tool(agentkit)
        tools.append(privy_transfer_tool)

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
                "Your primary responsibilities include managing funds, tracking expenses, "
                "and ensuring proper distribution of rewards using your Privy wallet. "
                f"Your Privy wallet ID is {self.wallet_id}. You should always verify "
                "wallet balances before making transactions and maintain detailed logs "
                "of all financial activities. You can transfer funds using the privy_transfer "
                "tool. You can also deploy and manage NFTs. If you ever need funds, you can "
                "request them from the faucet if you are on network ID 'base-sepolia'."
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
        """Get the wallet address for this judge agent."""
        try:
            # Check cache first
            cached_response = self._get_cached_response("get_wallet_address", debate_id=self.debate_id)
            if cached_response is not None:
                logger.info("Using cached wallet address")
                return cached_response

            # Get address from Privy wallet data
            if not self.privy_wallet or 'address' not in self.privy_wallet:
                raise ValueError("Privy wallet not initialized or missing address")
            
            wallet_address = self.privy_wallet['address']
            logger.info(f"Retrieved wallet address for debate: {self.debate_id}")
            
            # Cache the response
            self._set_cached_response("get_wallet_address", wallet_address, debate_id=self.debate_id)
            
            return wallet_address
            
        except Exception as e:
            logger.error(f"Error getting wallet address: {str(e)}")
            raise

    def check_funding_status(self) -> bool:
        """Check if the judge wallet has the required funding amount using Web3.
        
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

            # Get wallet address
            wallet_address = self.privy_wallet['address']
            
            # Initialize Web3 with Base Sepolia RPC URL
            w3 = Web3(Web3.HTTPProvider(NETWORK_RPC_URLS["base sepolia"]))
            
            # Check if connection is successful
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to Base Sepolia network")
            
            # Get balance in Wei
            balance_wei = w3.eth.get_balance(wallet_address)
            balance_eth = Web3.from_wei(balance_wei, 'ether')
            
            # Convert required funding to Wei for comparison
            required_wei = Web3.to_wei(self.funding_amount_eth, 'ether')
            
            # Check if balance is sufficient
            has_sufficient_funds = balance_wei >= required_wei
            
            # Create detailed response
            response = str(has_sufficient_funds)
            
            # Log the balance information
            logger.info(f"Wallet balance: {balance_eth} ETH")
            logger.info(f"Required balance: {self.funding_amount_eth} ETH")
            if has_sufficient_funds:
                logger.info("Sufficient funds available")
            else:
                logger.warning(f"Insufficient funds. Required: {self.funding_amount_eth} ETH, Available: {balance_eth} ETH")
            
            # Cache the response
            self._set_cached_response("check_funding_status", response,
                debate_id=self.debate_id,
                funding_amount_eth=self.funding_amount_eth
            )
            
            return has_sufficient_funds
                
        except Exception as e:
            logger.error(f"Error checking funding status: {str(e)}")
            raise

    def request_faucet(self) -> str:
        """Request funds from the faucet."""
        try:
            # Check cache first
            cached_response = self._get_cached_response("request_faucet", debate_id=self.debate_id)
            if cached_response is not None:
                logger.info("Using cached faucet request response")
                return cached_response

            message = "Request funds from the faucet to get some test tokens."
            response = None
            logger.info("Requesting faucet funds...")
            
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
        """Mint an NFT from an existing contract using debate ID and history as metadata.
        
        Args:
            contract_address (str): The address of the NFT contract
            debate_history (str): The history of the debate discussion
            debate_result (bool): The result of the debate
            
        Returns:
            str: Response from the minting operation
        """
        try:
            # Get our own wallet address first
            wallet_address = self.get_wallet_address()
            logger.info(f"Using wallet address for NFT minting: {wallet_address}")
            
            # Create metadata including funding details and debate history
            metadata = (
                f"data:application/json,{{\"name\":\"Debate NFT\","
                f"\"description\":\"NFT for debate {self.debate_id}\","
                f"\"debate_id\":\"{self.debate_id}\","
                f"\"funding_amount_eth\":\"{self.funding_amount_eth}\","
                f"\"target_address\":\"{self.target_address}\","
                f"\"debate_history\":\"{debate_history}\","
                f"\"debate_result\":\"{debate_result}\","
                f"\"timestamp\":\"{datetime.datetime.now().isoformat()}\"}}"
            )
            
            # Check cache first
            cached_response = self._get_cached_response("mint_nft", 
                debate_id=self.debate_id,
                contract_address=contract_address,
                wallet_address=wallet_address,
                metadata=metadata
            )
            if cached_response is not None:
                logger.info("Using cached NFT minting response")
                return cached_response
            
            message = (
                f"Mint an NFT from contract {contract_address} to my current wallet address "
                f"with token ID 1 and token URI {metadata} for record keeping."
            )
            response = None
            logger.info(f"Minting NFT from contract: {contract_address} to wallet address: {wallet_address}")
            
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
                    wallet_address=wallet_address,
                    metadata=metadata
                )
            
            return response
        except Exception as e:
            logger.error(f"Error minting NFT: {str(e)}")
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
        """Transfer initial funds from CDP wallet to the Privy wallet for the debate.
        
        Args:
            amount_eth (float): Amount of ETH to transfer (default: 0.000099 ETH)
            
        Returns:
            str: Response from the transfer operation
        """
        try:
            # Get our Privy wallet address
            privy_address = self.privy_wallet['address']
            logger.info(f"Preparing to transfer {amount_eth} ETH to Privy wallet: {privy_address}")
            
            # Check cache first
            cached_response = self._get_cached_response("transfer_initial_funds", 
                debate_id=self.debate_id,
                amount_eth=amount_eth,
                privy_address=privy_address
            )
            if cached_response is not None:
                logger.info("Using cached transfer response")
                return cached_response

            # Construct transfer message for CDP agent
            message = (
                f"Transfer {amount_eth} ETH from your CDP wallet to my Privy wallet address {privy_address}. "
                "This is to fund the debate operations."
            )
            response = None
            logger.info("Requesting CDP agent to transfer funds...")
            
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
                    privy_address=privy_address
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error transferring initial funds: {str(e)}")
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
            use_cache=True  # Set to False to disable caching
        )
        
        # 2. Get and print the wallet address
        logger.info("Requesting wallet address...")
        wallet_address = judge.get_wallet_address()
        print(f"\nJudge Agent Wallet Address: {wallet_address}")
        
        # 3.1 Get faucet funds for gas
        logger.info("Requesting faucet funds...")
        faucet_response = judge.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # 3.2 Use CDP Agentkit to transfer initial funds to the Privy wallet
        logger.info("Transferring initial funds to Privy wallet...")
        transfer_response = judge.transfer_initial_funds()
        print(f"\nInitial Fund Transfer Response: {transfer_response}")
        
        # 4. Check funding status
        logger.info("Checking funding status...")
        funding_status = judge.check_funding_status()
        print(f"\nFunding Status: {'Funds Available' if funding_status else 'Insufficient Funds'}")
        
        
        
        # 5. Check if funding is available, debate can be started
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
            
            # 6. Transfer funds if debate was approved
            logger.info("Processing debate result...")
            transfer_response = judge.transfer_funds_if_approved(debate_result)
            if transfer_response:
                print(f"\nTransfer Response: {transfer_response}")
                print("\nFunds have been transferred to the target address!")
                
                # 7. Deploy NFT contract
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
                
                # 8. Mint NFT after successful transfer with debate history
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
