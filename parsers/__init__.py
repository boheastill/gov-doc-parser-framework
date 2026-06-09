"""Source parsers. Importing this package registers every implemented parser.

Add a new source by creating `parsers/<source>.py` (copy `_template.py`) and
importing it here so it self-registers.
"""
from . import irishstatutebook  # noqa: F401  (registers on import)

__all__ = ["irishstatutebook"]
