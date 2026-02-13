# Flask backend for Steganography application (REST API)

from flask import Flask, request, session, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from supportFile import encode, encode_audio
import os
import cv2
import pyaes, pbkdf2, binascii
import pandas as pd

# Fixed IV and salt (demo use only)
iv = 99114684525942506313644461257805955214848508590114620791139267598143401799819
passwordSalt = b'$\xfb\x89\x1d\xb2\x08\x8f\x1b\xfa\xe49A`\xf9Z\xdc'

# Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024


def ensure_user_file():
    if not os.path.exists('users.csv'):
        df_users = pd.DataFrame({
            'username': ['admin'],
            'password': ['admin']
        })
        df_users.to_csv('users.csv', index=False)


def ensure_audio_log_file():
    if not os.path.exists('audio_log.csv'):
        df_audio = pd.DataFrame({
            'filename': [],
            'cipher_text': [],
            'timestamp': []
        })
        df_audio.to_csv('audio_log.csv', index=False)


# API ENDPOINTS

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Steganography API - Frontend: http://localhost:5173', 'status': 'running'})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})


@app.route('/api/audio-list', methods=['GET'])
def api_audio_list():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        ensure_audio_log_file()
        if os.path.exists('audio_log.csv'):
            df_audio = pd.read_csv('audio_log.csv')
            audio_list = df_audio.to_dict('records')
            return jsonify({'success': True, 'audio_files': audio_list})
        else:
            return jsonify({'success': True, 'audio_files': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    ensure_user_file()
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        pwd = data.get('password', '').strip()
        epass = data.get('epass', '').strip()

        if not username or not pwd or not epass:
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400

        df_users = pd.read_csv('users.csv')
        is_valid = ((df_users['username'] == username) &
                    (df_users['password'] == pwd)).any()

        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid Credentials'}), 401

        session['user'] = username
        session['aes_password'] = epass

        df_sec = pd.DataFrame({'password': [epass]})
        df_sec.to_csv('secrets.csv', index=False)

        return jsonify({'success': True, 'user': username, 'message': 'Login successful'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})


@app.route('/api/session', methods=['GET'])
def api_session():
    if 'user' not in session:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': session.get('user')})


@app.route('/api/home', methods=['GET'])
def api_home():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'message': f'Welcome {session.get("user")}', 'authenticated': True})


@app.route('/api/info', methods=['GET'])
def api_info():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'title': 'Steganography Information',
        'description': 'LSB Steganography with AES-256 Encryption'
    })


@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        filetype = request.form.get('filetype', 'image')
        
        if filetype == 'image':
            savepath = 'uploads'
            os.makedirs(savepath, exist_ok=True)

            photo = request.files.get('photo')
            photo1 = request.files.get('photo1')

            if photo and photo.filename:
                filepath = os.path.join(savepath, secure_filename(photo.filename))
                photo.save(filepath)
                img = cv2.imread(filepath)
                if img is not None:
                    cv2.imwrite("static/images/test_image.png", img)

            if photo1 and photo1.filename:
                filepath1 = os.path.join(savepath, secure_filename(photo1.filename))
                photo1.save(filepath1)
                img2 = cv2.imread(filepath1)
                if img2 is not None:
                    cv2.imwrite("static/images/test_image1.png", img2)

            return jsonify({'success': True, 'message': 'Images uploaded successfully'})

        elif filetype == 'audio':
            save_audio = 'upload_audio'
            os.makedirs(save_audio, exist_ok=True)

            audio = request.files.get('audiofile')
            if audio and audio.filename:
                audio_path = os.path.join(save_audio, secure_filename(audio.filename))
                audio.save(audio_path)
                session['audio_path'] = audio_path
                return jsonify({'success': True, 'message': 'Audio uploaded successfully'})

            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hide', methods=['POST'])
