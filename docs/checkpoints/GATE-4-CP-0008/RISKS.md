# Risks

`G4-F-004` proves that a producer-time review archive can be valid yet fail to represent the final sealed checkpoint. Promotion on that stale digest would make the review transport non-reproducible.
