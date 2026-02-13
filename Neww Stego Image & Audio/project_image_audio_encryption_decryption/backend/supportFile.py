# supportFile.py

from PIL import Image
import wave
import struct
import os

# ================================================================
# ---------------- IMAGE STEGANOGRAPHY ----------------------------
# ================================================================

# Convert encoding data into 8-bit binary
def genData(data):
    # data is expected to be bytes
    newd = []
    for i in data:
        newd.append(format(i, '08b'))  # i = int from 0-255
    return newd


def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        # take 3 pixels (9 channels)
        pix = [value for value in next(imdata)[:3] +
                              next(imdata)[:3] +
                              next(imdata)[:3]]

        # Store 8 bits of the current byte
        for j in range(8):
            if datalist[i][j] == '0' and pix[j] % 2 != 0:
                pix[j] -= 1
            elif datalist[i][j] == '1' and pix[j] % 2 == 0:
                pix[j] = pix[j] - 1 if pix[j] != 0 else 1

        # Stop bit in last channel (9th)
        if i == lendata - 1:
            # last byte → LSB = 1
            if pix[-1] % 2 == 0:
                pix[-1] = pix[-1] - 1 if pix[-1] != 0 else 1
        else:
            # not last → LSB = 0
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encode_enc(newimg, data):
    w = newimg.size[0]
    x, y = 0, 0

    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x, y = 0, y + 1
        else:
            x += 1


def encode(mgs):
    """
    mgs: bytes (ciphertext)
    First half -> test_image.png
    Second half -> test_image1.png
    """
    # First image
    image = Image.open('static/images/test_image.png', 'r')
    part1 = mgs[:len(mgs)//2]

    newimg = image.copy()
    encode_enc(newimg, part1)
    newimg.save('static/images/stegoImage.png')

    # Second image
    image2 = Image.open('static/images/test_image1.png', 'r')
    part2 = mgs[len(mgs)//2:]

    newimg2 = image2.copy()
    encode_enc(newimg2, part2)
    newimg2.save('static/images/stegoImage1.png')


# ================================================================
# ---------------- AUDIO STEGANOGRAPHY (NEW) ---------------------
# ================================================================

def encode_audio(audio_path, ciphertext_bytes):
    """
    Hide ciphertext into a WAV audio file using LSB in sample data.
    Output stored at static/audio/stego_audio.wav
    """

    # Ensure output folder exists
    os.makedirs("static/audio", exist_ok=True)

    # Open WAV file
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    song.close()

    # Convert ciphertext to bits
    bitstring = ''.join([format(byte, '08b') for byte in ciphertext_bytes])

    # Append stop marker "1111111111111110"
    bitstring += "1111111111111110"

    # Ensure audio capacity
    if len(bitstring) > len(frame_bytes):
        raise ValueError("Audio file too small to hide message.")

    # Modify LSB of audio bytes
    for i in range(len(bitstring)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bitstring[i])

    # Save output audio
    stego = wave.open("static/audio/stego_audio.wav", 'wb')
    stego.setparams(song.getparams())
    stego.writeframes(bytes(frame_bytes))
    stego.close()


# ================================================================
# ---------------- IMAGE DECODE FUNCTIONS ------------------------
# ================================================================

def _decode_single_image(path):
    """
    Read one stego image and recover the bytes stored in it.
    Stops when last bit (LSB) = 1.
    """
    image = Image.open(path, 'r')
    data = iter(image.getdata())
    bits = []

    while True:
        try:
            pixels = [value for value in next(data)[:3] +
                                      next(data)[:3] +
                                      next(data)[:3]]
        except StopIteration:
            break

        # First 8 channels = bits
        for i in range(8):
            bits.append(str(pixels[i] & 1))

        # Stop marker
        if (pixels[-1] & 1) == 1:
            break

    byte_arr = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8:
            break
        byte_arr.append(int("".join(chunk), 2))

    return bytes(byte_arr)


def decode():
    """
    Combine ciphertext parts from both stego images.
    """
    part1 = _decode_single_image('static/images/stegoImage.png')
    part2 = _decode_single_image('static/images/stegoImage1.png')
    return part1 + part2
