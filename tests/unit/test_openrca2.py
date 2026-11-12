"""OpenRCA 2.0, phase 0: the split, the separation of answers, and the access guard."""

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from flowguard.openrca2 import ANSWER_FILES, TELEMETRY_FILES
from flowguard.openrca2 import prepare as prepare_module
from flowguard.openrca2.access import CaseTelemetry, NotAllowed
from flowguard.openrca2.download import hashes
from flowguard.openrca2.prepare import (
    DEV,
    SEED,
    SYSTEMS,
    assign_ids,
    draw_split,
    split_text,
)

REAL = Path(__file__).parents[2] / "data" / "external" / "openrca2"
# Recorded in brief.md, section 33, when the split was made on 2026-11-12.
SPLIT_SHA256 = "74c8e2871481ce963f2e8f1bb8fa5cd98846cc3c62e9ec8c5c104c3c518530ae"


def make_case(root: Path, split: str, case_id: str) -> None:
    """A case laid out as prepare.py leaves it, with stand-in file contents."""
    for kind, files in (("telemetry", TELEMETRY_FILES), ("answers", ANSWER_FILES)):
        folder = root / kind / split / case_id
        folder.mkdir(parents=True)
        for name in files:
            (folder / name).write_text(f"{kind} {case_id} {name}", encoding="utf-8")


@pytest.fixture
def root(tmp_path: Path) -> Path:
    make_case(tmp_path, "dev", "case-001")
    make_case(tmp_path, "dev", "case-002")
    make_case(tmp_path, "held-out", "case-003")
    return tmp_path


# The guard: tool code gets the ten telemetry files of its case and nothing else.


def test_the_ten_telemetry_files_can_be_opened(root: Path) -> None:
    case = CaseTelemetry(root / "telemetry" / "dev", "case-001")
    assert len(case.tables()) == 10
    for name in case.tables():
        path = case.path(name)
        assert path.parent == (root / "telemetry" / "dev" / "case-001").resolve()
        assert path.read_text(encoding="utf-8") == f"telemetry case-001 {name}"


@pytest.mark.parametrize("name", sorted(ANSWER_FILES))
def test_an_answer_file_is_refused_even_when_it_sits_in_the_case_folder(
    root: Path, name: str
) -> None:
    folder = root / "telemetry" / "dev" / "case-001"
    (folder / name).write_text("{}", encoding="utf-8")  # as the download ships it
    with pytest.raises(NotAllowed):
        CaseTelemetry(root / "telemetry" / "dev", "case-001").path(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        ".",
        "..",
        "manifest.jsonl",
        "normal_traces",
        "NORMAL_TRACES.PARQUET",
        "normal_traces.parquet ",
        "normal_traces.parquet.",
        "normal_traces.parquet/../label.json",
        "../case-002/normal_traces.parquet",
        "..\\case-002\\normal_traces.parquet",
        "../../../answers/dev/case-001/label.json",
        "..\\..\\..\\answers\\dev\\case-001\\label.json",
        "normal_traces.parquet\x00.json",
    ],
)
def test_any_other_name_is_refused(root: Path, name: str) -> None:
    with pytest.raises(NotAllowed):
        CaseTelemetry(root / "telemetry" / "dev", "case-001").path(name)


def test_an_absolute_path_is_refused(root: Path) -> None:
    answer = root / "answers" / "dev" / "case-001" / "label.json"
    other = root / "telemetry" / "dev" / "case-002" / "normal_logs.parquet"
    case = CaseTelemetry(root / "telemetry" / "dev", "case-001")
    for path in (answer, other):
        assert path.is_file()
        with pytest.raises(NotAllowed):
            case.path(str(path))


@pytest.mark.parametrize(
    "case_id",
    [
        "",
        ".",
        "..",
        "case-1",
        "case-001/..",
        "../dev/case-001",
        "..\\dev\\case-001",
        "case-999",
        "CASE-001",
    ],
)
def test_only_a_case_id_of_this_split_names_a_case(root: Path, case_id: str) -> None:
    with pytest.raises(NotAllowed):
        CaseTelemetry(root / "telemetry" / "dev", case_id)


def test_the_answers_folder_is_not_a_place_to_open_a_case(root: Path) -> None:
    case = CaseTelemetry(
        root / "answers" / "dev", "case-001"
    )  # a wrong root, by mistake
    for name in sorted(ANSWER_FILES):
        with pytest.raises(NotAllowed):
            case.path(name)
    for name in case.tables():
        with pytest.raises(NotAllowed):
            case.path(name)


