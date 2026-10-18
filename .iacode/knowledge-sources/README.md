# Curated knowledge admission

The shipped registry is empty. No actual user/provider/repository content receives a reuse grant
from Gate7 authorization, storage consent or this directory's existence.

An operator-reviewed deployment supplies closed artifacts under `artifacts/` and exact digest-bound
rights evidence under `grants/`, with the source registry binding one current revision to its exact
project. The API reads this configured root; it cannot upload grants or fetch arbitrary paths/URLs.
Unknown/denied/revoked/expired rights refuse admission and current delivery. Training/distillation
remain denied. Structural validation is not proof of legal title; the administrator must possess
and retain reviewable rights evidence. See [ADR-0053](../../docs/adr/ADR-0053-knowledge-requires-content-bound-source-permission.md).

Synthetic validation sources are generated only in explicitly owned test roots and never added as
an implicit production fallback. The canonical checklist and checkpoint own acceptance status.
