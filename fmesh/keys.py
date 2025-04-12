import os

import rsa

# LINK https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class FMeshKeys:
    def __init__(self, fmesh):
        self.fmesh = fmesh

        # NOTE Identity keys
        self.private_key = None
        self.private_bytes = None
        self.public_key = None
        self.public_bytes = None

        # NOTE Encryption keys
        self.private_rsa_key = None
        self.private_rsa_pem = None
        self.public_rsa_key = None
        self.public_rsa_pem = None

        if os.path.exists("private.key"):
            self.fmesh.main_log.put("[ED25519] Loading ed25519 private key...")
            self.load()
        else:
            self.fmesh.main_log.put("[ED25519] Creating ed25519 private key...")
            self.create()

    def create(self):
        "ED25519 Creation"
        self.fmesh.main_log.put("[ED25519] Generating ed25519 identity...")

        self.private_key = ed25519.Ed25519PrivateKey.generate() 
        self.fmesh.main_log.put(self.private_key)

        self.private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.fmesh.main_log.put(self.private_bytes.hex())

        # Public Key Creation
        self.public_derivation()

        # RSA Creation
        self.derive()

        # Writing file
        self.save()

    def load(self, filepath="./"):
        # Reading file
        with open(filepath + "private.key", "rb") as key_file:
            self.private_bytes = key_file.read()

        # Loading key
        try:
            self.load_bytes(self.private_bytes)
            self.fmesh.main_log.put("[ED25519] Loaded ed25519 private key from file [+]")
        except Exception as e:
            self.fmesh.main_log.put("[ED25519] Could not load ed25519 private key: [X]")
            self.fmesh.main_log.put(e)
            exit()
            
    def load_bytes(self, private_bytes_provided: bytes):
        "INFO private_bytes_provided must be the same kind of data as the private_bytes (aka bytes)"

        self.fmesh.main_log.put("[ED25519] Loading ed25519 private key from bytes... [*]")
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes_provided)
        self.fmesh.main_log.put("[ED25519] Loaded ed25519 private key from bytes [+]")

        # Public Key Creation
        self.public_derivation()

        # RSA Creation
        self.derive()
        
    def public_derivation(self):
        "INFO Deriving a public key from the private key"

        self.fmesh.main_log.put("[ED25519] Generating ed25519 public key...[*]")
        self.public_key = self.private_key.public_key()
        
        self.public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        self.fmesh.main_log.put("[ED25519] We are: " + self.public_bytes.hex())
        self.fmesh.main_log.put("[ED25519] Generated ed25519 public key [+]")
        
    def derive(self):
        "RSA Derivation"
        self.fmesh.main_log.put("[RSA] Generating RSA keys from ed25519 identity... [*]")
        self.private_rsa_key = rsa.generate_key(self.private_bytes.hex()) # So that the two are linked
        self.private_rsa_pem = self.private_rsa_key.exportKey("PEM")
        self.public_rsa_key = self.private_rsa_key.public_key()
        self.public_rsa_pem = self.public_rsa_key.exportKey("PEM")

        self.fmesh.main_log.put("[RSA] Generated RSA keys from ed25519 identity [+]")

    def encrypt(self, message, public_key=None):
        "Encrypting a message (returning bytes)"

        # Supporting self encryption
        if not public_key:
            public_key = self.public_rsa_key

        # Generating the encrypted message
        encrypted = rsa.encrypt(message, public_key)
        return encrypted

    def decrypt(self, message, private_key=None):
        "Decrypting a message (returning bytes)"

        # Supporting self decryption by default
        if not private_key:
            private_key = self.private_rsa_key

        # Generating the decrypted message
        decrypted = rsa.decrypt(message, private_key)
        return decrypted

    def sign(self, message):
        "Sign a message after encoding it (returning bytes)"

        signature = self.private_key.sign(message.encode('utf-8'))
        return signature

    def verify(self, message, signature, public_key_provided=None):
        "Verify a message (returning boolean)"

        # Supporting self verification
        if not public_key_provided:
            public_key_provided = self.public_key

        # Generating the verified result
        return public_key_provided.verify(signature, message.encode('utf-8'))

    def save(self):
        "ANCHOR Utilities"

        self.fmesh.main_log.put("[ED25519] Saving ed25519 key...")
        with open("private.key", "wb") as f:
            f.write(self.private_bytes)
