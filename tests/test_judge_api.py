import requests
import logging
import json
from typing import Optional
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def chat_with_judge(debate_id: str, message: str, base_url: str = "http://localhost:8001", 
                   user_agent: str = None, source_app: str = None) -> Optional[str]:
    """
    Send a chat message to the judge agent API.
    
    Args:
        debate_id (str): Unique identifier for the debate
        message (str): Message to send to the judge
        base_url (str): Base URL of the judge agent API
        user_agent (str): Custom User-Agent header
        source_app (str): Source application identifier
        
    Returns:
        Optional[str]: The judge's response or None if request failed
    """
    endpoint = f"{base_url}/chat"
    
    payload = {
        "debate_id": debate_id,
        "message": message
    }
    
    # Set up headers to simulate different sources
    headers = {
        'Content-Type': 'application/json'
    }
    
    if user_agent:
        headers['User-Agent'] = user_agent
    if source_app:
        headers['X-Source-App'] = source_app
    
    try:
        logger.info(f"Sending request to {endpoint} for debate {debate_id}")
        logger.info(f"Request headers: {headers}")
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding response: {str(e)}")
        return None

def test_multiple_requests():
    """Test the API with multiple requests from different sources."""
    # List of test scenarios
    scenarios = [
        {
            "debate_id": "13928092",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "source_app": "web_frontend",
            "description": "Original debate from web frontend"
        },
        {
            "debate_id": "13928093",
            "user_agent": "DAOCouncil-Mobile/1.0",
            "source_app": "mobile_app",
            "description": "Different debate from mobile app"
        },
        {
            "debate_id": "13928092",  # Same debate ID as first request
            "user_agent": "PostmanRuntime/7.32.3",
            "source_app": "external_api",
            "description": "Same debate from different source"
        },
        {
            "debate_id": "test_debate_999",
            "user_agent": "Python-Requests/2.31.0",
            "source_app": "test_script",
            "description": "Test debate from script"
        }
    ]
    
    message = "What is your CDP wallet address? Please show me your current wallet address."
    
    for scenario in scenarios:
        logger.info(f"\nTesting scenario: {scenario['description']}")
        print("\n" + "="*70)
        print(f"Scenario: {scenario['description']}")
        print(f"Debate ID: {scenario['debate_id']}")
        print("="*70)
        
        response = chat_with_judge(
            debate_id=scenario['debate_id'],
            message=message,
            user_agent=scenario['user_agent'],
            source_app=scenario['source_app']
        )
        
        if response:
            print("\nResponse:")
            print("-"*50)
            print(response)
            print("-"*50 + "\n")
        else:
            print("\nFailed to get response")
        
        # Add a small delay between requests
        time.sleep(1)

def main():
    logger.info("Starting multiple test scenarios for judge agent API...")
    test_multiple_requests()

if __name__ == "__main__":
    main() 