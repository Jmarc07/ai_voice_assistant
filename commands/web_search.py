# web_search.py - Handles web search functionality

import webbrowser
import re
from logs.logger import log_action, log_error
from config.settings import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID
from config.constants import SEARCH_KEYWORDS

def web_search(command):
    """
    Perform a web search based on the command.
    
    Args:
        command (str): The search command
        
    Returns:
        str: Response message
    """
    try:
        # Extract search query by removing search keywords
        search_query = command.lower()
        for keyword in SEARCH_KEYWORDS:
            search_query = re.sub(f"{keyword}\\s+", "", search_query, flags=re.IGNORECASE)
        
        # Clean up the query
        search_query = search_query.strip()
        
        if not search_query:
            return "What would you like me to search for?"
        
        log_action(f"Searching for: {search_query}")
        
        # Check if we have API keys for Google Custom Search
        if GOOGLE_SEARCH_API_KEY != "your_google_api_key_here" and GOOGLE_SEARCH_ENGINE_ID != "your_search_engine_id_here":
            # Use Google Custom Search API (would require additional implementation)
            return perform_api_search(search_query)
        else:
            # Use simple browser search as fallback
            return perform_browser_search(search_query)
            
    except Exception as e:
        log_error("Error during web search", e)
        return "I encountered an error while trying to search. Please try again."

def perform_browser_search(query):
    """
    Perform a search by opening the default web browser.
    
    Args:
        query (str): The search query
        
    Returns:
        str: Response message
    """
    try:
        # Encode query for URL
        encoded_query = query.replace(' ', '+')
        
        # Create Google search URL
        url = f"https://www.google.com/search?q={encoded_query}"
        
        # Open in default browser
        webbrowser.open(url)
        
        return f"I've opened a search for '{query}' in your browser."
        
    except Exception as e:
        log_error("Error opening browser for search", e)
        return "I couldn't open the browser for search. Please check your internet connection."

def perform_api_search(query):
    """
    Perform a search using Google Custom Search API.
    
    Args:
        query (str): The search query
        
    Returns:
        str: Response with search results
    """
    try:
        # Note: This is a placeholder. To fully implement, you would need to:
        # 1. Import requests library
        # 2. Make an API call to Google Custom Search
        # 3. Process and return the results
        
        # This would require additional implementation with the requests library
        log_action("API search capability not fully implemented")
        
        # Fallback to browser search
        return perform_browser_search(query)
        
    except Exception as e:
        log_error("Error during API search", e)
        return "I encountered an error with the search API. Falling back to browser search."