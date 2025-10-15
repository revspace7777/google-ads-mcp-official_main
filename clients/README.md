# Google Ads Clients

This directory contains client-specific configurations and work for all Google Ads accounts managed under Zeroshot Solutions MCC.

## Active Clients

### Ocean Movers Main
- **Customer ID**: `1556744976`
- **Directory**: `./ocean-movers/`
- **Status**: Active - Analyzed
- **Services**: Moving & Storage

### T&E Moving and Storage LLC
- **Customer ID**: `5840144764`
- **Directory**: `./te-moving/`
- **Status**: ✅ Active - Complete data extraction
- **Services**: Moving & Storage

## All Available Clients

| Client Name | Customer ID | Directory | Status |
|-------------|-------------|-----------|--------|
| **T&E Moving and Storage LLC** | `5840144764` | `./te-moving/` | ✅ Complete analysis |
| **B & B Movers (Tarik Bilgin)** | `2111371572` | `./bb-movers/` | Setup pending |
| **678 Rid Junk LLC** | `8640190225` | `./rid-junk/` | Setup pending |
| **Moving & Storage of Jacksonville** | `7283506172` | `./jax-moving/` | Setup pending |
| **Ocean Movers Main** | `1556744976` | `./ocean-movers/` | ✅ Active |
| **ILO's Appliance Repair** | `5727024154` | `./ilos-repair/` | Setup pending |
| **Colonial Trucking Insurance** | `2452257371` | `./colonial-trucking/` | Setup pending |

## Parent MCC
- **Zeroshot Solutions (Manager)**: `4673669771`

## Setup New Client

1. Create directory: `mkdir clients/[client-name]`
2. Copy template: `cp clients/ocean-movers/client-config.yaml clients/[client-name]/`
3. Update customer ID and details
4. Create subdirectories: `campaigns/`, `reports/`, `scripts/`

## Directory Structure

```
clients/
├── README.md                    # This file
├── ocean-movers/               # Ocean Movers Main
│   ├── client-config.yaml
│   ├── README.md
│   ├── campaigns/
│   ├── reports/
│   └── scripts/
└── [other-clients]/            # Add as needed
```

## Quick Reference

### Query a specific client
```python
"List campaigns for customer ID [CUSTOMER_ID]"
```

### Get performance data
```python
"Show performance for [CLIENT_NAME] in the last 30 days"
```

