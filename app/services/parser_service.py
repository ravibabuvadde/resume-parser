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
    InternshipResponse,
    ProjectResponse,
    ResumeParseResponse,
    SkillsResponse,
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

        prompt = (
            "Extract only these fields from the resume: full_name, email, phone, linkedin, summary, skills, education, internships, projects, certifications, achievements, hobbies. "
            "Return valid JSON only. Ignore all other sections (e.g. languages, volunteer work, interests, publications, references, extracurricular, etc.). "
            "Do not omit any keys. If a field is missing, use an empty string for string values and an empty array for array values. "
            "Do not skip internships or projects. Extract internships and projects even when there is only one entry or when the section is small. "
            "If a section exists in the resume, populate every relevant field that can be found. Only use empty strings or empty arrays when the information is genuinely absent. "
            "Look for common alternate labels such as school/major for education, organization/position for internships, and name/summary/tech_stack/repo for projects. "
            "Categorize skills into programming_languages, web_technologies, frameworks, databases, tools, computer_science, machine_learning, and soft_skills. "
            "For internships, capture the duration and include the full description as an array of bullet points, preserving every bullet from the resume. "
            "Identify projects from headings such as Projects, Academic Projects, Personal Projects, Major Projects, Capstone Project, or Relevant Projects. "
            "For each project include only project_name, description, technologies, and duration. Do not include database, cloud, github, live_demo, role, team_size, highlights, responsibilities, or outcomes. "
            "For each achievement include title and type. For each certification include name and issuer. "
            "For the linkedin field, extract the full URL (e.g. linkedin.com/in/...). If only the word 'LinkedIn' appears without a URL, set it to an empty string. "
            "For each education entry, extract the cgpa or gpa or percentage if present. "
            "Never fabricate or hallucinate any data. If information is not present in the resume, use empty strings or empty arrays. "
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
        skills_payload = payload.get("skills", {}) if isinstance(payload.get("skills"), dict) else {}

        def _skill_list(*keys: str) -> list[str]:
            for key in keys:
                if isinstance(skills_payload, dict):
                    value = skills_payload.get(key)
                    if value is not None:
                        normalized = ensure_string_list(value)
                        if normalized:
                            return normalized
                value = payload.get(key)
                normalized = ensure_string_list(value)
                if normalized:
                    return normalized
            return []

        programming_languages = _skill_list("programming_languages")
        web_technologies = _skill_list("web_technologies")
        frameworks = _skill_list("frameworks")
        databases = _skill_list("databases")
        tools = _skill_list("tools", "tools_platforms")
        computer_science = _skill_list("computer_science", "computer_science_fundamentals")
        machine_learning = _skill_list("machine_learning")
        soft_skills = _skill_list("soft_skills")
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
            specialization_value = _coalesce(item.get("specialization"), item.get("field"), item.get("major"))
            if not degree_value and specialization_value:
                degree, specialization = _split_degree_and_specialization(specialization_value)
                if degree:
                    degree_value = degree
                    specialization_value = specialization
                else:
                    degree_value = ""
                    specialization_value = specialization_value
            elif degree_value and not specialization_value:
                degree, specialization = _split_degree_and_specialization(degree_value)
                if degree and specialization:
                    degree_value = degree
                    specialization_value = specialization
            return EducationResponse(
                institution=_coalesce(item.get("institution"), item.get("school"), item.get("university")),
                degree=degree_value,
                specialization=specialization_value,
                cgpa=_coalesce(item.get("cgpa"), item.get("gpa")),
            )

        def _normalize_internship(item: dict[str, Any]) -> InternshipResponse:
            return InternshipResponse(
                company=_coalesce(item.get("company"), item.get("organization"), item.get("company_name")),
                role=_coalesce(item.get("role"), item.get("position"), item.get("title")),
                duration=_coalesce(item.get("duration"), item.get("period"), item.get("timespan")),
                description=_normalize_description(item.get("description")),
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
            skills=SkillsResponse(
                programming_languages=programming_languages,
                web_technologies=web_technologies,
                frameworks=frameworks,
                databases=databases,
                tools=tools,
                computer_science=computer_science,
                machine_learning=machine_learning,
                soft_skills=soft_skills,
            ),
            education=[
                _normalize_education(item)
                for item in payload.get("education", [])
                if isinstance(item, dict)
            ],
            internships=[
                _normalize_internship(item)
                for item in payload.get("internships", [])
                if isinstance(item, dict)
            ],
            achievements=[
                AchievementResponse(
                    title=ensure_string(item.get("title") or item.get("name") or item.get("description")),
                    type=ensure_string(item.get("type") or item.get("category") or "General"),
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
        )
