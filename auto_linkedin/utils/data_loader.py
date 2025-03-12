"""
Data loader for the Auto LinkedIn application
"""

import os
import csv
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class DataLoader:
    """Data loader for LinkedIn posts"""
    
    def __init__(self):
        """Initialize data loader"""
        pass
    
    def load_file(self, file_path):
        """Load data from a file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == ".xlsx":
            return self.load_excel(file_path)
        elif file_ext == ".csv":
            return self.load_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def load_excel(self, file_path):
        """Load data from an Excel file"""
        try:
            logger.info(f"Loading Excel file: {file_path}")
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Convert to list of dictionaries
            return self.process_dataframe(df)
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise
    
    def load_csv(self, file_path):
        """Load data from a CSV file"""
        try:
            logger.info(f"Loading CSV file: {file_path}")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Convert to list of dictionaries
            return self.process_dataframe(df)
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            raise
    
    def process_dataframe(self, df):
        """Process DataFrame into list of post dictionaries"""
        # Validate and clean column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Check for required columns
        required_columns = ['text']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in data file")
        
        # Convert to list of dictionaries
        posts = []
        
        for _, row in df.iterrows():
            post = {
                "text": row.get("text", "") if pd.notna(row.get("text", "")) else ""
            }
            
            # Add image if present
            if "image" in df.columns and pd.notna(row.get("image", "")):
                post["image"] = row.get("image", "")
            
            # Validate post
            if not post["text"]:
                logger.warning(f"Skipping post with empty text: {post}")
                continue
            
            posts.append(post)
        
        logger.info(f"Loaded {len(posts)} posts from data file")
        return posts 