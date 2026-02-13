"""Error Handler Utility Module

Provides consistent error response formatting across the API.
"""

from flask import jsonify
from typing import Tuple, Dict, Any
import logging


logger = logging.getLogger(__name__)


def handle_error(
    message: str,
    status_code: int = 500,
    details: str = None
) -> Tuple[Dict[str, Any], int]:
    """
    Generate formatted error response.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code (default: 500)
        details (str, optional): Additional error details
    
    Returns:
        tuple: (Response JSON, HTTP status code)
    """
    error_response = {
        'success': False,
        'error': message,
        'status_code': status_code
    }
    
    if details:
        error_response['details'] = details
    
    if status_code >= 500:
        logger.error(f'Server error ({status_code}): {message} {details or ""}')
    elif status_code >= 400:
        logger.warning(f'Client error ({status_code}): {message}')
    
    return jsonify(error_response), status_code


def handle_validation_error(
    field: str,
    message: str
) -> Tuple[Dict[str, Any], int]:
    """
    Generate validation error response.
    
    Args:
        field (str): Field that failed validation
        message (str): Validation error message
    
    Returns:
        tuple: (Response JSON, HTTP 400)
    """
    return jsonify({
        'success': False,
        'error': f'Validation error',
        'field': field,
        'message': message,
        'status_code': 400
    }), 400


def handle_unauthorized() -> Tuple[Dict[str, Any], int]:
    """
    Generate unauthorized error response.
    
    Returns:
        tuple: (Response JSON, HTTP 401)
    """
    return handle_error('Authentication required', 401)


def handle_forbidden() -> Tuple[Dict[str, Any], int]:
    """
    Generate forbidden error response.
    
    Returns:
        tuple: (Response JSON, HTTP 403)
    """
    return handle_error('Access forbidden', 403)


def handle_not_found(resource: str = 'Resource') -> Tuple[Dict[str, Any], int]:
    """
    Generate not found error response.
    
    Args:
        resource (str): Resource that was not found
    
    Returns:
        tuple: (Response JSON, HTTP 404)
    """
    return handle_error(f'{resource} not found', 404)
