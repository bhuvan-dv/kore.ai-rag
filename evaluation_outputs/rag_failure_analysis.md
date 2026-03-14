# RAG Failure Analysis

## False Negative

- RET-04 (1. Ingestion, Chunking, and Retrieval Quality): score=4 | confidence=0.6337 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- RET-05 (1. Ingestion, Chunking, and Retrieval Quality): score=5 | confidence=0.6068 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, correct routing, 5 sources; primary issue: false negative.
- RET-10 (1. Ingestion, Chunking, and Retrieval Quality): score=4 | confidence=0.4216 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- AGT-02 (2. Agentic Orchestration and Query Decomposition): score=4 | confidence=0.4637 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, correct routing, 8 sources; primary issue: false negative.
- AGT-04 (2. Agentic Orchestration and Query Decomposition): score=4 | confidence=0.3854 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, correct routing, 3 sources; primary issue: false negative.
- CIT-01 (3. Source Selection, Citation Grounding, and Verification UX): score=4 | confidence=0.4655 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 3 sources; primary issue: false negative.
- CIT-03 (3. Source Selection, Citation Grounding, and Verification UX): score=4 | confidence=0.5905 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- CIT-06 (3. Source Selection, Citation Grounding, and Verification UX): score=3 | confidence=0.3919 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, acceptable routing, 3 sources; primary issue: false negative.
- CIT-07 (3. Source Selection, Citation Grounding, and Verification UX): score=4 | confidence=0.4554 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 6 sources; primary issue: false negative.
- HYB-04 (5. Multi-Source Reasoning and Tool Invocation): score=5 | confidence=0.5268 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, correct routing, 8 sources; primary issue: false negative.
- HYB-06 (5. Multi-Source Reasoning and Tool Invocation): score=5 | confidence=0.5683 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, correct routing, 8 sources; primary issue: false negative.
- UX-01 (6. UX, Reasoning Trace Visibility, and Demo Readiness): score=4 | confidence=0.4516 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- UX-02 (6. UX, Reasoning Trace Visibility, and Demo Readiness): score=5 | confidence=0.431 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, correct routing, 8 sources; primary issue: false negative.
- UX-03 (6. UX, Reasoning Trace Visibility, and Demo Readiness): score=4 | confidence=0.6017 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- ROB-04 (7. System Robustness, Failure Modes, and Adversarial Checks): score=4 | confidence=0.6139 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- ROB-05 (7. System Robustness, Failure Modes, and Adversarial Checks): score=3 | confidence=0.3388 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, acceptable routing, 6 sources; primary issue: false negative.
- ROB-08 (7. System Robustness, Failure Modes, and Adversarial Checks): score=3 | confidence=0.5471 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- ARC-01 (8. Architecture, Scalability, and Design-Defense Questions): score=4 | confidence=0.4225 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- ARC-02 (8. Architecture, Scalability, and Design-Defense Questions): score=3 | confidence=0.525 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.
- ARC-04 (8. Architecture, Scalability, and Design-Defense Questions): score=4 | confidence=0.4651 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: false negative.

## Tool Failure

