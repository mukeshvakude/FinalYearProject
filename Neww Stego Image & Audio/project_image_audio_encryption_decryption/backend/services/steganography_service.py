"""Steganography Service Module

Handles image and audio steganography operations using LSB (Least Significant Bit)
encoding/decoding.
"""

import pandas as pd
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from config import Config


class SteganographyService:
    """Service for image and audio steganography operations."""
    
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        """Initialize the steganography service."""
        self.audio_log_file = Config.DATABASE_AUDIO_LOG
        self._ensure_audio_log()
    
    def _ensure_audio_log(self):
        """Create audio log CSV file if it doesn't exist."""
        if not os.path.exists(self.audio_log_file):
            try:
                df_audio = pd.DataFrame({
                    'filename': [],
                    'cipher_text': [],
                    'timestamp': []
                })
                df_audio.to_csv(self.audio_log_file, index=False)
                self.logger.info(f'Audio log file created: {self.audio_log_file}')
            except Exception as e:
                self.logger.error(f'Failed to create audio log: {str(e)}')
    
    def encode_image(self, ciphertext: bytes) -> bool:
        """
        Encode cipher text into two image files using LSB steganography.
        
        Args:
            ciphertext (bytes): Encrypted binary data to hide
        
        Returns:
            bool: True if encoding successful
        
        Raises:
            Exception: If image encoding fails
        """
        try:
            from supportFile import encode
            
            self.logger.info(f'Encoding message into images ({len(ciphertext)} bytes)')
            encode(ciphertext)
            
            self.logger.info('Message successfully encoded in image files')
            return True
            
        except Exception as e:
            self.logger.error(f'Image encoding failed: {str(e)}')
            raise
    
    def encode_audio(self, audio_path: str, ciphertext: bytes) -> bool:
        """
        Encode cipher text into audio file using LSB steganography.
        
        Args:
            audio_path (str): Path to audio file
            ciphertext (bytes): Encrypted binary data to hide
        
        Returns:
            bool: True if encoding successful
        
        Raises:
            Exception: If audio encoding fails
        """
        try:
            from supportFile import encode_audio
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f'Audio file not found: {audio_path}')
            
            self.logger.info(
                f'Encoding message into audio ({os.path.basename(audio_path)}, '
                f'{len(ciphertext)} bytes)'
            )
            encode_audio(audio_path, ciphertext)
            
            self.logger.info('Message successfully encoded in audio file')
            return True
            
        except Exception as e:
            self.logger.error(f'Audio encoding failed: {str(e)}')
            raise
    
    def log_audio_operation(self, audio_path: str, cipher_hex: str) -> bool:
        """
        Log audio steganography operation to CSV file.
        
        Args:
            audio_path (str): Path to audio file
            cipher_hex (str): Encrypted message in hexadecimal format
        
        Returns:
            bool: True if logging successful
        """
        try:
            self._ensure_audio_log()
            
            filename = os.path.basename(audio_path)
            timestamp = datetime.now().isoformat()
            
            # Read existing log
            df_audio = pd.read_csv(self.audio_log_file)
            
            # Add new entry
            new_entry = pd.DataFrame({
                'filename': [filename],
                'cipher_text': [cipher_hex],
                'timestamp': [timestamp]
            })
            
            df_audio = pd.concat([df_audio, new_entry], ignore_index=True)
            df_audio.to_csv(self.audio_log_file, index=False)
            
            self.logger.info(f'Audio operation logged: {filename}')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to log audio operation: {str(e)}')
            return False
    
    def get_audio_log(self) -> List[Dict[str, Any]]:
        """
        Retrieve all logged audio steganography operations.
        
        Returns:
            list: List of audio operation records
        """
        try:
            self._ensure_audio_log()
            
            if os.path.exists(self.audio_log_file):
                df_audio = pd.read_csv(self.audio_log_file)
                return df_audio.to_dict('records')
            else:
                return []
                
        except Exception as e:
            self.logger.error(f'Error retrieving audio log: {str(e)}')
            return []
    
    def clear_audio_log(self) -> bool:
        """
        Clear all entries from audio log (for testing/maintenance).
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            if os.path.exists(self.audio_log_file):
                df_audio = pd.DataFrame({
                    'filename': [],
                    'cipher_text': [],
                    'timestamp': []
                })
                df_audio.to_csv(self.audio_log_file, index=False)
                self.logger.info('Audio log cleared')
                return True
            return False
            
        except Exception as e:
            self.logger.error(f'Failed to clear audio log: {str(e)}')
            return False
    
    def decode_image(self) -> bytes:
        """
        Decode cipher text from image files.
        
        Returns:
            bytes: Decoded binary data
        
        Raises:
            Exception: If image decoding fails
        """
        try:
            from supportFile import decode
            
            self.logger.info('Decoding message from image files')
            decoded_data = decode()
            
            self.logger.info(f'Image decoding successful ({len(decoded_data)} bytes)')
            return decoded_data
            
        except Exception as e:
            self.logger.error(f'Image decoding failed: {str(e)}')
            raise
    
    def get_steganography_info(self) -> Dict[str, Any]:
        """
        Get information about steganography methods.
        
        Returns:
            dict: Steganography details
        """
        return {
            'image_method': 'LSB (Least Significant Bit)',
            'audio_method': 'LSB (Least Significant Bit)',
            'image_format': 'PNG',
            'audio_format': 'WAV',
            'capacity_note': 'Depends on media size and bit depth'
        }
