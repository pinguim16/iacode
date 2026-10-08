# Risks

- Advisory state changes over time; every release still requires a fresh live scan.
- Angular remains on authorized major 22; no major migration was attempted.
- Docker Desktop host-port forwarding can drift while containers remain healthy; the live loopback suite detects it and a non-destructive restart recovered this run.
- M1 remains unpassed until a later fresh-session independent audit.
