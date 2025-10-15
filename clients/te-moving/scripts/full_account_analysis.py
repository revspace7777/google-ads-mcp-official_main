#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Account Data Extraction and Analysis
T&E Moving and Storage LLC - Customer ID: 5840144764

Extracts and saves:
1. All campaigns and campaign types
2. All ad groups
3. All keywords (positive)
4. All negative keywords (campaign, ad group, and shared lists)
5. Search queries from last 14 days with triggered keywords
6. Analysis of unwanted queries
"""

import sys
import io
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from google.ads.googleads.client import GoogleAdsClient

# Customer ID
CUSTOMER_ID = "5840144764"
CLIENT_NAME = "T&E Moving and Storage LLC"

# Unwanted query patterns for moving companies
UNWANTED_PATTERNS = [
    'truck rental', 'rent truck', 'rental truck',
    'uhaul', 'u-haul', 'u haul',
    'budget truck', 'penske', 'enterprise',
    'box truck rental', 'cargo van rental',
    'moving truck rental', 'truck hire',
    'rental', 'hire', 'lease'
]

def save_to_json(data, filename):
    """Save data to JSON file"""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved to: {filepath.name}")
    return filepath

def save_to_csv(data, filename, headers):
    """Save data to CSV file"""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    filepath = data_dir / filename
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"   Saved to: {filepath.name}")
    return filepath

def get_campaigns(client, customer_id):
    """Get all campaigns"""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY campaign.name
    """
    
    print("Fetching campaigns...")
    
    response = ga_service.search(customer_id=customer_id, query=query)
    
    campaigns = []
    for row in response:
        campaigns.append({
            'id': row.campaign.id,
            'name': row.campaign.name,
            'status': row.campaign.status.name,
            'type': row.campaign.advertising_channel_type.name,
            'bidding_strategy': row.campaign.bidding_strategy_type.name,
            'impressions': row.metrics.impressions,
            'clicks': row.metrics.clicks,
            'cost': row.metrics.cost_micros / 1_000_000,
            'conversions': row.metrics.conversions
        })
    
    return campaigns

def get_ad_groups(client, customer_id):
    """Get all ad groups"""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM ad_group
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY campaign.name, ad_group.name
    """
    
    print("Fetching ad groups...")
    
    response = ga_service.search(customer_id=customer_id, query=query)
    
    ad_groups = []
    for row in response:
        ad_groups.append({
            'campaign_id': row.campaign.id,
            'campaign_name': row.campaign.name,
            'ad_group_id': row.ad_group.id,
            'ad_group_name': row.ad_group.name,
            'status': row.ad_group.status.name,
            'type': row.ad_group.type.name,
            'impressions': row.metrics.impressions,
            'clicks': row.metrics.clicks,
            'cost': row.metrics.cost_micros / 1_000_000
        })
    
    return ad_groups

def get_keywords(client, customer_id):
    """Get all positive keywords"""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
            AND ad_group_criterion.status != 'REMOVED'
        ORDER BY campaign.name, ad_group.name, ad_group_criterion.keyword.text
    """
    
    print("Fetching keywords...")
    
    response = ga_service.search(customer_id=customer_id, query=query)
    
    keywords = []
    for row in response:
        keywords.append({
            'campaign_id': row.campaign.id,
            'campaign_name': row.campaign.name,
            'ad_group_id': row.ad_group.id,
            'ad_group_name': row.ad_group.name,
            'keyword': row.ad_group_criterion.keyword.text,
            'match_type': row.ad_group_criterion.keyword.match_type.name,
            'status': row.ad_group_criterion.status.name,
            'quality_score': row.ad_group_criterion.quality_info.quality_score if row.ad_group_criterion.quality_info.quality_score else 'N/A',
            'impressions': row.metrics.impressions,
            'clicks': row.metrics.clicks,
            'cost': row.metrics.cost_micros / 1_000_000,
            'conversions': row.metrics.conversions
        })
    
    return keywords

