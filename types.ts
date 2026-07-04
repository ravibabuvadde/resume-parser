
export interface Education {
  institution: string;
  degree: string;
  specialization: string;
  cgpa?: string;
}

export interface Internship {
  company: string;
  role: string;
  duration: string;
  description: string[];
}

export interface Achievement {
  title: string;
  type: string;
}

export interface Certification {
  name: string;
  issuer: string;
}

export interface Project {
  project_name: string;
  description: string[];
  technologies: string[];
  duration: string;
}

export interface ResumeData {
  full_name: string;
  email: string;
  phone: string;
  linkedin: string;
  summary: string;
  skills: {
    programming_languages: string[];
    web_technologies: string[];
    frameworks: string[];
    databases: string[];
    tools: string[];
    computer_science: string[];
    machine_learning: string[];
    soft_skills: string[];
  };
  education: Education[];
  internships: Internship[];
  achievements: Achievement[];
  certifications: Certification[];
  projects: Project[];
  hobbies: string[];
}

export type ActiveTab = 'overview' | 'education' | 'skills' | 'experience' | 'internships' | 'achievements' | 'projects' | 'hobbies' | 'json';
