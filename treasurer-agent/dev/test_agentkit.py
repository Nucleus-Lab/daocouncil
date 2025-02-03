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
from custom_tools import get_custom_tools

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

class TreasurerAgent:
    def __init__(self, debate_id: str, target_address: str, funding_amount_eth: float, use_cache: bool = True):
        """Initialize a treasurer agent for a specific debate.
        
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
        
        logger.info(f"Initializing TreasurerAgent for debate: {debate_id}")
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

        # Add custom tools
        custom_tools = get_custom_tools(agentkit)
        tools.extend(custom_tools)

        # Set up memory and config
        memory = MemorySaver()
        config = {"configurable": {"thread_id": f"DAO_Treasurer_{self.debate_id}"}}

        # Create ReAct Agent using the LLM and CDP Agentkit tools
        return create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=(
                "You are a responsible treasurer AI agent for a DAO debate. "
                "Your primary responsibilities include managing funds, tracking expenses, "
                "and ensuring proper distribution of rewards. You should always verify "
                "wallet balances before making transactions and maintain detailed logs "
                "of all financial activities. You can also deploy and manage NFTs with "
                "updatable metadata. If you ever need funds, you can request them from "
                "the faucet if you are on network ID 'base-sepolia'. Before executing "
                "your first action, get the wallet details to see what network you're on."
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
        """Get the wallet address for this treasurer agent."""
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
        """Check if the treasurer wallet has the required funding amount.
        
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

    def mint_nft(self, contract_address: str) -> str:
        """Mint an NFT from an existing contract using debate ID as metadata.
        
        Args:
            contract_address (str): The address of the NFT contract
            
        Returns:
            str: Response from the minting operation
        """
        try:
            # Create metadata including funding details
            metadata = f"data:application/json,{{\"name\":\"Debate NFT\",\"description\":\"NFT for debate {self.debate_id}\",\"debate_id\":\"{self.debate_id}\",\"funding_amount_eth\":\"{self.funding_amount_eth}\",\"target_address\":\"{self.target_address}\"}}"
            
            # Check cache first
            cached_response = self._get_cached_response("mint_nft", 
                debate_id=self.debate_id,
                contract_address=contract_address,
                target_address=self.target_address,
                metadata=metadata
            )
            if cached_response is not None:
                logger.info("Using cached NFT minting response")
                return cached_response
            
            message = (
                f"Mint an NFT from contract {contract_address} to address {self.target_address} "
                f"with token ID 1 and token URI {metadata}. Use the mint_updatable_nft tool for this operation."
            )
            response = None
            logger.info(f"Minting NFT from contract: {contract_address} to address: {self.target_address}")
            
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
                    target_address=self.target_address,
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

    def update_nft_with_debate_result(self, contract_address: str, token_id: int, debate_result: bool, debate_history: str) -> str:
        """Update NFT metadata with debate results and history.
        
        Args:
            contract_address (str): The NFT contract address
            token_id (int): The token ID to update
            debate_result (bool): The result of the debate
            debate_history (str): The chat history of the debate
            
        Returns:
            str: Response from the metadata update operation
        """
        try:
            # Check cache first
            cached_response = self._get_cached_response("update_nft_with_debate_result", 
                debate_id=self.debate_id,
                contract_address=contract_address,
                token_id=token_id,
                debate_result=debate_result
            )
            if cached_response is not None:
                logger.info("Using cached NFT metadata update response")
                return cached_response

            # Create updated metadata
            metadata = {
                "name": f"Debate NFT - {self.debate_id}",
                "description": f"NFT for debate {self.debate_id}",
                "debate_id": self.debate_id,
                "funding_amount_eth": str(self.funding_amount_eth),
                "target_address": self.target_address,
                "debate_result": "Approved" if debate_result else "Rejected",
                "debate_history": debate_history,
                "updated_at": f"{datetime.datetime.now().isoformat()}"
            }
            
            # Convert to data URI format
            metadata_uri = f"data:application/json,{json.dumps(metadata)}"
            
            message = f"Update the metadata for token {token_id} in NFT contract {contract_address} with new URI: {metadata_uri}"
            response = None
            logger.info(f"Updating NFT metadata for token {token_id} with debate results")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("NFT metadata update response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("update_nft_with_debate_result", response,
                    debate_id=self.debate_id,
                    contract_address=contract_address,
                    token_id=token_id,
                    debate_result=debate_result
                )
            
            return response
        except Exception as e:
            logger.error(f"Error updating NFT metadata with debate result: {str(e)}")
            raise

    def deploy_updatable_nft_contract(self) -> str:
        """Deploy a new updatable NFT contract for the debate using custom tool.
        
        Returns:
            str: The deployment response with contract address
        """
        try:
            # Check cache first
            cached_response = self._get_cached_response("deploy_updatable_nft_contract", 
                debate_id=self.debate_id,
                contract_name=f"Debate NFT {self.debate_id}"
            )
            if cached_response is not None:
                logger.info("Using cached updatable NFT contract deployment response")
                return cached_response

            message = (
                f"Deploy a new updatable NFT contract with name 'Debate NFT {self.debate_id}' "
                f"and symbol 'DEBATE'. Use the deploy_updatable_nft tool for this deployment."
            )
            response = None
            logger.info("Deploying updatable NFT contract...")
            
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("Updatable NFT contract deployment response received")
                elif "tools" in chunk:
                    logger.info(f"Tool execution: {chunk['tools']['messages'][0].content}")
                print("-------------------")
            
            # Cache the response
            if response:
                self._set_cached_response("deploy_updatable_nft_contract", response,
                    debate_id=self.debate_id,
                    contract_name=f"Debate NFT {self.debate_id}"
                )
            
            return response
        except Exception as e:
            logger.error(f"Error deploying updatable NFT contract: {str(e)}")
            raise

