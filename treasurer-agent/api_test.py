import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def make_api_request(message="hi"):
    """
    Make a POST request to the autonome API
    
    Args:
        message (str): The message to send in the request
        
    Returns:
        dict: The JSON response from the API
    """
    url = 'https://autonome.alt.technology/judge-shegtn/chat'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic anVkZ2U6TEJWdHBTWFBjeQ=='
    }
    
    # Changed 'text' to 'message' in the payload
    payload = json.dumps({"message": message})
    
    try:
        logger.info(f"Making POST request to {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")
        
        response = requests.post(url, headers=headers, data=payload)
        
        # Log response details for debugging
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        logger.debug(f"Response Content: {response.text}")
        
        response.raise_for_status()
        
        logger.info("Request successful")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {str(e)}")
        logger.error(f"Response content: {getattr(e.response, 'text', 'No response content')}")
        raise

if __name__ == "__main__":
    # Enable debug logging to see more details
    logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        result = make_api_request()
        print("Response:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")