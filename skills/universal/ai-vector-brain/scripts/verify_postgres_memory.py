#!/usr/bin/env python3
"""Opt-in server PostgreSQL behavior checks; no credentials in output/argv."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote
import uuid

ROOT = Path(__file__).resolve().parents[1]
# libpq expands a connection string only when it is passed as dbname, never from PGDATABASE, and argv
# would expose credentials, so the DSN is split into libpq's environment variables. Unknown keys fail
# closed: silently dropping one such as sslmode would weaken the connection.
PG_ENV = {'host': 'PGHOST', 'hostaddr': 'PGHOSTADDR', 'port': 'PGPORT', 'dbname': 'PGDATABASE', 'user': 'PGUSER',
          'password': 'PGPASSWORD', 'passfile': 'PGPASSFILE', 'service': 'PGSERVICE', 'options': 'PGOPTIONS',
          'application_name': 'PGAPPNAME', 'connect_timeout': 'PGCONNECT_TIMEOUT', 'sslmode': 'PGSSLMODE',
          'sslrootcert': 'PGSSLROOTCERT', 'sslcert': 'PGSSLCERT', 'sslkey': 'PGSSLKEY', 'sslcrl': 'PGSSLCRL',
          'channel_binding': 'PGCHANNELBINDING', 'gssencmode': 'PGGSSENCMODE',
          'target_session_attrs': 'PGTARGETSESSIONATTRS'}


def uri_decode(value: str) -> str:
    """Conservative UTF-8 URI subset: percent escapes, literal plus, no NUL."""
    if re.search(r'%(?![0-9a-fA-F]{2})', value) or '%00' in value.lower() or '\x00' in value:
        raise ValueError('MEMORY_TEST_DSN has invalid URI encoding')
    # libpq rejects interior literal spaces; percent-encoded spaces are valid.
    value = value.strip(' ')
    if ' ' in value:
        raise ValueError('MEMORY_TEST_DSN requires percent-encoded URI spaces')
    try:
        return unquote(value, errors='strict')
    except UnicodeError:
        raise ValueError('MEMORY_TEST_DSN requires UTF-8 URI encoding') from None


def keyword_params(dsn: str) -> dict:
    """Parse libpq keyword quoting and backslash escapes, without echoing input."""
    params, pos = {}, 0
    while pos < len(dsn):
        while pos < len(dsn) and dsn[pos].isspace():
            pos += 1
        if pos == len(dsn):
            break
        start = pos
        while pos < len(dsn) and not dsn[pos].isspace() and dsn[pos] != '=':
            pos += 1
        key = dsn[start:pos]
        while pos < len(dsn) and dsn[pos].isspace():
            pos += 1
        if not key or pos == len(dsn) or dsn[pos] != '=':
            raise ValueError('MEMORY_TEST_DSN is not a parseable libpq connection string')
        pos += 1
        while pos < len(dsn) and dsn[pos].isspace():
            pos += 1
        quoted = pos < len(dsn) and dsn[pos] == "'"
        if quoted:
            pos += 1
        value = []
        closed = not quoted
        while pos < len(dsn):
            char = dsn[pos]
            if quoted and char == "'":
                pos += 1
                closed = True
                break
            if not quoted and char.isspace():
                break
            pos += 1
            if char == '\\':
                if pos < len(dsn):
                    value.append(dsn[pos])
                    pos += 1
            else:
                value.append(char)
        if not closed:
            raise ValueError('MEMORY_TEST_DSN is not a parseable libpq connection string')
        params[key] = ''.join(value)
    return params


def dsn_env(dsn: str) -> dict:
    """libpq URI, key=value string, or bare database name -> PG* variables. ValueError never quotes the DSN."""
    if '\x00' in dsn:
        raise ValueError('MEMORY_TEST_DSN contains an invalid NUL')
    params = {}
    if re.match(r'postgres(ql)?://', dsn):
        # split by hand: urlsplit rejects libpq multi-host lists with bracketed IPv6 hosts
        netloc, path, qs = re.match(r'[^:]+://([^/?]*)([^?]*)\??(.*)', dsn).groups()
        query = []
        # libpq URI parameters are percent-decoded, never form-urlencoded.
        for pair in qs.split('&') if qs else []:
            if pair.count('=') != 1:
                raise ValueError('MEMORY_TEST_DSN is not a parseable libpq URI')
            key, value = pair.split('=')
            query.append((uri_decode(key), uri_decode(value)))
        userinfo, _, hostspec = netloc.rpartition('@')
        if userinfo:
            user, colon, password = userinfo.partition(':')
            params['user'] = uri_decode(user)
            if colon:
                params['password'] = uri_decode(password)
        hosts, ports = [], []
        for h in hostspec.split(',') if hostspec else []:
            if h.startswith('['):
                if ']' not in h:
                    raise ValueError('MEMORY_TEST_DSN is not a parseable libpq URI')
                host, _, rest = h[1:].partition(']')
                if not host or (rest and not rest.startswith(':')):
                    raise ValueError('MEMORY_TEST_DSN is not a parseable libpq URI')
                port = rest[1:] if rest.startswith(':') else ''
            else:
                host, _, port = h.partition(':')
            hosts.append(uri_decode(host))
            ports.append(uri_decode(port))
        if any(hosts):
            params['host'] = ','.join(hosts)
        if any(ports):
            params['port'] = ','.join(ports)
        if len(path) > 1:
            params['dbname'] = uri_decode(path[1:])
        params.update(query)
    elif '=' in dsn:
        params = keyword_params(dsn)
    else:
        params['dbname'] = dsn
    unknown = sorted(k for k in params if k not in PG_ENV)
    if unknown:
        raise ValueError('unsupported MEMORY_TEST_DSN parameter(s)')
    return {PG_ENV[k]: v for k, v in params.items()}


def build_sql(schema: str, role: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", schema + "") or not re.fullmatch(r"[a-z][a-z0-9_]*", role):
        raise ValueError("schema and role must be simple lowercase SQL identifiers")
    asset = (ROOT / "assets/sql/012_bitemporal_facts.sql").read_text()
    # Qualify the upgrade DROP so search_path cannot drop an existing public function.
    asset = asset.replace("DROP FUNCTION IF EXISTS assert_fact(", f'DROP FUNCTION IF EXISTS "{schema}".assert_fact(')
    rls = (ROOT / "assets/sql/006_rls_multitenant.sql").read_text()
    return f"""BEGIN;
