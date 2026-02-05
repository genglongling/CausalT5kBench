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
  author={Geng, Longling and Ouyang, Andy and Wu, Theodore and Cooper, Rachael and Zeng, Yuqiao and Hayes, Matthew John and Barretto, Daphne and Vijay, Sameer and Ancone, Gia and Rai, Ankit and Wolfman, Matthew and Flanagan, Patrick and Chang, Edward Y},
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

We thank the following contributors for their work on CausalT5K development.

### Contributors Table

| Name | Major | Level | Generation Domains | Generation Cases Number | Generation Cases ID | Validation Domains | Validation Cases Number | Validation Cases ID |
|------|-------|-------|-------------------|----------------------|-------------------|------------------|----------------------|-------------------|
| Longling Geng | [To be filled] | [To be filled] | - | 0 | N/A | - | 0 | N/A |
| Andy Ouyang | [To be filled] | [To be filled] | Law & Ethics | 165 | T3-BucketLarge-C-7.1-NC1-T3-BucketLarge-C-7171 | Law & Ethics | 171 | T3-BucketLarge-C-7001-T3-BucketLarge-C-7171 |
| Theodore Wu | [To be filled] | [To be filled] | Markets | 288 | G.2-G.10 | Markets | 34 | T3-BucketLarge-G.1-T3-BucketLarge-G.9 |
| Rachael Yaran Cooper | [To be filled] | [To be filled] | Daily Life | 52 | T3-BucketLarge-E-129-T3-BucketLarge-E-180 | Daily Life | 189 | T3-BucketLarge-E-1.100-T3-BucketLarge-E-186 |
| Yuqiao Zeng | [To be filled] | [To be filled] | Arts, Business, Computer Science, D9, Education, Finance, Health, Public Policy, Science, Sports | 177 | T3-BucketD-0001-T3-BucketLarge-D-9.316 | D9, Sports | 217 | T3-BucketLarge-D-9.100-T3-BucketLarge-D-9.316 |
| Matthew John Hayes | [To be filled] | [To be filled] | Law & Ethics | 412 | T3-BucketLarge-C-7.mhgen.A.1-T3-BucketLarge-C-7085 | Law & Ethics | 406 | T3-BucketLarge-C-7.1-NC1-T3-BucketLarge-C-7.mhgen.W9.4 |
| Daphne Barretto | [To be filled] | [To be filled] | D10 (Social Science), Medicine | 250 | T3-BucketA-0001-T3-BucketJ-81 | D10 (Social Science), Medicine | 170 | T3-BucketJ-01-T3-BucketLarge-A-4.9-P1-2 |
| Sameer Vijay | [To be filled] | [To be filled] | History | 260 | T3-BucketF-0001-T3-F.99 | D2, History | 200 | T3-BucketLarge-F-181-T3-F.99 |
| Gia Ancone | [To be filled] | [To be filled] | Medicine, Social Science | 407 | T3-BucketLarge-A-4.1-P1-1-T3-BucketLarge-J-A2.1.210 | Medicine, Social Science | 525 | T3-BucketA-0001-T3-BucketLarge-J-A2.1.9 |
| Ankit Rai | [To be filled] | [To be filled] | Medicine | 158 | T3-BucketLarge-A-4.1-P2-1-T3-BucketLarge-A-A2.1.99 | Medicine | 323 | T3-BucketLarge-A-4.1-P1-1-T3-BucketLarge-A-4.9-P3-2-R4 |
| Matthew Wolfman | [To be filled] | [To be filled] | D9, Sports | 200 | T3-BucketLarge-D-9.100-T3-BucketLarge-D9-9.542 | D9 | 200 | T3-BucketLarge-D9-9.100-T3-BucketLarge-D9-9.542 |
| Patrick Flanagan | [To be filled] | [To be filled] | - | 0 | N/A | - | 0 | N/A |
| Edward Y Chang | [To be filled] | [To be filled] | - | 0 | N/A | - | 0 | N/A |
| Alanood Alrassan | [To be filled] | [To be filled] | - | 0 | N/A | D8 - AI Safety & Alignment | 400 | T3-BucketI-L1-001-T3-BucketI-L3-120 |
| Alessandro Balzi | [To be filled] | [To be filled] | AI & Tech | 184 | T3-BucketLarge-I-L1-006-T3-BucketLarge-I-L3-060 | AI & Tech | 200 | T3-BucketLarge-I-L1-001-T3-BucketLarge-I-L3-060 |
| April Yang | [To be filled] | [To be filled] | D2, History | 80 | T3-F.1-T3-F.9 | - | 0 | N/A |
| Arya Marwaha | [To be filled] | [To be filled] | AI & Tech, Daily Life | 118 | T3-A2-001-T3-BucketLarge-I-L3-003 | Daily Life | 102 | T3-A2-001-T3-A2-102 |
| Atanu Mukherjee | [To be filled] | [To be filled] | Various | 315 | T3-BucketLarge-B-5.116-T3-BucketLarge-B-D5-L3-topup-24 | Various | 200 | T3-BucketLarge-B-5.116-T3-BucketLarge-B-D5-L3-topup-24 |
| Chenyang Dai | [To be filled] | [To be filled] | Daily Life | 337 | T3-BucketLarge-E-1.001-T3-BucketLarge-E-2.125 | Daily Life | 212 | T3-BucketLarge-E-1.001-T3-BucketLarge-E-1.212 |
| Chinmay Pimpalkhare | [To be filled] | [To be filled] | Daily Life | 256 | T3-BucketLarge-E-1.100-T3-BucketLarge-E-1.99 | Daily Life | 230 | T3-BucketLarge-E-1.1-T3-BucketLarge-E-1.99 |
| Chris Philip James Pearce | [To be filled] | [To be filled] | Economics | 219 | T3-BucketLarge-B-1.10-T3-BucketLarge-B-5.479 | Economics | 218 | T3-BucketLarge-B-1.10-T3-BucketLarge-B-6.85 |
| Deveen Manitha Harischandra | [To be filled] | [To be filled] | Markets | 79 | T3-BucketLarge-G-genL1-0001-T3-BucketLarge-G.9 | Markets | 160 | T3-BucketLarge-G-genL1-0001-T3-BucketLarge-G-lgren007-0115 |
| Fernando Torres Navarrete | [To be filled] | [To be filled] | D8 - AI Safety & Alignment | 400 | T3-BucketI-L1-001-T3-BucketI-L3-120 | - | 0 | N/A |
| Jordan Zhang | [To be filled] | [To be filled] | Medicine | 558 | T3-BucketA-0001-T3-BucketLarge-A-4.9-P3-2-R3 | Medicine | 19 | T3-BucketA-0019-T3-BucketA-0227 |
| Juli Huang | [To be filled] | [To be filled] | Markets | 79 | G.10-G.10 | Markets | 220 | G.2-G.10 |
| Kelvin Christian | [To be filled] | [To be filled] | Social Science | 230 | T3-BucketLarge-J-0046-T3-BucketLarge-J-0275 | - | 0 | N/A |
| Leiguang Ren | [To be filled] | [To be filled] | Markets | 115 | T3-BucketLarge-G-lgren007-0001-T3-BucketLarge-G-lgren007-0115 | - | 0 | N/A |
| Manolo Alvarez | [To be filled] | [To be filled] | D9, Sports | 172 | T3-BucketLarge-D-022f735f-T3-BucketLarge-D9-9.179 | Arts, Business, Education, Finance, Health | 200 | T3-BucketD-0047-T3-BucketLarge-D-f93e44bf |
| Mason Hu | [To be filled] | [To be filled] | Economics | 192 | T1-BucketSmall-A-5.372-T3-BucketLarge-B-8.00 | Economics | 194 | T1-BucketSmall-A-5.372-T3-BucketLarge-B-5.371 |
| Mingyang Wang | [To be filled] | [To be filled] | History | 30 | T3-BucketF-0151-T3-BucketF-0180 | History | 170 | T3-BucketF-0001-T3-BucketF-0180 |
| Mudit Baid | [To be filled] | [To be filled] | Medicine | 180 | T3-BucketLarge-A-4.1-P3-1-T3-BucketLarge-A-4.9-P3-2-R4 | Medicine | 360 | T3-BucketLarge-A-4.1-P1-1-T3-BucketLarge-A-4.9-P3-2 |
| Rebecca Joseph | [To be filled] | [To be filled] | Medicine | 79 | T3-BucketA-0231-T3-BucketLarge-A-new.3-P3-3 | Medicine | 243 | T3-BucketLarge-A-4.1-P1-1-T3-BucketLarge-A-new.3-P3-3 |
| Ryan He | [To be filled] | [To be filled] | Daily Life | 291 | T3-BucketLarge-E-1.1-T3-BucketLarge-E-186 | Daily Life | 177 | T3-BucketLarge-E-129-T3-BucketLarge-E-2.125 |
| Samantha Afra van Rijs | [To be filled] | [To be filled] | Agriculture, Arts, Business, Criminal Justice, Economics, Education, Finance, Health, Public Policy, Science | 251 | T3-BucketD-0041-T3-BucketLarge-D-0183 | Agriculture, Arts, Business, Computer Science, Criminal Justice, Education, Finance, Health, Public Policy, Science | 183 | T3-BucketD-0001-T3-BucketLarge-D-0183 |
| Sreya Vangara | [To be filled] | [To be filled] | D10 (Social Science), Social Science | 879 | T3-BucketJ-01-T3-BucketLarge-J-A2.1.9 | Social Science | 230 | T3-BucketLarge-J-0046-T3-BucketLarge-J-0275 |
| Veljko Skarich | [To be filled] | [To be filled] | Environment | 259 | T3-BucketH-0006-T3-BucketH-999 | Environment | 254 | T3-BucketH-1001-T3-BucketH-999 |
| Vivek Sathe | [To be filled] | [To be filled] | Economics | 188 | T3-BucketLarge-B-5.061-T3-BucketLarge-B-5.345 | Economics | 302 | T3-BucketLarge-B-5.061-T3-BucketLarge-B-8.00 |

