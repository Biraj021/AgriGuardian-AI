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
  MdLayers
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
      const res = await getCropAnalysisHistoryApi(10);
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
      setError(err.message || 'Image analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary-50 rounded-xl border border-primary-100 text-primary-600">
            <MdCropOriginal size={26} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Crop Image AI Analysis</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Computer vision architecture and visual telemetry for leaf and crop imagery
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload & Controls */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <MdCloudUpload className="text-primary-600" size={20} />
              Upload Crop Image
            </h2>

            {/* Drag & Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px] ${
                dragOver
                  ? 'border-primary-500 bg-primary-50/40 scale-[0.99]'
                  : 'border-gray-200 hover:border-primary-400 bg-gray-50/50'
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
                <div className="relative w-full aspect-video max-h-52 rounded-xl overflow-hidden shadow-sm border border-gray-200">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-full h-full object-contain bg-black/5"
                  />
                  <div className="absolute inset-0 bg-black/20 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold backdrop-blur-xs">
                    Click to change image
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-14 h-14 mx-auto rounded-full bg-primary-50 border border-primary-100 flex items-center justify-center text-primary-600 shadow-xs">
                    <MdImage size={28} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-800">
                      Drag and drop your crop photo here
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Supports JPG, PNG, WEBP (Max 10MB)
                    </p>
                  </div>
                  <button
                    type="button"
                    className="px-4 py-1.5 bg-white border border-gray-200 text-xs font-semibold text-gray-700 rounded-lg shadow-xs hover:bg-gray-50"
                  >
                    Browse Files
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
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs font-medium rounded-xl flex items-start gap-2">
                <MdWarningAmber className="shrink-0 mt-0.5" size={16} />
                <span>{error}</span>
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!selectedFile || analyzing}
              className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white font-bold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
            >
              {analyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Running Vision Pipeline...</span>
                </>
              ) : (
                <>
                  <MdAutoGraph size={18} />
                  <span>Analyze Crop Image</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: AI Analysis Result Card */}
        <div className="lg:col-span-7 space-y-6">
          {analyzing ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 space-y-4">
              <Skeleton className="h-6 w-48 rounded-lg" />
              <Skeleton className="h-24 w-full rounded-xl" />
              <Skeleton className="h-32 w-full rounded-xl" />
            </div>
          ) : result ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6">
              {/* Header Status */}
              <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Analysis Telemetry</h2>
                  <p className="text-xs text-gray-400 mt-0.5">ID: {result.analysis_id}</p>
                </div>
                <span className="px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 text-xs font-bold rounded-full">
                  Prototype Heuristics
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Format</p>
                  <p className="text-base font-bold text-gray-800 mt-0.5">{result.image_format || 'N/A'}</p>
                </div>
                <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Dimensions</p>
                  <p className="text-base font-bold text-gray-800 mt-0.5">{result.width} x {result.height}</p>
                </div>
                <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Green Ratio</p>
                  <p className="text-base font-bold text-emerald-600 mt-0.5">
                    {result.vegetation_proxy?.green_dominant_pixel_ratio != null
                      ? `${(result.vegetation_proxy.green_dominant_pixel_ratio * 100).toFixed(1)}%`
                      : 'N/A'}
                  </p>
                </div>
                <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Model Status</p>
                  <p className="text-[11px] font-bold text-amber-700 mt-1 truncate">No Trained Model</p>
                </div>
              </div>

              {/* Observations */}
              <div className="space-y-2.5">
                <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
                  <MdInfoOutline className="text-primary-600" size={16} />
                  Visual Observations
                </h3>
                <div className="space-y-2 bg-gray-50/60 p-4 rounded-xl border border-gray-100">
                  {result.observations && result.observations.map((obs, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-gray-700">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-1.5 shrink-0"></span>
                      <p className="leading-relaxed">{obs}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quality Notes */}
              {result.quality_notes && result.quality_notes.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider">Image Quality Assessment</h3>
                  <div className="space-y-1.5">
                    {result.quality_notes.map((note, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded-lg border border-gray-100">
                        <MdCheckCircle className="text-primary-500 shrink-0" size={14} />
                        <span>{note}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Architecture Extensibility Note */}
              <div className="p-4 bg-primary-50/50 border border-primary-100 rounded-xl text-xs text-primary-950 space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-primary-800">
                  <MdLayers size={16} />
                  Replaceable Vision Architecture
                </div>
                <p className="text-primary-900/80 leading-relaxed">
                  The backend utilizes a standardized <code className="bg-primary-100 px-1 py-0.5 rounded text-primary-900">VisionAnalyzer</code> abstraction. When a fine-tuned crop-disease model (such as ResNet/EfficientNet on PlantVillage) is integrated, it replaces the analyzer class seamlessly without breaking this dashboard or API contract.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center flex flex-col items-center justify-center min-h-[360px] text-gray-400 space-y-3">
              <div className="w-16 h-16 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center text-gray-300">
                <MdCropOriginal size={32} />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-700">No Image Analyzed Yet</p>
                <p className="text-xs text-gray-400 mt-1 max-w-sm">
                  Upload a clear image of a crop leaf or field sample on the left and click "Analyze Crop Image" to inspect visual metrics.
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
            <MdHistory className="text-primary-600" size={20} />
            <h2 className="text-base font-bold text-gray-900">Analysis History</h2>
          </div>
          <button 
            onClick={loadHistory}
            className="text-xs text-primary-600 hover:text-primary-700 font-semibold"
          >
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
                  <th className="pb-3 px-2">Date & Time</th>
                  <th className="pb-3 px-2">Dimensions</th>
                  <th className="pb-3 px-2">Format</th>
                  <th className="pb-3 px-2">Green Ratio</th>
                  <th className="pb-3 px-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 text-gray-700">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50/60 transition-colors">
                    <td className="py-3 px-2 font-medium">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-3 px-2">
                      {item.image_width && item.image_height ? `${item.image_width}x${item.image_height}` : 'N/A'}
                    </td>
                    <td className="py-3 px-2">{item.image_format || 'N/A'}</td>
                    <td className="py-3 px-2 font-semibold text-emerald-600">
                      {item.vegetation_proxy?.green_dominant_pixel_ratio != null
                        ? `${(item.vegetation_proxy.green_dominant_pixel_ratio * 100).toFixed(1)}%`
                        : 'N/A'}
                    </td>
                    <td className="py-3 px-2">
                      <span className="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 rounded text-[10px] font-semibold">
                        Prototype
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
