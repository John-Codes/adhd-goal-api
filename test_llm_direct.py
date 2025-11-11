#!/usr/bin/env python3
"""
Direct LLM functionality test using real API key from .env
This tests the core functionality without needing the full server running
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from LLM import LLMClient

def test_llm_with_real_key():
    """Test LLM client with the real API key from .env"""
    print("Testing LLM Client with real API key from .env file")
    print("=" * 60)
    
    try:
        # Get the real API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("FAIL: No OPENROUTER_API_KEY found in environment")
            return False
        
        print(f"Using API key: {api_key[:20]}...")
        
        # Initialize LLM client
        client = LLMClient(api_key=api_key)
        print("SUCCESS: LLMClient initialized with real API key")
        
        # Test a simple call
        response = client.call_llm("Say hello in exactly 3 words")
        print(f"Response: {response}")
        print("SUCCESS: LLM call completed successfully")
        
        return True
        
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_llm_without_key():
    """Test LLM client behavior without API key"""
    print("\nTesting LLM Client without API key (should fail)")
    print("=" * 60)
    
    # Temporarily remove API key
    original_key = os.environ.get("OPENROUTER_API_KEY")
    if "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]
    
    try:
        client = LLMClient()
        print("FAIL: Should have failed without API key")
        return False
    except ValueError as e:
        print(f"SUCCESS: Correctly failed with ValueError: {e}")
        return True
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        return False
    finally:
        # Restore API key
        if original_key:
            os.environ["OPENROUTER_API_KEY"] = original_key

def test_llm_override():
    """Test that explicit key overrides environment"""
    print("\nTesting explicit API key override")
    print("=" * 60)
    
    try:
        # Set environment variable
        os.environ["OPENROUTER_API_KEY"] = "environment-key-123"
        
        # Use explicit key
        client = LLMClient(api_key="explicit-key-456")
        
        if client.api_key == "explicit-key-456":
            print("SUCCESS: Explicit key correctly overrides environment")
            return True
        else:
            print(f"FAIL: Expected explicit key, got: {client.api_key}")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False
    finally:
        # Clean up
        os.environ.pop("OPENROUTER_API_KEY", None)

def main():
    """Run all direct LLM tests"""
    print("Direct LLM Functionality Testing")
    print("Using real API key from .env file for realistic testing")
    print()
    
    tests_passed = 0
    total_tests = 3
    
    if test_llm_with_real_key():
        tests_passed += 1
    
    if test_llm_without_key():
        tests_passed += 1
    
    if test_llm_override():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Direct LLM Tests: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("SUCCESS: All LLM functionality tests passed!")
        print("\nThe optional API key feature is working correctly:")
        print("- Real API key from .env file works")
        print("- Proper error handling for missing keys")
        print("- Explicit key overrides environment variable")
        print("\nNote: Full E2E tests require server startup (blocked by MongoDB)")
    else:
        print("WARNING: Some tests failed")

if __name__ == "__main__":
    main()