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
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JudgeAgent, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize a singleton judge agent that handles multiple debates."""
        if self._initialized:
            return
            
        logger.info("Initializing singleton JudgeAgent")
        self.debate_wallets = {}  # Map debate_ids to their wallet data
        load_dotenv()
        
        # Initialize the agent
        self.agent_executor, self.config = self._initialize_agent()
        self._initialized = True
        
    def _initialize_agent(self):
        """Initialize the CDP agent with wallet and tools."""
        # Initialize LLM
        llm = ChatOpenAI(
            model=os.getenv("MODEL"),
            temperature=0,
            openai_api_base=os.getenv("MODEL_BASE_URL"),
            openai_api_key=os.getenv("MODEL_API_KEY")
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
        config = {"configurable": {"thread_id": "DAO_Judge_Global"}}

        # Create ReAct Agent with updated state modifier
        return create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=(
                "You are a responsible judge AI agent for multiple DAO debates. "
                "You have a CDP wallet for agent operations and you are managing multiple Privy wallets for different debates. "
                "You should always verify wallet balances before making transactions and maintain detailed logs "
                "of all financial activities. You can create debate vault using privy_create_wallet tool. "
                "You can transfer funds from the debate vault wallet to any target address using the privy_transfer tool. "
                "If it is a transfer from the CDP wallet to other wallets, you should use the CDP transfer tool. "
                "You can also deploy and manage NFTs. If you ever need funds, you can "
                "request them from the faucet if you are on network ID 'base-sepolia'."
            ),
        ), config
        
    def get_wallet_for_debate(self, debate_id: str):
        """Get or create wallet data for a specific debate."""
        if debate_id not in self.debate_wallets:
            logger.info(f"Creating new wallet data for debate: {debate_id}")
            self.debate_wallets[debate_id] = {
                'wallet_data_file': f"wallet_data_{debate_id}.txt",
                'privy_wallet': None,
                'wallet_id': None
            }
        return self.debate_wallets[debate_id]
        
    def chat(self, debate_id: str, message: str) -> str:
        """Send a message to the agent and get its response.
        
        Args:
            debate_id (str): The ID of the debate this message is related to
            message (str): The message to send to the agent
            
        Returns:
            str: The agent's response
        """
        try:
            # Get wallet data for this debate
            wallet_data = self.get_wallet_for_debate(debate_id)
            
            # Add debate context to the message
            contextualized_message = f"[Debate ID: {debate_id}] {message}"
            logger.info(f"Processing message for debate {debate_id}")
            
            response = None
            tool_outputs = []
            
            # Stream the interaction with the agent
            for chunk in self.agent_executor.stream(
                {"messages": [HumanMessage(content=contextualized_message)]},
                self.config
            ):
                if "agent" in chunk:
                    response = chunk["agent"]["messages"][0].content
                    logger.info(f"Agent response received for debate {debate_id}")
                elif "tools" in chunk:
                    tool_message = chunk['tools']['messages'][0].content
                    logger.info(f"Tool execution for debate {debate_id}: {tool_message}")
                    tool_outputs.append(tool_message)
                print("-------------------")
            
            # If we got no response but have tool outputs, combine them
            if not response and tool_outputs:
                response = "\n".join(tool_outputs)
                
            if not response:
                raise ValueError("No response received from agent")
                
            logger.info(f"Message processing completed for debate {debate_id}")
            return response
            
        except Exception as e:
            error_msg = f"Error processing message for debate {debate_id}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
