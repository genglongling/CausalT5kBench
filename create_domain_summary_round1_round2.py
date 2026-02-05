#!/usr/bin/env python3
"""
Script to generate domain summary table comparing round=1 and round=2 validation.
Shows scores from both validation rounds organized by D1-D10 domains.

For round=2:
- Rule-based Score: Uses grade_assignment2.py
- Score from Other: Based on final_score_2 from round=2 datasets
- LLM Score: Uses Claude Sonnet 4.5
"""
import json
import os
import csv
from collections import defaultdict
import re
import subprocess
import sys
from pathlib import Path

# Read CSV files for round=1
assignment2_data = {}
assignment2_llm_data = {}

# Read assignment2.csv for round=1
with open('validated_dataset(round=1)/assignment2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name'].strip()
        assignment2_data[name] = {
            'final_score': float(row['final_score']) if row['final_score'] else 0.0,
            'validatees': row['validatees'].strip() if row['validatees'] else '',
            'validatee_score': float(row['validatee_score']) if row['validatee_score'] else None,
        }

# Read assignment2.csv for round=2 (rule-based scores from grading script)
assignment2_r2_data = {}
try:
    with open('validated_dataset(round=2)/assignment2.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name'].strip()
            # Use same scale as round=1 (both are from grading script, should be comparable)
            final_score = float(row['final_score']) if row['final_score'] else 0.0
            assignment2_r2_data[name] = {
                'final_score': final_score,  # Use same scale as round=1
                'final_score_raw': final_score
            }
except FileNotFoundError:
    print("Warning: validated_dataset(round=2)/assignment2.csv not found. Rule-based scores for round=2 will be unavailable.")

# Read LLM scores for round=2
round2_llm_scores = {}
try:
    with open('round2_llm_scores.json', 'r', encoding='utf-8') as f:
        round2_llm_scores = json.load(f)
except FileNotFoundError:
    print("Warning: round2_llm_scores.json not found. LLM scores for round=2 will be unavailable.")

# Read assignment2_with_llm.csv
with open('validated_dataset(round=1)/assignment2_with_llm.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name'].strip()
        llm_score_str = row['final_score'].strip() if row['final_score'] else '0.0/7.0'
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
    
    if domain_id and domain_id.startswith('D') and len(domain_id) <= 3:
        return domain_id
    
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

# Collect domain data from round=1
domain_data_r1 = defaultdict(lambda: {
    'cases': [],
    'case_ids': [],
    'authors': set(),
    'validators': set()
})

