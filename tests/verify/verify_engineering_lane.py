"""Deprecated alias — use ``tests.verify.verify_implement_lane``.

Kept so older runbooks / configs that invoke this module still work.
"""

from __future__ import annotations

import sys

from tests.verify.verify_implement_lane import main

if __name__ == "__main__":
    print(
        "[WARNING] verify_engineering_lane is deprecated; "
        "use python -m tests.verify.verify_implement_lane"
    )
    sys.exit(main())
