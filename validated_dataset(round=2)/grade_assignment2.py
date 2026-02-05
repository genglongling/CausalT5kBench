#!/usr/bin/env python3
"""
Assignment 2 Grading Script

Grades Assignment 2 submissions based on:
1. Dataset completeness (1 point)
2. Fields correctness (1 point)
3. Pearl level distribution (1 point)
4. Labeling distribution (1 point)
5. Labeling content quality using LLM (2 points)
6. Schema.json correctness (1 point)
7. Score.json correctness (1 point)
8. Score from validators (other's point/10)
9. Bonus (1 point if >170 cases)
"""

import json
import yaml
import csv
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
import re

# Target distributions from assignment2.tex
TARGET_TOTAL_CASES = 170
TARGET_PEARL_L1 = 17  # 10% of 170
TARGET_PEARL_L2 = 102  # 60% of 170
TARGET_PEARL_L3 = 51  # 30% of 170

# L1 label distribution (for 17 cases, scaled from 250:200:50 ratio)
TARGET_L1_WOLF = 8  # ~47% of 17
TARGET_L1_SHEEP = 7  # ~41% of 17
TARGET_L1_AMBIGUOUS = 2  # ~12% of 17

# L2: all should be NO
# L3 label distribution (for 51 cases, scaled from 50:50:50 ratio)
TARGET_L3_VALID = 17
TARGET_L3_INVALID = 17
TARGET_L3_CONDITIONAL = 17

# Tolerance for distributions
PEARL_TOLERANCE = 0.10  # ±10%
LABEL_TOLERANCE = 0.15  # ±15%

# Required fields for dataset (from assignment2.tex appendix)
REQUIRED_FIELDS = [
    "id", "case_id", "bucket", "pearl_level", "domain", "scenario", "claim",
    "label", "is_ambiguous", "variables", "trap", "difficulty",
    "causal_structure", "key_insight", "hidden_timestamp", "conditional_answers",
    "wise_refusal", "gold_rationale",
    "initial_author", "validator", "final_score"  # Assignment 2 specific
]

def load_metadata(metadata_file: Path) -> Dict[str, Any]:
    """Load submission metadata from YAML file."""
    with open(metadata_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    submissions = {}
    current_submission = None
    current_field = None
    in_submitters = False
    current_submitter = {}
    
    for line in content.split('\n'):
        stripped = line.strip()
        
        # Check for new submission
        if stripped.startswith('submission_') and stripped.endswith(':'):
            # Save previous submitter if exists
            if current_submission and current_submitter:
                if 'submitters' not in submissions[current_submission]:
                    submissions[current_submission]['submitters'] = []
                submissions[current_submission]['submitters'].append(current_submitter)
                current_submitter = {}
            
            current_submission = stripped.rstrip(':')
            submissions[current_submission] = {
                'submitters': [],
                'created_at': None,
                'score': 0.0,
                'status': 'pending'
            }
            in_submitters = False
            current_field = None
        
        elif current_submission:
            # Check if entering submitters section
            if ':submitters:' in stripped:
                in_submitters = True
                current_submitter = {}
            # Check for submitter fields
            elif in_submitters and ':name:' in stripped:
                # Save previous submitter
                if current_submitter:
                    submissions[current_submission]['submitters'].append(current_submitter)
                current_submitter = {'name': stripped.split(':name:')[1].strip()}
            elif in_submitters and ':email:' in stripped:
                current_submitter['email'] = stripped.split(':email:')[1].strip()
            elif in_submitters and ':sid:' in stripped:
                sid = stripped.split(':sid:')[1].strip().strip("'\"")
                current_submitter['sid'] = sid
            elif stripped.startswith(':created_at:'):
                in_submitters = False
                if current_submitter:
                    submissions[current_submission]['submitters'].append(current_submitter)
                    current_submitter = {}
                date_str = stripped.split(':created_at:')[1].strip()
                submissions[current_submission]['created_at'] = date_str
            elif stripped.startswith(':status:'):
                in_submitters = False
                if current_submitter:
                    submissions[current_submission]['submitters'].append(current_submitter)
                    current_submitter = {}
                submissions[current_submission]['status'] = stripped.split(':status:')[1].strip()
    
    # Save last submitter
    if current_submission and current_submitter:
        if 'submitters' not in submissions[current_submission]:
            submissions[current_submission]['submitters'] = []
        submissions[current_submission]['submitters'].append(current_submitter)
    
    return submissions

def find_submission_files(submission_dir: Path) -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
    """Find the three required files in a submission directory (searches recursively)."""
    dataset_file = None
    schema_file = None
    score_file = None
    
    # Search recursively for JSON files, excluding __MACOSX and node_modules
    json_files = []
    for pattern in ["**/*.json", "*.json"]:
        for file in submission_dir.glob(pattern):
            # Skip system and package files
            if "__MACOSX" in str(file) or "node_modules" in str(file):
                continue
            filename = file.name.lower()
            if filename in ['package.json', 'package-lock.json', 'tsconfig.json']:
                continue
            if file not in json_files:
                json_files.append(file)
    
    # First pass: look for standard patterns
    for file in json_files:
        filename = file.name.lower()
        # Check for schema files (highest priority - clear naming)
        if "schema" in filename and "dataset" not in filename and "score" not in filename:
            if not schema_file:  # Take first match
                schema_file = file
        # Check for score files (but exclude files that look like datasets)
        elif "score" in filename and "dataset" not in filename and "validated" not in filename:
            if not score_file:  # Take first match
                score_file = file
        # Check for dataset files
        elif "dataset" in filename and "schema" not in filename:
            if not dataset_file:  # Take first match
                dataset_file = file
    
    # If dataset not found, try to find any large JSON file that might be a dataset
    if not dataset_file:
        for file in json_files:
            filename = file.name.lower()
            # Skip files already identified as schema or score
            if file == schema_file or file == score_file:
                continue
            # Skip obvious schema files
            if "schema" in filename and file != schema_file:
                continue
            # Check if it's likely a dataset (has cases or is a list)
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # If it's a list with multiple items, or dict with 'cases', likely a dataset
                    if (isinstance(data, list) and len(data) > 10) or \
                       (isinstance(data, dict) and 'cases' in data):
                        dataset_file = file
                        break
            except:
                continue
    
    # Also check files with "validated" in name (might be datasets even if they have "score" in name)
    if not dataset_file:
        for file in json_files:
            filename = file.name.lower()
            # Skip files already identified
            if file == schema_file or file == score_file or file == dataset_file:
                continue
            # Check for validated files (these are often datasets)
            if "validated" in filename:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Verify it's actually a dataset structure
                        if (isinstance(data, list) and len(data) > 10) or \
                           (isinstance(data, dict) and 'cases' in data):
                            dataset_file = file
                            break
                except:
                    continue
    
    return dataset_file, schema_file, score_file

def check_dataset_completeness(dataset_file: Path) -> Tuple[bool, int, Dict[str, int]]:
    """Check if dataset has correct number of cases. Returns (pass, count, pearl_dist)."""
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict) and 'cases' in data:
            count = len(data['cases'])
            data = data['cases']
        else:
            return False, 0, {}
        
        # Count Pearl levels
        pearl_dist = {'L1': 0, 'L2': 0, 'L3': 0}
        if isinstance(data, list):
            for case in data:
                if isinstance(case, dict):
                    pearl = case.get('pearl_level', '')
                    if pearl in ['L1', 'L2', 'L3']:
                        pearl_dist[pearl] += 1
        
        # Check if count is >= TARGET_TOTAL_CASES
        passed = count >= TARGET_TOTAL_CASES
        return passed, count, pearl_dist
    except Exception as e:
        print(f"Error reading dataset file {dataset_file}: {e}")
        return False, 0, {}

