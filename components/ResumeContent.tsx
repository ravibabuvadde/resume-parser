
import React from 'react';
import { ResumeData, ActiveTab } from '../types';

interface ResumeContentProps {
  data: ResumeData;
  activeTab: ActiveTab;
}

const ResumeContent: React.FC<ResumeContentProps> = ({ data, activeTab }) => {
  // Defensive normalization of arrays
  const technicalSkills = [
    ...(data?.skills?.programming_languages || []),
    ...(data?.skills?.web_technologies || []),
    ...(data?.skills?.frameworks || []),
    ...(data?.skills?.databases || []),
    ...(data?.skills?.tools || []),
    ...(data?.skills?.computer_science || []),
    ...(data?.skills?.machine_learning || [])
  ];
  const softSkills = data?.skills?.soft_skills || [];
  const education = data?.education || [];
  const internships = data?.internships || [];
  const achievements = data?.achievements || [];
  const certifications = data?.certifications || [];
  const projects = data?.projects || [];
  const hobbies = data?.hobbies || [];

  const SectionHeader = ({ title, icon }: { title: string; icon: string }) => (
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center">
        <i className={`fas ${icon}`}></i>
      </div>
      <h2 className="text-2xl font-bold text-slate-800">{title}</h2>
    </div>
  );

  const StatCard = ({ label, value, icon, colorClass }: { label: string; value: string | number; icon: string; colorClass: string }) => (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl ${colorClass}`}>
        <i className={`fas ${icon}`}></i>
      </div>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</p>
        <p className="text-xl font-bold text-slate-800">{value}</p>
      </div>
    </div>
  );

  const renderOverview = () => (
    <div className="space-y-8 animate-fadeIn">
      <SectionHeader title="Resume Dashboard" icon="fa-chart-pie" />
      
      {/* Contact Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-100">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{data?.full_name || 'Name not found'}</h1>
            <p className="text-indigo-600 font-medium mt-1">Extracted Profile Summary</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {data?.email && (
              <a href={`mailto:${data.email}`} className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-full text-sm text-slate-600 border border-slate-200 hover:bg-slate-100 transition-colors">
                <i className="fas fa-envelope text-indigo-500"></i> {data.email}
              </a>
            )}
            {data?.phone && (
              <span className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-full text-sm text-slate-600 border border-slate-200">
                <i className="fas fa-phone text-indigo-500"></i> {data.phone}
              </span>
            )}
            {data?.linkedin && (
              <a href={data.linkedin} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-full text-sm text-slate-600 border border-slate-200 hover:bg-slate-100 transition-colors">
                <i className="fab fa-linkedin text-indigo-500"></i> LinkedIn
              </a>
            )}
          </div>
        </div>

        <div className="prose prose-slate max-w-none">
          <p className="text-slate-600 leading-relaxed italic border-l-4 border-indigo-200 pl-4">
            "{data?.summary || 'No professional summary extracted.'}"
          </p>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          label="Skills" 
          value={technicalSkills.length + softSkills.length} 
          icon="fa-bolt" 
          colorClass="bg-amber-50 text-amber-600" 
        />
        <StatCard 
          label="Internships" 
          value={internships.length} 
          icon="fa-id-badge" 
          colorClass="bg-blue-50 text-blue-600" 
        />
        <StatCard 
          label="Education" 
          value={education.length} 
          icon="fa-graduation-cap" 
          colorClass="bg-purple-50 text-purple-600" 
        />
        <StatCard 
          label="Achievements" 
          value={achievements.length + certifications.length} 
          icon="fa-trophy" 
          colorClass="bg-emerald-50 text-emerald-600" 
        />
        <StatCard 
          label="Projects" 
          value={projects.length} 
          icon="fa-diagram-project" 
          colorClass="bg-cyan-50 text-cyan-600" 
        />
      </div>

      {/* Quick Preview Sections */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center justify-between">
            Top Skills
            <i className="fas fa-arrow-right text-[10px]"></i>
          </h3>
          <div className="flex flex-wrap gap-2">
            {technicalSkills.slice(0, 6).map((s, i) => (
              <span key={i} className="px-2 py-1 bg-slate-50 text-slate-600 text-xs font-semibold rounded border border-slate-100">{s}</span>
            ))}
            {technicalSkills.length > 6 && <span className="text-xs text-slate-400">+{technicalSkills.length - 6} more</span>}
            {technicalSkills.length === 0 && <p className="text-slate-400 text-xs italic">No technical skills listed</p>}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center justify-between">
            Latest Role
            <i className="fas fa-arrow-right text-[10px]"></i>
          </h3>
          {internships.length > 0 ? (
            <div>
              <p className="font-bold text-slate-800 text-sm">{internships[0].role}</p>
              <p className="text-indigo-600 text-xs font-medium">{internships[0].company}</p>
            </div>
          ) : (
            <p className="text-slate-400 text-xs italic">No internship listed</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderEducation = () => (
    <div className="space-y-6 animate-fadeIn">
      <SectionHeader title="Education History" icon="fa-graduation-cap" />
      {education.length > 0 ? (
        education.map((edu, idx) => (
          <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:border-indigo-200 transition-all">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-bold text-slate-800">{edu.institution}</h3>
                <p className="text-indigo-600 font-semibold">{edu.degree}{edu.specialization ? ` in ${edu.specialization}` : ''}</p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
                   {edu.cgpa && (
                     <p className="text-emerald-600 text-sm font-bold">
                       <i className="fas fa-star mr-1"></i> CGPA: {edu.cgpa}
                     </p>
                   )}
                </div>
              </div>
            </div>
          </div>
        ))
      ) : (
        <div className="text-slate-400 py-12 text-center bg-white rounded-2xl border border-dashed border-slate-300">
          No education records found.
        </div>
      )}
    </div>
  );

  const renderSkills = () => (
    <div className="space-y-8 animate-fadeIn">
      <SectionHeader title="Skills & Competencies" icon="fa-tools" />
      
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <i className="fas fa-code text-indigo-500"></i> Technical Skills
            </h3>
            <span className="text-xs font-bold text-slate-400">{technicalSkills.length} items</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {technicalSkills.length > 0 ? (
              technicalSkills.map((skill, idx) => (
                <span key={idx} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium border border-indigo-100 hover:bg-indigo-100 transition-colors">
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-slate-400 text-sm italic">No technical skills detected.</p>
            )}
          </div>
        </div>
        
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <i className="fas fa-comments text-emerald-500"></i> Soft Skills
            </h3>
            <span className="text-xs font-bold text-slate-400">{softSkills.length} items</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {softSkills.length > 0 ? (
              softSkills.map((skill, idx) => (
                <span key={idx} className="px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium border border-emerald-100 hover:bg-emerald-100 transition-colors">
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-slate-400 text-sm italic">No soft skills detected.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderInternships = () => (
    <div className="space-y-6 animate-fadeIn">
      <SectionHeader title="Internships" icon="fa-id-badge" />
      {internships.length > 0 ? (
        internships.map((intern, idx) => (
          <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:border-indigo-200 transition-all">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-slate-800">{intern.role}</h3>
                <p className="text-emerald-600 font-semibold">{intern.company}</p>
              </div>
              <div className="text-right">
                <span className="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold">
                  {intern.duration}
                </span>
              </div>
            </div>
            <ul className="space-y-2">
              {(intern.description || []).map((item, i) => (
                <li key={i} className="text-slate-600 text-sm flex gap-3">
                  <span className="text-emerald-400 mt-1.5 flex-shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        ))
      ) : (
        <div className="text-slate-400 py-12 text-center bg-white rounded-2xl border border-dashed border-slate-300">
          No internship records found.
        </div>
      )}
    </div>
  );

  const renderAchievements = () => (
    <div className="space-y-6 animate-fadeIn">
      <SectionHeader title="Achievements & Certifications" icon="fa-trophy" />
      {(achievements.length > 0 || certifications.length > 0) ? (
        <div className="space-y-6">
          {achievements.length > 0 && (
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-4">Achievements</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {achievements.map((ach, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:border-indigo-200 transition-all">
                    <div className="flex items-start gap-4">
                      <div className="text-yellow-500 mt-1 text-xl">
                        <i className="fas fa-award"></i>
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-800">{ach.title}</h3>
                        <p className="text-indigo-600 text-sm font-semibold">{ach.type}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {certifications.length > 0 && (
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-4">Certifications</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {certifications.map((cert, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:border-indigo-200 transition-all">
                    <div className="flex items-start gap-4">
                      <div className="text-emerald-500 mt-1 text-xl">
                        <i className="fas fa-certificate"></i>
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-800">{cert.name}</h3>
                        <p className="text-indigo-600 text-sm font-semibold">{cert.issuer}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-slate-400 py-12 text-center bg-white rounded-2xl border border-dashed border-slate-300">
          No achievement or certification records found.
        </div>
      )}
    </div>
  );

  const renderProjects = () => (
    <div className="space-y-6 animate-fadeIn">
      <SectionHeader title="Projects" icon="fa-diagram-project" />
      {projects.length > 0 ? (
        projects.map((project, idx) => (
          <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:border-indigo-200 transition-all space-y-4">
            <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-slate-800">{project.project_name || 'Untitled Project'}</h3>
                <ul className="space-y-2 mt-2">
                  {(project.description || []).map((item, i) => (
                    <li key={i} className="text-slate-600 text-sm flex gap-3">
                      <span className="text-indigo-400 mt-1.5 flex-shrink-0">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="text-right text-sm text-slate-500">
                {project.duration && <div className="font-semibold text-indigo-600">{project.duration}</div>}
              </div>
            </div>

            <div className="space-y-3">
              {project.technologies.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {project.technologies.slice(0, 12).map((item, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-100">{item}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))
      ) : (
        <div className="text-slate-400 py-12 text-center bg-white rounded-2xl border border-dashed border-slate-300">
          No project records found.
        </div>
      )}
    </div>
  );

  const renderHobbies = () => (
    <div className="space-y-6 animate-fadeIn">
      <SectionHeader title="Hobbies & Interests" icon="fa-heart" />
      {hobbies.length > 0 ? (
        <div className="flex flex-wrap gap-3">
          {hobbies.map((hobby, idx) => (
            <span key={idx} className="px-4 py-2 bg-pink-50 text-pink-700 rounded-xl text-sm font-medium border border-pink-100 hover:bg-pink-100 transition-colors">
              <i className="fas fa-heart mr-2 text-pink-400"></i>{hobby}
            </span>
          ))}
        </div>
      ) : (
        <div className="text-slate-400 py-12 text-center bg-white rounded-2xl border border-dashed border-slate-300">
          No hobbies or interests listed.
        </div>
      )}
    </div>
  );

  const renderJson = () => (
    <div className="animate-fadeIn h-full flex flex-col">
      <SectionHeader title="Raw Extracted JSON" icon="fa-code" />
      <div className="flex-1 bg-slate-900 rounded-2xl p-6 overflow-auto custom-scrollbar shadow-inner border border-slate-800 font-mono text-xs leading-relaxed">
        <pre className="text-indigo-300 whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );

  switch (activeTab) {
    case 'overview': return renderOverview();
    case 'education': return renderEducation();
    case 'skills': return renderSkills();
    case 'internships': return renderInternships();
    case 'achievements': return renderAchievements();
    case 'projects': return renderProjects();
    case 'hobbies': return renderHobbies();
    case 'json': return renderJson();
    default: return renderOverview();
  }
};

export default ResumeContent;