def test_a_held_out_case_is_refused_outside_the_final_test(root: Path) -> None:
    with pytest.raises(NotAllowed):
        CaseTelemetry(root / "telemetry" / "held-out", "case-003")
    case = CaseTelemetry(root / "telemetry" / "held-out", "case-003", final_test=True)
    assert case.path("abnormal_logs.parquet").is_file()


def test_a_link_to_an_answer_file_is_refused(root: Path) -> None:
    folder = root / "telemetry" / "dev" / "case-001"
    (folder / "normal_logs.parquet").unlink()
    try:
        (folder / "normal_logs.parquet").symlink_to(
            root / "answers" / "dev" / "case-001" / "label.json"
        )
    except OSError:
        pytest.skip("this account may not create links")
    with pytest.raises(NotAllowed):
        CaseTelemetry(root / "telemetry" / "dev", "case-001").path(
            "normal_logs.parquet"
        )


def test_a_case_folder_that_is_a_link_is_refused(root: Path) -> None:
    try:
        (root / "telemetry" / "dev" / "case-004").symlink_to(
            root / "answers" / "dev" / "case-001", target_is_directory=True
        )
    except OSError:
        pytest.skip("this account may not create links")
    with pytest.raises(NotAllowed):
        CaseTelemetry(root / "telemetry" / "dev", "case-004")


# The IDs and the split.


def names(count: int) -> list[str]:
    return [f"batch-{number:04d}" for number in range(count)]


def test_ids_are_anonymous_and_do_not_follow_the_names() -> None:
    id_of = assign_ids(names(455), SEED)
    assert sorted(id_of.values()) == [f"case-{n:03d}" for n in range(1, 456)]
    assert id_of == assign_ids(list(reversed(names(455))), SEED)
    assert id_of != assign_ids(names(455), SEED + 1)
    in_name_order = [id_of[name] for name in names(455)]
    assert in_name_order != sorted(in_name_order)


def test_the_split_draws_the_set_number_within_each_system() -> None:
    systems = [system for system, count in SYSTEMS.items() for _ in range(count)]
    system_of = dict(
        zip(sorted(assign_ids(names(455), SEED).values()), systems, strict=True)
    )
    split = draw_split(system_of, DEV, SEED, frozenset())
    counts = Counter((system_of[case], part) for case, part in split.items())
    assert {system: counts[system, "dev"] for system in SYSTEMS} == {
        "ts": 60,
        "hs": 33,
        "otel-demo": 7,
    }
    assert {system: counts[system, "held-out"] for system in SYSTEMS} == {
        "ts": 215,
        "hs": 115,
        "otel-demo": 25,
    }
    assert split == draw_split(
        dict(reversed(system_of.items())), DEV, SEED, frozenset()
    )
    assert split != draw_split(system_of, DEV, SEED + 1, frozenset())


def test_a_case_already_seen_goes_to_development_without_adding_to_it() -> None:
    system_of = {f"case-{n:03d}": "hs" for n in range(1, 149)}
    for seen in system_of:
        split = draw_split(system_of, {"hs": 33}, SEED, frozenset({seen}))
        assert split[seen] == "dev"
        assert Counter(split.values()) == {"dev": 33, "held-out": 115}


def test_the_split_file_says_only_id_system_and_split() -> None:
    system_of = {"case-001": "ts", "case-002": "hs"}
    body = json.loads(
        split_text(system_of, {"case-001": "dev", "case-002": "held-out"}, SEED)
    )
    assert set(body) == {"dataset", "commit", "seed", "cases"}
    assert body["cases"] == [
        {"id": "case-001", "system": "ts", "split": "dev"},
        {"id": "case-002", "system": "hs", "split": "held-out"},
    ]


