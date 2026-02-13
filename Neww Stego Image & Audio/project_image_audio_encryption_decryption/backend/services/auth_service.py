"""Authentication Service Module

Handles user authentication, validation, and session management.
"""

import pandas as pd
import os
import logging
from config import Config


class AuthService:
    """Service for handling user authentication and credential validation."""
    
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        """Initialize the authentication service."""
        self.users_file = Config.DATABASE_USERS
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users CSV file if it doesn't exist."""
        if not os.path.exists(self.users_file):
            try:
                df_users = pd.DataFrame({
                    'username': ['admin'],
                    'password': ['admin']
                })
                df_users.to_csv(self.users_file, index=False)
                self.logger.info(f'Users file created: {self.users_file}')
            except Exception as e:
                self.logger.error(f'Failed to create users file: {str(e)}')
                raise
    
    def validate_user(self, username: str, password: str) -> bool:
        """
        Validate user credentials against stored data.
        
        Args:
            username (str): User's username
            password (str): User's password
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            if not username or not password:
                return False
            
            df_users = pd.read_csv(self.users_file)
            
            # Validate credentials
            is_valid = ((df_users['username'] == username) &
                       (df_users['password'] == password)).any()
            
            if not is_valid:
                self.logger.warning(f'Invalid login attempt: {username}')
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f'Error validating user: {str(e)}')
            return False
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.
        
        Args:
            username (str): Username to check
        
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            df_users = pd.read_csv(self.users_file)
            return (df_users['username'] == username).any()
        except Exception as e:
            self.logger.error(f'Error checking user existence: {str(e)}')
            return False
    
    def get_all_users(self) -> list:
        """
        Get list of all registered users.
        
        Returns:
            list: List of usernames
        """
        try:
            df_users = pd.read_csv(self.users_file)
            return df_users['username'].tolist()
        except Exception as e:
            self.logger.error(f'Error retrieving users: {str(e)}')
            return []
    
    def register_user(self, username: str, password: str) -> dict:
        """
        Register a new user in the system.
        
        IMPORTANT: Face enrollment is handled separately after user creation.
        This method only creates the user account.
        
        Args:
            username (str): New username
            password (str): New password
        
        Returns:
            dict: Success status with message
                {
                    'success': bool,
                    'message': str,
                    'username': str (if success)
                }
        """
        try:
            # Validate input
            if not username or not password:
                return {
                    'success': False,
                    'message': 'Username and password are required'
                }
            
            # Check if username already exists
            if self.user_exists(username):
                self.logger.warning(f'Registration attempt with existing username: {username}')
                return {
                    'success': False,
                    'message': 'Username already exists. Please choose a different username.'
                }
            
            # Read existing users
            df_users = pd.read_csv(self.users_file)
            
            # Create new user record
            new_user = pd.DataFrame({
                'username': [username],
                'password': [password]
            })
            
            # Append new user
            df_users = pd.concat([df_users, new_user], ignore_index=True)
            
            # Write back to file
            df_users.to_csv(self.users_file, index=False)
            
            self.logger.info(f'New user registered: {username}')
            
            return {
                'success': True,
                'message': 'User registered successfully. Please enroll your face.',
                'username': username
            }
            
        except Exception as e:
            self.logger.error(f'User registration error: {str(e)}')
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
