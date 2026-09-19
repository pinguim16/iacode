# Provenance and Rights

The canonical JSON representation uses camelCase. The human-facing names `source_type`, `storage_allowed`, `rag_allowed`, `training_allowed`, and `distillation_allowed` map respectively to `sourceType`, `storageAllowed`, `ragAllowed`, `trainingAllowed`, and `distillationAllowed`.

Every reusable artifact records source, provider, model, ownership, license, rights, evidence, and notes. Unknown rights are denied. Repository storage does not imply RAG, training, or distillation permission.

`trainingAllowed` and `distillationAllowed` remain `false` until explicit, reviewable rights evidence authorizes a future policy change.

