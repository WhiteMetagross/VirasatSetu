import os
import sys

# Add project root directory to sys.path so app modules are resolvable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
