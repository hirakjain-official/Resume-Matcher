#!/usr/bin/env python3
"""
Deployment Test Script
Tests basic functionality to ensure cloud deployment works correctly
"""

import os
import requests
import time
from pathlib import Path

def test_local_deployment():
    """Test local deployment setup"""
    print("🧪 Testing Local Deployment...")
    
    # Check if required files exist
    required_files = [
        'app.py',
        'resume_matcher.py', 
        'requirements.txt',
        '.env-example'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    # Check if templates exist
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/processing.html',
        'templates/results.html'
    ]
    
    for template in template_files:
        if Path(template).exists():
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            return False
    
    print("✅ Local deployment files verified")
    return True

def test_cloud_endpoints(base_url):
    """Test cloud deployment endpoints"""
    print(f"🌐 Testing Cloud Deployment at {base_url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Version: {health_data.get('version')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test main page
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Main page loading")
            if "Resume Matcher" in response.text:
                print("✅ Page content verified")
            else:
                print("⚠️ Page content may be incorrect")
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
        
        # Test favicon (should return 204)
        response = requests.get(f"{base_url}/favicon.ico", timeout=5)
        if response.status_code == 204:
            print("✅ Favicon endpoint working")
        else:
            print(f"⚠️ Favicon returned: {response.status_code} (expected 204)")
        
        print("✅ Cloud deployment endpoints verified")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("⚙️ Testing Environment Setup...")
    
    # Check if .env file exists
    if Path('.env').exists():
        print("✅ .env file exists")
        
        # Check if API key is configured (without exposing it)
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'OPENROUTER_API_KEY=' in env_content:
                if 'your_api_key_here' not in env_content:
                    print("✅ API key appears to be configured")
                else:
                    print("⚠️ API key not configured (using placeholder)")
            else:
                print("❌ OPENROUTER_API_KEY not found in .env")
    else:
        print("⚠️ .env file not found (may be using environment variables)")
    
    return True

def main():
    """Main test function"""
    print("🚀 AI Resume Matcher - Deployment Test")
    print("=" * 50)
    
    # Test local files
    if not test_local_deployment():
        print("❌ Local deployment test failed")
        return False
    
    print()
    
    # Test environment
    test_environment_setup()
    
    print()
    
    # Test cloud deployment if URL provided
    render_url = "https://resume-matcher-tahu.onrender.com"
    print(f"Testing cloud deployment at: {render_url}")
    
    if test_cloud_endpoints(render_url):
        print("\n🎉 All tests passed! Deployment looks good.")
    else:
        print("\n⚠️ Some cloud tests failed. Check the deployment logs.")
    
    print("\n📋 Next Steps:")
    print("1. Verify your OpenRouter API key is set correctly")
    print("2. Test file upload functionality manually")  
    print("3. Monitor logs for any processing errors")
    print("4. Check if processing works with sample resumes")

if __name__ == '__main__':
    main()