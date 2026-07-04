
import { GoogleGenAI, Type } from "@google/genai";
import { ResumeData } from "../types";

function fixAndParseJson(text: string): any {
  text = text.trim();
  text = text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();

  // Try direct parse first
  try { return JSON.parse(text); } catch (_) {}

  // Remove trailing commas before } and ]
  text = text.replace(/,\s*([}\]])/g, "$1");

  try { return JSON.parse(text); } catch (_) {}

  // Replace single quotes with double quotes (careful not to replace escaped ones)
  text = text.replace(/(?<!\\)'/g, '"');

  try { return JSON.parse(text); } catch (_) {}

  // Try to extract first { ... } block
  const firstBrace = text.indexOf("{");
  const lastBrace = text.lastIndexOf("}");
  if (firstBrace !== -1 && lastBrace > firstBrace) {
    let candidate = text.slice(firstBrace, lastBrace + 1);
    candidate = candidate.replace(/,\s*([}\]])/g, "$1");
    try { return JSON.parse(candidate); } catch (_) {}
  }

  throw new SyntaxError("Failed to parse AI response as JSON after cleanup");
}

/**
 * Direct Gemini integration for hyper-fast parsing.
 * Bypasses backend latency and uses Gemini 2.5 Flash for near-instant results.
 */
export async function parseResume(fileData: string, mimeType: string): Promise<ResumeData> {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [
        {
          inlineData: {
            data: fileData,
            mimeType: mimeType,
          },
        },
        {
          text: [
          "Extract only these sections from the resume: full_name, email, phone, linkedin, summary, skills, education, internships, projects, certifications, achievements, hobbies.",
          "Return valid JSON only. Ignore all other sections (e.g. languages, volunteer work, interests, publications, references, etc.).",
            "Categorize skills into programming_languages, web_technologies, frameworks, databases, tools, computer_science, machine_learning, and soft_skills.",
            "For internships, preserve the duration and capture the full description as an array of bullet points.",
            "Identify projects from headings such as Projects, Academic Projects, Personal Projects, Major Projects, Capstone Project, or Relevant Projects.",
            "For each project include only project_name, description, technologies, and duration.",
            "For each achievement include title and type. For each certification include name and issuer.",
            "For the linkedin field, extract the full URL (e.g. linkedin.com/in/...). If only the word 'LinkedIn' appears without a URL, set it to an empty string.",
            "For each education entry, extract the cgpa or gpa or percentage if present.",
            "Never fabricate or hallucinate any data. If a section does not exist in the resume, use empty strings or empty arrays.",
            "Only extract the fields listed above. Ignore everything else in the resume."
          ].join(" ")
        }
      ],
      config: {
        responseMimeType: "application/json",
        thinkingConfig: { thinkingBudget: 0 },
        responseSchema: {
        type: Type.OBJECT,
        properties: {
          full_name: { type: Type.STRING },
          email: { type: Type.STRING },
          phone: { type: Type.STRING },
          linkedin: { type: Type.STRING },
          summary: { type: Type.STRING },
          skills: {
            type: Type.OBJECT,
            properties: {
              programming_languages: { type: Type.ARRAY, items: { type: Type.STRING } },
              web_technologies: { type: Type.ARRAY, items: { type: Type.STRING } },
              frameworks: { type: Type.ARRAY, items: { type: Type.STRING } },
              databases: { type: Type.ARRAY, items: { type: Type.STRING } },
              tools: { type: Type.ARRAY, items: { type: Type.STRING } },
              computer_science: { type: Type.ARRAY, items: { type: Type.STRING } },
              machine_learning: { type: Type.ARRAY, items: { type: Type.STRING } },
              soft_skills: { type: Type.ARRAY, items: { type: Type.STRING } }
            },
            required: ["programming_languages", "soft_skills"]
          },
          education: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                institution: { type: Type.STRING },
                degree: { type: Type.STRING },
                specialization: { type: Type.STRING },
                cgpa: { type: Type.STRING }
              },
              required: ["institution"]
            }
          },
          internships: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                company: { type: Type.STRING },
                role: { type: Type.STRING },
                duration: { type: Type.STRING },
                description: { type: Type.ARRAY, items: { type: Type.STRING } }
              }
            }
          },
          certifications: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                name: { type: Type.STRING },
                issuer: { type: Type.STRING }
              }
            }
          },
          achievements: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                title: { type: Type.STRING },
                type: { type: Type.STRING }
              }
            }
          },
          projects: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                project_name: { type: Type.STRING },
                description: { type: Type.ARRAY, items: { type: Type.STRING } },
                technologies: { type: Type.ARRAY, items: { type: Type.STRING } },
                duration: { type: Type.STRING }
              }
            }
          },
          hobbies: { type: Type.ARRAY, items: { type: Type.STRING } }
        },
        required: ["full_name", "skills"]
      }
    }
  });

  const jsonText = response.text;
  if (!jsonText) throw new Error("Empty response from AI engine");

  const data = fixAndParseJson(jsonText);

  return {
    full_name: data.full_name || "",
    email: data.email || "",
    phone: data.phone || "",
    linkedin: data.linkedin || "",
    summary: data.summary || "",
    skills: {
      programming_languages: Array.isArray(data.skills?.programming_languages) ? data.skills.programming_languages : [],
      web_technologies: Array.isArray(data.skills?.web_technologies) ? data.skills.web_technologies : [],
      frameworks: Array.isArray(data.skills?.frameworks) ? data.skills.frameworks : [],
      databases: Array.isArray(data.skills?.databases) ? data.skills.databases : [],
      tools: Array.isArray(data.skills?.tools) ? data.skills.tools : [],
      computer_science: Array.isArray(data.skills?.computer_science) ? data.skills.computer_science : [],
      machine_learning: Array.isArray(data.skills?.machine_learning) ? data.skills.machine_learning : [],
      soft_skills: Array.isArray(data.skills?.soft_skills) ? data.skills.soft_skills : []
    },
    education: Array.isArray(data.education) ? data.education.map((item: any) => ({
      institution: item?.institution || "",
      degree: item?.degree || "",
      specialization: item?.specialization || "",
      cgpa: item?.cgpa || ""
    })) : [],
    internships: Array.isArray(data.internships) ? data.internships : [],
    achievements: Array.isArray(data.achievements) ? data.achievements : [],
    certifications: Array.isArray(data.certifications) ? data.certifications : [],
    projects: Array.isArray(data.projects) ? data.projects.map((project: any) => ({
      project_name: project?.project_name || "",
      description: Array.isArray(project?.description) ? project.description : [],
      technologies: Array.isArray(project?.technologies) ? project.technologies : [],
      duration: project?.duration || ""
    })) : [],
    hobbies: Array.isArray(data.hobbies) ? data.hobbies : []
  };

  } catch (error: any) {
    const msg = error?.message || "";
    if (msg.includes("does not support") || msg.includes("not supported")) {
      throw new Error("This model does not support PDF input. Try using the backend API instead.");
    }
    throw new Error("Parsing failed. Ensure the file is a valid document and try again.");
  }
}
