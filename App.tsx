
import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ResumeContent from './components/ResumeContent';
import { parseResume } from './services/geminiService';
import { ResumeData, ActiveTab } from './types';

const App: React.FC = () => {
  const [isParsing, setIsParsing] = useState(false);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [error, setError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        setError(`Fullscreen error: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.docx')) {
      setError("Supported: PDF, Images, DOCX, TXT.");
      return;
    }

    setIsParsing(true);
    setError(null);
    setResumeData(null);

    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const base64String = (reader.result as string).split(',')[1];
        const result = await parseResume(base64String, file.type || 'application/octet-stream');
        setResumeData(result);
        setActiveTab('overview');
      } catch (err: any) {
        setError(err.message || "Fast-parse failed. Please ensure the file contains readable text.");
      } finally {
        setIsParsing(false);
      }
    };
    reader.onerror = () => {
      setError("Failed to read local file.");
      setIsParsing(false);
    };
    reader.readAsDataURL(file);
  };

  const resetToHome = () => {
    setResumeData(null);
    setError(null);
    setIsParsing(false);
  };

  const triggerFileInput = () => fileInputRef.current?.click();

  return (
    <div className="flex h-screen w-full bg-slate-50 overflow-hidden font-inter">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isParsed={!!resumeData && !isParsing} 
      />

      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-10 shadow-sm">
          <div className="flex items-center gap-4">
            <button onClick={resetToHome} className="text-slate-400 hover:text-indigo-600 transition-colors text-sm font-semibold flex items-center gap-2">
              <i className="fas fa-home"></i>
              Dashboard
            </button>
            <i className="fas fa-chevron-right text-slate-300 text-[10px]"></i>
            <span className="text-slate-800 text-sm font-bold">
              {resumeData ? 'Analysis Result' : 'Upload Center'}
            </span>
          </div>
          
          <div className="flex items-center gap-3">
            <button 
              onClick={toggleFullscreen}
              className="p-2.5 text-slate-400 hover:text-indigo-600 hover:bg-slate-50 rounded-xl transition-all active:scale-90"
              title="Toggle Fullscreen"
            >
              <i className={`fas ${isFullscreen ? 'fa-compress' : 'fa-expand'} text-lg`}></i>
            </button>
            
            <button 
              onClick={triggerFileInput}
              disabled={isParsing}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white px-5 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all shadow-indigo-100 shadow-lg active:scale-95"
            >
              <i className="fas fa-plus"></i>
              New Upload
            </button>
          </div>
          <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.png,.jpg,.jpeg,.txt,.docx" />
        </header>

        <div className="flex-1 p-8 overflow-y-auto custom-scrollbar">
          {!resumeData && !isParsing && (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto animate-fadeIn">
              <div className="w-20 h-20 bg-indigo-600 rounded-3xl flex items-center justify-center text-white text-3xl mb-8 shadow-xl shadow-indigo-200">
                <i className="fas fa-bolt"></i>
              </div>
              <h2 className="text-4xl font-black text-slate-900 mb-4 tracking-tight">Hyper-Fast Analysis</h2>
              <p className="text-slate-500 text-lg mb-10 leading-relaxed">
                Experience the world's fastest resume parser. Extract structured profile data in under 2 seconds with Flash-AI.
              </p>
              
              <div 
                onClick={triggerFileInput}
                className="w-full border-2 border-dashed border-indigo-200 rounded-[2rem] p-16 hover:border-indigo-500 hover:bg-white cursor-pointer transition-all flex flex-col items-center gap-5 group shadow-sm hover:shadow-xl"
              >
                <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center group-hover:bg-indigo-600 transition-colors">
                  <i className="fas fa-upload text-indigo-600 text-xl group-hover:text-white transition-colors"></i>
                </div>
                <div>
                  <p className="text-slate-800 text-xl font-bold mb-1">Upload Resume</p>
                  <p className="text-slate-400 text-sm italic underline">Fast tracking enabled</p>
                </div>
              </div>

              {error && (
                <div className="mt-8 bg-red-50 text-red-600 p-4 rounded-2xl border border-red-100 flex items-center gap-3 w-full animate-shake">
                  <i className="fas fa-circle-exclamation"></i>
                  <span className="text-sm font-bold">{error}</span>
                </div>
              )}
            </div>
          )}

          {isParsing && (
            <div className="h-full flex flex-col items-center justify-center text-center animate-fadeIn">
              <div className="relative mb-8">
                <div className="w-20 h-20 border-[6px] border-slate-100 border-t-indigo-600 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <i className="fas fa-bolt text-indigo-600 text-xl"></i>
                </div>
              </div>
              <h3 className="text-2xl font-black text-slate-800 mb-2">Analyzing...</h3>
              <p className="text-slate-400 font-medium">Bypassing servers for instant extraction.</p>
              
              <div className="mt-10 w-48 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-indigo-600 h-full w-full animate-loading-bar origin-left"></div>
              </div>
            </div>
          )}

          {resumeData && !isParsing && (
            <div className="max-w-4xl mx-auto h-full pb-12 animate-slideUp">
              <ResumeContent data={resumeData} activeTab={activeTab} />
            </div>
          )}
        </div>
      </main>

      <style>{`
        @keyframes loading-bar {
          0% { transform: scaleX(0); }
          50% { transform: scaleX(0.7); }
          100% { transform: scaleX(1); }
        }
        .animate-loading-bar { animation: loading-bar 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        .animate-fadeIn { animation: fadeIn 0.3s ease-out forwards; }
        .animate-slideUp { animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        .animate-shake { animation: shake 0.5s linear; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { 
          from { opacity: 0; transform: translateY(20px); } 
          to { opacity: 1; transform: translateY(0); } 
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
      `}</style>
    </div>
  );
};

export default App;
