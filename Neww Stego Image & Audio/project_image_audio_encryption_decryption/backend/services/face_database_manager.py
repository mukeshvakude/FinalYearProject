"""
Face Database Manager

Handles storage and retrieval of face encodings from CSV database.
Manages user face profiles and authentication records.
"""

import pandas as pd
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from functools import lru_cache
import time


logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL for optimization
_cache = {}
_cache_times = {}


class FaceDatabaseManager:
    """
    Manages face encoding storage in CSV database.
    
    Schema:
    - username (str): Unique user identifier
    - face_encoding (str): JSON-serialized face encoding (list of 128 floats)
    - enrollment_date (str): ISO timestamp of face enrollment
    - face_image_path (str): Path to stored face image
    - last_authenticated (str): ISO timestamp of last successful authentication
    - authentication_count (int): Number of successful authentications
    - encoding_version (str): Version of face_recognition model used
    """
    
    def __init__(self, db_path: str = 'faces.csv'):
        """
        Initialize face database manager.
        
        Args:
            db_path (str): Path to faces.csv database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
        logger.info(f'Face Database Manager initialized with: {db_path}')
    
    def _ensure_database_exists(self):
        """Create database file with headers if it doesn't exist."""
        try:
            if not os.path.exists(self.db_path):
                df = pd.DataFrame(columns=[
                    'username',
                    'face_encoding',
                    'enrollment_date',
                    'face_image_path',
                    'last_authenticated',
                    'authentication_count',
                    'encoding_version'
                ])
                df.to_csv(self.db_path, index=False)
                logger.info(f'Face database created: {self.db_path}')
        except Exception as e:
            logger.error(f'Error creating face database: {str(e)}')
            raise
    
    def _read_database(self) -> pd.DataFrame:
        """
        Read face database from CSV with caching.
        
        Returns:
            pd.DataFrame: Face database
        """
        try:
            # Check cache (5-second TTL)
            cache_key = f'df_{self.db_path}'
            if cache_key in _cache:
                if time.time() - _cache_times[cache_key] < 5:
                    logger.debug(f'Returning cached database (age: {time.time() - _cache_times[cache_key]:.2f}s)')
                    return _cache[cache_key]
            
            # Cache miss or expired - read from disk
            if os.path.exists(self.db_path):
                df = pd.read_csv(self.db_path)
            else:
                df = pd.DataFrame(columns=[
                    'username',
                    'face_encoding',
                    'enrollment_date',
                    'face_image_path',
                    'last_authenticated',
                    'authentication_count',
                    'encoding_version'
                ])
            
            # Update cache
            _cache[cache_key] = df
            _cache_times[cache_key] = time.time()
            logger.debug('Database cached for 5 seconds')
            return df
        except Exception as e:
            logger.error(f'Error reading face database: {str(e)}')
            raise
    
    def _write_database(self, df: pd.DataFrame):
        """
        Write face database to CSV and clear cache.
        
        Args:
            df (pd.DataFrame): Face database dataframe
        """
        try:
            df.to_csv(self.db_path, index=False)
            # Clear cache after write
            cache_key = f'df_{self.db_path}'
            if cache_key in _cache:
                del _cache[cache_key]
                del _cache_times[cache_key]
            logger.info('Face database updated (cache cleared)')
        except Exception as e:
            logger.error(f'Error writing face database: {str(e)}')
            raise
    
    def enroll_face(self, username: str, face_encoding: List[float],
                   face_image_path: str, encoding_version: str = '1.0') -> bool:
        """
        Enroll a user's face in the database.
        
        Args:
            username (str): Username
            face_encoding (List[float]): Face encoding (128-element list)
            face_image_path (str): Path to face image file
            encoding_version (str): Version of face_recognition model
        
        Returns:
            bool: True if enrollment successful, False if user already has face
        """
        try:
            df = self._read_database()
            
            # Check if user already has face enrollment
            if username in df['username'].values:
                logger.warning(f'User {username} already has face enrollment')
                return False
            
            # Add new face record
            new_record = {
                'username': username,
                'face_encoding': json.dumps(face_encoding),
                'enrollment_date': datetime.now().isoformat(),
                'face_image_path': face_image_path,
                'last_authenticated': None,
                'authentication_count': 0,
                'encoding_version': encoding_version
            }
            
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            self._write_database(df)
            
            logger.info(f'Face enrolled for user: {username}')
            return True
            
        except Exception as e:
            logger.error(f'Face enrollment error: {str(e)}')
            raise
    
    def get_face_encoding(self, username: str) -> Optional[List[float]]:
        """
        Get face encoding for a user.
        
        Args:
            username (str): Username
        
        Returns:
            List[float]: Face encoding or None if not found
        """
        try:
            df = self._read_database()
            user_record = df[df['username'] == username]
            
            if user_record.empty:
                logger.warning(f'No face encoding found for user: {username}')
                return None
            
            encoding_json = user_record.iloc[0]['face_encoding']
            encoding = json.loads(encoding_json)
            
            return encoding
            
        except Exception as e:
            logger.error(f'Error retrieving face encoding: {str(e)}')
            raise
    
    def update_authentication(self, username: str) -> bool:
        """
        Update last authentication timestamp and increment count.
        
        Args:
            username (str): Username
        
        Returns:
            bool: True if update successful
        """
        try:
            df = self._read_database()
            user_idx = df[df['username'] == username].index
            
            if user_idx.empty:
                logger.warning(f'User not found for authentication update: {username}')
                return False
            
            idx = user_idx[0]
            df.at[idx, 'last_authenticated'] = datetime.now().isoformat()
            df.at[idx, 'authentication_count'] = int(df.at[idx, 'authentication_count']) + 1
            
            self._write_database(df)
            logger.info(f'Authentication updated for user: {username}')
            return True
            
        except Exception as e:
            logger.error(f'Error updating authentication: {str(e)}')
            raise
    
    def user_has_face(self, username: str) -> bool:
        """
        Check if user has enrolled face.
        
        Args:
            username (str): Username
        
        Returns:
            bool: True if user has face enrollment
        """
        try:
            df = self._read_database()
            return username in df['username'].values
        except Exception as e:
            logger.error(f'Error checking face enrollment: {str(e)}')
            return False
    
    def get_all_face_encodings(self) -> Tuple[List[str], List[List[float]]]:
        """
        Get all enrolled face encodings with their usernames.
        
        Returns:
            Tuple[List[str], List[List[float]]]: (usernames, face_encodings)
        """
        try:
            df = self._read_database()
            
            if df.empty:
                return ([], [])
            
            usernames = df['username'].tolist()
            encodings = [json.loads(enc) for enc in df['face_encoding'].tolist()]
            
            return (usernames, encodings)
            
        except Exception as e:
            logger.error(f'Error retrieving all face encodings: {str(e)}')
            raise
    
    def delete_face(self, username: str) -> bool:
        """
        Delete user's face enrollment (e.g., if re-enrollment needed).
        
        Args:
            username (str): Username
        
        Returns:
            bool: True if deleted successfully
        """
        try:
            df = self._read_database()
            
            if username not in df['username'].values:
                logger.warning(f'Face not found for deletion: {username}')
                return False
            
            df = df[df['username'] != username]
            self._write_database(df)
            
            logger.info(f'Face deleted for user: {username}')
            return True
            
        except Exception as e:
            logger.error(f'Error deleting face: {str(e)}')
            raise
    
    def get_user_stats(self, username: str) -> Optional[Dict]:
        """
        Get authentication statistics for a user.
        
        Args:
            username (str): Username
        
        Returns:
            Dict: User statistics (enrollment_date, last_authenticated, count) or None
        """
        try:
            df = self._read_database()
            user_record = df[df['username'] == username]
            
            if user_record.empty:
                return None
            
            record = user_record.iloc[0]
            return {
                'username': username,
                'enrolled': record['enrollment_date'],
                'last_authenticated': record['last_authenticated'],
                'authentication_count': int(record['authentication_count']),
                'encoding_version': record['encoding_version']
            }
            
        except Exception as e:
            logger.error(f'Error retrieving user stats: {str(e)}')
            raise
    
    def get_database_stats(self) -> Dict:
        """
        Get overall database statistics.
        
        Returns:
            Dict: Database statistics
        """
        try:
            df = self._read_database()
            
            return {
                'total_users': len(df),
                'total_authentications': int(df['authentication_count'].sum()),
                'last_enrollment': df['enrollment_date'].max() if not df.empty else None,
                'db_size_kb': os.path.getsize(self.db_path) / 1024 if os.path.exists(self.db_path) else 0
            }
            
        except Exception as e:
            logger.error(f'Error retrieving database stats: {str(e)}')
            raise
    
    def export_for_training(self) -> List[tuple]:
        """
        Export face data for training or backup.
        
        Returns:
            List[tuple]: List of (username, encoding_array) tuples
        """
        try:
            usernames, encodings = self.get_all_face_encodings()
            encoding_arrays = [np.array(enc) for enc in encodings]
            return list(zip(usernames, encoding_arrays))
            
        except Exception as e:
            logger.error(f'Error exporting training data: {str(e)}')
            raise
