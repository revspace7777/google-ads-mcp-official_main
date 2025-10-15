#!/usr/bin/env python3
"""
Test script for both Google Ads MCP servers
"""

import subprocess
import json
import time
import os
from pathlib import Path

def test_cdata_server():
    """Test the CDATA MCP server"""
    print("🧪 Testing CDATA MCP Server...")
    print("=" * 40)
    
    try:
        # Check if executable exists
        exe_path = Path("GoogleAdWordsMCPServer.exe")
        if not exe_path.exists():
            print("❌ GoogleAdWordsMCPServer.exe not found!")
            return False
        
        print(f"✅ Executable found: {exe_path.absolute()}")
        
        # Check if config file exists
        config_path = Path("google-ads.yaml")
        if not config_path.exists():
            print("❌ google-ads.yaml not found!")
            return False
        
        print(f"✅ Config file found: {config_path.absolute()}")
        
        # Try to run the server (with timeout)
        print("🔄 Starting CDATA server...")
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to see if it starts successfully
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ CDATA server started successfully!")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ CDATA server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CDATA server: {e}")
        return False

def test_official_server():
    """Test the official MCP server"""
    print("\n🧪 Testing Official MCP Server...")
    print("=" * 40)
    
    try:
        # Check if directory exists
        server_dir = Path("official-google-ads-mcp")
        if not server_dir.exists():
            print("❌ Official MCP server directory not found!")
            return False
        
        print(f"✅ Server directory found: {server_dir.absolute()}")
        
        # Check if Python is available
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Python not found!")
                return False
            print(f"✅ Python found: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Python not found!")
            return False
        
        # Try to run the server
        print("🔄 Testing official server...")
        result = subprocess.run(
            ["python", "-m", "ads_mcp.server", "--help"],
            cwd=str(server_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Official server test successful!")
            print("Help output:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Official server test failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Official server test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing official server: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Google Ads MCP Servers Test Suite")
    print("=" * 50)
    
    # Test CDATA server
    cdata_success = test_cdata_server()
    
    # Test official server
    official_success = test_official_server()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"CDATA Server: {'✅ PASS' if cdata_success else '❌ FAIL'}")
    print(f"Official Server: {'✅ PASS' if official_success else '❌ FAIL'}")
    
    if cdata_success and official_success:
        print("\n🎉 Both servers are ready to use!")
        print("Use 'python switch-mcp-server.py list' to see available servers")
    elif cdata_success:
        print("\n⚠️  Only CDATA server is ready")
    elif official_success:
        print("\n⚠️  Only Official server is ready")
    else:
        print("\n❌ No servers are ready. Please check the errors above.")

if __name__ == "__main__":
    main()
