"""Bundle entry point. py2app runs this as __main__, so it cannot use relative imports."""

import sys

from window_manager.app import main

if __name__ == "__main__":
    sys.exit(main())
