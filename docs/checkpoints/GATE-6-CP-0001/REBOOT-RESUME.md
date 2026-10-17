# Saved for machine reboot

Historical runtime-v2 reboot record. The subsequent runtime-v3 attempt and current BLOCKED
continuation are recorded in DOCKER-RECOVERY.md, HANDOFF.md, STATE.json and attempt0003.
Do not repeat the runtime-v3 publication or treat the old reboot pause as the current blocker.

Owner requested immediate persistence on 2026-10-17. Gate6 remains IN_PROGRESS;
this is a continuation save, not Gate completion, READY_FOR_REVIEW or a Gate seal.
No machine restart was initiated by the agent.

## Persisted subject and interruption

- Branch: main. STATE.json binds the saved continuation to HEAD after commit.
- Sealed predecessor: bcfe297278d25ee5a1db70a32b8c4ba0731941ea (Gate5).
- Interrupted immutable runtime-v2: 16769718a61f430d37b428422d0ad431b5b221f9.
- Preserved tag: iacode-subjects/GATE-6-CP-0001-runtime-v2. Never move it.
- Source fingerprint: 9c4d40cb7d04f512d29c8383a5f6c158f024062a23ede2447ab05fd6ddc6e43b.
- cmd-0123: full verifier exit1 following intentional owned interruption;
  no completed-stage verdict or final verifier report was available.
- cmd-0124: exact verifier process identity checked and only its tree stopped;
  the original recorder completed before the interrupt recorder appended.
- cmd-0125: exact temporary clone owner removed and zero owned Compose
  containers, volumes and networks observed. No global cleanup is claimed.
- attempts/FULL-VERIFY-INTERRUPTED-0002*.json retain the original progress,
  interruption and cleanup. FULL-PRODUCER-ef611f879b56-MANIFEST.json is neutral,
  not a PASS. Attempt0001 and runtime-v1 also remain preserved.

## Resume after reboot

1. Read the canonical startup contracts and the complete current checkpoint;
   run python scripts/development-ledger/validate_checkpoint.py and compare
   branch, HEAD and dirty state against STATE.json before any alteration.
2. Read PLAN/STEPS/COMMANDS/FINDINGS and HANDOFF. Confirm no owned prior job
   remains; never reuse historical process IDs to stop anything.
3. The reboot-save commit advances main beyond runtime-v2. The full wrapper
   requires remote main to equal the requested subject: publish a fresh immutable
   runtime-v3 subject from the reviewed saved state, never retag v1/v2 or pretend
   the interrupted run completed. Recheck source fingerprint and strict delta.
4. Run the complete non-fast verifier (currently 47 policy-derived stages) using
   the bundled Node24 path documented in COMMANDS. Do not resume at stage2 or
   narrow inherited gates. Await the actual process and recorder completion.
5. Only on actual full success complete functional acceptance for all37 runtime
   criteria and the full190-row derived requirements; perform whole Green Keeper,
   completeness, internal Red Team/null control and full clean-clone closure audit
   in canonical order. Preserve exact producer bytes and serial metadata writers.
6. Assemble and validate all internal evidence, then canonically finalize/seal,
   publish and reconstruct the fresh exact archive. None of these pending controls
   is represented as completed by this save.

## Boundaries

Local causal proofs remain recorded: domain29, API173, client35, integration36,
root23 and real lifecycle72 controls. Counts are not a full1947-test PASS.
No unresolved finding is concealed by the intentional interruption.
Independent M2 audit and second-tool validation remain pending. Gate7 has not
been authorized. Do not modify sealed predecessors or retry policy-refused
historical cleanup targets; the exact exclusions remain in HANDOFF and RISKS.
