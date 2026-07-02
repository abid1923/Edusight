import React, { useState, useEffect, useRef } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import client from '../api/client';
import { 
  LayoutDashboard, 
  BookOpen, 
  BrainCircuit, 
  LogOut, 
  Menu, 
  X, 
  Sun, 
  Moon, 
  Sparkles, 
  ChevronRight,
  User,
  Mail,
  Lock,
  Camera,
  Loader2,
  Settings,
  Trash2
} from 'lucide-react';

const MainLayout = () => {
  const { user, token, loading, logout, updateProfileState } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [avatar, setAvatar] = useState(null);

  // Profile fields state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [usernameVal, setUsernameVal] = useState('');
  const [passwordVal, setPasswordVal] = useState('');
  const [confirmPasswordVal, setConfirmPasswordVal] = useState('');
  
  const [modalError, setModalError] = useState('');
  const [modalSuccess, setModalSuccess] = useState('');
  const [modalSubmitting, setModalSubmitting] = useState(false);

  const fileInputRef = useRef(null);
  
  // Theme state initialized from localStorage/system preference
  const [darkMode, setDarkMode] = useState(() => {
    const stored = localStorage.getItem('theme');
    if (stored) return stored === 'dark';
    return true; // default dark mode for premium look
  });

  // Handle redirect if not authenticated
  useEffect(() => {
    if (!token && !loading) {
      navigate('/login');
    }
  }, [token, loading, navigate]);

  // Synchronize darkMode class on document.body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  // Sync avatar and form fields
  useEffect(() => {
    if (user?.username) {
      setAvatar(localStorage.getItem(`avatar_${user.username}`) || null);
    }
    if (user && modalOpen) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setUsernameVal(user.username || '');
      setPasswordVal('');
      setConfirmPasswordVal('');
      setModalError('');
      setModalSuccess('');
    }
  }, [user, modalOpen]);

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-[#0b0f19] flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 rounded-full border-4 border-brand-200 border-t-brand-500 animate-spin mb-4"></div>
          <p className="text-slate-500 dark:text-slate-400 font-medium">Memuat data pembelajaran...</p>
        </div>
      </div>
    );
  }

  // Sidebar nav items without Settings sidebar path
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Materi Belajar', path: '/learning', icon: BookOpen },
    { name: 'AI Insight', path: '/insight', icon: BrainCircuit },
  ];

  const handleAvatarClick = () => {
    fileInputRef.current.click();
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      setModalError('Ukuran gambar maksimal adalah 2MB.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result;
      localStorage.setItem(`avatar_${user.username}`, base64String);
      setAvatar(base64String);
      setModalSuccess('Foto profil berhasil diperbarui!');
    };
    reader.readAsDataURL(file);
  };

  const handleDeleteAvatar = () => {
    localStorage.removeItem(`avatar_${user.username}`);
    setAvatar(null);
    setModalSuccess('Foto profil berhasil dihapus!');
  };


  const handleUpdateProfileSubmit = async (e) => {
    e.preventDefault();
    setModalError('');
    setModalSuccess('');

    if (!usernameVal.trim() || !email.trim()) {
      setModalError('Username dan Email harus diisi.');
      return;
    }

    if (passwordVal && passwordVal !== confirmPasswordVal) {
      setModalError('Konfirmasi kata sandi tidak cocok.');
      return;
    }

    if (passwordVal && passwordVal.length < 6) {
      setModalError('Kata sandi baru minimal 6 karakter.');
      return;
    }

    try {
      setModalSubmitting(true);
      
      const payload = {
        full_name: fullName.trim() || null,
        email: email.trim(),
        username: usernameVal.trim()
      };

      if (passwordVal) {
        payload.password = passwordVal;
      }

      // Call profile update API endpoint
      const response = await client.put('/api/users/profile', payload);
      
      // Update local storage avatar key if username changed
      if (usernameVal.trim() !== user.username) {
        const currentAvatar = localStorage.getItem(`avatar_${user.username}`);
        if (currentAvatar) {
          localStorage.setItem(`avatar_${usernameVal.trim()}`, currentAvatar);
          localStorage.removeItem(`avatar_${user.username}`);
        }
      }

      updateProfileState(response.data);
      setModalSuccess('Profil berhasil diperbarui!');
      setPasswordVal('');
      setConfirmPasswordVal('');
    } catch (err) {
      console.error('Failed to update profile:', err);
      setModalError(err.response?.data?.detail || 'Gagal memperbarui profil.');
    } finally {
      setModalSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-[#0b0f19] text-slate-800 dark:text-slate-100 font-sans transition-colors duration-300">
      
      {/* ─── SIDEBAR BACKDROP FOR MOBILE ─── */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ─── SIDEBAR NAVIGATION ─── */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-[#0f1626] border-r border-slate-200/60 dark:border-slate-800/60 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Sidebar Header */}
        <div className="h-20 px-6 border-b border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center space-x-2" onClick={() => setSidebarOpen(false)}>
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand-500 to-blue-600 flex items-center justify-center shadow-md shadow-brand-500/25">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-brand-600 to-blue-500 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                Edusight
              </span>
              <span className="block text-[10px] text-slate-400 font-medium tracking-wide">AI-POWERED LEARNING</span>
            </div>
          </Link>
          <button 
            onClick={() => setSidebarOpen(false)}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white rounded-lg lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center px-4 py-3.5 rounded-xl font-medium text-sm transition-all duration-200 group
                  ${isActive 
                    ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/15' 
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'}
                `}
              >
                <Icon className={`w-5 h-5 mr-3.5 transition-transform duration-200 group-hover:scale-105 ${isActive ? 'text-white' : 'text-slate-400 dark:text-slate-500 group-hover:text-brand-500'}`} />
                <span className="flex-1">{item.name}</span>
                {isActive && <ChevronRight className="w-4 h-4 text-white opacity-80" />}
              </Link>
            );
          })}
        </nav>

        {/* User Info & Logout */}
        <div className="p-4 border-t border-slate-200/60 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-900/30">
          <div className="flex items-center space-x-3 mb-4 px-2">
            {avatar ? (
              <img src={avatar} alt="Avatar" className="w-10 h-10 rounded-full object-cover border border-slate-200 dark:border-slate-800" />
            ) : (
              <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-950 flex items-center justify-center border border-brand-200 dark:border-brand-900 text-brand-600 dark:text-brand-400 font-bold uppercase">
                {user.full_name ? user.full_name.charAt(0) : user.username.charAt(0)}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate dark:text-slate-200">
                {user.full_name || user.username}
              </p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 truncate">
                {user.email}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            className="w-full flex items-center justify-center px-4 py-2.5 rounded-xl border border-rose-200/50 hover:bg-rose-50 dark:border-rose-900/30 dark:hover:bg-rose-950/20 text-rose-600 dark:text-rose-400 font-semibold text-xs transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Keluar Akun
          </button>
        </div>
      </aside>

      {/* ─── MAIN CONTENT CONTAINER ─── */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen overflow-hidden">
        {/* Top Navbar */}
        <header className="h-20 px-6 lg:px-8 border-b border-slate-200/60 dark:border-slate-800/60 bg-white/70 dark:bg-[#0b0f19]/70 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl lg:hidden"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="hidden sm:block">
              <h2 className="text-lg font-bold dark:text-slate-100">
                {location.pathname === '/dashboard' && 'Dashboard'}
                {location.pathname === '/learning' && 'Kurikulum Pembelajaran'}
                {location.pathname === '/insight' && 'AI Insight & Analisis'}
              </h2>
              <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
                {location.pathname === '/dashboard' && 'Berikut adalah ringkasan performa dan tipe belajar belajarmu hari ini.'}
                {location.pathname === '/learning' && 'Pelajari topik-topik terstruktur untuk membangun pemahaman kuat.'}
                {location.pathname === '/insight' && 'Analisis mendalam mengenai kekuatan dan area perbaikan belajarmu.'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Theme Toggle Button */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2.5 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl transition-all duration-200 focus:outline-none"
              aria-label="Toggle Theme"
            >
              {darkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
            </button>

            {/* Profile Menu Trigger (Opens Modal) */}
            <button 
              onClick={() => setModalOpen(true)}
              className="flex items-center space-x-2.5 p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl transition-all duration-200"
            >
              {avatar ? (
                <img src={avatar} alt="Avatar" className="w-8 h-8 rounded-full object-cover border border-slate-200 dark:border-slate-800" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs font-bold uppercase shadow-sm shadow-brand-500/20">
                  {user.full_name ? user.full_name.charAt(0) : user.username.charAt(0)}
                </div>
              )}
              <span className="hidden md:inline text-sm font-semibold dark:text-slate-300">
                {user.username}
              </span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <Outlet />
        </main>
      </div>

      {/* ─── GLOBAL SETTINGS MODAL ─── */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
          
          <div className="bg-white dark:bg-[#0f1626] border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl relative flex flex-col max-h-[90vh] overflow-hidden animate-scale-up">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-850 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-brand-500" />
                <h3 className="font-bold text-base text-slate-800 dark:text-white">Pengaturan Profil</h3>
              </div>
              <button 
                onClick={() => setModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              {modalError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/25 text-rose-600 dark:text-rose-400 text-xs rounded-xl font-semibold">
                  {modalError}
                </div>
              )}
              {modalSuccess && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 text-xs rounded-xl font-semibold">
                  {modalSuccess}
                </div>
              )}

              {/* Avatar Upload Display */}
              <div className="flex flex-col items-center space-y-3">
                <div className="relative group cursor-pointer" onClick={handleAvatarClick}>
                  {avatar ? (
                    <img src={avatar} alt="Avatar" className="w-24 h-24 rounded-full object-cover border-2 border-brand-500 shadow-md" />
                  ) : (
                    <div className="w-24 h-24 rounded-full bg-brand-100 dark:bg-brand-950/60 border-2 border-brand-500 flex items-center justify-center text-brand-650 dark:text-brand-400 text-3xl font-extrabold uppercase shadow-sm">
                      {user.full_name ? user.full_name.charAt(0) : user.username.charAt(0)}
                    </div>
                  )}
                  {/* Photo Overlay */}
                  <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <Camera className="w-6 h-6 text-white" />
                  </div>
                </div>

                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleAvatarChange} 
                  accept="image/*" 
                  className="hidden" 
                />
                <div className="flex flex-col items-center space-y-1.5">
                  <span className="text-[10px] text-slate-400 dark:text-slate-500 font-bold block text-center uppercase tracking-wider">
                    Ketuk foto untuk mengunggah gambar baru
                  </span>
                  {avatar && (
                    <button
                      type="button"
                      onClick={handleDeleteAvatar}
                      className="text-[11px] font-bold text-rose-500 hover:text-rose-600 dark:hover:text-rose-400 transition-colors flex items-center gap-1 focus:outline-none"
                    >
                      <Trash2 className="w-3 h-3" />
                      Hapus Foto Profil
                    </button>
                  )}
                </div>
              </div>

              {/* Form Update Profile */}
              <form onSubmit={handleUpdateProfileSubmit} className="space-y-4">
                
                {/* Username */}
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-350 block" htmlFor="modalUsername">
                    Username
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
                      <User className="w-4 h-4" />
                    </div>
                    <input
                      id="modalUsername"
                      type="text"
                      className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400"
                      value={usernameVal}
                      onChange={(e) => setUsernameVal(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Email */}
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-350 block" htmlFor="modalEmail">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      id="modalEmail"
                      type="email"
                      className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Nama Lengkap */}
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-350 block" htmlFor="modalFullName">
                    Nama Lengkap
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
                      <User className="w-4 h-4" />
                    </div>
                    <input
                      id="modalFullName"
                      type="text"
                      className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                    />
                  </div>
                </div>

                {/* Password section */}
                <div className="pt-4 border-t border-slate-100 dark:border-slate-850 space-y-4">
                  <span className="block text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                    Ganti Kata Sandi (Kosongkan jika tidak ingin mengubah)
                  </span>

                  {/* Password Baru */}
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-600 dark:text-slate-350 block" htmlFor="modalPassword">
                      Kata Sandi Baru
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
                        <Lock className="w-4 h-4" />
                      </div>
                      <input
                        id="modalPassword"
                        type="password"
                        className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400"
                        placeholder="Minimal 6 karakter"
                        value={passwordVal}
                        onChange={(e) => setPasswordVal(e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Konfirmasi Password */}
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-600 dark:text-slate-350 block" htmlFor="modalConfirmPassword">
                      Konfirmasi Kata Sandi Baru
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
                        <Lock className="w-4 h-4" />
                      </div>
                      <input
                        id="modalConfirmPassword"
                        type="password"
                        className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400"
                        placeholder="Ulangi kata sandi baru"
                        value={confirmPasswordVal}
                        onChange={(e) => setConfirmPasswordVal(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                {/* Actions inside Modal */}
                <div className="pt-4 border-t border-slate-100 dark:border-slate-850 flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setModalOpen(false)}
                    className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    disabled={modalSubmitting}
                    className="btn-primary py-2 px-5 text-xs flex items-center space-x-2 shadow-lg shadow-brand-500/15"
                  >
                    {modalSubmitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                        <span>Menyimpan...</span>
                      </>
                    ) : (
                      <>
                        <span>Simpan Perubahan</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainLayout;
