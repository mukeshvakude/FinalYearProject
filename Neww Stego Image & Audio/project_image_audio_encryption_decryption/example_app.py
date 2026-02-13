"""
EXAMPLE: Complete Flask App with Face Authentication Integration

This is a reference implementation showing how to integrate face authentication
into your existing Flask project.

IMPORTANT: Adjust import paths and database connections based on your setup.

Components:
1. Face authentication service (modular functions)
2. Database operations for MySQL
3. Flask routes/endpoints
4. Attempt limiting for security
"""

from flask import Flask, request, session, jsonify
import logging

# ============================================================================
# IMPORT FACE AUTHENTICATION MODULES
# ============================================================================

from services.face_authentication import face_auth_service
from services.face_database import (
    store_face_encoding,
    get_face_encoding,
    user_has_face_encoding,
    delete_face_encoding,
    add_face_encoding_column
)
from routes.face_routes import (
    register_face_endpoint,
    get_face_status_endpoint,
    delete_face_endpoint,
    decrypt_with_face_verification
)

# ============================================================================
# SETUP FLASK APP
# ============================================================================

app = Flask(__name__)
app.secret_key = 'your-secret-key'
logger = logging.getLogger(__name__)

# YOUR EXISTING SERVICES
# from services.encryption_service import EncryptionService
# from services.steganography_service import SteganographyService
# encryption_service = EncryptionService()
# steganography_service = SteganographyService()

# ============================================================================
# DATABASE CONNECTION (Adjust to your setup)
# ============================================================================

import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'steganography_db'
}

def get_db_connection():
    """Get MySQL database connection"""
    return mysql.connector.connect(**db_config)

db_connection = get_db_connection()

# ============================================================================
# INITIALIZE DATABASE (Run once on startup)
# ============================================================================

@app.before_first_request
def initialize_database():
    """
    Initialize database schema.
    Add face_encoding column if not exists.
    """
    try:
        add_face_encoding_column(db_connection)
        logger.info('Database initialized: face_encoding column added')
    except Exception as e:
        logger.error(f'Database initialization error: {str(e)}')

# ============================================================================
# EXISTING ROUTES (Do NOT modify)
# ============================================================================

