#!/usr/bin/env python3
"""
Script to create a domain summary table organized by D1-D10 domains.
Uses domain_id field from the dataset to map cases to D1-D10.
"""
import json
import os
from collections import defaultdict

# Collect domain data with Pearl levels, organized by domain_id (D1-D10)
domain_data = defaultdict(lambda: {
    'L1': 0,
    'L2': 0,
    'L3': 0,
    'total': 0,
    'domain_name': set()
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
                # Try to get domain_id first, then fall back to domain name mapping
                domain_id = case.get('domain_id', '')
                domain = case.get('domain', '')
                domain_name_field = case.get('domain_name', '')
                pearl_level = case.get('pearl_level', '')
                
                # Determine D1-D10 from domain_id or domain name
                d_code = None
                if domain_id and domain_id.startswith('D') and len(domain_id) <= 3:
                    d_code = domain_id
                elif domain_name_field:
                    # Map domain_name to D codes
                    domain_name_lower = domain_name_field.lower()
                    if 'daily life' in domain_name_lower:
                        d_code = 'D1'
                    elif 'history' in domain_name_lower or domain == 'History' or domain == 'D2':
                        d_code = 'D2'
                    elif 'markets' in domain_name_lower or domain == 'Markets':
                        d_code = 'D3'
                    elif 'medicine' in domain_name_lower or 'health' in domain_name_lower or domain in ['Medicine', 'Health', 'Healthcare']:
                        d_code = 'D4'
                    elif 'economics' in domain_name_lower or domain == 'Economics':
                        d_code = 'D5'
                    elif 'environment' in domain_name_lower or 'climate' in domain_name_lower or domain in ['Environment', 'Climate']:
                        d_code = 'D6'
                    elif 'law' in domain_name_lower or 'ethics' in domain_name_lower or domain in ['Law & Ethics', 'Law', 'Ethics']:
                        d_code = 'D7'
                    elif 'ai' in domain_name_lower or 'tech' in domain_name_lower or domain in ['AI & Tech', 'D8 - AI Safety & Alignment', 'Technology', 'Computer Science']:
                        d_code = 'D8'
                    elif 'sports' in domain_name_lower or domain in ['Sports', 'D9']:
                        d_code = 'D9'
                    elif 'social science' in domain_name_lower or domain in ['Social Science', 'D10 (Social Science)', 'Psychology', 'Public Policy']:
                        d_code = 'D10'
                
                # Fallback: map by domain name if domain_id not found
                if not d_code:
                    if domain == 'Daily Life' or 'daily' in domain.lower():
                        d_code = 'D1'
                    elif domain == 'History' or domain == 'D2':
                        d_code = 'D2'
                    elif domain == 'Markets' or domain == 'Finance' or domain == 'Business':
                        d_code = 'D3'
                    elif domain in ['Medicine', 'Health', 'Healthcare', 'Public Health', 'Epidemiology']:
                        d_code = 'D4'
                    elif domain == 'Economics':
                        d_code = 'D5'
                    elif domain in ['Environment', 'Environmental Science', 'Climate', 'Climate Science']:
                        d_code = 'D6'
                    elif domain in ['Law & Ethics', 'Law', 'Legal', 'Ethics']:
                        d_code = 'D7'
                    elif domain in ['AI & Tech', 'D8 - AI Safety & Alignment', 'Technology', 'Computer Science']:
                        d_code = 'D8'
                    elif domain in ['Sports', 'D9']:
                        d_code = 'D9'
                    elif domain in ['Social Science', 'D10 (Social Science)', 'Psychology', 'Public Policy', 'Criminal Justice', 'Education']:
                        d_code = 'D10'
                
                if d_code:
                    domain_data[d_code]['total'] += 1
                    if pearl_level == 'L1':
                        domain_data[d_code]['L1'] += 1
                    elif pearl_level == 'L2':
                        domain_data[d_code]['L2'] += 1
                    elif pearl_level == 'L3':
                        domain_data[d_code]['L3'] += 1
                    if domain_name_field:
                        domain_data[d_code]['domain_name'].add(domain_name_field)
                    elif domain:
                        domain_data[d_code]['domain_name'].add(domain)
    except Exception as e:
        continue

# Define D1-D10 with their names
d_domains = {
    'D1': 'Daily Life',
    'D2': 'History',
    'D3': 'Markets & Finance',
    'D4': 'Medicine & Health',
    'D5': 'Economics',
    'D6': 'Environment & Climate',
    'D7': 'Law & Ethics',
    'D8': 'AI & Technology',
    'D9': 'Sports & Performance',
    'D10': 'Social Science'
}

# Calculate totals
grand_total = {'L1': 0, 'L2': 0, 'L3': 0, 'total': 0}

# Print table
print("| # | Domain | Pearl Levels | Cases |")
print("|---|--------|--------------|-------|")

for idx, (d_code, domain_name) in enumerate(d_domains.items(), 1):
    data = domain_data[d_code]
    grand_total['L1'] += data['L1']
    grand_total['L2'] += data['L2']
    grand_total['L3'] += data['L3']
    grand_total['total'] += data['total']
    
    pearl_str = f"L1: {data['L1']}, L2: {data['L2']}, L3: {data['L3']}"
    print(f"| {idx} | {domain_name} | {pearl_str} | {data['total']} |")

print(f"| **Grand Total** | | **L1: {grand_total['L1']}, L2: {grand_total['L2']}, L3: {grand_total['L3']}** | **{grand_total['total']}** |")

