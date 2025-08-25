"""
LSM Webcast Integration Module
Handles automatic outline downloading and processing
"""

import requests
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional
import logging

class LSMWebcastIntegration:
    def __init__(self):
        self.base_url = "https://www.lsmwebcast.com"
        self.archives_url = f"{self.base_url}/archives/"
        
        # Known conference patterns
        self.known_conferences = {
            "B25ANCC": {
                "title": "Chapters 5 through 8 of Romans—the Kernel of the Bible",
                "messages": 6,
                "date": "02/14/25"
            }
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_available_conferences(self) -> List[Dict]:
        """Get list of available conferences"""
        conferences = []
        
        for code, info in self.known_conferences.items():
            conferences.append({
                "code": code,
                "title": info["title"],
                "date": info["date"],
                "message_count": info["messages"],
                "available": True
            })
        
        return conferences
    
    def download_conference_outline(self, conference_code: str, message_number: int, language: str = "en") -> Optional[str]:
        """
        Download specific conference outline
        
        Args:
            conference_code: Conference code (e.g., "B25ANCC")
            message_number: Message number (1-6)
            language: Language code (default: "en")
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Generate URL
            filename = f"{conference_code}{message_number:02d}{language}.pdf"
            url = f"{self.archives_url}{filename}"
            
            self.logger.info(f"Downloading outline: {url}")
            
            # Download file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            temp_dir = tempfile.gettempdir()
            local_path = os.path.join(temp_dir, filename)
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Downloaded outline to: {local_path}")
            return local_path
            
        except Exception as e:
            self.logger.error(f"Error downloading outline: {e}")
            return None
    
    def get_latest_conference_outline(self, language: str = "en") -> Optional[str]:
        """Get the latest conference outline (Message 1)"""
        # For now, return the known Romans conference
        return self.download_conference_outline("B25ANCC", 1, language)
    
    def schedule_weekly_download(self, user_email: str, conference_code: str = "auto") -> bool:
        """
        Schedule weekly automatic downloads
        
        Args:
            user_email: User's email for delivery
            conference_code: Specific conference or "auto" for latest
            
        Returns:
            True if scheduled successfully
        """
        # This would integrate with the scheduling system
        # For now, just log the request
        self.logger.info(f"Scheduled weekly download for {user_email}, conference: {conference_code}")
        return True
