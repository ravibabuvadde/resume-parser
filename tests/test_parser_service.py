import pytest

from app.services.parser_service import ParserService


class DummyUploadFile:
    filename = "resume.pdf"

    async def read(self):
        return b"dummy"


@pytest.mark.asyncio
async def test_normalize_payload_preserves_empty_sections(monkeypatch):
    parser = ParserService()

    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "1234567890",
        "linkedin": "",
        "summary": "",
        "skills": {
            "programming_languages": ["Python"],
            "soft_skills": []
        },
        "education": [],
        "experience": [],
        "internships": [],
        "achievements": [],
        "certifications": [],
        "projects": []
    }

    result = parser._normalize_payload(payload)

    assert result.full_name == "Jane Doe"
    assert result.email == "jane@example.com"
    assert result.phone == "1234567890"
    assert result.linkedin == ""
    assert result.summary == ""
    assert result.internships == []
    assert result.projects == []


def test_normalize_payload_extracts_values_from_alternate_keys():
    parser = ParserService()

    payload = {
        "full_name": "Jane Doe",
        "skills": {
            "programming_languages": ["Python"],
            "web_technologies": ["HTML"],
            "frameworks": ["FastAPI"],
            "databases": ["PostgreSQL"],
            "tools": ["Git"],
            "computer_science": ["Data Structures"],
            "machine_learning": ["PyTorch"],
            "soft_skills": ["Communication"]
        },
        "projects": [
            {
                "name": "Resume Parser",
                "summary": "Built a document parser",
                "tech_stack": ["Python", "FastAPI"]
            }
        ],
        "education": [
            {
                "school": "MIT",
                "degree": "B.S.",
                "major": "Computer Science"
            }
        ],
        "internships": [
            {
                "organization": "OpenAI",
                "position": "Research Intern",
                "period": "Summer 2023",
                "description": "- Built a resume parser\n- Improved model accuracy by 20%"
            }
        ]
    }

    result = parser._normalize_payload(payload)

    assert result.projects[0].project_name == "Resume Parser"
    assert result.projects[0].description == ["Built a document parser"]
    assert result.projects[0].technologies == ["Python", "FastAPI"]
    assert result.education[0].institution == "MIT"
    assert result.education[0].degree == "B.S."
    assert result.education[0].specialization == "Computer Science"
    assert result.internships[0].company == "OpenAI"
    assert result.internships[0].role == "Research Intern"
    assert result.internships[0].duration == "Summer 2023"
    assert result.internships[0].description == ["Built a resume parser", "Improved model accuracy by 20%"]
    assert result.skills.programming_languages == ["Python"]
    assert result.skills.web_technologies == ["HTML"]
    assert result.skills.frameworks == ["FastAPI"]
    assert result.skills.databases == ["PostgreSQL"]
    assert result.skills.tools == ["Git"]
    assert result.skills.computer_science == ["Data Structures"]
    assert result.skills.machine_learning == ["PyTorch"]
    assert result.skills.soft_skills == ["Communication"]
