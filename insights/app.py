import os
from typing import Any, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import oracledb

# --- Oracle connection config ---
ORACLE_HOST = os.getenv("ORACLE_HOST", "oracle-xe")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "XEPDB1")
ORACLE_USER = os.getenv("ORACLE_USER", "MATRIX_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "Neo2025")
DSN = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"

# --- Template engine ---
env = Environment(loader=FileSystemLoader("templates"), auto_reload=True, cache_size=0)

# --- Lifespan for startup/shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = None  # pool created lazily
    try:
        yield
    finally:
        pool = getattr(app.state, "pool", None)
        if pool is not None:
            try:
                pool.close()
            except Exception:
                pass

# --- App ---
app = FastAPI(title="Matrix Insights API", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Helpers ---
def _get_pool():
    if app.state.pool is None:
        app.state.pool = oracledb.create_pool(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=DSN,
            min=1,
            max=4,
            increment=1,
            getmode=oracledb.SPOOL_ATTRVAL_WAIT,
        )
    return app.state.pool

def run_query(sql: str, binds: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    pool = _get_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, binds or {})
            cols = [d[0].lower() for d in cur.description]   # force lowercase
            return [dict(zip(cols, row)) for row in cur.fetchall()]


# --- Routes ---
@app.get("/health")
def health():
    _get_pool()  # touch pool
    return {"status": "ok"}

@app.get("/insights")
def insights():
    q1 = """
    SELECT s.ship_id, s.ship_name, COUNT(m.mission_id) AS missions
    FROM RESISTANCE_SHIPS s
    LEFT JOIN MISSIONS m ON m.ship_id = s.ship_id
    GROUP BY s.ship_id, s.ship_name
    ORDER BY missions DESC
    FETCH FIRST 5 ROWS ONLY
    """
    q2 = """
    SELECT l.location_id, l.loc_name, COUNT(*) AS encounters
    FROM MISSIONS m
    JOIN MATRIX_LOCATIONS l ON l.location_id = m.target_location_id
    WHERE m.agent_encountered = 'Y'
    GROUP BY l.location_id, l.loc_name
    ORDER BY encounters DESC
    FETCH FIRST 10 ROWS ONLY
    """
    q3 = """
    SELECT s.ship_id, s.ship_name,
           AVG(a.construct_training_hours) AS avg_training_hours,
           AVG(a.belief_level)            AS avg_belief
    FROM RESISTANCE_SHIPS s
    JOIN AWAKENED_HUMANS a ON a.ship_id = s.ship_id
    GROUP BY s.ship_id, s.ship_name
    ORDER BY avg_training_hours DESC
    FETCH FIRST 10 ROWS ONLY
    """
    q4 = """
    SELECT CASE WHEN m.oracle_guidance_id IS NULL THEN 'No Oracle' ELSE 'Oracle' END AS guidance,
           COUNT(*) AS missions,
           ROUND(100 * AVG(CASE WHEN m.mission_status = 'Success' THEN 1 ELSE 0 END), 1) AS success_pct
    FROM MISSIONS m
    GROUP BY CASE WHEN m.oracle_guidance_id IS NULL THEN 'No Oracle' ELSE 'Oracle' END
    """


    # q5: notable humans (top jack-ins), with mentor & ship
    q5 = """
    SELECT h.human_id,
           h.real_name,
           h.rsi_name,
           s.ship_name,
           h.jack_in_count,
           m.real_name AS mentor_name
    FROM AWAKENED_HUMANS h
    LEFT JOIN AWAKENED_HUMANS m ON m.human_id = h.mentor_id
    LEFT JOIN RESISTANCE_SHIPS s ON s.ship_id = h.ship_id
    ORDER BY h.jack_in_count DESC
    FETCH FIRST 5 ROWS ONLY
    """

    # q6: recent missions that had oracle guidance, show names and where
    q6 = """
    SELECT m.mission_id,
           m.mission_name,
           TO_CHAR(m.start_timestamp, 'YYYY-MM-DD') AS start_date,
           s.ship_name,
           l.loc_name,
           o.oracle_identity
    FROM MISSIONS m
    JOIN RESISTANCE_SHIPS s ON s.ship_id = m.ship_id
    JOIN MATRIX_LOCATIONS l ON l.location_id = m.target_location_id
    JOIN ORACLES o ON o.oracle_id = m.oracle_guidance_id
    WHERE m.oracle_guidance_id IS NOT NULL
    ORDER BY m.start_timestamp DESC NULLS LAST
    FETCH FIRST 5 ROWS ONLY
    """

    # q7: top agents by termination_count (with threat class & preferences)
    q7 = """
    SELECT agent_id,
           designation_code,
           threat_classification,
           termination_count,
           host_preference,
           patrol_zone
    FROM AGENTS
    ORDER BY termination_count DESC, encounter_count DESC
    FETCH FIRST 5 ROWS ONLY
    """

    return {
        "busiest_ships": run_query(q1),
        "agent_hotspots": run_query(q2),
        "training_by_ship": run_query(q3),
        "oracle_success": run_query(q4),

        # NEW:
        "notable_humans": run_query(q5),
        "oracle_guided_examples": run_query(q6),
        "top_agents": run_query(q7),
    }    


    

@app.get("/stats")
def stats():
    counts = {
        "ships":     run_query("SELECT COUNT(*) c FROM RESISTANCE_SHIPS")[0]["c"],
        "humans":    run_query("SELECT COUNT(*) c FROM AWAKENED_HUMANS")[0]["c"],
        "sleepers":  run_query("SELECT COUNT(*) c FROM SLEEPERS")[0]["c"],
        "agents":    run_query("SELECT COUNT(*) c FROM AGENTS")[0]["c"],
        "locations": run_query("SELECT COUNT(*) c FROM MATRIX_LOCATIONS")[0]["c"],
        "oracles":   run_query("SELECT COUNT(*) c FROM ORACLES")[0]["c"],
        "missions":  run_query("SELECT COUNT(*) c FROM MISSIONS")[0]["c"],
    }
    counts["total_rows"] = sum(counts.values())
    return counts


@app.get("/", response_class=HTMLResponse)
def home():
    data = insights()
    tmpl = env.get_template("index.html")
    return tmpl.render(**data)