def get_negative_keywords(client, customer_id):
    """Get all negative keywords"""
    ga_service = client.get_service("GoogleAdsService")
    
    # Campaign-level negative keywords
    campaign_query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign_criterion.keyword.text,
            campaign_criterion.keyword.match_type,
            campaign_criterion.negative
        FROM campaign_criterion
        WHERE campaign_criterion.type = 'KEYWORD'
            AND campaign_criterion.negative = TRUE
        ORDER BY campaign.name, campaign_criterion.keyword.text
    """
    
    # Ad group-level negative keywords
    ad_group_query = """
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.negative
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = 'KEYWORD'
            AND ad_group_criterion.negative = TRUE
        ORDER BY campaign.name, ad_group.name, ad_group_criterion.keyword.text
    """
    
    print("Fetching negative keywords...")
    
    negatives = {
        'campaign': [],
        'ad_group': []
    }
    
    # Campaign negatives
    response = ga_service.search(customer_id=customer_id, query=campaign_query)
    for row in response:
        negatives['campaign'].append({
            'campaign_id': row.campaign.id,
            'campaign_name': row.campaign.name,
            'keyword': row.campaign_criterion.keyword.text,
            'match_type': row.campaign_criterion.keyword.match_type.name,
            'level': 'campaign'
        })
    
    # Ad group negatives
    response = ga_service.search(customer_id=customer_id, query=ad_group_query)
    for row in response:
        negatives['ad_group'].append({
            'campaign_id': row.campaign.id,
            'campaign_name': row.campaign.name,
            'ad_group_id': row.ad_group.id,
            'ad_group_name': row.ad_group.name,
            'keyword': row.ad_group_criterion.keyword.text,
            'match_type': row.ad_group_criterion.keyword.match_type.name,
            'level': 'ad_group'
        })
    
    return negatives

def get_negative_keyword_lists(client, customer_id):
    """Get shared negative keyword lists"""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            shared_set.id,
            shared_set.name,
            shared_set.type,
            shared_criterion.keyword.text,
            shared_criterion.keyword.match_type
        FROM shared_criterion
        WHERE shared_set.type = 'NEGATIVE_KEYWORDS'
        ORDER BY shared_set.name, shared_criterion.keyword.text
    """
    
    print("Fetching shared negative keyword lists...")
    
    lists = defaultdict(list)
    
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        lists[row.shared_set.name].append({
            'list_id': row.shared_set.id,
            'list_name': row.shared_set.name,
            'keyword': row.shared_criterion.keyword.text,
            'match_type': row.shared_criterion.keyword.match_type.name
        })
    
    return dict(lists)

