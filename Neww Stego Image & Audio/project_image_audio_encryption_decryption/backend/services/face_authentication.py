"""
Face Authentication Service Module

Provides modular functions for face capture, encoding generation,
and face verification. Designed as a SEPARATE feature from password login.

Functions:
    - capture_face(): Capture face from webcam
    - generate_encoding(): Generate 128-dim face encoding
    - verify_face(): Compare two face encodings
    - encode_to_json(): Convert encoding to JSON string
    - decode_from_json(): Convert JSON back to encoding
"""

import cv2
import numpy as np
import json
import logging
from typing import Optional, Tuple

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠ Warning: face_recognition library not installed. Face authentication disabled.")

logger = logging.getLogger(__name__)


class FaceAuthenticationService:
    """
    Modular face authentication service.
    
    IMPORTANT: This is SEPARATE from password login.
    Users can use password login without face registration.
    """
    
    def __init__(self, tolerance: float = 0.6):
        """
        Initialize face authentication service.
        
        Args:
            tolerance (float): Face matching tolerance (0.0-1.0)
                              Lower = stricter matching
        """
        self.tolerance = tolerance
        self.model = 'hog'  # Use 'hog' for speed (default), 'cnn' for accuracy
        logger.info(f'Face Authentication Service initialized (tolerance={tolerance}, model={self.model})')
        
        # Pre-warm the face_recognition library on first load
        if FACE_RECOGNITION_AVAILABLE:
            try:
                logger.debug('Pre-warming face_recognition library...')
                dummy_array = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
                face_recognition.face_locations(dummy_array, model='hog')
                logger.debug('Face recognition library pre-warmed and ready')
            except Exception as e:
                logger.warning(f'Could not pre-warm face_recognition: {e}')
    
    def capture_face(self) -> Optional[np.ndarray]:
        """
        Capture face image from webcam.
        
        Returns:
            np.ndarray: Image array in BGR format, or None if failed
        
        Raises:
            RuntimeError: If webcam not available
        """
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                logger.error('Webcam not available')
                raise RuntimeError('Webcam not available. Please check camera permissions.')
            
            # Capture single frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logger.error('Failed to capture frame from webcam')
                raise RuntimeError('Failed to capture frame from webcam.')
            
            logger.info('Face captured from webcam')
            return frame
            
        except Exception as e:
            logger.error(f'Face capture error: {str(e)}')
            raise
    
    def generate_encoding(self, image: np.ndarray, use_fast_model: bool = False) -> Optional[np.ndarray]:
        """
        Generate 128-dimensional face encoding from image.
        
        IMPORTANT ERROR HANDLING:
        - No face detected → return None
        - Multiple faces detected → return None (ambiguous)
        - Single face detected → return encoding
        
        Args:
            image (np.ndarray): Image array (BGR format from OpenCV)
            use_fast_model (bool): Use fast HOG model instead of CNN (default: False)
        
        Returns:
            np.ndarray: 128-dim encoding vector, or None if validation fails
        """
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                raise RuntimeError('face_recognition library not installed')
            
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Optimize image size for faster processing
            height, width = rgb_image.shape[:2]
            if width > 800:
                scale = 800 / width
                rgb_image = cv2.resize(rgb_image, (int(width * scale), int(height * scale)))
                logger.debug(f'Resized image for faster processing: {width}x{height} -> {int(width * scale)}x{int(height * scale)}')
            
            # Detect faces in image (use fast model if requested)
            model_to_use = 'hog' if use_fast_model else self.model
            logger.debug(f'Detecting faces with model: {model_to_use}')
            face_locations = face_recognition.face_locations(rgb_image, model=model_to_use)
            
            # Validate face count
            if len(face_locations) == 0:
                logger.warning('No face detected in image')
                return None
            
            if len(face_locations) > 1:
                logger.warning(f'Multiple faces detected ({len(face_locations)}). Ambiguous.')
                return None
            
            # Generate encoding for single detected face
            logger.debug('Generating face encoding...')
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                logger.warning('Could not generate encoding from detected face')
                return None
            
            encoding = face_encodings[0]
            logger.info('Face encoding generated successfully')
            return encoding
            
        except Exception as e:
            logger.error(f'Encoding generation error: {str(e)}')
            raise
    
    def verify_face(self, stored_encoding: np.ndarray, 
                   live_encoding: np.ndarray) -> Tuple[bool, float]:
        """
        Verify if two face encodings match.
        
        Args:
            stored_encoding (np.ndarray): Stored reference encoding
            live_encoding (np.ndarray): Live capture encoding for verification
        
        Returns:
            Tuple[bool, float]: (is_match, distance_score)
                               distance < tolerance → Match (True)
                               distance >= tolerance → No Match (False)
        """
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                raise RuntimeError('face_recognition library not installed')
            
            # Calculate distance between encodings
            distance = face_recognition.face_distance([stored_encoding], live_encoding)[0]
            
            # Check if within tolerance
            is_match = distance < self.tolerance
            
            logger.info(f'Face verification: match={is_match}, distance={distance:.4f}, tolerance={self.tolerance}')
            return is_match, float(distance)
            
        except Exception as e:
            logger.error(f'Face verification error: {str(e)}')
            raise
    
    def encode_to_json(self, encoding: np.ndarray) -> str:
        """
        Convert face encoding numpy array to JSON string for database storage.
        
        Args:
            encoding (np.ndarray): 128-dim encoding vector
        
        Returns:
            str: JSON string representation
        """
        try:
            encoding_list = encoding.tolist()
            json_string = json.dumps(encoding_list)
            logger.debug('Encoding converted to JSON string')
            return json_string
        except Exception as e:
            logger.error(f'JSON encoding error: {str(e)}')
            raise
    
    def decode_from_json(self, json_string: str) -> np.ndarray:
        """
        Convert JSON string back to face encoding numpy array.
        
        Args:
            json_string (str): JSON string from database
        
        Returns:
            np.ndarray: 128-dim encoding vector
        """
        try:
            encoding_list = json.loads(json_string)
            encoding = np.array(encoding_list, dtype=np.float64)
            logger.debug('Encoding converted from JSON string')
            return encoding
        except Exception as e:
            logger.error(f'JSON decoding error: {str(e)}')
            raise


# Create singleton instance
face_auth_service = FaceAuthenticationService(tolerance=0.6)
