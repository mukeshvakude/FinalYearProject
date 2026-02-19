const crypto = require('crypto');

const ALGORITHM = 'aes-256-cbc';

// Derive a deterministic 32-byte key using SHA-256 so that any-length secret
// is safely normalised without sacrificing entropy.
function getKey() {
  const raw = process.env.AES_SECRET;
  if (!raw) throw new Error('AES_SECRET environment variable is not set');
  return crypto.createHash('sha256').update(raw, 'utf8').digest();
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
