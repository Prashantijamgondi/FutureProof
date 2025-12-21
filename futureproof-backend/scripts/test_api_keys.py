#!/usr/bin/env python3
"""Test API keys configuration"""

import os
import sys
from dotenv import load_dotenv
import httpx
import asyncio

# Load environment
load_dotenv()

async def test_groq_key():
    """Test Groq API key"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found")
        return False
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        
        print("✅ Groq API key valid")
        return True
    except Exception as e:
        print(f"❌ Groq API key invalid: {str(e)}")
        return False

async def test_github_token():
    """Test GitHub token"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ GitHub token valid (user: {user.get('login')})")
                return True
            else:
                print(f"❌ GitHub token invalid (status: {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ GitHub token test failed: {str(e)}")
        return False

async def test_database():
    """Test database connection"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        connection = engine.connect()
        connection.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("=" * 50)
    print("🔑 Testing API Keys Configuration")
    print("=" * 50)
    print()
    
    results = []
    
    print("Testing Groq API Key...")
    results.append(await test_groq_key())
    print()
    
    print("Testing GitHub Token...")
    results.append(await test_github_token())
    print()
    
    print("Testing Database Connection...")
    results.append(await test_database())
    print()
    
    print("=" * 50)
    if all(results):
        print("✅ All tests passed! You're ready to go!")
    else:
        print("⚠️  Some tests failed. Check your .env configuration.")
    print("=" * 50)
    
    return all(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
