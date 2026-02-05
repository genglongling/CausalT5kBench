#!/usr/bin/env python3
"""
Script to generate domain summary table for CausalT5K dataset.
Summarizes dataset quality scores organized by domain.
"""
import json
import os
import csv
from collections import defaultdict
import re

# Read CSV files
assignment2_data = {}
assignment2_llm_data = {}

# Read assignment2.csv
with open('validated_dataset(round=1)/assignment2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name'].strip()
        assignment2_data[name] = {
            'final_score': float(row['final_score']) if row['final_score'] else 0.0,
            'validatees': row['validatees'].strip() if row['validatees'] else '',
            'validatee_score': float(row['validatee_score']) if row['validatee_score'] else None,
            'score_from_other': float(row['score_from_other']) if row.get('score_from_other') and row['score_from_other'] else None
        }

# Read assignment2_with_llm.csv
with open('validated_dataset(round=1)/assignment2_with_llm.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name'].strip()
        llm_score_str = row['final_score'].strip() if row['final_score'] else '0.0/7.0'
        # Extract number from "X.XX/7.0" format
        match = re.match(r'(\d+\.?\d*)/', llm_score_str)
        llm_score = float(match.group(1)) if match else 0.0
        assignment2_llm_data[name] = llm_score

# Name normalization mapping
name_mapping = {
    'Matt Wolfman': 'Matt Wolfman',
    'Matthew Wolfman': 'Matt Wolfman',
    'Rachael Cooper': 'Rachael Yaran Cooper',
    'Rachael Yaran Cooper': 'Rachael Yaran Cooper',
    'ChenyangDai': 'Chenyang Dai',
    'Chris Pearce': 'Chris Philip James Pearce',
    'Samantha van Rijs': 'Samantha Afra van Rijs',
    'Fernando Torres': 'Fernando Torres Navarrete',
    'Deveen Harischandra': 'Deveen Manitha Harischandra',
    'Matthew Hayes': 'Matthew John Hayes',
    'Daphne': 'Daphne Barretto',
}

def normalize_name(name):
    if not name:
        return None
    name = str(name).strip()
    return name_mapping.get(name, name)

# Domain mapping to D1-D10
def map_to_d1_d10(domain, domain_id=None, domain_name_field=None):
    """Map domain to D1-D10 category"""
    if not domain or domain == 'Unknown':
        return None
    
    # Check domain_id first
    if domain_id and domain_id.startswith('D') and len(domain_id) <= 3:
        return domain_id
    
    # Check domain_name_field
    if domain_name_field:
        domain_name_lower = domain_name_field.lower()
        if 'daily life' in domain_name_lower:
            return 'D1'
        elif 'history' in domain_name_lower:
            return 'D2'
        elif 'markets' in domain_name_lower or 'finance' in domain_name_lower:
            return 'D3'
        elif 'medicine' in domain_name_lower or 'health' in domain_name_lower:
            return 'D4'
        elif 'economics' in domain_name_lower:
            return 'D5'
        elif 'environment' in domain_name_lower or 'climate' in domain_name_lower:
            return 'D6'
        elif 'law' in domain_name_lower or 'ethics' in domain_name_lower:
            return 'D7'
        elif 'ai' in domain_name_lower or 'tech' in domain_name_lower or 'technology' in domain_name_lower:
            return 'D8'
        elif 'sports' in domain_name_lower:
            return 'D9'
        elif 'social science' in domain_name_lower:
            return 'D10'
    
    # Map by domain name
    domain_lower = domain.lower()
    if domain == 'Daily Life' or 'daily' in domain_lower:
        return 'D1'
    elif domain == 'History' or domain == 'D2':
        return 'D2'
    elif domain in ['Markets', 'Finance', 'Business']:
        return 'D3'
    elif domain in ['Medicine', 'Health', 'Healthcare', 'Public Health', 'Epidemiology']:
        return 'D4'
    elif domain == 'Economics':
        return 'D5'
    elif domain in ['Environment', 'Environmental Science', 'Climate', 'Climate Science']:
        return 'D6'
    elif domain in ['Law & Ethics', 'Law', 'Legal', 'Ethics']:
        return 'D7'
    elif domain in ['AI & Tech', 'D8 - AI Safety & Alignment', 'Technology', 'Computer Science']:
        return 'D8'
    elif domain in ['Sports', 'D9']:
        return 'D9'
    elif domain in ['Social Science', 'D10 (Social Science)', 'Psychology', 'Public Policy', 'Criminal Justice', 'Education']:
        return 'D10'
    
    return None

def extract_case_info(case):
    """Extract case information"""
    case_id = case.get('id') or case.get('case_id') or case.get('caseId', '')
    domain = case.get('domain', 'Unknown')
    domain_id = case.get('domain_id', '')
    domain_name_field = case.get('domain_name', '')
    d_code = map_to_d1_d10(domain, domain_id, domain_name_field)
    return case_id, domain, d_code

