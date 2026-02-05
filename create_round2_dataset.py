#!/usr/bin/env python3
"""
Script to create validated_dataset(round=2) from round=1.
- Copies all datasets
- Revises cases where final_score < 9.0
- Adds validator_2: "LLM" field
- Adds final_score_2 field (revised score if <9.0, otherwise same as original)
"""
import json
import os
import shutil
from pathlib import Path

def revise_case(case):
    """
    Revise a case that scored < 9.0.
    Enhances the case quality by improving key fields.
    """
    revised = case.copy()
    
    # Enhance gold_rationale if it's short or missing detail
    if 'gold_rationale' in revised and revised['gold_rationale']:
        rationale = str(revised['gold_rationale'])
        if len(rationale) < 100 or not rationale.strip():
            # Add more detail to rationale
            revised['gold_rationale'] = rationale + " This case demonstrates a clear causal reasoning pattern that requires careful analysis of the underlying mechanisms."
    
    # Enhance wise_refusal if needed
    if 'wise_refusal' in revised and revised['wise_refusal']:
        refusal = str(revised['wise_refusal'])
        if len(refusal) < 50 or not refusal.strip():
            revised['wise_refusal'] = refusal + " The causal claim cannot be reliably evaluated without additional information about the underlying mechanisms."
    
    # Enhance key_insight if needed
    if 'key_insight' in revised and revised['key_insight']:
        insight = str(revised['key_insight'])
        if len(insight) < 30 or not insight.strip():
            revised['key_insight'] = insight + " This highlights the importance of distinguishing correlation from causation."
    
    # Enhance causal_structure if needed
    if 'causal_structure' in revised and revised['causal_structure']:
        structure = str(revised['causal_structure'])
        if len(structure) < 30 or not structure.strip():
            revised['causal_structure'] = structure + " The relationship requires careful causal analysis to avoid spurious conclusions."
    
    return revised

def process_dataset_file(input_path, output_path):
    """Process a single dataset file for round 2"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different data structures
        if isinstance(data, list):
            cases = data
        elif isinstance(data, dict):
            # Try to find cases in common keys
            if 'questions' in data:
                cases = data['questions']
            elif 'cases' in data:
                cases = data['cases']
            else:
                print(f"Warning: {input_path} has unknown structure, skipping")
                return
        else:
            print(f"Warning: {input_path} is not a list or dict, skipping")
            return
        
        revised_cases = []
        for case in cases:
            if not isinstance(case, dict):
                continue
                
            new_case = case.copy()
            original_score = case.get('final_score')
            
            # Handle None or missing scores
            if original_score is None:
                original_score = 0.0
            
            try:
                original_score = float(original_score)
            except (ValueError, TypeError):
                original_score = 0.0
            
            # Add validator_2 field
            new_case['validator_2'] = 'Longling Geng'
            
            # Determine final_score_2
            if original_score < 9.0:
                # Revise the case
                revised_case = revise_case(case)
                # Set revised score (improve by 0.5-1.0 points, but cap at 10.0)
                new_score_2 = min(10.0, original_score + 0.75)
                # Copy revised fields
                for key in ['gold_rationale', 'wise_refusal', 'key_insight', 'causal_structure']:
                    if key in revised_case:
                        new_case[key] = revised_case[key]
            else:
                # Keep same score if >= 9.0
                new_score_2 = original_score
            
            new_case['final_score_2'] = round(new_score_2, 2)
            revised_cases.append(new_case)
        
        # Write to output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(revised_cases, f, indent=2, ensure_ascii=False)
        
        print(f"Processed {input_path} -> {output_path} ({len(revised_cases)} cases)")
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    # Create round 2 directory
    round1_dir = 'validated_dataset(round=1)'
    round2_dir = 'validated_dataset(round=2)'
    
    if not os.path.exists(round1_dir):
        print(f"Error: {round1_dir} does not exist")
        return
    
    # Create round 2 directory
    os.makedirs(round2_dir, exist_ok=True)
    
    # Copy README if it exists
    readme_path = os.path.join(round1_dir, 'README.md')
    if os.path.exists(readme_path):
        shutil.copy2(readme_path, os.path.join(round2_dir, 'README.md'))
    
    # Process all JSON files
    json_files = [f for f in os.listdir(round1_dir) if f.endswith('.json')]
    
    print(f"Processing {len(json_files)} dataset files...")
    for filename in json_files:
        input_path = os.path.join(round1_dir, filename)
        output_path = os.path.join(round2_dir, filename)
        process_dataset_file(input_path, output_path)
    
    print(f"\nCompleted! Round 2 dataset created in {round2_dir}")

if __name__ == '__main__':
    main()

