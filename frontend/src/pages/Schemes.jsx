import React, { useState, useEffect, useMemo } from 'react';
import { getSchemesApi, checkSchemeEligibilityApi } from '../api/client';
import Skeleton from '../components/common/Skeleton';
import {
  MdSearch,
  MdFilterList,
  MdOpenInNew,
  MdCheckCircle,
  MdInfoOutline,
  MdAgriculture,
  MdClose,
  MdRefresh,
  MdVerified,
  MdBookmarkBorder,
  MdChevronRight,
  MdDescription,
} from 'react-icons/md';

const INDIAN_STATES = [
  'All States & UTs',
  'Andhra Pradesh',
  'Bihar',
  'Gujarat',
  'Haryana',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Tamil Nadu',
  'Telangana',
  'Uttar Pradesh',
  'West Bengal',
];

const CROP_OPTIONS = [
  'All Crops',
  'Wheat',
  'Rice',
  'Cotton',
  'Maize',
  'Soybean',
  'Sugarcane',
  'Pulses',
  'Millets',
  'Vegetables',
  'Fruits',
];

const FARMER_CATEGORIES = [
  'All Categories',
  'Small / Marginal (< 5 Acres)',
  'Medium / Large (> 5 Acres)',
  'Women Farmer',
  'SC/ST',
  'Tenant Farmer',
];

const CATEGORY_TABS = [
  { id: 'All', label: 'All Schemes' },
  { id: 'Direct Income Support', label: 'Income Support' },
  { id: 'Crop Insurance', label: 'Insurance' },
  { id: 'Irrigation & Solar', label: 'Irrigation & Solar' },
  { id: 'Credit & Finance', label: 'Credit & Loans' },
  { id: 'Farm Machinery', label: 'Machinery Subsidy' },
  { id: 'Soil & Organic', label: 'Soil & Organic' },
];

const CATEGORY_COLORS = {
  'Direct Income Support': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Crop Insurance': 'bg-blue-50 text-blue-700 border-blue-200',
  'Irrigation & Solar': 'bg-cyan-50 text-cyan-700 border-cyan-200',
  'Credit & Finance': 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Farm Machinery': 'bg-amber-50 text-amber-700 border-amber-200',
  'Soil & Organic': 'bg-purple-50 text-purple-700 border-purple-200',
};

const MATCH_BADGE_STYLE = {
  'High Match': 'bg-emerald-100 text-emerald-800 border-emerald-300',
  'Moderate Match': 'bg-blue-100 text-blue-800 border-blue-300',
  'General Match': 'bg-gray-100 text-gray-700 border-gray-200',
};