### Dataset Summary by Domain

The following table summarizes the dataset quality scores organized by domain:

| Domain | Total Case Numbers | Case ID Range | Initial Author | Validator | Rule-based Score | Score from Other | LLM Score | Final Score |
|--------|-------------------|---------------|----------------|-----------|------------------|------------------|-----------|-------------|
| AI & Tech | 200 | T3-BucketLarge-I-L1-001-T3-BucketLarge-I-L3-060 | Alessandro Balzi, Arya Marwaha | Alessandro Balzi | 3.00 | N/A | 2.00 | 2.21 |
| Agriculture | 1 | T3-BucketD-0165 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Arts | 9 | T3-BucketD-0013-T3-BucketD-0164 | Samantha Afra van Rijs, Yuqiao Zeng | Manolo Alvarez, Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Business | 48 | T3-BucketD-0006-T3-BucketD-0169 | Samantha Afra van Rijs, Yuqiao Zeng | Manolo Alvarez, Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Climate | 4 | T3-BucketH-885-T3-BucketH-887 |  |  | N/A | N/A | N/A | N/A |
| Climate Science | 1 | T3-BucketH-884 |  |  | N/A | N/A | N/A | N/A |
| Computer Science | 2 | T3-BucketD-0022-T3-BucketD-0037 | Yuqiao Zeng | Samantha Afra van Rijs | 5.00 | 0.85 | 6.00 | 4.51 |
| Criminal Justice | 3 | T3-BucketD-0108-T3-BucketD-0136 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| D10 (Social Science) | 81 | T3-BucketJ-01-T3-BucketJ-81 | Daphne Barretto, Sreya Vangara | Daphne Barretto | 3.00 | N/A | 3.00 | 2.57 |
| D2 | 79 | T3-F.1-T3-F.9 | April Yang | Sameer Vijay | 2.00 | 0.70 | 1.50 | 2.19 |
| D8 - AI Safety & Alignment | 400 | T3-BucketI-L1-001-T3-BucketI-L3-120 | Fernando Torres Navarrete | Alanood | 4.00 | N/A | 4.50 | 3.61 |
| D9 | 339 | T3-BucketLarge-D-9.110-T3-BucketLarge-D9-9.542 | Manolo Alvarez, Matt Wolfman, Yuqiao Zeng | Matt Wolfman, Yuqiao Zeng | 4.33 | 0.86 | 5.00 | 4.07 |
| Daily Life | 910 | T3-A2-001-T3-BucketLarge-E-2.125 | Arya Marwaha, Chenyang Dai, Chinmay Pimpalkhare... | Arya Marwaha, Chenyang Dai, Chinmay Pimpalkhare... | 4.00 | 0.68 | 4.30 | 3.49 |
| Economics | 507 | T1-BucketSmall-A-5.372-T3-BucketLarge-B-8.00 | Chris Philip James Pearce, Mason Hu, Samantha Afra van Rijs... | Chris Philip James Pearce, Mason Hu, Samantha Afra van Rijs... | 3.75 | 0.74 | 4.00 | 3.44 |
| Education | 37 | T3-BucketD-0011-T3-BucketD-0164 | Samantha Afra van Rijs, Yuqiao Zeng | Manolo Alvarez, Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Employment | 2 | T3-BucketD-0061-T3-BucketD-0075 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Environment | 286 | T3-BucketD-0148-T3-BucketH-999 | Samantha Afra van Rijs, Veljko Skarich | NOT ASSIGNED, Samantha Afra van Rijs, Veljko Skarich | 3.00 | 0.41 | 3.00 | 2.40 |
| Environmental Science | 1 | T3-BucketD-0097 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Epidemiology | 1 | T3-BucketD-0091 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Ethics | 2 | T3-BucketD-0143-T3-BucketD-0157 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Finance | 11 | T3-BucketD-0007-T3-BucketD-0115 | Samantha Afra van Rijs, Yuqiao Zeng | Manolo Alvarez, Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Health | 3 | T3-BucketD-0019-T3-BucketD-0047 | Samantha Afra van Rijs, Yuqiao Zeng | Manolo Alvarez, Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Healthcare | 25 | T3-BucketD-0056-T3-BucketD-0152 | Samantha Afra van Rijs | Manolo Alvarez, Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| History | 291 | T3-BucketF-0001-T3-F.99 | April Yang, Mingyang Wang, Sameer Vijay | Mingyang Wang, Sameer Vijay | 3.00 | 0.87 | 3.50 | 3.29 |
| Law | 4 | T3-BucketD-0086-T3-BucketD-0172 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Law & Ethics | 577 | T3-BucketLarge-C-7.1-NC1-T3-BucketLarge-C-7171 | Andy Ouyang, Matthew John Hayes | Andy Ouyang, Matthew John Hayes | 5.00 | 0.91 | 6.00 | 4.62 |
| Legal | 1 | T3-BucketD-0109 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Markets | 576 | G.2-G.10 | deveen@stanford.edu, julih@stanford.edu, lgren007@stanford.edu... | Deveen Manitha Harischandra, deveen@stanford.edu, julih@stanford.edu... | N/A | 0.75 | N/A | 3.76 |
| Media | 1 | T3-BucketD-0053 | Samantha Afra van Rijs | Manolo Alvarez | 4.00 | N/A | 4.50 | 3.61 |
| Medicine | 1477 | T3-BucketA-0001-T3-BucketLarge-J-A2.1.210 | 4, A2, Ankit Rai... | Ankit Rai, Daphne Barretto, Gia Ancone... | 3.80 | 0.91 | 4.10 | 3.75 |
| Military | 1 | T3-BucketD-0149 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Philosophy | 1 | T3-BucketD-0154 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Physics | 2 | T3-BucketD-0139-T3-BucketD-0161 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Psychology | 22 | T3-BucketD-0052-T3-BucketD-0166 | Samantha Afra van Rijs | Manolo Alvarez, Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Public Health | 16 | T3-BucketD-0047-T3-BucketD-0173 | Samantha Afra van Rijs | Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Public Policy | 24 | T3-BucketD-0020-T3-BucketD-0166 | Samantha Afra van Rijs, Yuqiao Zeng | Manolo Alvarez, Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Science | 1 | T3-BucketD-0018 | Yuqiao Zeng | Samantha Afra van Rijs | 5.00 | 0.85 | 6.00 | 4.51 |
| Social Science | 325 | T3-BucketD-0062-T3-BucketLarge-J-A2.1.9 | Gia Ancone, Kelvin Christian, Samantha Afra van Rijs... | Gia Ancone, Samantha Afra van Rijs, Sreya Vangara | 3.50 | 0.75 | 3.75 | 3.31 |
| Sports | 206 | T3-BucketD-0001-T3-BucketLarge-D-f93e44bf | Manolo Alvarez, Matt Wolfman, Samantha Afra van Rijs... | Manolo Alvarez, Samantha Afra van Rijs, Yuqiao Zeng | 4.25 | 0.79 | 4.88 | 3.89 |
| Technology | 13 | T3-BucketD-0033-T3-BucketD-0174 | Samantha Afra van Rijs, Yuqiao Zeng | Samantha Afra van Rijs | 4.50 | 0.85 | 5.25 | 4.17 |
| Transportation | 3 | T3-BucketD-0054-T3-BucketD-0158 | Samantha Afra van Rijs | Manolo Alvarez, Samantha Afra van Rijs | 4.00 | N/A | 4.50 | 3.61 |
| Unknown | 413 | T3-BucketLarge-B-1.10-T3-BucketLarge-B-D5-L3-topup-24 | Atanu Mukherjee, Chris Philip James Pearce | Atanu Mukherjee, Chris Philip James Pearce | 3.00 | 0.92 | 2.50 | 3.13 |

**Score Definitions:**
- **Rule-based Score**: Average `final_score` from `assignment2.csv` (0-5 scale) for initial authors in this domain
- **Score from Other**: Average `validatee_score` from validators who validated cases in this domain (0-1 scale, normalized to 0-5 in final calculation)
- **LLM Score**: Average `final_score` from `assignment2_with_llm.csv` (0-7 scale, normalized to 0-5 in final calculation)
- **Final Score**: Average of the three scores above (all normalized to 0-5 scale)
