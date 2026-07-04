
import React from 'react';
import { ActiveTab } from '../types';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  isParsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isParsed }) => {
  const menuItems: { id: ActiveTab; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: 'fa-user' },
    { id: 'education', label: 'Education', icon: 'fa-graduation-cap' },
    { id: 'skills', label: 'Skills', icon: 'fa-tools' },
    { id: 'internships', label: 'Internships', icon: 'fa-id-badge' },
    { id: 'achievements', label: 'Achievements', icon: 'fa-trophy' },
    { id: 'projects', label: 'Projects', icon: 'fa-diagram-project' },
    { id: 'hobbies', label: 'Hobbies', icon: 'fa-heart' },
    { id: 'json', label: 'Raw JSON', icon: 'fa-code' },
  ];

  return (
    <div className="w-64 bg-white h-full border-r border-slate-200 flex flex-col">
      <div className="p-6 border-b border-slate-100">
        <h1 className="text-xl font-bold text-indigo-600 tracking-tight flex items-center gap-2">
          <i className="fas fa-file-invoice"></i>
          MOCKSTEP
        </h1>
        <p className="text-xs text-slate-500 mt-1 uppercase font-semibold tracking-wider">Resume Parser</p>
      </div>
      
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto custom-scrollbar">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => isParsed && setActiveTab(item.id)}
            disabled={!isParsed}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
              !isParsed 
                ? 'text-slate-300 cursor-not-allowed'
                : activeTab === item.id
                  ? 'bg-indigo-50 text-indigo-600 shadow-sm'
                  : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <i className={`fas ${item.icon} w-5 text-center`}></i>
            {item.label}
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-100">
        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-2">Powered by</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-xs font-semibold text-slate-700">MOCKSTEP AI Engine</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