SET LOCAL statement_timeout = '30s';
SET LOCAL lock_timeout = '5s';
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname='btree_gist') THEN
  RAISE EXCEPTION 'preflight: preinstall btree_gist in the dedicated test database';
 END IF;
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='{role}' AND NOT rolbypassrls AND NOT rolsuper AND oid <> (SELECT oid FROM pg_roles WHERE rolname=current_user)) THEN
  RAISE EXCEPTION 'preflight: RLS role must exist, differ from owner, and be NOSUPERUSER NOBYPASSRLS';
 END IF;
END $$;
CREATE SCHEMA "{schema}";
SET LOCAL search_path = "{schema}", public;
CREATE FUNCTION "{schema}".expect(ok boolean, label text) RETURNS void LANGUAGE plpgsql AS $$ BEGIN
 IF ok IS DISTINCT FROM TRUE THEN RAISE EXCEPTION 'assertion failed: %', label; END IF;
END $$;
{asset}
{asset}
INSERT INTO entities VALUES ('incident:42','incident'), ('person:alice','person');
SELECT "{schema}".expect(assert_fact('e1','incident:42','incident_owner','"person:alice"','2026-03-01 08:50Z','event:open',NULL,10)='current','insert');
-- Synthetic transaction-time fixture: now() is constant inside this rollback transaction.
UPDATE state_facts SET recorded_at='2026-01-01 00:00Z' WHERE event_id='e1';
SELECT "{schema}".expect(assert_fact('e2','incident:42','incident_owner','"person:bob"','2026-03-01 09:10Z','event:update',NULL,10)='current','update');
SELECT "{schema}".expect(assert_fact('e2','incident:42','incident_owner','"person:bob"','2026-03-01 09:10Z','event:update',NULL,10)='duplicate','duplicate');
SELECT "{schema}".expect(assert_fact('e3','incident:42','incident_owner','"person:alice"','2026-03-01 09:00Z','snapshot',NULL,10)='unchanged','late agreeing snapshot');
SELECT "{schema}".expect(assert_fact('e4','incident:42','incident_owner','"person:alice"','2026-03-01 09:11Z','index',NULL,0)='held_lower_authority','authority');
SELECT "{schema}".expect((SELECT count(*)=1 FROM fact_candidates WHERE event_id='e4'),'held candidate');
SELECT "{schema}".expect(assert_fact('e5','incident:42','incident_owner','"team:oncall"','2026-03-01 08:40Z','snapshot',NULL,10)='history','backfill');
SELECT "{schema}".expect((SELECT value='"person:alice"'::jsonb FROM state_facts WHERE entity_id='incident:42' AND attribute='incident_owner' AND superseded_at IS NULL AND valid_from <= '2026-03-01 09:05Z' AND (valid_to IS NULL OR '2026-03-01 09:05Z' < valid_to)),'as of');
SELECT "{schema}".expect((SELECT value='"person:bob"'::jsonb FROM state_facts WHERE entity_id='incident:42' AND attribute='incident_owner' AND superseded_at IS NULL AND valid_from <= '2026-03-01 09:10Z' AND (valid_to IS NULL OR '2026-03-01 09:10Z' < valid_to)),'exclusive boundary');
SELECT "{schema}".expect((SELECT value='"person:alice"'::jsonb FROM state_facts WHERE recorded_at <= '2026-02-01 00:00Z' AND (superseded_at IS NULL OR '2026-02-01 00:00Z' < superseded_at) AND valid_from <= '2026-03-01 09:20Z' AND (valid_to IS NULL OR '2026-03-01 09:20Z' < valid_to)),'known at synthetic fixture');
SELECT "{schema}".expect(assert_fact('e7','incident:42','incident_owner','"person:carol"','2026-03-01 09:02Z','late:correction',NULL,10)='history','backfill inside closed interval');
SELECT "{schema}".expect((SELECT value='"person:carol"'::jsonb AND valid_to='2026-03-01 09:10Z'::timestamptz FROM state_facts WHERE event_id='e7'),'backfill end preserved');
SELECT "{schema}".expect(assert_fact('e6','incident:42','incident_owner','null','2026-03-01 09:30Z','event:clear',NULL,10)='current','clearance');
SELECT "{schema}".expect((SELECT value='null'::jsonb FROM state_facts WHERE entity_id='incident:42' AND attribute='incident_owner' AND superseded_at IS NULL AND valid_to IS NULL),'cleared value');
SELECT "{schema}".expect(NOT EXISTS(SELECT 1 FROM state_facts WHERE attribute='task_owner'),'unknown attribute');
DO $$ BEGIN
 BEGIN
  INSERT INTO state_facts(entity_id,attribute,value,valid_from,source_id) VALUES ('incident:42','incident_owner','"bad"','2026-03-01 09:31Z','bad');
  RAISE EXCEPTION 'overlap negative control accepted';
 EXCEPTION WHEN exclusion_violation THEN NULL; END;
