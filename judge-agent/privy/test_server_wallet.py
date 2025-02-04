import os
import requests
import logging
from dotenv import load_dotenv
from decimal import Decimal
from web3 import Web3

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

# Network configurations
NETWORK_RPC_URLS = {
    "base sepolia": "https://sepolia.base.org",
    "base": "https://mainnet.base.org",
    "ethereum": "https://mainnet.ethereum.org",
    "sepolia": "https://rpc.sepolia.org"
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
    def send_transaction(self, wallet_id, recipient_address, eth_amount, network="eip155:84532"):
        """
        Send a transaction using the specified wallet
        
        Args:
            wallet_id (str): The ID of the wallet to send from
            recipient_address (str): The recipient's Ethereum address
            eth_amount (float): The amount to send in ETH
            network (str): The network name (default is "base sepolia")
            network (str): The network identifier (default is Base Sepolia)
        
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
        
        # Add gas parameters
        data = {
            "method": "eth_sendTransaction",
            "caip2": network_id,
            "params": {
                "transaction": {
                    "to": recipient_address,
                    "value": wei_value,
                    "gasLimit": "0x5208",  # 21000 gas units
                    "maxFeePerGas": "0x59682F00",  # 1.5 Gwei
                    "maxPriorityFeePerGas": "0x59682F00"  # 1.5 Gwei
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
            print("tx_data", tx_data)
            logger.info(f"Transaction sent successfully. Transaction hash: {tx_data['data'].get('hash')}")
            return tx_data
            

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send transaction: {str(e)}")
            if hasattr(e.response, 'json'):
                logger.error(f"Error details: {e.response.json()}")
            raise

    @staticmethod
    def load_wallet_from_file(filepath: str = "wallets.txt") -> dict:
        """
        Load existing wallet details from a file.
        
        Args:
            filepath (str): Path to the wallet file
            
        Returns:
            dict: Wallet data containing 'id' and 'address'
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Parse wallet ID and address from the file content
            import re
            wallet_id_match = re.search(r'Wallet ID: (\w+)', content)
            wallet_address_match = re.search(r'Wallet Address: (0x[a-fA-F0-9]{40})', content)
            
            if not wallet_id_match or not wallet_address_match:
                raise ValueError("Could not find wallet ID or address in file")
                
            wallet_data = {
                'id': wallet_id_match.group(1),
                'address': wallet_address_match.group(1)
            }
            
            logger.info(f"Loaded existing wallet: {wallet_data['address']}")
            return wallet_data
            
        except Exception as e:
            logger.error(f"Error loading wallet from file: {str(e)}")
            raise

    def use_existing_wallet(self, wallet_id: str = None, filepath: str = "wallets.txt") -> dict:
        """
        Use an existing wallet either by ID or from file.
        
        Args:
            wallet_id (str, optional): Specific wallet ID to use
            filepath (str, optional): Path to wallet file if no ID provided
            
        Returns:
            dict: Wallet data including ID and address
        """
        try:
            if wallet_id:
                # If wallet_id is provided, verify it exists
                endpoint = f"{self.base_url}/wallets/{wallet_id}"
                
                headers = {
                    'Content-Type': 'application/json',
                    'privy-app-id': self.privy_app_id
                }
                
                response = requests.get(
                    endpoint,
                    headers=headers,
                    auth=(self.privy_app_id, self.privy_app_secret)
                )
                
                response.raise_for_status()
                wallet_data = response.json()
                logger.info(f"Using existing wallet with ID: {wallet_id}")
                
            else:
                # Load wallet data from file
                wallet_data = self.load_wallet_from_file(filepath)
                logger.info(f"Using wallet from file: {filepath}")
            
            return wallet_data
            
        except Exception as e:
            logger.error(f"Error using existing wallet: {str(e)}")
            raise


    def check_balance_web3(self, wallet_address: str, network: str = "base sepolia") -> float:
        """
        Check wallet balance using Web3 on specified network.
        
        Args:
            wallet_address (str): The wallet address to check
            network (str): Network name (default: base sepolia)
            
        Returns:
            float: Balance in ETH
        """
        try:
            # Get RPC URL for the network
            rpc_url = NETWORK_RPC_URLS.get(network.lower())
            if not rpc_url:
                raise ValueError(f"Unsupported network: {network}")
            
            # Initialize Web3
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Check connection
            if not w3.is_connected():
                raise ConnectionError(f"Failed to connect to {network} network")
            
            logger.info(f"Checking balance on {network} for address: {wallet_address}")
            
            # Get balance in Wei
            balance_wei = w3.eth.get_balance(wallet_address)
            
            # Convert Wei to ETH
            balance_eth = Web3.from_wei(balance_wei, 'ether')
            
            logger.info(f"Balance on {network}: {balance_eth} ETH ({balance_wei} Wei)")
            return float(balance_eth)
            
        except Exception as e:
            logger.error(f"Failed to check balance using Web3: {str(e)}")
            raise

def main():
    # user defined values
    network = "base sepolia"  # Using Base Sepolia testnet
    recipient = "0xYourRecipientAddress"  # Replace with actual recipient address
    eth_amount = 0.01  # Amount in ETH
    
    try:
        # Initialize the Privy wallet client
        privy_wallet = PrivyServerWallet()
        
        # Example 2: Use existing wallet from file
        print("\n=== Using Existing Wallet ===")
        existing_wallet = privy_wallet.use_existing_wallet()
        print(f"Loaded Wallet ID: {existing_wallet['id']}")
        print(f"Loaded Wallet Address: {existing_wallet['address']}")
        
        # Check wallet balance using Web3
        print("\n=== Checking Wallet Balance ===")
        print("\nUsing Web3:")
        web3_balance = privy_wallet.check_balance_web3(existing_wallet['address'])
        print(f"Wallet Balance (Web3): {web3_balance} ETH")
        
        # Use the Web3 balance for transaction verification
        recipient = "0xBd606164D19e32474CCBda3012783B218E10E52e"
        eth_amount = 0.0001  # Reduced amount to leave room for gas
        
        # Calculate total cost (rough estimate)
        gas_cost_eth = 0.0000315  # 21000 * 1.5 Gwei
        total_cost = eth_amount + gas_cost_eth
        
        # Verify sufficient balance before sending
        if web3_balance >= total_cost:
            print(f"\nSending transaction from existing wallet...")
            print(f"Transfer amount: {eth_amount} ETH")
            print(f"Estimated gas cost: {gas_cost_eth} ETH")
            print(f"Total cost: {total_cost} ETH")
            
            tx = privy_wallet.send_transaction(
                wallet_id=existing_wallet['id'],
                recipient_address=recipient,
                eth_amount=eth_amount
            )
            print(f"Transaction sent! Hash: {tx.get('hash')}")
        else:
            print(f"\nInsufficient balance. Required: {total_cost} ETH (including gas), Available: {web3_balance} ETH")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
