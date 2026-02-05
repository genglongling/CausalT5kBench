# CausalT5K: Diagnosing Sycophancy, Rung Collapse, and Informed Refusal for Trustworthy Causal Reasoning

## Overview

CausalT5K is a comprehensive benchmark dataset designed to evaluate and diagnose critical failure modes in large language models' causal reasoning capabilities. This dataset focuses on three key diagnostic dimensions:

1. **Sycophancy**: The tendency of models to agree with user claims even when they are causally invalid
2. **Rung Collapse**: The failure to properly distinguish between Pearl's three levels of causal reasoning (Association, Intervention, Counterfactual)
3. **Informed Refusal**: The ability to appropriately refuse to answer when causal claims cannot be reliably evaluated

## Dataset Structure

The dataset contains over 5,000 causal reasoning cases organized across multiple dimensions:

### Pearl Hierarchy Levels
- **L1 (Association)**: Observational data and correlations
- **L2 (Intervention)**: Causal effects under interventions
- **L3 (Counterfactual)**: Counterfactual reasoning about what would have happened

### Causal Traps
The dataset includes various causal reasoning pitfalls:
- **Confounding** (C): Omitted variables, common causes
- **Selection Bias** (W1): Availability, media narrative, survivorship bias
- **Mediation** (M): Intermediate variables
- **Ecological Fallacy** (W5): Aggregate to individual inference errors
- **Regression to Mean** (W4): Statistical artifacts
- And many more...

### Dataset Organization

- **`validated_dataset(round=1)/`**: Contains validated datasets from the first validation round
- **`unvalidated_dataset/`**: Contains unvalidated submissions organized by contributor groups

### Data Format

Each case in the dataset includes:

```json
{
  "id": "unique_case_id",
  "case_id": "case_identifier",
  "bucket": "bucket_name",
  "pearl_level": "L1|L2|L3",
  "domain": "domain_name",
  "subdomain": "subdomain_name",
  "trap": {
    "type": "trap_code",
    "type_name": "Trap Name",
    "subtype": "subtype_code",
    "subtype_name": "Subtype Name"
  },
  "difficulty": "Easy|Medium|Hard",
  "scenario": "Description of the causal scenario",
  "claim": "Causal claim to evaluate",
  "label": "YES|NO",
  "is_ambiguous": false,
  "variables": {
    "X": "Variable X description",
    "Y": "Variable Y description",
    "Z": ["Confounding variables"]
  },
  "causal_structure": "Description of causal relationships",
  "key_insight": "Key insight about the causal trap",
  "hidden_timestamp": "Temporal information if relevant",
  "conditional_answers": {
    "answer_if_condition_1": "...",
    "answer_if_condition_2": "..."
  },
  "wise_refusal": "Appropriate refusal response",
  "gold_rationale": "Correct explanation",
  "initial_author": "Author name",
  "validator": "Validator name",
  "final_score": 8.5
}
```

## Key Features

### 1. Sycophancy Detection
Cases are designed to test whether models will:
- Agree with user claims that are causally invalid
- Maintain correct causal reasoning despite user framing
- Distinguish between correlation and causation

### 2. Rung Collapse Diagnosis
The dataset systematically tests:
- Whether models can distinguish L1 (association) from L2 (intervention) reasoning
- Whether models collapse counterfactual (L3) reasoning to lower levels
- Appropriate use of causal language at each Pearl level

### 3. Informed Refusal Evaluation
Cases include scenarios where:
- Causal claims cannot be reliably evaluated from available information
- Models should refuse rather than guess
- Appropriate refusal responses are provided as ground truth

## Usage

### Loading the Dataset

The validated datasets are available in JSON format in the `validated_dataset(round=1)/` directory. Each file contains an array of causal reasoning cases.

### Evaluation Metrics

When evaluating models on CausalT5K, consider:

1. **Accuracy**: Overall correctness on YES/NO labels
2. **Sycophancy Rate**: Agreement with invalid user claims
3. **Rung Accuracy**: Performance breakdown by Pearl level (L1/L2/L3)
4. **Refusal Quality**: Whether models appropriately refuse when they should
5. **Trap-Specific Performance**: Accuracy across different causal trap types

## Citation

If you use CausalT5K in your research, please cite:

```bibtex
@article{causalt5k2024,
  title={CausalT5K: Diagnosing Sycophancy, Rung Collapse, and Informed Refusal for Trustworthy Causal Reasoning},
  author={...},
  journal={...},
  year={2024}
}
```

## Dataset Statistics

- **Total Cases**: 5,000+
- **Pearl Level Distribution**: 
  - L1 (Association): ~10%
  - L2 (Intervention): ~60%
  - L3 (Counterfactual): ~30%
- **Domains**: Sports, Healthcare, Economics, Environment, Technology, and more
- **Validation**: Multi-round validation process with expert review

## Contributing

This dataset was created through a collaborative effort. Contributors are organized by groups (A-J), and each submission has been validated for quality and correctness.

## License

[Specify license here]

## Contact

For questions or issues related to the dataset, please [specify contact information].

## Acknowledgments

We thank all contributors and validators who helped create and validate this comprehensive causal reasoning benchmark.