validated_dir_r1 = 'validated_dataset(round=1)'
for filename in os.listdir(validated_dir_r1):
    if not filename.endswith('.json'):
        continue
    filepath = os.path.join(validated_dir_r1, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cases = json.load(f)
            if not isinstance(cases, list):
                continue
            
            for case in cases:
                case_id, domain, d_code = extract_case_info(case)
                author = normalize_name(case.get('initial_author'))
                validator = normalize_name(case.get('validator'))
                
                key = d_code if d_code else domain
                domain_data_r1[key]['cases'].append(case)
                if case_id:
                    domain_data_r1[key]['case_ids'].append(case_id)
                if author:
                    domain_data_r1[key]['authors'].add(author)
                if validator:
                    domain_data_r1[key]['validators'].add(validator)
    except Exception as e:
        continue

# Collect domain data from round=2
domain_data_r2 = defaultdict(lambda: {
    'cases': [],
    'case_ids': [],
    'authors': set(),
    'validators': set(),
    'validators_2': set()
})

validated_dir_r2 = 'validated_dataset(round=2)'
for filename in os.listdir(validated_dir_r2):
    if not filename.endswith('.json'):
        continue
    filepath = os.path.join(validated_dir_r2, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cases = json.load(f)
            if not isinstance(cases, list):
                continue
            
            for case in cases:
                case_id, domain, d_code = extract_case_info(case)
                author = normalize_name(case.get('initial_author'))
                validator = normalize_name(case.get('validator'))
                validator_2 = case.get('validator_2', '')
                
                key = d_code if d_code else domain
                domain_data_r2[key]['cases'].append(case)
                if case_id:
                    domain_data_r2[key]['case_ids'].append(case_id)
                if author:
                    domain_data_r2[key]['authors'].add(author)
                if validator:
                    domain_data_r2[key]['validators'].add(validator)
                if validator_2:
                    domain_data_r2[key]['validators_2'].add(validator_2)
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
            if validatees and author:
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

def get_rule_based_score_r2(authors, domain_cases):
    """
    Get rule-based score for round=2 using grade_assignment2.py results.
    Reads from assignment2.csv generated by the grading script.
    Scores are already normalized to 0-5 scale.
    """
    scores = []
    for author in authors:
        author_norm = normalize_name(author)
        if author_norm in assignment2_r2_data:
            scores.append(assignment2_r2_data[author_norm]['final_score'])
    return sum(scores) / len(scores) if scores else None

def get_score_from_other_r2(domain_cases):
    """
    Get Score from Other for round=2 based on final_score_2.
    final_score_2 is the score given by the second validator (Longling Geng).
    Normalize from 0-10 to 0-1 scale to match round=1 format.
    """
    scores = []
    for case in domain_cases:
        score_2 = case.get('final_score_2')
        if score_2 is not None:
            # final_score_2 is on 0-10 scale, normalize to 0-1 scale (like round=1)
            scores.append(float(score_2) / 10.0)
    return sum(scores) / len(scores) if scores else None

def get_llm_score_r2(domain_code):
    """
    Get LLM score for round=2 from pre-evaluated scores.
    Scores are on 0-7 scale (matching round=1 format).
    """
    return round2_llm_scores.get(domain_code)

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
print("| Domain | Total Case Numbers | Case ID Range | Initial Author | First Validator | Rule-based Score (human validation round=1) | Score from Other (human validation round=1) | LLM Score (human validation round=1) | Final Score (human validation round=1) | Second Validator | Rule-based Score (human validation round=2) | Score from Other (human validation round=2) | LLM Score (human validation round=2) | Final Score (human validation round=2) |")
print("|--------|-------------------|---------------|----------------|-----------------|-------------------------------------------|--------------------------------------------|--------------------------------------|----------------------------------------|------------------|-------------------------------------------|--------------------------------------------|--------------------------------------|----------------------------------------|")

# Process D1-D10 first
d_keys = [f'D{i}' for i in range(1, 11)]

for domain in d_keys:
    if domain not in domain_data_r1:
        continue
    
    data_r1 = domain_data_r1[domain]
    data_r2 = domain_data_r2.get(domain, {'cases': [], 'case_ids': [], 'authors': set(), 'validators': set(), 'validators_2': set()})
    
    total_cases = len(data_r1['cases'])
    case_id_range = get_id_range(data_r1['case_ids'])
    authors = sorted(data_r1['authors'])
    validators_r1 = sorted(data_r1['validators'])
    validators_r2 = sorted(data_r2.get('validators_2', set()))
    
    authors_str = ', '.join(authors[:2]) + ('...' if len(authors) > 2 else '')
    validators_r1_str = ', '.join(validators_r1[:2]) + ('...' if len(validators_r1) > 2 else '')
    validators_r2_str = ', '.join(validators_r2) if validators_r2 else 'Longling Geng'
    
    # Round 1 scores
    rule_score_r1 = get_rule_based_score(authors)
    score_other_r1 = get_score_from_other(data_r1['cases'])
    llm_score_r1 = get_llm_score(authors)
    
    # Round 2 scores
    # Rule-based score: Use grade_assignment2.py results (same scale as round=1)
    rule_score_r2 = get_rule_based_score_r2(authors, data_r2['cases']) if data_r2['cases'] else None
    # Score from Other: Based on final_score_2 from round=2 (0-1 scale)
    score_other_r2 = get_score_from_other_r2(data_r2['cases']) if data_r2['cases'] else None
    # LLM Score: From pre-evaluated Claude Sonnet 4.5 scores
    llm_score_r2 = get_llm_score_r2(domain)
    
    # Calculate final scores (normalized to 0-5 scale)
    final_scores_r1 = []
    if rule_score_r1 is not None:
        final_scores_r1.append(rule_score_r1)
    if score_other_r1 is not None:
        final_scores_r1.append(score_other_r1 * 5.0)
    if llm_score_r1 is not None:
        final_scores_r1.append((llm_score_r1 / 7.0) * 5.0)
    final_score_r1 = sum(final_scores_r1) / len(final_scores_r1) if final_scores_r1 else None
    
    final_scores_r2 = []
    if rule_score_r2 is not None:
        # rule_score_r2 is on same scale as round=1 (0-5 scale from assignment2.csv)
        final_scores_r2.append(rule_score_r2)
    if score_other_r2 is not None:
        # score_other_r2 is on 0-1 scale, normalize to 0-5 for final calculation
        final_scores_r2.append(score_other_r2 * 5.0)
    if llm_score_r2 is not None:
        # llm_score_r2 is already on 0-5 scale (evaluated to match 0-5 scale)
        final_scores_r2.append(llm_score_r2)
    final_score_r2 = sum(final_scores_r2) / len(final_scores_r2) if final_scores_r2 else None
    
    # Format values
    rule_score_r1_str = f"{rule_score_r1:.2f}" if rule_score_r1 is not None else "N/A"
    score_other_r1_str = f"{score_other_r1:.2f}" if score_other_r1 is not None else "N/A"
    llm_score_r1_str = f"{llm_score_r1:.2f}" if llm_score_r1 is not None else "N/A"
    final_score_r1_str = f"{final_score_r1:.2f}" if final_score_r1 is not None else "N/A"
    
    # Format round=2 scores
    rule_score_r2_str = f"{rule_score_r2:.2f}" if rule_score_r2 is not None else "N/A"
    score_other_r2_str = f"{score_other_r2:.2f}" if score_other_r2 is not None else "N/A"  # 0-1 scale
    llm_score_r2_str = f"{llm_score_r2:.2f}" if llm_score_r2 is not None else ""  # 0-7 scale
    final_score_r2_str = f"{final_score_r2:.2f}" if final_score_r2 is not None else "N/A"
    
    domain_display = d_domain_names.get(domain, domain)
    
    print(f"| {domain_display} ({domain}) | {total_cases} | {case_id_range} | {authors_str} | {validators_r1_str} | {rule_score_r1_str} | {score_other_r1_str} | {llm_score_r1_str} | {final_score_r1_str} | {validators_r2_str} | {rule_score_r2_str} | {score_other_r2_str} | {llm_score_r2_str} | {final_score_r2_str} |")

