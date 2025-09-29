import os
import time
import random
from datetime import datetime, timedelta

from faker import Faker
import oracledb

fake = Faker()

# --- Env / connection ---
db_host = os.getenv("ORACLE_HOST", "oracle-xe")
db_port = int(os.getenv("ORACLE_PORT", "1521"))
db_service = os.getenv("ORACLE_SERVICE", "XEPDB1")  # service name
db_user = os.getenv("ORACLE_USER", "MATRIX_USER")
db_password = os.getenv("ORACLE_PASSWORD", "Neo2025")
RESET = os.getenv("RESET_DATA", "0") == "1"

dsn = f"{db_host}:{db_port}/{db_service}"
print(f"Connecting to {db_user}@{db_host}:{db_port}/{db_service}")

# --- Wait for DB ---
conn = None
for attempt in range(60):
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=dsn)
        with conn.cursor() as c:
            c.execute("SELECT 1 FROM DUAL")
        print("DB ready.")
        break
    except Exception as e:
        print(f"[{attempt+1}/60] DB not ready yet: {e}")
        time.sleep(10)
else:
    raise RuntimeError("Database not ready after 10 minutes")

def random_date(start_year=1999, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return fake.date_time_between(start_date=start, end_date=end)

try:
    cur = conn.cursor()

    # Optional: clear tables for idempotency
    if RESET:
        print("RESET_DATA=1 - > clearing tables (child ? parent to satisfy FKs)...")
        for t in ["MISSIONS",
                  "AWAKENED_HUMANS",
                  "ORACLES",
                  "MATRIX_LOCATIONS",
                  "AGENTS",
                  "SLEEPERS",
                  "RESISTANCE_SHIPS"]:
            cur.execute(f"DELETE FROM {t}")
        conn.commit()
        print("Tables cleared.")

    # -------------------------
    # RESISTANCE_SHIPS (25)
    # -------------------------
    ships = [
        (1, 'Nebuchadnezzar', 'Mark III', 'X:100,Y:200,Z:300', 80, 12, 5000, 'Optimal'),
        (2, 'Logos', 'Mark IV', 'X:150,Y:250,Z:350', 60, 10, 4800, 'Damaged'),
        (3, 'Mjolnir', 'Prototype', 'X:200,Y:300,Z:400', 90, 15, 5200, 'Optimal'),
    ]
    for i in range(4, 26):
        ships.append((
            i,
            f"Ship_{i}",
            random.choice(['Mark III', 'Mark IV', 'Prototype']),
            f"X:{random.randint(0,1000)},Y:{random.randint(0,1000)},Z:{random.randint(0,1000)}",
            random.randint(50, 100),
            random.randint(8, 20),
            random.randint(4000, 6000),
            random.choice(['Optimal', 'Damaged', 'Critical']),
        ))
    cur.executemany("""
        INSERT INTO RESISTANCE_SHIPS
        (ship_id, ship_name, ship_class, coordinates, emp_charge_status, crew_capacity, last_broadcast_depth, operational_condition)
        VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
    """, ships)
    print(f"Inserted ships: {len(ships)}")

    # -------------------------
    # AWAKENED_HUMANS (400)
    # -------------------------
    humans = [
        (1, 'Thomas Anderson', 'Neo', 'Fighter', 90, random_date(1999, 1999), 1, 'Kung Fu Master', 50, 'Y', None, 200, 5),
        (2, 'Morpheus', 'Morpheus', 'Commander', 95, random_date(1995, 1999), 1, 'Leadership', 30, 'N', None, 150, 5),
        (3, 'Trinity', 'Trinity', 'Fighter', 85, random_date(1997, 1999), 1, 'Infiltration Expert', 40, 'Y', 2, 180, 4),
    ]
    roles = ['Commander', 'Operator', 'Fighter', 'Medic']
    specialties = ['Kung Fu Master', 'Code Breaker', 'Weapons Expert', 'Medic Specialist', 'Pilot']
    for i in range(4, 401):
        mentor = random.randint(1, i-1) if i > 1 and random.random() > 0.2 else None
        humans.append((
            i, fake.name(), f"RSI_{i}", random.choice(roles), random.randint(50, 100),
            random_date(1995, 2025), random.randint(1, 25), random.choice(specialties),
            random.randint(0, 100), random.choice(['Y', 'N']), mentor,
            random.randint(50, 300), random.randint(1, 5),
        ))
    cur.executemany("""
        INSERT INTO AWAKENED_HUMANS
        (human_id, real_name, rsi_name, role, mental_stability, awakening_date, ship_id, specialty_skill, jack_in_count, in_matrix, mentor_id, construct_training_hours, belief_level)
        VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13)
    """, humans)
    print(f"Inserted humans: {len(humans)}")

    # -------------------------
    # SLEEPERS (3000)
    # -------------------------
    sleepers = []
    occupations = ['Accountant', 'Office Worker', 'Police Officer', 'Teacher', 'Programmer']
    for i in range(1, 3001):
        sleepers.append((
            i, fake.name(), random.choice(occupations), f"Sector_{random.randint(1,50)},Pod_{i}",
            random.randint(80,100), random.randint(5,50), random.randint(0,100),
            random.randint(0,100), random.randint(0,5), random.randint(0,20),
        ))
    # executemany is fine for 3k rows
    cur.executemany("""
        INSERT INTO SLEEPERS
        (sleeper_id, simulated_identity, matrix_occupation, pod_location, connection_stability, years_connected, awakening_potential, extraction_priority, anomaly_flags, rejection_risk)
        VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)
    """, sleepers)
    print(f"Inserted sleepers: {len(sleepers)}")

    # -------------------------
    # AGENTS (30)
    # -------------------------
    agents = [
        (1, 'Agent_Smith_001', 'Critical', 8, 20, 5, 9, 9, 'Downtown', 'Y', 'SMITH_V1', 'Businessmen', 2, 'N'),
        (2, 'Agent_Jones_001', 'High', 6, 10, 2, 7, 8, 'Subway', 'N', 'JONES_V1', 'Police', 1, 'Y'),
    ]
    for i in range(3, 31):
        agents.append((
            i, f"Agent_{fake.last_name()}_{i:03d}", random.choice(['Low','Medium','High']),
            random.randint(1,10), random.randint(0,50), random.randint(0,10),
            random.randint(1,10), random.randint(1,10), fake.street_name(),
            random.choice(['Y','N']), f"CODE_{i}", random.choice(['Businessmen','Police','Civilians']),
            random.randint(1,3), random.choice(['Y','N']),
        ))
    cur.executemany("""
        INSERT INTO AGENTS
        (agent_id, designation_code, threat_classification, auth_level, encounter_count, termination_count, speed_rating, strength_rating, patrol_zone, replication_ability, code_signature, host_preference, upgrade_generation, rule_bound)
        VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14)
    """, agents)
    print(f"Inserted agents: {len(agents)}")

    # -------------------------
    # MATRIX_LOCATIONS (150)
    # -------------------------
    locations = [
        (1, 'Corporate Lobby', 3, 'Y', 30, 5, 500, 'Agent Smith confrontation'),
        (2, 'Rooftop Helipad', 4, 'N', 20, 10, 50, 'Bullet time event'),
        (3, 'Oracle Apartment', 2, 'Y', 60, 2, 100, 'Prophecy delivered'),
    ]
    loc_names = ['Subway Station', 'Warehouse', 'Government Building', 'Alley', 'Nightclub']
    for i in range(4, 151):
        locations.append((
            i, f"{random.choice(loc_names)}_{i}", random.randint(1,5),
            random.choice(['Y','N']), random.randint(10,120), random.randint(0,20),
            random.randint(0,1000), f"Event_{i}",
        ))
    cur.executemany("""
        INSERT INTO MATRIX_LOCATIONS
        (location_id, loc_name, security_level, hard_line_available, agent_response_time, glitch_frequency, civilian_density, notable_events)
        VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
    """, locations)
    print(f"Inserted locations: {len(locations)}")

    # -------------------------
    # ORACLES (5)
    # -------------------------
    oracles = [
        (1, 'The Oracle', 3, 50, 95, 3, 30, 5, 'Seraph', 'Fresh'),
        (2, 'Oracle_Beta', 3, 30, 80, 2, 20, 4, 'Guardian_2', 'Baking'),
    ]
    for i in range(3, 6):
        oracles.append((
            i, f"Oracle_{i}", random.randint(1,150), random.randint(10,100),
            random.randint(70,95), random.randint(1,5), random.randint(10,60),
            random.randint(1,5), f"Guardian_{i}", random.choice(['Fresh','Baking','None']),
        ))
    cur.executemany("""
        INSERT INTO ORACLES
        (oracle_id, oracle_identity, location_id, prophecy_count, accuracy_rating, protection_level, foresight_range, choice_emphasis, protected_by, cookie_batch_status)
        VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)
    """, oracles)
    print(f"Inserted oracles: {len(oracles)}")

    # -------------------------
    # MISSIONS
    # -------------------------
    
    missions_buffer = [
        (1, 'Rescue Neo', 'Extraction', 1, 1, 'Success', random_date(1999, 1999), random_date(1999, 1999), 'Neo freed', 0, 'Y', 1, 3, 'Switch', 1, 'N', 2),
        (2, 'Oracle Consult', 'Oracle Consultation', 3, 1, 'Success', random_date(1999, 1999), random_date(1999, 1999), 'Prophecy received', 0, 'N', 1, 2, 'Apoc', 3, 'Y', 0),
    ]
    mission_types = ['Extraction','Sabotage','Oracle Consultation','Agent Evasion','Intelligence Gathering']
    callsigns = ['Switch','Apoc','Cypher','Mouse','Dozer']

    def flush_missions(buf):
        if not buf:
            return
        cur.executemany("""
            INSERT INTO MISSIONS
            (mission_id, mission_name, mission_type, target_location_id, ship_id, mission_status,
             start_timestamp, end_timestamp, outcome, casualties, agent_encountered, oracle_guidance_id,
             danger_rating, operator_callsign, hard_line_exit_used, code_anomaly_detected, bullet_time_events)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17)
        """, buf)
        print(f"Inserted missions chunk: {len(buf)}")

    for i in range(3, 6401):
        start = random_date(1995, 2025)
        end = start + timedelta(days=random.randint(0,7)) if random.random() > 0.2 else None
        missions_buffer.append((
            i, f"Mission_{i}", random.choice(mission_types), random.randint(1,150),
            random.randint(1,25), random.choice(['Planned','Active','Success','Failed']),
            start, end, f"Outcome_{i}", random.randint(0,5), random.choice(['Y','N']),
            random.randint(1,5) if random.random() > 0.7 else None, random.randint(1,5),
            random.choice(callsigns), random.randint(1,150) if random.random() > 0.5 else None,
            random.choice(['Y','N']), random.randint(0,3),
        ))
        if len(missions_buffer) >= 1000:
            flush_missions(missions_buffer)
            missions_buffer = []
    flush_missions(missions_buffer)

    conn.commit()
    print("Data generation complete!")

except Exception as e:
    print(f"Error during data generation: {e}")
    raise
finally:
    try:
        cur.close()
        print("Cursor closed.")
    except Exception:
        pass
    try:
        conn.close()
        print("Connection closed.")
    except Exception:
        pass
