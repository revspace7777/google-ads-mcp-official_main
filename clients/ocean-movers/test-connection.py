#!/usr/bin/env python3
"""
Test connection to Ocean Movers Main Google Ads account
Customer ID: 1556744976
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import from root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_ocean_movers_connection():
    """Test connection to Ocean Movers Main account"""
    
    print("🧪 Ocean Movers Main - Connection Test")
    print("=" * 50)
    
    # Client details
    client_name = "Ocean Movers Main"
    customer_id = "1556744976"
    customer_id_formatted = "155-674-4976"
    
    print(f"Client: {client_name}")
    print(f"Customer ID: {customer_id} ({customer_id_formatted})")
    print()
    
    # Check if credentials file exists
    credentials_path = Path(__file__).parent.parent.parent / "google-ads.yaml"
    
    if not credentials_path.exists():
        print(f"❌ Credentials file not found: {credentials_path}")
        return False
    
    print(f"✅ Credentials file found: {credentials_path}")
    
    # Try to import Google Ads library
    try:
        from google.ads.googleads.client import GoogleAdsClient
        print("✅ Google Ads library imported successfully")
    except ImportError as e:
        print(f"❌ Google Ads library not found: {e}")
        print("   Install with: pip install google-ads")
        return False
    
    # Try to create client
    try:
        client = GoogleAdsClient.load_from_storage(str(credentials_path))
        print("✅ Google Ads client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # Try to query campaigns
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status
            FROM campaign
            LIMIT 5
        """
        
        print()
        print(f"🔍 Querying campaigns for customer {customer_id}...")
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaigns = list(response)
        
        if campaigns:
            print(f"✅ Successfully retrieved {len(campaigns)} campaign(s):")
            print()
            for row in campaigns:
                campaign = row.campaign
                print(f"  • {campaign.name}")
                print(f"    ID: {campaign.id}")
                print(f"    Status: {campaign.status.name}")
                print()
        else:
            print("⚠️  No campaigns found (account may be empty)")
        
        return True
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ocean_movers_connection()
    
    print()
    print("=" * 50)
    if success:
        print("✅ Connection test PASSED")
        print()
        print("Ocean Movers Main is ready to use!")
    else:
        print("❌ Connection test FAILED")
        print()
        print("Please check the errors above and verify:")
        print("1. google-ads.yaml contains valid credentials")
        print("2. Customer ID 1556744976 is correct")
        print("3. Google Ads API dependencies are installed")
    
    sys.exit(0 if success else 1)

