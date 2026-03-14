# False-Positive / False-Negative Evaluation Plan

Built from the requirements in [Candidate_Assignment.pdf](/Users/bhuvanraj/Downloads/Candidate_Assignment.pdf) and intentionally focused on failure discovery rather than broad coverage. This file is designed to complement, not repeat, [PROJECT_EVALUATION_QUESTION_BANK.md](/Users/bhuvanraj/Developer/kore.ai-rag/PROJECT_EVALUATION_QUESTION_BANK.md).

## How to Use This File

- Use Section A to catch unsupported or overconfident answers.
- Use Section B to catch missed answers the system should have handled.
- Use Section C to test precision vs recall with tightly related pairs.
- Use Sections D-F to isolate confidence, grounding, and routing mistakes.
- Mark each test as `Pass`, `Partial`, or `Fail` during live runs.

## A. False Positive Test Questions

Questions likely to trigger unsupported, weakly grounded, or hallucinated answers.

| Test ID | Exact question | Category | Why it matters | What failure would look like | What correct behavior should look like | Expected confidence | Expected handling mode | Main evaluation focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FP-01 | "What contractual penalties does Kore.ai impose if uptime drops below SLA?" | False Positive | Enterprise-sounding legal detail is likely absent from docs and should not be invented | The system fabricates SLA percentages, credits, or legal remedies | The system states the information is not supported by available sources and stays cautious | Low | Plain RAG | Precision |
| FP-02 | "What is Kore.ai's exact per-agent monthly price for Agent AI Voice?" | False Positive | Pricing hallucinations are a classic enterprise-RAG failure | A specific dollar amount appears without a supporting source | The system refuses to guess and offers only what the retrieved sources support | Low | Plain RAG | Precision |
| FP-03 | "Which undocumented admin API lets me bulk-delete all bots in one request?" | False Positive | Tests whether the system invents private/internal APIs | It returns a plausible endpoint and method | It says no grounded evidence was found and avoids fabricating API details | Low | Tool | Precision |
| FP-04 | "Does Kore.ai provide on-call support in the Europe-West region with a 15-minute incident response SLA?" | False Positive | Combines geography, support policy, and SLA detail outside likely corpus scope | It invents support tiers and region promises | It responds cautiously and avoids policy claims not grounded in sources | Low | Plain RAG | Precision |
| FP-05 | "What are the exact HIPAA deployment controls required before launching Kore.ai in a hospital?" | False Positive | Compliance questions often produce confident nonsense if not grounded | It outputs a checklist as if documented in the source corpus | It distinguishes between what the docs say and what is missing | Low | Agentic RAG | Precision |
| FP-06 | "Which Microsoft Teams rate limits apply specifically to Kore.ai bots?" | False Positive | Cross-system operational limits can tempt model interpolation | It blends Teams limits with Kore.ai docs without evidence | It clarifies that the answer is unsupported or partial | Low | Hybrid | Precision |
| FP-07 | "Can Kore.ai natively replace AWS Connect end to end without any third-party setup?" | False Positive | Overgeneralized architecture claims expose weak grounding | It asserts platform equivalence or replacement claims unsupported by docs | It carefully frames supported integrations versus unsupported equivalence claims | Low | Agentic RAG | Precision |
| FP-08 | "What is the migration path from Dialogflow CX to Kore.ai, step by step?" | False Positive | Similar domain, but likely outside indexed documentation | It manufactures a migration workflow | It acknowledges the gap and gives only source-backed adjacent info if any | Low | Agentic RAG | Precision |
| FP-09 | "List the private environment variables required by Kore.ai internal staging deployments." | False Positive | Tests whether internal-only implementation details are invented | It returns variable names that sound plausible | It says such deployment internals are not supported by sources | Low | Plain RAG | Precision |
| FP-10 | "What governance approval is required before enabling sentiment analysis for regulated insurance calls?" | False Positive | Domain/regulatory overlays often trigger overreach | It invents policy, workflow, or compliance approvals | It stays within evidence and notes missing governance specifics | Low | Agentic RAG | Precision |
| FP-11 | "What changed in the latest unreleased Kore.ai platform build?" | False Positive | Tests response to recency claims outside the dataset | It answers as if it knows unreleased features | It says available sources do not establish that | Low | Tool | Precision |
| FP-12 | "Which billing API endpoint can I use to pull real-time Kore.ai invoice data?" | False Positive | Forces the system to avoid fabricating capabilities because "API" is present | It returns an endpoint just because the query looks technical | It safely says no supported source/tool provides that endpoint | Low | Tool | Precision |
| FP-13 | "How many GPUs does Kore.ai allocate per enterprise tenant?" | False Positive | Infrastructure internals are likely absent but easy to bluff | It invents infrastructure architecture details | It declines to speculate and cites source limitations | Low | Plain RAG | Precision |
| FP-14 | "Does Kore.ai guarantee GDPR Article 28 addendum templates out of the box?" | False Positive | Legal/compliance guarantees require strict grounding | It gives a yes/no claim without evidence | It stays cautious and avoids legal guarantees | Low | Plain RAG | Precision |
| FP-15 | "Which exact competitors does Kore.ai beat on total cost of ownership according to official docs?" | False Positive | Market/competitive claims are often not in product docs | It makes up comparative claims | It says the available sources do not support a grounded comparison | Low | Plain RAG | Precision |

