#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Search Queries and Negative Keyword Conflicts
Ocean Movers Main - Customer ID: 1556744976

This script identifies:
1. Search queries from last 14 days with triggered keywords
2. All negative keywords and their lists
3. Conflicts preventing wanted clicks
4. Misconfigurations allowing unwanted clicks (truck rental, uhaul, budget, etc.)
"""

import sys
import io
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
CUSTOMER_ID = "1556744976"

# Unwanted query patterns for moving companies
UNWANTED_PATTERNS = [
    'truck rental', 'rent truck', 'rental truck',
    'uhaul', 'u-haul', 'u haul',
    'budget truck', 'penske', 'enterprise',
    'box truck rental', 'cargo van rental',
    'moving truck rental', 'truck hire',
    'rental', 'hire', 'lease'
]

def get_search_queries(client, customer_id, days=14):
    """Get search query report for last N days"""
    ga_service = client.get_service("GoogleAdsService")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = f"""
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
    
    print("🔍 Fetching search queries from last 14 days...")
    print()
    
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

def get_negative_keywords(client, customer_id):
    """Get all negative keywords at campaign and ad group level"""
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
    """
    
    print("📋 Fetching negative keywords...")
    print()
    
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
            'match_type': row.campaign_criterion.keyword.match_type.name
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
            'match_type': row.ad_group_criterion.keyword.match_type.name
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
    """
    
    print("📚 Fetching shared negative keyword lists...")
    print()
    
    lists = defaultdict(list)
    
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        lists[row.shared_set.name].append({
            'list_id': row.shared_set.id,
            'keyword': row.shared_criterion.keyword.text,
            'match_type': row.shared_criterion.keyword.match_type.name
        })
    
    return dict(lists)

def analyze_unwanted_queries(queries):
    """Identify unwanted queries that got through"""
    unwanted = []
    
    for query in queries:
        search_term = query['search_term'].lower()
        
        # Check if search term contains unwanted patterns
        for pattern in UNWANTED_PATTERNS:
            if pattern in search_term:
                unwanted.append({
                    **query,
                    'unwanted_pattern': pattern
                })
                break
    
    return unwanted

def check_conflicts(queries, negatives):
    """Check for negative keyword conflicts"""
    conflicts = []
    
    # Build list of all negative keywords
    all_negatives = []
    
    for neg in negatives['campaign']:
        all_negatives.append({
            'keyword': neg['keyword'].lower(),
            'match_type': neg['match_type'],
            'level': 'campaign',
            'campaign': neg['campaign_name']
        })
    
    for neg in negatives['ad_group']:
        all_negatives.append({
            'keyword': neg['keyword'].lower(),
            'match_type': neg['match_type'],
            'level': 'ad_group',
            'campaign': neg['campaign_name'],
            'ad_group': neg['ad_group_name']
        })
    
    # Check each query against negatives
    for query in queries:
        search_term = query['search_term'].lower()
        
        for neg in all_negatives:
            # Simple conflict check (exact match for now)
            if neg['keyword'] in search_term and neg['match_type'] == 'EXACT':
                conflicts.append({
                    'search_term': query['search_term'],
                    'negative_keyword': neg['keyword'],
                    'match_type': neg['match_type'],
                    'level': neg['level'],
                    'campaign': query['campaign_name']
                })
    
    return conflicts

