import base64
import json
import os
import re
from pathlib import Path
from typing import Any

import google.generativeai as genai
from fastapi import UploadFile
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from app.config import get_settings
from app.schemas import (
    AchievementResponse,
    CertificationResponse,
    EducationResponse,
    ExperienceResponse,
    ProjectResponse,
    ResumeParseResponse,
)
from app.utils import ensure_string, ensure_string_list


def _fix_and_parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    text = re.sub(r",\s*,", ",", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    text = re.sub(r"(?<!\\)'", "\"", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace : last_brace + 1]
        candidate = re.sub(r",\s*}", "}", candidate)
        candidate = re.sub(r",\s*]", "]", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError(f"Failed to parse JSON even after cleanup: {text[:200]}...", text, 0)


class ParserService:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = settings.model_name
        if self.api_key:
            genai.configure(api_key=self.api_key)

    async def parse_resume(self, file: UploadFile) -> ResumeParseResponse:
        filename = (file.filename or "").lower()
        if not filename.endswith((".pdf", ".docx")):
            raise ValueError("Only PDF and DOCX files are supported")

        data = await file.read()
        if not data:
            raise ValueError("Empty file uploaded")

        mime_type = self._detect_mime_type(filename)
        encoded_data = base64.b64encode(data).decode("utf-8")

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction="You are an expert resume parser. Return valid JSON only.",
        )

        prompt = ("""
            Extract resume information and return ONLY valid JSON.

            Follow this EXACT schema. Do not add, remove, or rename any fields.

            {
            "full_name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "summary": "",
            "skills": [],
            "education": [
                {
                "institution": "",
                "degree": "",
                "field_of_study": "",
                "start_date": "",
                "end_date": "",
                "cgpa": ""
                }
            ],
            "experience": [
                {
                "organization": "",
                "position": "",
                "duration": "",
                "description": []
                }
            ],
            "projects": [
                {
                "project_name": "",
                "description": [],
                "technologies": [],
                "duration": ""
                }
            ],
            "certifications": [
                {
                "name": "",
                "issuer": ""
                }
            ],
            "achievements": [
                {
                "title": "",
                "description": ""
                }
            ],
            "hobbies": [],
            "additional_info": ""
            }

            GENERAL RULES

            - Return JSON only.
            - Output must be directly parseable using json.loads().
            - Do not wrap the response inside markdown.
            - Do not include explanations.
            - Do not include comments.
            - Do not output null.
            - Do not output None.
            - Do not output N/A.
            - Use empty strings ("") for missing string values.
            - Use empty arrays ([]) for missing arrays.
            - Every top-level key must always be present.
            - Do not invent, infer, estimate, or hallucinate information.
            - Only extract information explicitly present in the resume.
            - If information is genuinely unavailable, return empty values.
            - Preserve the order of entries exactly as they appear in the resume.

            CONTACT INFORMATION

            - Extract the first valid full name found in the resume.
            - Extract the first valid email address.
            - Extract the first valid phone number.
            - Remove unnecessary spaces in phone numbers.
            - Preserve country codes if present.
            - LinkedIn must contain a complete URL.
            - Examples:
            - https://linkedin.com/in/johndoe
            - linkedin.com/in/johndoe
            - If only the word "LinkedIn" appears without a URL, return an empty string.

            SUMMARY

            Extract professional summary, profile summary, objective, career objective, or about section if present.

            SKILLS

            Extract all explicitly mentioned skills into a single array.

            Rules:
            - skills must always be an array
            - remove duplicates
            - preserve capitalization
            - do not categorize
            - do not infer skills
            - include only explicitly mentioned skills

            EDUCATION

            Education may appear under headings such as:

            Education
            Academic Background
            Academics
            Qualification
            Qualifications
            Schooling
            Education Details

            Common labels include:

            University
            College
            Institute
            School
            Degree
            Course
            Program
            Branch
            Major
            Specialization
            Field of Study

            Extract:

            - institution
            - degree
            - field_of_study
            - start_date
            - end_date
            - cgpa

            For cgpa:
            Extract CGPA, GPA, percentage, or score if present.

            Preserve dates exactly as written.

            Examples:

            Jan 2023
            January 2023
            2020-2024
            2020 – 2024
            Present
            Current

            EXPERIENCE

            Experience may appear under:

            Experience
            Experience
            Experience
            Work Experience
            Professional Experience
            Industrial Training
            Summer Experience
            Research Experience
            Trainee Experience

            Extract:

            - organization
            - position
            - duration
            - description

            Rules:

            - Preserve all bullet points.
            - Description must always be an array.
            - Include every bullet exactly as found.
            - Do not summarize.
            - Do not merge multiple experience entries.
            - Do not omit experience entries even if only one exists.

            PROJECTS

            Projects may appear under:

            Projects
            Project
            Academic Projects
            Personal Projects
            Relevant Projects
            Capstone Project
            Capstone
            Major Project
            Minor Project
            Research Projects
            Final Year Project

            Extract only:

            - project_name
            - description
            - technologies
            - duration

            Rules:

            - Description must always be an array.
            - Technologies must be an array.
            - Include only explicitly mentioned technologies.
            - Do not infer technologies.
            - Preserve descriptions as closely as possible.
            - Do not omit projects even if there is only one.
            - Do not merge multiple projects.

            Never include:

            database
            cloud
            github
            repo
            repository
            live_demo
            website
            role
            team_size
            responsibilities
            outcomes
            highlights
            achievements

            CERTIFICATIONS

            Certifications may appear under:

            Certifications
            Certificates
            Courses
            Training
            Credentials
            Professional Certifications

            Extract:

            - name
            - issuer

            Only include certifications explicitly mentioned.

            ACHIEVEMENTS

            Achievements may appear under:

            Achievements
            Awards
            Honors
            Recognition
            Accomplishments
            Scholarships
            Positions of Responsibility

            Extract:

            - title
            - description

            HOBBIES

            Hobbies may appear under:

            Hobbies
            Interests
            Activities
            Personal Interests

            Extract only personal hobbies and interests.

            Ignore professional interests.

            ADDITIONAL INFORMATION

            Extract remaining relevant information that does not belong to any predefined category.

            Examples:
            - portfolio links
            - website
            - publications
            - patents
            - memberships
            - hackathons
            - extracurricular activities
            - languages known

            Return as plain text.

            If absent return "".

            SECTION DETECTION

            Sections may appear:

            - in uppercase
            - in lowercase
            - bolded
            - underlined
            - in tables
            - in columns
            - abbreviated
            - inline with other text

            Recognize sections regardless of formatting.

            FINAL CONSTRAINTS

            - Do not fabricate information.
            - Do not guess missing values.
            - Do not create additional keys.
            - Do not rename keys.
            - Do not skip experience entries.
            - Do not skip projects.
            - Do not skip education entries.
            - Do not skip certifications.
            - Do not skip achievements.
            - Maintain exact field names.
            - Return only valid JSON."""
            "Only extract the fields listed above. Ignore everything else in the resume."
        )

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        last_error = None
        for attempt in range(2):
            try:
                response = model.generate_content(
                    [{"mime_type": mime_type, "data": encoded_data}, prompt],
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0,
                    },
                    safety_settings=safety_settings,
                )

                if not response.text:
                    raise ValueError("Model failed to respond")

                payload = _fix_and_parse_json(response.text)
                return self._normalize_payload(payload)

            except json.JSONDecodeError as exc:
                last_error = exc
                continue

        raise ValueError(
            f"Failed to parse response after retry: {last_error}"
        ) from last_error

    def _detect_mime_type(self, filename: str) -> str:
        if filename.endswith(".pdf"):
            return "application/pdf"
        if filename.endswith(".docx"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        raise ValueError("Unsupported file type")

    def _normalize_payload(self, payload: dict[str, Any]) -> ResumeParseResponse:
        def _coalesce(*values: Any) -> str:
            for value in values:
                if value is None:
                    continue
                if isinstance(value, str):
                    if value.strip():
                        return value.strip()
                elif value:
                    return str(value)
            return ""

        def _coalesce_list(*values: Any) -> list[str]:
            for value in values:
                if value is None:
                    continue
                if isinstance(value, list):
                    normalized = ensure_string_list(value)
                    if normalized:
                        return normalized
                elif isinstance(value, str) and value.strip():
                    return [value.strip()]
            return []

        def _normalize_description(value: Any) -> list[str]:
            if value is None:
                return []
            if isinstance(value, list):
                return [item.strip() for item in ensure_string_list(value) if item and item.strip()]
            if isinstance(value, str):
                if value.strip():
                    lines = [line.strip() for line in value.splitlines() if line.strip()]
                    if not lines:
                        return []
                    items: list[str] = []
                    for line in lines:
                        stripped = line.lstrip("-•* ")
                        if stripped:
                            items.append(stripped)
                    return items or [value.strip()]
            return []

        def _split_degree_and_specialization(value: str) -> tuple[str, str]:
            text = value.strip()
            if not text:
                return "", ""
            prefix = ""
            for token in ["B.Tech", "B.E", "B.Sc", "M.Tech", "M.E", "M.Sc", "BCA", "MCA", "MBA", "BBA", "Diploma", "PhD", "BA", "B.Com", "M.Com"]:
                if text.startswith(token):
                    prefix = token
                    remainder = text[len(token):].strip()
                    if remainder.startswith("in"):
                        remainder = remainder[2:].strip()
                    if remainder.startswith("-"):
                        remainder = remainder[1:].strip()
                    return prefix, remainder
            if " in " in text:
                left, right = text.split(" in ", 1)
                return left.strip(), right.strip()
            if " - " in text:
                left, right = text.split(" - ", 1)
                return left.strip(), right.strip()
            return "", text

        def _normalize_education(item: dict[str, Any]) -> EducationResponse:
            degree_value = _coalesce(item.get("degree"), item.get("qualification"))
            field_of_study_value = _coalesce(
                item.get("field_of_study"),
                item.get("specialization"),
                item.get("field"),
                item.get("major"),
            )
            if not degree_value and field_of_study_value:
                degree, field_of_study = _split_degree_and_specialization(field_of_study_value)
                if degree:
                    degree_value = degree
                    field_of_study_value = field_of_study
                else:
                    degree_value = ""
                    field_of_study_value = field_of_study_value
            elif degree_value and not field_of_study_value:
                degree, field_of_study = _split_degree_and_specialization(degree_value)
                if degree and field_of_study:
                    degree_value = degree
                    field_of_study_value = field_of_study
            return EducationResponse(
                institution=_coalesce(item.get("institution"), item.get("school"), item.get("university")),
                degree=degree_value,
                field_of_study=field_of_study_value,
                start_date=_coalesce(item.get("start_date"), item.get("start")),
                end_date=_coalesce(item.get("end_date"), item.get("end")),
                cgpa=_coalesce(item.get("cgpa"), item.get("gpa")),
            )

        def _normalize_experience(
            item: dict[str, Any]
        ) -> ExperienceResponse:

            return ExperienceResponse(

                organization=_coalesce(
                    item.get("organization"),
                    item.get("company"),
                    item.get("company_name")
                ),

                position=_coalesce(
                    item.get("position"),
                    item.get("role"),
                    item.get("title")
                ),

                duration=_coalesce(
                    item.get("duration"),
                    item.get("period"),
                    item.get("timespan")
                ),

                description=_normalize_description(
                    item.get("description")
                ),
            )

        def _normalize_project(item: dict[str, Any]) -> ProjectResponse:
            description_value = item.get("description")
            if isinstance(description_value, str):
                description_list = _normalize_description(description_value)
            elif isinstance(description_value, list):
                description_list = _normalize_description(description_value)
            else:
                description_list = _normalize_description(item.get("summary"))
            return ProjectResponse(
                project_name=_coalesce(item.get("project_name"), item.get("name"), item.get("title")),
                description=description_list,
                technologies=_coalesce_list(item.get("technologies"), item.get("tech_stack"), item.get("tech")),
                duration=_coalesce(item.get("duration"), item.get("period")),
            )

        return ResumeParseResponse(
            full_name=ensure_string(payload.get("full_name")),
            email=ensure_string(payload.get("email")),
            phone=ensure_string(payload.get("phone")),
            linkedin=ensure_string(payload.get("linkedin")),
            summary=ensure_string(payload.get("summary") or payload.get("objective")),
            skills=ensure_string_list(payload.get("skills")),
            education=[
                _normalize_education(item)
                for item in payload.get("education", [])
                if isinstance(item, dict)
            ],
            experience=[

                _normalize_experience(item)

                for item in payload.get(
                    "experience",
                    []
                )

                if isinstance(
                    item,
                    dict
                )

            ],
            achievements=[
                AchievementResponse(

                    title=ensure_string(

                        item.get("title")

                        or item.get("name")

                    ),

                    description=ensure_string(

                        item.get("description")

                    )

                )
                for item in payload.get("achievements", [])
                if isinstance(item, dict)
            ],
            certifications=[
                CertificationResponse(
                    name=ensure_string(item.get("name") or item.get("title")),
                    issuer=ensure_string(item.get("issuer") or item.get("organization") or item.get("provider")),
                )
                for item in payload.get("certifications", [])
                if isinstance(item, dict)
            ],
            projects=[
                _normalize_project(item)
                for item in payload.get("projects", [])
                if isinstance(item, dict)
            ],
            hobbies=ensure_string_list(payload.get("hobbies")),
            additional_info=ensure_string(
                payload.get(
                    "additional_info"
                )
            ),
        )
    
