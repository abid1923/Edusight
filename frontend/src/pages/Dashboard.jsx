import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../store/AuthContext';
import { 
  Trophy, 
  BookOpen, 
  Activity, 
  BrainCircuit, 
  Sparkles, 
  ArrowRight, 
  TrendingUp,
  Award,
  Zap,
  Target,
  LogIn,
  CheckCircle2,
  HelpCircle,
  AlertCircle,
  Clock,
  ChevronRight,
  Compass
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip,
  CartesianGrid 
} from 'recharts';

const Dashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [continueLearning, setContinueLearning] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await client.get('/api/users/dashboard');
      setData(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching dashboard statistics:', err);
      setError('Gagal memuat data dashboard. Pastikan backend Anda berjalan.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (data && data.username) {
      const stored = localStorage.getItem(`continue_learning_${data.username}`);
      if (stored) {
        try {
          setContinueLearning(JSON.parse(stored));
        } catch (e) {
          console.error('Failed to parse continue learning bookmark', e);
        }
      }
    }
  }, [data]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        {/* Header skeleton */}
        <div className="h-10 w-48 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>

        {/* Hero Card skeleton */}
        <div className="h-44 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
        
        {/* Main layout skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="h-64 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
              <div className="h-64 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
            </div>
            <div className="h-56 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
          </div>
          <div className="space-y-6">
            <div className="h-48 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
            <div className="h-40 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
            <div className="h-64 bg-slate-200 dark:bg-slate-800/50 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl max-w-xl mx-auto my-12">
        <AlertCircle className="w-12 h-12 text-rose-500 mx-auto mb-4" />
        <h3 className="text-lg font-bold mb-2">Terjadi Kesalahan</h3>
        <p className="text-slate-500 dark:text-slate-400 text-sm mb-6">{error || 'Gagal memuat data.'}</p>
        <button 
          onClick={fetchDashboardData}
          className="btn-primary flex items-center justify-center mx-auto space-x-2 text-xs py-2.5"
        >
          <span>Coba Ulang</span>
        </button>
      </div>
    );
  }

  const { 
    username, 
    learning_type, 
    reason, 
    strength, 
    weakness, 
    motivation, 
    progress_summary, 
    recommendation_summary,
    features
  } = data;

  const { 
    total_materials_completed, 
    total_quiz_attempts, 
    total_learning_paths, 
    overall_progress_percent,
    recent_activities,
    path_progress 
  } = progress_summary;

  // Helper for activity icon & label
  const getActivityDetails = (type) => {
    switch (type) {
      case 'login':
        return { icon: LogIn, color: 'text-brand-500 bg-brand-50 dark:bg-brand-950/40 border-brand-200 dark:border-brand-900', label: 'Login ke Platform' };
      case 'material_complete':
        return { icon: CheckCircle2, color: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900', label: 'Menyelesaikan Materi' };
      case 'quiz_attempt':
        return { icon: Award, color: 'text-blue-500 bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-900', label: 'Mengerjakan Kuis' };
      default:
        return { icon: HelpCircle, color: 'text-slate-500 bg-slate-50 dark:bg-slate-900 border-slate-200', label: 'Aktivitas Belajar' };
    }
  };

  const getLearningTypeBadgeDetails = (type) => {
    switch (type) {
      case 'Active Learner':
        return { color: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20', label: 'Active Learner' };
      case 'Moderate Learner':
        return { color: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20', label: 'Moderate Learner' };
      case 'Passive Learner':
        return { color: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20', label: 'Passive Learner' };
      default:
        return { color: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-200/50', label: 'Belum Diketahui' };
    }
  };

  // Build the item to continue learning
  const resumeItem = continueLearning || data.progress_summary?.next_material || null;

  // Process data for charts
  const donutData = [
    { name: 'Selesai', value: overall_progress_percent, fill: '#3b82f6' },
    { name: 'Sisa', value: 100 - overall_progress_percent, fill: '#334155' }
  ];

  const getWeeklyActivityData = () => {
    const days = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];
    const data = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(today.getDate() - i);
      const dayName = days[d.getDay()];
      const count = recent_activities.filter(act => {
        if (!act.created_at) return false;
        const actDate = new Date(act.created_at);
        return actDate.toDateString() === d.toDateString();
      }).length;
      data.push({ name: dayName, aktivitas: count });
    }
    return data;
  };
  const weeklyData = getWeeklyActivityData();

  return (
    <div className="space-y-6 pb-12">
      {/* ─── HERO GREETING BANNER (BLUE GRADIENT) ─── */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white p-6 md:p-8 shadow-lg shadow-blue-500/10">
        {/* Floating circles decoration */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-white/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>
        <div className="absolute bottom-0 left-1/3 w-64 h-64 bg-indigo-500/10 rounded-full blur-2xl -mb-12 pointer-events-none"></div>
        
        <div className="relative z-10 space-y-2">
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Halo, {user?.full_name || user?.username || 'Pelajar'}!
          </h2>
          <p className="text-sm text-blue-100/90 leading-relaxed font-medium max-w-2xl">
            Selamat datang kembali di platform pembelajaran adaptif. Mari tingkatkan pemahaman dan aktivitas belajar Anda hari ini!
          </p>
        </div>
      </section>

      {/* ─── CORE SECTIONS GRID ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* ================= LEFT & CENTER COLUMN (2/3 WIDTH) ================= */}
        <div className="lg:col-span-2 flex flex-col justify-between">
          
          {/* Row of Stats Visualizations: Donut Progress Chart & Stats Grid Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            
            {/* Learning Time / Progress Chart Card */}
            <div className="glass-card p-6 flex flex-col justify-center items-center h-72 relative">
              <div className="absolute top-6 left-6 right-6 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Progress Belajar</span>
                <Clock className="w-4 h-4 text-brand-500" />
              </div>
              
              <div className="w-full flex-1 flex items-center justify-center relative mt-6">
                <ResponsiveContainer width="100%" height={150}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={58}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      <Cell fill="#3b82f6" />
                      <Cell fill="#1e293b" />
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                {/* Center score display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-black tracking-tight">{overall_progress_percent}%</span>
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Selesai</span>
                </div>
              </div>
            </div>

            {/* Learning Stats Grid Card (Replaced the weekly activity line chart) */}
            <div className="glass-card p-6 flex flex-col justify-between h-72">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Ringkasan Statistik</span>
                <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
              </div>

              <div className="flex-1 flex flex-col justify-center space-y-4">
                {/* Stat 1: Materi Selesai */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
                      <BookOpen className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide">Materi Selesai</span>
                      <span className="text-xs font-extrabold text-slate-700 dark:text-slate-200">{total_materials_completed}</span>
                    </div>
                  </div>
                </div>

                {/* Stat 2: Percobaan Kuis */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center text-brand-500">
                      <Trophy className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide">Pengerjaan Kuis</span>
                      <span className="text-xs font-extrabold text-slate-700 dark:text-slate-200">{total_quiz_attempts} Kali Percobaan</span>
                    </div>
                  </div>
                </div>

                {/* Stat 3: Rata-rata Nilai */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide">Rata-rata Nilai</span>
                      <span className="text-xs font-extrabold text-slate-700 dark:text-slate-200">
                        {features && features.avg_quiz_score !== undefined ? features.avg_quiz_score.toFixed(1) : '0.0'}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Progress Jalur Pembelajaran Section (Vertical layout stack stretched to match right column height) */}
          <section className="glass-card p-6 flex-1 flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-3 mb-4">
              <div>
                <h3 className="font-bold text-sm uppercase tracking-wider text-slate-850 dark:text-slate-100 flex items-center">
                  <Trophy className="w-5 h-5 text-brand-500 mr-2" />
                  Progress Jalur Pembelajaran
                </h3>
              </div>
              <span className="text-[10px] font-extrabold bg-blue-500/10 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-lg border border-blue-500/20">
                {total_learning_paths} PATHS ACTIVE
              </span>
            </div>

            <div className="flex-1 flex flex-col justify-around space-y-5">
              {path_progress.map((p, idx) => (
                <div 
                  key={p.path_id} 
                  className="p-6 rounded-2xl border border-slate-150 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 flex flex-col md:flex-row md:items-center justify-between gap-5 hover:border-brand-500/30 hover:scale-[1.01] hover:shadow-lg hover:shadow-brand-500/5 transition-all duration-200 group"
                >
                  <div className="flex items-center space-x-5">
                    <div className={`px-4 py-2.5 rounded-2xl text-xs font-black tracking-wider uppercase ${
                      idx === 0 
                        ? 'bg-blue-500/10 text-blue-500' 
                        : idx === 1 
                          ? 'bg-cyan-500/10 text-cyan-500' 
                          : 'bg-emerald-500/10 text-emerald-500'
                    }`}>
                      Path {idx + 1}
                    </div>
                    <div>
                      <h4 className="font-extrabold text-base text-slate-700 dark:text-slate-200 group-hover:text-brand-500 transition-colors">
                        {p.path_name}
                      </h4>
                      <span className="text-xs font-bold text-slate-400 dark:text-slate-500 mt-1 block">
                        {p.completed} dari {p.total} Materi Selesai
                      </span>
                    </div>
                  </div>

                  <div className="flex-1 max-w-md w-full space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-extrabold text-slate-400">
                      <span>PROGRESS</span>
                      <span className="text-slate-700 dark:text-slate-300 text-sm font-black">{p.percent}%</span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-800 h-3 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full bg-gradient-to-r ${
                          idx === 0 
                            ? 'from-blue-500 to-indigo-600' 
                            : idx === 1 
                              ? 'from-cyan-500 to-blue-500' 
                              : 'from-emerald-500 to-teal-500'
                        } transition-all duration-500`}
                        style={{ width: `${p.percent}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </div>

        {/* ================= RIGHT SIDEBAR COLUMN (1/3 WIDTH) ================= */}
        <div className="space-y-6">
          
          {/* Card 1: AI Gaya Belajar (Profile Analysis Summary Card) */}
          <section className="glass-card p-6 border-l-4 border-l-brand-500 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-brand-500/10 dark:bg-brand-500/5 rounded-full blur-2xl -mr-12 -mt-12 pointer-events-none"></div>
            
            <div className="relative z-10 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">AI Gaya Belajar</span>
                <BrainCircuit className="w-4 h-4 text-brand-500" />
              </div>

              {/* Learning Type Badge */}
              {(() => {
                const badge = getLearningTypeBadgeDetails(learning_type);
                return (
                  <div className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold ${badge.color}`}>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{badge.label}</span>
                  </div>
                );
              })()}

              <div className="space-y-3 pt-1">
                {learning_type === 'Undetermined' ? (
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Aktivitas Anda belum memenuhi kriteria kognitif AI. Terus kerjakan materi dan kuis untuk membuka profil Anda!
                  </p>
                ) : (
                  <>
                    <p className="text-xs text-slate-600 dark:text-slate-350 leading-relaxed">
                      {reason || 'Anda memiliki pola belajar teranalisis AI.'}
                    </p>
                    {motivation && (
                      <p className="text-[11px] italic text-slate-400 dark:text-slate-500 border-l border-slate-300 dark:border-slate-700 pl-2">
                        "{motivation}"
                      </p>
                    )}
                  </>
                )}
              </div>

              <div className="pt-2">
                <Link 
                  to="/insight" 
                  className="btn-primary py-2 w-full text-center text-[10px] font-bold uppercase tracking-wider flex items-center justify-center space-x-1 shadow-md shadow-brand-500/10"
                >
                  <span>Analisis Kognitif AI</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </section>

          {/* Card 2: Lanjutkan Belajar (Continue Slide box) */}
          <section className="glass-card p-6 border-l-4 border-l-emerald-500 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/10 dark:bg-emerald-500/5 rounded-full blur-2xl -mr-12 -mt-12 pointer-events-none"></div>
            
            <div className="relative z-10 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Lanjutkan Belajar</span>
                <BookOpen className="w-4 h-4 text-emerald-500" />
              </div>

              {resumeItem ? (
                <div className="space-y-4">
                  <div className="p-3.5 rounded-xl bg-slate-50/50 dark:bg-slate-900/40 border border-slate-100 dark:border-slate-800 space-y-1">
                    <span className="block text-[8px] font-bold text-slate-400 dark:text-slate-500 tracking-wider">JALUR BELAJAR</span>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate block">
                      {resumeItem.pathName}
                    </span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 truncate block">
                      {resumeItem.chapterName} • Slide {resumeItem.slideIndex + 1}
                    </span>
                  </div>

                  <Link 
                    to={`/learning?pathId=${resumeItem.pathId}&materialId=${resumeItem.materialId}`} 
                    className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white text-[10px] font-bold uppercase tracking-wider flex items-center justify-center space-x-1 transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-md shadow-emerald-500/20"
                  >
                    <span>Lanjutkan Slide</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              ) : (
                <div className="p-3.5 rounded-xl bg-slate-50/50 dark:bg-slate-900/40 border border-slate-100 dark:border-slate-800 text-center py-5">
                  <Trophy className="w-7 h-7 text-amber-500 mx-auto mb-2 animate-bounce" />
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-200 block">Semua Materi Selesai!</span>
                  <span className="text-[10px] text-slate-400 block mt-1">Selamat atas kelulusan pembelajaran Anda.</span>
                </div>
              )}
            </div>
          </section>

          {/* Card 3: Aktivitas Terbaru (Log timeline, fills the right column nicely) */}
          <section className="glass-card p-6 border-l-4 border-l-indigo-500">
            <div className="flex items-center justify-between mb-5 border-b border-slate-100 dark:border-slate-800/80 pb-2">
              <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Aktivitas Terbaru</span>
              <Activity className="w-4 h-4 text-indigo-500" />
            </div>

            <div className="space-y-4 max-h-[220px] overflow-y-auto pr-1">
              {recent_activities.length === 0 ? (
                <div className="text-center py-6 text-slate-400 text-[10px] font-semibold uppercase tracking-wider">
                  Belum ada aktivitas tercatat
                </div>
              ) : (
                <div className="relative border-l border-slate-200 dark:border-slate-800 ml-2.5 space-y-5 py-1">
                  {recent_activities.map((act, i) => {
                    const details = getActivityDetails(act.type);
                    const ActIcon = details.icon;
                    const timestampStr = act.created_at 
                      ? new Date(act.created_at).toLocaleDateString('id-ID', {
                          day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
                        })
                      : 'Baru saja';
                    
                    return (
                      <div key={i} className="relative pl-5 group">
                        {/* Dot container */}
                        <div className={`absolute -left-3 top-0.5 w-6 h-6 rounded-full border flex items-center justify-center ${details.color} shadow-sm`}>
                          <ActIcon className="w-3 h-3" />
                        </div>
                        
                        <div className="space-y-0.5">
                          <p className="text-[11px] font-bold text-slate-700 dark:text-slate-350">
                            {details.label}
                          </p>
                          <span className="text-[9px] font-semibold text-slate-400 block">
                            {timestampStr}
                          </span>
                          {act.metadata && act.metadata.path && (
                            <span className="text-[9px] text-brand-500 font-bold block">
                              Path: {act.metadata.path}
                            </span>
                          )}
                          {act.metadata && act.metadata.score !== undefined && (
                            <span className="text-[9px] text-emerald-500 font-extrabold block">
                              Skor: {act.metadata.score}/100
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </section>

        </div>

      </div>
    </div>
  );
};

export default Dashboard;
