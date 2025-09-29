ALTER SESSION SET CONTAINER = XEPDB1;
ALTER SESSION SET CURRENT_SCHEMA = MATRIX_USER;

CREATE TABLE RESISTANCE_SHIPS (
  ship_id               NUMBER PRIMARY KEY,
  ship_name             VARCHAR2(100),
  ship_class            VARCHAR2(50),
  coordinates           VARCHAR2(100),
  emp_charge_status     NUMBER,
  crew_capacity         NUMBER,
  last_broadcast_depth  NUMBER,
  operational_condition VARCHAR2(20)
);

CREATE TABLE AWAKENED_HUMANS (
  human_id                 NUMBER PRIMARY KEY,
  real_name                VARCHAR2(120),
  rsi_name                 VARCHAR2(120),
  role                     VARCHAR2(50),
  mental_stability         NUMBER,
  awakening_date           DATE,
  ship_id                  NUMBER REFERENCES RESISTANCE_SHIPS(ship_id),
  specialty_skill          VARCHAR2(80),
  jack_in_count            NUMBER,
  in_matrix                CHAR(1),
  mentor_id                NUMBER NULL,     -- self-ref allowed
  construct_training_hours NUMBER,
  belief_level             NUMBER
);

CREATE TABLE SLEEPERS (
  sleeper_id           NUMBER PRIMARY KEY,
  simulated_identity   VARCHAR2(120),
  matrix_occupation    VARCHAR2(80),
  pod_location         VARCHAR2(120),
  connection_stability NUMBER,
  years_connected      NUMBER,
  awakening_potential  NUMBER,
  extraction_priority  NUMBER,
  anomaly_flags        NUMBER,
  rejection_risk       NUMBER
);

CREATE TABLE AGENTS (
  agent_id              NUMBER PRIMARY KEY,
  designation_code      VARCHAR2(80),
  threat_classification VARCHAR2(20),
  auth_level            NUMBER,
  encounter_count       NUMBER,
  termination_count     NUMBER,
  speed_rating          NUMBER,
  strength_rating       NUMBER,
  patrol_zone           VARCHAR2(80),
  replication_ability   CHAR(1),
  code_signature        VARCHAR2(80),
  host_preference       VARCHAR2(40),
  upgrade_generation    NUMBER,
  rule_bound            CHAR(1)
);

CREATE TABLE MATRIX_LOCATIONS (
  location_id         NUMBER PRIMARY KEY,
  loc_name            VARCHAR2(120),
  security_level      NUMBER,
  hard_line_available CHAR(1),
  agent_response_time NUMBER,
  glitch_frequency    NUMBER,
  civilian_density    NUMBER,
  notable_events      VARCHAR2(200)
);

CREATE TABLE ORACLES (
  oracle_id         NUMBER PRIMARY KEY,
  oracle_identity   VARCHAR2(120),
  location_id       NUMBER REFERENCES MATRIX_LOCATIONS(location_id),
  prophecy_count    NUMBER,
  accuracy_rating   NUMBER,
  protection_level  NUMBER,
  foresight_range   NUMBER,
  choice_emphasis   NUMBER,
  protected_by      VARCHAR2(80),
  cookie_batch_status VARCHAR2(40)
);

CREATE TABLE MISSIONS (
  mission_id              NUMBER PRIMARY KEY,
  mission_name            VARCHAR2(150),
  mission_type            VARCHAR2(60),
  target_location_id      NUMBER REFERENCES MATRIX_LOCATIONS(location_id),
  ship_id                 NUMBER REFERENCES RESISTANCE_SHIPS(ship_id),
  mission_status          VARCHAR2(20),
  start_timestamp         DATE,
  end_timestamp           DATE NULL,
  outcome                 VARCHAR2(200),
  casualties              NUMBER,
  agent_encountered       CHAR(1),
  oracle_guidance_id      NUMBER NULL,
  danger_rating           NUMBER,
  operator_callsign       VARCHAR2(40),
  hard_line_exit_used     NUMBER NULL,
  code_anomaly_detected   CHAR(1),
  bullet_time_events      NUMBER
);

-- optional helpful indexes
CREATE INDEX idx_awakened_ship ON AWAKENED_HUMANS(ship_id);
CREATE INDEX idx_missions_loc ON MISSIONS(target_location_id);
