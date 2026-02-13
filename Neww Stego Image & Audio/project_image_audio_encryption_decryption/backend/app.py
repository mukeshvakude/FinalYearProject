

"""
Professional Steganography Application - Backend API

A Flask-based REST API for secure message hiding using LSB steganography
combined with AES-256-CTR encryption.

Features:
- User authentication and session management
- Image and audio steganography with AES encryption
- Comprehensive error handling and validation
- CORS support for cross-origin requests
"""

from flask import Flask, request, session, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import logging.config
import os
import sys

# Import application modules
from config import Config
from services.auth_service import AuthService
from services.encryption_service import EncryptionService
from services.steganography_service import SteganographyService
from services.file_manager import FileManager
from services.face_auth_service import FaceAuthService
from services.face_database_manager import FaceDatabaseManager
from utils.error_handler import handle_error
from utils.validators import validate_credentials, validate_message, validate_hex
from utils.logger import setup_logger

# Initialize Flask Application
app = Flask(__name__)
app.config.from_object(Config)

# Setup CORS
CORS(app, supports_credentials=True)

# Setup Logging
setup_logger()
logger = logging.getLogger(__name__)

# Initialize Services
auth_service = AuthService()
encryption_service = EncryptionService()
steganography_service = SteganographyService()
file_manager = FileManager()
face_auth_service = FaceAuthService(tolerance=0.6, model='large')
face_db_manager = FaceDatabaseManager(db_path=Config.DATABASE_FACES)


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint providing API status and information.
    
    Returns:
        JSON: API status and frontend URL
    """
    return jsonify({
        'message': 'Steganography API - Frontend: http://localhost:5173',
        'status': 'running',
        'version': '2.0.0'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring API availability.
    
    Returns:
        JSON: Health status information
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Steganography API'
    }), 200


# ============================================================================
# FACE AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/face/enroll', methods=['POST'])
def enroll_face():
    """
    Enroll user's face for authentication.
    
    Multipart Form Data:
        - face_image (file): Face image file (PNG, JPG, etc.)
    
    Returns:
        JSON: Enrollment status
        Status Codes:
            - 200: Face enrolled successfully
            - 400: Invalid image or no face detected
            - 401: Not authenticated
            - 409: User already has enrolled face
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        username = session.get('user')
        
        # Check if user already has face enrollment
        if face_db_manager.user_has_face(username):
            return handle_error('Face already enrolled for this user. Delete previous enrollment first.', 409)
        
        # Get uploaded face image
        if 'face_image' not in request.files:
            return handle_error('Face image file is required', 400)
        
        face_image = request.files['face_image']
        if not face_image or face_image.filename == '':
            return handle_error('No image selected', 400)
        
        # Validate file extension
        allowed_extensions = Config.ALLOWED_FACE_EXTENSIONS
        if not ('.' in face_image.filename and 
                face_image.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return handle_error(f'Invalid file type. Allowed: {allowed_extensions}', 400)
        
        # Save uploaded image
        file_manager.ensure_directory(Config.FACE_UPLOAD_FOLDER)
        filename = f'{username}_face_{datetime.now().timestamp()}.png'
        face_path = os.path.join(Config.FACE_UPLOAD_FOLDER, secure_filename(filename))
        face_image.save(face_path)
        
        # Generate face encoding
        try:
            face_encoding = face_auth_service.capture_face_from_image(face_path)
            if face_encoding is None:
                os.remove(face_path)
                return handle_error('No face detected in image. Please upload a clear face image.', 400)
        except Exception as e:
            os.remove(face_path)
            logger.error(f'Face encoding generation error: {str(e)}')
            return handle_error('Failed to process face image', 400)
        
        # Validate image quality
        quality = face_auth_service.validate_image_quality(face_path)
        if not quality['valid']:
            os.remove(face_path)
            warnings = ', '.join(quality['warnings'])
            return handle_error(f'Image quality issues: {warnings}', 400)
        
        # Enroll face in database
        encoding_list = face_auth_service.encoding_to_list(face_encoding)
        success = face_db_manager.enroll_face(
            username=username,
            face_encoding=encoding_list,
            face_image_path=face_path,
            encoding_version=Config.FACE_ENCODING_VERSION
        )
        
        if not success:
            os.remove(face_path)
            return handle_error('Failed to enroll face', 500)
        
        # Mark face enrollment in session
        session['face_enrolled'] = True
        
        logger.info(f'Face enrolled for user: {username}')
        
        return jsonify({
            'success': True,
            'message': 'Face enrolled successfully',
            'username': username,
            'enrollment_time': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'Face enrollment error: {str(e)}', exc_info=True)
        return handle_error('Face enrollment failed', 500)


@app.route('/api/face/verify', methods=['POST'])
def verify_face():
    """
    Verify user's face for authentication (live verification).
    
    Multipart Form Data:
        - face_image (file): Face image to verify
    
    Returns:
        JSON: Verification result and authentication token
        Status Codes:
            - 200: Face verified successfully
            - 400: Invalid image or face doesn't match
            - 401: Not authenticated or face verification failed
            - 404: User has no enrolled face
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        username = session.get('user')
        
        # Check if user has enrolled face
        if not face_db_manager.user_has_face(username):
            return handle_error('No face enrolled for this user', 404)
        
        # Get face image for verification
        if 'face_image' not in request.files:
            return handle_error('Face image file is required', 400)
        
        face_image = request.files['face_image']
        if not face_image or face_image.filename == '':
            return handle_error('No image selected', 400)
        
        # Validate file extension
        allowed_extensions = Config.ALLOWED_FACE_EXTENSIONS
        if not ('.' in face_image.filename and 
                face_image.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return handle_error(f'Invalid file type. Allowed: {allowed_extensions}', 400)
        
        # Save temporary verification image
        file_manager.ensure_directory(Config.FACE_UPLOAD_FOLDER)
        temp_filename = f'{username}_verify_{datetime.now().timestamp()}.png'
        temp_face_path = os.path.join(Config.FACE_UPLOAD_FOLDER, secure_filename(temp_filename))
        face_image.save(temp_face_path)
        
        try:
            # Generate encoding for verification image
            test_encoding = face_auth_service.capture_face_from_image(temp_face_path)
            if test_encoding is None:
                os.remove(temp_face_path)
                return handle_error('No face detected in verification image', 400)
            
            # Get enrolled face encoding
            known_encoding_list = face_db_manager.get_face_encoding(username)
            if not known_encoding_list:
                os.remove(temp_face_path)
                return handle_error('Enrolled face not found', 404)
            
            known_encoding = face_auth_service.list_to_encoding(known_encoding_list)
            
            # Compare faces
            is_match = face_auth_service.is_match(known_encoding, test_encoding)
            distance = face_auth_service.compare_faces(known_encoding, test_encoding)
            
            # Clean up temporary image
            os.remove(temp_face_path)
            
            if not is_match:
                logger.warning(f'Face verification failed for user: {username} (distance: {distance:.4f})')
                return jsonify({
                    'success': False,
                    'message': 'Face does not match enrolled face',
                    'distance': float(distance),
                    'tolerance': Config.FACE_RECOGNITION_TOLERANCE
                }), 401
            
            # Update authentication record
            face_db_manager.update_authentication(username)
            
            # Mark face as verified in session
            session['face_verified'] = True
            session['face_verification_time'] = datetime.now().isoformat()
            
            logger.info(f'Face verified for user: {username}')
            
            return jsonify({
                'success': True,
                'message': 'Face verified successfully',
                'username': username,
                'distance': float(distance),
                'tolerance': Config.FACE_RECOGNITION_TOLERANCE,
                'verification_time': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            if os.path.exists(temp_face_path):
                os.remove(temp_face_path)
            logger.error(f'Face verification processing error: {str(e)}')
            return handle_error('Face verification failed', 500)
        
    except Exception as e:
        logger.error(f'Face verification error: {str(e)}', exc_info=True)
        return handle_error('Face verification error', 500)


@app.route('/api/face/check-enrollment', methods=['GET'])
def check_face_enrollment():
    """
    Check if current user has enrolled face.
    
    Returns:
        JSON: Enrollment status and details
        Status Codes:
            - 200: Request successful
            - 401: Not authenticated
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        # If face recognition is disabled, return immediately
        if not Config.FACE_RECOGNITION_ENABLED:
            logger.debug('Face recognition disabled - skipping enrollment check')
            return jsonify({
                'username': session.get('user'),
                'face_enrolled': False,
                'stats': None,
                'face_required': False,
                'face_auth_disabled': True
            }), 200
        
        username = session.get('user')
        has_face = face_db_manager.user_has_face(username)
        
        stats = None
        if has_face:
            stats = face_db_manager.get_user_stats(username)
        
        return jsonify({
            'username': username,
            'face_enrolled': has_face,
            'stats': stats,
            'face_required': Config.FACE_RECOGNITION_ENABLED
        }), 200
        
    except Exception as e:
        logger.error(f'Error checking face enrollment: {str(e)}')
        return handle_error('Face enrollment check failed', 500)


@app.route('/api/face/delete', methods=['POST'])
def delete_face():
    """
    Delete user's enrolled face (for re-enrollment).
    
    Returns:
        JSON: Deletion status
        Status Codes:
            - 200: Face deleted successfully
            - 401: Not authenticated
            - 404: No face enrolled
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        username = session.get('user')
        
        # Delete face from database
        success = face_db_manager.delete_face(username)
        
        if not success:
            return handle_error('No face enrolled to delete', 404)
        
        # Clear face verification from session
        if 'face_verified' in session:
            del session['face_verified']
        if 'face_verification_time' in session:
            del session['face_verification_time']
        
        logger.info(f'Face deleted for user: {username}')
        
        return jsonify({
            'success': True,
            'message': 'Face enrollment deleted successfully',
            'username': username
        }), 200
        
    except Exception as e:
        logger.error(f'Face deletion error: {str(e)}')
        return handle_error('Face deletion failed', 500)


@app.route('/api/face/stats', methods=['GET'])
def get_face_stats():
    """
    Get face authentication statistics for current user.
    
    Returns:
        JSON: User face statistics
        Status Codes:
            - 200: Stats retrieved successfully
            - 401: Not authenticated
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        username = session.get('user')
        stats = face_db_manager.get_user_stats(username)
        
        return jsonify({
            'success': True,
            'username': username,
            'face_stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f'Error retrieving face stats: {str(e)}')
        return handle_error('Face stats retrieval failed', 500)


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """
    User registration endpoint with face enrollment requirement.
    
    IMPORTANT: This endpoint performs TWO OPERATIONS:
    1. Creates user account (username/password)
    2. Requires face enrollment before registration is complete
    
    Request JSON:
        - username (str): Desired username
        - password (str): Account password
        - epass (str): Encryption password for AES operations
    
    Returns:
        JSON: Registration status
        Status Codes:
            - 201: User created - face enrollment next
            - 400: Missing credentials or invalid input
            - 409: Username already exists
            - 500: Server error
    
    WORKFLOW:
    1. Frontend sends username, password, epass
    2. Backend creates user account
    3. Backend creates session
    4. Frontend prompts for face enrollment
    5. Face enrollment happens via separate /api/face/enroll endpoint
    """
    try:
        data = request.get_json()
        
        # Validate input
        validation_error = validate_credentials(data)
        if validation_error:
            return handle_error(validation_error['error'], 400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        epass = data.get('epass', '').strip()
        
        # Register user
        result = auth_service.register_user(username, password)
        
        if not result['success']:
            # Check if it's a duplicate username error
            status_code = 409 if 'already exists' in result['message'] else 400
            return handle_error(result['message'], status_code)
        
        # Create session for face enrollment
        session['user'] = username
        session['aes_password'] = epass
        session['registration_time'] = datetime.now().isoformat()
        session['face_enrolled'] = False  # Mark face as not enrolled yet
        
        logger.info(f'New user registered: {username} - Face enrollment pending')
        
        return jsonify({
            'success': True,
            'user': username,
            'message': 'User registered successfully. Please enroll your face to complete registration.',
            'next_step': 'face_enrollment',
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f'Registration error: {str(e)}', exc_info=True)
        return handle_error('Registration failed', 500)


@app.route('/api/login', methods=['POST'])
def login():
    """
    User login endpoint with credential validation and face verification.
    
    IMPORTANT: Based on configuration, face verification may be required.
    
    Request JSON:
        - username (str): User username
        - password (str): User password
        - epass (str): Encryption password for AES operations
    
    Returns:
        JSON: Success/failure status with user information
        Status Codes:
            - 200: Successful login (face enrolled or not required)
            - 206: Login successful but face enrollment/verification may be needed
            - 400: Missing or invalid credentials
            - 401: Invalid username/password or face verification required
            - 404: User not found
            - 500: Server error
    
    WORKFLOW:
    1. Validate username and password
    2. Create session
    3. Check if face enrollment is required (config dependent)
    4. If face enrolled: indicate face verification needed
    5. If face not enrolled: indicate face enrollment needed
    6. Frontend handles next steps (face enrollment or verification)
    """
    try:
        data = request.get_json()
        
        # Validate input
        validation_error = validate_credentials(data)
        if validation_error:
            return handle_error(validation_error['error'], 400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        epass = data.get('epass', '').strip()
        
        # Authenticate user
        if not auth_service.validate_user(username, password):
            logger.warning(f'Failed login attempt for user: {username}')
            return handle_error('Invalid credentials', 401)
        
        # Store in session
        session['user'] = username
        session['aes_password'] = epass
        session['login_time'] = datetime.now().isoformat()
        session['face_verified'] = False  # Reset face verification flag
        
        logger.info(f'User logged in: {username}')
        
        # Check if face recognition is enabled
        if Config.FACE_RECOGNITION_ENABLED:
            user_has_face = face_db_manager.user_has_face(username)
            
            if user_has_face:
                # Face is enrolled - user needs to verify it before sensitive operations
                response_data = {
                    'success': True,
                    'user': username,
                    'message': 'Login successful. Face verification required for sensitive operations.',
                    'face_enrolled': True,
                    'requires_face_verification': True,
                    'next_step': 'face_verification',
                    'timestamp': datetime.now().isoformat()
                }
                status_code = 206  # Partial - more authentication needed
            else:
                # No face enrolled - user needs to enroll
                response_data = {
                    'success': True,
                    'user': username,
                    'message': 'Login successful. Face enrollment is recommended for enhanced security.',
                    'face_enrolled': False,
                    'requires_face_enrollment': True,
                    'next_step': 'face_enrollment',
                    'timestamp': datetime.now().isoformat()
                }
                status_code = 206
        else:
            # Face recognition disabled - proceed normally
            response_data = {
                'success': True,
                'user': username,
                'message': 'Login successful',
                'timestamp': datetime.now().isoformat()
            }
            status_code = 200
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f'Login error: {str(e)}', exc_info=True)
        return handle_error('Internal server error', 500)


@app.route('/api/logout', methods=['POST'])
def logout():
    """
    User logout endpoint clearing session data.
    
    Returns:
        JSON: Logout confirmation
    """
    try:
        username = session.get('user', 'Unknown')
        session.clear()
        logger.info(f'User logged out: {username}')
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Logout error: {str(e)}')
        return handle_error('Logout failed', 500)


@app.route('/api/session', methods=['GET'])
def check_session():
    """
    Check current session authentication status.
    
    Returns:
        JSON: Authentication status and user information
        Status Codes:
            - 200: User is authenticated
            - 401: User is not authenticated
    """
    if 'user' not in session:
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user': session.get('user'),
        'login_time': session.get('login_time')
    }), 200


# ============================================================================
# CONTENT ENDPOINTS
# ============================================================================

@app.route('/api/home', methods=['GET'])
def home():
    """
    Home page content endpoint.
    
    Returns:
        JSON: Welcome message and user information
    """
    if 'user' not in session:
        return handle_error('Not authenticated', 401)
    
    return jsonify({
        'message': f'Welcome {session.get("user")}!',
        'authenticated': True,
        'description': 'Secure message hiding with LSB Steganography and AES-256 encryption'
    }), 200


@app.route('/api/info', methods=['GET'])
def info():
    """
    Application information endpoint.
    
    Returns:
        JSON: Application details and features
    """
    if 'user' not in session:
        return handle_error('Not authenticated', 401)
    
    return jsonify({
        'title': 'Steganography Information',
        'description': 'LSB Steganography with AES-256 Encryption',
        'encryption': 'AES-256-CTR',
        'key_derivation': 'PBKDF2',
        'features': [
            'Image steganography (2-image LSB encoding)',
            'Audio steganography (WAV file LSB encoding)',
            'Military-grade AES-256 encryption',
            'PBKDF2 key derivation',
            'Session-based authentication'
        ]
    }), 200


# ============================================================================
# FILE MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """
    File upload endpoint supporting images and audio files.
    
    Form Parameters:
        - filetype (str): 'image' or 'audio'
        - photo (file): First image file (for image type)
        - photo1 (file): Second image file (for image type)
        - audiofile (file): Audio file in WAV format (for audio type)
    
    Returns:
        JSON: Upload status and confirmation
        Status Codes:
            - 200: Files uploaded successfully
            - 400: Invalid files or missing files
            - 401: Not authenticated
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        filetype = request.form.get('filetype', 'image')
        
        if filetype == 'image':
            return _handle_image_upload()
        elif filetype == 'audio':
            return _handle_audio_upload()
        else:
            return handle_error('Invalid file type. Use "image" or "audio"', 400)
            
    except Exception as e:
        logger.error(f'Upload error: {str(e)}', exc_info=True)
        return handle_error('File upload failed', 500)


def _handle_image_upload():
    """
    Handle image file uploads and processing.
    
    Returns:
        JSON: Upload status
    """
    try:
        photo = request.files.get('photo')
        photo1 = request.files.get('photo1')
        
        if not photo and not photo1:
            return handle_error('At least one image is required', 400)
        
        file_manager.ensure_directory('uploads')
        
        if photo and photo.filename:
            filepath = os.path.join('uploads', secure_filename(photo.filename))
            photo.save(filepath)
            file_manager.process_image(filepath, 'static/images/test_image.png')
            logger.info(f'Image 1 uploaded: {photo.filename}')
        
        if photo1 and photo1.filename:
            filepath1 = os.path.join('uploads', secure_filename(photo1.filename))
            photo1.save(filepath1)
            file_manager.process_image(filepath1, 'static/images/test_image1.png')
            logger.info(f'Image 2 uploaded: {photo1.filename}')
        
        return jsonify({
            'success': True,
            'message': 'Images uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Image upload error: {str(e)}')
        return handle_error('Image upload failed', 500)


def _handle_audio_upload():
    """
    Handle audio file uploads and processing.
    
    Returns:
        JSON: Upload status
    """
    try:
        audio = request.files.get('audiofile')
        
        if not audio or not audio.filename:
            return handle_error('Audio file is required', 400)
        
        if not audio.filename.lower().endswith('.wav'):
            return handle_error('Only WAV format is supported', 400)
        
        file_manager.ensure_directory('upload_audio')
        
        filename = secure_filename(audio.filename)
        audio_path = os.path.join('upload_audio', filename)
        audio.save(audio_path)
        
        session['audio_path'] = audio_path
        logger.info(f'Audio uploaded: {filename}')
        
        return jsonify({
            'success': True,
            'message': 'Audio uploaded successfully',
            'filename': filename
        }), 200
        
    except Exception as e:
        logger.error(f'Audio upload error: {str(e)}')
        return handle_error('Audio upload failed', 500)


# ============================================================================
# STEGANOGRAPHY ENDPOINTS
# ============================================================================

@app.route('/api/hide', methods=['POST'])
def hide_message():
    """
    Hide an encrypted message in image or audio files.
    
    Request JSON:
        - message (str): Message to hide
        - filetype (str): 'image' or 'audio'
    
    Returns:
        JSON: Cipher text and success status
        Status Codes:
            - 200: Message hidden successfully
            - 400: Invalid input or missing files
            - 401: Not authenticated
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        data = request.get_json()
        message = data.get('message', '').strip()
        filetype = data.get('filetype', 'image')
        
        # Validate message
        validation_error = validate_message(message)
        if validation_error:
            return handle_error(validation_error['error'], 400)
        
        # Get AES password from session
        aes_password = session.get('aes_password')
        if not aes_password:
            return handle_error('Encryption password not set', 400)
        
        # Encrypt message
        cipher_hex = encryption_service.encrypt_message(message, aes_password)
        
        # Hide in media
        if filetype == 'image':
            result = _hide_in_image(cipher_hex)
        elif filetype == 'audio':
            result = _hide_in_audio(cipher_hex)
        else:
            return handle_error('Invalid file type', 400)
        
        if not result['success']:
            return handle_error(result['error'], 400)
        
        logger.info(f'Message hidden in {filetype} by user {session.get("user")}')
        
        return jsonify({
            'success': True,
            'message': f'Message hidden in {filetype}',
            'cipher': cipher_hex
        }), 200
        
    except Exception as e:
        logger.error(f'Hide message error: {str(e)}', exc_info=True)
        return handle_error('Failed to hide message', 500)


def _hide_in_image(cipher_hex):
    """
    Hide cipher text in two image files.
    
    Args:
        cipher_hex (str): Encrypted message in hexadecimal format
    
    Returns:
        dict: Success status and error message if applicable
    """
    try:
        if not (os.path.exists('static/images/test_image.png') and 
                os.path.exists('static/images/test_image1.png')):
            return {
                'success': False,
                'error': 'Required image files not found. Please upload both images.'
            }
        
        # Decode cipher and hide in images
        ciphertext = bytes.fromhex(cipher_hex)
        steganography_service.encode_image(ciphertext)
        
        return {'success': True}
        
    except Exception as e:
        logger.error(f'Image encoding error: {str(e)}')
        return {'success': False, 'error': f'Image encoding failed: {str(e)}'}


def _hide_in_audio(cipher_hex):
    """
    Hide cipher text in audio file and log the operation.
    
    Args:
        cipher_hex (str): Encrypted message in hexadecimal format
    
    Returns:
        dict: Success status and error message if applicable
    """
    try:
        audio_path = session.get('audio_path')
        
        if not audio_path or not os.path.exists(audio_path):
            return {
                'success': False,
                'error': 'No audio file uploaded'
            }
        
        # Decode cipher and hide in audio
        ciphertext = bytes.fromhex(cipher_hex)
        steganography_service.encode_audio(audio_path, ciphertext)
        
        # Log audio operation
        steganography_service.log_audio_operation(audio_path, cipher_hex)
        
        return {'success': True}
        
    except Exception as e:
        logger.error(f'Audio encoding error: {str(e)}')
        return {'success': False, 'error': f'Audio encoding failed: {str(e)}'}


@app.route('/api/decrypt', methods=['POST'])
def decrypt_message():
    """
    Decrypt a previously encrypted message.
    
    SECURITY: Requires face authentication before decryption if enabled.
    
    Request JSON:
        - cipherText (str): Encrypted message in hexadecimal format
        - password (str): Decryption password
    
    Returns:
        JSON: Decrypted message or error details
        Status Codes:
            - 200: Successfully decrypted
            - 400: Invalid cipher text or decryption failed
            - 401: Not authenticated or face verification required
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        username = session.get('user')
        
        # Check if face authentication is required and verified (only if enabled)
        if Config.FACE_RECOGNITION_ENABLED:
            if not face_db_manager.user_has_face(username):
                return handle_error(
                    'Face authentication required. Please enroll your face first.',
                    401
                )
            
            if not session.get('face_verified'):
                return handle_error(
                    'Face verification required before decryption. Please verify your face.',
                    401
                )
        
        data = request.get_json()
        cipher_hex = data.get('cipherText', '').strip()
        password = data.get('password', '').strip()
        
        # Validate inputs
        if not cipher_hex:
            return handle_error('Cipher text is required', 400)
        
        if not password:
            return handle_error('Password is required', 400)
        
        # Validate hex format
        hex_error = validate_hex(cipher_hex)
        if hex_error:
            return handle_error(hex_error, 400)
        
        # Decrypt message
        result = encryption_service.decrypt_message(cipher_hex, password)
        
        if not result['success']:
            logger.warning(f'Decrypt attempt failed: {result["error"]}')
            return handle_error(result['error'], 400)
        
        logger.info(f'Message decrypted by user {username}' + 
                   (' (face verified)' if Config.FACE_RECOGNITION_ENABLED else ''))
        
        return jsonify({
            'success': True,
            'message': result['plaintext']
        }), 200
        
    except Exception as e:
        logger.error(f'Decrypt error: {str(e)}', exc_info=True)
        return handle_error('Decryption failed', 500)


@app.route('/api/audio-list', methods=['GET'])
def get_audio_list():
    """
    Get list of uploaded audio files with their encrypted messages.
    
    Returns:
        JSON: List of audio files with cipher texts
        Status Codes:
            - 200: List retrieved successfully
            - 401: Not authenticated
            - 500: Server error
    """
    try:
        if 'user' not in session:
            return handle_error('Not authenticated', 401)
        
        audio_files = steganography_service.get_audio_log()
        
        return jsonify({
            'success': True,
            'audio_files': audio_files,
            'count': len(audio_files)
        }), 200
        
    except Exception as e:
        logger.error(f'Audio list error: {str(e)}')
        return handle_error('Failed to retrieve audio list', 500)


# ============================================================================
# MIDDLEWARE AND ERROR HANDLERS
# ============================================================================

@app.before_request
def before_request():
    """Request preprocessing and validation."""
    if request.method == 'POST' and request.is_json:
        if not request.data:
            return handle_error('Request body cannot be empty', 400)


@app.after_request
def after_request(response):
    """
    Apply response headers to prevent caching.
    Ensures fresh content is always loaded.
    """
    response.headers['Cache-Control'] = (
        'no-store, no-cache, must-revalidate, max-age=0'
    )
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return handle_error('Endpoint not found', 404)


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    return handle_error('Method not allowed', 405)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f'Internal server error: {str(error)}')
    return handle_error('Internal server error', 500)


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info('Starting Steganography API Server...')
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,
        threaded=True
    )