END $$;
SELECT "{schema}".expect(value_references('{{"nested":["person:alice"]}}','person:alice') AND NOT value_references('"person:alice2"','person:alice'),'reference identity');
CREATE TEMP TABLE erase_events ON COMMIT DROP AS
 SELECT event_id FROM fact_events WHERE entity_id='person:alice'
 UNION SELECT event_id FROM state_facts WHERE event_id IS NOT NULL AND (entity_id='person:alice' OR value_references(value,'person:alice'))
 UNION SELECT event_id FROM fact_candidates WHERE entity_id='person:alice' OR value_references(value,'person:alice');
DELETE FROM fact_candidates WHERE entity_id='person:alice' OR value_references(value,'person:alice');
DELETE FROM state_facts WHERE entity_id='person:alice' OR value_references(value,'person:alice');
DELETE FROM fact_events WHERE event_id IN (SELECT event_id FROM erase_events);
DELETE FROM entities WHERE entity_id='person:alice';
SELECT "{schema}".expect(NOT EXISTS(SELECT 1 FROM state_facts WHERE value_references(value,'person:alice')) AND NOT EXISTS(SELECT 1 FROM fact_candidates WHERE value_references(value,'person:alice')) AND NOT EXISTS(SELECT 1 FROM fact_events WHERE event_id IN ('e1','e4')),'erase all references');
SELECT "{schema}".expect(EXISTS(SELECT 1 FROM state_facts WHERE value='"person:bob"'::jsonb),'erase preserves unrelated');
SELECT "{schema}".expect(NOT EXISTS(SELECT 1 FROM state_facts WHERE entity_id='incident:42' AND attribute='incident_owner' AND superseded_at IS NULL AND valid_from <= '2026-03-01 09:01Z' AND (valid_to IS NULL OR '2026-03-01 09:01Z' < valid_to)),'erased period unknown');
-- Minimal table fixtures exercise the exact 006 policy asset, without pgvector.
CREATE TABLE documents(id integer PRIMARY KEY, tenant_id text);
CREATE TABLE chunks(id integer PRIMARY KEY, tenant_id text);
CREATE TABLE embeddings(id integer PRIMARY KEY, tenant_id text);
-- Seed before installing FORCE RLS, without defining app.tenant_id.
INSERT INTO documents VALUES (1,'tenant:a'), (2,'tenant:b');
INSERT INTO chunks VALUES (1,'tenant:a'), (2,'tenant:b');
INSERT INTO embeddings VALUES (1,'tenant:a'), (2,'tenant:b');
{rls}
GRANT USAGE ON SCHEMA "{schema}" TO "{role}";
GRANT SELECT, INSERT ON documents,chunks,embeddings TO "{role}";
SET LOCAL ROLE "{role}";
SELECT "{schema}".expect(current_setting('app.tenant_id',true) IS NULL,'preflight missing tenant setting');
SELECT "{schema}".expect(NOT EXISTS(SELECT 1 FROM documents) AND NOT EXISTS(SELECT 1 FROM chunks) AND NOT EXISTS(SELECT 1 FROM embeddings),'missing tenant denies');
DO $$ DECLARE target text; BEGIN
 FOREACH target IN ARRAY ARRAY['documents','chunks','embeddings'] LOOP
  BEGIN
   EXECUTE format('INSERT INTO %I VALUES (4,%L)',target,'tenant:a');
   RAISE EXCEPTION 'missing tenant write negative control accepted: %',target;
  EXCEPTION WHEN insufficient_privilege THEN NULL; END;
 END LOOP;
