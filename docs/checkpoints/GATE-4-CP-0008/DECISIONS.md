# Decisions

- CP0007 is the immutable subject; all new evidence belongs to CP0008.
- The published canonical denominators and execution order are fixed. No selective rerun may turn a
  failed verifier into a pass.
- Same-session internal assurance remains labelled internal. The independent verdict is supported
  only by this audit session and its attestation about the sealed subject.
- Command evidence in CP0008 may reference only Git-transportable inputs. Generated outputs are
  recorded as outputs and summarized by tracked reports, never declared as `.git`, temporary,
  ignored or untracked inputs.
- No product correction is permitted in this run. Any substantive failure changes the verdict to
  `REWORK_REQUIRED` and becomes a formal finding.
