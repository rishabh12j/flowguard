"""The checker passes a sound benchmark and catches a broken one.

It can't catch a wrong category label: the oracle answers from the ground truth,
so a mislabelled incident agrees with itself. The checker proves the data
supports each ground truth; the labels come from the family definitions.
"""

import json

import pytest

from flowguard.benchmark.check import check
from flowguard.benchmark.generate import generate, write

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def benchmark(tmp_path):
    # One incident per family: every family, both splits.
    write(generate(11, dev_variants=1, test_cases=11), tmp_path, 11)
    return tmp_path


def first_to_diagnose(benchmark):
    for path in sorted((benchmark / "ground_truth").glob("*.json")):
        truth = json.loads(path.read_text(encoding="utf-8"))
        if truth["expected_outcome"] == "diagnose":
            return path, truth
    raise AssertionError("no incident to diagnose")


async def test_a_generated_benchmark_passes(benchmark):
    assert await check(benchmark) == []


async def test_a_plan_that_cant_pass_validation_is_caught(benchmark):
    path, truth = first_to_diagnose(benchmark)
    truth["reference_plan"][0]["target"] = "a-service-that-isnt-there"
    path.write_text(json.dumps(truth), encoding="utf-8")

    problems = await check(benchmark)

    assert problems
    assert all(problem.startswith(truth["incident_id"]) for problem in problems)


async def test_required_evidence_that_doesnt_exist_is_caught(benchmark):
    path, truth = first_to_diagnose(benchmark)
    truth["required_evidence_ids"].append("LOG-99999")
    path.write_text(json.dumps(truth), encoding="utf-8")

    problems = await check(benchmark)

    assert any("required evidence not gathered: ['LOG-99999']" in p for p in problems)
