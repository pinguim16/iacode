# Diff Summary

CP0007 closes the publication-portability defect recorded in `DIVERGENCE.md` without changing Gate
4 product behavior. It introduces checkpoint schema 3.3.0 and one shared classifier that rejects
command inputs which cannot cross Git transport, including `.git`, ignored, absolute and escaping
paths. The recorder excludes such automatic inputs and refuses explicit ones; the validator
independently recomputes the refusal. Historical pre-3.3 checkpoints retain digest-bound
compatibility. Tests, ADR-0034, protocol documentation, Engineering Memory and the complete
corrective checkpoint evidence were updated accordingly.
