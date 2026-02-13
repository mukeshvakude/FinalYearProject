"""Encryption Service Module

Handles AES-256-CTR encryption and decryption operations with PBKDF2 key
derivation.
"""

import pyaes
import pbkdf2
import binascii
import logging
from typing import Tuple, Dict, Any


class EncryptionService:
    """Service for cryptographic operations using AES-256-CTR encryption."""
    
    logger = logging.getLogger(__name__)
    
    # Fixed IV and Salt (for demo use only - should be randomized in production)
    IV = 99114684525942506313644461257805955214848508590114620791139267598143401799819
    PASSWORD_SALT = b'$\xfb\x89\x1d\xb2\x08\x8f\x1b\xfa\xe49A`\xf9Z\xdc'
    
    KEY_SIZE = 32  # 256 bits for AES-256
    
    def __init__(self):
        """Initialize the encryption service."""
        self.algorithm = 'AES-256-CTR'
        self.logger.info('Encryption service initialized')
    
    def _derive_key(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password (str): User's password
        
        Returns:
            bytes: 32-byte encryption key
        
        Raises:
            Exception: If key derivation fails
        """
        try:
            if not password:
                raise ValueError('Password cannot be empty')
            
            key = pbkdf2.PBKDF2(password, self.PASSWORD_SALT).read(self.KEY_SIZE)
            return key
            
        except Exception as e:
            self.logger.error(f'Key derivation failed: {str(e)}')
            raise
    
    def encrypt_message(self, plaintext: str, password: str) -> str:
        """
        Encrypt a message using AES-256-CTR mode.
        
        Args:
            plaintext (str): Message to encrypt
            password (str): Encryption password
        
        Returns:
            str: Encrypted message in hexadecimal format
        
        Raises:
            Exception: If encryption fails
        """
        try:
            if not plaintext:
                raise ValueError('Plaintext cannot be empty')
            
            # Derive key from password
            key = self._derive_key(password)
            
            # Encode message to bytes
            message_bytes = plaintext.encode('utf-8')
            
            # Encrypt using AES-256-CTR
            aes_cipher = pyaes.AESModeOfOperationCTR(
                key,
                pyaes.Counter(self.IV)
            )
            ciphertext = aes_cipher.encrypt(message_bytes)
            
            # Convert to hexadecimal
            cipher_hex = binascii.hexlify(ciphertext).decode()
            
            self.logger.info(f'Message encrypted successfully ({len(message_bytes)} bytes)')
            return cipher_hex
            
        except Exception as e:
            self.logger.error(f'Encryption error: {str(e)}')
            raise
    
    def decrypt_message(self, cipher_hex: str, password: str) -> Dict[str, Any]:
        """
        Decrypt a message encrypted with AES-256-CTR mode.
        
        Args:
            cipher_hex (str): Encrypted message in hexadecimal format
            password (str): Decryption password
        
        Returns:
            dict: Dictionary with 'success' (bool) and either 'plaintext' or 'error'
        """
        try:
            if not cipher_hex or not password:
                return {
                    'success': False,
                    'error': 'Cipher text and password are required'
                }
            
            # Validate hexadecimal format
            if not all(c in '0123456789abcdefABCDEF' for c in cipher_hex):
                return {
                    'success': False,
                    'error': 'Cipher text must be in valid hexadecimal format'
                }
            
            if len(cipher_hex) % 2 != 0:
                return {
                    'success': False,
                    'error': 'Cipher text has invalid length'
                }
            
            # Convert hex to bytes
            try:
                ciphertext = binascii.unhexlify(cipher_hex)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Invalid cipher text format: {str(e)}'
                }
            
            # Derive key from password
            try:
                key = self._derive_key(password)
            except Exception as e:
                return {
                    'success': False,
                    'error': 'Key derivation failed'
                }
            
            # Decrypt using AES-256-CTR
            try:
                aes_cipher = pyaes.AESModeOfOperationCTR(
                    key,
                    pyaes.Counter(self.IV)
                )
                plaintext_bytes = aes_cipher.decrypt(ciphertext)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Decryption failed: {str(e)}'
                }
            
            # Decode UTF-8
            try:
                plaintext = plaintext_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return {
                    'success': False,
                    'error': (
                        'Decrypted data is not valid text. '
                        'This usually means the password is incorrect or the cipher text is corrupted.'
                    )
                }
            
            self.logger.info(f'Message decrypted successfully ({len(plaintext_bytes)} bytes)')
            
            return {
                'success': True,
                'plaintext': plaintext
            }
            
        except Exception as e:
            self.logger.error(f'Decryption error: {str(e)}')
            return {
                'success': False,
                'error': 'Decryption operation failed'
            }
    
    def get_encryption_info(self) -> Dict[str, str]:
        """
        Get information about the encryption method.
        
        Returns:
            dict: Encryption details
        """
        return {
            'algorithm': self.algorithm,
            'mode': 'CTR',
            'key_size': f'{self.KEY_SIZE * 8} bits',
            'key_derivation': 'PBKDF2',
            'encoding': 'Hexadecimal'
        }
