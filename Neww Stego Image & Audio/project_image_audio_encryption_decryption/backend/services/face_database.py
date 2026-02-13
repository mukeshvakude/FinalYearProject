"""
Database Helper Functions for Face Authentication

Handles MySQL operations for storing and retrieving face encodings.
Works with existing user authentication database.

Functions:
    - add_face_encoding_column(): Add face_encoding column to users table
    - store_face_encoding(): Save face encoding to database
    - get_face_encoding(): Retrieve face encoding from database
    - user_has_face_encoding(): Check if user has registered face
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def add_face_encoding_column(db_connection):
    """
    Add face_encoding column to users table if it doesn't exist.
    
    WARNING: This should only be called ONCE during setup.
    
    Args:
        db_connection: Database connection object
    
    Returns:
        bool: True if successful or column already exists
    """
    try:
        cursor = db_connection.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='users' AND COLUMN_NAME='face_encoding'
        """)
        
        if cursor.fetchone():
            logger.info('face_encoding column already exists')
            return True
        
        # Add column if it doesn't exist
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN face_encoding LONGTEXT NULL
        """)
        
        db_connection.commit()
        logger.info('face_encoding column added to users table')
        return True
        
    except Exception as e:
        logger.error(f'Error adding face_encoding column: {str(e)}')
        db_connection.rollback()
        return False
    finally:
        cursor.close()


def store_face_encoding(db_connection, user_id: int, encoding_json: str) -> bool:
    """
    Store face encoding for user in database.
    
    Args:
        db_connection: Database connection object
        user_id (int): User ID
        encoding_json (str): JSON string of face encoding
    
    Returns:
        bool: True if successful
    """
    try:
        cursor = db_connection.cursor()
        
        # Update user's face_encoding column
        cursor.execute("""
            UPDATE users 
            SET face_encoding = %s 
            WHERE id = %s
        """, (encoding_json, user_id))
        
        db_connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f'Face encoding stored for user_id={user_id}')
            return True
        else:
            logger.warning(f'User not found: user_id={user_id}')
            return False
        
    except Exception as e:
        logger.error(f'Error storing face encoding: {str(e)}')
        db_connection.rollback()
        return False
    finally:
        cursor.close()


def get_face_encoding(db_connection, user_id: int) -> Optional[str]:
    """
    Retrieve face encoding from database for user.
    
    Args:
        db_connection: Database connection object
        user_id (int): User ID
    
    Returns:
        str: JSON string of face encoding, or None if not found
    """
    try:
        cursor = db_connection.cursor()
        
        cursor.execute("""
            SELECT face_encoding 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if result and result[0]:
            logger.info(f'Face encoding retrieved for user_id={user_id}')
            return result[0]
        else:
            logger.warning(f'No face encoding found for user_id={user_id}')
            return None
        
    except Exception as e:
        logger.error(f'Error retrieving face encoding: {str(e)}')
        return None
    finally:
        cursor.close()


def user_has_face_encoding(db_connection, user_id: int) -> bool:
    """
    Check if user has registered face encoding.
    
    Args:
        db_connection: Database connection object
        user_id (int): User ID
    
    Returns:
        bool: True if user has face encoding registered
    """
    try:
        encoding = get_face_encoding(db_connection, user_id)
        has_face = encoding is not None and encoding.strip() != ''
        
        logger.debug(f'User {user_id} has_face_encoding: {has_face}')
        return has_face
        
    except Exception as e:
        logger.error(f'Error checking face encoding: {str(e)}')
        return False


def delete_face_encoding(db_connection, user_id: int) -> bool:
    """
    Delete (clear) face encoding for user.
    
    Useful for re-registration or account removal.
    
    Args:
        db_connection: Database connection object
        user_id (int): User ID
    
    Returns:
        bool: True if successful
    """
    try:
        cursor = db_connection.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET face_encoding = NULL 
            WHERE id = %s
        """, (user_id,))
        
        db_connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f'Face encoding deleted for user_id={user_id}')
            return True
        else:
            logger.warning(f'User not found for deletion: user_id={user_id}')
            return False
        
    except Exception as e:
        logger.error(f'Error deleting face encoding: {str(e)}')
        db_connection.rollback()
        return False
    finally:
        cursor.close()
