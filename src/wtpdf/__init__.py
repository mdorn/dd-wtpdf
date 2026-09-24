import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main() -> None:
    app_path = str(Path(__file__).parent / "app.py")
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())
