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
        "skills": [],
        "education": [],
        "experience": [],
        "achievements": [],
        "certifications": [],
        "projects": [],
        "hobbies": [],
        "additional_info": "",
    }

    result = parser._normalize_payload(payload)

    assert result.full_name == "Jane Doe"
    assert result.email == "jane@example.com"
    assert result.phone == "1234567890"
    assert result.linkedin == ""
    assert result.summary == ""
    assert result.skills == []
    assert result.experience == []
    assert result.projects == []
    assert result.additional_info == ""


def test_normalize_payload_extracts_values_from_alternate_keys():
    parser = ParserService()

    payload = {
        "full_name": "Jane Doe",
        "skills": ["Python", "HTML", "FastAPI", "PostgreSQL", "Git", "Communication"],
        "projects": [
            {
                "name": "Resume Parser",
                "summary": "Built a document parser",
                "tech_stack": ["Python", "FastAPI"],
            }
        ],
        "education": [
            {
                "school": "MIT",
                "degree": "B.S.",
                "major": "Computer Science",
                "start_date": "2019",
                "end_date": "2023",
            }
        ],
        "experience": [
            {
                "organization": "OpenAI",
                "position": "Research Intern",
                "period": "Summer 2023",
                "description": "- Built a resume parser\n- Improved model accuracy by 20%",
            }
        ],
    }

    result = parser._normalize_payload(payload)

    assert result.projects[0].project_name == "Resume Parser"
    assert result.projects[0].description == ["Built a document parser"]
    assert result.projects[0].technologies == ["Python", "FastAPI"]
    assert result.education[0].institution == "MIT"
    assert result.education[0].degree == "B.S."
    assert result.education[0].field_of_study == "Computer Science"
    assert result.education[0].start_date == "2019"
    assert result.education[0].end_date == "2023"
    assert result.experience[0].organization == "OpenAI"
    assert result.experience[0].position == "Research Intern"
    assert result.experience[0].duration == "Summer 2023"
    assert result.experience[0].description == [
        "Built a resume parser",
        "Improved model accuracy by 20%",
    ]
    assert result.skills == [
        "Python",
        "HTML",
        "FastAPI",
        "PostgreSQL",
        "Git",
        "Communication",
    ]


def test_normalize_education_reads_field_of_study():
    parser = ParserService()

    payload = {
        "education": [
            {
                "institution": "Stanford",
                "degree": "M.S.",
                "field_of_study": "Artificial Intelligence",
            }
        ],
    }

    result = parser._normalize_payload(payload)

    assert result.education[0].field_of_study == "Artificial Intelligence"
