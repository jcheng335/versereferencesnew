#!/usr/bin/env python3
"""
Weekly LSM Webcast Scraper for Render Cron Job
Automatically downloads latest outlines and sends to subscribers
"""

import os
import sys
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.lsm_scraper import LSMWebcastScraper
from utils.accurate_inline_processor import AccurateInlineProcessor
from utils.email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main weekly scraper function"""
    try:
        logger.info("Starting weekly LSM Webcast scraper...")
        
        # Initialize components
        scraper = LSMWebcastScraper()
        processor = AccurateInlineProcessor(os.environ.get('DATABASE_URL'))
        email_sender = EmailSender()
        
        # Get latest conference outline
        logger.info("Fetching latest conference outline...")
        latest_outline = scraper.get_latest_outline()
        
        if not latest_outline:
            logger.warning("No new outline found")
            return
        
        logger.info(f"Found outline: {latest_outline['title']}")
        
        # Process the outline with verse population
        logger.info("Processing outline with verse population...")
        session_data = processor.process_file(
            latest_outline['file_path'], 
            latest_outline['filename']
        )
        
        if not session_data['success']:
            logger.error(f"Failed to process outline: {session_data['error']}")
            return
        
        # Populate verses
        populated_result = processor.populate_verses(session_data['session_id'])
        
        if not populated_result['success']:
            logger.error(f"Failed to populate verses: {populated_result['error']}")
            return
        
        logger.info(f"Successfully populated {populated_result['verse_count']} verses")
        
        # Get subscriber list (you would implement this based on your user management)
        subscribers = get_subscriber_list()
        
        # Send emails to subscribers
        logger.info(f"Sending emails to {len(subscribers)} subscribers...")
        
        for subscriber in subscribers:
            try:
                # Export clean text for Word
                clean_text = processor.export_clean_text(session_data['session_id'])
                
                # Send email with attachment
                email_sender.send_weekly_outline(
                    subscriber['email'],
                    latest_outline['title'],
                    clean_text,
                    latest_outline['conference_info']
                )
                
                logger.info(f"Sent outline to {subscriber['email']}")
                
            except Exception as e:
                logger.error(f"Failed to send email to {subscriber['email']}: {e}")
        
        logger.info("Weekly scraper completed successfully!")
        
    except Exception as e:
        logger.error(f"Weekly scraper failed: {e}")
        raise

def get_subscriber_list():
    """Get list of premium subscribers"""
    # This would connect to your database and get premium subscribers
    # For now, return empty list - you'll implement this based on your user system
    return []

if __name__ == "__main__":
    main()

