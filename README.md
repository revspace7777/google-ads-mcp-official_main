# Google Ads MCP Server Project

Multi-server setup for Google Ads API access with MCP (Model Context Protocol) integration.

## Quick Start

### Active MCP Servers
- **CDATA Server** (`GoogleAds`) - Windows executable
- **Official Server** (`GoogleAds-Official`) - Python-based GitHub implementation

### Prerequisites
1. Cursor or VS Code with MCP support
2. Google Ads API credentials configured in `google-ads.yaml`
3. For CDATA: Run PowerShell as Administrator
4. For Official: Python 3.12+ with dependencies installed

## Project Structure

```
google-ads-mcp/
├── clients/                    # Client-specific work
│   ├── ocean-movers/          # Ocean Movers Main (active)
│   └── README.md
├── official-google-ads-mcp/   # Official MCP server
├── archive/                   # Archived setup files
├── google-ads.yaml            # API credentials (DO NOT COMMIT)
├── customer_ids.txt           # Customer ID reference
├── mcp-config.json           # Server switching config
├── switch-mcp-server.py      # Switch between servers
├── test-mcp-servers.py       # Test both servers
└── MCP-SETUP-GUIDE.md        # Detailed setup guide

```

## Usage

### Switch MCP Servers
```powershell
# List available servers
python switch-mcp-server.py list

# Switch to CDATA server
python switch-mcp-server.py switch GoogleAds-CDATA

# Switch to official server
python switch-mcp-server.py switch GoogleAds-Official

# Check current server
python switch-mcp-server.py current
```

### Test Servers
```powershell
python test-mcp-servers.py
```

### Query Google Ads Data
```
"List all campaigns for Ocean Movers Main"
"Show performance metrics for customer 1556744976"
"Get ad groups for campaign [CAMPAIGN_ID]"
```

## Client Accounts

See `clients/README.md` for complete list of managed accounts.

**Active:**
- Ocean Movers Main: `1556744976`

**Available:**
- T&E Moving and Storage: `5840144764`
- B & B Movers: `2111371572`
- 678 Rid Junk: `8640190225`
- Moving & Storage of Jacksonville: `7283506172`
- ILO's Appliance Repair: `5727024154`
- Colonial Trucking Insurance: `2452257371`

## Documentation

- `MCP-SETUP-GUIDE.md` - Complete setup instructions
- `clients/README.md` - Client account reference
- `clients/ocean-movers/README.md` - Ocean Movers specific

## Security

**DO NOT COMMIT:**
- `google-ads.yaml` (contains API credentials)
- Any files in `archive/` directory
- Client-specific data with sensitive information

See `.gitignore` for complete list.

