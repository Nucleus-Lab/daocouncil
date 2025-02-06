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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        load_dotenv()
        
        logger.info(f"Initializing JudgeAgent for debate: {debate_id}")
        logger.info(f"Target address: {target_address}")
        logger.info(f"Required funding: {funding_amount_eth} ETH")
        logger.info(f"Cache enabled: {use_cache}")
        self.agent_executor, self.config = self._initialize_agent()

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

        # Load existing wallet data if available
        wallet_data = None
        if os.path.exists(self.wallet_data_file):
            logger.info(f"Loading existing wallet data for debate: {self.debate_id}")
            with open(self.wallet_data_file) as f:
                wallet_data = f.read()

        # Configure CDP Agentkit
        values = {}
        if wallet_data is not None:
            values = {"cdp_wallet_data": wallet_data}

        agentkit = CdpAgentkitWrapper(**values)

        # Persist the wallet data
        wallet_data = agentkit.export_wallet()
        with open(self.wallet_data_file, "w") as f:
            f.write(wallet_data)

        # Initialize toolkit and tools
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()

        # Set up memory and config
        memory = MemorySaver()
        config = {"configurable": {"thread_id": f"DAO_Judge_{self.debate_id}"}}

        # Create ReAct Agent using the LLM and CDP Agentkit tools
        return create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=(
                "You are a responsible judge AI agent for a DAO debate. "
                "Your primary responsibilities include managing funds, tracking expenses, "
                "and ensuring proper distribution of rewards. You should always verify "
                "wallet balances before making transactions and maintain detailed logs "
                "of all financial activities. You can also deploy and manage NFTs. If "
                "you ever need funds, you can request them from the faucet if you are on "
                "network ID 'base-sepolia'. Before executing your first action, get the "
                "wallet details to see what network you're on."
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

            # Execute the get_wallet_details action to retrieve the address
            message = "What is my wallet address?"
            response = None
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]}, 
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info(f"Retrieved wallet address for debate: {self.debate_id}")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("get_wallet_address", response, debate_id=self.debate_id)
            
            return response
        except Exception as e:
            logger.error(f"Error getting wallet address: {str(e)}")
            raise

    def check_funding_status(self) -> bool:
        """Check if the judge wallet has the required funding amount.
        
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
                response = cached_response
            else:
                message = (
                    f"Check my ETH balance to see if I have at least {self.funding_amount_eth} ETH. "
                    "Start your response with either '[SUFFICIENT]' or '[INSUFFICIENT]' "
                    "followed by the detailed balance information."
                )
                response = None
                logger.info("Checking wallet balance...")
                
                for chunk in self.agent_executor.stream(
                    {"messages": [HumanMessage(content=message)]},
                    self.config
                ):
                    if "agent" in chunk:
                        response = chunk["agent"]["messages"][0].content
                        logger.info("Balance check response received")
                    elif "tools" in chunk:
                        logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                    print("-------------------")
                
                # Cache the response
                if response:
                    self._set_cached_response("check_funding_status", response,
                        debate_id=self.debate_id,
                        funding_amount_eth=self.funding_amount_eth
                    )
            
            # Log the full response for debugging
            logger.info(f"Full response: {response}")
            
            # Check for keywords in response
            has_sufficient_funds = "[SUFFICIENT]" in response
            
            if has_sufficient_funds:
                logger.info("Sufficient funds available")
            else:
                logger.warning(f"Insufficient funds. Required: {self.funding_amount_eth} ETH")
            
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
        """Transfer funds to target address if debate result is approved.
        
        Args:
            debate_result (bool): True if debate was approved, False if rejected
            
        Returns:
            Optional[str]: Transfer response if successful, None if debate was rejected
        """
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

            # Construct transfer message
            message = f"Transfer {self.funding_amount_eth} ETH to address {self.target_address}"
            response = None
            logger.info(f"Initiating transfer of {self.funding_amount_eth} ETH to {self.target_address}")
            
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
        
        # 3. Get faucet funds for gas
        logger.info("Requesting faucet funds...")
        faucet_response = judge.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # 4. Deploy NFT contract
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
        
        # 5. Request faucet funds (to simulate DAO depositing funds into the AI agent)
        logger.info("Requesting faucet funds...")
        faucet_response = judge.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # 6. Check funding status
        logger.info("Checking funding status...")
        funding_status = judge.check_funding_status()
        print(f"\nFunding Status: {'Funds Available' if funding_status else 'Insufficient Funds'}")
        
        # Simulate debate history (in real implementation, this would come from the debate system)
        debate_history = """
        Participant 1: I propose we allocate funds for project X
        Participant 2: What are the expected returns?
        Participant 1: We expect 20% ROI in 6 months
        Participant 2: That sounds reasonable, I support this
        Moderator: The proposal has received majority support
        """
        
        # 7. Check if funding is available, debate can be started
        if funding_status:
            print("\nDebate can be started!")
            
            # Simulate debate result (in real implementation, this would come from the debate system)
            debate_result = True  # For testing, assume debate was approved
            
            # 8. Transfer funds if debate was approved
            logger.info("Processing debate result...")
            transfer_response = judge.transfer_funds_if_approved(debate_result)
            if transfer_response:
                print(f"\nTransfer Response: {transfer_response}")
                print("\nFunds have been transferred to the target address!")
                
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