def get_search_queries(client, customer_id):
    """Get search query report"""
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            search_term_view.search_term,
            search_term_view.status,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            segments.keyword.info.text,
            segments.keyword.info.match_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM search_term_view
        WHERE segments.date DURING LAST_14_DAYS
        ORDER BY metrics.impressions DESC
    """
    
    print("Fetching search queries (last 14 days)...")
    
    response = ga_service.search(customer_id=customer_id, query=query)
    
    queries = []
    for row in response:
        queries.append({
            'search_term': row.search_term_view.search_term,
            'status': row.search_term_view.status.name,
            'campaign_id': row.campaign.id,
            'campaign_name': row.campaign.name,
            'ad_group_id': row.ad_group.id,
            'ad_group_name': row.ad_group.name,
            'keyword': row.segments.keyword.info.text if row.segments.keyword.info.text else 'N/A',
            'match_type': row.segments.keyword.info.match_type.name if row.segments.keyword.info.match_type else 'UNKNOWN',
            'impressions': row.metrics.impressions,
            'clicks': row.metrics.clicks,
            'cost': row.metrics.cost_micros / 1_000_000,
            'conversions': row.metrics.conversions
        })
    
    return queries

def analyze_unwanted_queries(queries):
    """Identify unwanted queries"""
    unwanted = []
    
    for query in queries:
        search_term = query['search_term'].lower()
        
        for pattern in UNWANTED_PATTERNS:
            if pattern in search_term:
                unwanted.append({
                    **query,
                    'unwanted_pattern': pattern
                })
                break
    
    return unwanted

def generate_analysis_report(campaigns, ad_groups, keywords, negatives, neg_lists, queries, unwanted):
    """Generate comprehensive analysis report"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = Path(__file__).parent.parent / "reports" / f"full_analysis_{timestamp}.txt"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"{CLIENT_NAME} - COMPLETE ACCOUNT ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Customer ID: {CUSTOMER_ID}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Campaigns: {len(campaigns)}\n")
        f.write(f"Total Ad Groups: {len(ad_groups)}\n")
        f.write(f"Total Keywords: {len(keywords)}\n")
        f.write(f"Campaign-level Negatives: {len(negatives['campaign'])}\n")
        f.write(f"Ad Group-level Negatives: {len(negatives['ad_group'])}\n")
        f.write(f"Shared Negative Lists: {len(neg_lists)}\n")
        f.write(f"Search Queries (14 days): {len(queries)}\n")
        f.write(f"Unwanted Queries: {len(unwanted)}\n\n")
        
        # Campaigns
        f.write("CAMPAIGNS\n")
        f.write("-" * 80 + "\n")
        for camp in campaigns:
            f.write(f"\n{camp['name']}\n")
            f.write(f"  ID: {camp['id']}\n")
            f.write(f"  Type: {camp['type']}\n")
            f.write(f"  Status: {camp['status']}\n")
            f.write(f"  Bidding: {camp['bidding_strategy']}\n")
            f.write(f"  Stats: {camp['impressions']} impr, {camp['clicks']} clicks, ")
            f.write(f"${camp['cost']:.2f}, {camp['conversions']} conv\n")
        
        # Unwanted queries
        if unwanted:
            f.write("\n\nUNWANTED QUERIES (TRUCK RENTAL, UHAUL, ETC.)\n")
            f.write("-" * 80 + "\n")
            
            unwanted_sorted = sorted(unwanted, key=lambda x: x['cost'], reverse=True)
            
            for q in unwanted_sorted:
                f.write(f"\nX '{q['search_term']}'\n")
                f.write(f"  Pattern: {q['unwanted_pattern']}\n")
                f.write(f"  Triggered: {q['keyword']} ({q['match_type']})\n")
                f.write(f"  Campaign: {q['campaign_name']}\n")
                f.write(f"  Ad Group: {q['ad_group_name']}\n")
                f.write(f"  Stats: {q['impressions']} impr, {q['clicks']} clicks, ${q['cost']:.2f}\n")
            
            total_waste = sum(q['cost'] for q in unwanted)
            total_waste_clicks = sum(q['clicks'] for q in unwanted)
            f.write(f"\nTOTAL WASTE: ${total_waste:.2f} ({total_waste_clicks} clicks)\n")
        
        # Recommendations
        f.write("\n\nRECOMMENDED NEGATIVE KEYWORDS\n")
        f.write("-" * 80 + "\n")
        
        unwanted_terms = set()
        for q in unwanted:
            search_term = q['search_term'].lower()
            for pattern in UNWANTED_PATTERNS:
                if pattern in search_term:
                    if pattern not in [neg['keyword'].lower() for neg in negatives['campaign']]:
                        unwanted_terms.add(pattern)
        
        if unwanted_terms:
            f.write("\nAdd these as PHRASE or EXACT match negatives:\n")
            for term in sorted(unwanted_terms):
                f.write(f"  + \"{term}\" (PHRASE)\n")
        else:
            f.write("\nGood coverage on common unwanted terms\n")
    
    print(f"\nAnalysis report saved to: {report_path.name}")
    return report_path

