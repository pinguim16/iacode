# Resume validation

- Baseline branch and commit: `main` at `f61f84ca7e830002db1674f1df2aca8172f6e483`.
- Baseline matched `STATE.json`; no divergence file was required.
- `validate_checkpoint.py`: PASS before audit execution.
- Integrity chain: PASS with 20 anchors after anchoring sealed subject `GATE-3-CP-0003`.
- Authorised remote: `origin/main` and `iacode-checkpoints/GATE-3-CP-0003` synchronised.
- Sealed M1 subjects: 7/7 valid locally and 7/7 valid from a transport clone of the remote.
- Published evidence objects: PASS; 70 named commits, zero unpublished.
- History secret scan: PASS, zero findings under the repository allowlist.
- Full verification: FAIL, 31/32 stages; only `dependency-scan` failed.
- Independent dependency repetition: FAIL, PyPI 0 findings, npm 2 Critical and 4 High.
- Frozen stop condition: fired; later audit criteria remain unverified.
