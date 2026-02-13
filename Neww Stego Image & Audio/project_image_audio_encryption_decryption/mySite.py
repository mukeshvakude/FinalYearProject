# mySite.py

from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.utils import secure_filename
from supportFile import encode   # image LSB encoding
import os
import cv2
import pyaes, pbkdf2, binascii
import pandas as pd

# Fixed IV and salt (demo use only)
iv = 99114684525942506313644461257805955214848508590114620791139267598143401799819
passwordSalt = b'$\xfb\x89\x1d\xb2\x08\x8f\x1b\xfa\xe49A`\xf9Z\xdc'

# Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# ----------------------------------------------
# Ensure users.csv exists
# ----------------------------------------------
def ensure_user_file():
    if not os.path.exists('users.csv'):
        df_users = pd.DataFrame({
            'username': ['admin'],
            'password': ['admin']
        })
        df_users.to_csv('users.csv', index=False)


# ----------------------------------------------
# LOGIN
# ----------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def input():
    error = None
    ensure_user_file()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        pwd = request.form.get('password', '').strip()
        epass = request.form.get('epass', '').strip()  # AES password

        df_users = pd.read_csv('users.csv')

        is_valid = ((df_users['username'] == username) &
                    (df_users['password'] == pwd)).any()

        if not is_valid:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['user'] = username
            session['aes_password'] = epass

            df_sec = pd.DataFrame({'password': [epass]})
            df_sec.to_csv('secrets.csv', index=False)

            return redirect(url_for('home'))

    return render_template('input.html', error=error)


# ----------------------------------------------
# LOGOUT
# ----------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('input'))


# ----------------------------------------------
# HOME
# ----------------------------------------------
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect(url_for('input'))
    return render_template('home.html')


# ----------------------------------------------
# INFO
# ----------------------------------------------
@app.route('/info', methods=['GET', 'POST'])
def info():
    if 'user' not in session:
        return redirect(url_for('input'))
    return render_template('info.html')


# ----------------------------------------------
# DECRYPTION PAGE PLACEHOLDER
# ----------------------------------------------
@app.route('/dcode', methods=['GET', 'POST'])
def dcode():
    if 'user' not in session:
        return redirect(url_for('input'))
    return render_template('dcode.html')


# ----------------------------------------------
# ENCRYPTION PAGE (IMAGE + AUDIO SUPPORT)
# ----------------------------------------------
@app.route('/image', methods=['GET', 'POST'])
def image():
    if 'user' not in session:
        return redirect(url_for('input'))

    # AES password from session
    password = session.get('aes_password', '')

    # fallback to secrets.csv
    if not password and os.path.exists('secrets.csv'):
        df_sec = pd.read_csv('secrets.csv')
        if len(df_sec) > 0:
            password = str(df_sec['password'][0])

    if not password:
        return redirect(url_for('input'))

    # Derive AES key
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)

    cipher = None  # used for GUI
    filetype = 'image'  # default mode

    if request.method == 'POST':

        action = request.form['sub']
        filetype = request.form.get('filetype', 'image')  # "image" or "audio"

        # ------------------------------------
        # UPLOAD
        # ------------------------------------
        if action == 'Uploads':

            # IMAGE UPLOAD
            if filetype == "image":

                savepath = 'uploads'
                os.makedirs(savepath, exist_ok=True)

                photo = request.files.get('photo')
                if photo and photo.filename:
                    filepath = os.path.join(savepath, secure_filename(photo.filename))
                    photo.save(filepath)
                    img = cv2.imread(filepath)
                    cv2.imwrite("static/images/test_image.png", img)

                photo1 = request.files.get('photo1')
                if photo1 and photo1.filename:
                    filepath1 = os.path.join(savepath, secure_filename(photo1.filename))
                    photo1.save(filepath1)
                    img2 = cv2.imread(filepath1)
                    cv2.imwrite("static/images/test_image1.png", img2)

            # AUDIO UPLOAD
            elif filetype == "audio":
                save_audio = 'upload_audio'
                os.makedirs(save_audio, exist_ok=True)

                audio = request.files.get('audiofile')
                if audio and audio.filename:
                    audio_path = os.path.join(save_audio, secure_filename(audio.filename))
                    audio.save(audio_path)

                    # store audio path for use during Hide
                    session['audio_path'] = audio_path

            # IMPORTANT: keep same mode (image/audio) after upload
            return render_template('image.html', cipher=None, filetype=filetype)

        # ------------------------------------
        # HIDE / ENCRYPT
        # ------------------------------------
        elif action == 'Hide':

            mgs = request.form['mgs']
            plaintext = mgs.encode('utf-8')

            # AES Encryption
            aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
            ciphertext = aes.encrypt(plaintext)

            # IMAGE ENCODING
            if filetype == "image":
                encode(ciphertext)

            # AUDIO ENCODING
            elif filetype == "audio":
                from supportFile import encode_audio
                audio_path = session.get('audio_path')

                if audio_path:
                    encode_audio(audio_path, ciphertext)
                else:
                    # No audio uploaded, stay in audio mode
                    return render_template('image.html', cipher=None, filetype='audio')

            cipher = binascii.hexlify(ciphertext).decode()

            # Keep mode after hide
            return render_template('image.html', cipher=cipher, filetype=filetype)

    # Initial GET load
    return render_template('image.html', cipher=cipher, filetype='image')


# ----------------------------------------------
# DISABLE CACHING
# ----------------------------------------------
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = (
        'no-store, no-cache, must-revalidate, '
        'post-check=0, pre-check=0, max-age=0'
    )
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


# ----------------------------------------------
# START SERVER
# ----------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
