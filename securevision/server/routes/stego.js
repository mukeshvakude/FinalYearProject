const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const Jimp = require('jimp');
const auth = require('../middleware/auth');
const { encrypt, decrypt } = require('../utils/crypto');

const UPLOAD_DIR = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, UPLOAD_DIR),
  filename: (_req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });

// ── LSB helpers ──────────────────────────────────────────────────────────────

const DELIMITER = '11111110'; // 0xFF sentinel

/**
 * Encode a UTF-8 string as a binary bit-string with a trailing delimiter.
 */
function textToBinary(text) {
  const bytes = Buffer.from(text, 'utf8');
  return Array.from(bytes)
    .map((b) => b.toString(2).padStart(8, '0'))
    .join('') + DELIMITER;
}

/**
 * Convert a binary string back to UTF-8 text.
 */
function binaryToText(bits) {
  let text = '';
  for (let i = 0; i + 8 <= bits.length; i += 8) {
    text += String.fromCharCode(parseInt(bits.slice(i, i + 8), 2));
  }
  return Buffer.from(text, 'binary').toString('utf8');
}

/**
 * Hide binary data in the LSB of the red channel of every pixel.
 * Mutates the Jimp image in place.
 */
function lsbEncode(image, binaryData) {
  const { width, height } = image.bitmap;
  const capacity = width * height;
  if (binaryData.length > capacity) {
    throw new Error(`Image too small: needs ${binaryData.length} pixels, has ${capacity}`);
  }

  let bitIdx = 0;
  image.scan(0, 0, width, height, function (x, y, idx) {
    if (bitIdx >= binaryData.length) return;
    const red = this.bitmap.data[idx];
    const bit = parseInt(binaryData[bitIdx++], 10);
    // Clear LSB then set it to our bit
    this.bitmap.data[idx] = (red & 0xfe) | bit;
  });
}

/**
 * Extract LSB data from the red channel until the 8-bit delimiter (0xFF) is found.
 */
function lsbDecode(image) {
  const { width, height } = image.bitmap;
  let bits = '';

  image.scan(0, 0, width, height, function (x, y, idx) {
    bits += (this.bitmap.data[idx] & 1).toString();
  });

  // Search for delimiter
  const delimIdx = bits.indexOf(DELIMITER);
  if (delimIdx === -1) throw new Error('No hidden message found in this image');

  return binaryToText(bits.slice(0, delimIdx));
}

// ── Routes ───────────────────────────────────────────────────────────────────

// POST /api/stego/encode
router.post('/encode', auth, upload.single('image'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Image file is required (field: image)' });
  const { message } = req.body;
  if (!message || !message.trim()) {
    fs.unlink(req.file.path, () => {});
    return res.status(400).json({ error: 'message is required' });
  }

  try {
    const encrypted = encrypt(message.trim());
    const binary = textToBinary(encrypted);

    const image = await Jimp.read(req.file.path);
    lsbEncode(image, binary);

    const outFilename = `stego-${Date.now()}.png`;
    const outPath = path.join(UPLOAD_DIR, outFilename);
    await image.writeAsync(outPath);

    // Clean up original upload
    fs.unlink(req.file.path, () => {});

    return res.json({
      message: 'Message encoded successfully',
      downloadUrl: `/uploads/${outFilename}`
    });
  } catch (err) {
    fs.unlink(req.file.path, () => {});
    console.error('Encode error:', err);
    return res.status(500).json({ error: err.message || 'Encoding failed' });
  }
});

// POST /api/stego/decode
router.post('/decode', auth, upload.single('image'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Image file is required (field: image)' });

  try {
    const image = await Jimp.read(req.file.path);
    const extracted = lsbDecode(image);
    const decrypted = decrypt(extracted);

    fs.unlink(req.file.path, () => {});
    return res.json({ message: decrypted });
  } catch (err) {
    fs.unlink(req.file.path, () => {});
    console.error('Decode error:', err);
    return res.status(500).json({ error: err.message || 'Decoding failed' });
  }
});

module.exports = router;
