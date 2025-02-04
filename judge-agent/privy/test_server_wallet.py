import os
import requests
import logging
from dotenv import load_dotenv
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Network configurations
NETWORK_IDS = {
    "ethereum": "eip155:1",
    "sepolia": "eip155:11155111",
    "base": "eip155:8453",
    "base sepolia": "eip155:84532",
    "base goerli": "eip155:84531"
}

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
        
        # Prepare headers and data
        headers = {
            'Content-Type': 'application/json',
            'privy-app-id': self.privy_app_id
        }
        
        data = {
            'chain_type': 'ethereum'
        }
        
        logger.info("Creating new server wallet...")
        
        try:
            # Make the request
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                auth=(self.privy_app_id, self.privy_app_secret)
            )
            
            response.raise_for_status()  # Raise an exception for bad status codes
            
            wallet_data = response.json()
            logger.info(f"Successfully created wallet with address: {wallet_data.get('address')}")
            return wallet_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            if hasattr(e.response, 'json'):
                logger.error(f"Error details: {e.response.json()}")
            raise

    def _eth_to_wei(self, eth_amount):
        """
        Convert ETH to Wei
        1 ETH = 10^18 Wei
        """
        try:
            wei_value = int(Decimal(str(eth_amount)) * Decimal('1000000000000000000'))
            logger.info(f"Converting {eth_amount} ETH to {wei_value} Wei")
            return wei_value
        except Exception as e:
            logger.error(f"Error converting ETH to Wei: {str(e)}")
            raise

    def send_transaction(self, wallet_id, recipient_address, eth_amount, network="base sepolia"):
        """
        Send a transaction using the specified wallet
        
        Args:
            wallet_id (str): The ID of the wallet to send from
            recipient_address (str): The recipient's Ethereum address
            eth_amount (float): The amount to send in ETH
            network (str): The network name (default is "base sepolia")
        
        Returns:
            dict: Transaction response data including the transaction hash
        """
        endpoint = f"{self.base_url}/wallets/{wallet_id}/rpc"
        
        headers = {
            'Content-Type': 'application/json',
            'privy-app-id': self.privy_app_id
        }
        
        # Convert ETH to Wei
        wei_value = self._eth_to_wei(eth_amount)
        
        # Get network ID from the network name
        network_id = NETWORK_IDS.get(network.lower())
        if not network_id:
            raise ValueError(f"Unsupported network: {network}. Supported networks: {', '.join(NETWORK_IDS.keys())}")
        
        logger.info(f"Using network: {network} ({network_id})")
        
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
        
        logger.info(f"Sending transaction to {recipient_address} with value {eth_amount} ETH ({wei_value} Wei)")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                auth=(self.privy_app_id, self.privy_app_secret)
            )
            
            response.raise_for_status()
            
            tx_data = response.json()
            logger.info(f"Transaction sent successfully. Transaction hash: {tx_data.get('hash')}")
            return tx_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send transaction: {str(e)}")
            if hasattr(e.response, 'json'):
                logger.error(f"Error details: {e.response.json()}")
            raise

def main():
    # user defined values
    network = "base sepolia"  # Using Base Sepolia testnet
    recipient = "0xYourRecipientAddress"  # Replace with actual recipient address
    eth_amount = 0.01  # Amount in ETH
    
    try:
        # Initialize the Privy wallet client
        privy_wallet = PrivyServerWallet()
        
        # Create a new wallet
        wallet = privy_wallet.create_wallet()
        print("\nWallet Created Successfully!")
        print(f"Wallet ID: {wallet['id']}")
        print(f"Wallet Address: {wallet['address']}")
        
        print("\nSending transaction...")
        tx = privy_wallet.send_transaction(
            wallet_id=wallet['id'],
            recipient_address=recipient,
            eth_amount=eth_amount,
            network=network
        )
        print(f"Transaction sent! Hash: {tx.get('hash')}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