## B. False Negative Test Questions

Questions that should succeed from the project scope or available indexed sources, but might fail due to retrieval, routing, or chunking issues.

| Test ID | Exact question | Category | Why it matters | What failure would look like | What correct behavior should look like | Expected confidence | Expected handling mode | Main evaluation focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FN-01 | "How do I configure a Kore.ai widget theme?" | False Negative | A direct docs query should be easy if retrieval is healthy | The system says it cannot find enough information or cites unrelated pages | It retrieves the right widget-theming content and answers concretely | High | Plain RAG | Recall |
| FN-02 | "What steps are involved in creating a dialog from an utterance?" | False Negative | Tests whether procedural documentation is retrievable despite phrasing variation | It misses dialog creation and falls back cautiously | It finds the relevant procedural guidance | High | Plain RAG | Recall |
| FN-03 | "What channels are available for Kore.ai bots?" | False Negative | Core product capability question should be answerable | The system is vague or low-confidence despite available evidence | It returns a grounded channel-oriented answer | Medium | Hybrid | Recall |
| FN-04 | "What does the BotKit SDK help developers do?" | False Negative | GitHub README retrieval should work, not just docs pages | It ignores README content or cannot distinguish SDK purpose | It surfaces BotKit-specific capabilities from GitHub-origin sources | High | Plain RAG | Recall |
| FN-05 | "How does the Android Kore SDK fit into a mobile implementation?" | False Negative | Tests SDK-source retrieval and synthesis | It answers generically about mobile without SDK grounding | It points to Android SDK source material and summarizes its role | Medium | Plain RAG | Recall |
| FN-06 | "What prerequisites are listed for the Amazon Connect integration with Agent AI Voice?" | False Negative | Direct long-title niche doc should still be found | The answer misses prerequisites or returns unrelated AWS content | It retrieves the Amazon Connect page and lists prerequisites accurately | High | Plain RAG | Recall |
| FN-07 | "What options are available when configuring External Voice Transfer?" | False Negative | A concrete feature question should not fall through due to title mismatch | It returns only partial or unrelated telephony info | It cites the correct voice transfer-related sources and answers specifically | Medium | Plain RAG | Recall |
| FN-08 | "What are the API rate limits according to the system?" | False Negative | Tool-backed question should be one of the easiest successes | It fails to invoke the tool or still returns low confidence | It uses the tool path and returns the structured answer clearly | High | Tool | Recall |
| FN-09 | "What does the platform health endpoint report?" | False Negative | Another tool-friendly query to test invocation reliability | It answers from vague docs or says unsupported | It calls the tool path and reports health/uptime/services | High | Tool | Recall |
| FN-10 | "Compare BotKit SDK and AgentAssistWidget at a high level." | False Negative | Multi-source README comparison should be doable within scope | It fails because sources come from different repositories | It synthesizes across GitHub README materials without hallucinating | Medium | Agentic RAG | Recall |
| FN-11 | "How can I identify whether a source came from GitHub or docs.kore.ai in the UI?" | False Negative | UI transparency itself is part of the assignment scope | The UI hides provenance or makes it impossible to verify | The UI clearly exposes the original source link and type | High | Hybrid | Recall |
| FN-12 | "Where can I inspect the reasoning steps for an answer?" | False Negative | The React deliverable explicitly includes reasoning visibility | No reasoning view is available or steps are not tied to the answer | The UI surfaces reasoning steps and tools used | High | Hybrid | Recall |
| FN-13 | "When confidence is low, what should the user see?" | False Negative | The fallback behavior is a core requirement, not a bonus | The warning is missing or sources are hidden | The UI shows low-confidence wording plus retrieved sources for verification | High | Hybrid | Recall |
| FN-14 | "What is the difference between a simple documentation lookup and a query that needs multiple sources?" | False Negative | Tests whether the system can express its own routing behavior | It gives a generic answer without reflecting the design | It explains simple vs complex handling in a way consistent with the system | Medium | Agentic RAG | Recall |
| FN-15 | "What are the core stages in the ingestion pipeline?" | False Negative | The architecture and ingestion components are explicitly in project scope | It cannot explain its own pipeline or mixes up stages | It names loading, chunking, embedding, vector storage, and retrieval clearly | High | Plain RAG | Recall |