def check_fields(dataset_file: Path) -> Tuple[bool, List[str]]:
    """Check if all required fields are present. Returns (pass, missing_fields)."""
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'cases' in data:
            data = data['cases']
        
        if not isinstance(data, list) or len(data) == 0:
            return False, REQUIRED_FIELDS
        
        # Check first case for required fields
        sample = data[0]
        missing = [f for f in REQUIRED_FIELDS if f not in sample]
        
        return len(missing) == 0, missing
    except Exception as e:
        print(f"Error checking fields in {dataset_file}: {e}")
        return False, REQUIRED_FIELDS

def check_pearl_distribution(pearl_dist: Dict[str, int], total: int) -> Tuple[bool, Dict[str, float], Dict[str, int]]:
    """Check if Pearl level distribution matches target. Returns (pass, percentages, counts)."""
    if total == 0:
        return False, {}, {}
    
    counts = {
        'L1': pearl_dist.get('L1', 0),
        'L2': pearl_dist.get('L2', 0),
        'L3': pearl_dist.get('L3', 0)
    }
    
    percentages = {
        'L1': (counts['L1'] / total) * 100,
        'L2': (counts['L2'] / total) * 100,
        'L3': (counts['L3'] / total) * 100
    }
    
    # If total > 170, check if they have at least the target numbers (not exact ratio)
    if total > TARGET_TOTAL_CASES:
        passed = (
            counts['L1'] >= TARGET_PEARL_L1 and
            counts['L2'] >= TARGET_PEARL_L2 and
            counts['L3'] >= TARGET_PEARL_L3
        )
    else:
        # If exactly 170, check percentage match
        target_percentages = {
            'L1': (TARGET_PEARL_L1 / TARGET_TOTAL_CASES) * 100,  # ~10%
            'L2': (TARGET_PEARL_L2 / TARGET_TOTAL_CASES) * 100,  # ~60%
            'L3': (TARGET_PEARL_L3 / TARGET_TOTAL_CASES) * 100   # ~30%
        }
        
        passed = True
        for level in ['L1', 'L2', 'L3']:
            diff = abs(percentages[level] - target_percentages[level])
            if diff > PEARL_TOLERANCE * 100:  # Convert tolerance to percentage
                passed = False
    
    return passed, percentages, counts

