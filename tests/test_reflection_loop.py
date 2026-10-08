import pytest

from src.reflection_loop import (
    critique,
    generate,
    reflection_loop,
    revise,
)


# =========================================================
# Task 1: critique()
# =========================================================


def test_too_long_rule():
    text = (
        "This agent is a very long example sentence "
        "that contains many words beyond the allowed limit."
    )

    issues = critique(text)

    assert "too_long" in issues


def test_too_short_rule():
    text = "Agent."

    issues = critique(text)

    assert "too_short" in issues


def test_missing_keyword_rule():
    text = "This is a short sentence."

    issues = critique(text)

    assert "missing_keyword" in issues


def test_no_period_rule():
    text = "This agent works correctly"

    issues = critique(text)

    assert "no_period" in issues


def test_valid_text_has_no_issues():
    text = "This agent works correctly."

    issues = critique(text)

    assert issues == []


def test_critique_returns_named_issues():
    text = "Short sentence"

    issues = critique(text)

    assert isinstance(issues, list)
    assert "missing_keyword" in issues
    assert "no_period" in issues


def test_invalid_input_is_rejected():
    with pytest.raises(TypeError):
        critique(None)


# =========================================================
# Task 2: revise()
# =========================================================


def test_revise_fixes_missing_period_only():
    original = "This agent works correctly"

    revised = revise(original, ["no_period"])

    assert revised == "This agent works correctly."


def test_revise_adds_missing_keyword():
    original = "This system works correctly."

    revised = revise(original, ["missing_keyword"])

    assert "agent" in revised.lower()
    assert revised.endswith(".")


def test_revise_fixes_too_long_text():
    original = (
        "This agent is a very long example sentence "
        "that contains many words beyond the allowed limit."
    )

    revised = revise(original, ["too_long"])

    assert len(revised.split()) <= 12


def test_revise_fixes_too_short_text():
    original = "Agent."

    revised = revise(original, ["too_short"])

    assert len(revised.split()) >= 3


def test_revise_does_not_change_clean_text():
    original = "This agent works correctly."

    revised = revise(original, [])

    assert revised == original


def test_revise_only_applies_requested_fix():
    original = "This agent works correctly."

    revised = revise(original, ["no_period"])

    assert revised == original


def test_revise_rejects_invalid_text():
    with pytest.raises(TypeError):
        revise(None, [])


def test_revise_rejects_invalid_issues():
    with pytest.raises(TypeError):
        revise("This agent works.", "no_period")


def test_revise_output_can_be_critiqued():
    original = "This system works correctly"

    issues = critique(original)
    revised = revise(original, issues)

    remaining_issues = critique(revised)

    assert "no_period" not in remaining_issues


# =========================================================
# Task 3: reflection_loop()
# =========================================================


def test_generate_returns_deterministic_draft():
    first = generate("describe software")
    second = generate("describe software")

    assert first == second


def test_reflection_loop_converges():
    result = reflection_loop("describe software", max_rounds=3)

    assert result["converged"] is True
    assert result["rounds"] <= 3
    assert critique(result["final"]) == []


def test_reflection_loop_keeps_full_history():
    result = reflection_loop("describe software", max_rounds=3)

    assert isinstance(result["history"], list)
    assert len(result["history"]) == result["rounds"]

    for item in result["history"]:
        assert "round" in item
        assert "text" in item
        assert "issues" in item


def test_reflection_loop_history_starts_with_issues():
    result = reflection_loop("describe software", max_rounds=3)

    assert result["history"][0]["issues"]


def test_reflection_loop_has_round_limit():
    result = reflection_loop("describe software", max_rounds=1)

    assert result["rounds"] == 1
    assert len(result["history"]) == 1


def test_reflection_loop_rejects_invalid_round_limit():
    with pytest.raises(ValueError):
        reflection_loop("describe software", max_rounds=0)


def test_reflection_loop_rejects_invalid_prompt():
    with pytest.raises(ValueError):
        reflection_loop("", max_rounds=3)


def test_reflection_loop_rejects_invalid_round_type():
    with pytest.raises(TypeError):
        reflection_loop("describe software", max_rounds="3")

# =========================================================
# Task 4: Non-Convergence
# =========================================================


def test_non_convergence_respects_max_rounds():
    """
    Use a critic that always reports an impossible issue and
    a reviser that cannot resolve it.

    The loop must stop at max_rounds.
    """

    from src.reflection_loop import reflection_loop_with_critic

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

    assert result["converged"] is False
    assert result["rounds"] == 3
    assert len(result["history"]) == 3