## C. Near-Neighbor Paired Tests

Each pair is designed so one question should succeed and the other should fail safely, exposing precision vs recall problems.

| Test ID | Exact question | Category | Why it matters | What failure would look like | What correct behavior should look like | Expected confidence | Expected handling mode | Main evaluation focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PAIR-01A | "How do I configure the Amazon Connect integration with Agent AI Voice?" | Near-Neighbor Pair | In-scope product integration question should succeed | It fails or stays low-confidence despite clear docs | It retrieves the integration docs and answers concretely | High | Plain RAG | Recall |
| PAIR-01B | "How do I configure the Twilio Flex integration with Agent AI Voice?" | Near-Neighbor Pair | Similar wording but likely unsupported should fail safely | It hallucinates a Twilio Flex workflow | It says the available sources do not establish that integration | Low | Plain RAG | Precision |
| PAIR-02A | "What does the BotKit SDK do?" | Near-Neighbor Pair | Supported SDK query should work | It misses GitHub content entirely | It answers from the BotKit README | High | Plain RAG | Recall |
| PAIR-02B | "What does the BotKit Terraform provider do?" | Near-Neighbor Pair | Similar but likely nonexistent artifact should not be invented | It fabricates a provider or infrastructure repo | It refuses to speculate beyond sources | Low | Plain RAG | Precision |
| PAIR-03A | "What are the API rate limits?" | Near-Neighbor Pair | Tool-supported query should be easy | It avoids the tool and gives weak docs-only output | It invokes the tool and returns the structured answer | High | Tool | Recall |
| PAIR-03B | "What are the billing export API rate limits?" | Near-Neighbor Pair | Similar phrasing but unsupported subdomain tests precision | It extends the known rate-limit answer to billing exports without evidence | It clarifies that only the supported limits in sources/tool can be stated | Low | Tool | Precision |
| PAIR-04A | "What prerequisites are required for External Voice Transfer setup?" | Near-Neighbor Pair | Should succeed from available voice-transfer docs | It misses prerequisites or misroutes to generic voice docs | It gives source-backed prerequisite information | Medium | Plain RAG | Recall |
| PAIR-04B | "What prerequisites are required for WhatsApp Voice Transfer setup?" | Near-Neighbor Pair | Similar construction but likely unsupported combination | It invents a WhatsApp-specific voice transfer workflow | It safely declines unsupported specifics | Low | Plain RAG | Precision |
| PAIR-05A | "Can I inspect the full retrieved source text in the UI?" | Near-Neighbor Pair | Supported UI behavior should succeed | The system or demo implies it cannot do this | The UI shows expandable full retrieved content | High | Hybrid | Recall |
| PAIR-05B | "Can I inspect the full original website page content for every citation in the UI?" | Near-Neighbor Pair | Similar request but stronger claim may exceed implementation | It claims full document rendering if only chunks are shown | It accurately states chunk-level evidence visibility and its limits | Medium | Hybrid | Calibration |
| PAIR-06A | "Which tools were used to answer this question?" | Near-Neighbor Pair | Supported reasoning transparency check | Tools are hidden or generic | The reasoning trace reveals actual tool usage | High | Agentic RAG | Recall |
| PAIR-06B | "Which external CRM API credentials did the system use to answer this question?" | Near-Neighbor Pair | Similar style but unsupported internal detail should fail safely | It invents secrets or credential flow | It clearly says that information is not available and should not be exposed | Low | Agentic RAG | Precision |
| PAIR-07A | "What does the health endpoint report?" | Near-Neighbor Pair | Supported API-tool question | It cannot answer despite the mock tool existing | It reports health status fields grounded in tool output | High | Tool | Recall |
| PAIR-07B | "What does the audit-log endpoint report?" | Near-Neighbor Pair | Similar but unsupported endpoint should not be guessed | It invents an audit-log endpoint response | It safely says no grounded support was found | Low | Tool | Precision |
| PAIR-08A | "How is confidence handled when evidence is weak?" | Near-Neighbor Pair | Core assignment behavior should be explainable | It cannot articulate fallback behavior | It explains low-confidence response and verification flow | High | Hybrid | Recall |
| PAIR-08B | "How is confidence handled when legal liability is high?" | Near-Neighbor Pair | Similar wording but unsupported policy question | It invents special legal-risk logic not implemented | It distinguishes implemented confidence logic from unsupported policy claims | Low | Hybrid | Precision |

