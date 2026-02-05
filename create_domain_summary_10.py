#!/usr/bin/env python3
"""
Script to create a 10-domain summary table with Pearl level distributions.
Groups all domains into 10 main categories.
"""
import json
import os
from collections import defaultdict

# Domain mapping to 10 main categories
domain_mapping = {
    # Daily Life
    'Daily Life': 'Daily Life',
    
    # History
    'History': 'History',
    'D2': 'History',
    
    # Markets
    'Markets': 'Markets & Finance',
    'Finance': 'Markets & Finance',
    'Business': 'Markets & Finance',
    
    # Economics (separate category)
    'Economics': 'Economics',
    
    # Medicine
    'Medicine': 'Medicine & Health',
    'Health': 'Medicine & Health',
    'Healthcare': 'Medicine & Health',
    'Public Health': 'Medicine & Health',
    'Epidemiology': 'Medicine & Health',
    
    # Economics (separate from Markets)
    # Already mapped above
    
    # Environment
    'Environment': 'Environment & Climate',
    'Environmental Science': 'Environment & Climate',
    'Climate': 'Environment & Climate',
    'Climate Science': 'Environment & Climate',
    
    # Law & Ethics
    'Law & Ethics': 'Law & Ethics',
    'Law': 'Law & Ethics',
    'Legal': 'Law & Ethics',
    'Ethics': 'Law & Ethics',
    
    # AI & Technology
    'AI & Tech': 'AI & Technology',
    'D8 - AI Safety & Alignment': 'AI & Technology',
    'Technology': 'AI & Technology',
    'Computer Science': 'AI & Technology',
    
    # Sports
    'Sports': 'Sports & Performance',
    'D9': 'Sports & Performance',
    
    # Social Science
    'Social Science': 'Social Science',
    'D10 (Social Science)': 'Social Science',
    'Psychology': 'Social Science',
    'Public Policy': 'Social Science',
    'Criminal Justice': 'Social Science',
    'Employment': 'Social Science',
    'Education': 'Social Science',
}

def map_to_main_domain(domain):
    """Map a domain to one of the 10 main categories"""
    if not domain or domain == 'Unknown':
        return None
    return domain_mapping.get(domain, None)

# Collect domain data with Pearl levels
domain_data = defaultdict(lambda: {
    'L1': 0,
    'L2': 0,
    'L3': 0,
    'total': 0
})

validated_dir = 'validated_dataset(round=1)'
for filename in os.listdir(validated_dir):
    if not filename.endswith('.json'):
        continue
    filepath = os.path.join(validated_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cases = json.load(f)
            if not isinstance(cases, list):
                continue
            
            for case in cases:
                domain = case.get('domain', 'Unknown')
                pearl_level = case.get('pearl_level', '')
                
                main_domain = map_to_main_domain(domain)
                if main_domain:
                    domain_data[main_domain]['total'] += 1
                    if pearl_level == 'L1':
                        domain_data[main_domain]['L1'] += 1
                    elif pearl_level == 'L2':
                        domain_data[main_domain]['L2'] += 1
                    elif pearl_level == 'L3':
                        domain_data[main_domain]['L3'] += 1
    except Exception as e:
        continue

# Define the 10 main domains in order
main_domains = [
    'Daily Life',
    'History',
    'Markets & Finance',
    'Medicine & Health',
    'Economics',
    'Environment & Climate',
    'Law & Ethics',
    'AI & Technology',
    'Sports & Performance',
    'Social Science'
]

# Calculate totals
grand_total = {'L1': 0, 'L2': 0, 'L3': 0, 'total': 0}

# Print table
print("| # | Domain | Pearl Levels | Cases |")
print("|---|--------|--------------|-------|")

for idx, domain in enumerate(main_domains, 1):
    data = domain_data[domain]
    grand_total['L1'] += data['L1']
    grand_total['L2'] += data['L2']
    grand_total['L3'] += data['L3']
    grand_total['total'] += data['total']
    
    pearl_str = f"L1: {data['L1']}, L2: {data['L2']}, L3: {data['L3']}"
    print(f"| {idx} | {domain} | {pearl_str} | {data['total']} |")

print(f"| **Grand Total** | | **L1: {grand_total['L1']}, L2: {grand_total['L2']}, L3: {grand_total['L3']}** | **{grand_total['total']}** |")

