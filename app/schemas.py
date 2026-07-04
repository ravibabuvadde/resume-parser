from typing import List

from pydantic import BaseModel, Field


class EducationResponse(BaseModel):
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    cgpa: str = ""


class ExperienceResponse(BaseModel):
    organization: str = ""

    position: str = ""

    duration: str = ""

    description: list[str] = []


class AchievementResponse(BaseModel):
    title: str = ""

    description: str = ""


class CertificationResponse(BaseModel):
    name: str = ""
    issuer: str = ""


class ProjectResponse(BaseModel):
    project_name: str = ""
    description: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    duration: str = ""


class ResumeParseResponse(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""

    summary: str = ""

    skills: list[str] = []

    education: list[EducationResponse] = []

    experience: list[ExperienceResponse] = []

    projects: list[ProjectResponse] = []

    certifications: list[CertificationResponse] = []

    achievements: list[AchievementResponse] = []

    hobbies: list[str] = []

    additional_info: str = ""


class ErrorResponse(BaseModel):
    detail: str
