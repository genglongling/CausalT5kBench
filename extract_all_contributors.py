#!/usr/bin/env python3
"""
Script to extract all contributors from CausalT5K dataset.
Generates contributor table with generation and validation statistics.
"""
import json
import os
from collections import defaultdict
import re

# Name consolidation mapping
name_consolidation = {
    'Matthew Hayes': 'Matthew John Hayes',
    'Matthew John Hayes': 'Matthew John Hayes',
    'Daphne': 'Daphne Barretto',
    'Daphne Barretto': 'Daphne Barretto',
    'Daphne Barretto She/her': 'Daphne Barretto',
    'Matt Wolfman': 'Matthew Wolfman',
    'Matthew Wolfman': 'Matthew Wolfman',
    'ChenyangDai': 'Chenyang Dai',
    'Chenyang Dai': 'Chenyang Dai',
    'Chris Pearce': 'Chris Philip James Pearce',
    'Chris Philip James Pearce': 'Chris Philip James Pearce',
    'Rachael Cooper': 'Rachael Yaran Cooper',
    'Rachael Yaran Cooper': 'Rachael Yaran Cooper',
    'Samantha van Rijs': 'Samantha Afra van Rijs',
    'Samantha Afra van Rijs': 'Samantha Afra van Rijs',
    'Fernando Torres': 'Fernando Torres Navarrete',
    'Fernando Torres Navarrete': 'Fernando Torres Navarrete',
    'Deveen Harischandra': 'Deveen Manitha Harischandra',
    'Deveen Manitha Harischandra': 'Deveen Manitha Harischandra',
    'wutheodo@stanford.edu': 'Theodore Wu',
    'julih@stanford.edu': 'Juli Huang',
    'lgren007@stanford.edu': 'Leiguang Ren',
    'deveen@stanford.edu': 'Deveen Manitha Harischandra',
    'mhayes3@stanford.edu': 'Matthew John Hayes',
}

def consolidate_name(name):
    """Consolidate name variations"""
    if not name:
        return None
    name = str(name).strip()
    # Check exact match first
    if name in name_consolidation:
        return name_consolidation[name]
    # Check if it's a known variation
    for key, value in name_consolidation.items():
        if key.lower() == name.lower() or name.lower() in key.lower() or key.lower() in name.lower():
            return value
    return name

def extract_case_info(case):
    """Extract case information"""
    case_id = case.get('id') or case.get('case_id') or case.get('caseId', '')
    domain = case.get('domain', 'Unknown')
    return case_id, domain

# Collect generation data from validated_dataset(round=1)
gen_data = defaultdict(lambda: {'domains': set(), 'case_ids': []})
val_data = defaultdict(lambda: {'domains': set(), 'case_ids': []})

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
                # Generation data (initial_author)
                author = case.get('initial_author')
                if author:
                    author = consolidate_name(author)
                    case_id, domain = extract_case_info(case)
                    gen_data[author]['domains'].add(domain)
                    if case_id:
                        gen_data[author]['case_ids'].append(case_id)
                
                # Validation data (validator)
                validator = case.get('validator')
                if validator:
                    validator = consolidate_name(validator)
                    case_id, domain = extract_case_info(case)
                    val_data[validator]['domains'].add(domain)
                    if case_id:
                        val_data[validator]['case_ids'].append(case_id)
    except Exception as e:
        continue

# Also check unvalidated_dataset for additional generation data
unvalidated_dir = 'unvalidated_dataset'
for group_dir in os.listdir(unvalidated_dir):
    group_path = os.path.join(unvalidated_dir, group_dir)
    if not os.path.isdir(group_path):
        continue
    for filename in os.listdir(group_path):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(group_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    cases = data
                elif isinstance(data, dict) and 'questions' in data:
                    cases = data['questions']
                else:
                    continue
                
                for case in cases:
                    author = None
                    if 'initial_author' in case:
                        author = consolidate_name(case['initial_author'])
                    elif 'author' in case:
                        author = consolidate_name(case['author'])
                    elif 'annotations' in case and 'author' in case['annotations']:
                        author = consolidate_name(case['annotations']['author'])
                    
                    if author:
                        case_id, domain = extract_case_info(case)
                        gen_data[author]['domains'].add(domain)
                        if case_id:
                            gen_data[author]['case_ids'].append(case_id)
        except Exception as e:
            continue

# Format output
def get_id_range(case_ids):
    """Get case ID range"""
    if not case_ids:
        return "N/A"
    try:
        sorted_ids = sorted(case_ids, key=lambda x: (int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 0, str(x)))
    except:
        sorted_ids = sorted(case_ids)
    if len(sorted_ids) == 1:
        return sorted_ids[0]
    return f"{sorted_ids[0]}-{sorted_ids[-1]}"

# Get all unique contributors, filter out invalid entries
all_contributors = set(gen_data.keys()) | set(val_data.keys())
all_contributors = sorted([c for c in all_contributors if c and c != 'N/A' and c.strip() and c not in ['LLM', 'NOT ASSIGNED', '4', 'A2']])

# Print results in table format
print("| Name | Major | Level | Generation Domains | Generation Cases Number | Generation Cases ID | Validation Domains | Validation Cases Number | Validation Cases ID |")
print("|------|-------|-------|-------------------|----------------------|-------------------|------------------|----------------------|-------------------|")

for contributor in all_contributors:
    gen_info = gen_data[contributor]
    val_info = val_data[contributor]
    
    # Generation data
    gen_domains = sorted([d for d in gen_info['domains'] if d != 'Unknown'])[:8]
    gen_domains_str = ', '.join(gen_domains) if gen_domains else '-' if not gen_info['domains'] else 'Various'
    gen_count = len(gen_info['case_ids'])
    gen_id_range = get_id_range(gen_info['case_ids'])
    
    # Validation data
    val_domains = sorted([d for d in val_info['domains'] if d != 'Unknown'])[:8]
    val_domains_str = ', '.join(val_domains) if val_domains else '-' if not val_info['domains'] else 'Various'
    val_count = len(val_info['case_ids'])
    val_id_range = get_id_range(val_info['case_ids'])
    
    # Format domains for markdown (limit length)
    if len(gen_domains_str) > 60:
        gen_domains_str = ', '.join(gen_domains[:5]) + '...'
    if len(val_domains_str) > 60:
        val_domains_str = ', '.join(val_domains[:5]) + '...'
    
    print(f"| {contributor} | [To be filled] | [To be filled] | {gen_domains_str} | {gen_count} | {gen_id_range} | {val_domains_str} | {val_count} | {val_id_range} |")