## D. Confidence Calibration Tests

These are designed to reveal whether thresholds are too lenient, too strict, or poorly aligned with evidence quality.

| Test ID | Exact question | Category | Why it matters | What failure would look like | What correct behavior should look like | Expected confidence | Expected handling mode | Main evaluation focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAL-01 | "What is a dialog task?" | Confidence Calibration | Easy, direct factual query should not be underconfident | It returns low confidence despite strong supporting sources | It returns a confident answer with strong evidence | High | Plain RAG | Calibration |
| CAL-02 | "Summarize the Amazon Connect with Agent AI Voice setup process in one paragraph." | Confidence Calibration | Supported but broad procedural summary should often be medium/high, not low by default | It falls back too aggressively despite relevant evidence | It gives a grounded summary with appropriate confidence | Medium | Plain RAG | Calibration |
| CAL-03 | "What are the platform API rate limits?" | Confidence Calibration | Tool-backed query should calibrate upward if tool succeeds | Confidence stays low despite structured tool result | Confidence is appropriately high | High | Tool | Calibration |
| CAL-04 | "What is Kore.ai's pricing for nonprofit healthcare agencies?" | Confidence Calibration | Unsupported query should not receive medium/high confidence | It returns a fluent answer with medium or high confidence | It falls to low confidence and avoids unsupported pricing | Low | Plain RAG | Calibration |
| CAL-05 | "How do I create a dialog task from an utterance?" | Confidence Calibration | Supported procedural query checks whether the threshold is too strict | It gets marked low confidence because chunks are fragmented | It is answered with sensible confidence and clear sources | High | Plain RAG | Calibration |
| CAL-06 | "Explain the difference between BotKit SDK and Android Kore SDK in two sentences." | Confidence Calibration | Multi-source README synthesis should not be treated as unsupported if evidence exists | It drops to low confidence unnecessarily | It lands around medium confidence with grounded distinctions | Medium | Agentic RAG | Calibration |
| CAL-07 | "Does Kore.ai include a documented billing export endpoint?" | Confidence Calibration | Precision-sensitive unsupported API query should remain low confidence | It answers confidently because the query sounds technical | It stays low and source-limited | Low | Tool | Calibration |
| CAL-08 | "What prerequisites are listed for External Voice Transfer?" | Confidence Calibration | Niche but supported feature should not be misclassified as unsupported | It returns a fallback warning unnecessarily | It answers with medium or high confidence, depending on evidence strength | Medium | Plain RAG | Calibration |
| CAL-09 | "What changed in the latest platform release?" | Confidence Calibration | Dataset staleness and unsupported recency are calibration traps | It answers as if current release notes are guaranteed by corpus | It signals limitation and avoids false certainty | Low | Tool | Calibration |
| CAL-10 | "How should I interpret a medium-confidence answer in this system?" | Confidence Calibration | Evaluator wants semantics behind the numbers | The UI/system gives no meaningful distinction from low or high | Medium is presented as cautious but usable with verification | Medium | Hybrid | Calibration |
| CAL-11 | "Why are you not confident in this answer?" | Confidence Calibration | Low-confidence cases should be explainable, not opaque | The system cannot tie low confidence to weak evidence or retrieval gaps | It explains that evidence support is limited or partial | Low | Hybrid | Calibration |
| CAL-12 | "What does the health endpoint say about uptime?" | Confidence Calibration | Tool-friendly, structured, likely-supported query | It still lands at medium/low confidence without reason | It comes back high confidence if tool result is present | High | Tool | Calibration |
| CAL-13 | "Can Kore.ai replace all enterprise telephony infrastructure on its own?" | Confidence Calibration | Broad architecture overclaim should never come back confident | It gives a strong yes/no without bounded evidence | It stays cautious and grounded in integration docs only | Low | Agentic RAG | Calibration |
| CAL-14 | "What are the stages of the ingestion pipeline in this project?" | Confidence Calibration | Project-self-description should be one of the easiest supported answers | It comes back low because retrieval/scoring logic is poorly calibrated | It returns high confidence with clear stage names | High | Plain RAG | Calibration |
| CAL-15 | "What is the exact legal review process for enabling sentiment analysis?" | Confidence Calibration | Unsupported governance process should be a clean low-confidence case | It invents internal workflow and still marks it medium | It safely declines with low confidence | Low | Plain RAG | Calibration |

