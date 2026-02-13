"""
Face Authentication Endpoints

Flask routes for face registration and verification.
These are SEPARATE from password login.

Routes:
    POST /register-face      - Register user's face
    GET /face-status         - Check if user has registered face
    POST /delete-face        - Delete user's face registration
    (Modify /decrypt route to use face verification)

IMPORTANT: Do not modify password login behavior.
Face authentication is optional and independent.
"""

import logging
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import datetime

# Note: Adjust imports based on your Flask app structure
# from services.face_authentication import face_auth_service
# from services.face_database import (
#     store_face_encoding, get_face_encoding, 
#     user_has_face_encoding, delete_face_encoding,
#     add_face_encoding_column
# )

logger = logging.getLogger(__name__)


# ============================================================================
# FACE REGISTRATION ENDPOINT
# ============================================================================

def register_face_endpoint(request, session, db_connection):
    """
    Register user's face.
    
    REQUIREMENTS:
    - User must be logged in (session['user_id'] exists)
    - Captures face from uploaded image
    - Generates face encoding
    - Stores in database
    - Max 1 face per user (overwrites existing)
    
    Endpoint: POST /register-face
    
    Request Format:
        Multipart form data:
        - face_image: PNG/JPG image file (base64 or file upload)
    
    Returns:
        JSON response:
        {
            'success': bool,
            'message': str,
            'timestamp': str (ISO format)
        }
    
    Status Codes:
        201: Face registered successfully
        400: Invalid image or no face detected
        401: User not logged in
        409: Other face registration errors
        500: Server error
    """
    try:
        # STEP 1: Verify user is logged in
        if 'user_id' not in session:
            logger.warning('Unauthenticated face registration attempt')
            return {
                'success': False,
                'message': 'Must be logged in to register face',
                'error_code': 'NOT_AUTHENTICATED'
            }, 401
        
        user_id = session['user_id']
        
        # STEP 2: Get face image from request
        if 'face_image' not in request.files:
            logger.warning(f'No face image provided by user {user_id}')
            return {
                'success': False,
                'message': 'Face image is required',
                'error_code': 'MISSING_IMAGE'
            }, 400
        
        face_file = request.files['face_image']
        if face_file.filename == '':
            return {
                'success': False,
                'message': 'No file selected',
                'error_code': 'EMPTY_IMAGE'
            }, 400
        
        # Validate file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
        if '.' not in face_file.filename or \
           face_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            logger.warning(f'Invalid image format uploaded by user {user_id}')
            return {
                'success': False,
                'message': f'Invalid file type. Allowed: {allowed_extensions}',
                'error_code': 'INVALID_FORMAT'
            }, 400
        
        # STEP 3: Load image and convert to OpenCV format
        try:
            img = Image.open(face_file.stream)
            face_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f'Error loading image: {str(e)}')
            return {
                'success': False,
                'message': 'Could not process image file',
                'error_code': 'IMAGE_ERROR'
            }, 400
        
        # STEP 4: Generate face encoding
        face_encoding = face_auth_service.generate_encoding(face_image)
        
        if face_encoding is None:
            # Could be: no face, multiple faces, or error
            logger.warning(f'Face encoding generation failed for user {user_id}')
            return {
                'success': False,
                'message': 'Face detection failed. Possible reasons:\n'
                          '1. No face detected in image\n'
                          '2. Multiple faces detected\n'
                          '3. Poor image quality\n'
                          'Please try a clear photo with only your face.',
                'error_code': 'FACE_DETECTION_FAILED'
            }, 400
        
        # STEP 5: Convert encoding to JSON and store
        encoding_json = face_auth_service.encode_to_json(face_encoding)
        
        success = store_face_encoding(db_connection, user_id, encoding_json)
        
        if not success:
            logger.error(f'Failed to store face encoding for user {user_id}')
            return {
                'success': False,
                'message': 'Database error storing face',
                'error_code': 'DATABASE_ERROR'
            }, 500
        
        logger.info(f'Face registered successfully for user {user_id}')
        
        return {
            'success': True,
            'message': 'Face registered successfully! Your face can now be used for verification.',
            'face_registration_complete': True,
            'timestamp': datetime.now().isoformat()
        }, 201
        
    except Exception as e:
        logger.error(f'Register face error: {str(e)}', exc_info=True)
        return {
            'success': False,
            'message': 'Server error during face registration',
            'error_code': 'SERVER_ERROR'
        }, 500


# ============================================================================
# FACE STATUS ENDPOINT
# ============================================================================

