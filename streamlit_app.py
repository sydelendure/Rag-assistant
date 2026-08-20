"""
Streamlit Cloud Default Entrypoint.
Routes execution directly to ui.py.
"""
import runpy
from pathlib import Path

ui_path = Path(__file__).parent / "ui.py"
runpy.run_path(str(ui_path), run_name="__main__")
