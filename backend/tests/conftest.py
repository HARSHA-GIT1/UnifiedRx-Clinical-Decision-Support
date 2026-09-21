import sys
import os

# Ensure the project root (backend) is on the PYTHONPATH so that imports like
# `from app.services...` work when pytest is executed from the `backend` directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
