import os

import rsa

# LINK https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class FMeshKeys:
    def __init__(self):
        # NOTE Identity keys
        self.privateKey = None
        self.privateBytes = None
        self.publicKey = None
        self.publicBytes = None

        # NOTE Encryption keys
        self.privateRSAKey = None
        self.privateRSAPEM = None
        self.publicRSAKey = None
        self.publicRSAPEM = None

        if os.path.exists("private.key"):
            print("[ED25519] Loading ed25519 private key...")
            self.load()
        else:
            print("[ED25519] Creating ed25519 private key...")
            self.create()

    def create(self):
        "ED25519 Creation"
        print("[ED25519] Generating ed25519 identity...")

        self.privateKey = ed25519.Ed25519PrivateKey.generate() 
        print(self.privateKey)

        self.privateBytes = self.privateKey.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        print(self.privateBytes.hex())

        # Public Key Creation
        self.publicDerivation()

        # RSA Creation
        self.derive()

        # Writing file
        self.save()

    def load(self, filepath="./"):
        # Reading file
        with open(filepath + "private.key", "rb") as keyFile:
            self.privateBytes = keyFile.read()

        # Loading key
        try:
            self.loadBytes(self.privateBytes)
            print("[ED25519] Loaded ed25519 private key from file [+]")
        except Exception as e:
            print("[ED25519] Could not load ed25519 private key: [X]")
            print(e)
            exit()
            
    def loadBytes(self, privateBytesProvided: bytes):
        "INFO privateBytesProvided must be the same kind of data as the privateBytes (aka bytes)"

        print("[ED25519] Loading ed25519 private key from bytes... [*]")
        self.privateKey = ed25519.Ed25519PrivateKey.from_private_bytes(privateBytesProvided)
        print("[ED25519] Loaded ed25519 private key from bytes [+]")

        # Public Key Creation
        self.publicDerivation()

        # RSA Creation
        self.derive()
        
    def publicDerivation(self):
        "INFO Deriving a public key from the private key"

        print("[ED25519] Generating ed25519 public key...[*]")
        self.publicKey = self.privateKey.public_key()
        
        self.publicBytes = self.publicKey.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        print("[ED25519] We are: " + self.publicBytes.hex())
        print("[ED25519] Generated ed25519 public key [+]")
        
    def derive(self):
        "RSA Derivation"
        print("[RSA] Generating RSA keys from ed25519 identity... [*]")
        self.privateRSAKey = rsa.generate_key(self.privateBytes.hex()) # So that the two are linked
        self.privateRSAPEM = self.privateRSAKey.exportKey("PEM")
        self.publicRSAKey = self.privateRSAKey.public_key()
        self.publicRSAPEM = self.publicRSAKey.exportKey("PEM")

        print("[RSA] Generated RSA keys from ed25519 identity [+]")

    def encrypt(self, message, publicKey=None):
        "Encrypting a message (returning bytes)"

        # Supporting self encryption
        if not publicKey:
            publicKey = self.publicRSAKey

        # Generating the encrypted message
        encrypted = rsa.encrypt(message, publicKey)
        return encrypted

    def decrypt(self, message, privateKey=None):
        "Decrypting a message (returning bytes)"

        # Supporting self decryption by default
        if not privateKey:
            privateKey = self.privateRSAKey

        # Generating the decrypted message
        decrypted = rsa.decrypt(message, privateKey)
        return decrypted

    def sign(self, message):
        "Sign a message after encoding it (returning bytes)"

        signature = self.privateKey.sign(message.encode('utf-8'))
        return signature

    def verify(self, message, signature, publicKeyProvided=None):
        "Verify a message (returning boolean)"

        # Supporting self verification
        if not publicKeyProvided:
            publicKeyProvided = self.publicKey

        # Generating the verified result
        return publicKeyProvided.verify(signature, message.encode('utf-8'))

    def save(self):
        "ANCHOR Utilities"

        print("[ED25519] Saving ed25519 key...")
        with open("private.key", "wb") as f:
            f.write(self.privateBytes)