@app.route('/login', methods=['POST'])
def login():
    """
    User login with email/password.
    
    IMPORTANT: This route is UNCHANGED.
    Face authentication is SEPARATE.
    
    Request JSON:
    {
        'email': 'user@example.com',
        'password': 'user_password'
    }
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Your existing authentication logic
        # ...
        
        # On successful authentication, set session
        session['user_id'] = user_id
        session['email'] = email
        
        return {
            'success': True,
            'message': 'Login successful',
            'user_id': user_id,
            'has_face': user_has_face_encoding(db_connection, user_id)
        }, 200
        
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return {'success': False, 'message': 'Login failed'}, 401


@app.route('/logout', methods=['POST'])
def logout():
    """
    User logout.
    
    UNCHANGED: Face authentication doesn't affect logout.
    """
    session.clear()
    return {'success': True, 'message': 'Logged out'}, 200


# ============================================================================
# NEW: FACE AUTHENTICATION ROUTES
# ============================================================================

@app.route('/register-face', methods=['POST'])
def register_face():
    """
    Register user's face.
    
    WORKFLOW:
    1. User logs in with password
    2. User chooses to register face (optional)
    3. User uploads face image
    4. Face encoding generated and stored
    
    Request: Multipart form-data
        - face_image: PNG/JPG file
    
    Response: JSON
        - success: bool
        - message: str
    
    Status Codes:
        201: Face registered
        400: Invalid image or no face detected
        401: Not logged in
        409: Face already registered (can overwrite)
    """
    return register_face_endpoint(request, session, db_connection)


@app.route('/face-status', methods=['GET'])
def face_status():
    """
    Check if user has registered face.
    
    Returns:
    {
        'success': bool,
        'has_face': bool,
        'can_decrypt_with_face': bool
    }
    """
    return get_face_status_endpoint(session, db_connection)


@app.route('/delete-face', methods=['POST'])
def delete_face():
    """
    Delete user's face registration.
    
    Useful for:
    - Re-registering with new face
    - Account cleanup
    - Security concerns
    
    Response:
    {
        'success': bool,
        'message': str
    }
    
    Status Codes:
        200: Face deleted
        401: Not logged in
        404: No face registered
    """
    return delete_face_endpoint(request, session, db_connection)


# ============================================================================
# MODIFIED: EXISTING DECRYPT ROUTE (Add face verification)
# ============================================================================

@app.route('/decrypt', methods=['POST'])
def decrypt():
    """
    Decrypt message with optional face verification.
    
    WORKFLOW:
    1. User submits cipher text and password
    2. If user has registered face:
       - Require face verification (max 3 attempts)
       - Compare face with stored encoding
    3. If no face registered:
       - Proceed with decryption normally
    4. Decrypt message using AES key
    
    Request JSON:
    {
        'cipherText': 'hex_encoded_cipher',
        'password': 'encryption_password',
        'face_image': 'base64_image'  (required if face registered)
    }
    
    Response:
    {
        'success': bool,
        'message': 'decrypted_text' or error message,
        'face_used_for_verification': bool
    }
    
    Status Codes:
        200: Decryption successful
        400: Invalid cipher text
        401: Not logged in or face verification failed
        405: Face verification required but no image provided
    """
    return decrypt_with_face_verification(
        request=request,
        session=session,
        db_connection=db_connection,
        encrypt_service=encryption_service,  # Your encryption service
        max_attempts=3  # Maximum face verification attempts
    )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {str(error)}')
    return {'success': False, 'message': 'Server error'}, 500


# ============================================================================
# REQUEST/RESPONSE HELPERS
# ============================================================================

@app.before_request
def before_request():
    """Request preprocessing"""
    # Optionally validate JSON
    if request.method == 'POST' and request.is_json:
        if not request.data:
            return {'error': 'Empty request body'}, 400


@app.after_request
def after_request(response):
    """Add security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_info(user_id):
    """Get user info including face status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT email, face_encoding FROM users WHERE id = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        return {
            'user_id': user_id,
            'email': result[0],
            'has_face': result[1] is not None
        }
    return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info('Starting Flask app with Face Authentication')
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,
        threaded=True
    )


# ============================================================================
# API SUMMARY
# ============================================================================

"""
API ENDPOINTS:

1. PASSWORD LOGIN (Unchanged)
   POST /login
   Body: {email, password}
   Returns: {success, user_id, has_face}

2. LOGOUT (Unchanged)
   POST /logout
   
3. NEW: REGISTER FACE (Optional)
   POST /register-face
   Body: multipart form {face_image}
   Response: {success, message}
   Status: 201 on success, 400 on error

4. NEW: CHECK FACE STATUS
   GET /face-status
   Response: {success, has_face, can_decrypt_with_face}

5. NEW: DELETE FACE
   POST /delete-face
   Response: {success, message}

6. DECRYPT (Modified)
   POST /decrypt
   Body: {cipherText, password, face_image}
   Response: {success, message, face_used_for_verification}
   
   If user has face:
   - Requires face_image in request
   - Verifies face before decryption
   - Max 3 attempts
   
   If user has NO face:
   - Proceeds without face verification


SECURITY FEATURES:

✅ Attempt Limiting
   - Maximum 3 face verification attempts per decrypt request
   - After 3 failures → 401 error
   - Prevents brute force attacks

✅ No Image Storage
   - Only 128-float encoding stored
   - Original images never saved
   - Prevents privacy leaks

✅ Clean Error Messages
   - Users know what went wrong
   - Specific error codes
   - Guidance on how to fix

✅ Session-Based
   - Face registration tied to logged-in user
   - Face verification in same session

✅ Optional Feature
   - Users can skip face registration
   - Decryption works without face
   - No forced flow


INTEGRATING THIS CODE:

1. Copy face_authentication.py to backend/services/
2. Copy face_database.py to backend/services/
3. Copy face_routes.py to backend/routes/
4. Update imports in your app.py
5. Register the /register-face, /face-status, /delete-face routes
6. Modify /decrypt route to use decrypt_with_face_verification()
7. Initialize database on startup
8. Done!

The face authentication is now SEPARATE from password login.
"""
