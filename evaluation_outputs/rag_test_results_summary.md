# RAG Evaluation Summary

- Total test count: 143
- Pass count: 71
- Partial count: 68
- Fail count: 4
- Error count: 0
- False positive count: 1
- False negative count: 52

## Common Failure Themes

- False Negative
- Tool Failure
- Misclassification
- Weak Retrieval
- Confidence Miscalibration
- Citation Drift
- Hallucination

## Best Categories

- 5. Multi-Source Reasoning and Tool Invocation: 7.67
- 1. Ingestion, Chunking, and Retrieval Quality: 7.2
- False Positive: 6.73
- Confidence Calibration: 6.73
- 4. Confidence Scoring, Low-Confidence Fallback, and Hallucination Prevention: 6.62

## Worst Categories

- Near-Neighbor Pair: 4.38
- 6. UX, Reasoning Trace Visibility, and Demo Readiness: 4.17
- Routing: 4.1
- 3. Source Selection, Citation Grounding, and Verification UX: 3.25
- 8. Architecture, Scalability, and Design-Defense Questions: 2.88

## Top 10 Critical Issues

- CIT-05 (3. Source Selection, Citation Grounding, and Verification UX): Weak Retrieval | score=0 | Expected a supported outcome; got partial with none grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- CIT-08 (3. Source Selection, Citation Grounding, and Verification UX): Misclassification | score=0 | Expected a supported outcome; got partial with weak grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- ROB-06 (7. System Robustness, Failure Modes, and Adversarial Checks): Confidence Miscalibration | score=0 | Expected a unsupported outcome; got incorrect with medium grounding, overconfident calibration, acceptable routing, 8 sources; primary issue: confidence miscalibration.
- ARC-03 (8. Architecture, Scalability, and Design-Defense Questions): Weak Retrieval | score=0 | Expected a supported outcome; got partial with none grounding, underconfident calibration, acceptable routing, 8 sources; primary issue: weak retrieval.
- FP-03 (False Positive): Tool Failure | score=0 | Expected a unsupported outcome; got incorrect with strong grounding, overconfident calibration, wrong routing, 8 sources; primary issue: tool failure.
- FN-10 (False Negative): Weak Retrieval | score=0 | Expected a supported outcome; got partial with none grounding, underconfident calibration, correct routing, 6 sources; primary issue: weak retrieval.
- PAIR-02A (Near-Neighbor Pair): Weak Retrieval | score=0 | Expected a supported outcome; got partial with none grounding, underconfident calibration, correct routing, 5 sources; primary issue: weak retrieval.
- PAIR-03B (Near-Neighbor Pair): Tool Failure | score=0 | Expected a unsupported outcome; got incorrect with strong grounding, overconfident calibration, wrong routing, 3 sources; primary issue: tool failure.
- PAIR-06A (Near-Neighbor Pair): Misclassification | score=0 | Expected a supported outcome; got partial with none grounding, underconfident calibration, wrong routing, 5 sources; primary issue: misclassification.
- PAIR-06B (Near-Neighbor Pair): Hallucination | score=0 | Expected a unsupported outcome; got incorrect with weak grounding, overconfident calibration, acceptable routing, 3 sources; primary issue: hallucination.

## Final Verdict

Partially ready but recall-limited: the system misses too many answerable questions.
