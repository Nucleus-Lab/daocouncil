import os
from dotenv import load_dotenv
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.agent_toolkits import CdpToolkit
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from cdp_agentkit_custom_tools import get_privy_tools
import logging
from langchain.schema import HumanMessage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JudgeAgent:
    def __init__(self, debate_id: str):
        """Initialize a judge agent for a specific debate.
        
        Args:
            debate_id (str): Unique identifier for the debate
            target_address (str): The wallet address that will receive funds if debate passes
            funding_amount_eth (float): Amount of ETH required for the debate
        """
        self.debate_id = debate_id
        self.wallet_data_file = f"wallet_data_{debate_id}.txt"
        self.privy_wallet = None  # Will be set during initialization
        self.wallet_id = None     # Will be set during initialization
        load_dotenv()

        logger.info(f"Initializing JudgeAgent for debate: {debate_id}")
        
        # Initialize the agent and get the debate vault wallet
        self.agent_executor, self.config = self._initialize_agent()
        
    def _initialize_agent(self):
        """Initialize the CDP agent with wallet and tools."""
        # Initialize LLM
        llm = ChatOpenAI(
            model=os.getenv("MODEL"),
            temperature=0,
            openai_api_base=os.getenv("OPENAI_BASE_URL"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
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
                "You have a CDP wallet for agent operations and you are managing multiple Privy wallets for different debates. "
                "You should always verify wallet balances before making transactions and maintain detailed logs"
                "of all financial activities. You can create debate vault using privy_create_wallet tool. "
                "You can transfer funds from the debate vault wallet to any target address using the privy_transfer tool. "
                "If it is a transfer from the CDP wallet to other wallets, you should use the CDP transfer tool. "
                "You can also deploy and manage NFTs. If you ever need funds, you can "
                "request them from the faucet if you are on network ID 'base-sepolia'."
            ),
        ), config
        
    def chat(self, message: str) -> str:
        """Send a message to the agent and get its response.
        
        This is a general-purpose chat function that can handle any formatted message
        and interact with the agent. It will process the message through the agent's
        tools and return the response.
        
        Args:
            message (str): The message to send to the agent
            
        Returns:
            str: The agent's response
        """
        try:
            logger.info("Processing message through agent...")
            response = None
            tool_outputs = []
            
            # Stream the interaction with the agent
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info("Agent response received")
                elif "tools" in chunk:
                    tool_message = chunk['tools']['messages'][0].content
                    logger.info(f"Tool execution: {tool_message}")
                    tool_outputs.append(tool_message)
                print("-------------------")
            
            # If we got no response but have tool outputs, combine them
            if not response and tool_outputs:
                response = "\n".join(tool_outputs)
                
            if not response:
                raise ValueError("No response received from agent")
                
            logger.info("Message processing completed")
            return response
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