def get_face_status_endpoint(session, db_connection):
    """
    Check if user has registered face.
    
    Endpoint: GET /face-status
    
    Returns:
        JSON response:
        {
            'success': bool,
            'has_face': bool,
            'can_decrypt': bool  (requires face for decryption if registered)
        }
    
    Status Codes:
        200: Success
        401: Not logged in
    """
    try:
        if 'user_id' not in session:
            return {'success': False, 'message': 'Not logged in'}, 401
        
        user_id = session['user_id']
        has_face = user_has_face_encoding(db_connection, user_id)
        
        logger.debug(f'Face status check for user {user_id}: has_face={has_face}')
        
        return {
            'success': True,
            'has_face': has_face,
            'can_decrypt_with_face': has_face
        }, 200
        
    except Exception as e:
        logger.error(f'Face status error: {str(e)}')
        return {'success': False, 'message': 'Error checking face status'}, 500


# ============================================================================
# DELETE FACE ENDPOINT
# ============================================================================

def delete_face_endpoint(request, session, db_connection):
    """
    Delete user's registered face.
    
    Useful for re-registration or account cleanup.
    
    Endpoint: POST /delete-face
    
    Returns:
        JSON response:
        {
            'success': bool,
            'message': str
        }
    
    Status Codes:
        200: Face deleted
        401: Not logged in
        404: No face registered
        500: Error
    """
    try:
        if 'user_id' not in session:
            return {'success': False, 'message': 'Not logged in'}, 401
        
        user_id = session['user_id']
        
        # Check if user has face
        if not user_has_face_encoding(db_connection, user_id):
            return {
                'success': False,
                'message': 'No face registration found to delete',
                'error_code': 'NO_FACE_FOUND'
            }, 404
        
        # Delete face encoding
        success = delete_face_encoding(db_connection, user_id)
        
        if success:
            logger.info(f'Face deleted for user {user_id}')
            return {
                'success': True,
                'message': 'Face registration deleted successfully'
            }, 200
        else:
            return {
                'success': False,
                'message': 'Error deleting face',
                'error_code': 'DELETE_ERROR'
            }, 500
        
    except Exception as e:
        logger.error(f'Delete face error: {str(e)}')
        return {'success': False, 'message': 'Server error'}, 500


# ============================================================================
# MODIFY EXISTING DECRYPT ENDPOINT
# ============================================================================

