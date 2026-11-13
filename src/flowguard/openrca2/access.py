"""The one way tool code reaches a case's files on OpenRCA 2.0.

A tool is handed a `CaseTelemetry` and asks it for a table's path. It gives out
the paths of the case's ten telemetry parquet files and nothing else: no answer
file, no other case, no folder above the case. The answers are kept in another
folder as well (see prepare.py); this is the second barrier, for a mistake or a
path a model makes up.

For SQL, `connect` gives a DuckDB connection with one view per table, named
after its file (`abnormal_traces`), that can read those ten files and nothing
else: DuckDB's external access is turned off with the ten paths as the only
exceptions, and the configuration is locked so a query cannot turn it back on.
"""

import re
from pathlib import Path
from typing import TYPE_CHECKING

from flowguard.openrca2 import TELEMETRY_FILES

if TYPE_CHECKING:
    import duckdb

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

    def connect(
        self, *, underscore_columns: bool = False
    ) -> "duckdb.DuckDBPyConnection":
        """An in-memory DuckDB connection that can read this case's ten tables only.

        Each table is a view named after its file without `.parquet`. Any other
        file, a glob, ATTACH, COPY, an extension, or changing a setting fails.
        With `underscore_columns`, dots in column names become underscores
        (`attr.status_code` is `attr_status_code`), as the standard agent's
        tools show them.
        """
        import duckdb

        paths = {name: self.path(name).as_posix() for name in self.tables()}
        con = duckdb.connect(":memory:")
        allowed = ", ".join(_quote(path) for path in paths.values())
        con.execute(f"SET allowed_paths = [{allowed}]")
        con.execute("SET enable_external_access = false")
        con.execute("SET lock_configuration = true")
        for name, path in paths.items():
            view = name.removesuffix(".parquet")
            source = f"read_parquet({_quote(path)})"
            columns = "*"
            if underscore_columns:
                names = [
                    d[0]
                    for d in con.execute(f"SELECT * FROM {source} LIMIT 0").description
                ]
                columns = ", ".join(
                    f"{_ident(c)} AS {_ident(c.replace('.', '_'))}" for c in names
                )
            con.execute(f"CREATE VIEW {view} AS SELECT {columns} FROM {source}")
        return con


def _quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def _ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'
