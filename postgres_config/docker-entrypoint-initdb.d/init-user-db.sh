#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER radius with encrypted password '$RADIUS_DB_PASS';
	CREATE DATABASE radius;
	GRANT ALL PRIVILEGES ON DATABASE radius TO radius;
	GRANT ALL PRIVILEGES ON DATABASE radius TO $POSTGRES_USER;
EOSQL
psql --username "radius" --password "$RADIUS_DB_PASS" --dbname radius -a -f /radius-schema/schema.sql
