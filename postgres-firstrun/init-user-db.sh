#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER bot WITH PASSWORD 'password' ;
	CREATE DATABASE telegram;
	ALTER DATABASE telegram OWNER TO bot;
	GRANT USAGE, CREATE ON SCHEMA public TO bot;
EOSQL
# 'public' schema access is needed for alembic migrations
