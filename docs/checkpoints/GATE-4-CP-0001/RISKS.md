# Risks

- Docker Desktop and the local container network are runtime dependencies for the live quality and
  sandbox scenarios; the full verifier proved them in this run, but later reviews must reproduce
  those scenarios rather than infer health from container status.
- Toolchain image digests and offline caches are pinned. Updating a base image, lockfile, seed POM
  or declared image input invalidates the content address and requires full sandbox revalidation.
- The program-state file is a timestamped pre-seal snapshot of the last published product commit;
  the sealed checkpoint tag is the authoritative post-seal resume pointer.
- Internal Red Team and mirror results are not independent. Gate 4 remains unapproved until a later
  independent run reviews the sealed subject and records the required verdicts.
