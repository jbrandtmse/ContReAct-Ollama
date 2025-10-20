#!/usr/bin/env python3
"""
Quick test script to verify Telegram integration works with the Bot context manager fix.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from contreact_ollama.communication.telegram_service import TelegramOperatorChannel


def main():
    """Test the Telegram service."""
    print("Testing Telegram Bot context manager fix...")
    print("-" * 50)
    
    # Get authorized user from environment or use default
    authorized_user = int(os.getenv("TELEGRAM_AUTHORIZED_USER_ID", "2007989261"))
    
    try:
        # Initialize channel
        print(f"1. Initializing Telegram channel for user {authorized_user}...")
        channel = TelegramOperatorChannel(
            authorized_users=[authorized_user],
            timeout_minutes=1  # Short timeout for testing
        )
        print("   ✓ Channel initialized successfully")
        
        # Test connection
        print("\n2. Testing connection...")
        if channel.check_connection():
            print("   ✓ Connection check passed")
        else:
            print("   ✗ Connection check failed")
            return 1
        
        # Test sending a message
        print("\n3. Sending test message...")
        try:
            channel.send_message(
                message="🧪 This is a test message from the Telegram integration fix verification script.",
                run_id="test-run",
                cycle_number=0
            )
            print("   ✓ Message sent successfully!")
            print("\n✅ All tests passed! The Bot context manager fix is working correctly.")
            return 0
            
        except Exception as e:
            print(f"   ✗ Failed to send message: {e}")
            return 1
            
    except Exception as e:
        print(f"✗ Error during initialization: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