def check_label_distribution(dataset_file: Path, pearl_dist: Dict[str, int]) -> Tuple[bool, Dict[str, Dict[str, int]]]:
    """Check if label distribution matches target. Returns (pass, label_dist)."""
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'cases' in data:
            data = data['cases']
        
        if not isinstance(data, list):
            return False, {}
        
        label_dist = {
            'L1': {'Wolf': 0, 'Sheep': 0, 'Ambiguous': 0},
            'L2': {'NO': 0, 'Other': 0},
            'L3': {'Valid': 0, 'Invalid': 0, 'Conditional': 0}
        }
        
        for case in data:
            if not isinstance(case, dict):
                continue
            pearl = case.get('pearl_level', '')
            label = case.get('label', '').strip()  # Use 'label' not 'final_label'
            
            if pearl == 'L1':
                # L1 labels: YES (Sheep), NO (Wolf), AMBIGUOUS
                if label.upper() in ['YES', 'SHEEP', 'S']:
                    label_dist['L1']['Sheep'] += 1
                elif label.upper() in ['NO', 'WOLF', 'W']:
                    label_dist['L1']['Wolf'] += 1
                elif label.upper() in ['AMBIGUOUS', 'A']:
                    label_dist['L1']['Ambiguous'] += 1
            elif pearl == 'L2':
                # L2: all should be NO
                if label.upper() == 'NO':
                    label_dist['L2']['NO'] += 1
                else:
                    label_dist['L2']['Other'] += 1
            elif pearl == 'L3':
                # L3 labels: VALID, INVALID, CONDITIONAL
                if label.upper() in ['VALID', 'V']:
                    label_dist['L3']['Valid'] += 1
                elif label.upper() in ['INVALID', 'I']:
                    label_dist['L3']['Invalid'] += 1
                elif label.upper() in ['CONDITIONAL', 'C']:
                    label_dist['L3']['Conditional'] += 1
        
        # Check if distributions match targets
        passed = True
        
        # L1: Check ratio (roughly 8:7:2 for 17 cases)
        # Note: L1 uses YES (Sheep), NO (Wolf), AMBIGUOUS
        l1_total = pearl_dist.get('L1', 0)
        if l1_total > 0:
            # YES = Sheep, NO = Wolf
            sheep_pct = label_dist['L1']['Sheep'] / l1_total
            wolf_pct = label_dist['L1']['Wolf'] / l1_total
            amb_pct = label_dist['L1']['Ambiguous'] / l1_total
            # Should be roughly 41% Sheep (YES):47% Wolf (NO):12% Ambiguous
            if abs(sheep_pct - 0.41) > LABEL_TOLERANCE or abs(wolf_pct - 0.47) > LABEL_TOLERANCE:
                passed = False
        
        # L2: Should be 100% NO
        l2_total = pearl_dist.get('L2', 0)
        if l2_total > 0:
            no_pct = label_dist['L2']['NO'] / l2_total
            if no_pct < 0.95:  # Allow 5% tolerance
                passed = False
        
        # L3: Should be roughly 1:1:1
        l3_total = pearl_dist.get('L3', 0)
        if l3_total > 0:
            valid_pct = label_dist['L3']['Valid'] / l3_total
            invalid_pct = label_dist['L3']['Invalid'] / l3_total
            cond_pct = label_dist['L3']['Conditional'] / l3_total
            # Should be roughly 33% each
            if abs(valid_pct - 0.33) > LABEL_TOLERANCE or abs(invalid_pct - 0.33) > LABEL_TOLERANCE:
                passed = False
        
        return passed, label_dist
    except Exception as e:
        print(f"Error checking label distribution: {e}")
        return False, {}

def evaluate_labeling_content_llm(dataset_file: Path) -> Tuple[float, str]:
    """
    Evaluate labeling content quality using LLM.
    Returns (score, notes) where score is 0-2.
    
    TODO: Implement LLM-based evaluation.
    This function should:
    1. Sample cases from the dataset
    2. Send them to an LLM API (e.g., OpenAI, Anthropic) with evaluation prompts
    3. Parse the LLM response and assign scores based on content quality
    
    Example integration:
    ```python
    import openai
    # Sample cases
    # Send to LLM with prompt asking to evaluate quality
    # Parse response and return score (0-2)
    ```
    """
    # Placeholder: Return 0.0 until LLM evaluation is implemented
    return 0.0, "LLM evaluation not yet implemented"

def check_schema(schema_file: Path) -> Tuple[bool, str]:
    """Check if schema.json is valid and correct. Returns (pass, notes)."""
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Check required top-level fields
        required_schema_fields = ['schema_version', 'assignment', 'author', 'group', 'field_definitions']
        missing = [f for f in required_schema_fields if f not in schema]
        
        if missing:
            return False, f"Missing schema fields: {', '.join(missing)}"
        
        # Check if field_definitions contains required fields (from assignment2.tex)
        field_defs = schema.get('field_definitions', {})
        required_case_fields = ['pearl_level', 'label', 'trap', 'difficulty', 'variables', 'scenario']
        missing_case_fields = [f for f in required_case_fields if f not in field_defs]
        
        if missing_case_fields:
            return False, f"Missing field definitions: {', '.join(missing_case_fields)}"
        
        return True, "Schema is valid"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error checking schema: {e}"

def check_score(score_file: Path) -> Tuple[bool, str, float]:
    """Check if score.json is valid and correct. Returns (pass, notes, avg_score)."""
    try:
        with open(score_file, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        
        if not isinstance(scores, list):
            return False, "Score file should be a JSON array", 0.0
        
        if len(scores) == 0:
            return False, "No scores found", 0.0
        
        # Check structure of each score entry
        required_score_fields = ['case_id', 'total', 'decision']
        total_scores = []
        
        for i, score_entry in enumerate(scores):
            missing = [f for f in required_score_fields if f not in score_entry]
            if missing:
                return False, f"Score entry {i+1} missing fields: {', '.join(missing)}", 0.0
            
            total = score_entry.get('total', 0)
            if isinstance(total, (int, float)):
                total_scores.append(float(total))
        
        if len(total_scores) == 0:
            return False, "No valid scores found", 0.0
        
        avg_score = sum(total_scores) / len(total_scores)
        return True, f"Valid score file with {len(scores)} entries", avg_score
    
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}", 0.0
    except Exception as e:
        return False, f"Error checking score: {e}", 0.0

