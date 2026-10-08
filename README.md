# Topic 12 — Reflection Loop in Code

## Project Overview

This project implements a deterministic reflection loop for improving generated drafts through repeated critique and revision. The implementation demonstrates how an agent can inspect its own output, identify explicit issues, apply targeted corrections, and stop when the draft satisfies all quality rules.

The project contains five assessment tasks:

1. **Critique** — identifies named issues using four explicit rules.
2. **Revision** — applies targeted fixes without unnecessarily changing valid text.
3. **Reflection Loop** — repeatedly performs critique and revision until convergence or a round limit.
4. **Non-Convergence** — verifies that an impossible reflection process terminates safely at `max_rounds`.
5. **Reflection Value Measurement** — evaluates improvement across 10 deterministic drafts.

The implementation is deterministic and does not require an external API, model, or API key.

## Project Structure

```text
Reflection_Loop_Assessment/
├── src/
│   └── reflection_loop.py
├── tests/
│   └── test_reflection_loop.py
├── evidence/
│   ├── task1_critique.json
│   ├── task2_revision.json
│   ├── task3_reflection_loop.json
│   ├── task4_non_convergence.json
│   ├── task5_metrics.json
│   └── generate_evidence.py
├── task5_metrics.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Core Reflection Rules

The critic checks four rules:

- Maximum 12 words
- Minimum 3 words
- Required keyword: `agent`
- Required ending punctuation: `.`

The critic returns machine-readable issue names such as:

```text
too_long
too_short
missing_keyword
no_period
```

## Reflection Workflow

```text
Generate
   ↓
Critique
   ↓
Issues found?
   ├── No → Stop / Converged
   └── Yes
         ↓
       Revise
         ↓
      Critique again
```

The loop stores a complete history containing the round number, draft text, and issues detected in each round.

## Task 1 — Critique

`critique()` validates a draft against four independent rules and returns a list of named issues. Input validation rejects non-string values.

## Task 2 — Revision

`revise()` applies targeted fixes for the reported issues. The implementation is designed to avoid fixing one rule while immediately breaking another, for example by preserving the required keyword while enforcing the maximum word limit.

## Task 3 — Reflection Loop

`reflection_loop()` combines generation, critique, revision, history tracking, convergence detection, and a configurable `max_rounds` safety limit.

A live execution converged in two rounds:

```text
Round 1:
too_long, missing_keyword, no_period

Round 2:
no issues

converged: True
```

## Task 4 — Non-Convergence

A separate injectable critic/reviser interface was implemented for controlled testing. An intentionally impossible critic always reports an unresolved issue while the reviser makes no progress.

With `max_rounds = 3`, the system terminates after three rounds and reports:

```text
converged: False
rounds: 3
```

This demonstrates that the reflection loop cannot continue indefinitely.

## Task 5 — Reflection Value Measurement

Ten deterministic drafts were evaluated before and after reflection.

| Metric | Result |
|---|---:|
| Total drafts | 10 |
| Initially valid drafts | 3 |
| Converged drafts | 10/10 |
| Convergence rate | 100.0% |
| Total issues before | 12 |
| Total issues after | 0 |
| Average issues before | 1.20 |
| Average issues after | 0.00 |
| Issue reduction | 100.0% |
| Average rounds | 1.70 |

All ten drafts converged successfully.

## Evidence

The `evidence/` directory contains JSON artifacts for all five assessment tasks:

- `task1_critique.json`
- `task2_revision.json`
- `task3_reflection_loop.json`
- `task4_non_convergence.json`
- `task5_metrics.json`

Evidence can be regenerated with:

```cmd
python evidence\generate_evidence.py
```

## Installation

From the project directory:

```cmd
python -m pip install -r requirements.txt
```

## Running the Tests

Run the complete test suite:

```cmd
python -m pytest -q
```

Final verification:

```text
36 passed
```

## Running the Reflection Loop

```cmd
python srceflection_loop.py
```

## Running Task 5 Metrics

```cmd
python task5_metrics.py
```

## Generating Evidence

```cmd
python evidence\generate_evidence.py
```

## Security and GitHub Safety

The project does not require API keys or external credentials. The `.gitignore` excludes virtual environments, Python cache files, pytest cache, and environment files.

No secrets should be committed to the repository.

## Reflection

This activity helped me understand reflection as an executable agent pattern rather than only a theoretical concept. The most useful part was separating the process into explicit critique and revision functions. Returning named issues from the critic made the system easier to test and allowed the reviser to apply targeted changes instead of rewriting the entire draft. I also learned that a reflection loop needs a clear convergence condition and a hard round limit. During implementation, an early revision strategy repeatedly recreated a problem it had just fixed, which showed why interacting constraints must be considered together. Fixing that behavior made the loop converge predictably.

The non-convergence task was especially important because a useful agent cannot assume that every critique can be resolved. By injecting an intentionally impossible critic and an ineffective reviser, I verified that the system stops safely after the configured number of rounds. This provides a practical safeguard against infinite loops.

The ten-draft measurement also demonstrated the value of reflection quantitatively. The implementation reduced 12 detected issues to zero across all ten drafts, with a 100% convergence rate and an average of 1.70 rounds. Overall, this project improved my understanding of deterministic agent evaluation, state/history tracking, validation, convergence, failure handling, and measurable quality improvement.
