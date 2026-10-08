"""
Topic 12 — Task 5: Measuring Reflection Value

Evaluates reflection across 10 deterministic drafts.
"""

from src.reflection_loop import critique, revise


DRAFTS = [
    "This agent works correctly.",
    "This system works correctly",
    "Short.",
    "This agent is a very long sentence that contains many extra words beyond the limit.",
    "The system performs the required operation correctly.",
    "Agent.",
    "This agent handles requests correctly.",
    "A very short",
    "This agent provides a useful response without issues.",
    "This is another long example sentence containing many words that exceed the configured limit",
]


def run_reflection(draft: str, max_rounds: int = 5) -> dict:
    """
    Run the same deterministic reflection process used by the project.
    """

    current = draft
    history = []

    for round_number in range(1, max_rounds + 1):
        issues = critique(current)

        history.append(
            {
                "round": round_number,
                "text": current,
                "issues": issues.copy(),
            }
        )

        if not issues:
            return {
                "final": current,
                "rounds": round_number,
                "converged": True,
                "history": history,
            }

        current = revise(current, issues)

    return {
        "final": current,
        "rounds": max_rounds,
        "converged": False,
        "history": history,
    }


def evaluate():
    """
    Measure the effect of reflection across all ten drafts.
    """

    total_before_issues = 0
    total_after_issues = 0
    initially_valid = 0
    converged = 0
    total_rounds = 0

    results = []

    for index, draft in enumerate(DRAFTS, start=1):

        before_issues = critique(draft)

        reflection = run_reflection(draft)

        after_issues = critique(reflection["final"])

        total_before_issues += len(before_issues)
        total_after_issues += len(after_issues)

        if not before_issues:
            initially_valid += 1

        if reflection["converged"]:
            converged += 1

        total_rounds += reflection["rounds"]

        results.append(
            {
                "draft": index,
                "before_issues": before_issues,
                "after_issues": after_issues,
                "rounds": reflection["rounds"],
                "converged": reflection["converged"],
                "final": reflection["final"],
            }
        )

    total = len(DRAFTS)

    average_before = total_before_issues / total
    average_after = total_after_issues / total

    if total_before_issues == 0:
        issue_reduction = 0.0
    else:
        issue_reduction = (
            (total_before_issues - total_after_issues)
            / total_before_issues
            * 100
        )

    convergence_rate = converged / total * 100

    average_rounds = total_rounds / total

    print("=" * 70)
    print("Topic 12 — Task 5: Reflection Value Measurement")
    print("=" * 70)

    print(f"Total drafts: {total}")
    print(f"Initially valid drafts: {initially_valid}")
    print(f"Converged drafts: {converged}/{total}")
    print(f"Convergence rate: {convergence_rate:.1f}%")
    print()

    print(f"Total issues before reflection: {total_before_issues}")
    print(f"Total issues after reflection:  {total_after_issues}")
    print(f"Average issues before:          {average_before:.2f}")
    print(f"Average issues after:           {average_after:.2f}")
    print(f"Issue reduction:                {issue_reduction:.1f}%")
    print(f"Average rounds:                 {average_rounds:.2f}")
    print()

    print("-" * 70)
    print("Per-draft results")
    print("-" * 70)

    for result in results:
        print(
            f"Draft {result['draft']:02d} | "
            f"before={len(result['before_issues'])} | "
            f"after={len(result['after_issues'])} | "
            f"rounds={result['rounds']} | "
            f"converged={result['converged']}"
        )

    print("=" * 70)

    return {
        "total": total,
        "initially_valid": initially_valid,
        "converged": converged,
        "convergence_rate": convergence_rate,
        "total_before_issues": total_before_issues,
        "total_after_issues": total_after_issues,
        "average_before": average_before,
        "average_after": average_after,
        "issue_reduction": issue_reduction,
        "average_rounds": average_rounds,
        "results": results,
    }


if __name__ == "__main__":
    evaluate()

