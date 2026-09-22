# Red Team Report — GATE 0 — FOUNDATION

Result: `RED_TEAM_PASS`

- Checkpoint: `GATE-0-CP-0001`
- Generated: `2026-09-22T00:31:27Z`
- Source: scripts/development-ledger/gate0_red_team.py with gate0_runtime_attacks.py — the internal adversarial battery of GATE 0 — FOUNDATION, executed against the delivery

Every attack below executed a mutation and required the specific refusal it aimed at. A
non-zero exit code is not a defence: a control that refused for an unrelated reason has
not been tested.

## Null-mutation control

Result: `VALID`

the unmutated fixture is accepted by every control this battery mutates: the application accepts its own configuration (configuration loads, health=UP, version=0.0.0-test); redaction leaves a clean message alone (connected to db:5432 in 35ms); the scope control accepts the real tree (no violation); the infrastructure suite accepts the real compose file (..................
----------------------------------------------------------------------
Ran 18 tests in 0.657s

OK)

The unmutated fixture goes through the identical path and must be **accepted** before any
refusal below is attributed to the mutation that produced it.

## Scenarios

| Attack | Category | Target | Mutation | Expected | Result |
|---|---|---|---|---|---|
| `G0-A` | mandatory | configuration | IACODE_CORS_ALLOW_ORIGINS='*' | the configuration refuses to load and names the wildcard | `DEFENDED` |
| `G0-B` | mandatory | configuration | IACODE_DATABASE_URL without the asyncpg driver | the configuration refuses to load and names the driver | `DEFENDED` |
| `G0-C` | mandatory | configuration | IACODE_MINIO_ENDPOINT='http://minio:9000' | the configuration refuses at start-up rather than on the first object call | `DEFENDED` |
| `G0-D` | mandatory | configuration | IACODE_LOG_LEVEL='CHATTY' | the configuration refuses to load | `DEFENDED` |
| `G0-E` | mandatory | configuration | load the configuration with no environment at all | every credential default is empty rather than a working value | `DEFENDED` |
| `G0-F` | mandatory | secret handling | log a DSN in the message and a secret key in the structured context | both are replaced with [REDACTED] while the host stays readable | `DEFENDED` |
| `G0-I` | mandatory | error contract | raise an exception whose message contains a connection string | the response carries a stable code and a correlation id, and no internal detail | `DEFENDED` |
| `G0-J` | mandatory | correlation | supply a correlation identifier that is too short, one with a space and one oversized | every supplied value is replaced by a generated one rather than echoed | `DEFENDED` |
| `G0-K` | mandatory | readiness | run the application against addresses where nothing is listening | readiness answers 503 NOT_READY with every dependency DOWN while liveness stays UP | `DEFENDED` |
| `G0-L` | mandatory | readiness | point the database at an unreachable host with a password in the URL | the failure detail is redacted before it reaches the response | `DEFENDED` |
| `G0-M` | mandatory | readiness | a probe that sleeps for an hour | readiness bounds the probe and answers DOWN within the configured timeout | `DEFENDED` |
| `G0-N` | mandatory | version | configure a password and a secret key, then read /version | the payload carries build identity only | `DEFENDED` |
| `G0-G` | mandatory | secret handling | a secret three levels down, inside a list, under a key the code never names | redaction reaches it, because it matches on the key name at any depth | `DEFENDED` |
| `G0-H` | mandatory | secret handling | an ordinary operational message with no credential in it | the message passes through unchanged, so redaction stays worth having | `DEFENDED` |
| `G0-O` | mandatory | scope | plant a module in a directory the scope registry reserves for a later Gate | the scope control reports a violation naming the path and the owning Gate | `DEFENDED` |
| `G0-P` | mandatory | scope | replace a reserved README with prose that does not declare the reservation | the scope control reports the missing declaration | `DEFENDED` |
| `G0-Q` | mandatory | infrastructure | bind the API's published port to 0.0.0.0 instead of 127.0.0.1 | test_published_ports_are_loopback_only refuses, naming the host address | `DEFENDED` |
| `G0-R` | mandatory | infrastructure | replace a pinned image reference with :latest | test_every_image_is_pinned refuses, naming the floating tag | `DEFENDED` |
| `G0-S` | mandatory | infrastructure | weaken the migration dependency to service_started | test_compose_uses_health_conditions_not_sleeps refuses, naming the weakened condition | `DEFENDED` |
| `G0-T` | mandatory | infrastructure | remove the named volume from PostgreSQL | test_durable_state_uses_named_volumes refuses, naming the service | `DEFENDED` |
| `G0-U` | mandatory | infrastructure | replace the API healthcheck with a command that always succeeds | test_healthchecks_do_more_than_confirm_a_process_exists refuses | `DEFENDED` |
| `G0-V` | mandatory | backup | a manifest recording result=FAILED | the restore refuses before touching the target | `DEFENDED` |
| `G0-W` | mandatory | backup | a dump whose bytes do not match the recorded digest | the restore refuses before dropping anything | `DEFENDED` |
| `G0-X` | mandatory | backup | run the backup with every container command failing | the component is reported FAILED with a reason, so the run exits non-zero | `DEFENDED` |
| `G0-Y` | mandatory | dependency failure | docker compose stop postgres | liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns | `DEFENDED` |
| `G0-Z` | mandatory | dependency failure | docker compose stop redis | liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns | `DEFENDED` |
| `G0-AA` | mandatory | dependency failure | docker compose stop minio | liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns | `DEFENDED` |
| `G0-AB` | mandatory | dependency failure | docker compose stop temporal | liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns | `DEFENDED` |