def load_cross_validation_data(csv_file: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load cross-validation assignment data to find validators and validatees."""
    validator_scores = defaultdict(list)  # email -> list of scores received
    validatee_info = defaultdict(list)  # email -> list of validatees
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Big Group'] == 'TOTAL':
                    continue
                
                validated_email = row['Validated Email']
                validator_email = row['Validator Email']
                validated_name = row['Validated Name']
                
                # This will be populated from score.json files
                # For now, we'll need to read those files
                validatee_info[validator_email].append({
                    'name': validated_name,
                    'email': validated_email
                })
    except Exception as e:
        print(f"Error loading cross-validation data: {e}")
    
    return validator_scores, validatee_info

def calculate_validator_scores(submissions_dir: Path, cross_val_file: Path, metadata: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, List[str]], Dict[str, float]]:
    """
    Calculate average scores received from validators and list of validatees.
    Returns: (validator_avg_scores, validatee_lists, validatee_avg_scores)
    """
    # Map email to submission_id
    email_to_submission = {}
    for sub_id, meta in metadata.items():
        if meta.get('submitters'):
            email = meta['submitters'][0].get('email', '')
            if email:
                email_to_submission[email] = sub_id
    
    validator_scores = defaultdict(list)  # validated_email -> list of scores from validators
    validatee_lists = defaultdict(list)  # validator_email -> list of validatee names
    validatee_scores_given = defaultdict(list)  # validator_email -> list of scores they gave
    
    # Load cross-validation assignments (if file exists)
    if cross_val_file.exists():
        with open(cross_val_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Big Group') == 'TOTAL':
                    continue
                
                validated_email = row.get('Validated Email', '')
                validator_email = row.get('Validator Email', '')
                validated_name = row.get('Validated Name', '')
                
                if validated_name:
                    validatee_lists[validator_email].append(validated_name)
                
                # Try to find validator's submission and their score.json
                validator_sub_id = email_to_submission.get(validator_email)
                if validator_sub_id:
                    validator_dir = submissions_dir / validator_sub_id
                    _, _, score_file = find_submission_files(validator_dir)
                    
                    if score_file:
                        # Read score.json and calculate average
                        try:
                            with open(score_file, 'r', encoding='utf-8') as f:
                                scores = json.load(f)
                            if isinstance(scores, list) and len(scores) > 0:
                                total_scores = [s.get('total', 0) for s in scores if isinstance(s.get('total'), (int, float))]
                                if total_scores:
                                    avg = sum(total_scores) / len(total_scores)
                                    validator_scores[validated_email].append(avg)
                                    validatee_scores_given[validator_email].append(avg)
                        except Exception as e:
                            print(f"Warning: Could not read score file for {validator_email}: {e}")
    else:
        print(f"Warning: Cross-validation file not found at {cross_val_file}. Skipping validator scores.")
    
    # Calculate averages
    avg_scores_received = {}
    for email, scores in validator_scores.items():
        if scores:
            avg_scores_received[email] = sum(scores) / len(scores) / 10.0  # Normalize to 0-1
        else:
            avg_scores_received[email] = 0.0
    
    avg_scores_given = {}
    for email, scores in validatee_scores_given.items():
        if scores:
            avg_scores_given[email] = sum(scores) / len(scores) / 10.0  # Normalize to 0-1
        else:
            avg_scores_given[email] = 0.0
    
    return avg_scores_received, validatee_lists, avg_scores_given

def grade_submission_from_file(submissions_dir: Path, submission_id: str, metadata: Dict[str, Any], dataset_file: Path) -> Dict[str, Any]:
    """Grade a submission when we have the dataset file directly."""
    # Create a result dict similar to grade_submission
    result = {
        'submission_id': submission_id,
        'name': '',
        'sid': '',
        'email': '',
        'dataset_completeness': 0.0,
        'fields': 0.0,
        'pearl_distribution': 0.0,
        'label_distribution': 0.0,
        'labeling_content': 0.0,
        'schema_correct': 0.0,
        'score_correct': 0.0,
        'score_from_validators': 0.0,
        'bonus': 0.0,
        'final_score': 0.0,
        'notes': [],
        'validatees': '',
        'validatee_score': 0.0
    }
    
    # Get submitter info
    if metadata.get('submitters'):
        submitter = metadata['submitters'][0]
        result['name'] = submitter.get('name', '')
        result['sid'] = submitter.get('sid', '')
        result['email'] = submitter.get('email', '')
    
    result['notes'].append(f"Dataset file: {dataset_file.name}")
    
    # Grade the dataset file directly
    passed, count, pearl_dist = check_dataset_completeness(dataset_file)
    result['dataset_completeness'] = 1.0 if passed else 0.0
    result['notes'].append(f"Dataset cases: {count} (target: {TARGET_TOTAL_CASES})")
    
    passed, missing = check_fields(dataset_file)
    result['fields'] = 1.0 if passed else 0.0
    if missing:
        result['notes'].append(f"Missing fields: {', '.join(missing)}")
    
    passed, percentages, pearl_counts = check_pearl_distribution(pearl_dist, count)
    result['pearl_distribution'] = 1.0 if passed else 0.0
    stats_note = f"Pearl distribution - L1: {pearl_counts.get('L1', 0)} ({percentages.get('L1', 0):.1f}%), L2: {pearl_counts.get('L2', 0)} ({percentages.get('L2', 0):.1f}%), L3: {pearl_counts.get('L3', 0)} ({percentages.get('L3', 0):.1f}%)"
    result['notes'].append(stats_note)
    
    passed, label_dist = check_label_distribution(dataset_file, pearl_dist)
    result['label_distribution'] = 1.0 if passed else 0.0
    
    score, notes = evaluate_labeling_content_llm(dataset_file)
    result['labeling_content'] = score
    result['notes'].append(f"Labeling content: {notes}")
    
    # Schema and score files not available when using direct JSON
    result['notes'].append("Schema file: Not available (using direct JSON)")
    result['notes'].append("Score file: Not available (using direct JSON)")
    
    # Bonus for >170 cases
    if count > TARGET_TOTAL_CASES:
        result['bonus'] = 1.0
        result['notes'].append(f"Bonus: {count - TARGET_TOTAL_CASES} extra cases")
    
    # Extract validatees from initial_author field
    validatees_from_dataset = set()
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'cases' in data:
            data = data['cases']
        
        if isinstance(data, list):
            for case in data:
                initial_author = case.get('initial_author', '').strip()
                if initial_author:
                    validatees_from_dataset.add(initial_author)
    except Exception as e:
        result['notes'].append(f"Warning: Could not extract validatees: {e}")
    
    result['validatees'] = ', '.join(sorted(validatees_from_dataset)) if validatees_from_dataset else ''
    
    # Calculate final score
    result['final_score'] = (
        result['dataset_completeness'] +
        result['fields'] +
        result['pearl_distribution'] +
        result['label_distribution'] +
        result['labeling_content'] +
        result['schema_correct'] +
        result['score_correct'] +
        result['score_from_validators'] +
        result['bonus']
    )
    
    return result

def grade_submission(submission_dir: Path, submission_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Grade a single submission."""
    result = {
        'submission_id': submission_id,
        'name': '',
        'sid': '',
        'email': '',
        'dataset_completeness': 0.0,
        'fields': 0.0,
        'pearl_distribution': 0.0,
        'label_distribution': 0.0,
        'labeling_content': 0.0,
        'schema_correct': 0.0,
        'score_correct': 0.0,
        'score_from_validators': 0.0,
        'bonus': 0.0,
        'final_score': 0.0,
        'notes': []
    }
    
    # Get submitter info
    if metadata.get('submitters'):
        submitter = metadata['submitters'][0]
        result['name'] = submitter.get('name', '')
        result['sid'] = submitter.get('sid', '')
        result['email'] = submitter.get('email', '')
    
    # Find files
    dataset_file, schema_file, score_file = find_submission_files(submission_dir)
    
    if not dataset_file:
        result['notes'].append("Missing dataset.json file")
        # Still try to extract score even if dataset is missing
        if score_file:
            result['notes'].append(f"Score file: {score_file.name}")
            # Extract validatee_score before returning - use same logic as below
            try:
                with open(score_file, 'r', encoding='utf-8') as f:
                    scores = json.load(f)
                
                avg_score = 0.0
                score_format_used = None
                
                if isinstance(scores, list) and len(scores) > 0:
                    total_scores = []
                    for s in scores:
                        if isinstance(s, dict):
                            score_val = s.get('final_score') or s.get('total') or s.get('total_score') or s.get('score')
                            if isinstance(score_val, (int, float)):
                                total_scores.append(float(score_val))
                                if not score_format_used:
                                    if 'final_score' in s:
                                        score_format_used = "final_score"
                                    elif 'total' in s:
                                        score_format_used = "total"
                                    elif 'total_score' in s:
                                        score_format_used = "total_score"
                                    elif 'score' in s:
                                        score_format_used = "score"
                    if total_scores:
                        avg_score = sum(total_scores) / len(total_scores)
                        if score_format_used:
                            result['notes'].append(f"Score format: {score_format_used}, {len(total_scores)} entries")
                elif isinstance(scores, dict):
                    if 'results' in scores:
                        results = scores.get('results', [])
                        if isinstance(results, list):
                            total_scores = []
                            for r in results:
                                if isinstance(r, dict):
                                    score_val = r.get('total') or r.get('final_score') or r.get('total_score') or r.get('score')
                                    if isinstance(score_val, (int, float)):
                                        total_scores.append(float(score_val))
                            if total_scores:
                                avg_score = sum(total_scores) / len(total_scores)
                                score_format_used = "results"
                                result['notes'].append(f"Score format: {score_format_used}, {len(total_scores)} entries")
                    elif 'average_score' in scores:
                        avg_score = scores.get('average_score', 0.0)
                        score_format_used = "average_score"
                        result['notes'].append(f"Score format: {score_format_used}")
                
                if avg_score >= 0:
                    result['validatee_score'] = avg_score / 10.0
                else:
                    result['validatee_score'] = 0.0
            except Exception as e:
                result['notes'].append(f"Warning: Could not read score file: {e}")
                result['validatee_score'] = 0.0
        else:
            result['notes'].append("Missing score.json file")
            result['validatee_score'] = 0.0
        return result
    else:
        # Note the actual filename found
        result['notes'].append(f"Dataset file: {dataset_file.name}")
    
    if not schema_file:
        result['notes'].append("Missing schema.json file")
    else:
        result['notes'].append(f"Schema file: {schema_file.name}")
    
    if not score_file:
        result['notes'].append("Missing score.json file")
    else:
        result['notes'].append(f"Score file: {score_file.name}")
    
    # 1. Check dataset completeness
    passed, count, pearl_dist = check_dataset_completeness(dataset_file)
    result['dataset_completeness'] = 1.0 if passed else 0.0
    result['notes'].append(f"Dataset cases: {count} (target: {TARGET_TOTAL_CASES})")
    
    # 2. Check fields
    passed, missing = check_fields(dataset_file)
    result['fields'] = 1.0 if passed else 0.0
    if missing:
        result['notes'].append(f"Missing fields: {', '.join(missing)}")
    
    # 3. Check Pearl distribution
    passed, percentages, pearl_counts = check_pearl_distribution(pearl_dist, count)
    result['pearl_distribution'] = 1.0 if passed else 0.0
    
    # Add detailed statistics to notes
    stats_note = f"Pearl distribution - L1: {pearl_counts.get('L1', 0)} ({percentages.get('L1', 0):.1f}%), L2: {pearl_counts.get('L2', 0)} ({percentages.get('L2', 0):.1f}%), L3: {pearl_counts.get('L3', 0)} ({percentages.get('L3', 0):.1f}%)"
    if count > TARGET_TOTAL_CASES:
        stats_note += f" | Target (min): L1≥{TARGET_PEARL_L1}, L2≥{TARGET_PEARL_L2}, L3≥{TARGET_PEARL_L3}"
    else:
        stats_note += f" | Target: L1={TARGET_PEARL_L1} (10%), L2={TARGET_PEARL_L2} (60%), L3={TARGET_PEARL_L3} (30%)"
    result['notes'].append(stats_note)
    
    # 4. Check label distribution
    passed, label_dist = check_label_distribution(dataset_file, pearl_dist)
    result['label_distribution'] = 1.0 if passed else 0.0
    
    # Add detailed label statistics to notes
    label_stats = []
    if pearl_counts.get('L1', 0) > 0:
        l1_labels = label_dist.get('L1', {})
        l1_total = sum(l1_labels.values())
        if l1_total > 0:
            label_stats.append(f"L1 labels - YES: {l1_labels.get('Sheep', 0)} ({l1_labels.get('Sheep', 0)/l1_total*100:.1f}%), NO: {l1_labels.get('Wolf', 0)} ({l1_labels.get('Wolf', 0)/l1_total*100:.1f}%), AMBIGUOUS: {l1_labels.get('Ambiguous', 0)} ({l1_labels.get('Ambiguous', 0)/l1_total*100:.1f}%)")
    
    if pearl_counts.get('L2', 0) > 0:
        l2_labels = label_dist.get('L2', {})
        l2_total = sum(l2_labels.values())
        if l2_total > 0:
            no_pct = (l2_labels.get('NO', 0) / l2_total) * 100
            label_stats.append(f"L2 labels - NO: {l2_labels.get('NO', 0)} ({no_pct:.1f}%), Other: {l2_labels.get('Other', 0)}")
    
    if pearl_counts.get('L3', 0) > 0:
        l3_labels = label_dist.get('L3', {})
        l3_total = sum(l3_labels.values())
        if l3_total > 0:
            label_stats.append(f"L3 labels - VALID: {l3_labels.get('Valid', 0)} ({l3_labels.get('Valid', 0)/l3_total*100:.1f}%), INVALID: {l3_labels.get('Invalid', 0)} ({l3_labels.get('Invalid', 0)/l3_total*100:.1f}%), CONDITIONAL: {l3_labels.get('Conditional', 0)} ({l3_labels.get('Conditional', 0)/l3_total*100:.1f}%)")
    
    if label_stats:
        result['notes'].append("Label distribution: " + " | ".join(label_stats))
    else:
        result['notes'].append("Label distribution: Unable to analyze")
    
    # 5. Evaluate labeling content (LLM)
    score, notes = evaluate_labeling_content_llm(dataset_file)
    result['labeling_content'] = score
    result['notes'].append(f"Labeling content: {notes}")
    
    # 6. Check schema
    if schema_file:
        passed, notes = check_schema(schema_file)
        result['schema_correct'] = 1.0 if passed else 0.0
        result['notes'].append(f"Schema: {notes}")
    else:
        result['notes'].append("Schema file not found")
    
    # 7. Check score
    if score_file:
        passed, notes, avg_score = check_score(score_file)
        result['score_correct'] = 1.0 if passed else 0.0
        result['notes'].append(f"Score file: {notes}")
    else:
        result['notes'].append("Score file not found")
    
    # 8. Bonus for >170 cases
    if count > TARGET_TOTAL_CASES:
        result['bonus'] = 1.0
        result['notes'].append(f"Bonus: {count - TARGET_TOTAL_CASES} extra cases")
    
    # 9. Get validatees from initial_author field in dataset
    validatees_from_dataset = set()
    if dataset_file:
        try:
            with open(dataset_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'cases' in data:
                data = data['cases']
            
            if isinstance(data, list):
                for case in data:
                    initial_author = case.get('initial_author', '').strip()
                    if initial_author:
                        validatees_from_dataset.add(initial_author)
        except Exception as e:
            result['notes'].append(f"Warning: Could not extract validatees: {e}")
    
    result['validatees'] = ', '.join(sorted(validatees_from_dataset)) if validatees_from_dataset else ''
    
    # 10. Get validatee_score from score.json (average score they gave to validatees)
    if score_file:
        try:
            with open(score_file, 'r', encoding='utf-8') as f:
                scores = json.load(f)
            
            avg_score = 0.0
            score_format_used = None
            
            if isinstance(scores, list) and len(scores) > 0:
                # Try different field names for the score
                total_scores = []
                for s in scores:
                    if isinstance(s, dict):
                        # Try multiple field names in order of preference
                        score_val = None
                        
                        # Try 'final_score' first (common in Assignment 2)
                        if 'final_score' in s:
                            score_val = s.get('final_score')
                            if score_val is not None:
                                score_format_used = "final_score"
                        
                        # Try 'total' 
                        if score_val is None and 'total' in s:
                            score_val = s.get('total')
                            if score_val is not None:
                                score_format_used = "total"
                        
                        # Try 'total_score'
                        if score_val is None and 'total_score' in s:
                            score_val = s.get('total_score')
                            if score_val is not None:
                                score_format_used = "total_score"
                        
                        # Try calculating from nested 'scores' dict
                        if score_val is None and 'scores' in s:
                            nested = s.get('scores', {})
                            if isinstance(nested, dict):
                                # First check if 'total' exists in nested scores
                                if 'total' in nested:
                                    score_val = nested.get('total')
                                    score_format_used = "scores.total"
                                else:
                                    # Sum individual score components (exclude 'total' if it exists)
                                    score_val = sum(v for k, v in nested.items() 
                                                   if isinstance(v, (int, float)) and k != 'total')
                                    if score_val is not None and score_val > 0:
                                        score_format_used = "scores (sum)"
                        
                        # Try 'score' field
                        if score_val is None and 'score' in s:
                            score_val = s.get('score')
                            if score_val is not None:
                                score_format_used = "score"
                        
                        # Try 'score_breakdown' - might contain total
                        if score_val is None and 'score_breakdown' in s:
                            breakdown = s.get('score_breakdown', {})
                            if isinstance(breakdown, dict) and 'total' in breakdown:
                                score_val = breakdown.get('total')
                                score_format_used = "score_breakdown.total"
                        
                        # Try 'rubricScore' with nested 'totalScore' (like Theodore Wu's format)
                        if score_val is None and 'rubricScore' in s:
                            rubric = s.get('rubricScore', {})
                            if isinstance(rubric, dict) and 'totalScore' in rubric:
                                score_val = rubric.get('totalScore')
                                score_format_used = "rubricScore.totalScore"
                        
                        # Try 'scores' dict within list entry (like Juli Huang's format)
                        if score_val is None and 'scores' in s:
                            nested_scores = s.get('scores', {})
                            if isinstance(nested_scores, dict):
                                # Check for total in nested scores
                                if 'total' in nested_scores:
                                    score_val = nested_scores.get('total')
                                    score_format_used = "scores.total (nested)"
                                elif 'total_score' in nested_scores:
                                    score_val = nested_scores.get('total_score')
                                    score_format_used = "scores.total_score (nested)"
                        
                        # Accept score even if 0 (might be valid)
                        if isinstance(score_val, (int, float)):
                            total_scores.append(float(score_val))
                
                if total_scores:
                    avg_score = sum(total_scores) / len(total_scores)
                    if score_format_used:
                        result['notes'].append(f"Score format: {score_format_used}, {len(total_scores)} entries")
            
            elif isinstance(scores, dict):
                # Try different dict formats
                # First check if it's a dict with case IDs as keys (like Ray Du's format)
                # If values are dicts with 'total_score', extract from those
                first_value = next(iter(scores.values())) if scores else None
                if isinstance(first_value, dict) and 'total_score' in first_value:
                    # This is a dict with case IDs as keys, values contain total_score
                    total_scores = []
                    for case_id, case_data in scores.items():
                        if isinstance(case_data, dict):
                            score_val = case_data.get('total_score') or case_data.get('total') or case_data.get('final_score')
                            if isinstance(score_val, (int, float)):
                                total_scores.append(float(score_val))
                    if total_scores:
                        avg_score = sum(total_scores) / len(total_scores)
                        score_format_used = "dict (case_id keys)"
                        result['notes'].append(f"Score format: {score_format_used}, {len(total_scores)} entries")
                elif 'average_score' in scores:
                    avg_score = scores.get('average_score', 0.0)
                    score_format_used = "average_score"
                elif 'avg_score' in scores:
                    avg_score = scores.get('avg_score', 0.0)
                    score_format_used = "avg_score"
                elif 'mean_score' in scores:
                    avg_score = scores.get('mean_score', 0.0)
                    score_format_used = "mean_score"
                elif 'cases' in scores:
                    # Extract from cases array (like Sreya Vangara's format)
                    cases = scores.get('cases', [])
                    if isinstance(cases, list):
                        total_scores = []
                        for case in cases:
                            if isinstance(case, dict):
                                score_val = case.get('final_score') or case.get('total') or case.get('total_score') or case.get('score')
                                if isinstance(score_val, (int, float)):
                                    total_scores.append(float(score_val))
                        if total_scores:
                            avg_score = sum(total_scores) / len(total_scores)
                            score_format_used = "cases"
                elif 'case_scores' in scores:
                    # Extract from case_scores (like Alessandro Balzi's or Mingyang Wang's format)
                    case_scores = scores.get('case_scores', [])
                    if isinstance(case_scores, list):
                        total_scores = []
                        for cs in case_scores:
                            if isinstance(cs, dict):
                                # Try direct fields
                                score_val = cs.get('final_score') or cs.get('total') or cs.get('total_score') or cs.get('score')
                                # Try nested 'scores' dict
                                if score_val is None and 'scores' in cs:
                                    nested = cs.get('scores', {})
                                    if isinstance(nested, dict):
                                        score_val = nested.get('total') or nested.get('total_score')
                                if isinstance(score_val, (int, float)):
                                    total_scores.append(float(score_val))
                        if total_scores:
                            avg_score = sum(total_scores) / len(total_scores)
                            score_format_used = "case_scores"
                elif 'scores' in scores:
                    # Extract from scores array (like Fernando Torres Navarrete's or Juli Huang's format)
                    scores_list = scores.get('scores', [])
                    if isinstance(scores_list, list):
                        total_scores = []
                        for s in scores_list:
                            if isinstance(s, dict):
                                # Try direct fields first
                                score_val = s.get('final_score') or s.get('total') or s.get('total_score') or s.get('score')
                                # If not found, check nested 'scores' dict
                                if score_val is None and 'scores' in s:
                                    nested = s.get('scores', {})
                                    if isinstance(nested, dict):
                                        score_val = nested.get('total') or nested.get('total_score')
                                if isinstance(score_val, (int, float)):
                                    total_scores.append(float(score_val))
                        if total_scores:
                            avg_score = sum(total_scores) / len(total_scores)
                            score_format_used = "scores (array)"
                elif 'scored_cases' in scores:
                    # Extract from scored_cases (like April Yang's format)
                    scored_cases = scores.get('scored_cases', [])
                    if isinstance(scored_cases, list):
                        total_scores = []
                        for sc in scored_cases:
                            if isinstance(sc, dict):
                                score_val = sc.get('final_score') or sc.get('total') or sc.get('total_score') or sc.get('score')
                                if isinstance(score_val, (int, float)):
                                    total_scores.append(float(score_val))
                        if total_scores:
                            avg_score = sum(total_scores) / len(total_scores)
                            score_format_used = "scored_cases"
                elif 'results' in scores:
                    # Extract from results (like Mason Hu's format)
                    results = scores.get('results', [])
                    if isinstance(results, list):
                        total_scores = []
                        for r in results:
                            if isinstance(r, dict):
                                score_val = r.get('final_score') or r.get('total') or r.get('total_score') or r.get('score')
                                if isinstance(score_val, (int, float)):
                                    total_scores.append(float(score_val))
                        if total_scores:
                            avg_score = sum(total_scores) / len(total_scores)
                            score_format_used = "results"
                elif 'detailed_scores' in scores:
                    # Extract from detailed_scores array
                    detailed = scores.get('detailed_scores', [])
                    if isinstance(detailed, list):
                        total_scores = []
                        for ds in detailed:
                            if isinstance(ds, dict):
                                score_val = ds.get('final_score') or ds.get('total') or ds.get('total_score') or ds.get('score')
                                if isinstance(score_val, (int, float)):
                                    total_scores.append(float(score_val))
                        if total_scores:
                            avg_score = sum(total_scores) / len(total_scores)
                            score_format_used = "detailed_scores"
                
                if score_format_used:
                    result['notes'].append(f"Score format: {score_format_used}")
            
            if avg_score >= 0:  # Accept 0 as valid
                result['validatee_score'] = avg_score / 10.0  # Normalize to 0-1
                if avg_score == 0:
                    result['notes'].append(f"Average score is 0 (all cases scored 0)")
            else:
                result['validatee_score'] = 0.0
                result['notes'].append("Could not extract scores from file")
                
        except Exception as e:
            result['notes'].append(f"Warning: Could not read score file for validatee_score: {e}")
            result['validatee_score'] = 0.0
    else:
        result['validatee_score'] = 0.0
    
    # Calculate final score (includes validator scores)
    # Note: score_from_validators is normalized 0-1, so we add it directly
    result['final_score'] = (
        result['dataset_completeness'] +
        result['fields'] +
        result['pearl_distribution'] +
        result['label_distribution'] +
        result['labeling_content'] +
        result['schema_correct'] +
        result['score_correct'] +
        result['score_from_validators'] +  # Already normalized 0-1
        result['bonus']
    )
    
    return result

def main():
    """Main grading function."""
    # Paths
    base_dir = Path(__file__).parent
    submissions_dir = base_dir
    metadata_file = base_dir / "submission_metadata.yml"
    cross_val_file = Path(__file__).parent.parent / "assignment2" / "cross_validation_assignment.csv"
    output_file = base_dir / "assignment2.csv"
    
    print("="*80)
    print("ASSIGNMENT 2 GRADING SCRIPT")
    print("="*80)
    
    # Load metadata
    print("\nLoading metadata...")
    metadata = load_metadata(metadata_file)
    print(f"Found {len(metadata)} submissions in metadata")
    
    # Load cross-validation data
    print("\nLoading cross-validation assignments...")
    if cross_val_file.exists():
        validator_avg_scores, validatee_lists, validatee_avg_scores = calculate_validator_scores(submissions_dir, cross_val_file, metadata)
    else:
        print(f"Cross-validation file not found at {cross_val_file}. Using empty validator scores.")
        validator_avg_scores = {}
        validatee_lists = {}
        validatee_avg_scores = {}
    
    # Grade each submission
    print("\nGrading submissions...")
    results = []
    
    for submission_id, meta in metadata.items():
        submission_dir = submissions_dir / submission_id
        # If directory doesn't exist, check if there's a JSON file with this submission_id
        if not submission_dir.exists():
            # Look for JSON file with this submission_id in the name
            json_file = None
            for file in submissions_dir.glob(f"{submission_id}*.json"):
                json_file = file
                break
            
            if json_file:
                # Use the submissions_dir directly and pass the json_file path
                print(f"Grading {submission_id} (using JSON file: {json_file.name})...")
                result = grade_submission_from_file(submissions_dir, submission_id, meta, json_file)
            else:
                print(f"Warning: Directory or JSON file not found for {submission_id}")
                continue
        else:
            print(f"Grading {submission_id}...")
            result = grade_submission(submission_dir, submission_id, meta)
        
        # Add validator scores (scores received from others)
        email = result['email']
        result['score_from_validators'] = validator_avg_scores.get(email, 0.0)
        
        results.append(result)
    
    # Write results to CSV
    print(f"\nWriting results to {output_file}...")
    fieldnames = [
        'submission_id', 'name', 'sid', 'email',
        'dataset_completeness', 'fields', 'pearl_distribution', 'label_distribution',
        'labeling_content', 'schema_correct', 'score_correct', 'score_from_validators',
        'bonus', 'final_score', 'validatees', 'validatee_score', 'notes'
    ]
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {k: result.get(k, '') for k in fieldnames}
            # Convert notes list to string
            if isinstance(row['notes'], list):
                row['notes'] = '; '.join(row['notes'])
            writer.writerow(row)
    
    print(f"\n✓ Grading complete! Results written to {output_file}")
    print(f"Total submissions graded: {len(results)}")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    avg_final = sum(r['final_score'] for r in results) / len(results) if results else 0
    print(f"Average final score: {avg_final:.2f}/10.0")
    print(f"Submissions with bonus: {sum(1 for r in results if r['bonus'] > 0)}")

if __name__ == "__main__":
    main()