def decrypt_with_face_verification(request, session, db_connection, 
                                   encrypt_service, max_attempts=3):
    """
    Modified decrypt endpoint WITH face verification.
    
    WORKFLOW:
    1. User must be logged in
    2. Check if user has registered face
    3. If yes: Require face verification before decryption
    4. If no: Proceed with decryption normally
    
    This keeps face authentication OPTIONAL and SEPARATE.
    
    Args:
        request: Flask request object
        session: User session
        db_connection: Database connection
        encrypt_service: Encryption service for decryption
        max_attempts: Maximum face verification attempts (default: 3)
    
    Returns:
        JSON response with decrypted message or error
    
    Status Codes:
        200: Decryption successful
        400: Invalid cipher or decryption failed
        401: Not logged in
        401: Face verification failed (exceeded attempts)
        405: User has face but won't verify
    """
    try:
        # STEP 1: Verify user is logged in (existing check)
        if 'user_id' not in session:
            return {'success': False, 'message': 'Not logged in'}, 401
        
        user_id = session['user_id']
        
        # STEP 2: Get request data
        data = request.get_json()
        cipher_text = data.get('cipherText', '').strip()
        password = data.get('password', '').strip()
        
        if not cipher_text or not password:
            return {
                'success': False,
                'message': 'Cipher text and password required'
            }, 400
        
        # STEP 3: Check if user has registered face
        has_face = user_has_face_encoding(db_connection, user_id)
        
        if has_face:
            # STEP 4: User has face - require verification
            logger.info(f'User {user_id} has face encoding. Requiring verification.')
            
            # Get face verification data from request
            face_image_data = data.get('face_image')  # Base64 encoded image
            
            if not face_image_data:
                return {
                    'success': False,
                    'message': 'Face verification required. Please provide face image.',
                    'requires_face_verification': True,
                    'error_code': 'FACE_VERIFICATION_REQUIRED'
                }, 405
            
            # STEP 5: Verify face with attempt limiting
            face_verified = False
            attempts = session.get('face_attempts', 0)
            
            if attempts >= max_attempts:
                logger.warning(f'User {user_id} exceeded face verification attempts')
                session['face_attempts'] = 0  # Reset
                return {
                    'success': False,
                    'message': f'Maximum face verification attempts exceeded ({max_attempts})',
                    'error_code': 'MAX_ATTEMPTS_EXCEEDED'
                }, 401
            
            try:
                # Decode face image
                face_image_bytes = base64.b64decode(face_image_data)
                face_image = Image.open(BytesIO(face_image_bytes))
                face_image_cv = cv2.cvtColor(np.array(face_image), cv2.COLOR_RGB2BGR)
                
                # Generate live encoding
                live_encoding = face_auth_service.generate_encoding(face_image_cv)
                
                if live_encoding is None:
                    attempts += 1
                    session['face_attempts'] = attempts
                    logger.warning(f'Face detection failed for user {user_id} (attempt {attempts}/{max_attempts})')
                    return {
                        'success': False,
                        'message': f'Face detection failed. Please try again. Attempts: {attempts}/{max_attempts}',
                        'attempts_remaining': max_attempts - attempts,
                        'error_code': 'FACE_DETECTION_FAILED'
                    }, 401
                
                # Get stored encoding
                stored_json = get_face_encoding(db_connection, user_id)
                stored_encoding = face_auth_service.decode_from_json(stored_json)
                
                # Compare faces
                is_match, distance = face_auth_service.verify_face(stored_encoding, live_encoding)
                
                if not is_match:
                    attempts += 1
                    session['face_attempts'] = attempts
                    logger.warning(f'Face mismatch for user {user_id} (distance={distance:.4f}, attempt {attempts}/{max_attempts})')
                    return {
                        'success': False,
                        'message': f'Face does not match. Please try again. Attempts: {attempts}/{max_attempts}',
                        'attempts_remaining': max_attempts - attempts,
                        'distance': distance,
                        'error_code': 'FACE_MISMATCH'
                    }, 401
                
                # Face verified!
                face_verified = True
                session['face_attempts'] = 0  # Reset attempts on success
                logger.info(f'Face verified successfully for user {user_id}')
                
            except Exception as e:
                logger.error(f'Face verification error: {str(e)}')
                attempts += 1
                session['face_attempts'] = attempts
                return {
                    'success': False,
                    'message': f'Face verification error. Attempts: {attempts}/{max_attempts}',
                    'attempts_remaining': max_attempts - attempts,
                    'error_code': 'FACE_VERIFICATION_ERROR'
                }, 401
        
        # STEP 6: Proceed with decryption (face verified or not required)
        # This is your existing decryption logic
        result = encrypt_service.decrypt_message(cipher_text, password)
        
        if result['success']:
            logger.info(f'Message decrypted successfully for user {user_id} (face_required={has_face})')
            return {
                'success': True,
                'message': result['plaintext'],
                'face_used_for_verification': has_face
            }, 200
        else:
            return {
                'success': False,
                'message': result['error'],
                'error_code': 'DECRYPTION_FAILED'
            }, 400
        
    except Exception as e:
        logger.error(f'Decrypt error: {str(e)}', exc_info=True)
        return {'success': False, 'message': 'Server error during decryption'}, 500


# ============================================================================
# INTEGRATION GUIDE
# ============================================================================

"""
INTEGRATION STEPS:

1. Import in your Flask app.py:
   
   from services.face_authentication import face_auth_service
   from services.face_database import (
       store_face_encoding, get_face_encoding,
       user_has_face_encoding, delete_face_encoding,
       add_face_encoding_column
   )
   from routes.face_routes import (
       register_face_endpoint, get_face_status_endpoint,
       delete_face_endpoint, decrypt_with_face_verification
   )

2. Add database column on startup:
   
   @app.before_request
   def init_db():
       add_face_encoding_column(db_connection)

3. Register routes in your Flask app:
   
   @app.route('/register-face', methods=['POST'])
   def register_face():
       return register_face_endpoint(request, session, db_connection)
   
   @app.route('/face-status', methods=['GET'])
   def face_status():
       return get_face_status_endpoint(session, db_connection)
   
   @app.route('/delete-face', methods=['POST'])
   def delete_face():
       return delete_face_endpoint(request, session, db_connection)

4. MODIFY existing decrypt route:
   
   @app.route('/decrypt', methods=['POST'])  # EXISTING ROUTE
   def decrypt():
       # Replace with:
       return decrypt_with_face_verification(
           request, session, db_connection, 
           encryption_service,  # Your encryption service
           max_attempts=3
       )

5. Make sure database connection is available:
   - Update import statements to match your database setup
   - Ensure db_connection is passed to functions

IMPORTANT:
- Face registration is OPTIONAL
- Users can still login with password
- Decryption works WITHOUT face if no face registered
- Face verification only required IF user registered face
- Maximum 3 attempts before lockout
- Clean error messages for UX
"""
