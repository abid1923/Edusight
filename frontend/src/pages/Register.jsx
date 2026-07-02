import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import { User, Mail, Lock, Sparkles, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [errorMsg, setErrorMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username.trim() || !email.trim() || !password.trim()) {
      setErrorMsg('Semua kolom penting harus diisi.');
      return;
    }

    if (username.length < 3) {
      setErrorMsg('Username minimal harus 3 karakter.');
      return;
    }

    if (password.length < 6) {
      setErrorMsg('Kata sandi minimal harus 6 karakter.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Konfirmasi kata sandi tidak cocok.');
      return;
    }

    try {
      setErrorMsg('');
      setSubmitting(true);
      const success = await register(username, email, password, fullName);
      if (success) {
        navigate('/dashboard');
      }
    } catch (err) {
      setErrorMsg(err.message || 'Registrasi gagal. Silakan gunakan username atau email lain.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="space-y-1">
        <h2 className="text-xl font-bold tracking-tight text-slate-800 dark:text-white">Daftar Akun Baru</h2>
        <p className="text-slate-500 dark:text-slate-400 text-xs">Mulai perjalanan belajar adaptif cerdas berbasis AI hari ini.</p>
      </div>

      {errorMsg && (
        <div className="flex items-start p-3 bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs rounded-xl space-x-2">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3.5">
        {/* Nama Lengkap */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block" htmlFor="fullName">
            Nama Lengkap (Opsional)
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
              <User className="w-4 h-4" />
            </div>
            <input
              id="fullName"
              type="text"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/35 focus:border-brand-500 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 transition-all duration-200"
              placeholder="Masukkan nama lengkap Anda"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={submitting}
            />
          </div>
        </div>

        {/* Username */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block" htmlFor="username">
            Username
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
              <User className="w-4 h-4" />
            </div>
            <input
              id="username"
              type="text"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/35 focus:border-brand-500 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 transition-all duration-200"
              placeholder="Min. 3 karakter, tanpa spasi"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
              required
            />
          </div>
        </div>

        {/* Email */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block" htmlFor="email">
            Alamat Email
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
              <Mail className="w-4 h-4" />
            </div>
            <input
              id="email"
              type="email"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/35 focus:border-brand-500 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 transition-all duration-200"
              placeholder="nama@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={submitting}
              required
            />
          </div>
        </div>

        {/* Password */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block" htmlFor="password">
            Kata Sandi
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
              <Lock className="w-4 h-4" />
            </div>
            <input
              id="password"
              type="password"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/35 focus:border-brand-500 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 transition-all duration-200"
              placeholder="Minimal 6 karakter"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
              required
            />
          </div>
        </div>

        {/* Confirm Password */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block" htmlFor="confirmPassword">
            Konfirmasi Kata Sandi
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
              <Lock className="w-4 h-4" />
            </div>
            <input
              id="confirmPassword"
              type="password"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/35 focus:border-brand-500 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 transition-all duration-200"
              placeholder="Ulangi kata sandi Anda"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={submitting}
              required
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full mt-3 py-3 bg-brand-500 hover:bg-brand-600 text-white rounded-xl font-semibold text-xs shadow-lg shadow-brand-500/25 flex items-center justify-center space-x-2 transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-55"
          disabled={submitting}
        >
          {submitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Mendaftarkan...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Daftar & Belajar</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      {/* Navigation to login */}
      <div className="text-center pt-2 border-t border-slate-200 dark:border-slate-800/40">
        <p className="text-[11px] text-slate-500 dark:text-slate-400">
          Sudah memiliki akun?{' '}
          <Link to="/login" className="text-brand-600 dark:text-brand-400 hover:text-brand-500 dark:hover:text-brand-300 font-semibold transition-colors duration-200">
            Masuk di sini
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
