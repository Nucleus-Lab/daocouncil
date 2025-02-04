import os
import logging
import json
from typing import Optional, Dict, Any
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

# # Privy wallet creation tool description
# PRIVY_CREATE_WALLET_PROMPT = """
# This tool will create a new Privy wallet using the Privy API.
# The wallet will be used as a vault for debate funds.
# """

# Add new tool description
PRIVY_GET_OR_CREATE_WALLET_PROMPT = """
This tool will get an existing Privy wallet for a debate ID or create a new one if it doesn't exist.
The wallet will be used as a vault for the debate funds.
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

# class PrivyCreateWalletInput(BaseModel):
#     """Input argument schema for Privy wallet creation."""
#     chain_type: str = Field(
#         default="ethereum",
#         description="The chain type for the wallet (default: ethereum)"
#     )

# Add new input schema
class PrivyGetOrCreateWalletInput(BaseModel):
    """Input argument schema for getting or creating a Privy wallet."""
    debate_id: str = Field(
        ...,
        description="The unique identifier for the debate"
    )
    chain_type: str = Field(
        default="ethereum",
        description="The chain type for the wallet (default: ethereum)"
    )

class PrivyWalletTools:
    def __init__(self):
        load_dotenv()
        self.privy_app_id = os.getenv('PRIVY_APP_ID')
        self.privy_app_secret = os.getenv('PRIVY_APP_SECRET')
        self.base_url = "https://api.privy.io/v1"

        if not self.privy_app_id or not self.privy_app_secret:
            raise ValueError("PRIVY_APP_ID and PRIVY_APP_SECRET must be set in .env file")

        # Add wallet storage path
        self.wallet_storage_path = "debate_wallets.json"
        self._ensure_wallet_storage()

    def _ensure_wallet_storage(self):
        """Ensure the wallet storage file exists."""
        if not os.path.exists(self.wallet_storage_path):
            with open(self.wallet_storage_path, 'w') as f:
                json.dump({}, f)
            logger.info(f"Created wallet storage file: {self.wallet_storage_path}")

    def _get_stored_wallet(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """Get stored wallet data for a debate ID."""
        try:
            with open(self.wallet_storage_path, 'r') as f:
                wallets = json.load(f)
                return wallets.get(debate_id)
        except Exception as e:
            logger.error(f"Error reading stored wallet: {str(e)}")
            return None

    def _store_wallet(self, debate_id: str, wallet_data: Dict[str, Any]):
        """Store wallet data for a debate ID."""
        try:
            with open(self.wallet_storage_path, 'r') as f:
                wallets = json.load(f)
            
            wallets[debate_id] = wallet_data
            
            with open(self.wallet_storage_path, 'w') as f:
                json.dump(wallets, f, indent=2)
            
            logger.info(f"Stored wallet data for debate: {debate_id}")
        except Exception as e:
            logger.error(f"Error storing wallet: {str(e)}")
            raise

    def get_or_create_wallet(self, debate_id: str, chain_type: str = "ethereum") -> Dict[str, Any]:
        """Get existing wallet for debate ID or create new one.
        
        Args:
            debate_id (str): The unique identifier for the debate
            chain_type (str): The chain type for the wallet
            
        Returns:
            Dict[str, Any]: The wallet data
        """
        try:
            # Check for existing wallet
            existing_wallet = self._get_stored_wallet(debate_id)
            if existing_wallet:
                logger.info(f"Found existing wallet for debate: {debate_id}")
                return existing_wallet

            # Create new wallet if none exists
            logger.info(f"No existing wallet found for debate: {debate_id}, creating new one...")
            wallet_data = self.create_wallet(chain_type)
            
            # Store the new wallet
            self._store_wallet(debate_id, wallet_data)
            
            return wallet_data
            
        except Exception as e:
            error_msg = f"Failed to get or create wallet: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def create_wallet(self, chain_type: str = "ethereum") -> Dict[str, Any]:
        """Create a new Privy wallet.
        
        Args:
            chain_type (str): The chain type for the wallet (default: ethereum)
            
        Returns:
            Dict[str, Any]: The created wallet data
        """
        try:
            endpoint = f"{self.base_url}/wallets"
            
            headers = {
                'Content-Type': 'application/json',
                'privy-app-id': self.privy_app_id
            }
            
            data = {
                'chain_type': chain_type
            }
            
            logger.info("Creating new Privy wallet...")
            
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
            
        except Exception as e:
            error_msg = f"Failed to create Privy wallet: {str(e)}"
            logger.error(error_msg)
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                logger.error(f"Error details: {e.response.json()}")
            raise ValueError(error_msg)

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

def privy_get_or_create_wallet(wallet: Wallet, debate_id: str, chain_type: str = "ethereum") -> str:
    """CDP Tool function for getting or creating Privy wallet.
    
    Args:
        wallet (Wallet): CDP wallet (not used but required by CDP Tool interface)
        debate_id (str): The unique identifier for the debate
        chain_type (str): The chain type for the wallet
        
    Returns:
        str: JSON string containing the wallet data
    """
    try:
        privy_tools = PrivyWalletTools()
        wallet_data = privy_tools.get_or_create_wallet(debate_id, chain_type)
        return f"Successfully retrieved/created Privy wallet for debate {debate_id}. Wallet data: {wallet_data}"
    except Exception as e:
        error_msg = f"Failed to get/create Privy wallet: {str(e)}"
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
            name="privy_get_or_create_wallet",
            description=PRIVY_GET_OR_CREATE_WALLET_PROMPT,
            cdp_agentkit_wrapper=agentkit,
            args_schema=PrivyGetOrCreateWalletInput,
            func=privy_get_or_create_wallet,
        ),
        CdpTool(
            name="privy_transfer",
            description=PRIVY_TRANSFER_PROMPT,
            cdp_agentkit_wrapper=agentkit,
            args_schema=PrivyTransferInput,
            func=privy_transfer,
        )
    ]
