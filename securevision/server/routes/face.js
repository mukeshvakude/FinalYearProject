const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');
const auth = require('../middleware/auth');

const UPLOAD_DIR = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, UPLOAD_DIR),
  filename: (_req, file, cb) => cb(null, `face-${Date.now()}-${file.originalname}`)
});
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });

// POST /api/face/verify
router.post(
  '/verify',
  auth,
  upload.fields([
    { name: 'image1', maxCount: 1 },
    { name: 'image2', maxCount: 1 }
  ]),
  async (req, res) => {
    const files = req.files;
    if (!files || !files.image1 || !files.image2) {
      return res.status(400).json({ error: 'Two images are required (fields: image1, image2)' });
    }

    const img1Path = files.image1[0].path;
    const img2Path = files.image2[0].path;

    try {
      const form = new FormData();
      form.append('image1', fs.createReadStream(img1Path));
      form.append('image2', fs.createReadStream(img2Path));

      const faceServiceUrl = process.env.FACE_SERVICE_URL || 'http://localhost:8000';
      const response = await axios.post(`${faceServiceUrl}/verify-face`, form, {
        headers: form.getHeaders(),
        timeout: 60000
      });

      return res.json(response.data);
    } catch (err) {
      console.error('Face verify error:', err.message);
      if (err.response) {
        return res.status(err.response.status).json(err.response.data);
      }
      return res.status(500).json({ error: 'Face service unavailable or error: ' + err.message });
    } finally {
      fs.unlink(img1Path, () => {});
      fs.unlink(img2Path, () => {});
    }
  }
);

module.exports = router;