END $$;
SELECT set_config('app.tenant_id','tenant:a',true);

SELECT set_config('app.tenant_id','tenant:b',true);
INSERT INTO documents VALUES (5,'tenant:b'); INSERT INTO chunks VALUES (5,'tenant:b'); INSERT INTO embeddings VALUES (5,'tenant:b');
SELECT "{schema}".expect((SELECT count(*)=2 AND min(id)=2 AND max(id)=5 FROM documents) AND (SELECT count(*)=2 AND min(id)=2 AND max(id)=5 FROM chunks) AND (SELECT count(*)=2 AND min(id)=2 AND max(id)=5 FROM embeddings),'tenant b reads');
DO $$ DECLARE target text; BEGIN
 FOREACH target IN ARRAY ARRAY['documents','chunks','embeddings'] LOOP
  BEGIN
   EXECUTE format('INSERT INTO %I VALUES (3,%L)',target,'tenant:a');
   RAISE EXCEPTION 'cross tenant negative control accepted: %',target;
  EXCEPTION WHEN insufficient_privilege THEN NULL; END;
 END LOOP;
END $$;
SELECT set_config('app.tenant_id','tenant:a',true);
SELECT "{schema}".expect((SELECT count(*)=1 AND min(id)=1 FROM documents) AND (SELECT count(*)=1 AND min(id)=1 FROM chunks) AND (SELECT count(*)=1 AND min(id)=1 FROM embeddings),'tenant a reads');
SELECT set_config('app.tenant_id','',true);
SELECT "{schema}".expect(NOT EXISTS(SELECT 1 FROM documents) AND NOT EXISTS(SELECT 1 FROM chunks) AND NOT EXISTS(SELECT 1 FROM embeddings),'empty tenant denies');
RESET ROLE;
ROLLBACK;
\\echo MEMORY_INTEGRATION_PASSED
"""


def run(environ=None, find_psql=shutil.which, execute=subprocess.run):
    env = dict(os.environ if environ is None else environ)
    if env.get('MEMORY_TEST_ALLOW') != 'dedicated-test-database':
        return 2, {'status': 'not_run', 'reason': 'set MEMORY_TEST_ALLOW=dedicated-test-database'}
    if not env.get('MEMORY_TEST_DSN') or not env.get('MEMORY_TEST_RLS_ROLE'):
        return 2, {'status': 'not_run', 'reason': 'MEMORY_TEST_DSN and MEMORY_TEST_RLS_ROLE are required'}
    role = env['MEMORY_TEST_RLS_ROLE']
    if not re.fullmatch(r'[a-z][a-z0-9_]*', role):
        return 2, {'status': 'not_run', 'reason': 'invalid RLS role identifier'}
    try:
        env.update(dsn_env(env.pop('MEMORY_TEST_DSN')))
    except ValueError as exc:
        return 2, {'status': 'not_run', 'reason': str(exc)}
    psql = find_psql('psql')
    if not psql:
        return 2, {'status': 'not_run', 'reason': 'psql unavailable; no simulated fallback'}
    sql = build_sql('memory_verify_' + uuid.uuid4().hex, role)
    try:
        result = execute([psql, '-X', '-q', '-v', 'ON_ERROR_STOP=1', '-f', '-'], input=sql, text=True, capture_output=True, env=env, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return 2, {'status': 'inconclusive', 'reason': 'psql unavailable or timed out; transaction rolls back on disconnect'}
    if result.returncode or 'MEMORY_INTEGRATION_PASSED' not in result.stdout:
        # Server errors may echo connection credentials; do not print raw stderr.
        return 1, {'status': 'failed', 'reason': 'server connection, preflight, or behavioral assertion failed', 'psql_exit': result.returncode}
    return 0, {'status': 'passed', 'backend': 'server_postgresql', 'transaction': 'rolled_back', 'coverage': ['bitemporal_mutations', 'synthetic_known_at', 'nonowner_rls_template'], 'unmeasured': ['concurrent_writers', 'pgvector_retrieval', 'fact_store_tenant_adapter', 'multi_transaction_replay']}


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    code, report = run()
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(code)
