"""Deterministic, transparent skill matching.

Score = matched job skills / job skills detected, as a percentage.
This is a demo compatibility metric based on keyword-detected skills.
It is NOT a hiring prediction.
"""

from dataclasses import dataclass


@dataclass
class SkillMatch:
    match_percentage: int | None
    matched_skills: list[str]
    missing_skills: list[str]
    additional_skills: list[str]
    cv_skills: list[str]
    job_skills: list[str]
    explanation: str


def _sorted(skills: set[str]) -> list[str]:
    return sorted(skills, key=str.lower)


def match_skills(cv_skills: list[str], job_skills: list[str]) -> SkillMatch:
    cv_set, job_set = set(cv_skills), set(job_skills)
    matched = cv_set & job_set
    missing = job_set - cv_set
    additional = cv_set - job_set

    if job_set:
        percentage = round(100 * len(matched) / len(job_set))
        explanation = (
            f"{len(matched)} of {len(job_set)} skills detected in the job "
            f"description were also found in the CV."
        )
    else:
        percentage = None
        explanation = (
            "No known skills were detected in the job description, so a skill "
            "match percentage cannot be calculated."
        )

    return SkillMatch(
        match_percentage=percentage,
        matched_skills=_sorted(matched),
        missing_skills=_sorted(missing),
        additional_skills=_sorted(additional),
        cv_skills=_sorted(cv_set),
        job_skills=_sorted(job_set),
        explanation=explanation,
    )
