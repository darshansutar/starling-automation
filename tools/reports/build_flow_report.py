"""Compatibility entrypoint. Historical dated exports are archives, not current instructions."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_explanation_report.py')), run_name="__main__")
