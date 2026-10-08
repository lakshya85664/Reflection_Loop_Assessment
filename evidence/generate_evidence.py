"""
Topic 12 — Evidence Generation

Generates reproducible JSON evidence for all five tasks.
"""

import json
import sys
from pathlib import Path


# ---------------------------------------------------------
# Add project root to Python's import path.
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.reflection_loop import (
    critique,
    revise,
    reflection_loop,
    reflection_loop_with_critic,
)

from task5_metrics import DRAFTS, run_reflection


EVIDENCE_DIR = Path(__file__).resolve().parent


def write_json(filename, data):
    """
    Write evidence data as formatted JSON.
    """

    path = EVIDENCE_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Created: {path}")


def task1_evidence():
    """
    Task 1 — Critique evidence.
    """

    text = "This system works correctly"

    return {
        "task": 1,
        "name": "Critique",
        "input": text,
        "issues": critique(text),
        "rules": {
            "max_words": 12,
            "min_words": 3,
            "must_include": "agent",
            "must_end_with": ".",
        },
    }


def task2_evidence():
    """
    Task 2 — Revision evidence.
    """

    original = "This system works correctly"

    issues = critique(original)
    revised = revise(original, issues)

    return {
        "task": 2,
        "name": "Revision",
        "original": original,
        "issues": issues,
        "revised": revised,
        "remaining_issues": critique(revised),
    }


def task3_evidence():
    """
    Task 3 — Reflection loop evidence.
    """

    result = reflection_loop(
        "describe software",
        max_rounds=3,
    )

    return {
        "task": 3,
        "name": "Reflection Loop",
        "result": result,
    }


def task4_evidence():
    """
    Task 4 — Non-convergence evidence.
    """

    def impossible_critic(text):
        return ["impossible_issue"]

    def ineffective_reviser(text, issues):
        return text

    result = reflection_loop_with_critic(
        "describe software",
        max_rounds=3,
        critic=impossible_critic,
        reviser=ineffective_reviser,
    )

    return {
        "task": 4,
        "name": "Non-Convergence",
        "result": result,
        "expected_behavior": {
            "converged": False,
            "rounds": 3,
            "termination": "max_rounds",
        },
    }


def task5_evidence():
    """
    Task 5 — Reflection value measurement across 10 drafts.
    """

    results = []

    total_before = 0
    total_after = 0
    converged = 0
    total_rounds = 0

    for index, draft in enumerate(DRAFTS, start=1):

        before = critique(draft)

        result = run_reflection(draft)

        after = critique(result["final"])

        total_before += len(before)
        total_after += len(after)
        total_rounds += result["rounds"]

        if result["converged"]:
            converged += 1

        results.append(
            {
                "draft": index,
                "original": draft,
                "before_issues": before,
                "final": result["final"],
                "after_issues": after,
                "rounds": result["rounds"],
                "converged": result["converged"],
            }
        )

    total = len(DRAFTS)

    return {
        "task": 5,
        "name": "Reflection Value Measurement",
        "total_drafts": total,
        "converged": converged,
        "convergence_rate_percent": (
            converged / total * 100
        ),
        "total_issues_before": total_before,
        "total_issues_after": total_after,
        "average_issues_before": (
            total_before / total
        ),
        "average_issues_after": (
            total_after / total
        ),
        "issue_reduction_percent": (
            (total_before - total_after)
            / total_before
            * 100
        ),
        "average_rounds": (
            total_rounds / total
        ),
        "results": results,
    }


def main():
    """
    Generate evidence for all five tasks.
    """

    print("Topic 12 — Evidence Generation")
    print("=" * 60)

    write_json(
        "task1_critique.json",
        task1_evidence(),
    )

    write_json(
        "task2_revision.json",
        task2_evidence(),
    )

    write_json(
        "task3_reflection_loop.json",
        task3_evidence(),
    )

    write_json(
        "task4_non_convergence.json",
        task4_evidence(),
    )

    write_json(
        "task5_metrics.json",
        task5_evidence(),
    )

    print("=" * 60)
    print("Evidence generation complete.")


if __name__ == "__main__":
    main()