# Collect domain data
domain_data = defaultdict(lambda: {
    'cases': [],
    'case_ids': [],
    'authors': set(),
    'validators': set()
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
                case_id, domain, d_code = extract_case_info(case)
                author = normalize_name(case.get('initial_author'))
                validator = normalize_name(case.get('validator'))
                
                # Use D1-D10 code as the key, fallback to domain if no code
                key = d_code if d_code else domain
                
                domain_data[key]['cases'].append(case)
                if case_id:
                    domain_data[key]['case_ids'].append(case_id)
                if author:
                    domain_data[key]['authors'].add(author)
                if validator:
                    domain_data[key]['validators'].add(validator)
    except Exception as e:
        continue

# Helper functions
def get_id_range(case_ids):
    if not case_ids:
        return "N/A"
    try:
        sorted_ids = sorted(case_ids, key=lambda x: (int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 0, str(x)))
    except:
        sorted_ids = sorted(case_ids)
    if len(sorted_ids) == 1:
        return sorted_ids[0]
    return f"{sorted_ids[0]}-{sorted_ids[-1]}"

def get_rule_based_score(authors):
    """Get average final_score from assignment2.csv for authors"""
    scores = []
    for author in authors:
        author_norm = normalize_name(author)
        if author_norm in assignment2_data:
            scores.append(assignment2_data[author_norm]['final_score'])
    return sum(scores) / len(scores) if scores else None

def get_score_from_other(domain_cases):
    """For each case, find validator, check if initial_author is in validator's validatees, get validatee_score"""
    scores = []
    for case in domain_cases:
        author = normalize_name(case.get('initial_author'))
        validator = normalize_name(case.get('validator'))
        
        if validator and validator in assignment2_data:
            validatees = assignment2_data[validator]['validatees']
            # Check if author is in validator's validatees list
            if validatees and author:
                # Split validatees by comma and check
                validatee_list = [v.strip() for v in validatees.split(',')]
                if author in validatee_list or any(author in v or v in author for v in validatee_list):
                    if assignment2_data[validator]['validatee_score'] is not None:
                        scores.append(assignment2_data[validator]['validatee_score'])
    return sum(scores) / len(scores) if scores else None

def get_llm_score(authors):
    """Get average LLM score from assignment2_with_llm.csv"""
    scores = []
    for author in authors:
        author_norm = normalize_name(author)
        if author_norm in assignment2_llm_data:
            scores.append(assignment2_llm_data[author_norm])
    return sum(scores) / len(scores) if scores else None

# D1-D10 domain names
d_domain_names = {
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

# Generate table
print("| Domain | Total Case Numbers | Case ID Range | Initial Author | Validator | Rule-based Score | Score from Other | LLM Score | Final Score |")
print("|--------|-------------------|---------------|----------------|-----------|------------------|------------------|-----------|-------------|")

# Process D1-D10 first, then others
d_keys = [f'D{i}' for i in range(1, 11)]
other_keys = [k for k in sorted(domain_data.keys()) if k not in d_keys]

for domain in d_keys + other_keys:
    if domain not in domain_data:
        continue
    data = domain_data[domain]
    total_cases = len(data['cases'])
    case_id_range = get_id_range(data['case_ids'])
    authors = sorted(data['authors'])
    validators = sorted(data['validators'])
    
    authors_str = ', '.join(authors[:3]) + ('...' if len(authors) > 3 else '')
    validators_str = ', '.join(validators[:3]) + ('...' if len(validators) > 3 else '')
    
    rule_score = get_rule_based_score(authors)
    score_other = get_score_from_other(data['cases'])
    llm_score = get_llm_score(authors)
    
    # Calculate final score (average of the three, all normalized to 0-5 scale)
    final_scores = []
    if rule_score is not None:
        final_scores.append(rule_score)  # Already 0-5
    if score_other is not None:
        # Normalize from 0-1 to 0-5
        final_scores.append(score_other * 5.0)
    if llm_score is not None:
        # Normalize LLM score from 0-7 to 0-5 scale
        final_scores.append((llm_score / 7.0) * 5.0)
    
    final_score = sum(final_scores) / len(final_scores) if final_scores else None
    
    rule_score_str = f"{rule_score:.2f}" if rule_score is not None else "N/A"
    score_other_str = f"{score_other:.2f}" if score_other is not None else "N/A"
    llm_score_str = f"{llm_score:.2f}" if llm_score is not None else "N/A"
    final_score_str = f"{final_score:.2f}" if final_score is not None else "N/A"
    
    # Format domain name with D code
    if domain in d_domain_names:
        domain_display = f"{d_domain_names[domain]} ({domain})"
    else:
        domain_display = domain
    
    print(f"| {domain_display} | {total_cases} | {case_id_range} | {authors_str} | {validators_str} | {rule_score_str} | {score_other_str} | {llm_score_str} | {final_score_str} |")

