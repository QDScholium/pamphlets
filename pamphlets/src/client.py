"""
This module creates a singleton Mistral client instance.
This ensures that only one client is created and reused throughout the application.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from mistralai import Mistral

# Global client instance that will be reused
_client_instance = None

def get_client():
    """
    Returns the singleton Mistral client instance.
    Creates it if it doesn't exist yet.
    """
    global _client_instance
    if _client_instance is None:
        api_key = os.environ["MISTRAL_API_KEY"]
        _client_instance = Mistral(api_key=api_key)
    return _client_instance

# Create the singleton instance
client = get_client()