- AGT-07 (2. Agentic Orchestration and Query Decomposition): score=2 | confidence=0.5553 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 8 sources; primary issue: tool failure.
- AGT-08 (2. Agentic Orchestration and Query Decomposition): score=7 | confidence=0.585 | Expected a unsupported outcome; got unsupported with strong grounding, well-calibrated calibration, wrong routing, 8 sources; primary issue: tool failure.
- CFG-03 (4. Confidence Scoring, Low-Confidence Fallback, and Hallucination Prevention): score=2 | confidence=0.5164 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: tool failure.
- CFG-04 (4. Confidence Scoring, Low-Confidence Fallback, and Hallucination Prevention): score=7 | confidence=0.6851 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- HYB-03 (5. Multi-Source Reasoning and Tool Invocation): score=6 | confidence=0.6788 | Expected a supported outcome; got correct with medium grounding, well-calibrated calibration, wrong routing, 3 sources; primary issue: tool failure.
- ROB-03 (7. System Robustness, Failure Modes, and Adversarial Checks): score=7 | confidence=0.6359 | Expected a unsupported outcome; got unsupported with strong grounding, well-calibrated calibration, wrong routing, 8 sources; primary issue: tool failure.
- FP-03 (False Positive): score=0 | confidence=0.6807 | Expected a unsupported outcome; got incorrect with strong grounding, overconfident calibration, wrong routing, 8 sources; primary issue: tool failure.
- FP-11 (False Positive): score=6 | confidence=0.5645 | Expected a unsupported outcome; got unsupported with medium grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- FP-12 (False Positive): score=2 | confidence=0.7344 | Expected a unsupported outcome; got unsupported with medium grounding, overconfident calibration, wrong routing, 3 sources; primary issue: tool failure.
- FN-08 (False Negative): score=7 | confidence=0.667 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- FN-09 (False Negative): score=1 | confidence=0.4534 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, wrong routing, 5 sources; primary issue: tool failure.
- PAIR-03A (Near-Neighbor Pair): score=7 | confidence=0.6851 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- PAIR-03B (Near-Neighbor Pair): score=0 | confidence=0.6643 | Expected a unsupported outcome; got incorrect with strong grounding, overconfident calibration, wrong routing, 3 sources; primary issue: tool failure.
- PAIR-07A (Near-Neighbor Pair): score=0 | confidence=0.3636 | Expected a supported outcome; got partial with none grounding, underconfident calibration, wrong routing, 5 sources; primary issue: tool failure.
- PAIR-07B (Near-Neighbor Pair): score=7 | confidence=0.5178 | Expected a unsupported outcome; got unsupported with strong grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- CAL-03 (Confidence Calibration): score=7 | confidence=0.7618 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 3 sources; primary issue: tool failure.
- CAL-07 (Confidence Calibration): score=6 | confidence=0.5941 | Expected a unsupported outcome; got unsupported with medium grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- CAL-09 (Confidence Calibration): score=6 | confidence=0.5472 | Expected a unsupported outcome; got unsupported with medium grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: tool failure.
- CAL-12 (Confidence Calibration): score=2 | confidence=0.4037 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: tool failure.
- GRD-03 (Citation / Grounding): score=7 | confidence=0.6968 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 8 sources; primary issue: tool failure.

## Misclassification

- RET-03 (1. Ingestion, Chunking, and Retrieval Quality): score=7 | confidence=0.6976 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: misclassification.
- CIT-08 (3. Source Selection, Citation Grounding, and Verification UX): score=0 | confidence=0.3875 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- CFG-08 (4. Confidence Scoring, Low-Confidence Fallback, and Hallucination Prevention): score=2 | confidence=0.3736 | Expected a unsupported outcome; got unsupported with none grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: misclassification.
- UX-06 (6. UX, Reasoning Trace Visibility, and Demo Readiness): score=2 | confidence=0.5089 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- ROB-01 (7. System Robustness, Failure Modes, and Adversarial Checks): score=4 | confidence=0.2782 | Expected a unsupported outcome; got unsupported with weak grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: misclassification.
- FN-03 (False Negative): score=7 | confidence=0.7016 | Expected a supported outcome; got correct with strong grounding, well-calibrated calibration, wrong routing, 5 sources; primary issue: misclassification.
- FN-11 (False Negative): score=2 | confidence=0.4946 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- PAIR-05A (Near-Neighbor Pair): score=2 | confidence=0.4374 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- PAIR-06A (Near-Neighbor Pair): score=0 | confidence=0.2331 | Expected a supported outcome; got partial with none grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- CAL-06 (Confidence Calibration): score=2 | confidence=0.6434 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- GRD-06 (Citation / Grounding): score=1 | confidence=0.4875 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- GRD-09 (Citation / Grounding): score=2 | confidence=0.4093 | Expected a supported outcome; got partial with strong grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- RTE-08 (Routing): score=1 | confidence=0.5816 | Expected a supported outcome; got partial with medium grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.

