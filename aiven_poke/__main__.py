import sys

from .main import main

rc = 1
try:
    main()
    rc = 0
except Exception as e:  # noqa: BLE001
    print(f"Error: {e}", file=sys.stderr)
sys.exit(rc)
