"""
Face Recognition and Authentication Service

Provides face enrollment, verification, and authentication capabilities
using industry-standard face_recognition library with dlib backend.

Features:
- Face detection and encoding generation
- Face comparing with registered faces
- Face database management
- Session-based face authentication
"""

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠ Warning: face_recognition library not installed. Face auth will be disabled.")

import cv2
import numpy as np
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


logger = logging.getLogger(__name__)


class FaceAuthService:
    """
    Service for face authentication and recognition operations.
    
    Uses face_recognition library for accurate face detection and matching.
    Supports face enrollment, verification, and recognition.
    """
    
    def __init__(self, tolerance: float = 0.6, model: str = 'large'):
        """
        Initialize face recognition service.
        
        Args:
            tolerance (float): Distance tolerance for face comparison (0.0-1.0)
                             Lower values = stricter matching. Default: 0.6
            model (str): Model to use ('small' for speed or 'large' for accuracy)
        """
        self.tolerance = tolerance
        self.model = model
        self.face_encodings_cache = {}
        logger.info(f'Face Auth Service initialized with tolerance={tolerance}, model={model}')
    
    def capture_face_from_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load and process face image, return first detected face encoding.
        
        Args:
            image_path (str): Path to face image file
        
        Returns:
            np.ndarray: Face encoding (128-dimensional vector) or None if no face found
        
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image is corrupted or unreadable
        """
        try:
            # Validate file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f'Image file not found: {image_path}')
            
            # Load image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f'Failed to load image: {image_path}')
            
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces and generate encodings
            face_encodings = face_recognition.face_encodings(
                rgb_image,
                model=self.model
            )
            
            if len(face_encodings) == 0:
                logger.warning(f'No face detected in image: {image_path}')
                return None
            
            if len(face_encodings) > 1:
                logger.warning(f'Multiple faces detected in image: {image_path}, using first face')
            
            logger.info(f'Face encoding generated from: {image_path}')
            return face_encodings[0]
            
        except FileNotFoundError as e:
            logger.error(f'File not found error: {str(e)}')
            raise
        except ValueError as e:
            logger.error(f'Image processing error: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'Unexpected error during face capture: {str(e)}')
            raise
    
    def compare_faces(self, known_encoding: np.ndarray, 
                     test_encoding: np.ndarray) -> float:
        """
        Compare two face encodings and return distance score.
        
        Args:
            known_encoding (np.ndarray): Reference face encoding
            test_encoding (np.ndarray): Face encoding to test
        
        Returns:
            float: Distance between encodings (0.0 = identical, 1.0+ = different)
                  Values below tolerance threshold are considered matches
        """
        try:
            distances = face_recognition.face_distance(
                [known_encoding],
                test_encoding
            )
            return float(distances[0])
        except Exception as e:
            logger.error(f'Face comparison error: {str(e)}')
            raise
    
    def is_match(self, known_encoding: np.ndarray, 
                test_encoding: np.ndarray) -> bool:
        """
        Verify if two face encodings match within tolerance threshold.
        
        Args:
            known_encoding (np.ndarray): Reference face encoding
            test_encoding (np.ndarray): Face encoding to test
        
        Returns:
            bool: True if faces match (distance < tolerance), False otherwise
        """
        distance = self.compare_faces(known_encoding, test_encoding)
        is_match = distance < self.tolerance
        
        logger.info(f'Face match result: {is_match} (distance: {distance:.4f})')
        return is_match
    
    def encoding_to_list(self, encoding: np.ndarray) -> List[float]:
        """
        Convert face encoding numpy array to JSON-serializable list.
        
        Args:
            encoding (np.ndarray): Face encoding array
        
        Returns:
            List[float]: Face encoding as list of floats
        """
        return encoding.tolist()
    
    def list_to_encoding(self, encoding_list: List[float]) -> np.ndarray:
        """
        Convert face encoding list back to numpy array.
        
        Args:
            encoding_list (List[float]): Face encoding as list
        
        Returns:
            np.ndarray: Face encoding as numpy array
        """
        return np.array(encoding_list)
    
    def get_face_landmarks(self, image_path: str) -> Optional[List]:
        """
        Get facial landmarks (eyes, nose, mouth, etc.) from image.
        
        Args:
            image_path (str): Path to face image
        
        Returns:
            List: Face landmarks or None if no face detected
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            landmarks = face_recognition.face_landmarks(rgb_image)
            
            return landmarks if landmarks else None
            
        except Exception as e:
            logger.error(f'Landmark detection error: {str(e)}')
            return None
    
    def detect_faces_in_image(self, image_path: str) -> List[tuple]:
        """
        Detect all faces in an image and return their bounding boxes.
        
        Args:
            image_path (str): Path to image
        
        Returns:
            List[tuple]: List of face locations as (top, right, bottom, left)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(
                rgb_image,
                model=self.model
            )
            
            return face_locations
            
        except Exception as e:
            logger.error(f'Face detection error: {str(e)}')
            return []
    
    def generate_encoding_from_array(self, image_array: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate face encoding from image numpy array (from webcam/stream).
        
        Args:
            image_array (np.ndarray): Image as numpy array (BGR format from OpenCV)
        
        Returns:
            np.ndarray: Face encoding or None if no face detected
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # Generate encodings
            face_encodings = face_recognition.face_encodings(
                rgb_image,
                model=self.model
            )
            
            if len(face_encodings) == 0:
                logger.warning('No face detected in image array')
                return None
            
            if len(face_encodings) > 1:
                logger.warning(f'Multiple faces detected, using first')
            
            return face_encodings[0]
            
        except Exception as e:
            logger.error(f'Encoding generation error: {str(e)}')
            return None
    
    def batch_compare_faces(self, known_encodings: List[np.ndarray],
                           test_encoding: np.ndarray) -> List[bool]:
        """
        Compare test encoding against multiple known encodings.
        
        Args:
            known_encodings (List[np.ndarray]): List of reference encodings
            test_encoding (np.ndarray): Test face encoding
        
        Returns:
            List[bool]: List of match results for each known encoding
        """
        try:
            results = face_recognition.compare_faces(
                known_encodings,
                test_encoding,
                tolerance=self.tolerance
            )
            return results
        except Exception as e:
            logger.error(f'Batch comparison error: {str(e)}')
            raise
    
    def batch_distance(self, known_encodings: List[np.ndarray],
                      test_encoding: np.ndarray) -> List[float]:
        """
        Get distance scores between test encoding and multiple known encodings.
        
        Args:
            known_encodings (List[np.ndarray]): List of reference encodings
            test_encoding (np.ndarray): Test face encoding
        
        Returns:
            List[float]: List of distance scores
        """
        try:
            distances = face_recognition.face_distance(
                known_encodings,
                test_encoding
            )
            return [float(d) for d in distances]
        except Exception as e:
            logger.error(f'Batch distance calculation error: {str(e)}')
            raise
    
    def get_best_match(self, known_encodings: List[np.ndarray],
                      test_encoding: np.ndarray) -> Tuple[int, float]:
        """
        Find best matching face from list of known encodings.
        
        Args:
            known_encodings (List[np.ndarray]): List of reference encodings
            test_encoding (np.ndarray): Test face encoding
        
        Returns:
            Tuple[int, float]: Tuple of (best_match_index, distance_score)
                              Returns (-1, float('inf')) if no good match
        """
        distances = self.batch_distance(known_encodings, test_encoding)
        
        if not distances:
            return (-1, float('inf'))
        
        best_match_idx = np.argmin(distances)
        best_match_distance = distances[best_match_idx]
        
        if best_match_distance < self.tolerance:
            return (best_match_idx, best_match_distance)
        else:
            return (-1, best_match_distance)
    
    def validate_image_quality(self, image_path: str) -> Dict[str, any]:
        """
        Validate image quality for face recognition.
        
        Args:
            image_path (str): Path to image
        
        Returns:
            Dict with quality metrics and validation result
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'valid': False, 'error': 'Failed to load image'}
            
            # Check brightness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Check if face is detectable
            faces = self.detect_faces_in_image(image_path)
            
            quality_check = {
                'valid': True,
                'brightness': float(brightness),
                'faces_detected': len(faces),
                'image_size': image.shape,
                'warnings': []
            }
            
            if brightness < 50 or brightness > 200:
                quality_check['warnings'].append('Poor lighting conditions')
                quality_check['valid'] = False
            
            if len(faces) == 0:
                quality_check['warnings'].append('No face detected')
                quality_check['valid'] = False
            elif len(faces) > 1:
                quality_check['warnings'].append('Multiple faces detected')
            
            return quality_check
            
        except Exception as e:
            logger.error(f'Image quality validation error: {str(e)}')
            return {'valid': False, 'error': str(e)}