def api_hide():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    try:
        data = request.get_json()
        message = data.get('message', '')
        filetype = data.get('filetype', 'image')

        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        password = session.get('aes_password', '')
        if not password:
            return jsonify({'success': False, 'error': 'AES password not set'}), 400

        # Derive AES key
        try:
            key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Key derivation failed: {str(e)}'}), 500

        # Encrypt message
        try:
            plaintext = message.encode('utf-8')
            aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
            ciphertext = aes.encrypt(plaintext)
            cipher_hex = binascii.hexlify(ciphertext).decode()
        except Exception as e:
            return jsonify({'success': False, 'error': f'Encryption failed: {str(e)}'}), 500

        if filetype == 'image':
            try:
                # Check if image files exist
                if not os.path.exists('static/images/test_image.png'):
                    return jsonify({'success': False, 'error': 'Image 1 not uploaded'}), 400
                if not os.path.exists('static/images/test_image1.png'):
                    return jsonify({'success': False, 'error': 'Image 2 not uploaded'}), 400
                
                encode(ciphertext)
                return jsonify({
                    'success': True,
                    'message': 'Message hidden in image',
                    'cipher': cipher_hex
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'Image encoding failed: {str(e)}'}), 500

        elif filetype == 'audio':
            try:
                audio_path = session.get('audio_path')
                if not audio_path or not os.path.exists(audio_path):
                    return jsonify({'success': False, 'error': 'No audio file uploaded'}), 400

                encode_audio(audio_path, ciphertext)
                
                # Log audio file with encrypted message
                filename = os.path.basename(audio_path)
                ensure_audio_log_file()
                df_audio = pd.read_csv('audio_log.csv')
                new_entry = pd.DataFrame({
                    'filename': [filename],
                    'cipher_text': [cipher_hex],
                    'timestamp': [pd.Timestamp.now()]
                })
                df_audio = pd.concat([df_audio, new_entry], ignore_index=True)
                df_audio.to_csv('audio_log.csv', index=False)
                
                return jsonify({
                    'success': True,
                    'message': 'Message hidden in audio',
                    'cipher': cipher_hex
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'Audio encoding failed: {str(e)}'}), 500

        return jsonify({'success': False, 'error': 'Invalid filetype'}), 400

    except Exception as e:
        import traceback
        error_msg = f'{str(e)} - {traceback.format_exc()}'
        return jsonify({'success': False, 'error': error_msg}), 500


# DECRYPT MESSAGE API
@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    try:
        data = request.get_json()
        cipher_hex = data.get('cipherText', '').strip()
        password = data.get('password', '').strip()

        if not cipher_hex:
            return jsonify({'success': False, 'error': 'No cipher text provided'}), 400

        if not password:
            return jsonify({'success': False, 'error': 'No password provided'}), 400

        # Validate hex format
        if not all(c in '0123456789abcdefABCDEF' for c in cipher_hex):
            return jsonify({'success': False, 'error': 'Cipher text must be in hexadecimal format'}), 400

        if len(cipher_hex) % 2 != 0:
            return jsonify({'success': False, 'error': 'Cipher text has invalid length (must be even number of hex characters)'}), 400

        # Convert hex to bytes
        try:
            ciphertext = binascii.unhexlify(cipher_hex)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid cipher text format: {str(e)}'}), 400

        # Derive AES key from password
        try:
            key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Key derivation failed: {str(e)}'}), 500

        # Decrypt message
        try:
            aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
            plaintext = aes.decrypt(ciphertext)
            
            # Try to decode as UTF-8
            try:
                decrypted_message = plaintext.decode('utf-8')
            except UnicodeDecodeError as ue:
                return jsonify({
                    'success': False, 
                    'error': f'Decryption successful but result is not valid text. This usually means the password is incorrect or cipher text is corrupted. Details: {str(ue)}'
                }), 400
            
            return jsonify({
                'success': True,
                'message': decrypted_message
            })
        except Exception as e:
            return jsonify({'success': False, 'error': f'Decryption failed: {str(e)}'}), 500

    except Exception as e:
        import traceback
        error_msg = f'{str(e)} - {traceback.format_exc()}'
        return jsonify({'success': False, 'error': error_msg}), 500


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = (
        'no-store, no-cache, must-revalidate, '
        'post-check=0, pre-check=0, max-age=0'
    )
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
