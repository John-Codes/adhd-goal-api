#!/usr/bin/env python3
"""
Debug script to decode JWT token and see its structure
"""

import jwt
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT secret key
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# Test JWT token provided by the user
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItZGVtbyIsImVtYWlsIjoidGVzdC5kZW1vQGV4YW1wbGUuY29tIiwibmFtZSI6IkRlbW8gVGVzdCBVc2VyIiwidGVzdF9hY2NvdW50Ijp0cnVlLCJpc192ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzYyOTcwNTMyfQ.QY265AVFyHEElwNoT1L1-w4oZMEXjTMI7Zpkm1m2w88"

def decode_jwt():
    """Decode JWT token and show its payload"""
    print("Decoding JWT token...")
    print(f"Secret key: {SECRET_KEY}")
    print(f"Algorithm: {ALGORITHM}")
    print()
    
    try:
        # First, let's try to decode without verification to see the header and payload
        # JWT tokens are base64 encoded, so we can decode them manually
        parts = TEST_TOKEN.split('.')
        if len(parts) != 3:
            print(f"ERROR: Invalid JWT format, expected 3 parts, got {len(parts)}")
            return
        
        header_part = parts[0]
        payload_part = parts[1]
        signature_part = parts[2]
        
        print("JWT Header (base64):", header_part)
        import base64
        header = json.loads(base64.urlsafe_b64decode(header_part + '=='))
        print("JWT Header:", json.dumps(header, indent=2))
        print()
        
        print("JWT Payload (base64):", payload_part)
        payload = json.loads(base64.urlsafe_b64decode(payload_part + '=='))
        print("JWT Payload:", json.dumps(payload, indent=2))
        print()
        
        # Try to verify with our secret key
        if SECRET_KEY is None:
            print("ERROR: JWT_SECRET_KEY is None! Check your .env file")
            return
        print("Attempting to verify with our secret key...")
        verified_payload = jwt.decode(TEST_TOKEN, SECRET_KEY, algorithms=[ALGORITHM])
        print("SUCCESS: Token verified!")
        print("Verified Payload:", json.dumps(verified_payload, indent=2))
        
        # Check all fields in the payload
        print("\nAll payload fields:")
        for key, value in verified_payload.items():
            print(f"  {key}: {value}")
            
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    decode_jwt()