## E. Citation / Grounding Tests

Designed to expose irrelevant citations, partial matches, weak source support, and semantically similar but non-supporting documents.

| Test ID | Exact question | Category | Why it matters | What failure would look like | What correct behavior should look like | Expected confidence | Expected handling mode | Main evaluation focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GRD-01 | "Which exact source supports your statement about the prerequisites for Amazon Connect integration?" | Citation / Grounding | Forces evidence-level verification | It cites a nearby but non-supporting integration page | It points to the actual supporting source and relevant retrieved text | High | Plain RAG | Grounding |
| GRD-02 | "Show me the source that supports your answer about BotKit SDK event handling." | Citation / Grounding | GitHub README evidence should be directly inspectable | It cites generic docs instead of the SDK README | It links to the BotKit README-derived source | High | Plain RAG | Grounding |
| GRD-03 | "Which source proves that API rate limits came from a tool-backed answer rather than a guessed documentation summary?" | Citation / Grounding | Tool answers still need user-visible grounding | There is no visible trace of the tool-backed origin | Reasoning and sources make the origin clear | High | Tool | Grounding |
| GRD-04 | "Are these citations semantically related, or do they directly support the specific steps you listed?" | Citation / Grounding | Evaluates support strength, not just topical similarity | Sources are generally related but do not justify the listed steps | The cited chunks directly support the claims made | Medium | Hybrid | Grounding |
| GRD-05 | "If one citation is from a theming page and the answer is about dialog creation, why was it included?" | Citation / Grounding | Captures common retrieval drift and noisy citation sets | Irrelevant sources appear without explanation | Irrelevant sources are absent or clearly lower-ranked and not relied upon | Medium | Plain RAG | Grounding |
| GRD-06 | "Show me the full retrieved chunk, not just the citation label, for the statement about connector options." | Citation / Grounding | Grounding should be inspectable at chunk level | UI only shows labels or paths without evidence content | The full supporting chunk can be expanded and reviewed | High | Hybrid | Grounding |
| GRD-07 | "Did you cite the original docs link or only a local markdown file representation?" | Citation / Grounding | Original-source traceability is part of the assignment | Citation points only to `.md` path or opaque local artifact | Citation resolves to the source URL and preserves provenance | High | Hybrid | Grounding |
| GRD-08 | "Which citation supports the difference between Android Kore SDK and AgentAssistWidget, and which claims are unsupported?" | Citation / Grounding | Multi-source comparisons should separate supported from unsupported claims | The answer blurs distinctions with weak or absent support | It maps specific claims to specific sources and admits gaps | Medium | Agentic RAG | Grounding |
| GRD-09 | "If a source was retrieved but not used in the final answer, can I tell?" | Citation / Grounding | Important for debugging ranking and synthesis quality | The UI hides ranking context and all sources appear equally authoritative | The interface or trace makes source usage transparent enough to inspect | Medium | Hybrid | Grounding |
| GRD-10 | "Can you show a case where the top retrieved source is relevant but still not sufficient to justify the full answer?" | Citation / Grounding | Tests whether the system/candidate understands partial support | It treats top retrieval as proof of all claims | It distinguishes partial grounding from full grounding | Medium | Agentic RAG | Grounding |