## What each attack observed

### `G0-A` — A permissive CORS wildcard reaches the running API.

- Mutation: IACODE_CORS_ALLOW_ORIGINS='*'
- Expected: the configuration refuses to load and names the wildcard
- Observed: Value error, IACODE_CORS_ALLOW_ORIGINS may not contain '*'; list the exact origins [type=value_error, input_value=['*'], input_type=list]
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-B` — A synchronous database URL silently blocks the event loop.

- Mutation: IACODE_DATABASE_URL without the asyncpg driver
- Expected: the configuration refuses to load and names the driver
- Observed: Value error, IACODE_DATABASE_URL must use the postgresql+asyncpg driver, found 'postgresql' [type=value_error, input_value='postgresql://iacode:iacode@db:5432/iacode', input_type=s
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-C` — A scheme in the object-storage endpoint produces a client that builds broken URLs.

- Mutation: IACODE_MINIO_ENDPOINT='http://minio:9000'
- Expected: the configuration refuses at start-up rather than on the first object call
- Observed: Value error, IACODE_MINIO_ENDPOINT is host:port without a scheme; use IACODE_MINIO_SECURE [type=value_error, input_value='http://minio:9000', input_type=str]
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-D` — An invalid enumerated configuration value is accepted.

- Mutation: IACODE_LOG_LEVEL='CHATTY'
- Expected: the configuration refuses to load
- Observed: Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL' [type=literal_error, input_value='CHATTY', input_type=str]
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-E` — A default credential ships inside the application.

- Mutation: load the configuration with no environment at all
- Expected: every credential default is empty rather than a working value
- Observed: every credential default is empty
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-F` — A credential reaches a log record through the message.

- Mutation: log a DSN in the message and a secret key in the structured context
- Expected: both are replaced with [REDACTED] while the host stays readable
- Observed: redacted; host preserved as 'minio'
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-I` — An unhandled exception returns its traceback to the caller.

- Mutation: raise an exception whose message contains a connection string
- Expected: the response carries a stable code and a correlation id, and no internal detail
- Observed: HTTP 500; code=INTERNAL_ERROR correlationId present
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-J` — A caller controls what is written into our logs and headers.

- Mutation: supply a correlation identifier that is too short, one with a space and one oversized
- Expected: every supplied value is replaced by a generated one rather than echoed
- Observed: all three replaced, e.g. 01a0c685-ae66-7000-a4c9-...
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-K` — Readiness reports READY while no dependency is reachable.

- Mutation: run the application against addresses where nothing is listening
- Expected: readiness answers 503 NOT_READY with every dependency DOWN while liveness stays UP
- Observed: ready=HTTP 503 NOT_READY, health=UP, 4 dependencies reported
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-L` — A driver error puts the database password in the readiness payload.

- Mutation: point the database at an unreachable host with a password in the URL
- Expected: the failure detail is redacted before it reaches the response
- Observed: the failure detail is redacted
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-M` — A dependency that never answers makes readiness hang forever.

- Mutation: a probe that sleeps for an hour
- Expected: readiness bounds the probe and answers DOWN within the configured timeout
- Observed: answered in 1.0s with DOWN
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-N` — The version endpoint becomes a diagnostics dump.

- Mutation: configure a password and a secret key, then read /version
- Expected: the payload carries build identity only
- Observed: the payload carries build identity only
- Executed: GATE-0 internal Red Team, executed in the API image
- Result: `DEFENDED`

### `G0-G` — A credential hides at depth under a key nothing enumerates.

- Mutation: a secret three levels down, inside a list, under a key the code never names
- Expected: redaction reaches it, because it matches on the key name at any depth
- Observed: {"deeply": {"nested": [{"AWS_SECRET_ACCESS_KEY": "[REDACTED]"}]}}
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-H` — Redaction destroys the log it was supposed to protect.

