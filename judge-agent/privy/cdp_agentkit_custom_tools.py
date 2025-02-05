import logging
from pydantic import BaseModel, Field
from cdp_langchain.tools import CdpTool
from cdp import Wallet
from privy_wallet_tools import PrivyWalletTools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Privy transfer tool description
PRIVY_TRANSFER_PROMPT = """
This tool will transfer ETH from a Privy wallet to another address using the Privy API.
The tool requires the wallet ID, recipient address, and amount in ETH.
Use the transaction hash from the tool, format it into the transaction link on the network you are using and return it.
For example, if the transaction is on base-sepolia, the transaction link is https://sepolia.basescan.org/tx/<transaction_hash>
"""


# Privy wallet creation tool description
PRIVY_CREATE_WALLET_PROMPT = """
This tool will create a new Privy wallet using the Privy API.
The wallet will be used as a vault for debate funds.
"""

class PrivyTransferInput(BaseModel):
    """Input argument schema for Privy transfer action."""
    wallet_id: str = Field(
        ...,
        description="The ID of the Privy wallet to send from"
    )
    recipient_address: str = Field(
        ...,
        description="The recipient's Ethereum address"
    )
    amount_eth: float = Field(
        ...,
        description="The amount of ETH to send"
    )
    network: str = Field(
        default="base sepolia",
        description="The network to use (default: base sepolia)"
    )

class PrivyCreateWalletInput(BaseModel):
    """Input argument schema for Privy wallet creation."""
    chain_type: str = Field(
        default="ethereum",
        description="The chain type for the wallet (default: ethereum)"
    )



def privy_create_wallet(wallet: Wallet, chain_type: str = "ethereum") -> str:
    """CDP Tool function for creating Privy wallet.
    
    Args:
        wallet (Wallet): CDP wallet (not used but required by CDP Tool interface)
        chain_type (str): The chain type for the wallet
        
    Returns:
        str: JSON string containing the created wallet data
    """
    try:
        privy_tools = PrivyWalletTools()
        wallet_data = privy_tools.create_wallet(chain_type)
        return f"Successfully created Privy wallet. Wallet data: {wallet_data}"
    except Exception as e:
        error_msg = f"Failed to create Privy wallet: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def privy_transfer(wallet: Wallet, wallet_id: str, recipient_address: str, amount_eth: float, network: str = "base sepolia") -> str:
    """CDP Tool function for Privy transfer.
    
    Args:
        wallet (Wallet): CDP wallet (not used but required by CDP Tool interface)
        wallet_id (str): The ID of the Privy wallet to send from
        recipient_address (str): The recipient's Ethereum address
        amount_eth (float): Amount of ETH to send
        network (str): Network to use
        
    Returns:
        str: Transfer result message
    """
    privy_tools = PrivyWalletTools()
    return privy_tools.transfer_eth(wallet_id, recipient_address, amount_eth, network)

def get_privy_tools(agentkit) -> list[CdpTool]:
    """Create CDP Tools for Privy operations.
    
    Args:
        agentkit: The CDP Agentkit wrapper instance
        
    Returns:
        list[CdpTool]: List of Privy tools
    """
    return [
        CdpTool(
            name="privy_create_wallet",
            description=PRIVY_CREATE_WALLET_PROMPT,
            cdp_agentkit_wrapper=agentkit,
            args_schema=PrivyCreateWalletInput,
            func=privy_create_wallet,
        ),
        CdpTool(
            name="privy_transfer",
            description=PRIVY_TRANSFER_PROMPT,
            cdp_agentkit_wrapper=agentkit,
            args_schema=PrivyTransferInput,
            func=privy_transfer,
        )
    ] 