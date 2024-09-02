from pypuf.simulation import ArbiterPUF
from pypuf.io import random_inputs
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import hashlib
import os
import numpy as np

def simulate_puf_responses():
    """
    Simulate PUF responses using ArbiterPUF from the pypuf library for both fixed and random challenges.
    """
    # Create an ArbiterPUF with a given number of stages (n=256) and a seed for repeatability
    puf = ArbiterPUF(n=256, seed=45)
    
    # Generate a fixed challenge and a random challenge
    fixed_challenge = np.array(random_inputs(n=256, N=1, seed=1))  # Convert list to NumPy array
    random_seed = int.from_bytes(os.urandom(4), byteorder='big')  # 32-bit seed for random challenge
    random_challenge = np.array(random_inputs(n=256, N=1, seed=random_seed))  # Convert list to NumPy array
    
    # Ensure challenges are in the correct format (NumPy array)
    challenges = np.vstack([fixed_challenge, random_challenge])  # Stack them to create a 2D array
    
    # Get the PUF responses to these challenges
    responses = puf.eval(challenges)
    
    # Convert the responses from -1, +1 to 0, 1
    response_bits = [(response > 0).astype(int).flatten() for response in responses]
    response_bytes = [bits.tobytes() for bits in response_bits]
    
    return response_bytes

def derive_ecc_key_from_response(response_bytes):
    """
    Derive an ECC key from the fixed challenge response using deterministic key generation.
    """
    # Use the first 256 bits of the response as the private key seed
    private_key_seed = response_bytes[0]  # First response is used for private key seed
    
    # Hash the seed to derive a deterministic private key
    private_key_int = int.from_bytes(hashlib.sha256(private_key_seed).digest(), 'big')
    
    # Use the private key to generate an ECC key pair
    private_key = ec.derive_private_key(private_key_int, ec.SECP256R1(), default_backend())
    return private_key

def sign_message_with_nonce(private_key, message):
    """
    Sign a message using ECDSA with the private key.
    """
    # Hash the message
    message_hash = hashlib.sha256(message.encode()).digest()
    
    # Sign the message
    signature = private_key.sign(message_hash, ec.ECDSA(hashes.SHA256()))
    
    return signature

def main():
    # Simulate PUF responses
    response_bytes = simulate_puf_responses()
    print(f"Response Bytes: {[r.hex() for r in response_bytes]}")

    # Derive ECC key from the fixed challenge response
    private_key = derive_ecc_key_from_response(response_bytes)
    public_key = private_key.public_key()
    
    # Display the ECC key pair
    private_key_bytes = private_key.private_numbers().private_value.to_bytes(32, byteorder='big')
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    print(f"ECC Private Key: {private_key_bytes.hex()}")
    print(f"ECC Public Key: {public_key_bytes.hex()}")

    # Sign a message with the private key
    message = "Example message1"
    signature = sign_message_with_nonce(private_key, message)
    
    print(f"Message Signature: {signature.hex()}")

if __name__ == "__main__":
    main()
