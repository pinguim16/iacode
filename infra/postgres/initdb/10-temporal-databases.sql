-- Temporal's databases, created before its auto-setup runs.
--
-- Temporal shares this PostgreSQL server with the IACode system of record but keeps its own
-- databases. Sharing the server keeps the Foundation stack to one database container; separate
-- databases keep a backup of `iacode` free of Temporal's internal tables, which are Temporal's to
-- rebuild and not ours to restore.
--
-- This script runs once, on an empty data directory, as the superuser the image creates. It is
-- idempotent anyway: the image skips the whole directory when the volume already has data, and
-- `\gexec` makes each CREATE a no-op when the database is already there.

SELECT 'CREATE DATABASE temporal'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'temporal')\gexec

SELECT 'CREATE DATABASE temporal_visibility'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'temporal_visibility')\gexec
