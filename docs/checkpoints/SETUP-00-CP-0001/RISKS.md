# Risks

- Claude Code is not installed; genuine second-tool validation is pending manual execution.
- The active model's exact identifier and reasoning effort are not exposed; metadata records that limitation rather than guessing.
- The built-in schema validator intentionally supports the JSON Schema features used here, not the entire draft specification. Adding new schema keywords requires validator tests or a managed dependency.
- `HEAD` is symbolic by design to avoid cryptographic self-reference. Receivers must resolve it with Git and use the validator.
- Secret detection is defense in depth and cannot prove absence of every credential format; patterns and tests must evolve.
- Tool adapters can drift from canonical definitions; independent documentation review remains mandatory.
- SETUP-00 supplies governance and tooling only; none of the planned runtime behavior exists.