def main():
    print("=" * 80)
    print(f"{CLIENT_NAME} - DATA EXTRACTION & ANALYSIS")
    print("=" * 80)
    print()
    
    # Load credentials
    credentials_path = Path(__file__).parent.parent.parent.parent / "google-ads.yaml"
    
    try:
        client = GoogleAdsClient.load_from_storage(str(credentials_path))
        print(f"Connected to Google Ads API\n")
    except Exception as e:
        print(f"Failed to load credentials: {e}")
        return
    
    # Extract all data
    print("EXTRACTING DATA...")
    print("-" * 80)
    
    campaigns = get_campaigns(client, CUSTOMER_ID)
    save_to_json(campaigns, 'campaigns.json')
    save_to_csv(campaigns, 'campaigns.csv', 
                ['id', 'name', 'status', 'type', 'bidding_strategy', 
                 'impressions', 'clicks', 'cost', 'conversions'])
    
    ad_groups = get_ad_groups(client, CUSTOMER_ID)
    save_to_json(ad_groups, 'ad_groups.json')
    save_to_csv(ad_groups, 'ad_groups.csv',
                ['campaign_id', 'campaign_name', 'ad_group_id', 'ad_group_name',
                 'status', 'type', 'impressions', 'clicks', 'cost'])
    
    keywords = get_keywords(client, CUSTOMER_ID)
    save_to_json(keywords, 'keywords.json')
    save_to_csv(keywords, 'keywords.csv',
                ['campaign_id', 'campaign_name', 'ad_group_id', 'ad_group_name', 'keyword', 'match_type', 
                 'status', 'quality_score', 'impressions', 'clicks', 'cost', 'conversions'])
    
    negatives = get_negative_keywords(client, CUSTOMER_ID)
    all_negatives = negatives['campaign'] + negatives['ad_group']
    save_to_json(negatives, 'negative_keywords.json')
    
    # Fix field names for CSV - ad_group_name won't exist for campaign-level negatives
    for neg in all_negatives:
        if 'ad_group_name' not in neg:
            neg['ad_group_name'] = ''
        if 'ad_group_id' not in neg:
            neg['ad_group_id'] = ''
    
    save_to_csv(all_negatives, 'negative_keywords.csv',
                ['campaign_id', 'campaign_name', 'ad_group_id', 'ad_group_name', 'keyword', 'match_type', 'level'])
    
    neg_lists = get_negative_keyword_lists(client, CUSTOMER_ID)
    save_to_json(neg_lists, 'negative_keyword_lists.json')
    
    # Flatten neg lists for CSV
    neg_list_flat = []
    for list_name, keywords in neg_lists.items():
        for kw in keywords:
            neg_list_flat.append(kw)
    if neg_list_flat:
        save_to_csv(neg_list_flat, 'negative_keyword_lists.csv',
                    ['list_id', 'list_name', 'keyword', 'match_type'])
    
    queries = get_search_queries(client, CUSTOMER_ID)
    save_to_json(queries, 'search_queries.json')
    save_to_csv(queries, 'search_queries.csv',
                ['search_term', 'status', 'campaign_id', 'campaign_name', 'ad_group_id', 'ad_group_name',
                 'keyword', 'match_type', 'impressions', 'clicks', 'cost', 'conversions'])
    
    print()
    print("ANALYZING DATA...")
    print("-" * 80)
    
    unwanted = analyze_unwanted_queries(queries)
    if unwanted:
        save_to_json(unwanted, 'unwanted_queries.json')
        save_to_csv(unwanted, 'unwanted_queries.csv',
                    ['search_term', 'status', 'unwanted_pattern', 'keyword', 'match_type',
                     'campaign_id', 'campaign_name', 'ad_group_id', 'ad_group_name', 
                     'impressions', 'clicks', 'cost', 'conversions'])
    
    # Generate report
    report_path = generate_analysis_report(campaigns, ad_groups, keywords, 
                                           negatives, neg_lists, queries, unwanted)
    
    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nAll data saved to: clients/te-moving/data/")
    print(f"Analysis report: {report_path}")

if __name__ == "__main__":
    main()