## F. Agentic vs Plain-RAG Routing Tests

Questions specifically designed to reveal whether the system correctly uses plain retrieval, multi-step reasoning, or tools.

| Test ID | Exact question | Category | Why it matters | What failure would look like | What correct behavior should look like | Expected confidence | Expected handling mode | Main evaluation focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RTE-01 | "What is BotKit SDK?" | Routing | Simple factual SDK lookup should stay on the simplest path | It triggers unnecessary multi-step reasoning or wrong tool usage | It uses straightforward retrieval and answers directly | High | Plain RAG | Precision |
| RTE-02 | "Compare BotKit SDK, Android Kore SDK, and AgentAssistWidget, and tell me when to use each." | Routing | This should trigger synthesis across sources, not one-shot retrieval only | It treats it like a single-fact lookup and gives a shallow answer | It uses agentic synthesis across multiple sources | Medium | Agentic RAG | Recall |
| RTE-03 | "What are the API rate limits?" | Routing | Should prefer the extra tool if available | It routes only through vector search | It uses the API tool path and shows that in reasoning | High | Tool | Recall |
| RTE-04 | "What are the prerequisites for Amazon Connect integration, and which SDK should I review if I need mobile support afterward?" | Routing | Mixed-source, two-part query should not stay on a single simple path | It answers only one half or chooses a single source family | It synthesizes docs plus SDK guidance appropriately | Medium | Agentic RAG | Recall |
| RTE-05 | "What is the platform health status?" | Routing | Simple tool-backed status query should route cleanly | It uses plain docs only or gives a vague answer | It uses the health tool path and reports structured fields | High | Tool | Recall |
| RTE-06 | "Summarize the ingestion pipeline of this project." | Routing | A project-self-description question should not need tools or decomposition | It overcomplicates the path or routes to irrelevant tools | It uses plain retrieval from project docs and answers clearly | High | Plain RAG | Precision |
| RTE-07 | "For this answer, explain why you chose an API tool instead of plain retrieval." | Routing | Tool choice must be explainable, not decorative | There is no coherent reason or the answer does not match execution | Reasoning and candidate explanation align with the actual route | Medium | Tool | Grounding |
| RTE-08 | "Break this into steps: find the channel options, identify if a tool is needed, then answer." | Routing | Explicit process requests should test reasoning visibility | The system ignores the decomposition cue entirely | The trace shows multi-step handling or a defendable equivalent | Medium | Agentic RAG | Calibration |
| RTE-09 | "What is the current platform version and what does that imply for deployment choices?" | Routing | Mixed tool plus synthesis query | It answers version only or invents deployment implications | It separates supported version facts from more interpretive claims | Medium | Hybrid | Calibration |
| RTE-10 | "Which mode should handle this question: simple retrieval, multi-step reasoning, or a tool? Explain." | Routing | Meta-query checks whether routing policy is understandable | The system cannot explain its own routing logic | It gives a routing choice consistent with the actual design | Medium | Agentic RAG | Grounding |

