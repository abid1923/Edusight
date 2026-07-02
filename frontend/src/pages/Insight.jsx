import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import { 
  BrainCircuit, 
  Sparkles, 
  AlertCircle, 
  ArrowRight,
  Zap,
  Target,
  Award,
  Loader2,
  ChevronRight,
  ExternalLink,
  Check
} from 'lucide-react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer 
} from 'recharts';

const getLearningTypeDetails = (type) => {
  switch (type) {
    case 'Active Learner':
      return {
        bg: 'from-blue-500/10 to-indigo-500/10 dark:from-blue-500/20 dark:to-indigo-500/20 border-blue-500/30 dark:border-blue-500/40 text-blue-600 dark:text-blue-400 shadow-blue-500/5',
        icon: <Zap className="w-6 h-6 text-blue-500 dark:text-blue-400 animate-bounce" />,
        label: 'Active Learner',
        textGradient: 'from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-300',
        statusText: 'Aktivitas belajar: Tinggi ⚡',
      };
    case 'Moderate Learner':
      return {
        bg: 'from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20 border-emerald-500/30 dark:border-emerald-500/40 text-emerald-600 dark:text-emerald-400 shadow-emerald-500/5',
        icon: <Sparkles className="w-6 h-6 text-emerald-550 dark:text-emerald-400 animate-pulse" />,
        label: 'Moderate Learner',
        textGradient: 'from-emerald-600 to-teal-600 dark:from-emerald-400 dark:to-teal-300',
        statusText: 'Aktivitas belajar: Cukup Baik ✨',
      };
    default: // Passive Learner
      return {
        bg: 'from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20 border-amber-500/30 dark:border-amber-500/40 text-amber-600 dark:text-amber-400 shadow-amber-500/5',
        icon: <Target className="w-6 h-6 text-amber-550 dark:text-amber-455 animate-pulse" />,
        label: 'Passive Learner',
        textGradient: 'from-amber-600 to-orange-600 dark:from-amber-400 dark:to-orange-300',
        statusText: 'Aktivitas belajar: Memerlukan Peningkatan 🎯',
      };
  }
};

const formatIndonesianDateTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  const months = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ];
  const day = date.getDate();
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `Terakhir dianalisis pada: ${day} ${month} ${year} pukul ${hours}.${minutes}`;
};

