"""Generate the Paper 2 CI outcomes summary figure.

This script intentionally treats CI outcomes as operational workflow evidence
only. It does not make claims about numerical correctness, physical validity,
mathematical proof, productivity improvement, or autonomous AI validation.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = (
    REPO_ROOT
    / "docs"
    / "paper_2_ai_assisted_scientific_engineering"
    / "pr_ci_outcomes.csv"
)
FIGURES_DIR = REPO_ROOT / "figures" / "paper_2"
OUTPUT_PNG = FIGURES_DIR / "ci_outcomes_summary.png"
OUTPUT_MD = FIGURES_DIR / "ci_outcomes_summary.md"

EXPECTED_TOTAL = 38
EXPECTED_SUCCESS = 36
EXPECTED_FAILURE = 2
EXPECTED_UNKNOWN = 0
EXPECTED_FAILURE_PRS = [45, 56]

SUCCESS_CONCLUSION = "success"
FAILURE_CONCLUSION = "failure"


@dataclass(frozen=True)
class CiOutcomeSummary:
    total: int
    success: int
    failure: int
    unknown: int
    failure_prs: list[int]


def load_ci_outcomes(source_csv: Path) -> list[dict[str, str]]:
    if not source_csv.is_file():
        raise FileNotFoundError(f"Required source CSV not found: {source_csv}")

    with source_csv.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"pr_number", "workflow_conclusion"}
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Source CSV missing required column(s): {missing}")
        return list(reader)


def summarize_ci_outcomes(rows: list[dict[str, str]]) -> CiOutcomeSummary:
    success = 0
    failure = 0
    failure_prs: list[int] = []

    for index, row in enumerate(rows, start=2):
        conclusion = row["workflow_conclusion"].strip().lower()
        pr_number_text = row["pr_number"].strip()

        if not pr_number_text:
            raise ValueError(f"Missing PR number at CSV line {index}")

        try:
            pr_number = int(pr_number_text)
        except ValueError as exc:
            raise ValueError(
                f"Invalid PR number at CSV line {index}: {pr_number_text!r}"
            ) from exc

        if conclusion == SUCCESS_CONCLUSION:
            success += 1
        elif conclusion == FAILURE_CONCLUSION:
            failure += 1
            failure_prs.append(pr_number)

    total = len(rows)
    unknown = total - success - failure
    return CiOutcomeSummary(
        total=total,
        success=success,
        failure=failure,
        unknown=unknown,
        failure_prs=failure_prs,
    )


def validate_summary(summary: CiOutcomeSummary) -> None:
    expected = CiOutcomeSummary(
        total=EXPECTED_TOTAL,
        success=EXPECTED_SUCCESS,
        failure=EXPECTED_FAILURE,
        unknown=EXPECTED_UNKNOWN,
        failure_prs=EXPECTED_FAILURE_PRS,
    )
    if summary != expected:
        raise ValueError(
            "CI outcome summary does not match expected values. "
            f"Expected {expected}; computed {summary}."
        )


def generate_figure(summary: CiOutcomeSummary, output_png: Path) -> None:
    labels = ["Success", "Failure", "Unknown"]
    counts = [summary.success, summary.failure, summary.unknown]

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    bars = ax.bar(labels, counts)
    ax.set_title("Paper 2 CI outcomes, PR #31-#68")
    ax.set_ylabel("PR count")
    ax.set_ylim(0, max(counts) + 5)
    ax.bar_label(bars, labels=[str(count) for count in counts], padding=3)
    ax.text(
        0.5,
        -0.18,
        "Operational workflow evidence only; not scientific validity.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(output_png, dpi=200)
    plt.close(fig)


def write_markdown(summary: CiOutcomeSummary, output_md: Path) -> None:
    failure_prs = ", ".join(str(pr_number) for pr_number in summary.failure_prs)
    output_md.write_text(
        "\n".join(
            [
                "# Paper 2 CI Outcomes Summary",
                "",
                "## Purpose",
                "Provide a reproducible summary figure for Paper 2 CI outcomes across PR #31-#68.",
                "",
                "## Source File",
                "`docs/paper_2_ai_assisted_scientific_engineering/pr_ci_outcomes.csv`",
                "",
                "## Generation Command",
                "`python scripts/paper_2_generate_ci_outcomes_figure.py`",
                "",
                "## Computed Counts",
                f"- total rows: {summary.total}",
                f"- success: {summary.success}",
                f"- failure: {summary.failure}",
                f"- unknown/unavailable: {summary.unknown}",
                "",
                "## Failure PRs",
                f"{failure_prs}",
                "",
                "## Interpretation Boundary",
                "CI success is operational workflow evidence, not proof of numerical correctness, physical validity, mathematical proof, productivity improvement, or autonomous AI scientific validation.",
                "",
                "## Claims Supported",
                "- The recorded CI workflow outcomes in the source CSV contain 36 successes, 2 failures, and 0 unknown/unavailable outcomes.",
                "- The recorded failed CI outcomes correspond to PR #45 and PR #56.",
                "- The figure summarizes operational workflow evidence only.",
                "",
                "## Claims Not Supported",
                "- Numerical correctness.",
                "- Physical validity.",
                "- Mathematical proof.",
                "- Productivity improvement.",
                "- Autonomous AI scientific validation.",
                "- Scientific validity of solver outputs or research conclusions.",
                "",
                "## Rollback Plan",
                "Remove `scripts/paper_2_generate_ci_outcomes_figure.py`, `figures/paper_2/ci_outcomes_summary.png`, and `figures/paper_2/ci_outcomes_summary.md`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = load_ci_outcomes(SOURCE_CSV)
    summary = summarize_ci_outcomes(rows)
    validate_summary(summary)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    generate_figure(summary, OUTPUT_PNG)
    write_markdown(summary, OUTPUT_MD)

    print(f"total={summary.total}")
    print(f"success={summary.success}")
    print(f"failure={summary.failure}")
    print(f"unknown={summary.unknown}")
    print(f"failure_prs={summary.failure_prs}")


if __name__ == "__main__":
    main()
