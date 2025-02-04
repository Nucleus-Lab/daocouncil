import requests

def chat_with_agent(debate_id: str, message: str):
    """Send a chat request to the judge agent API."""
    url = "http://localhost:8000/chat"
    
    payload = {
        "debate_id": debate_id,
        "message": message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise exception for error status codes
        
        result = response.json()
        print(f"Debate ID: {result['debate_id']}")
        print(f"Response: {result['response']}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling chat API: {str(e)}")
        if hasattr(e.response, 'json'):
            print(f"Error details: {e.response.json()}")
        raise

# Example usage:
if __name__ == "__main__":
    # Create a new wallet
    chat_with_agent(
        debate_id="test_debate_001",
        message="Create a new Privy wallet for this debate"
    )
    
    # Request faucet funds
    chat_with_agent(
        debate_id="test_debate_001",
        message="Request funds from the faucet to the CDP wallet"
    )
    
    # Transfer to vault
    chat_with_agent(
        debate_id="test_debate_001",
        message="Transfer 0.00001 ETH from CDP wallet to the Privy vault"
    )