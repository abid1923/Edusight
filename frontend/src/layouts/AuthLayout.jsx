import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import { Sparkles, Sun, Moon } from 'lucide-react';

const AuthLayout = () => {
  const { token, loading } = useAuth();
  const navigate = useNavigate();
  
  const [darkMode, setDarkMode] = useState(() => {
    const stored = localStorage.getItem('theme');
    if (stored) return stored === 'dark';
    return true; // default dark
  });

  useEffect(() => {
    if (token && !loading) {
      navigate('/dashboard');
    }
  }, [token, loading, navigate]);

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50 dark:bg-[#0b0f19] text-slate-800 dark:text-slate-100 relative overflow-hidden transition-colors duration-300">
      {/* Subtle ambient lighting for dark mode only */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/5 dark:bg-brand-500/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-blue-500/5 dark:bg-blue-500/10 rounded-full blur-[120px] pointer-events-none"></div>

      {/* Floating theme toggle */}
      <button
        onClick={() => setDarkMode(!darkMode)}
        className="absolute top-6 right-6 p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-brand-500 dark:hover:text-brand-400 transition-colors shadow-sm"
      >
        {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
      </button>

      <div className="w-full max-w-md relative z-10">
        {/* Brand header */}
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-500 to-blue-600 flex items-center justify-center shadow-lg shadow-brand-500/30 mb-4 hover:scale-105 transition-transform duration-300">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">
            Edusight
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1.5 font-medium">Platform belajar yang memahami gaya belajarmu</p>
        </div>

        {/* Card containing Login/Register forms */}
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur-md border border-slate-200 dark:border-slate-800/80 rounded-2xl p-8 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
