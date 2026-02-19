from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from deepface import DeepFace

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/verify-face', methods=['POST'])
def verify_face():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Two images required (image1, image2)'}), 400

    img1 = request.files['image1']
    img2 = request.files['image2']

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f2:
        img1.save(f1.name)
        img2.save(f2.name)
        try:
            result = DeepFace.verify(
                img1_path=f1.name,
                img2_path=f2.name,
                enforce_detection=False
            )
            return jsonify({
                'verified': result['verified'],
                'distance': result['distance'],
                'threshold': result['threshold'],
                'model': result.get('model', 'VGG-Face'),
                'similarity_score': round((1 - result['distance']) * 100, 2)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.unlink(f1.name)
            os.unlink(f2.name)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    # NOTE: This built-in Flask server is for development only.
    # In production use a WSGI server such as Gunicorn:
    #   gunicorn -w 2 -b 0.0.0.0:8000 app:app
    app.run(host='0.0.0.0', port=port, debug=False)
