"""File Manager Service Module

Handles file operations including uploads, validation, and processing.
"""

import os
import logging
from typing import Optional, Tuple
from config import Config


class FileManager:
    """Service for managing file operations."""
    
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        """Initialize the file manager service."""
        self.upload_folder = Config.UPLOAD_FOLDER
        self.audio_folder = Config.UPLOAD_AUDIO_FOLDER
        self.max_file_size = Config.MAX_CONTENT_LENGTH
        self.allowed_images = Config.ALLOWED_IMAGE_EXTENSIONS
        self.allowed_audio = Config.ALLOWED_AUDIO_EXTENSIONS
    
    def ensure_directory(self, directory: str) -> bool:
        """
        Create directory if it doesn't exist.
        
        Args:
            directory (str): Directory path
        
        Returns:
            bool: True if directory exists or was created
        """
        try:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f'Directory ensured: {directory}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to create directory {directory}: {str(e)}')
            return False
    
    def is_allowed_image(self, filename: str) -> bool:
        """
        Check if file is an allowed image format.
        
        Args:
            filename (str): Filename to check
        
        Returns:
            bool: True if file extension is allowed
        """
        if not filename or '.' not in filename:
            return False
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        return file_ext in self.allowed_images
    
    def is_allowed_audio(self, filename: str) -> bool:
        """
        Check if file is an allowed audio format.
        
        Args:
            filename (str): Filename to check
        
        Returns:
            bool: True if file extension is allowed
        """
        if not filename or '.' not in filename:
            return False
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        return file_ext in self.allowed_audio
    
    def get_file_size(self, filepath: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            filepath (str): Path to file
        
        Returns:
            int: File size in bytes, or None if file not found
        """
        try:
            if os.path.exists(filepath):
                return os.path.getsize(filepath)
            return None
        except Exception as e:
            self.logger.error(f'Error getting file size: {str(e)}')
            return None
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file.
        
        Args:
            filepath (str): Path to file
        
        Returns:
            bool: True if file was deleted
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f'File deleted: {filepath}')
                return True
            return False
        except Exception as e:
            self.logger.error(f'Failed to delete file {filepath}: {str(e)}')
            return False
    
    def file_exists(self, filepath: str) -> bool:
        """
        Check if file exists.
        
        Args:
            filepath (str): Path to file
        
        Returns:
            bool: True if file exists
        """
        return os.path.exists(filepath)
    
    def process_image(self, source_path: str, dest_path: str) -> bool:
        """
        Process and save image file.
        
        Args:
            source_path (str): Source image path
            dest_path (str): Destination path
        
        Returns:
            bool: True if processing successful
        """
        try:
            import cv2
            
            if not os.path.exists(source_path):
                self.logger.error(f'Source image not found: {source_path}')
                return False
            
            # Read image
            img = cv2.imread(source_path)
            
            if img is None:
                self.logger.error(f'Failed to read image: {source_path}')
                return False
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest_path)
            if dest_dir:
                self.ensure_directory(dest_dir)
            
            # Write image
            cv2.imwrite(dest_path, img)
            
            self.logger.info(f'Image processed: {dest_path}')
            return True
            
        except ImportError:
            self.logger.error('OpenCV (cv2) is not installed')
            return False
        except Exception as e:
            self.logger.error(f'Image processing failed: {str(e)}')
            return False
    
    def get_file_info(self, filepath: str) -> dict:
        """
        Get file information.
        
        Args:
            filepath (str): Path to file
        
        Returns:
            dict: File information (name, size, exists, etc.)
        """
        try:
            filename = os.path.basename(filepath)
            file_size = self.get_file_size(filepath)
            exists = self.file_exists(filepath)
            
            return {
                'filename': filename,
                'path': filepath,
                'size': file_size,
                'exists': exists,
                'absolute_path': os.path.abspath(filepath)
            }
        except Exception as e:
            self.logger.error(f'Error getting file info: {str(e)}')
            return {}
    
    def cleanup_old_files(self, directory: str, max_age_hours: int = 24) -> int:
        """
        Delete old files from directory (for maintenance).
        
        Args:
            directory (str): Directory path
            max_age_hours (int): Delete files older than this (in hours)
        
        Returns:
            int: Number of files deleted
        """
        try:
            import time
            
            if not os.path.exists(directory):
                return 0
            
            deleted_count = 0
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        deleted_count += 1
                        self.logger.info(f'Old file deleted: {filepath}')
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f'Error cleaning up files: {str(e)}')
            return 0