export default function SchemesPage() {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [error, setError] = useState(null);
  const [disclaimer, setDisclaimer] = useState('');

  // Filter & Search states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedState, setSelectedState] = useState('All States & UTs');
  const [selectedCrop, setSelectedCrop] = useState('All Crops');
  const [landAcres, setLandAcres] = useState('');
  const [farmerCategory, setFarmerCategory] = useState('All Categories');

  // Evaluation profile state (when user clicked "Find Relevant Schemes")
  const [appliedEvaluation, setAppliedEvaluation] = useState(null);

  // Selected scheme for detail modal
  const [activeModalScheme, setActiveModalScheme] = useState(null);

  // Initial load
  useEffect(() => {
    fetchInitialSchemes();
  }, []);

  async function fetchInitialSchemes() {
    setLoading(true);
    setError(null);
    try {
      const res = await getSchemesApi();
      if (res && res.schemes) {
        setSchemes(res.schemes);
        if (res.disclaimer) setDisclaimer(res.disclaimer);
      }
    } catch (err) {
      console.error('Failed to load schemes:', err);
      setError(err.message || 'Unable to connect to the Government Schemes service.');
    } finally {
      setLoading(false);
    }
  }

  // Handle Eligibility check / Find Schemes
  async function handleFindSchemes(e) {
    if (e) e.preventDefault();
    setCheckingEligibility(true);
    setError(null);

    const payload = {
      state: selectedState !== 'All States & UTs' ? selectedState : null,
      crop: selectedCrop !== 'All Crops' ? selectedCrop : null,
      land_acres: landAcres !== '' && !isNaN(Number(landAcres)) ? parseFloat(landAcres) : null,
      farmer_category: farmerCategory !== 'All Categories' ? farmerCategory : null,
    };

    try {
      const res = await checkSchemeEligibilityApi(payload);
      if (res && res.schemes) {
        setSchemes(res.schemes);
        setAppliedEvaluation(res.input_profile);
        if (res.disclaimer) setDisclaimer(res.disclaimer);
      }
    } catch (err) {
      console.error('Eligibility check error:', err);
      setError(err.message || 'Failed to evaluate scheme eligibility.');
    } finally {
      setCheckingEligibility(false);
    }
  }

  // Handle reset
  function handleResetFilters() {
    setSearchQuery('');
    setSelectedCategory('All');
    setSelectedState('All States & UTs');
    setSelectedCrop('All Crops');
    setLandAcres('');
    setFarmerCategory('All Categories');
    setAppliedEvaluation(null);
    fetchInitialSchemes();
  }

  // Filter schemes on client for instantaneous search and category tabs
  const filteredSchemes = useMemo(() => {
    return schemes.filter((scheme) => {
      // Category tab
      if (selectedCategory !== 'All') {
        if (!scheme.category.toLowerCase().includes(selectedCategory.toLowerCase())) {
          return false;
        }
      }
      // Text search
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchName = scheme.name?.toLowerCase().includes(query);
        const matchDesc = scheme.short_description?.toLowerCase().includes(query);
        const matchBenefits = scheme.benefits?.toLowerCase().includes(query);
        const matchDocs = (scheme.required_documents || []).some((doc) =>
          doc.toLowerCase().includes(query)
        );
        if (!matchName && !matchDesc && !matchBenefits && !matchDocs) {
          return false;
        }
      }
      return true;
    });
  }, [schemes, selectedCategory, searchQuery]);

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 pb-16">
      {/* Header Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-emerald-800 via-emerald-700 to-teal-800 rounded-3xl p-6 sm:p-8 text-white shadow-lg">
        <div className="relative z-10 max-w-3xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-emerald-200 text-xs font-semibold uppercase tracking-wider border border-white/10">
            <MdAgriculture className="text-base" /> National Agriculture Support Portal
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Government Schemes & Subsidies Finder
          </h1>
          <p className="text-emerald-100 text-sm sm:text-base leading-relaxed">
            Discover Central & State agricultural programs, direct income assistance, crop insurance,
            solar irrigation subsidies, and affordable credit options tailored to your farm profile.
          </p>
        </div>
        {/* Background decorative circles */}
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 rounded-full bg-emerald-500/20 blur-2xl pointer-events-none" />
        <div className="absolute right-32 bottom-0 translate-y-12 w-48 h-48 rounded-full bg-teal-400/20 blur-xl pointer-events-none" />
      </div>

      {/* Advisory & Legal Disclaimer Banner */}
      <div className="bg-amber-50 border border-amber-200/80 rounded-2xl p-4 flex items-start gap-3 text-xs text-amber-900 shadow-sm">
        <MdInfoOutline className="text-amber-600 text-lg shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-amber-900">Official Advisory & Information Notice</p>
          <p className="text-amber-800/90 leading-relaxed">
            {disclaimer ||
              'This module provides recommendations and relevance estimates based on public guidelines of Government of India schemes. It is an informational advisory tool and does not constitute a legally binding eligibility decision or official sanction. Final approval is subject to document verification by designated authorities.'}
          </p>
        </div>
      </div>

      {/* Scheme Recommendation & Filter Card */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-sm space-y-5">
        <div className="flex items-center justify-between flex-wrap gap-2 border-b border-gray-100 pb-3">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-primary-50 text-primary-600 font-bold text-lg">
              🎯
            </span>
            <div>
              <h2 className="text-base font-bold text-gray-900">Farmer Profile & Scheme Eligibility Matcher</h2>
              <p className="text-xs text-gray-500">
                Provide your farm details to get customized scheme relevance scores and required documents
              </p>
            </div>
          </div>
          {(selectedState !== 'All States & UTs' ||
            selectedCrop !== 'All Crops' ||
            landAcres !== '' ||
            farmerCategory !== 'All Categories' ||
            searchQuery !== '' ||
            appliedEvaluation) && (
            <button
              onClick={handleResetFilters}
              className="text-xs font-semibold text-gray-500 hover:text-gray-800 flex items-center gap-1 transition-colors px-2 py-1 rounded-lg hover:bg-gray-100"
            >
              <MdRefresh size={14} /> Reset All
            </button>
          )}
        </div>

        <form onSubmit={handleFindSchemes} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {/* State Selector */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                State / Union Territory
              </label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              >
                {INDIAN_STATES.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            {/* Crop Selector */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Primary Crop Cultivated
              </label>
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              >
                {CROP_OPTIONS.map((cr) => (
                  <option key={cr} value={cr}>
                    {cr}
                  </option>
                ))}
              </select>
            </div>

            {/* Landholding Size */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Land Size (Acres)
              </label>
              <input
                type="number"
                min="0"
                max="1000"
                step="0.1"
                placeholder="e.g. 4.5"
                value={landAcres}
                onChange={(e) => setLandAcres(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              />
            </div>

            {/* Farmer Category */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Farmer Category
              </label>
              <select
                value={farmerCategory}
                onChange={(e) => setFarmerCategory(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              >
                {FARMER_CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Action Row: Search & Find Button */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
            {/* Search Input */}
            <div className="relative flex-1">
              <MdSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                type="text"
                placeholder="Search schemes by name, keyword (e.g., solar, loan, drip, subsidy)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl pl-10 pr-9 py-2.5 text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <MdClose size={16} />
                </button>
              )}
            </div>

            <button
              type="submit"
              disabled={checkingEligibility}
              className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 active:scale-95 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center justify-center gap-2 shrink-0 disabled:opacity-60 cursor-pointer"
            >
              {checkingEligibility ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Evaluating Eligibility...
                </>
              ) : (
                <>
                  <MdFilterList size={16} />
                  Find Schemes & Check Eligibility
                </>
              )}
            </button>
          </div>
        </form>

        {appliedEvaluation && (
          <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-xl p-3 flex items-center justify-between flex-wrap gap-2 text-xs text-emerald-900">
            <div className="flex items-center gap-2">
              <MdVerified className="text-emerald-600 text-base shrink-0" />
              <span>
                Personalized match calculated for: <strong>{appliedEvaluation.state}</strong> • Crop:{' '}
                <strong>{appliedEvaluation.crop}</strong>
                {appliedEvaluation.land_acres != null && (
                  <>
                    {' '}
                    • Holding: <strong>{appliedEvaluation.land_acres} Acres</strong>
                  </>
                )}
                {appliedEvaluation.farmer_category && (
                  <>
                    {' '}
                    • Category: <strong>{appliedEvaluation.farmer_category}</strong>
                  </>
                )}
              </span>
            </div>
            <span className="text-[11px] font-semibold text-emerald-700 bg-white px-2 py-0.5 rounded-md border border-emerald-200">
              Ranked by Relevance
            </span>
          </div>
        )}
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {CATEGORY_TABS.map((tab) => {
          const isActive = selectedCategory === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                isActive
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 text-xs p-4 rounded-xl flex items-center justify-between">
          <p>{error}</p>
          <button
            onClick={fetchInitialSchemes}
            className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 font-bold rounded-lg transition-colors cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Scheme Cards Count Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-gray-800">
          Showing {filteredSchemes.length} Scheme{filteredSchemes.length === 1 ? '' : 's'}
        </h3>
        {appliedEvaluation && (
          <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
            <MdCheckCircle /> AI Relevance Scoring Active
          </span>
        )}
      </div>

      {/* Loading Skeleton */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm space-y-4">
              <div className="flex items-center gap-3">
                <Skeleton className="w-12 h-12 rounded-2xl" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/3" />
                </div>
              </div>
              <Skeleton className="h-12 w-full rounded-xl" />
              <Skeleton className="h-20 w-full rounded-xl" />
              <div className="flex gap-2">
                <Skeleton className="h-8 flex-1 rounded-xl" />
                <Skeleton className="h-8 w-28 rounded-xl" />
              </div>
            </div>
          ))}
        </div>
      ) : filteredSchemes.length === 0 ? (
        /* Empty State */
        <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center space-y-4 shadow-sm">
          <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center text-3xl mx-auto">
            🔍
          </div>
          <div className="space-y-1">
            <h4 className="text-base font-bold text-gray-800">No matching schemes found</h4>
            <p className="text-xs text-gray-500 max-w-md mx-auto">
              We couldn't find any schemes matching your current combination of category, crop, and search filters.
            </p>
          </div>
          <button
            onClick={handleResetFilters}
            className="px-4 py-2 bg-primary-50 text-primary-700 font-bold text-xs rounded-xl hover:bg-primary-100 transition-colors inline-flex items-center gap-1 cursor-pointer"
          >
            <MdRefresh size={16} /> Reset Filters
          </button>
        </div>
      ) : (
        /* Scheme Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filteredSchemes.map((scheme) => {
            const categoryClass =
              CATEGORY_COLORS[scheme.category] || 'bg-gray-100 text-gray-700 border-gray-200';
            const matchClass =
              MATCH_BADGE_STYLE[scheme.match_level] || 'bg-gray-100 text-gray-700 border-gray-200';

            return (
              <div
                key={scheme.id}
                className="bg-white rounded-2xl border border-gray-100 hover:border-primary-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between overflow-hidden"
              >
                <div className="p-5 sm:p-6 space-y-4 flex-1">
                  {/* Card Top: Icon, Title, Badges */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-2xl shrink-0 shadow-sm">
                        {scheme.icon || '🏛️'}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span
                            className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${categoryClass}`}
                          >
                            {scheme.category}
                          </span>
                          {scheme.match_level && (
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${matchClass} flex items-center gap-1`}
                            >
                              <MdVerified size={12} />
                              {scheme.match_level} ({scheme.relevance_score}%)
                            </span>
                          )}
                        </div>
                        <h4 className="text-sm sm:text-base font-bold text-gray-900 leading-snug">
                          {scheme.name}
                        </h4>
                      </div>
                    </div>
                  </div>

                  {/* Short Description */}
                  <p className="text-xs text-gray-600 leading-relaxed">{scheme.short_description}</p>

                  {/* Benefits Highlight Box */}
                  <div className="bg-gradient-to-br from-emerald-50/80 to-teal-50/40 border border-emerald-100/90 rounded-xl p-3.5 text-xs text-emerald-950">
                    <p className="text-[10px] uppercase font-bold text-emerald-800 tracking-wider mb-1 flex items-center gap-1">
                      <span>🎁</span> Key Benefits & Financial Assistance
                    </p>
                    <p className="font-medium text-emerald-900 leading-relaxed">{scheme.benefits}</p>
                  </div>

                  {/* Eligibility Snippet */}
                  <div className="space-y-1 text-xs">
                    <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">
                      Basic Eligibility
                    </p>
                    <p className="text-gray-700 leading-relaxed font-medium bg-gray-50/80 p-2.5 rounded-xl border border-gray-100">
                      {scheme.basic_eligibility}
                    </p>
                  </div>

                  {/* Match Reasons (if evaluated) */}
                  {scheme.match_reasons && scheme.match_reasons.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      <p className="text-[10px] uppercase font-bold text-emerald-700 tracking-wider">
                        Relevance Factors for Your Profile
                      </p>
                      <div className="space-y-1">
                        {scheme.match_reasons.map((reason, idx) => (
                          <div
                            key={idx}
                            className="flex items-center gap-1.5 text-[11px] text-gray-600"
                          >
                            <MdCheckCircle className="text-emerald-500 shrink-0" size={13} />
                            <span>{reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Required Documents Tags */}
                  <div className="space-y-1.5 pt-1">
                    <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">
                      Required Documents
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {(scheme.required_documents || []).map((doc, idx) => (
                        <span
                          key={idx}
                          className="text-[10px] font-medium bg-gray-100 text-gray-700 px-2 py-0.5 rounded-lg border border-gray-200/60"
                        >
                          📄 {doc}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Card Footer: Action Buttons */}
                <div className="p-4 bg-gray-50/80 border-t border-gray-100 flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveModalScheme(scheme)}
                    className="flex-1 px-3 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-white hover:bg-gray-100 border border-gray-200 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <MdDescription size={15} />
                    View Details
                  </button>

                  <a
                    href={scheme.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 px-3 py-2 rounded-xl text-xs font-bold text-white bg-primary-600 hover:bg-primary-700 shadow-sm transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <span>Official Portal</span>
                    <MdOpenInNew size={14} />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Scheme Detail Modal */}
      {activeModalScheme && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl border border-gray-100">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 border-b border-gray-100 pb-4">
              <div className="flex items-start gap-3.5">
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-3xl shrink-0">
                  {activeModalScheme.icon || '🏛️'}
                </div>
                <div>
                  <span
                    className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                      CATEGORY_COLORS[activeModalScheme.category] || 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {activeModalScheme.category}
                  </span>
                  <h3 className="text-lg font-bold text-gray-900 mt-1">
                    {activeModalScheme.name}
                  </h3>
                  <p className="text-xs text-gray-500 font-medium mt-0.5">
                    Central Sector / Government of India Scheme
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveModalScheme(null)}
                className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 flex items-center justify-center transition-colors cursor-pointer"
              >
                <MdClose size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="space-y-4 text-xs text-gray-700 leading-relaxed">
              <div>
                <h4 className="font-bold text-gray-900 text-sm mb-1">About the Scheme</h4>
                <p className="text-gray-600">{activeModalScheme.short_description}</p>
              </div>

              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 space-y-1">
                <h4 className="font-bold text-emerald-900 text-xs uppercase tracking-wider flex items-center gap-1">
                  <span>💰</span> Benefits & Financial Assistance
                </h4>
                <p className="text-emerald-900 font-medium">{activeModalScheme.benefits}</p>
              </div>

              <div className="space-y-1">
                <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider">
                  Detailed Eligibility Guidelines
                </h4>
                <p className="bg-gray-50 p-3 rounded-xl border border-gray-100 text-gray-700 font-medium">
                  {activeModalScheme.basic_eligibility}
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                  <h5 className="font-bold text-gray-700 mb-1 text-[11px] uppercase">
                    Applicable States
                  </h5>
                  <p className="text-gray-600">
                    {(activeModalScheme.applicable_states || []).join(', ')}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                  <h5 className="font-bold text-gray-700 mb-1 text-[11px] uppercase">
                    Applicable Crops
                  </h5>
                  <p className="text-gray-600">
                    {(activeModalScheme.applicable_crops || []).join(', ')}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider">
                  Required Documentation Checklist
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(activeModalScheme.required_documents || []).map((doc, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 p-2 rounded-xl bg-gray-50 border border-gray-100 text-gray-700"
                    >
                      <MdCheckCircle className="text-emerald-600 shrink-0" size={16} />
                      <span className="font-medium text-[11px]">{doc}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Informational disclaimer */}
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200/70 text-[11px] text-amber-900">
                <strong>Application Note:</strong> Keep self-attested copies of your land records and
                Aadhaar-linked bank passbook ready before applying on the official portal.
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setActiveModalScheme(null)}
                className="px-4 py-2.5 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-100 transition-colors cursor-pointer"
              >
                Close
              </button>
              <a
                href={activeModalScheme.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-primary-600 hover:bg-primary-700 shadow-md transition-all flex items-center gap-2 cursor-pointer"
              >
                <span>Visit Official Scheme Portal</span>
                <MdOpenInNew size={15} />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
