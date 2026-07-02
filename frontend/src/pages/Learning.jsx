import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import { 
  BookOpen, 
  GraduationCap, 
  ChevronRight, 
  Play, 
  ArrowLeft, 
  Lock, 
  CheckCircle2, 
  ChevronLeft, 
  Award, 
  Sparkles, 
  Lightbulb, 
  Brain, 
  Timer, 
  RefreshCw, 
  XCircle, 
  AlertCircle, 
  Check, 
  Copy 
} from 'lucide-react';
import client from '../api/client';

// Static mappings to the dynamic JSON files in public directory
const MATERIAL_MAP = {
  "Machine Learning": {
    1: "/content/materi/materi path machine learning/bab 1/ml_bab1_dasar_ml_materi.json",
    2: "/content/materi/materi path machine learning/bab 2/ml_bab2_supervised_materi.json",
    3: "/content/materi/materi path machine learning/bab 3/ml_bab3_unsupervised_materi.json",
    4: "/content/materi/materi path machine learning/bab 4/ml_bab4_deeplearning_materi.json",
    5: "/content/materi/materi path machine learning/bab 5/ml_bab5_deployment_mlops_materi.json"
  },
  "Frontend Development": {
    1: "/content/materi/materi path front end/bab 1/FE_bab1_dasar_html_materi.json",
    2: "/content/materi/materi path front end/bab 2/FE_bab2_css_materi.json",
    3: "/content/materi/materi path front end/bab 3/FE_bab3_javascript_materi.json",
    4: "/content/materi/materi path front end/bab 4/FE_bab4_dom_event_materi.json",
    5: "/content/materi/materi path front end/bab 5/FE_bab5_react_materi.json"
  },
  "Backend Development": {
    1: "/content/materi/materi path backend/bab 1/backend_bab1_nodejs_materi.json",
    2: "/content/materi/materi path backend/bab 2/backend_bab2_express_materi.json",
    3: "/content/materi/materi path backend/bab 3/backend_bab3_sql_materi.json",
    4: "/content/materi/materi path backend/bab 4/backend_bab4_mongodb_materi.json",
    5: "/content/materi/materi path backend/bab 5/backend_bab5_auth_materi.json"
  }
};

const QUIZ_MAP = {
  "Machine Learning": {
    1: "/content/kuis/kuis machine learning/bab1_ml_kuis.json",
    2: "/content/kuis/kuis machine learning/bab2_ml_kuis.json",
    3: "/content/kuis/kuis machine learning/bab3_ml_kuis.json",
    4: "/content/kuis/kuis machine learning/bab4_ml_kuis.json",
    5: "/content/kuis/kuis machine learning/bab5_ml_kuis.json"
  },
  "Frontend Development": {
    1: "/content/kuis/kuis front end/bab1_dasar_html_kuis.json",
    2: "/content/kuis/kuis front end/bab2_css_kuis.json",
    3: "/content/kuis/kuis front end/bab3_javascript_kuis.json",
    4: "/content/kuis/kuis front end/bab4_dom_event_kuis.json",
    5: "/content/kuis/kuis front end/bab5_react_kuis.json"
  },
  "Backend Development": {
    1: "/content/kuis/kuis back end/backend_bab1_nodejs_kuis.json",
    2: "/content/kuis/kuis back end/backend_bab2_express_kuis.json",
    3: "/content/kuis/kuis back end/backend_bab3_sql_kuis.json",
    4: "/content/kuis/kuis back end/backend_bab4_mongodb_kuis.json",
    5: "/content/kuis/kuis back end/backend_bab5_auth_kuis.json"
  }
};

const getSlideKey = (username, materialId) => username ? `material_slide_${username}_${materialId}` : `material_slide_${materialId}`;

