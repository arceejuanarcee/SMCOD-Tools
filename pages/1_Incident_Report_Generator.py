# pages/1_Incident_Report_Generator.py
import runpy
from pathlib import Path
from auth import require_login

require_login()  # ✅ if not logged in, it redirects to app.py

ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "IR_gen.py"), run_name="__main__")
