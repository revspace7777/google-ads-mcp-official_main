#!/usr/bin/env python3
"""
Google Ads MCP Server Switcher
Allows switching between CDATA and Official Google Ads MCP servers
"""

import json
import os
import sys
from pathlib import Path

CONFIG_FILE = "mcp-config.json"

def load_config():
    """Load the MCP configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file {CONFIG_FILE} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {CONFIG_FILE}: {e}")
        return None

def save_config(config):
    """Save the MCP configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving {CONFIG_FILE}: {e}")
        return False

def list_servers(config):
    """List available MCP servers"""
    print("📋 Available Google Ads MCP Servers:")
    print("=" * 50)
    
    for i, server_name in enumerate(config['availableServers'], 1):
        server_config = config['mcpServers'][server_name]
        status = "🟢 ACTIVE" if server_name == config['activeServer'] else "⚪ Available"
        
        print(f"{i}. {server_name} {status}")
        print(f"   Description: {server_config.get('description', 'No description')}")
        print(f"   Command: {server_config['command']}")
        print()

def switch_server(config, server_name):
    """Switch to a different MCP server"""
    if server_name not in config['availableServers']:
        print(f"❌ Server '{server_name}' not found!")
        print(f"Available servers: {', '.join(config['availableServers'])}")
        return False
    
    old_server = config['activeServer']
    config['activeServer'] = server_name
    
    if save_config(config):
        print(f"✅ Switched from '{old_server}' to '{server_name}'")
        print(f"🔄 Restart Cursor/VS Code to apply changes")
        return True
    else:
        print("❌ Failed to save configuration")
        return False

def show_current_server(config):
    """Show current active server"""
    active = config['activeServer']
    server_config = config['mcpServers'][active]
    
    print(f"🎯 Current Active Server: {active}")
    print("=" * 50)
    print(f"Description: {server_config.get('description', 'No description')}")
    print(f"Command: {server_config['command']}")
    print(f"Working Directory: {server_config.get('cwd', 'Not set')}")
    
    if 'env' in server_config:
        print("Environment Variables:")
        for key, value in server_config['env'].items():
            print(f"  {key}: {value}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔧 Google Ads MCP Server Switcher")
        print("=" * 50)
        print("Usage:")
        print("  python switch-mcp-server.py list          - List available servers")
        print("  python switch-mcp-server.py current       - Show current server")
        print("  python switch-mcp-server.py switch <name> - Switch to server")
        print("  python switch-mcp-server.py help          - Show this help")
        return
    
    config = load_config()
    if not config:
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_servers(config)
    elif command == "current":
        show_current_server(config)
    elif command == "switch":
        if len(sys.argv) < 3:
            print("❌ Please specify a server name")
            print("Available servers:", ", ".join(config['availableServers']))
            return
        switch_server(config, sys.argv[2])
    elif command == "help":
        print("🔧 Google Ads MCP Server Switcher")
        print("=" * 50)
        print("This tool helps you switch between different Google Ads MCP servers:")
        print()
        print("• GoogleAds-CDATA: CDATA's Windows executable MCP server")
        print("• GoogleAds-Official: Official Google Ads MCP server from GitHub")
        print()
        print("After switching, restart Cursor/VS Code to apply changes.")
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python switch-mcp-server.py help' for usage information")

if __name__ == "__main__":
    main()
