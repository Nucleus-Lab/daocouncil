from dotenv import load_dotenv
import os
import requests
from typing import Dict, Any

class PrivyWalletTools:
    def __init__(self):
        load_dotenv()
        self.privy_app_id = os.getenv('PRIVY_APP_ID')
        self.privy_app_secret = os.getenv('PRIVY_APP_SECRET')
        self.base_url = "https://api.privy.io/v1"

        if not self.privy_app_id or not self.privy_app_secret:
            raise ValueError("PRIVY_APP_ID and PRIVY_APP_SECRET must be set in .env file")

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
            
            print("Creating new Privy wallet...")
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                auth=(self.privy_app_id, self.privy_app_secret)
            )
            
            response.raise_for_status()
            wallet_data = response.json()
            
            print(f"Successfully created Privy wallet with address: {wallet_data.get('address')}")
            return wallet_data
            
        except Exception as e:
            error_msg = f"Failed to create Privy wallet: {str(e)}"
            print(error_msg)
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                print(f"Error details: {e.response.json()}")
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
            
            print(f"Initiating Privy transfer of {amount_eth} ETH to {recipient_address}")
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                auth=(self.privy_app_id, self.privy_app_secret)
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"Transfer successful. Transaction hash: {result.get('hash')}")
            return f"Successfully transferred {amount_eth} ETH to {recipient_address}. Transaction hash: {result.get('hash')}"
            
        except Exception as e:
            error_msg = f"Failed to transfer ETH: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)