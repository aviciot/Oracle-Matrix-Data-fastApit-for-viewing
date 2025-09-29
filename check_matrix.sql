---docker exec -it matrix_oracle_xe sqlplus -s MATRIX_USER/Neo2025@oracle-xe:1521/xepdb1 @check_matrix.sql

SET PAGESIZE 100
SET LINESIZE 200
SET FEEDBACK OFF
COLUMN table_name FORMAT A25
COLUMN row_count FORMAT 9999999

PROMPT === Row counts per table ===

SELECT 'RESISTANCE_SHIPS' AS table_name, COUNT(*) AS row_count FROM RESISTANCE_SHIPS
UNION ALL
SELECT 'AWAKENED_HUMANS', COUNT(*) FROM AWAKENED_HUMANS
UNION ALL
SELECT 'SLEEPERS', COUNT(*) FROM SLEEPERS
UNION ALL
SELECT 'AGENTS', COUNT(*) FROM AGENTS
UNION ALL
SELECT 'MATRIX_LOCATIONS', COUNT(*) FROM MATRIX_LOCATIONS
UNION ALL
SELECT 'ORACLES', COUNT(*) FROM ORACLES
UNION ALL
SELECT 'MISSIONS', COUNT(*) FROM MISSIONS
ORDER BY table_name;

PROMPT
PROMPT === Foreign key consistency checks ===

PROMPT -- Humans must reference valid ships
SELECT COUNT(*) AS invalid_humans
FROM AWAKENED_HUMANS h
WHERE NOT EXISTS (
    SELECT 1 FROM RESISTANCE_SHIPS s WHERE s.ship_id = h.ship_id
);

PROMPT -- Missions must reference valid ships
SELECT COUNT(*) AS invalid_missions_ships
FROM MISSIONS m
WHERE NOT EXISTS (
    SELECT 1 FROM RESISTANCE_SHIPS s WHERE s.ship_id = m.ship_id
);

PROMPT -- Missions must reference valid locations
SELECT COUNT(*) AS invalid_missions_locations
FROM MISSIONS m
WHERE NOT EXISTS (
    SELECT 1 FROM MATRIX_LOCATIONS l WHERE l.location_id = m.target_location_id
);

PROMPT -- Oracles must reference valid locations
SELECT COUNT(*) AS invalid_oracles_locations
FROM ORACLES o
WHERE NOT EXISTS (
    SELECT 1 FROM MATRIX_LOCATIONS l WHERE l.location_id = o.location_id
);

PROMPT === Done ===
EXIT;