def main():
    """Test the TreasurerAgent implementation."""
    try:
        # Create a treasurer agent for a test debate
        debate_id = "test_debate_001"
        target_address = "0xBd606164D19e32474CCBda3012783B218E10E52e"
        funding_amount_eth = 0.00003
        
        # Enable caching by default, can be disabled with use_cache=False
        logger.info("Creating treasurer agent...")
        treasurer = TreasurerAgent(
            debate_id=debate_id,
            target_address=target_address,
            funding_amount_eth=funding_amount_eth,
            use_cache=True  # Set to False to disable caching
        )
        
        # Get and print the wallet address
        logger.info("Requesting wallet address...")
        wallet_address = treasurer.get_wallet_address()
        print(f"\nTreasurer Agent Wallet Address: {wallet_address}")
        
        # Get faucet funds for gas
        logger.info("Requesting faucet funds...")
        faucet_response = treasurer.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # Deploy updatable NFT contract using custom tool
        logger.info("Deploying updatable NFT contract...")
        deploy_response = treasurer.deploy_updatable_nft_contract()
        print(f"\nUpdatable NFT Contract Deployment Response: {deploy_response}")
        
        # Extract contract address from deployment response
        import re
        contract_address_match = re.search(r'0x[a-fA-F0-9]{40}', deploy_response)
        if not contract_address_match:
            raise ValueError("Could not extract contract address from deployment response")
        contract_address = contract_address_match.group(0)
        logger.info(f"Extracted contract address: {contract_address}")
        
        # Mint NFT
        logger.info("Minting NFT...")
        mint_response = treasurer.mint_nft(contract_address)
        print(f"\nNFT Minting Response: {mint_response}")
        
        # Request faucet funds for gas (to simulate DAO depositing funds into the AI agent)
        logger.info("Requesting faucet funds...")
        faucet_response = treasurer.request_faucet()
        print(f"\nFaucet Response: {faucet_response}")
        
        # Check funding status
        logger.info("Checking funding status...")
        funding_status = treasurer.check_funding_status()
        print(f"\nFunding Status: {'Funds Available' if funding_status else 'Insufficient Funds'}")
        
        # Simulate debate history (in real implementation, this would come from the debate system)
        debate_history = """
        Participant 1: I propose we allocate funds for project X
        Participant 2: What are the expected returns?
        Participant 1: We expect 20% ROI in 6 months
        Participant 2: That sounds reasonable, I support this
        Moderator: The proposal has received majority support
        """
        
        # Print debate can be started if funding is available
        if funding_status:
            print("\nDebate can be started!")
            
            # Simulate debate result (in real implementation, this would come from the debate system)
            debate_result = True  # For testing, assume debate was approved
            
            # Update NFT metadata with debate result and history using custom tool
            logger.info("Updating NFT metadata with debate results...")
            update_response = treasurer.update_nft_with_debate_result(
                contract_address=contract_address,
                token_id=1,  # Assuming first token ID is 1
                debate_result=debate_result,
                debate_history=debate_history
            )
            print(f"\nNFT Metadata Update Response: {update_response}")
            
            # Transfer funds if debate was approved
            logger.info("Processing debate result...")
            transfer_response = treasurer.transfer_funds_if_approved(debate_result)
            if transfer_response:
                print(f"\nTransfer Response: {transfer_response}")
                print("\nFunds have been transferred to the target address!")
            else:
                print("\nNo funds were transferred (debate was rejected)")
        else:
            print("\nDebate cannot be started due to insufficient funds.")
            
            # Even if debate can't start due to insufficient funds, update NFT to record this
            logger.info("Updating NFT metadata with cancelled status...")
            update_response = treasurer.update_nft_with_debate_result(
                contract_address=contract_address,
                token_id=1,  # Assuming first token ID is 1
                debate_result=False,
                debate_history="Debate cancelled due to insufficient funds"
            )
            print(f"\nNFT Metadata Update Response: {update_response}")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
