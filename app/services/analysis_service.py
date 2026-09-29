"""Runs the full CV vs. job analysis by combining the individual services.

Skill match and semantic similarity are reported separately - they are
never merged into a single opaque score.
"""

from dataclasses import dataclass

from app.services.cv_service import CVDocument
from app.services.job_service import JobDescription
from app.services.matching_service import SkillMatch, match_skills
from app.services.semantic_service import SemanticSimilarity, compute_similarity
from app.services.skill_service import extract_skills


@dataclass
class FullAnalysis:
    cv: CVDocument
    cv_skills: list[str]
    job: JobDescription
    job_skills: list[str]
    skill_match: SkillMatch
    semantic_similarity: SemanticSimilarity


def run_analysis(cv: CVDocument, job: JobDescription) -> FullAnalysis:
    cv_skills = extract_skills(cv.text)
    job_skills = extract_skills(job.text)
    skill_match = match_skills(cv_skills, job_skills)
    return FullAnalysis(
        cv=cv,
        cv_skills=cv_skills,
        job=job,
        job_skills=job_skills,
        skill_match=skill_match,
        semantic_similarity=compute_similarity(cv.text, job.text),
    )