## Weak Retrieval

- AGT-03 (2. Agentic Orchestration and Query Decomposition): score=2 | confidence=0.3803 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, correct routing, 8 sources; primary issue: weak retrieval.
- CIT-04 (3. Source Selection, Citation Grounding, and Verification UX): score=1 | confidence=0.3471 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- CIT-05 (3. Source Selection, Citation Grounding, and Verification UX): score=0 | confidence=0.4485 | Expected a supported outcome; got partial with none grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- UX-04 (6. UX, Reasoning Trace Visibility, and Demo Readiness): score=1 | confidence=0.5824 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- ARC-03 (8. Architecture, Scalability, and Design-Defense Questions): score=0 | confidence=0.3704 | Expected a supported outcome; got partial with none grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- ARC-05 (8. Architecture, Scalability, and Design-Defense Questions): score=1 | confidence=0.5273 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- FN-10 (False Negative): score=0 | confidence=0.4938 | Expected a supported outcome; got partial with none grounding, underconfident calibration, correct routing, 6 sources; primary issue: weak retrieval.
- PAIR-02A (Near-Neighbor Pair): score=0 | confidence=0.4686 | Expected a supported outcome; got partial with none grounding, underconfident calibration, correct routing, 5 sources; primary issue: weak retrieval.
- GRD-04 (Citation / Grounding): score=1 | confidence=0.4586 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, acceptable routing, 7 sources; primary issue: weak retrieval.
- RTE-09 (Routing): score=1 | confidence=0.558 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- RTE-10 (Routing): score=2 | confidence=0.4579 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, correct routing, 8 sources; primary issue: weak retrieval.

## Confidence Miscalibration

- RET-08 (1. Ingestion, Chunking, and Retrieval Quality): score=5 | confidence=0.6805 | Expected a unsupported outcome; got unsupported with strong grounding, overconfident calibration, acceptable routing, 7 sources; primary issue: confidence miscalibration.
- ROB-06 (7. System Robustness, Failure Modes, and Adversarial Checks): score=0 | confidence=0.7145 | Expected a unsupported outcome; got incorrect with medium grounding, overconfident calibration, acceptable routing, 8 sources; primary issue: confidence miscalibration.
- FP-06 (False Positive): score=6 | confidence=0.7374 | Expected a unsupported outcome; got unsupported with strong grounding, overconfident calibration, correct routing, 3 sources; primary issue: confidence miscalibration.
- FP-07 (False Positive): score=6 | confidence=0.7108 | Expected a unsupported outcome; got unsupported with strong grounding, overconfident calibration, correct routing, 8 sources; primary issue: confidence miscalibration.
- FP-08 (False Positive): score=6 | confidence=0.6946 | Expected a unsupported outcome; got unsupported with strong grounding, overconfident calibration, correct routing, 8 sources; primary issue: confidence miscalibration.
- PAIR-01B (Near-Neighbor Pair): score=5 | confidence=0.7369 | Expected a unsupported outcome; got unsupported with strong grounding, overconfident calibration, acceptable routing, 8 sources; primary issue: confidence miscalibration.

## Citation Drift

- FP-01 (False Positive): score=6 | confidence=0.5611 | Expected a unsupported outcome; got unsupported with weak grounding, well-calibrated calibration, acceptable routing, 8 sources; primary issue: citation drift.
- FP-10 (False Positive): score=7 | confidence=0.4036 | Expected a unsupported outcome; got unsupported with weak grounding, well-calibrated calibration, correct routing, 8 sources; primary issue: citation drift.

## Hallucination

- PAIR-06B (Near-Neighbor Pair): score=0 | confidence=0.6686 | Expected a unsupported outcome; got incorrect with weak grounding, overconfident calibration, acceptable routing, 3 sources; primary issue: hallucination.
