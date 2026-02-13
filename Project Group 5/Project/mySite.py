# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
from werkzeug import secure_filename
from supportFile import *
import os
import cv2
import pyaes, pbkdf2, binascii, os, secrets
import pandas as pd
#from flask_ngrok import run_with_ngrok
'''
# Derive a 256-bit AES encryption key from the password
password = "s3cr3t*c0d3"
passwordSalt = os.urandom(16)
key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
print('AES encryption key:', binascii.hexlify(key))
iv = secrets.randbits(256)
'''
iv = 99114684525942506313644461257805955214848508590114620791139267598143401799819
passwordSalt = b'$\xfb\x89\x1d\xb2\x08\x8f\x1b\xfa\xe49A`\xf9Z\xdc'
password = ''
login_status = 0

app = Flask(__name__)
#run_with_ngrok(app)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def input():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			password = request.form['epass']
			login_status = 1
			sec = {'login':login_status,'password':password}
			df = pd.DataFrame(sec,index=[0])
			df.to_csv('secrets.csv')

			return redirect(url_for('home'))

	return render_template('input.html', error=error)	
	

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/info', methods=['GET', 'POST'])
def info():
	return render_template('info.html')



@app.route('/image', methods=['GET', 'POST'])
def image():
	df = pd.read_csv('secrets.csv')
	sec = df.to_dict('list')
	password = sec['password'][0]
	login_status = sec['login'][0]
	key = pbkdf2.PBKDF2(password, passwordSalt).read(32)

	if(login_status != 1):
		return redirect(url_for('input'))

	if request.method == 'POST':
		if request.form['sub']=='Upload':
			savepath = r'upload/'
			photo = request.files['photo']
			photo.save(os.path.join(savepath,(secure_filename(photo.filename))))
			image = cv2.imread(os.path.join(savepath,secure_filename(photo.filename)))
			cv2.imwrite(os.path.join("static/images/","test_image.png"),image)

			photo1 = request.files['photo1']
			print(secure_filename(photo1.filename))
			photo1.save(os.path.join(savepath,(secure_filename(photo1.filename))))
			image = cv2.imread(os.path.join(savepath,secure_filename(photo1.filename)))
			cv2.imwrite(os.path.join("static/images/","test_image1.png"),image)

			return render_template('image.html')
		elif request.form['sub'] == 'Hide':
			mgs = request.form['mgs']
			# Encrypt the plaintext with the given key:
			#   ciphertext = AES-256-CTR-Encrypt(plaintext, key, iv)
			
			plaintext = mgs
			aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
			ciphertext = aes.encrypt(plaintext)
			print('Encrypted:', binascii.hexlify(ciphertext))
			encode(ciphertext)
			return render_template('image.html',cipher=binascii.hexlify(ciphertext))

	return render_template('image.html')



# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False, threaded=True)
	#app.run()