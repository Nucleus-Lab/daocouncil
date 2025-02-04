import os
import logging
from typing import Optional
from pydantic import BaseModel, Field
from cdp_langchain.tools import CdpTool
from cdp import Wallet
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Privy transfer tool description
PRIVY_TRANSFER_PROMPT = """
This tool will transfer ETH from a Privy wallet to another address using the Privy API.
The tool requires the wallet ID, recipient address, and amount in ETH.
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

class PrivyWalletTools:
    def __init__(self):
        load_dotenv()
        self.privy_app_id = os.getenv('PRIVY_APP_ID')
        self.privy_app_secret = os.getenv('PRIVY_APP_SECRET')
        self.base_url = "https://api.privy.io/v1"

        if not self.privy_app_id or not self.privy_app_secret:
            raise ValueError("PRIVY_APP_ID and PRIVY_APP_SECRET must be set in .env file")

    def transfer_eth(self, wallet_id: str, recipient_address: str, amount_eth: float, network: str = "base sepolia") -> str:
        """Transfer ETH using Privy wallet.
        
        Args:
            wallet_id (str): The ID of the Privy wallet to send from
            recipient_address (str): The recipient's Ethereum address
            amount_eth (float): Amount of ETH to send
            network (str): Network to use (default: base sepolia)
            
        Returns:
            str: Transaction response
        """
        try:
            # Network ID mapping
            NETWORK_IDS = {
                "base sepolia": "eip155:84532",
                "base": "eip155:8453",
                "ethereum": "eip155:1",
                "sepolia": "eip155:11155111"
            }
            
            network_id = NETWORK_IDS.get(network.lower())
            if not network_id:
                raise ValueError(f"Unsupported network: {network}")

            # Convert ETH to Wei
            wei_value = int(amount_eth * 10**18)
            
            endpoint = f"{self.base_url}/wallets/{wallet_id}/rpc"
            
            headers = {
                'Content-Type': 'application/json',
                'privy-app-id': self.privy_app_id
            }
            
            data = {
                "method": "eth_sendTransaction",
                "caip2": network_id,
                "params": {
                    "transaction": {
                        "to": recipient_address,
                        "value": wei_value
                    }
                }
            }
            
            logger.info(f"Initiating Privy transfer of {amount_eth} ETH to {recipient_address}")
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                auth=(self.privy_app_id, self.privy_app_secret)
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Transfer successful. Transaction hash: {result.get('hash')}")
            return f"Successfully transferred {amount_eth} ETH to {recipient_address}. Transaction hash: {result.get('hash')}"
            
        except Exception as e:
            error_msg = f"Failed to transfer ETH: {str(e)}"
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

def get_privy_transfer_tool(agentkit) -> CdpTool:
    """Create a CDP Tool for Privy transfers.
    
    Args:
        agentkit: The CDP Agentkit wrapper instance
        
    Returns:
        CdpTool: The Privy transfer tool
    """
    return CdpTool(
        name="privy_transfer",
        description=PRIVY_TRANSFER_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=PrivyTransferInput,
        func=privy_transfer,
    )
