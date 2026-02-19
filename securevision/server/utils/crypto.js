const crypto = require('crypto');

const ALGORITHM = 'aes-256-cbc';

// Derive a 32-byte key from the env variable
function getKey() {
  const raw = process.env.AES_SECRET || 'default_32_char_secret_key_here!';
  // Ensure exactly 32 bytes (pad with zeros or truncate)
  return Buffer.from(raw.padEnd(32, '0').slice(0, 32), 'utf8');
}

/**
 * Encrypts plaintext using AES-256-CBC.
 * @param {string} text - plaintext to encrypt
 * @returns {string} "ivHex:ciphertextHex"
 */
function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, getKey(), iv);
  const encrypted = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()]);
  return `${iv.toString('hex')}:${encrypted.toString('hex')}`;
}

/**
 * Decrypts an AES-256-CBC encrypted string.
 * @param {string} data - "ivHex:ciphertextHex"
 * @returns {string} plaintext
 */
function decrypt(data) {
  const [ivHex, encryptedHex] = data.split(':');
  if (!ivHex || !encryptedHex) throw new Error('Invalid encrypted data format');
  const iv = Buffer.from(ivHex, 'hex');
  const encryptedBuffer = Buffer.from(encryptedHex, 'hex');
  const decipher = crypto.createDecipheriv(ALGORITHM, getKey(), iv);
  const decrypted = Buffer.concat([decipher.update(encryptedBuffer), decipher.final()]);
  return decrypted.toString('utf8');
}

module.exports = { encrypt, decrypt };
