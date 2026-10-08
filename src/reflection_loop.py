"""
Topic 12: Reflection Loop in Code

Tasks:
1. critique()
2. revise()
3. reflection_loop()
4. Test non-convergence safely.

The implementation is deterministic and uses no external APIs.
"""


RULES = {
    "max_words": 12,
    "min_words": 3,
    "must_include": "agent",
    "must_end_with": ".",
}


def generate(prompt: str) -> str:
    """
    Generate a deterministic initial draft.
    """

    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")

    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    return (
        "This is a really quite long sentence about "
        "how every single software system works today"
    )


def critique(text: str) -> list[str]:
    """
    Check a draft against four explicit rules.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    issues = []
    words = text.split()

    if len(words) > RULES["max_words"]:
        issues.append("too_long")

    if len(words) < RULES["min_words"]:
        issues.append("too_short")

    if RULES["must_include"].lower() not in text.lower():
        issues.append("missing_keyword")

    if not text.rstrip().endswith(RULES["must_end_with"]):
        issues.append("no_period")

    return issues


def revise(text: str, issues: list[str]) -> str:
    """
    Apply targeted fixes for the supplied issues.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if not isinstance(issues, list):
        raise TypeError("issues must be a list")

    revised = text.strip()

    words = revised.rstrip(".").split()

    # Fix too_short.
    if "too_short" in issues:
        if not words:
            words = ["This", "agent", "works"]
        else:
            while len(words) < RULES["min_words"]:
                words.append("works")

    # Fix missing keyword.
    if "missing_keyword" in issues:
        keyword = RULES["must_include"].lower()

        if keyword not in [
            word.lower().rstrip(".,!?")
            for word in words
        ]:
            if len(words) < RULES["max_words"]:
                words.append(RULES["must_include"])
            else:
                words[-1] = RULES["must_include"]

    # Fix too_long.
    if "too_long" in issues:
        keyword = RULES["must_include"].lower()

        if len(words) > RULES["max_words"]:

            keyword_positions = [
                index
                for index, word in enumerate(words)
                if word.lower().rstrip(".,!?") == keyword
            ]

            if keyword_positions:
                keyword_index = keyword_positions[0]

                if keyword_index < RULES["max_words"]:
                    words = words[:RULES["max_words"]]
                else:
                    words = (
                        words[:RULES["max_words"] - 1]
                        + [RULES["must_include"]]
                    )
            else:
                words = (
                    words[:RULES["max_words"] - 1]
                    + [RULES["must_include"]]
                )

    revised = " ".join(words).strip()

    # Always ensure a valid sentence ending.
    if revised and not revised.endswith(RULES["must_end_with"]):
        revised += RULES["must_end_with"]

    return revised


def reflection_loop(prompt: str, max_rounds: int = 3) -> dict:
    """
    Run the standard reflection loop.
    """

    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")

    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    if isinstance(max_rounds, bool):
        raise TypeError("max_rounds must be an integer")

    if not isinstance(max_rounds, int):
        raise TypeError("max_rounds must be an integer")

    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1")

    text = generate(prompt)
    history = []

    for rnd in range(1, max_rounds + 1):

        issues = critique(text)

        history.append(
            {
                "round": rnd,
                "text": text,
                "issues": issues.copy(),
            }
        )

        if not issues:
            return {
                "final": text,
                "rounds": rnd,
                "converged": True,
                "history": history,
            }

        text = revise(text, issues)

    return {
        "final": text,
        "rounds": max_rounds,
        "converged": False,
        "history": history,
    }


def reflection_loop_with_critic(
    prompt: str,
    max_rounds: int,
    critic,
    reviser,
) -> dict:
    """
    Run a reflection loop using injected critic and reviser functions.

    This makes non-convergence testable without modifying the
    production critique() and revise() behavior.

    The loop is guaranteed to stop after max_rounds.
    """

    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")

    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    if isinstance(max_rounds, bool):
        raise TypeError("max_rounds must be an integer")

    if not isinstance(max_rounds, int):
        raise TypeError("max_rounds must be an integer")

    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1")

    if not callable(critic):
        raise TypeError("critic must be callable")

    if not callable(reviser):
        raise TypeError("reviser must be callable")

    text = generate(prompt)
    history = []

    for rnd in range(1, max_rounds + 1):

        issues = critic(text)

        if not isinstance(issues, list):
            raise TypeError("critic must return a list")

        history.append(
            {
                "round": rnd,
                "text": text,
                "issues": issues.copy(),
            }
        )

        # Successful convergence.
        if not issues:
            return {
                "final": text,
                "rounds": rnd,
                "converged": True,
                "history": history,
            }

        # Apply the supplied reviser.
        text = reviser(text, issues)

        if not isinstance(text, str):
            raise TypeError("reviser must return a string")

    # Maximum rounds reached.
    return {
        "final": text,
        "rounds": max_rounds,
        "converged": False,
        "history": history,
    }


if __name__ == "__main__":
    result = reflection_loop("describe software")

    print("Reflection history")
    print("=" * 60)

    for item in result["history"]:
        print(item)

    print("=" * 60)
    print("final:", result["final"])
    print("rounds:", result["rounds"])
    print("converged:", result["converged"])