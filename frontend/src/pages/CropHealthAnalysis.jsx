import React, { useState, useEffect, useRef } from 'react';
import { analyzeCropImageApi, getCropAnalysisHistoryApi } from '../api/client';
import Skeleton from '../components/common/Skeleton';
import { 
  MdCloudUpload, 
  MdImage, 
  MdInfoOutline, 
  MdWarningAmber, 
  MdHistory, 
  MdCheckCircle, 
  MdCropOriginal,
  MdAutoGraph,
  MdLayers,
  MdLocalFlorist,
  MdShield,
  MdLightbulb,
  MdHelpOutline,
  MdOutlineRefresh,
  MdOutlineCameraAlt,
  MdOutlineRule,
  MdCheck,
  MdClose
} from 'react-icons/md';

export default function CropHealthAnalysis() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    try {
      setLoadingHistory(true);
      const res = await getCropAnalysisHistoryApi(15);
      if (res && res.analyses) {
        setHistory(res.analyses);
      }
    } catch (err) {
      console.error('Failed to load analysis history:', err);
    } finally {
      setLoadingHistory(false);
    }
  }

  const validateAndSetFile = (file) => {
    setError(null);
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image file (JPG, PNG, or WEBP).');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Image file size exceeds 10MB limit.');
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setResult(null);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const data = await analyzeCropImageApi(formData);
      setResult(data);
      loadHistory();
    } catch (err) {
      setError(err.message || 'Vision AI analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const getSeverityBadge = (severity) => {
    const s = (severity || '').toLowerCase();
    if (s.includes('healthy') || s.includes('no obvious')) {
      return {
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dot: 'bg-emerald-500',
        label: 'Healthy / No Obvious Issue'
      };
    }
    if (s.includes('low')) {
      return {
        bg: 'bg-blue-50 text-blue-700 border-blue-200',
        dot: 'bg-blue-500',
        label: 'Low Severity'
      };
    }
    if (s.includes('moderate')) {
      return {
        bg: 'bg-amber-50 text-amber-700 border-amber-200',
        dot: 'bg-amber-500',
        label: 'Moderate Severity'
      };
    }
    if (s.includes('high') || s.includes('severe')) {
      return {
        bg: 'bg-rose-50 text-rose-700 border-rose-200',
        dot: 'bg-rose-500',
        label: 'High Severity'
      };
    }
    return {
      bg: 'bg-gray-100 text-gray-700 border-gray-200',
      dot: 'bg-gray-400',
      label: severity || 'Unknown'
    };
  };

  const getImageQualityBadge = (quality) => {
    const q = (quality || '').toLowerCase();
    if (q === 'good') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (q === 'acceptable') return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-rose-50 text-rose-700 border-rose-200';
  };

  // Map backend model_status to a user-friendly error card config
  const GEMINI_ERROR_CARDS = {
    gemini_sdk_missing: {
      icon: '🔧',
      title: 'Server Configuration Issue',
      message: 'Gemini Vision is not installed on the server.',
      detail: 'The google-genai package is missing from the backend. Contact your administrator.',
      color: 'border-gray-300 bg-gray-50',
      titleColor: 'text-gray-800',
    },
    gemini_api_key_missing: {
      icon: '🔑',
      title: 'Vision AI Not Configured',
      message: 'Gemini Vision is not configured on the server.',
      detail: 'GEMINI_API_KEY is not set in the server environment.',
      color: 'border-amber-200 bg-amber-50',
      titleColor: 'text-amber-900',
    },
    gemini_client_init_error: {
      icon: '⚙️',
      title: 'Initialization Error',
      message: 'Gemini Vision client failed to initialize.',
      detail: 'Check the server logs for Gemini client configuration errors.',
      color: 'border-orange-200 bg-orange-50',
      titleColor: 'text-orange-900',
    },
    gemini_auth_error: {
      icon: '🔒',
      title: 'Authentication Failed',
      message: 'Gemini API authentication failed.',
      detail: 'The server API key may be invalid or expired. Check GEMINI_API_KEY in your server configuration.',
      color: 'border-red-200 bg-red-50',
      titleColor: 'text-red-900',
    },
    gemini_model_not_found: {
      icon: '🤖',
      title: 'Model Unavailable',
      message: 'The configured Gemini model is unavailable.',
      detail: 'Update GEMINI_VISION_MODEL in your server configuration to a supported model (e.g. gemini-2.5-flash).',
      color: 'border-purple-200 bg-purple-50',
      titleColor: 'text-purple-900',
    },
    gemini_quota_error: {
      icon: '⏳',
      title: 'API Quota Reached',
      message: 'Gemini API quota or rate limit was reached.',
      detail: 'Please wait a moment and try again.',
      color: 'border-amber-200 bg-amber-50',
      titleColor: 'text-amber-900',
    },
    gemini_timeout_error: {
      icon: '📡',
      title: 'Request Timed Out',
      message: 'Gemini Vision could not be reached in time.',
      detail: 'Please check your network connection and try again.',
      color: 'border-blue-200 bg-blue-50',
      titleColor: 'text-blue-900',
    },
    gemini_network_error: {
      icon: '🌐',
      title: 'Network Error',
      message: 'Could not connect to Gemini Vision.',
      detail: 'Please check your network connection and try again.',
      color: 'border-blue-200 bg-blue-50',
      titleColor: 'text-blue-900',
    },
    gemini_response_error: {
      icon: '📄',
      title: 'Invalid Response',
      message: 'Gemini returned an unexpected response format.',
      detail: 'Please try again. If the issue persists, contact support.',
      color: 'border-gray-200 bg-gray-50',
      titleColor: 'text-gray-800',
    },
    gemini_image_error: {
      icon: '🖼️',
      title: 'Image Processing Failed',
      message: 'The uploaded image could not be processed.',
      detail: 'Try uploading a different JPEG, PNG, or WEBP image under 10MB.',
      color: 'border-rose-200 bg-rose-50',
      titleColor: 'text-rose-900',
    },
    gemini_api_error: {
      icon: '⚠️',
      title: 'Gemini API Error',
      message: 'Gemini Vision returned an unexpected error.',
      detail: 'Please try again. Check the server logs if the problem persists.',
      color: 'border-orange-200 bg-orange-50',
      titleColor: 'text-orange-900',
    },
  };

  const getGeminiErrorCard = (modelStatus, observations) => {
    const cfg = GEMINI_ERROR_CARDS[modelStatus];
    if (!cfg) return null;
    const serverDetail = observations && observations.length > 0 ? observations[0] : cfg.detail;
    return (
      <div className={`rounded-2xl shadow-sm border p-6 space-y-4 ${cfg.color}`}>
        <div className="flex items-start gap-3">
          <span className="text-3xl leading-none">{cfg.icon}</span>
          <div>
            <h2 className={`text-lg font-bold ${cfg.titleColor}`}>{cfg.title}</h2>
            <p className="text-sm font-semibold text-gray-700 mt-1">{cfg.message}</p>
          </div>
        </div>
        <div className="bg-white/70 rounded-xl border border-white/50 p-4 text-xs text-gray-700 space-y-1.5">
          <p className="font-semibold text-gray-800">Server message:</p>
          <p className="leading-relaxed">{serverDetail}</p>
          {cfg.detail !== serverDetail && (
            <p className="text-gray-500 italic mt-1">{cfg.detail}</p>
          )}
        </div>
        <p className="text-[11px] text-gray-500">
          ⓘ This is a server-side configuration or connectivity issue, not an image problem.
          No API keys or secrets are ever sent to or displayed in the browser.
        </p>
      </div>
    );
  };


  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-50 rounded-xl border border-emerald-100 text-emerald-600 shadow-xs">
            <MdLocalFlorist size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Crop Health Vision AI</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Multimodal botanical visual intelligence for real-time crop disease and stress detection
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold rounded-full shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Multimodal Vision AI
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload & Controls */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <MdCloudUpload className="text-emerald-600" size={20} />
                Upload Plant / Leaf Photo
              </h2>
              {selectedFile && (
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFile(null);
                    setPreviewUrl(null);
                    setResult(null);
                  }}
                  className="text-xs text-gray-400 hover:text-gray-600 font-medium"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Drag & Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[240px] ${
                dragOver
                  ? 'border-emerald-500 bg-emerald-50/40 scale-[0.99]'
                  : 'border-gray-200 hover:border-emerald-400 bg-gray-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={handleFileChange}
              />

              {previewUrl ? (
                <div className="relative w-full aspect-video max-h-56 rounded-xl overflow-hidden shadow-xs border border-gray-200">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-full h-full object-contain bg-black/5"
                  />
                  <div className="absolute inset-0 bg-black/30 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold backdrop-blur-xs">
                    <MdOutlineCameraAlt size={18} className="mr-1.5" />
                    Click to change photo
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-14 h-14 mx-auto rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 shadow-xs">
                    <MdImage size={28} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-800">
                      Drag & drop any crop or plant photo
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Leaves, fruits, stems, or field samples (JPG, PNG, WEBP - Max 10MB)
                    </p>
                  </div>
                  <button
                    type="button"
                    className="px-4 py-1.5 bg-white border border-gray-200 text-xs font-semibold text-gray-700 rounded-lg shadow-xs hover:bg-gray-50"
                  >
                    Select from Device
                  </button>
                </div>
              )}
            </div>

            {selectedFile && (
              <div className="flex items-center justify-between text-xs text-gray-600 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <span className="font-medium truncate max-w-[200px]">{selectedFile.name}</span>
                <span className="text-gray-400">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
              </div>
            )}

            {error && (
              <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 text-xs font-medium rounded-xl flex items-start gap-2.5">
                <MdWarningAmber className="shrink-0 mt-0.5" size={16} />
                <span className="leading-relaxed">{error}</span>
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!selectedFile || analyzing}
              className="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
            >
              {analyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Running Multimodal Vision AI...</span>
                </>
              ) : (
                <>
                  <MdAutoGraph size={18} />
                  <span>Analyze Crop Health</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Best Practice Guide */}
          <div className="bg-emerald-50/40 border border-emerald-100 rounded-2xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
              <MdLightbulb size={16} className="text-emerald-600" />
              Photography Tips for Accurate AI Analysis
            </h3>
            <ul className="space-y-2 text-xs text-emerald-900/80">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                <span><strong>Clear Focus:</strong> Hold camera 15-30cm from the affected leaf or fruit.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                <span><strong>Natural Daylight:</strong> Avoid harsh flash glare or deep shadows.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                <span><strong>Contrast:</strong> Capture both healthy and affected portions in the frame.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Right Column: AI Analysis Result Card */}
        <div className="lg:col-span-7 space-y-6">
          {analyzing ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 space-y-5">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
                <h3 className="text-sm font-bold text-gray-800">Analyzing crop image with Gemini Multimodal AI...</h3>
              </div>
              <Skeleton className="h-20 w-full rounded-xl" />
              <Skeleton className="h-32 w-full rounded-xl" />
              <Skeleton className="h-28 w-full rounded-xl" />
            </div>
          ) : result ? (
          (() => {
            // First check for backend Gemini error states — render a proper error card
            const errorCard = getGeminiErrorCard(result.model_status, result.observations);
            if (errorCard) return errorCard;

            return result.image_relevant === false ? (
              /* Non-Crop / Irrelevant Image Notice */
              <div className="bg-white rounded-2xl shadow-sm border border-amber-200 p-6 space-y-5">
                <div className="flex items-start gap-3">
                  <div className="p-2.5 bg-amber-100 text-amber-800 rounded-xl">
                    <MdWarningAmber size={26} />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Non-Agricultural Image Detected</h2>
                    <p className="text-xs text-gray-500 mt-1">
                      {result.relevance_reason || 'The uploaded image does not contain a recognizable crop or plant.'}
                    </p>
                  </div>
                </div>

                <div className="bg-amber-50/60 p-4 rounded-xl border border-amber-100 text-xs text-amber-900 space-y-2">
                  <p className="font-semibold">Next Step:</p>
                  <p>{result.recommendations?.[0] || 'Please upload a photo of a crop, plant leaf, fruit, or farm problem.'}</p>
                  {result.next_photo_tip && (
                    <p className="text-amber-800/80 italic mt-1">Tip: {result.next_photo_tip}</p>
                  )}
                </div>
              </div>
            ) : (
              /* Comprehensive Agricultural Analysis Results */
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6">
                {/* Identification & Condition Header */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-gray-100 pb-5">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-xl font-bold text-gray-900">
                        {result.crop && result.crop !== 'Unknown' ? result.crop : 'Plant / Crop Sample'}
                      </h2>
                      {result.plant_part && (
                        <span className="px-2.5 py-0.5 bg-gray-100 text-gray-700 text-xs font-semibold rounded-md">
                          {result.plant_part}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-semibold text-emerald-800 mt-1 flex items-center gap-1.5">
                      <MdCheckCircle className="text-emerald-600" size={16} />
                      Condition: {result.overall_condition || 'Analyzed'}
                    </p>
                  </div>

                  {/* Severity Badge */}
                  {(() => {
                    const badge = getSeverityBadge(result.severity);
                    return (
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 border text-xs font-bold rounded-xl ${badge.bg}`}>
                        <span className={`w-2 h-2 rounded-full ${badge.dot}`}></span>
                        {badge.label}
                      </span>
                    );
                  })()}
                </div>

                {/* Key Metadata Row */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Image Quality</p>
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className={`px-2 py-0.5 border text-xs font-bold rounded ${getImageQualityBadge(result.image_quality)}`}>
                        {result.image_quality || 'Acceptable'}
                      </span>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">AI Engine</p>
                    <p className="text-xs font-bold text-gray-800 mt-1 truncate">
                      {result.model?.name || 'Gemini Vision AI'}
                    </p>
                  </div>

                  <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100 col-span-2 sm:col-span-1">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Dimensions</p>
                    <p className="text-xs font-bold text-gray-800 mt-1">
                      {result.width && result.height ? `${result.width} × ${result.height} px` : 'Standard'}
                    </p>
                  </div>
                </div>

                {/* Visible Observations */}
                {result.observations && result.observations.length > 0 && (
                  <div className="space-y-2.5">
                    <h3 className="text-xs font-bold text-gray-800 uppercase tracking-wider flex items-center gap-1.5">
                      <MdOutlineRule className="text-emerald-600" size={16} />
                      Observed Symptoms (Visual Evidence)
                    </h3>
                    <div className="space-y-2 bg-gray-50/70 p-4 rounded-xl border border-gray-100">
                      {result.observations.map((obs, idx) => (
                        <div key={idx} className="flex items-start gap-2.5 text-xs text-gray-700">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                          <p className="leading-relaxed">{obs}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Possible Issues & Reasons */}
                {result.possible_issues && result.possible_issues.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-xs font-bold text-gray-800 uppercase tracking-wider flex items-center gap-1.5">
                      <MdInfoOutline className="text-emerald-600" size={16} />
                      Possible Issues & Explanations
                    </h3>
                    <div className="space-y-2.5">
                      {result.possible_issues.map((issue, idx) => (
                        <div key={idx} className="p-4 bg-emerald-50/40 border border-emerald-100 rounded-xl space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-emerald-950">{issue.name}</span>
                            {issue.confidence && (
                              <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                                {issue.confidence}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-emerald-900/80 leading-relaxed">{issue.reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Farmer-friendly Recommendations */}
                {result.recommendations && result.recommendations.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-xs font-bold text-gray-800 uppercase tracking-wider flex items-center gap-1.5">
                      <MdShield className="text-emerald-600" size={16} />
                      Recommended Next Steps
                    </h3>
                    <div className="space-y-2 bg-emerald-50/30 p-4 rounded-xl border border-emerald-100/70">
                      {result.recommendations.map((rec, idx) => (
                        <div key={idx} className="flex items-start gap-2.5 text-xs text-gray-800">
                          <span className="p-0.5 bg-emerald-100 text-emerald-700 rounded-full mt-0.5 shrink-0">
                            <MdCheck size={12} />
                          </span>
                          <span className="leading-relaxed font-medium">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Photo Retake Tip */}
                {result.next_photo_tip && (
                  <div className="p-4 bg-amber-50/50 border border-amber-200/60 rounded-xl text-xs text-amber-950 flex items-start gap-3">
                    <MdOutlineCameraAlt size={18} className="text-amber-700 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-amber-900">Photography Recommendation: </span>
                      <span className="text-amber-900/80">{result.next_photo_tip}</span>
                    </div>
                  </div>
                )}

                {/* Honesty & Safety Disclaimer */}
                <div className="p-3.5 bg-gray-50 border border-gray-200 rounded-xl text-[11px] text-gray-500 flex items-start gap-2.5">
                  <MdInfoOutline size={16} className="text-gray-400 shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    <strong>Honesty Notice:</strong> {result.disclaimer || 'This is AI-assisted visual guidance based on image evidence, not a certified laboratory diagnosis. Always verify with local agricultural experts before applying chemical treatments.'}
                  </p>
                </div>
              </div>
            );
          })()
          ) : (
            /* Blank state */
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center flex flex-col items-center justify-center min-h-[380px] text-gray-400 space-y-3">
              <div className="w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
                <MdCropOriginal size={32} />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-700">No Image Analyzed Yet</p>
                <p className="text-xs text-gray-400 mt-1 max-w-sm">
                  Upload a photo of any crop leaf, stem, fruit, or field sample on the left to receive instant multimodal visual health diagnostics.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* History Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-gray-100 pb-4">
          <div className="flex items-center gap-2">
            <MdHistory className="text-emerald-600" size={20} />
            <h2 className="text-base font-bold text-gray-900">Analysis History</h2>
          </div>
          <button 
            onClick={loadHistory}
            className="text-xs text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1 cursor-pointer"
          >
            <MdOutlineRefresh size={14} />
            Refresh
          </button>
        </div>

        {loadingHistory ? (
          <div className="space-y-3">
            <Skeleton className="h-12 w-full rounded-xl" />
            <Skeleton className="h-12 w-full rounded-xl" />
          </div>
        ) : history.length === 0 ? (
          <p className="text-xs text-gray-400 py-4 text-center">No past analyses recorded for this farm.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-100 text-gray-400 font-bold uppercase tracking-wider">
                  <th className="pb-3 px-3">Date & Time</th>
                  <th className="pb-3 px-3">Crop / Plant</th>
                  <th className="pb-3 px-3">Part</th>
                  <th className="pb-3 px-3">Condition</th>
                  <th className="pb-3 px-3">Severity</th>
                  <th className="pb-3 px-3">Engine</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 text-gray-700">
                {history.map((item) => {
                  const severityBadge = getSeverityBadge(item.severity);
                  return (
                    <tr key={item.id} className="hover:bg-gray-50/60 transition-colors">
                      <td className="py-3 px-3 font-medium text-gray-900">
                        {item.created_at ? new Date(item.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : 'N/A'}
                      </td>
                      <td className="py-3 px-3 font-semibold text-gray-800">
                        {item.crop || 'Unknown'}
                      </td>
                      <td className="py-3 px-3 text-gray-500">
                        {item.plant_part || 'Leaf'}
                      </td>
                      <td className="py-3 px-3 max-w-[220px] truncate text-gray-600">
                        {item.overall_condition || (item.observations?.[0] ? item.observations[0] : 'Analyzed')}
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 border rounded text-[10px] font-semibold ${severityBadge.bg}`}>
                          {item.severity || 'Unknown'}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-gray-400 text-[11px]">
                        {item.model_name || 'Vision AI'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
