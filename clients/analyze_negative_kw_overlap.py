#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Negative Keyword Overlap & Divergence
Between Ocean Movers Main and T&E Moving & Storage

Analyzes:
1. Shared negative keywords between both accounts
2. Unique negatives per account
3. Impact of consolidating to unified lists
4. Recommended list structure for multi-account management
"""

import sys
import io
import json
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Client data paths
OCEAN_MOVERS_DATA = Path(__file__).parent / "ocean-movers" / "data"
TE_MOVING_DATA = Path(__file__).parent / "te-moving" / "data"

def load_negatives(client_path, client_name):
    """Load all negative keywords for a client"""
    negatives_file = client_path / "negative_keywords.json"
    lists_file = client_path / "negative_keyword_lists.json"
    
    negatives = {
        'campaign': [],
        'ad_group': [],
        'shared_lists': {}
    }
    
    # Load campaign/ad group negatives
    if negatives_file.exists():
        with open(negatives_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            negatives['campaign'] = data.get('campaign', [])
            negatives['ad_group'] = data.get('ad_group', [])
    
    # Load shared lists
    if lists_file.exists():
        with open(lists_file, 'r', encoding='utf-8') as f:
            negatives['shared_lists'] = json.load(f)
    
    print(f"\n{client_name}:")
    print(f"  Campaign-level negatives: {len(negatives['campaign'])}")
    print(f"  Ad group-level negatives: {len(negatives['ad_group'])}")
    print(f"  Shared lists: {len(negatives['shared_lists'])}")
    
    return negatives

def normalize_keyword(keyword, match_type):
    """Normalize keyword for comparison"""
    # Convert to lowercase and create a comparable key
    return (keyword.lower().strip(), match_type)

def extract_all_negatives(negatives_data):
    """Extract all unique negatives regardless of level"""
    all_negatives = set()
    
    # Campaign level
    for neg in negatives_data['campaign']:
        all_negatives.add(normalize_keyword(neg['keyword'], neg['match_type']))
    
    # Ad group level
    for neg in negatives_data['ad_group']:
        all_negatives.add(normalize_keyword(neg['keyword'], neg['match_type']))
    
    # Shared lists
    for list_name, keywords in negatives_data['shared_lists'].items():
        for kw in keywords:
            all_negatives.add(normalize_keyword(kw['keyword'], kw['match_type']))
    
    return all_negatives

def categorize_negatives(keyword):
    """Categorize negative keywords into logical groups"""
    keyword_lower = keyword.lower()
    
    # Rental/DIY related
    if any(term in keyword_lower for term in ['rental', 'rent', 'hire', 'lease', 'uhaul', 'u-haul', 'penske', 'budget', 'enterprise']):
        return 'rental_diy'
    
    # Job/employment
    if any(term in keyword_lower for term in ['job', 'career', 'hiring', 'employment', 'salary', 'wage']):
        return 'jobs_employment'
    
    # Real estate
    if any(term in keyword_lower for term in ['apartment', 'house', 'home', 'condo', 'for rent', 'for sale', 'realtor', 'real estate']):
        return 'real_estate'
    
    # DIY/How-to
    if any(term in keyword_lower for term in ['how to', 'how do', 'diy', 'tutorial', 'guide']):
        return 'diy_howto'
    
    # Junk/items
    if any(term in keyword_lower for term in ['junk', 'scrap', 'donation', 'sell', 'buy', 'dealer']):
        return 'junk_items'
    
    # Marine/ocean related (irrelevant for moving)
    if any(term in keyword_lower for term in ['ocean', 'sea', 'boat', 'yacht', 'ship', 'marine', 'cruise']):
        return 'marine_ocean'
    
    # Geographic (specific locations to exclude)
    if any(term in keyword_lower for term in ['puerto rico', 'hawaii', 'alaska', 'international']):
        return 'geographic_exclusions'
    
    # Other services
    if any(term in keyword_lower for term in ['shipping', 'freight', 'cargo', 'logistics', 'warehouse']):
        return 'other_services'
    
    return 'other'

def analyze_overlap(ocean_negatives, te_negatives):
    """Analyze overlap and divergence"""
    
    ocean_set = extract_all_negatives(ocean_negatives)
    te_set = extract_all_negatives(te_negatives)
    
    # Calculate overlap
    shared = ocean_set & te_set
    ocean_only = ocean_set - te_set
    te_only = te_set - ocean_set
    
    print("\n" + "=" * 80)
    print("NEGATIVE KEYWORD OVERLAP ANALYSIS")
    print("=" * 80)
    
    print(f"\nOcean Movers total unique negatives: {len(ocean_set)}")
    print(f"T&E Moving total unique negatives: {len(te_set)}")
    print(f"\nShared negatives: {len(shared)} ({len(shared)/len(ocean_set)*100:.1f}% of Ocean, {len(shared)/len(te_set)*100:.1f}% of T&E)")
    print(f"Ocean-only negatives: {len(ocean_only)}")
    print(f"T&E-only negatives: {len(te_only)}")
    
    # Categorize shared negatives
    shared_categories = defaultdict(list)
    for kw, match_type in shared:
        category = categorize_negatives(kw)
        shared_categories[category].append((kw, match_type))
    
    print("\n" + "-" * 80)
    print("SHARED NEGATIVES BY CATEGORY")
    print("-" * 80)
    
    for category, keywords in sorted(shared_categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{category.upper().replace('_', ' ')} ({len(keywords)} keywords):")
        for kw, match_type in sorted(keywords)[:10]:  # Show top 10
            print(f"  - \"{kw}\" ({match_type})")
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more")
    
    # Categorize unique negatives
    ocean_categories = defaultdict(list)
    for kw, match_type in ocean_only:
        category = categorize_negatives(kw)
        ocean_categories[category].append((kw, match_type))
    
    te_categories = defaultdict(list)
    for kw, match_type in te_only:
        category = categorize_negatives(kw)
        te_categories[category].append((kw, match_type))
    
    print("\n" + "-" * 80)
    print("OCEAN MOVERS UNIQUE NEGATIVES")
    print("-" * 80)
    
    for category, keywords in sorted(ocean_categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{category.upper().replace('_', ' ')} ({len(keywords)} keywords):")
        for kw, match_type in sorted(keywords)[:5]:
            print(f"  - \"{kw}\" ({match_type})")
        if len(keywords) > 5:
            print(f"  ... and {len(keywords) - 5} more")
    
    print("\n" + "-" * 80)
    print("T&E MOVING UNIQUE NEGATIVES")
    print("-" * 80)
    
    for category, keywords in sorted(te_categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{category.upper().replace('_', ' ')} ({len(keywords)} keywords):")
        for kw, match_type in sorted(keywords)[:5]:
            print(f"  - \"{kw}\" ({match_type})")
        if len(keywords) > 5:
            print(f"  ... and {len(keywords) - 5} more")
    
    return {
        'shared': shared,
        'ocean_only': ocean_only,
        'te_only': te_only,
        'shared_categories': shared_categories,
        'ocean_categories': ocean_categories,
        'te_categories': te_categories
    }

def recommend_unified_structure(analysis):
    """Recommend unified negative keyword list structure"""
    
    print("\n" + "=" * 80)
    print("RECOMMENDED UNIFIED NEGATIVE KEYWORD STRUCTURE")
    print("=" * 80)
    
    # Combine all negatives
    all_negatives = analysis['shared'] | analysis['ocean_only'] | analysis['te_only']
    
    # Categorize everything
    unified_categories = defaultdict(list)
    for kw, match_type in all_negatives:
        category = categorize_negatives(kw)
        unified_categories[category].append((kw, match_type))
    
    print("\nProposed Shared Negative Keyword Lists:")
    print("-" * 80)
    
    list_structure = []
    
    for category, keywords in sorted(unified_categories.items(), key=lambda x: len(x[1]), reverse=True):
        list_name = f"Moving_Co_{category.replace('_', '_').title()}"
        
        print(f"\n📚 LIST: {list_name}")
        print(f"   Keywords: {len(keywords)}")
        print(f"   Purpose: Exclude {category.replace('_', ' ')} related queries")
        
        # Show examples
        phrase_kws = [kw for kw, mt in keywords if mt == 'PHRASE']
        exact_kws = [kw for kw, mt in keywords if mt == 'EXACT']
        broad_kws = [kw for kw, mt in keywords if mt == 'BROAD']
        
        if phrase_kws:
            print(f"   PHRASE ({len(phrase_kws)}): {', '.join([kw for kw in sorted(phrase_kws)[:3]])}")
        if exact_kws:
            print(f"   EXACT ({len(exact_kws)}): {', '.join([kw for kw in sorted(exact_kws)[:3]])}")
        if broad_kws:
            print(f"   BROAD ({len(broad_kws)}): {', '.join([kw for kw in sorted(broad_kws)[:3]])}")
        
        list_structure.append({
            'name': list_name,
            'category': category,
            'keywords': keywords,
            'count': len(keywords)
        })
    
    # Impact analysis
    print("\n" + "=" * 80)
    print("CONSOLIDATION IMPACT ANALYSIS")
    print("=" * 80)
    
    print("\n✅ BENEFITS OF UNIFIED LISTS:")
    print("-" * 80)
    print("1. Single source of truth - no divergence over time")
    print("2. Easier management - update once, applies everywhere")
    print("3. Consistency across all moving company clients")
    print("4. Better coverage - combines best negatives from both accounts")
    print(f"5. Total coverage: {len(all_negatives)} unique negatives")
    
    print("\n⚠️  CONSIDERATIONS:")
    print("-" * 80)
    print("1. Location-specific negatives may not apply to all clients")
    print("2. Some unique service offerings may need custom negatives")
    print("3. Brand-specific negatives should remain account-level")
    
    print("\n💡 RECOMMENDED APPROACH:")
    print("-" * 80)
    print("1. CORE SHARED LISTS (apply to all moving company accounts):")
    for lst in list_structure[:5]:  # Top 5 categories
        print(f"   - {lst['name']} ({lst['count']} keywords)")
    
    print("\n2. ACCOUNT-LEVEL NEGATIVES (keep unique to each client):")
    print("   Ocean Movers:")
    for category, keywords in sorted(analysis['ocean_categories'].items(), key=lambda x: len(x[1]), reverse=True)[:3]:
        if category not in ['rental_diy', 'jobs_employment', 'diy_howto']:  # Skip common ones
            print(f"   - {category.replace('_', ' ').title()}: {len(keywords)} keywords")
    
    print("\n   T&E Moving:")
    for category, keywords in sorted(analysis['te_categories'].items(), key=lambda x: len(x[1]), reverse=True)[:3]:
        if category not in ['rental_diy', 'jobs_employment', 'diy_howto']:
            print(f"   - {category.replace('_', ' ').title()}: {len(keywords)} keywords")
    
    print("\n3. MATCH TYPE RECOMMENDATIONS:")
    print("   - Use PHRASE match for most negatives (blocks variations)")
    print("   - Use EXACT match for specific blocking (e.g., competitor names)")
    print("   - Use BROAD match sparingly (can block too much)")
    
    # Save unified lists to file
    output_file = Path(__file__).parent / "unified_negative_keywords.json"
    output_data = {
        'lists': [
            {
                'name': lst['name'],
                'category': lst['category'],
                'keywords': [{'keyword': kw, 'match_type': mt} for kw, mt in lst['keywords']],
                'count': lst['count']
            }
            for lst in list_structure
        ],
        'total_keywords': len(all_negatives),
        'shared_between_clients': len(analysis['shared']),
        'coverage_improvement': {
            'ocean_movers_adds': len(analysis['te_only']),
            'te_moving_adds': len(analysis['ocean_only'])
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Unified negative keyword lists saved to: {output_file.name}")
    
    return list_structure

def main():
    print("=" * 80)
    print("NEGATIVE KEYWORD OVERLAP & CONSOLIDATION ANALYSIS")
    print("Ocean Movers Main vs T&E Moving & Storage LLC")
    print("=" * 80)
    
    # Load data
    print("\nLoading negative keywords...")
    ocean_negatives = load_negatives(OCEAN_MOVERS_DATA, "Ocean Movers Main")
    te_negatives = load_negatives(TE_MOVING_DATA, "T&E Moving & Storage")
    
    # Analyze overlap
    analysis = analyze_overlap(ocean_negatives, te_negatives)
    
    # Recommend structure
    unified_lists = recommend_unified_structure(analysis)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review unified_negative_keywords.json")
    print("2. Create shared lists in Google Ads")
    print("3. Apply lists to both accounts")
    print("4. Remove redundant account-level negatives")
    print("5. Monitor for any missed impressions/clicks")

if __name__ == "__main__":
    main()