const Learning = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  // Navigation & View States
  const [paths, setPaths] = useState([]);
  const [activePath, setActivePath] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [activeMaterial, setActiveMaterial] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Study Slide States
  const [materialData, setMaterialData] = useState(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const startTimeRef = useRef(null);

  // Quiz States
  const [quizActive, setQuizActive] = useState(false);
  const [quizData, setQuizData] = useState(null); // API questions
  const [quizJSONData, setQuizJSONData] = useState(null); // Local explanations/referensi
  const [answers, setAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizSubmitting, setQuizSubmitting] = useState(false);
  const [activeQuizQuestion, setActiveQuizQuestion] = useState(0);

  // Copy code feedback state
  const [copiedIndex, setCopiedIndex] = useState(null);

  // Load available paths with stats
  const fetchPaths = async () => {
    try {
      setLoading(true);
      const res = await client.get('/api/learning/paths');
      setPaths(res.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Gagal memuat jalur pembelajaran. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPaths();
  }, []);

  // Handle URL params for resume bookmarking
  useEffect(() => {
    const initFromParams = async () => {
      const pathIdParam = searchParams.get('pathId');
      const materialIdParam = searchParams.get('materialId');
      
      if (paths.length > 0 && pathIdParam) {
        const selectedPath = paths.find(p => p.id === parseInt(pathIdParam, 10));
        if (selectedPath) {
          setActivePath(selectedPath);
          try {
            setLoading(true);
            const res = await client.get(`/api/learning/paths/${selectedPath.id}/materials`);
            const loadedMaterials = res.data;
            setMaterials(loadedMaterials);
            setError('');
            
            if (materialIdParam) {
              const selectedMat = loadedMaterials.find(m => m.id === parseInt(materialIdParam, 10));
              if (selectedMat && selectedMat.is_unlocked) {
                setActiveMaterial(selectedMat);
                setError('');
                try {
                  await client.post(`/api/learning/materials/${selectedMat.id}/start`);
                  startTimeRef.current = Date.now();
                  const jsonPath = MATERIAL_MAP[selectedPath.name]?.[selectedMat.order];
                  if (jsonPath) {
                    const jsonRes = await fetch(jsonPath);
                    if (jsonRes.ok) {
                      const data = await jsonRes.json();
                      setMaterialData(data);
                      const savedIndex = localStorage.getItem(getSlideKey(user?.username, selectedMat.id));
                      setCurrentSlideIndex(savedIndex ? parseInt(savedIndex, 10) : 0);
                      
                      setQuizActive(false);
                      setQuizData(null);
                      setQuizJSONData(null);
                      setAnswers({});
                      setQuizResult(null);
                      setQuizSubmitted(false);
                      setActiveQuizQuestion(0);
                    }
                  }
                } catch (e) {
                  console.error(e);
                }
              }
            }
          } catch (err) {
            console.error(err);
          } finally {
            setLoading(false);
          }
        }
      }
    };
    
    initFromParams();
  }, [paths, searchParams]);

  // Save learning path resume bookmark
  useEffect(() => {
    if (activePath && activeMaterial && user?.username) {
      localStorage.setItem(`continue_learning_${user.username}`, JSON.stringify({
        pathId: activePath.id,
        pathName: activePath.name,
        materialId: activeMaterial.id,
        materialTitle: activeMaterial.title,
        chapterName: `Bab ${activeMaterial.order}: ${activeMaterial.title}`,
        slideIndex: currentSlideIndex
      }));
    }
  }, [activePath, activeMaterial, currentSlideIndex, user]);

  // Fetch materials for a selected path
  const handleSelectPath = async (path) => {
    setActivePath(path);
    try {
      setLoading(true);
      const res = await client.get(`/api/learning/paths/${path.id}/materials`);
      setMaterials(res.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Gagal memuat daftar materi.');
    } finally {
      setLoading(false);
    }
  };

  // Start learning session for a material
  const handleStartMaterial = async (material, showQuizImmediately = false) => {
    const skipToQuiz = showQuizImmediately === true;
    setActiveMaterial(material);
    setLoading(true);
    setError('');

    try {
      // 1. Log session start in backend
      await client.post(`/api/learning/materials/${material.id}/start`);
      startTimeRef.current = Date.now();

      // 2. Fetch slide data from local JSON
      const jsonPath = MATERIAL_MAP[activePath.name]?.[material.order];
      if (!jsonPath) {
        throw new Error('Materi JSON tidak terpetakan');
      }

      const res = await fetch(jsonPath);
      if (!res.ok) {
        throw new Error('Gagal membaca file konten materi');
      }
      const data = await res.json();
      setMaterialData(data);

      // Restore last slide index or start at 0
      const savedIndex = localStorage.getItem(getSlideKey(user?.username, material.id));
      setCurrentSlideIndex(savedIndex ? parseInt(savedIndex, 10) : 0);

      // Reset states
      setQuizActive(false);
      setQuizData(null);
      setQuizJSONData(null);
      setAnswers({});
      setQuizResult(null);
      setQuizSubmitted(false);
      setActiveQuizQuestion(0);

      if (skipToQuiz) {
        // Load questions from API (shuffled database questions)
        const apiRes = await client.get(`/api/learning/materials/${material.id}/quiz`);
        setQuizData(apiRes.data);

        // Load metadata & explanations from local JSON
        const quizJsonPath = QUIZ_MAP[activePath.name]?.[material.order];
        if (quizJsonPath) {
          const jsonRes = await fetch(quizJsonPath);
          if (jsonRes.ok) {
            const jsonData = await jsonRes.json();
            setQuizJSONData(jsonData);
          }
        }

        setQuizActive(true);
        setActiveQuizQuestion(0);
        setAnswers({});

        const isExhausted = material.attempts_count >= 3;
        const isPassed = material.best_score >= 70;

        if (material.attempts_count > 0) {
          setQuizSubmitted(true);
          setQuizResult({
            score: material.best_score || material.last_score || 0,
            correct_answers: Math.round(((material.best_score || material.last_score || 0) / 100) * 10),
            total_questions: 10,
            attempt_number: material.attempts_count,
            attempts_remaining: Math.max(0, 3 - material.attempts_count),
            passed: isPassed
          });
        } else {
          setQuizSubmitted(false);
          setQuizResult(null);
        }
      }

    } catch (err) {
      console.error(err);
      setError('Gagal memuat materi. Pastikan file konten tersedia.');
      setActiveMaterial(null);
    } finally {
      setLoading(false);
    }
  };

  // Auto save slide index
  const handleSetSlide = (idx) => {
    setCurrentSlideIndex(idx);
    if (activeMaterial) {
      localStorage.setItem(getSlideKey(user?.username, activeMaterial.id), idx.toString());
    }
  };

  // Start the quiz at the end of the slide decks
  const handleStartQuiz = async (isRetake = false) => {
    const forceRetake = isRetake === true;
    setLoading(true);
    setError('');
    try {
      // 1. Load questions from API (shuffled database questions)
      const apiRes = await client.get(`/api/learning/materials/${activeMaterial.id}/quiz`);
      setQuizData(apiRes.data);

      // 2. Load metadata & explanations from local JSON
      const jsonPath = QUIZ_MAP[activePath.name]?.[activeMaterial.order];
      if (jsonPath) {
        const jsonRes = await fetch(jsonPath);
        if (jsonRes.ok) {
          const jsonData = await jsonRes.json();
          setQuizJSONData(jsonData);
        }
      }

      setQuizActive(true);
      setActiveQuizQuestion(0);
      setAnswers({});

      const isExhausted = activeMaterial.attempts_count >= 3;
      const isPassed = activeMaterial.best_score >= 70;

      if (!forceRetake && (isExhausted || isPassed)) {
        setQuizSubmitted(true);
        setQuizResult({
          score: activeMaterial.best_score || activeMaterial.last_score || 0,
          correct_answers: Math.round(((activeMaterial.best_score || activeMaterial.last_score || 0) / 100) * 10),
          total_questions: 10,
          attempt_number: activeMaterial.attempts_count,
          attempts_remaining: Math.max(0, 3 - activeMaterial.attempts_count),
          passed: isPassed
        });
      } else {
        setQuizSubmitted(false);
        setQuizResult(null);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Gagal memuat kuis.');
    } finally {
      setLoading(false);
    }
  };

  // Select option in quiz
  const handleSelectOption = (questionId, optionKey) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionKey
    }));
  };

  // Submit quiz answers to backend
  const handleSubmitQuiz = async () => {
    // Validate that all questions are answered
    const unanswered = quizData.questions.some(q => !answers[q.id]);
    if (unanswered) {
      alert('Silakan jawab semua soal terlebih dahulu.');
      return;
    }

    setQuizSubmitting(true);
    try {
      const formattedAnswers = Object.entries(answers).map(([qId, ans]) => ({
        question_id: parseInt(qId, 10),
        answer: ans.toLowerCase()
      }));

      const res = await client.post(`/api/learning/quiz/${quizData.quiz_id}/submit`, {
        answers: formattedAnswers
      });

      setQuizResult(res.data);
      setQuizSubmitted(true);

      // Refresh list of materials to update scores, unlocks, and attempts_count in parent state
      try {
        const pathRes = await client.get(`/api/learning/paths/${activePath.id}/materials`);
        setMaterials(pathRes.data);
        const updatedMat = pathRes.data.find(m => m.id === activeMaterial.id);
        if (updatedMat) {
          setActiveMaterial(updatedMat);
        }
      } catch (refreshErr) {
        console.error('Gagal memperbarui data materi setelah kuis:', refreshErr);
      }
    } catch (err) {
      console.error(err);
      alert('Gagal mengirim jawaban kuis.');
    } finally {
      setQuizSubmitting(false);
    }
  };

  // Mark material complete and save duration
  const handleCompleteMaterial = async () => {
    setLoading(true);
    try {
      const duration = startTimeRef.current 
        ? Math.round((Date.now() - startTimeRef.current) / 1000) 
        : 60;

      await client.post(`/api/learning/materials/${activeMaterial.id}/complete`, {
        time_spent_seconds: duration
      });

      // Clear stored slide
      localStorage.removeItem(getSlideKey(user?.username, activeMaterial.id));
      if (user?.username) {
        localStorage.removeItem(`continue_learning_${user.username}`);
      }

      // Refresh data and exit material view
      const pathRes = await client.get(`/api/learning/paths/${activePath.id}/materials`);
      setMaterials(pathRes.data);

      setActiveMaterial(null);
      setMaterialData(null);
      setQuizActive(false);
      setQuizData(null);
      setQuizJSONData(null);
    } catch (err) {
      console.error(err);
      alert('Gagal menyimpan progres pembelajaran.');
    } finally {
      setLoading(false);
    }
  };

  // Back navigation handler
  const handleGoBack = () => {
    if (quizActive) {
      if (quizSubmitted) {
        // No need to warn if the quiz has already been submitted
        setQuizActive(false);
        setQuizData(null);
        setQuizJSONData(null);
        // Refresh materials list
        handleSelectPath(activePath);
      } else {
        // Prompt user warning
        if (window.confirm('Keluar dari kuis akan membatalkan pengerjaan saat ini. Anda yakin?')) {
          setQuizActive(false);
          setQuizData(null);
          setQuizJSONData(null);
        }
      }
    } else if (activeMaterial) {
      setActiveMaterial(null);
      setMaterialData(null);
      // Refresh path's materials list to get up to date completed states
      handleSelectPath(activePath);
    } else if (activePath) {
      setActivePath(null);
      setMaterials([]);
      fetchPaths();
    }
  };

  // Helper for rendering custom slide content types
  const renderSlideContent = (block, idx) => {
    switch (block.tipe) {
      case 'paragraf':
        return (
          <div key={idx} className="space-y-3">
            {block.judul && (
              <h4 className="text-lg font-bold text-slate-800 dark:text-slate-200 mt-4 first:mt-0">
                {block.judul}
              </h4>
            )}
            <p className="text-base text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {block.isi}
            </p>
          </div>
        );

      case 'gambar':
        const imageSrc = block.src.startsWith('/assets') ? `/content${block.src}` : block.src;
        return (
          <div key={idx} className="my-6 flex flex-col items-center">
            {block.judul && (
              <h5 className="text-sm font-semibold text-slate-700 dark:text-slate-300 self-start mb-2">
                {block.judul}
              </h5>
            )}
            <div className="border border-slate-200/60 dark:border-slate-800/80 rounded-2xl p-1.5 bg-slate-50 dark:bg-slate-900/50 shadow-md max-w-full">
              <img 
                src={imageSrc} 
                alt={block.alt || block.judul} 
                className="max-h-80 object-contain rounded-xl mx-auto"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&w=800&q=80';
                }}
              />
            </div>
            {block.deskripsi_gambar && (
              <p className="text-[11px] text-slate-400 dark:text-slate-500 italic mt-2 text-center max-w-xl">
                {block.deskripsi_gambar}
              </p>
            )}
          </div>
        );

      case 'analogi':
        return (
          <div key={idx} className="p-5 rounded-2xl bg-amber-500/10 dark:bg-amber-500/5 border border-amber-500/15 text-slate-700 dark:text-slate-300 my-5 relative overflow-hidden">
            <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 mb-2">
              <Lightbulb className="w-5 h-5 animate-pulse shrink-0" />
              <span className="text-xs font-bold uppercase tracking-wider">{block.judul || 'Analogi'}</span>
            </div>
            <p className="text-sm leading-relaxed italic whitespace-pre-line relative z-10">{block.isi}</p>
          </div>
        );

      case 'refleksi':
        return (
          <div key={idx} className="p-5 rounded-2xl bg-brand-500/10 dark:bg-brand-500/5 border border-brand-500/15 text-slate-700 dark:text-slate-300 my-5">
            <div className="flex items-center space-x-2 text-brand-650 dark:text-brand-400 mb-2">
              <Brain className="w-5 h-5 shrink-0 text-brand-500" />
              <span className="text-xs font-bold uppercase tracking-wider">{block.judul || 'Refleksi'}</span>
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-line">{block.isi}</p>
          </div>
        );

      case 'fun_fact':
        return (
          <div key={idx} className="p-5 rounded-2xl bg-emerald-500/10 dark:bg-emerald-500/5 border border-emerald-500/15 text-slate-700 dark:text-slate-300 my-5">
            <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 mb-2">
              <Sparkles className="w-5 h-5 shrink-0" />
              <span className="text-xs font-bold uppercase tracking-wider">{block.judul || 'Fun Fact'}</span>
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-line">{block.isi}</p>
          </div>
        );

      case 'kode':
        const isCopied = copiedIndex === idx;
        return (
          <div key={idx} className="my-5 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800/80 bg-slate-950 text-slate-200 shadow-lg">
            <div className="px-4 py-2 bg-slate-900 border-b border-slate-800/80 flex justify-between items-center text-[10px] text-slate-400 font-mono">
              <span className="uppercase">{block.bahasa || 'code'}</span>
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(block.kode);
                  setCopiedIndex(idx);
                  setTimeout(() => setCopiedIndex(null), 2000);
                }}
                className="hover:text-white transition-colors duration-150 flex items-center space-x-1"
              >
                {isCopied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                <span>{isCopied ? 'Tersalin' : 'Salin'}</span>
              </button>
            </div>
            <pre className="p-4 overflow-x-auto text-[11px] font-mono leading-relaxed bg-[#060913]">
              <code>{block.kode}</code>
            </pre>
            {block.penjelasan && (
              <div className="px-4 py-3 bg-[#0d1322] border-t border-slate-850 text-xs text-slate-400">
                <p className="font-semibold text-slate-300 mb-1">Penjelasan Kode:</p>
                <p className="leading-relaxed whitespace-pre-line">{block.penjelasan}</p>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  // ─────────────────────────────────────────────────────────────
  // ─── RENDER VIEW 1: PATH SELECTION
  // ─────────────────────────────────────────────────────────────
  if (!activePath) {
    return (
      <div className="space-y-8 pb-12">
        <div className="glass-card p-6 border-l-4 border-l-brand-500 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 dark:bg-brand-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
          <div className="relative z-10 flex items-center space-x-3.5">
            <GraduationCap className="w-6 h-6 text-brand-500 shrink-0" />
            <p className="text-slate-700 dark:text-slate-200 text-sm font-semibold leading-relaxed">
              Pilih salah satu jalur di bawah ini untuk memulai kurikulum belajarmu secara personal.
            </p>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center space-x-2 text-xs">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 bg-slate-200 dark:bg-slate-800/40 rounded-2xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {paths.map((path) => {
              const percent = path.total_materials > 0 
                ? Math.round((path.completed_materials / path.total_materials) * 100) 
                : 0;

              // Assign custom colors per path index
              const colorClasses = [
                { bg: 'bg-brand-500', text: 'text-brand-500', lightBg: 'bg-brand-500/10 border-brand-500/20' },
                { bg: 'bg-sky-500', text: 'text-sky-500', lightBg: 'bg-sky-500/10 border-sky-500/20' },
                { bg: 'bg-emerald-500', text: 'text-emerald-500', lightBg: 'bg-emerald-500/10 border-emerald-500/20' }
              ][(path.order - 1) % 3];

              return (
                <div 
                  key={path.id} 
                  className="glass-card p-6 flex flex-col justify-between interactive-item relative group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold border ${colorClasses.lightBg} ${colorClasses.text}`}>
                        Path {path.order}
                      </span>
                      <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                        {path.total_materials} Bab
                      </span>
                    </div>
                    
                    <h4 className="font-bold text-base tracking-tight text-slate-800 dark:text-slate-100 group-hover:text-brand-500 transition-colors duration-250">
                      {path.name}
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      {path.description || 'Pelajari konsep dasar secara bertahap dengan bimbingan kurikulum cerdas.'}
                    </p>
                  </div>
                  
                  <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800/60 space-y-3">
                    <div className="flex justify-between items-center text-[10px] font-bold text-slate-400">
                      <span>Progres Jalur</span>
                      <span className={colorClasses.text}>{percent}%</span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-500 ${colorClasses.bg}`} 
                        style={{ width: `${percent}%` }}
                      ></div>
                    </div>
                    
                    <button 
                      onClick={() => handleSelectPath(path)}
                      className={`w-full mt-2 py-2.5 ${colorClasses.bg} text-white hover:opacity-95 rounded-xl text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5`}
                    >
                      <Play className="w-3.5 h-3.5 shrink-0 fill-white" />
                      <span>{percent > 0 ? 'Lanjutkan Belajar' : 'Mulai Jalur'}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────
  // ─── RENDER VIEW 2: MATERIALS LIST
  // ─────────────────────────────────────────────────────────────
  if (activePath && !activeMaterial) {
    return (
      <div className="space-y-6 pb-12">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
          <button onClick={handleGoBack} className="hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            Jalur Belajar
          </button>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-slate-800 dark:text-slate-200">{activePath.name}</span>
        </div>

        {/* Path Header */}
        <div className="glass-card p-6 flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-l-4 border-l-brand-500">
          <div className="space-y-1">
            <h3 className="text-lg font-bold tracking-tight">{activePath.name}</h3>
            <p className="text-slate-500 dark:text-slate-400 text-xs max-w-xl leading-relaxed">
              Materi disusun berurutan. Bab berikutnya akan terbuka secara otomatis setelah Anda menyelesaikan materi saat ini.
            </p>
          </div>
          <button 
            onClick={handleGoBack}
            className="px-4 py-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shrink-0 transition-all duration-200 active:scale-98"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Kembali</span>
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center space-x-2 text-xs">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800/40 rounded-2xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {materials.map((material, idx) => {
              const isLocked = !material.is_unlocked;
              const isCompleted = material.is_completed;

              return (
                <div 
                  key={material.id} 
                  onClick={() => {
                    if (!isLocked) {
                      handleStartMaterial(material);
                    }
                  }}
                  className={`
                    glass-card p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all duration-200 cursor-pointer
                    ${isLocked ? 'opacity-60 border-dashed bg-slate-100/30 dark:bg-slate-900/10 cursor-not-allowed' : 'hover:border-slate-350 dark:hover:border-slate-700/80 hover:shadow-md'}
                  `}
                >
                  <div className="flex items-start space-x-4 min-w-0">
                    <div className={`
                      w-10 h-10 rounded-xl flex items-center justify-center border shrink-0
                      ${isLocked 
                        ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 border-slate-200 dark:border-slate-700' 
                        : isCompleted
                          ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                          : 'bg-brand-500/10 text-brand-500 border-brand-500/20'}
                    `}>
                      {isLocked ? (
                        <Lock className="w-4.5 h-4.5" />
                      ) : isCompleted ? (
                        <CheckCircle2 className="w-5 h-5 fill-emerald-500/5" />
                      ) : (
                        <span className="text-sm font-bold">{idx + 1}</span>
                      )}
                    </div>

                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center space-x-2.5">
                        <span className="text-slate-400 dark:text-slate-500 font-bold text-[10px] tracking-wide uppercase">
                          Bab {material.order}
                        </span>
                        {isCompleted && (
                          <span className="px-2 py-0.5 rounded-full text-[8px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/10">
                            Selesai
                          </span>
                        )}
                      </div>
                      <h4 className="font-bold text-sm tracking-tight truncate dark:text-slate-200">
                        {material.title}
                      </h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-1">
                        {material.description || 'Pelajari materi lengkap dari bab kurikulum adaptif ini.'}
                      </p>

                      {material.has_quiz && (
                        <div className="flex flex-wrap items-center gap-2 pt-2 text-[10px] font-semibold text-slate-500 dark:text-slate-400">
                          {material.attempts_count > 0 ? (
                            <>
                              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/15">
                                Skor Terakhir: <strong className="font-extrabold">{material.last_score}%</strong>
                              </span>
                              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/15">
                                Skor Terbaik: <strong className="font-extrabold">{material.best_score}%</strong>
                              </span>
                              <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-650 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                Percobaan: <strong className="font-extrabold">{material.attempts_count}x</strong>
                              </span>
                            </>
                          ) : (
                            <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-850 text-slate-450 italic border border-slate-200/50 dark:border-slate-800/80">
                              Kuis belum dikerjakan
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto shrink-0 self-end sm:self-center">
                    {isLocked ? (
                      <span className="text-[10px] font-bold text-slate-400/80 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg flex items-center space-x-1 w-full sm:w-auto justify-center">
                        <Lock className="w-3 h-3" />
                        <span>Materi Terkunci</span>
                      </span>
                    ) : (
                      <>
                        {material.has_quiz && material.attempts_count > 0 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStartMaterial(material, true);
                            }}
                            className="w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-bold bg-blue-500/10 hover:bg-blue-500/20 text-blue-600 dark:text-blue-400 border border-blue-500/20 active:scale-98 transition-all duration-200 text-center"
                          >
                            Lihat Hasil & Pembahasan
                          </button>
                        )}
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStartMaterial(material);
                          }}
                          className={`
                            w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-bold transition-all duration-200 active:scale-98
                            ${isCompleted 
                              ? 'bg-slate-100 hover:bg-slate-200 text-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700/85 dark:text-slate-200 border border-slate-250 dark:border-slate-700' 
                              : 'bg-brand-500 hover:bg-brand-600 text-white shadow-sm shadow-brand-500/20'}
                          `}
                        >
                          {isCompleted ? 'Pelajari Ulang' : 'Mulai Belajar'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────
  // ─── RENDER VIEW 3: SLIDE-BASED LEARNING
  // ─────────────────────────────────────────────────────────────
  if (activeMaterial && materialData && !quizActive) {
    const subBabList = materialData.sub_bab || [];
    const currentSubBab = subBabList[currentSlideIndex];
    const totalSlides = subBabList.length;
    const progressPercent = totalSlides > 0 ? Math.round(((currentSlideIndex + 1) / totalSlides) * 100) : 0;
    const isLastSlide = currentSlideIndex === totalSlides - 1;

    return (
      <div className="space-y-6 pb-12">
        {/* Top Sticky Header */}
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
          <div className="flex items-center space-x-2">
            <button onClick={handleGoBack} className="hover:text-slate-600 dark:hover:text-slate-200">
              Materi
            </button>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="text-slate-800 dark:text-slate-200 line-clamp-1 max-w-xs">{activeMaterial.title}</span>
          </div>
          <button 
            onClick={handleGoBack}
            className="flex items-center space-x-1.5 text-rose-500 hover:text-rose-600"
          >
            <span>Tutup Materi</span>
          </button>
        </div>

        {/* Global Progress Indicators */}
        <div className="space-y-2.5">
          <div className="flex justify-between items-center text-[10px] font-bold text-slate-400">
            <span className="uppercase tracking-wider">Slide {currentSlideIndex + 1} dari {totalSlides}</span>
            <span>{progressPercent}% Dibaca</span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800/60 rounded-full h-1 overflow-hidden">
            <div 
              className="bg-brand-500 h-full rounded-full transition-all duration-350" 
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>

        {/* Main Slide Card */}
        <div className="glass-card flex flex-col justify-between relative overflow-hidden border-t-4 border-t-brand-500 w-full">
          {/* Top glowing glow */}
          <div className="absolute top-0 right-0 w-48 h-48 bg-brand-500/5 rounded-full blur-3xl pointer-events-none"></div>

          <div className="flex-1 flex flex-col">
            {/* Sub-Bab Header */}
            {currentSubBab && (
              <div className="p-8 lg:p-10 pb-5 border-b border-slate-100 dark:border-slate-800/80 space-y-2">
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-brand-500/10 text-brand-500 border border-brand-500/20">
                  Subbab {currentSubBab.id}
                </span>
                <h3 className="text-xl md:text-2xl font-bold tracking-tight text-slate-800 dark:text-slate-100 mt-1">
                  {currentSubBab.judul}
                </h3>
              </div>
            )}

            {/* Sub-Bab Content Blocks */}
            <div className="p-8 lg:p-10 pt-5 space-y-6">
              {currentSubBab ? (
                currentSubBab.konten.map((block, idx) => renderSlideContent(block, idx))
              ) : (
                <div className="text-center text-slate-400 py-12">
                  Tidak ada konten yang tersedia untuk slide ini.
                </div>
              )}
            </div>
          </div>

          {/* Slide Navigation Footer */}
          <div className="p-6 lg:p-8 bg-slate-50/50 dark:bg-slate-900/35 border-t border-slate-100 dark:border-slate-800/70 flex items-center justify-between gap-4">
            <button
              onClick={() => handleSetSlide(Math.max(0, currentSlideIndex - 1))}
              disabled={currentSlideIndex === 0}
              className={`
                px-4 py-2 border rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all duration-150 active:scale-98
                ${currentSlideIndex === 0 
                  ? 'text-slate-300 dark:text-slate-600 border-slate-100 dark:border-slate-800 cursor-not-allowed' 
                  : 'text-slate-700 hover:bg-slate-100 border-slate-200 dark:text-slate-300 dark:border-slate-800 dark:hover:bg-slate-800/70'}
              `}
            >
              <ChevronLeft className="w-4.5 h-4.5" />
              <span>Sebelumnya</span>
            </button>

            {isLastSlide ? (
              <button
                onClick={handleStartQuiz}
                className="px-5 py-2.5 bg-gradient-to-r from-brand-500 to-blue-600 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-brand-500/20 hover:opacity-95 active:scale-98 transition-all duration-200 animate-pulse-subtle"
              >
                <GraduationCap className="w-4.5 h-4.5 fill-white" />
                <span>
                  {activeMaterial && (activeMaterial.best_score >= 70 || activeMaterial.attempts_count >= 3)
                    ? "Lihat Hasil & Pembahasan Kuis"
                    : "Mulai Kuis Bab"}
                </span>
              </button>
            ) : (
              <button
                onClick={() => handleSetSlide(Math.min(totalSlides - 1, currentSlideIndex + 1))}
                className="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm shadow-brand-500/15 active:scale-98 transition-all duration-150"
              >
                <span>Lanjut</span>
                <ChevronRight className="w-4.5 h-4.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────
  // ─── RENDER VIEW 4: QUIZ INTERACTIVE VIEW
  // ─────────────────────────────────────────────────────────────
  if (activeMaterial && quizActive && quizData) {
    const questions = quizData.questions || [];
    const activeQuestion = questions[activeQuestionIndex => activeQuizQuestion]; // safety binding
    const currentQuestion = questions[activeQuizQuestion];
    const totalQuestions = questions.length;

    return (
      <div className="space-y-6 pb-12">
        {/* Quiz Header Breadcrumb */}
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
          <div className="flex items-center space-x-2">
            <span>Kuis</span>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="text-slate-800 dark:text-slate-200">{quizData.title}</span>
          </div>
          <button 
            onClick={handleGoBack}
            className="flex items-center space-x-1 text-rose-500 hover:text-rose-600"
          >
            <span>Batalkan Kuis</span>
          </button>
        </div>

        {/* ─── CASE A: QUIZ COMPLETED (SHOW SCORE & REVIEW) ─── */}
        {quizSubmitted && quizResult ? (
          <div className="space-y-6">
            {/* Result Summary Card */}
            <div className="glass-card p-6 lg:p-8 text-center relative overflow-hidden border-t-4 border-t-brand-500">
              <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/5 rounded-full blur-3xl"></div>
              
              <div className="max-w-xl mx-auto space-y-5 relative z-10">
                <div className="w-16 h-16 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-500 flex items-center justify-center mx-auto shadow-sm">
                  <Award className="w-8 h-8" />
                </div>
                
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Skor Kuis Anda</span>
                  <h2 className="text-4xl font-extrabold text-slate-800 dark:text-white tracking-tight">
                    {quizResult.score} / 100
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Benar {quizResult.correct_answers} dari {quizResult.total_questions} soal
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/35 border border-slate-100 dark:border-slate-800 text-left space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-bold">
                    {quizResult.score >= 70 ? (
                      <>
                        <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                        <span className="text-emerald-600 dark:text-emerald-400">Selamat! Anda Lulus Evaluasi Bab ini.</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-5 h-5 text-rose-500 shrink-0" />
                        <span className="text-rose-600 dark:text-rose-400">Anda berada di bawah skor target kelulusan (70). Silakan coba lagi untuk meningkatkan nilai Anda.</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row justify-center items-center gap-3 pt-3">
                  {quizResult.attempts_remaining > 0 && (
                    <button
                      onClick={() => handleStartQuiz(true)}
                      className="w-full sm:w-auto px-5 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800/80 dark:hover:bg-slate-700/80 text-slate-800 dark:text-slate-200 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition-all duration-150 active:scale-98 border border-slate-250 dark:border-slate-750"
                    >
                      <RefreshCw className="w-4 h-4 shrink-0" />
                      <span>Ulang Kuis (Tersisa {quizResult.attempts_remaining} Kali)</span>
                    </button>
                  )}

                  <button
                    onClick={handleCompleteMaterial}
                    className="w-full sm:w-auto px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 shadow-md shadow-brand-500/20 transition-all duration-150 active:scale-98"
                  >
                    <span>Selesaikan Materi & Lanjutkan</span>
                    <ChevronRight className="w-4.5 h-4.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Answer Explanations & Review Panel (Shown on attempt >= 3 or score === 100 or best score is 100) */}
            {quizResult && (quizResult.attempt_number >= 3 || quizResult.score === 100 || (activeMaterial && activeMaterial.best_score === 100)) ? (
              <div className="glass-card p-6 lg:p-8 space-y-6">
                <h3 className="font-bold text-base border-b border-slate-100 dark:border-slate-800/80 pb-3">
                  Pembahasan & Review Soal
                </h3>

                <div className="space-y-8">
                  {questions.map((q, idx) => {
                    const userAnswer = answers[q.id];
                    // API option mapping to correct JSON option
                    const jsonQuestion = quizJSONData?.soal?.find(jq => jq.pertanyaan.trim() === q.question_text.trim());
                    const correctAnsKey = jsonQuestion?.jawaban || 'A';
                    
                    const isCorrect = userAnswer && userAnswer.toUpperCase() === correctAnsKey.toUpperCase();

                    return (
                      <div key={q.id} className="space-y-3 p-4 bg-slate-50/50 dark:bg-slate-900/30 border border-slate-150 dark:border-slate-800/80 rounded-2xl">
                        <div className="flex items-center space-x-2">
                          <span className="text-slate-400 font-extrabold text-xs">Soal {idx + 1}</span>
                          {userAnswer ? (
                            <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${isCorrect ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/10' : 'bg-rose-500/10 text-rose-600 border border-rose-500/10'}`}>
                              {isCorrect ? 'Benar' : 'Salah'}
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-blue-500/10 text-blue-600 border border-blue-500/10">
                              Kunci Jawaban
                            </span>
                          )}
                        </div>
                        
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
                          {q.question_text}
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                          {[
                            { key: 'A', text: q.option_a },
                            { key: 'B', text: q.option_b },
                            { key: 'C', text: q.option_c },
                            { key: 'D', text: q.option_d }
                          ].map((opt) => {
                            const isUserSelected = userAnswer && userAnswer.toUpperCase() === opt.key;
                            const isCorrectOption = correctAnsKey.toUpperCase() === opt.key;

                            return (
                              <div
                                key={opt.key}
                                className={`
                                  p-3 rounded-xl border text-xs leading-normal flex items-start space-x-2.5
                                  ${isCorrectOption 
                                    ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/25'
                                    : isUserSelected
                                      ? 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/25'
                                      : 'bg-slate-50/50 dark:bg-slate-900/30 text-slate-550 dark:text-slate-400 border-slate-150 dark:border-slate-800'}
                                `}
                              >
                                <span className="font-extrabold shrink-0">{opt.key}.</span>
                                <span className="font-medium">{opt.text}</span>
                              </div>
                            );
                          })}
                        </div>

                        {jsonQuestion && jsonQuestion.penjelasan && (
                          <div className="p-3.5 bg-brand-500/5 rounded-xl border border-brand-500/10 text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mt-3">
                            <p className="font-bold text-slate-700 dark:text-slate-350 mb-1">Pembahasan:</p>
                            <p>{jsonQuestion.penjelasan}</p>
                            {jsonQuestion.sub_bab_referensi && (
                              <p className="text-[10px] text-slate-400 mt-2 font-semibold">
                                Referensi Sub-Bab: {jsonQuestion.sub_bab_referensi}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="glass-card p-6 lg:p-8 space-y-4 border-l-4 border-l-amber-500 text-left">
                <div className="flex items-start space-x-3 text-amber-600 dark:text-amber-400">
                  <Lock className="w-5 h-5 mt-0.5 shrink-0" />
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider">Pembahasan Kuis Terkunci</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                      Pembahasan kuis akan terbuka setelah Anda menyelesaikan 3 kali percobaan kuis atau berhasil mendapatkan skor 100.
                    </p>
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-2 font-bold">
                      Percobaan Anda saat ini: {quizResult ? quizResult.attempt_number : 0} / 3.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* ─── CASE B: QUIZ IN-PROGRESS (WIZARD QUESTION CARDS) ─── */
          <div className="glass-card flex flex-col justify-between min-h-[420px] border-t-4 border-t-brand-500">
            {currentQuestion ? (
              <div className="p-6 lg:p-8 space-y-6 flex-1">
                {/* Quiz Progress Counter */}
                <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 border-b border-slate-100 dark:border-slate-800/80 pb-3">
                  <span className="uppercase tracking-wider">Soal {activeQuizQuestion + 1} dari {totalQuestions}</span>
                  <span className="text-brand-500">KUIS EVALUASI PEMAHAMAN</span>
                </div>

                {/* Question Area */}
                <div className="space-y-4">
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
                    {currentQuestion.question_text}
                  </p>

                  {/* Options List */}
                  <div className="grid grid-cols-1 gap-3 pt-3">
                    {[
                      { key: 'A', text: currentQuestion.option_a },
                      { key: 'B', text: currentQuestion.option_b },
                      { key: 'C', text: currentQuestion.option_c },
                      { key: 'D', text: currentQuestion.option_d }
                    ].map((opt) => {
                      const isSelected = answers[currentQuestion.id] === opt.key;
                      
                      return (
                        <button
                          key={opt.key}
                          onClick={() => handleSelectOption(currentQuestion.id, opt.key)}
                          className={`
                            w-full p-4 rounded-xl border text-left text-xs leading-normal flex items-start space-x-3 transition-all duration-150 hover:-translate-y-0.5 active:translate-y-0 hover:shadow-sm
                            ${isSelected 
                              ? 'bg-brand-500/10 border-brand-500/30 text-brand-650 dark:text-brand-400 font-bold' 
                              : 'bg-slate-50/50 hover:bg-slate-100 dark:bg-slate-900/30 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400 border-slate-150 dark:border-slate-800'}
                          `}
                        >
                          <div className={`
                            w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold border shrink-0
                            ${isSelected 
                              ? 'bg-brand-500 border-brand-500 text-white' 
                              : 'bg-white dark:bg-slate-800 text-slate-400 border-slate-200 dark:border-slate-700'}
                          `}>
                            {opt.key}
                          </div>
                          <span className="font-semibold">{opt.text}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400 flex-1 flex items-center justify-center">
                Mengevaluasi data soal kuis...
              </div>
            )}

            {/* Quiz Navigation Buttons */}
            <div className="p-4 lg:p-6 bg-slate-50/50 dark:bg-slate-900/35 border-t border-slate-100 dark:border-slate-800/70 flex items-center justify-between gap-4">
              <button
                onClick={() => setActiveQuizQuestion(Math.max(0, activeQuizQuestion - 1))}
                disabled={activeQuizQuestion === 0}
                className={`
                  px-4 py-2 border rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all duration-150 active:scale-98
                  ${activeQuizQuestion === 0 
                    ? 'text-slate-300 dark:text-slate-600 border-slate-100 dark:border-slate-800 cursor-not-allowed' 
                    : 'text-slate-700 hover:bg-slate-100 border-slate-200 dark:text-slate-300 dark:border-slate-800 dark:hover:bg-slate-800/70'}
                `}
              >
                <ChevronLeft className="w-4.5 h-4.5" />
                <span>Soal Sebelumnya</span>
              </button>

              {activeQuizQuestion === totalQuestions - 1 ? (
                <button
                  onClick={handleSubmitQuiz}
                  disabled={quizSubmitting}
                  className="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-brand-500/25 active:scale-98 transition-all duration-150 disabled:opacity-50"
                >
                  {quizSubmitting ? 'Mengirim...' : 'Kirim Jawaban'}
                  <ChevronRight className="w-4.5 h-4.5" />
                </button>
              ) : (
                <button
                  onClick={() => setActiveQuizQuestion(Math.min(totalQuestions - 1, activeQuizQuestion + 1))}
                  className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-xl text-xs font-bold flex items-center space-x-1.5 active:scale-98 transition-all duration-150 border border-slate-200 dark:border-slate-750"
                >
                  <span>Berikutnya</span>
                  <ChevronRight className="w-4.5 h-4.5" />
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Fallback loading layout
  return (
    <div className="min-h-[400px] flex items-center justify-center bg-transparent">
      <div className="flex flex-col items-center">
        <div className="w-10 h-10 rounded-full border-4 border-brand-200 border-t-brand-500 animate-spin mb-4"></div>
        <p className="text-slate-400 text-xs font-medium">Memproses database kurikulum adaptif...</p>
      </div>
    </div>
  );
};

export default Learning;