## Top 25 Precision Tests

1. FP-01
2. FP-02
3. FP-03
4. FP-04
5. FP-05
6. FP-06
7. FP-07
8. FP-08
9. FP-09
10. FP-10
11. FP-11
12. FP-12
13. FP-13
14. FP-14
15. FP-15
16. PAIR-01B
17. PAIR-02B
18. PAIR-03B
19. PAIR-04B
20. PAIR-06B
21. PAIR-07B
22. PAIR-08B
23. CAL-04
24. CAL-07
25. CAL-15

## Top 25 Recall Tests

1. FN-01
2. FN-02
3. FN-03
4. FN-04
5. FN-05
6. FN-06
7. FN-07
8. FN-08
9. FN-09
10. FN-10
11. FN-11
12. FN-12
13. FN-13
14. FN-14
15. FN-15
16. PAIR-01A
17. PAIR-02A
18. PAIR-03A
19. PAIR-04A
20. PAIR-05A
21. PAIR-06A
22. PAIR-07A
23. PAIR-08A
24. CAL-01
25. CAL-05

## Top 15 Confidence-Calibration Tests

1. CAL-01
2. CAL-02
3. CAL-03
4. CAL-04
5. CAL-05
6. CAL-06
7. CAL-07
8. CAL-08
9. CAL-09
10. CAL-10
11. CAL-11
12. CAL-12
13. CAL-13
14. CAL-14
15. CAL-15

## Top 10 Demo-Ready Paired Tests

1. PAIR-01A vs PAIR-01B
2. PAIR-02A vs PAIR-02B
3. PAIR-03A vs PAIR-03B
4. PAIR-04A vs PAIR-04B
5. PAIR-05A vs PAIR-05B
6. PAIR-06A vs PAIR-06B
7. PAIR-07A vs PAIR-07B
8. PAIR-08A vs PAIR-08B
9. CAL-01 vs CAL-04
10. FN-06 vs FP-07

## Final Evaluator Checklist

### Signs the system is overconfident

- It answers unsupported pricing, legal, compliance, or internal-API questions with specific details.
- It uses medium or high confidence on questions whose sources are only topically related.
- It cites semantically similar documents that do not actually support the answer claims.
- It treats tool-like wording as evidence and fabricates API endpoints or payloads.
- It fails paired tests where the unsupported variant should clearly fall back safely.

### Signs the system is underconfident

- It returns fallback warnings for direct product questions like widget configuration, dialog creation, or SDK purpose.
- It treats supported README/documentation questions as low confidence despite clear evidence.
- Tool-backed answers such as rate limits or health status do not receive meaningfully higher confidence.
- It cannot answer project-self-description questions about ingestion, reasoning trace, or fallback behavior.
- It fails the supported side of near-neighbor pairs too often.

### Signs the system is properly calibrated

- Supported direct questions resolve with confident answers and relevant citations.
- Niche-but-supported questions land in medium confidence when evidence is partial but real.
- Unsupported enterprise-policy or internal-implementation questions fail safely with low confidence.
- Tool-backed questions clearly show the tool path and confidence uplift.
- Multi-source questions use broader reasoning without pretending every claim is fully supported.

### Evaluator decision rule

- If false positives dominate: the system has a precision/grounding problem and is too risky for enterprise search.
- If false negatives dominate: the system has a recall/routing/chunking problem and feels weak despite having the data.
- If both are high: the system lacks robust retrieval calibration and should not be presented as reliable agentic RAG yet.
- If direct supported questions succeed, unsupported questions fail safely, and medium-confidence behavior is understandable: the system is reasonably aligned with the PDF expectations.

