from hashlib import sha256


# NOTE Just an easy wrapper around sha256
def sha256_hex(input):
    return sha256(input.encode('utf-8')).hexdigest()