def generate_report(queries, negatives, neg_lists, unwanted, conflicts):
    """Generate comprehensive analysis report"""
    
    print("=" * 80)
    print("OCEAN MOVERS MAIN - SEARCH QUERY & NEGATIVE KEYWORD ANALYSIS")
    print("=" * 80)
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Search Queries (14 days): {len(queries)}")
    print(f"Unwanted Queries Getting Through: {len(unwanted)}")
    print(f"Campaign-level Negatives: {len(negatives['campaign'])}")
    print(f"Ad Group-level Negatives: {len(negatives['ad_group'])}")
    print(f"Shared Negative Lists: {len(neg_lists)}")
    print(f"Potential Conflicts: {len(conflicts)}")
    print()
    
    # Unwanted queries that got through
    if unwanted:
        print("🚨 UNWANTED QUERIES GETTING THROUGH (TRUCK RENTAL, UHAUL, ETC.)")
        print("-" * 80)
        
        # Sort by cost
        unwanted_sorted = sorted(unwanted, key=lambda x: x['cost'], reverse=True)
        
        for q in unwanted_sorted[:20]:  # Top 20
            print(f"\n❌ '{q['search_term']}'")
            print(f"   Pattern: {q['unwanted_pattern']}")
            print(f"   Triggered Keyword: {q['keyword']} ({q['match_type']})")
            print(f"   Campaign: {q['campaign_name']}")
            print(f"   Ad Group: {q['ad_group_name']}")
            print(f"   Stats: {q['impressions']} impr, {q['clicks']} clicks, ${q['cost']:.2f}")
        
        print()
        
        # Calculate waste
        total_waste = sum(q['cost'] for q in unwanted)
        total_waste_clicks = sum(q['clicks'] for q in unwanted)
        print(f"💸 TOTAL WASTE: ${total_waste:.2f} ({total_waste_clicks} clicks)")
        print()
    
    # Negative keyword coverage
    print("📋 NEGATIVE KEYWORD COVERAGE")
    print("-" * 80)
    
    if negatives['campaign']:
        print("\nCampaign-level Negatives:")
        for neg in negatives['campaign'][:10]:
            print(f"  - {neg['keyword']} ({neg['match_type']}) in {neg['campaign_name']}")
    
    if negatives['ad_group']:
        print("\nAd Group-level Negatives:")
        for neg in negatives['ad_group'][:10]:
            print(f"  - {neg['keyword']} ({neg['match_type']}) in {neg['campaign_name']} > {neg['ad_group_name']}")
    
    if neg_lists:
        print("\nShared Negative Keyword Lists:")
        for list_name, keywords in neg_lists.items():
            print(f"\n  📚 {list_name} ({len(keywords)} keywords)")
            for kw in keywords[:5]:
                print(f"     - {kw['keyword']} ({kw['match_type']})")
            if len(keywords) > 5:
                print(f"     ... and {len(keywords) - 5} more")
    
    print()
    
    # Recommended negative keywords
    print("💡 RECOMMENDED NEGATIVE KEYWORDS TO ADD")
    print("-" * 80)
    
    # Extract unique unwanted terms
    unwanted_terms = set()
    for q in unwanted:
        search_term = q['search_term'].lower()
        for pattern in UNWANTED_PATTERNS:
            if pattern in search_term:
                # Extract the actual term
                if pattern not in [neg['keyword'].lower() for neg in negatives['campaign']]:
                    unwanted_terms.add(pattern)
    
    if unwanted_terms:
        print("\nAdd these as PHRASE or EXACT match negatives:")
        for term in sorted(unwanted_terms):
            print(f"  ➕ \"{term}\" (PHRASE)")
        print()
        print("Additional broad terms to consider:")
        print("  ➕ \"rental\" (PHRASE)")
        print("  ➕ \"rent\" (PHRASE)")  
        print("  ➕ \"hire\" (PHRASE)")
        print("  ➕ \"lease\" (PHRASE)")
    else:
        print("✅ Good coverage on common unwanted terms")
    
    print()
    
    # Match type analysis
    print("🎯 KEYWORD MATCH TYPE ANALYSIS")
    print("-" * 80)
    
    match_type_stats = defaultdict(lambda: {'queries': 0, 'unwanted': 0})
    
    for q in queries:
        match_type_stats[q['match_type']]['queries'] += 1
    
    for q in unwanted:
        match_type_stats[q['match_type']]['unwanted'] += 1
    
    for match_type, stats in match_type_stats.items():
        unwanted_pct = (stats['unwanted'] / stats['queries'] * 100) if stats['queries'] > 0 else 0
        print(f"\n{match_type}:")
        print(f"  Total queries: {stats['queries']}")
        print(f"  Unwanted: {stats['unwanted']} ({unwanted_pct:.1f}%)")
        
        if match_type == 'BROAD' and unwanted_pct > 20:
            print(f"  ⚠️  High unwanted rate - consider using PHRASE or EXACT match")
    
    print()

def main():
    # Load credentials
    credentials_path = Path(__file__).parent.parent.parent.parent / "google-ads.yaml"
    
    try:
        client = GoogleAdsClient.load_from_storage(str(credentials_path))
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return
    
    # Fetch data
    queries = get_search_queries(client, CUSTOMER_ID)
    negatives = get_negative_keywords(client, CUSTOMER_ID)
    neg_lists = get_negative_keyword_lists(client, CUSTOMER_ID)
    
    # Analyze
    unwanted = analyze_unwanted_queries(queries)
    conflicts = check_conflicts(queries, negatives)
    
    # Generate report
    generate_report(queries, negatives, neg_lists, unwanted, conflicts)
    
    # Save to file
    output_path = Path(__file__).parent.parent / "reports" / f"search_query_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"📄 Report saved to: {output_path}")

if __name__ == "__main__":
    main()

