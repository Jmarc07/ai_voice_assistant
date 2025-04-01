# commands/web_search.py
import os
import sys
import webbrowser
import requests
import re

# Import settings and modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID
from logs.logger import logger

class WebSearch:
    def __init__(self, assistant):
        self.assistant = assistant
        self.use_api = GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID
        logger.info("Web search handler initialized")
    
    def handle(self, command, is_admin=False):
        """
        Handle web search commands
        
        Args:
            command (str): The search command
            is_admin (bool): Whether the user has admin privileges
        
        Returns:
            bool: True if the command was handled successfully, False otherwise
        """
        try:
            # Extract the search query from the command
            search_terms = self._extract_search_query(command)
            
            if not search_terms:
                self.assistant.respond("What would you like me to search for?")
                return False
            
            logger.info(f"Searching for: {search_terms}")
            self.assistant.respond(f"Searching for {search_terms}...")
            
            # Perform the search
            if self.use_api:
                results = self._search_with_api(search_terms)
                if results:
                    self._report_results(results)
                    return True
            
            # Fallback to browser search if API fails or is not configured
            self._search_with_browser(search_terms)
            return True
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            self.assistant.respond("I had trouble performing that search.")
            return False
    
    def _extract_search_query(self, command):
        """Extract the search query from the command"""
        # Remove search keywords from the command
        search_patterns = [
            r'search (?:for |about |)(.+)',
            r'look up (.+)',
            r'find (?:info about |information about |info on |information on |)(.+)',
            r'google (.+)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, command.lower())
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, use everything after "search"
        if "search" in command.lower():
            return command.lower().split("search", 1)[1].strip()
        
        return command.strip()
    
    def _search_with_api(self, query):
        """Perform a search using the Google Custom Search API"""
        if not self.use_api:
            return None
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': GOOGLE_SEARCH_API_KEY,
                'cx': GOOGLE_SEARCH_ENGINE_ID,
                'num': 5  # Number of results to return
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                results = response.json()
                if 'items' in results:
                    return results['items']
                else:
                    logger.warning("No search results found")
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
            
            return None
        except Exception as e:
            logger.error(f"Error using search API: {e}")
            return None
    
    def _search_with_browser(self, query):
        """Open a web browser with the search query"""
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        self.assistant.respond(f"I've opened a web browser with search results for {query}.")
    
    def _report_results(self, results):
        """Report the search results to the user"""
        if not results:
            self.assistant.respond("I couldn't find any results for that search.")
            return
        
        response = f"I found {len(results)} results. Here's the top result: "
        
        # Get the title and snippet from the first result
        top_result = results[0]
        title = top_result.get('title', 'Untitled')
        snippet = top_result.get('snippet', 'No description available.')
        
        response += f"{title}. {snippet}"
        
        self.assistant.respond(response)
        
        # Ask if user wants more details
        self.assistant.respond("Would you like me to open the search results in a browser?")
        
        # Listen for response
        answer = self.assistant.speech_recognizer.listen(phrase_time_limit=3)
        
        if answer and ('yes' in answer.lower() or 'yeah' in answer.lower() or 'sure' in answer.lower()):
            self._search_with_browser(results[0].get('link', f"https://www.google.com/search?q={results[0].get('title')}"))