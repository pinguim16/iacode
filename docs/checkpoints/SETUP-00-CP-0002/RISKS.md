# Risks

- Genuine second-provider cold-start validation remains blocked until the local Claude Code installation is authenticated. The attempted process performed no model call and made no repository changes.
- `C:/Users/cesar/.local/bin` is not in the detecting process's PATH. Automation that invokes bare `claude` can still fail unless it uses the absolute path or the environment is corrected outside this repository.
- Claude Code is independently installed in more than one location with different versions (`2.1.195` and `2.1.187`). The user-local `2.1.195` executable is the verified target for future validation.
- Tool adapter formats can evolve. The adapters deliberately use only required frontmatter plus the documented `model: inherit` field and are covered by repository tests.
