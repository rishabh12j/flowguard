"""The one way tool code reaches a case's files on OpenRCA 2.0.

A tool is handed a `CaseTelemetry` and asks it for a table's path. It gives out
the paths of the case's ten telemetry parquet files and nothing else: no answer
file, no other case, no folder above the case. The answers are kept in another
folder as well (see prepare.py); this is the second barrier, for a mistake or a
path a model makes up.

It covers paths that Python code opens. A query engine that can read files named
inside a query has to have that turned off where the engine is set up.
"""

import re
from pathlib import Path

from flowguard.openrca2 import TELEMETRY_FILES

CASE_ID = re.compile(r"case-\d{3,}")
HELD_OUT = "held-out"


class NotAllowed(PermissionError):
    """Tool code asked for something other than a case's telemetry."""


class CaseTelemetry:
    """A case's ten telemetry files, by name.

    `root` is one split's telemetry folder, such as `.../telemetry/dev`. The
    held-out folder is refused unless `final_test` is set, which only the one
    test run does.
    """

    def __init__(self, root: Path, case_id: str, *, final_test: bool = False) -> None:
        if not CASE_ID.fullmatch(case_id):
            raise NotAllowed(f"not a case ID: {case_id!r}")
        root = root.resolve(strict=True)
        if root.name == HELD_OUT and not final_test:
            raise NotAllowed("held-out cases are opened only by the final test")
        folder = root / case_id
        if (
            folder.is_symlink()
            or not folder.is_dir()
            or folder.resolve().parent != root
        ):
            raise NotAllowed(f"no such case: {case_id}")
        self.case_id = case_id
        self._folder = folder

    def tables(self) -> list[str]:
        """The names that `path` accepts: always the same ten."""
        return sorted(TELEMETRY_FILES)

    def path(self, name: str) -> Path:
        """Where one telemetry file is. `name` is one of the ten file names, exactly."""
        if name not in TELEMETRY_FILES:
            raise NotAllowed(f"not a telemetry file: {name!r}")
        file = self._folder / name
        # A link planted in the folder could point at an answer file.
        if (
            file.is_symlink()
            or not file.is_file()
            or file.resolve().parent != self._folder
        ):
            raise NotAllowed(f"not a telemetry file: {name!r}")
        return file
