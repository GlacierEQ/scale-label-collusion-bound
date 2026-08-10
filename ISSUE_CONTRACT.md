# ISSUE CONTRACT

## Pain
Suspiciously high pairwise annotator agreement can indicate copied labeling behavior or other non-independent processes, but raw agreement is misleading when annotators have skewed label marginals.

## Success
- Compare observed pairwise agreement with expected agreement under independent annotator-specific empirical marginals.
- Require an explicit minimum overlap before screening a pair.
- Flag agreement lift above an explicit policy margin.
- Bind exact annotation input and screening policy into deterministic pair/report fingerprints.
- Refuse duplicate annotator/item rows and malformed identities/labels.

## Boundary
A flag is an **agreement anomaly requiring investigation**, not proof of collusion or misconduct. This repository does not authenticate annotators, infer intent, adjudicate misconduct, or execute labeling actions.
