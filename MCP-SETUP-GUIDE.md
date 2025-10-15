# Google Ads MCP Servers Setup Guide

## Overview
You now have **two Google Ads MCP servers** configured with the ability to switch between them:

1. **CDATA MCP Server** - Windows executable (`GoogleAdWordsMCPServer.exe`)
2. **Official MCP Server** - GitHub repository implementation

## Current Status ✅

### Credentials Configured
- ✅ OAuth Client ID & Secret
- ✅ Refresh Token generated
- ✅ Developer Token added
- ✅ MCC Login Customer ID: `4673669771`
- ✅ Configuration file: `google-ads.yaml`

### Files Created
- ✅ `google-ads.yaml` - Complete API configuration
- ✅ `mcp-config.json` - MCP server switching configuration
- ✅ `switch-mcp-server.py` - Server switching utility
- ✅ `test-mcp-servers.py` - Testing script
- ✅ `customer_ids.txt` - Reference for all customer accounts

## Next Steps

### 1. CDATA MCP Server Setup
**Status**: Ready to configure in Cursor dialog
- Open the "Data MCP Server for GoogleAds" dialog
- Fill in:
  - Developer Token: `K3HnqTUWdg1HX5ThupLw_Q`
  - Client Customer ID: `4673669771`
- Click "Connect" then "Save Configuration"

### 2. Official MCP Server Setup
**Status**: Needs uv installation
```powershell
# Install uv globally
pip install --user uv

# Install dependencies
cd official-google-ads-mcp
uv pip sync
cd ..
```

### 3. Test Both Servers
```powershell
# Test both servers
python test-mcp-servers.py

# List available servers
python switch-mcp-server.py list

# Switch between servers
python switch-mcp-server.py switch GoogleAds-CDATA
python switch-mcp-server.py switch GoogleAds-Official
```

## Usage Examples

### Switch to CDATA Server
```powershell
python switch-mcp-server.py switch GoogleAds-CDATA
```

### Switch to Official Server
```powershell
python switch-mcp-server.py switch GoogleAds-Official
```

### Check Current Server
```powershell
python switch-mcp-server.py current
```

## Cursor Configuration

After switching servers, update your Cursor MCP configuration:

### For CDATA Server
```json
{
  "mcpServers": {
    "GoogleAds": {
      "command": "GoogleAdWordsMCPServer.exe",
      "args": [],
      "cwd": "C:\\Users\\samso\\_cursor_projects\\google-ads-mcp",
      "env": {
        "GOOGLE_ADS_CONFIG": "google-ads.yaml"
      }
    }
  }
}
```

### For Official Server
```json
{
  "mcpServers": {
    "GoogleAds": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\samso\\_cursor_projects\\google-ads-mcp\\official-google-ads-mcp",
        "-m",
        "ads_mcp.server"
      ],
      "env": {
        "GOOGLE_ADS_CREDENTIALS": "C:\\Users\\samso\\_cursor_projects\\google-ads-mcp\\google-ads.yaml"
      }
    }
  }
}
```

## Customer Accounts Available
- T&E Moving and Storage LLC: `5840144764`
- B & B Movers (Tarik Bilgin): `2111371572`
- 678 Rid Junk LLC: `8640190225`
- Moving & Storage of Jacksonville: `7283506172`
- Ocean Movers Main: `1556744976`
- ILO's Appliance Repair: `5727024154`
- Colonial Trucking Insurance: `2452257371`

## Troubleshooting

### CDATA Server Issues
- **Elevation Required**: Run PowerShell as Administrator
- **Config Not Found**: Ensure `google-ads.yaml` is in the same directory

### Official Server Issues
- **uv Not Found**: Install with `pip install --user uv`
- **Dependencies**: Run `uv pip sync` in the official-google-ads-mcp directory

### General Issues
- **Restart Required**: After switching servers, restart Cursor/VS Code
- **Credentials**: Verify all tokens are current and valid