def test_non_convergence_preserves_repeated_issue():
    """
    The unresolved issue should remain visible in every round.
    """

    from src.reflection_loop import reflection_loop_with_critic

    def impossible_critic(text):
        return ["impossible_issue"]

    def ineffective_reviser(text, issues):
        return text

    result = reflection_loop_with_critic(
        "describe software",
        max_rounds=4,
        critic=impossible_critic,
        reviser=ineffective_reviser,
    )

    assert result["converged"] is False

    for item in result["history"]:
        assert "impossible_issue" in item["issues"]


def test_non_convergence_does_not_run_forever():
    """
    A small max_rounds value provides an explicit termination
    guarantee even when revision makes no progress.
    """

    from src.reflection_loop import reflection_loop_with_critic

    call_count = {"critic": 0}

    def impossible_critic(text):
        call_count["critic"] += 1
        return ["never_fixed"]

    def ineffective_reviser(text, issues):
        return text

    result = reflection_loop_with_critic(
        "describe software",
        max_rounds=5,
        critic=impossible_critic,
        reviser=ineffective_reviser,
    )

    assert result["converged"] is False
    assert result["rounds"] == 5
    assert call_count["critic"] == 5


def test_custom_loop_can_converge():
    """
    The injected version should still support successful
    convergence when the critic eventually returns no issues.
    """

    from src.reflection_loop import reflection_loop_with_critic

    calls = {"count": 0}

    def critic(text):
        calls["count"] += 1

        if calls["count"] == 1:
            return ["needs_fix"]

        return []

    def reviser(text, issues):
        return text + " fixed"

    result = reflection_loop_with_critic(
        "describe software",
        max_rounds=3,
        critic=critic,
        reviser=reviser,
    )

    assert result["converged"] is True
    assert result["rounds"] == 2
    assert len(result["history"]) == 2

# =========================================================
# Task 5: Reflection Value Measurement
# =========================================================


def test_task5_uses_exactly_ten_drafts():
    from task5_metrics import DRAFTS

    assert len(DRAFTS) == 10


def test_task5_all_drafts_converge():
    from task5_metrics import DRAFTS, run_reflection

    for draft in DRAFTS:
        result = run_reflection(draft)

        assert result["converged"] is True
        assert critique(result["final"]) == []


def test_task5_reflection_removes_all_detected_issues():
    from task5_metrics import DRAFTS, run_reflection

    total_before = 0
    total_after = 0

    for draft in DRAFTS:
        before = critique(draft)

        result = run_reflection(draft)

        after = critique(result["final"])

        total_before += len(before)
        total_after += len(after)

    assert total_before == 12
    assert total_after == 0


def test_task5_convergence_rate_is_100_percent():
    from task5_metrics import DRAFTS, run_reflection

    converged = 0

    for draft in DRAFTS:
        result = run_reflection(draft)

        if result["converged"]:
            converged += 1

    convergence_rate = converged / len(DRAFTS) * 100

    assert convergence_rate == 100.0


def test_task5_average_issues_before_is_1_2():
    from task5_metrics import DRAFTS

    total_issues = sum(
        len(critique(draft))
        for draft in DRAFTS
    )

    average = total_issues / len(DRAFTS)

    assert average == 1.2


def test_task5_average_issues_after_is_zero():
    from task5_metrics import DRAFTS, run_reflection

    total_after = 0

    for draft in DRAFTS:
        result = run_reflection(draft)

        total_after += len(
            critique(result["final"])
        )

    average_after = total_after / len(DRAFTS)

    assert average_after == 0.0


def test_task5_issue_reduction_is_100_percent():
    from task5_metrics import DRAFTS, run_reflection

    before = sum(
        len(critique(draft))
        for draft in DRAFTS
    )

    after = sum(
        len(critique(run_reflection(draft)["final"]))
        for draft in DRAFTS
    )

    reduction = (
        (before - after) / before * 100
    )

    assert reduction == 100.0


def test_task5_results_are_deterministic():
    from task5_metrics import DRAFTS, run_reflection

    first_run = [
        run_reflection(draft)
        for draft in DRAFTS
    ]

    second_run = [
        run_reflection(draft)
        for draft in DRAFTS
    ]

    assert first_run == second_run