- Mutation: an ordinary operational message with no credential in it
- Expected: the message passes through unchanged, so redaction stays worth having
- Observed: connected to db:5432 in 35ms with log level INFO
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-O` — A later Gate's capability is implemented inside this Gate.

- Mutation: plant a module in a directory the scope registry reserves for a later Gate
- Expected: the scope control reports a violation naming the path and the owning Gate
- Observed: apps/cli is reserved for GATE 5 but carries gateway.py
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-P` — A reserved directory quietly drops the declaration that reserves it.

- Mutation: replace a reserved README with prose that does not declare the reservation
- Expected: the scope control reports the missing declaration
- Observed: apps/cli is reserved for GATE 5 and does not declare the reservation
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-Q` — The stack is published on every interface.

- Mutation: bind the API's published port to 0.0.0.0 instead of 127.0.0.1
- Expected: test_published_ports_are_loopback_only refuses, naming the host address
- Observed: exit 1; test_published_ports_are_loopback_only fired
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-R` — An image floats on a moving tag.

- Mutation: replace a pinned image reference with :latest
- Expected: test_every_image_is_pinned refuses, naming the floating tag
- Observed: exit 1; test_every_image_is_pinned fired
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-S` — The API is allowed to start before the migration succeeds.

- Mutation: weaken the migration dependency to service_started
- Expected: test_compose_uses_health_conditions_not_sleeps refuses, naming the weakened condition
- Observed: exit 1; test_compose_uses_health_conditions_not_sleeps fired
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-T` — Durable state moves into the container filesystem.

- Mutation: remove the named volume from PostgreSQL
- Expected: test_durable_state_uses_named_volumes refuses, naming the service
- Observed: exit 1; test_durable_state_uses_named_volumes fired
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-U` — A healthcheck is reduced to proving a process exists.

- Mutation: replace the API healthcheck with a command that always succeeds
- Expected: test_healthchecks_do_more_than_confirm_a_process_exists refuses
- Observed: exit 1; test_healthchecks_do_more_than_confirm_a_process_exists fired
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-V` — A half-finished backup is restored as if it were complete.

- Mutation: a manifest recording result=FAILED
- Expected: the restore refuses before touching the target
- Observed: iacode-g0-restore-uuio24tn records result='FAILED'; an incomplete backup is not restorable and pretending otherwise is how a partial recovery is mistaken for a full one
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-W` — A corrupted dump is restored over a working database.

- Mutation: a dump whose bytes do not match the recorded digest
- Expected: the restore refuses before dropping anything
- Observed: postgres.dump does not match its recorded checksum; the backup is corrupt
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-X` — A backup against a stopped stack reports success.

- Mutation: run the backup with every container command failing
- Expected: the component is reported FAILED with a reason, so the run exits non-zero
- Observed: FAILED: Error: No such container
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-Y` — With postgres stopped, the API keeps claiming it can accept work.

- Mutation: docker compose stop postgres
- Expected: liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns
- Observed: health=UP ready=HTTP 503 NOT_READY down=['postgres', 'temporal'] expected=['postgres', 'temporal']; recovered=READY
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-Z` — With redis stopped, the API keeps claiming it can accept work.

- Mutation: docker compose stop redis
- Expected: liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns
- Observed: health=UP ready=HTTP 503 NOT_READY down=['redis'] expected=['redis']; recovered=READY
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-AA` — With minio stopped, the API keeps claiming it can accept work.

- Mutation: docker compose stop minio
- Expected: liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns
- Observed: health=UP ready=HTTP 503 NOT_READY down=['minio'] expected=['minio']; recovered=READY
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`

### `G0-AB` — With temporal stopped, the API keeps claiming it can accept work.

- Mutation: docker compose stop temporal
- Expected: liveness stays UP, readiness answers 503 NOT_READY over exactly the declared blast radius, no credential leaks, and readiness recovers when the service returns
- Observed: health=UP ready=HTTP 503 NOT_READY down=['temporal'] expected=['temporal']; recovered=READY
- Executed: GATE-0 internal Red Team, executed on the host
- Result: `DEFENDED`
