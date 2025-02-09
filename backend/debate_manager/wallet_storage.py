import json
import os
import logging
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the storage file path
STORAGE_FILE = "debate_wallets.json"

def _ensure_storage_exists():
    """Ensure the storage file exists and is properly initialized."""
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'w') as f:
            json.dump({}, f, indent=2)

def store_debate_wallets(
    debate_id: str,
    cdp_wallet_address: str,
    privy_wallet_address: str,
    privy_wallet_id: str
) -> None:
    """Store wallet information for a debate in JSON file.
    
    Args:
        debate_id (str): Unique identifier for the debate
        cdp_wallet_address (str): CDP wallet address
        privy_wallet_address (str): Privy wallet address
        privy_wallet_id (str): Privy wallet ID
    """
    try:
        _ensure_storage_exists()
        
        # Read existing data
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
        
        # Update with new wallet info
        data[debate_id] = {
            'cdp_wallet_address': cdp_wallet_address,
            'privy_wallet_address': privy_wallet_address,
            'privy_wallet_id': privy_wallet_id
        }
        
        # Write back to file
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Stored wallet information for debate {debate_id}")
        
    except Exception as e:
        logger.error(f"Error storing wallet information: {str(e)}")
        raise

def get_debate_wallets(debate_id: str) -> Optional[Dict[str, str]]:
    """Retrieve wallet information for a debate from JSON file.
    
    Args:
        debate_id (str): Unique identifier for the debate
        
    Returns:
        Optional[Dict[str, str]]: Wallet information if found, None otherwise
    """
    try:
        _ensure_storage_exists()
        
        # Read data from file
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
        
        # Return wallet info if exists
        wallet_info = data.get(debate_id)
        if wallet_info:
            logger.info(f"Retrieved wallet information for debate {debate_id}")
            return wallet_info
        else:
            logger.warning(f"No wallet information found for debate {debate_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error retrieving wallet information: {str(e)}")
        raise 