def test_preparing_moves_the_answers_out_and_prints_no_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    systems = {"ts": 6, "hs": 4}
    records = [
        {
            "name": f"batch-{system}-{n}",
            "system": system,
            "root_services": ["secret-service"],
            "chaos_types": ["SecretFault"],
        }
        for system, count in systems.items()
        for n in range(count)
    ]
    raw = tmp_path / "raw"
    lines = []
    for record in records:
        folder = raw / "cases" / record["name"]
        folder.mkdir(parents=True)
        for file in TELEMETRY_FILES | ANSWER_FILES:
            (folder / file).write_text(f"{record['name']} {file}", encoding="utf-8")
            lines.append(f"{hashes(folder / file)[0]}  cases/{record['name']}/{file}\n")
    (raw / "manifest.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8"
    )
    (tmp_path / "answers" / "all-cases").mkdir(parents=True)
    (tmp_path / "answers" / "all-cases" / "download.sha256").write_text(
        "".join(lines), encoding="utf-8"
    )

    monkeypatch.setattr(prepare_module, "SYSTEMS", systems)
    monkeypatch.setattr(prepare_module, "DEV", {"ts": 2, "hs": 1})
    monkeypatch.setattr(prepare_module, "SEEN_IN_README", "batch-hs-0")
    monkeypatch.setattr("sys.argv", ["prepare", "--root", str(tmp_path)])
    assert prepare_module.main() == 0
    monkeypatch.setattr("sys.argv", ["prepare", "--root", str(tmp_path), "--verify"])
    assert prepare_module.main() == 0

    printed = capsys.readouterr().out
    assert "batch-" not in printed and "secret" not in printed.lower()
    assert "case-0" not in printed

    split = {
        c["id"]: c
        for c in json.loads((tmp_path / "split.json").read_text(encoding="utf-8"))[
            "cases"
        ]
    }
    assert Counter((c["system"], c["split"]) for c in split.values()) == {
        ("ts", "dev"): 2, ("ts", "held-out"): 4, ("hs", "dev"): 1, ("hs", "held-out"): 3,
    }  # fmt: skip
    ids = json.loads(
        (tmp_path / "answers" / "all-cases" / "case-ids.json").read_text(
            encoding="utf-8"
        )
    )
    assert split[ids["id_of_folder"]["batch-hs-0"]]["split"] == "dev"
    assert not (raw / "cases").exists() and not (raw / "manifest.jsonl").exists()
    for case in split.values():
        telemetry = tmp_path / "telemetry" / case["split"] / case["id"]
        answers = tmp_path / "answers" / case["split"] / case["id"]
        assert {f.name for f in telemetry.iterdir()} == TELEMETRY_FILES
        assert {f.name for f in answers.iterdir()} == ANSWER_FILES

    # The split is made once.
    monkeypatch.setattr("sys.argv", ["prepare", "--root", str(tmp_path)])
    with pytest.raises(SystemExit):
        prepare_module.main()


# The real data, where it has been downloaded and prepared. Counts and names of
# files only: no case is opened.


@pytest.mark.skipif(
    not (REAL / "split.json").is_file(), reason="OpenRCA 2.0 is not on this machine"
)
class TestRealData:
    def test_the_split_file_is_the_one_recorded(self) -> None:
        text = (REAL / "split.json").read_bytes()
        assert hashlib.sha256(text).hexdigest() == SPLIT_SHA256
        cases = json.loads(text)["cases"]
        counts = Counter((case["system"], case["split"]) for case in cases)
        assert {s: counts[s, "dev"] for s in SYSTEMS} == DEV
        assert {s: counts[s, "dev"] + counts[s, "held-out"] for s in SYSTEMS} == SYSTEMS

    def test_the_telemetry_folders_hold_only_telemetry(self) -> None:
        split = {
            c["id"]: c["split"]
            for c in json.loads((REAL / "split.json").read_text(encoding="utf-8"))[
                "cases"
            ]
        }
        for part in ("dev", "held-out"):
            folders = list((REAL / "telemetry" / part).iterdir())
            assert {f.name for f in folders} == {
                case for case, its in split.items() if its == part
            }
            for folder in folders:
                assert {f.name for f in folder.iterdir()} == TELEMETRY_FILES
        everything = [p for p in (REAL / "telemetry").rglob("*") if p.is_file()]
        assert len(everything) == 4550
        assert not [p for p in everything if p.suffix != ".parquet"]

    def test_no_answer_file_is_left_beside_the_download(self) -> None:
        assert not (REAL / "raw" / "cases").exists()
        assert not (REAL / "raw" / "manifest.jsonl").exists()
        for name in ANSWER_FILES:
            assert not list((REAL / "raw").rglob(name))
            assert not list((REAL / "telemetry").rglob(name))
