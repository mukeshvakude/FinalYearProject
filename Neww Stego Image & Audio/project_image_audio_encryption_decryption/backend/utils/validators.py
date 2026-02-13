"""Validators Utility Module

Provides input validation functions for request data.
"""

import re
from typing import Dict, Optional, Any


def validate_credentials(data: Any) -> Optional[Dict[str, str]]:
    """
    Validate login credentials format.
    
    Args:
        data: Request data dictionary
    
    Returns:
        Dict with error message if validation fails, None if valid
    """
    if not isinstance(data, dict):
        return {'error': 'Invalid request format'}
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    epass = data.get('epass', '').strip()
    
    if not username:
        return {'error': 'Username is required'}
    
    if not password:
        return {'error': 'Password is required'}
    
    if not epass:
        return {'error': 'Encryption password is required'}
    
    if len(username) < 3:
        return {'error': 'Username must be at least 3 characters long'}
    
    if len(password) < 3:
        return {'error': 'Password must be at least 3 characters long'}
    
    if len(epass) < 3:
        return {'error': 'Encryption password must be at least 3 characters long'}
    
    return None


def validate_message(message: str) -> Optional[Dict[str, str]]:
    """
    Validate secret message format.
    
    Args:
        message (str): Message to validate
    
    Returns:
        Dict with error message if validation fails, None if valid
    """
    if not message:
        return {'error': 'Message cannot be empty'}
    
    if len(message) > 10000:
        return {'error': 'Message is too long (max 10000 characters)'}
    
    # Check for null bytes
    if '\x00' in message:
        return {'error': 'Message contains invalid characters'}
    
    return None


def validate_hex(hex_string: str) -> Optional[str]:
    """
    Validate hexadecimal string format.
    
    Args:
        hex_string (str): String to validate as hex
    
    Returns:
        Error message if validation fails, None if valid
    """
    if not hex_string:
        return 'Hex string cannot be empty'
    
    if not all(c in '0123456789abcdefABCDEF' for c in hex_string):
        return 'Cipher text must contain only hexadecimal characters'
    
    if len(hex_string) % 2 != 0:
        return 'Cipher text must have even length'
    
    return None


def validate_file_size(file_size: int, max_size: int = 50 * 1024 * 1024) -> Optional[str]:
    """
    Validate file size.
    
    Args:
        file_size (int): File size in bytes
        max_size (int): Maximum allowed size in bytes
    
    Returns:
        Error message if validation fails, None if valid
    """
    if file_size <= 0:
        return 'File size must be greater than zero'
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return f'File is too large (max {max_mb:.0f}MB)'
    
    return None


def validate_filename(filename: str) -> Optional[str]:
    """
    Validate filename for security.
    
    Args:
        filename (str): Filename to validate
    
    Returns:
        Error message if validation fails, None if valid
    """
    if not filename:
        return 'Filename cannot be empty'
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return 'Invalid filename'
    
    # Check length
    if len(filename) > 255:
        return 'Filename is too long'
    
    return None


def validate_email(email: str) -> Optional[str]:
    """
    Validate email address format.
    
    Args:
        email (str): Email to validate
    
    Returns:
        Error message if validation fails, None if valid
    """
    if not email:
        return 'Email cannot be empty'
    
    # Simple email regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return 'Invalid email format'
    
    return None


def validate_password_strength(password: str) -> Optional[str]:
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
    
    Returns:
        Error message if password is weak, None if strong
    """
    if len(password) < 8:
        return 'Password must be at least 8 characters long'
    
    if not any(c.isupper() for c in password):
        return 'Password must contain at least one uppercase letter'
    
    if not any(c.islower() for c in password):
        return 'Password must contain at least one lowercase letter'
    
    if not any(c.isdigit() for c in password):
        return 'Password must contain at least one digit'
    
    if not any(c in '!@#$%^&*()-_=+' for c in password):
        return 'Password must contain at least one special character'
    
    return None
