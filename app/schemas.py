from typing import List

from pydantic import BaseModel, Field


class SkillsResponse(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    web_technologies: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    computer_science: List[str] = Field(default_factory=list)
    machine_learning: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)


class EducationResponse(BaseModel):
    institution: str = ""
    degree: str = ""
    specialization: str = ""
    cgpa: str = ""


class InternshipResponse(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
    description: List[str] = Field(default_factory=list)


class AchievementResponse(BaseModel):
    title: str = ""
    type: str = ""


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
    skills: SkillsResponse = Field(default_factory=SkillsResponse)
    education: List[EducationResponse] = Field(default_factory=list)
    internships: List[InternshipResponse] = Field(default_factory=list)
    achievements: List[AchievementResponse] = Field(default_factory=list)
    certifications: List[CertificationResponse] = Field(default_factory=list)
    projects: List[ProjectResponse] = Field(default_factory=list)
    hobbies: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str
