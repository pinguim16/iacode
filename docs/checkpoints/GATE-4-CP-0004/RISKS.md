# Risks

`G4-F-002` shows that the published non-fast verifier is intermittent or order-dependent: infra and smoke failed in the single clean-clone run but passed on exact isolated reruns. Promotion on retries would permit a false PASS.