const Insight = () => {
  const [threshold, setThreshold] = useState(null);
  const [insight, setInsight] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Step 1: Check Activity Threshold
      const thresholdRes = await client.get('/api/insight/threshold');
      setThreshold(thresholdRes.data);
      
      if (thresholdRes.data.meets_threshold) {
        // Step 2: Try to get latest insight
        try {
          const insightRes = await client.get('/api/insight/me');
          setInsight(insightRes.data);
        } catch (insightErr) {
          if (insightErr.response && insightErr.response.status === 404) {
            // Threshold met but no insight generated yet
            setInsight(null);
          } else {
            console.error('Error fetching insight:', insightErr);
            setError('Gagal memuat detail insight.');
          }
        }
      }
    } catch (err) {
      console.error('Error checking threshold:', err);
      setError('Gagal memuat status aktivitas belajar Anda.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      setError('');
      const response = await client.post('/api/insight/generate?force=true');
      if (response.data.success) {
        setInsight(response.data.insight);
      } else {
        setError(response.data.message || 'Gagal generate AI Insight.');
      }
    } catch (err) {
      console.error('Error generating insight:', err);
      setError('Terjadi kesalahan saat menghubungi server AI.');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
        <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Menganalisis data aktivitas belajarmu...</p>
      </div>
    );
  }

  // --- CASE 1: NOT MEETING THRESHOLD ---
  if (threshold && !threshold.meets_threshold) {
    const loginDetail = threshold.details.find(d => d.metric.toLowerCase().includes('login'));
    const quizDetail = threshold.details.find(d => d.metric.toLowerCase().includes('quiz'));
    const materialDetail = threshold.details.find(d => d.metric.toLowerCase().includes('completion') || d.metric.toLowerCase().includes('material'));

    const loginMet = loginDetail ? loginDetail.met : false;
    const quizMet = quizDetail ? quizDetail.met : false;
    const materialMet = materialDetail ? materialDetail.met : false;

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card p-8 border-l-4 border-l-brand-500 overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
          <div className="relative z-10 space-y-2">
            <h3 className="text-xl font-bold flex items-center text-slate-800 dark:text-white">
              <BrainCircuit className="w-7 h-7 text-brand-500 mr-2.5" />
              AI Insight & Analisis Gaya Belajar
            </h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm max-w-2xl leading-relaxed">
              Model AI kami memetakan gaya belajar unik Anda berdasarkan pola aktivitas di platform. Penuhi aktivitas belajar di bawah ini untuk membuka visualisasi Radar Chart dan rekomendasi personal.
            </p>
          </div>
        </div>

        {/* Threshold Requirements */}
        <div className="glass-card p-6 md:p-8 space-y-6">
          <div>
            <h4 className="font-bold text-base mb-1.5 flex items-center text-slate-800 dark:text-slate-200">
              <AlertCircle className="w-5 h-5 text-amber-500 mr-2 animate-pulse" />
              Aktivitas Belajar Belum Cukup
            </h4>
            <p className="text-xs text-slate-550 dark:text-slate-400 leading-relaxed font-medium">
              Selesaikan lebih banyak aktivitas belajar untuk mendapatkan analisis gaya belajar yang lebih akurat.
            </p>
          </div>

          <div className="space-y-4 max-w-md pt-2">
            {[
              { label: 'Pelajari beberapa materi', met: materialMet },
              { label: 'Kerjakan kuis', met: quizMet },
              { label: 'Tingkatkan aktivitas belajar', met: loginMet }
            ].map((item, idx) => (
              <div key={idx} className="flex items-center space-x-3 text-sm text-slate-700 dark:text-slate-300">
                <div className={`w-5 h-5 rounded-md border flex items-center justify-center transition-all duration-150 ${item.met ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-350 dark:border-slate-750 bg-white dark:bg-slate-900'}`}>
                  {item.met && <Check className="w-3.5 h-3.5" />}
                </div>
                <span className={item.met ? 'line-through text-slate-450 dark:text-slate-500 font-medium' : 'font-semibold'}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end">
            <Link to="/learning" className="btn-primary py-2.5 px-5 text-xs flex items-center space-x-2">
              <span>Mulai Belajar Sekarang</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // --- CASE 2: THRESHOLD MET, READY TO GENERATE ---
  if (threshold && threshold.meets_threshold && !insight) {
    return (
      <div className="space-y-6">
        <div className="glass-card p-8 border-l-4 border-l-brand-500 overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="space-y-2">
              <h3 className="text-xl font-bold flex items-center text-slate-800 dark:text-white">
                <BrainCircuit className="w-7 h-7 text-brand-500 mr-2.5" />
                AI Insight Siap Dibuat!
              </h3>
              <p className="text-slate-500 dark:text-slate-400 text-sm max-w-xl leading-relaxed">
                Hebat! Aktivitas belajarmu telah memenuhi syarat minimum. Model AI sekarang dapat mengelompokkan datamu dan memberikan analisis profil kognitif belajar yang akurat.
              </p>
            </div>
            
            <button 
              onClick={handleGenerate}
              disabled={generating}
              className="btn-primary py-3 px-6 text-xs flex items-center shrink-0 space-x-2"
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  <span>Menganalisis...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  <span>Generate AI Insight</span>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-500/10 text-rose-500 border border-rose-500/20 rounded-xl text-xs font-semibold">
            {error}
          </div>
        )}
      </div>
    );
  }

  // --- CASE 3: INSIGHT LOADED ---
  const { 
    learning_type, 
    reason, 
    strength, 
    weakness, 
    motivation, 
    features, 
    recommendations,
    generated_at 
  } = insight;

  const badge = getLearningTypeDetails(learning_type);

  // Radar chart data normalization
  const radarData = features ? [
    {
      subject: 'Frekuensi Belajar',
      // data_min=1, data_max=50 (dari scaler.pkl)
      A: Math.min(100, Math.round((features.total_login - 1) / (50 - 1) * 100)),
      fullMark: 100
    },
    {
      subject: 'Durasi Belajar',
      // data_min=9, data_max=4889 (dari scaler.pkl)
      A: Math.min(100, Math.round((features.total_study_minutes - 9) / (4889 - 9) * 100)),
      fullMark: 100
    },
    {
      subject: 'Penyelesaian Materi',
      A: Math.round(features.completion_rate),
      fullMark: 100
    },
    {
      subject: 'Pemahaman Materi',
      A: Math.round(features.avg_quiz_score),
      fullMark: 100
    },
    {
      subject: 'Efisiensi Belajar',
      A: Math.min(100, Math.max(0, Math.round((1 - (features.avg_attempts_per_material - 1) / 2) * 100))),
      fullMark: 100
    }
  ] : [];

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20';
      case 'medium':
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';
      default:
        return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-700/50';
    }
  };


  const getResourceTag = (type) => {
    switch (type?.toLowerCase()) {
      case 'youtube': return 'YouTube Video';
      case 'article': return 'Artikel Bacaan';
      case 'tutorial': return 'Tutorial Praktis';
      default: return 'Materi Internal';
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header and Generate Button */}
      <div className="glass-card p-6 md:p-8 border-l-4 border-l-brand-500 overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 dark:bg-brand-550/5 rounded-full blur-3xl -mr-20 -mt-20"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <h3 className="text-2xl font-black flex items-center text-slate-800 dark:text-white">
              <BrainCircuit className="w-7 h-7 text-brand-500 mr-2.5 animate-pulse" />
              AI Insight & Gaya Belajar
            </h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm max-w-xl">
              Analisis gaya belajarmu yang dipetakan secara cerdas berdasarkan kebiasaan belajarmu di platform.
            </p>
          </div>
          
          <button 
            onClick={handleGenerate}
            disabled={generating}
            className="btn-primary py-2.5 px-5 text-xs flex items-center shrink-0 space-x-2"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Memperbarui...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Perbarui Analisis AI</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Hero Learning Type Visualization Card */}
      <div className={`glass-card p-5 md:p-6 border-t-4 border-t-brand-500 relative overflow-hidden bg-gradient-to-br ${badge.bg} rounded-2xl hover:shadow-md transition-all duration-300`}>
        <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/5 rounded-full blur-3xl -mr-24 -mt-24 pointer-events-none"></div>
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center gap-5">
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 shadow-md flex items-center justify-center shrink-0 w-16 h-16 border border-slate-100 dark:border-slate-800">
            {badge.icon}
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 block">
              Gaya Belajar Anda
            </span>
            <h2 className={`text-2xl md:text-3xl font-black tracking-tight leading-none text-transparent bg-clip-text bg-gradient-to-r ${badge.textGradient}`}>
              {badge.label}
            </h2>
            <p className="text-xs md:text-sm font-bold text-slate-750 dark:text-slate-200">
              {badge.statusText}
            </p>
            <p className="text-slate-450 dark:text-slate-500 text-[10px] md:text-xs italic font-semibold pt-0.5">
              {formatIndonesianDateTime(generated_at)}
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 text-rose-500 border border-rose-500/20 rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Main Analysis Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left: Radar Chart Component */}
        <div className="glass-card p-6 md:p-8 flex flex-col justify-between min-h-[420px]">
          <div>
            <h4 className="font-bold text-base flex items-center text-slate-800 dark:text-slate-100">
              <Award className="w-5 h-5 text-brand-500 mr-2" />
              Faktor Penentu Gaya Belajar
            </h4>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 leading-relaxed">
              Grafik radar di bawah memetakan performa belajarmu dalam skala 0-100% pada 5 variabel model clustering K-Means.
            </p>
          </div>

          <div className="w-full h-72 my-4 flex items-center justify-center">
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" radius="70%" data={radarData}>
                  <PolarGrid stroke="#475569" strokeDasharray="3 3" opacity={0.3} />
                  <PolarAngleAxis 
                    dataKey="subject" 
                    tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 600 }}
                  />
                  <PolarRadiusAxis 
                    angle={30} 
                    domain={[0, 100]} 
                    tick={{ fill: '#64748b', fontSize: 9 }}
                  />
                  <Radar
                    name="Profil Belajar"
                    dataKey="A"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.3}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-400 text-xs">Gagal merender data chart.</p>
            )}
          </div>

          <div className="p-3 bg-slate-50 dark:bg-slate-900/30 border border-slate-100 dark:border-slate-800/80 rounded-xl flex items-center space-x-3 text-slate-500 dark:text-slate-400">
            <AlertCircle className="w-5 h-5 text-brand-500 shrink-0" />
            <span className="text-[10px] leading-relaxed">
              Skala visual disesuaikan berdasarkan rasio performa aktual terhadap target ideal platform.
            </span>
          </div>
        </div>

        {/* Right: AI Insights Details */}
        <div className="space-y-6">
          
          {/* Why This Learning Type */}
          <div className="glass-card p-6 border-l-4 border-l-brand-500 space-y-3">
            <h5 className="text-xs font-extrabold text-brand-500 tracking-wider uppercase">Mengapa Tipe Belajar Ini?</h5>
            <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300 font-medium">
              {reason}
            </p>
          </div>

          {/* Strength & Weakness Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="p-5 bg-emerald-500/5 border border-emerald-500/15 rounded-2xl space-y-3">
              <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 font-bold text-xs uppercase tracking-wider">
                <Zap className="w-4.5 h-4.5" />
                <span>Kekuatan Belajarmu</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                {strength}
              </p>
            </div>

            {/* Weaknesses */}
            <div className="p-5 bg-amber-500/5 border border-amber-500/15 rounded-2xl space-y-3">
              <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 font-bold text-xs uppercase tracking-wider">
                <Target className="w-4.5 h-4.5" />
                <span>Area Perbaikan</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                {weakness}
              </p>
            </div>
          </div>

          {/* Motivation Quote Box */}
          <div className="p-6 bg-gradient-to-r from-brand-500/10 to-brand-500/20 rounded-2xl border border-brand-500/20 relative overflow-hidden flex flex-col justify-center min-h-[100px]">
            <div className="absolute top-1/2 left-4 -translate-y-1/2 opacity-10">
              <Sparkles className="w-16 h-16 text-brand-500" />
            </div>
            <span className="block text-[9px] font-bold text-brand-500 uppercase tracking-widest mb-1.5">MOTIVASI BELAJAR</span>
            <p className="text-xs italic text-slate-700 dark:text-slate-200 relative z-10 font-semibold leading-relaxed">
              "{motivation}"
            </p>
          </div>

        </div>
      </div>

      {/* Recommendations Section */}
      <section className="glass-card p-6 md:p-8 space-y-6">
        <div>
          <h3 className="font-bold text-base flex items-center text-slate-800 dark:text-slate-100">
            <Sparkles className="w-5 h-5 text-brand-500 mr-2" />
            Rekomendasi Materi Terarah
          </h3>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
            Berdasarkan kebiasaan belajarmu, AI merekomendasikan topik-topik berikut untuk dipelajari selanjutnya guna mengoptimalkan hasil pembelajaran.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations && recommendations.length === 0 ? (
            <div className="col-span-2 text-center py-8 text-slate-400 text-xs">
              Belum ada rekomendasi aktif saat ini.
            </div>
          ) : (
            recommendations.map((rec, i) => (
              <div 
                key={i} 
                className="p-5 bg-slate-50 dark:bg-slate-900/30 rounded-2xl border border-slate-100 dark:border-slate-800/80 flex flex-col justify-between space-y-4 hover:border-brand-500/30 transition-all duration-300 group"
              >
                <div className="space-y-2.5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-brand-500/10 text-brand-500">
                        {getResourceTag(rec.resource_type)}
                      </span>
                      <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100 leading-snug group-hover:text-brand-500 transition-colors duration-200">
                        {rec.title}
                      </h4>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-400 dark:text-slate-500 leading-relaxed">
                    {rec.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-semibold">
                  <span className="text-slate-500 dark:text-slate-400">Jalur: {rec.path_name}</span>
                  {rec.url ? (
                    <a 
                      href={rec.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-brand-500 hover:text-brand-600 dark:text-brand-400 flex items-center space-x-1"
                    >
                      <span>Buka Referensi</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <Link 
                      to="/learning" 
                      className="text-brand-500 hover:text-brand-600 dark:text-brand-400 flex items-center font-bold"
                    >
                      <span>Mulai Belajar</span>
                      <ChevronRight className="w-3.5 h-3.5 ml-0.5 group-hover:translate-x-0.5 transition-transform duration-200" />
                    </Link>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
};

export default Insight;
