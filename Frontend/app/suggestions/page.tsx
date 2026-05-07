'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPES
// ============================================================================

interface ProcessedEntry {
  entry_id: string;
  original_post_id: string;
  batch_id: string;
  processed_text: string;
  ai_suggestion: string;
  ai_info: string;
  sentiment: 'very_negative' | 'negative' | 'neutral' | 'positive' | 'very_positive';
  severity: 'low' | 'medium' | 'high' | 'critical';
  is_adverse_event: boolean;
  processed_at: string;
}

interface Category {
  category_name: string;
  category_type: 'medicine' | 'hospital' | 'drug' | 'condition' | 'symptom' | 'procedure' | 'general';
  total_entries: number;
  last_updated: string;
  tags: string[];
}

interface CategoryDetails extends Category {
  entries: ProcessedEntry[];
  summary?: {
    total_adverse_events: number;
    avg_sentiment_score: number;
    severity_breakdown: Record<string, number>;
  };
}

interface BatchStatus {
  batch_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_posts: number;
  processed_posts: number;
  processing_time_ms?: number;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function SuggestionsPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<CategoryDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [batchStatuses, setBatchStatuses] = useState<BatchStatus[]>([]);
  const [filterType, setFilterType] = useState<string>('all');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  // ============================================================================
  // FETCH CATEGORIES
  // ============================================================================

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const url = filterType === 'all' 
        ? `${API_BASE}/categories?limit=100`
        : `${API_BASE}/categories?category_type=${filterType}&limit=100`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch categories');
      
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error fetching categories:', error);
      alert('Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // FETCH CATEGORY DETAILS
  // ============================================================================

  const fetchCategoryDetails = async (categoryName: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/categories/${encodeURIComponent(categoryName)}?limit=50`);
      if (!response.ok) throw new Error('Failed to fetch category details');
      
      const data = await response.json();
      setSelectedCategory(data);
    } catch (error) {
      console.error('Error fetching category details:', error);
      alert('Failed to fetch category details');
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // PROCESS LATEST DATA (Clean & Anonymize)
  // ============================================================================

  const processLatestData = async () => {
    setProcessing(true);
    setBatchStatuses([]);

    try {
      const response = await fetch(`${API_BASE}/clean/latest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) throw new Error('Failed to start cleaning');

      const data = await response.json();
      
      // Check if there's data to process
      if (data.status === 'no_posts_to_clean') {
        alert('No unprocessed data found. Run a search first!');
        setProcessing(false);
        return;
      }

      alert(`Data cleaned successfully! ${data.message}`);
      setProcessing(false);
      fetchCategories(); // Refresh to show any new data
    } catch (error) {
      console.error('Error cleaning data:', error);
      alert('Failed to clean data');
      setProcessing(false);
    }
  };

  // ============================================================================
  // ANALYZE LATEST DATA (Send to AI Agents)
  // ============================================================================

  const analyzeLatestData = async () => {
    setAnalyzing(true);

    try {
      const response = await fetch(`${API_BASE}/analyze/latest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) throw new Error('Failed to start analysis');

      const data = await response.json();
      
      // Check if there's data to analyze
      if (data.status === 'no_posts_to_analyze') {
        alert('No cleaned posts found. Run PROCESS first!');
        setAnalyzing(false);
        return;
      }

      alert(`AI analysis started! ${data.message}`);
      setAnalyzing(false);
      // Refresh categories after a delay to show new results
      setTimeout(() => fetchCategories(), 3000);
    } catch (error) {
      console.error('Error analyzing data:', error);
      alert('Failed to start AI analysis');
      setAnalyzing(false);
    }
  };

  // ============================================================================
  // POLL BATCH STATUSES
  // ============================================================================

  const pollBatchStatuses = async (batchIds: string[]) => {
    const interval = setInterval(async () => {
      try {
        const statuses = await Promise.all(
          batchIds.map(async (batchId) => {
            const response = await fetch(`${API_BASE}/process/batch/${batchId}/status`);
            if (!response.ok) return null;
            return response.json();
          })
        );

        const validStatuses = statuses.filter(s => s !== null) as BatchStatus[];
        setBatchStatuses(validStatuses);

        // Check if all batches are completed or failed
        const allDone = validStatuses.every(s => s.status === 'completed' || s.status === 'failed');
        
        if (allDone) {
          clearInterval(interval);
          setProcessing(false);
          fetchCategories(); // Refresh categories
          alert('Processing completed!');
        }
      } catch (error) {
        console.error('Error polling batch statuses:', error);
      }
    }, 3000); // Poll every 3 seconds
  };

  // ============================================================================
  // INITIAL LOAD
  // ============================================================================

  useEffect(() => {
    fetchCategories();
  }, [filterType]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-sky-700">AI Suggestions</h1>
              <p className="text-gray-600 mt-1">Categorized insights from processed posts</p>
            </div>
            <button
              onClick={fetchCategories}
              disabled={loading}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              <svg className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Reload
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Process Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Step 1: Process Data</h2>
          <p className="text-gray-600 text-sm mb-4">
            Clean and anonymize unprocessed search results (removes PII/PHI, normalizes text)
          </p>
          <button
            onClick={processLatestData}
            disabled={processing}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {processing ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Clean & Anonymize Data
              </>
            )}
          </button>
        </div>

        {/* Analyze Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Step 2: Analyze with AI</h2>
          <p className="text-gray-600 text-sm mb-4">
            Send cleaned data to AI agents for medical entity extraction, sentiment analysis, and safety auditing
          </p>
          <button
            onClick={analyzeLatestData}
            disabled={analyzing}
            className="px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {analyzing ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Analyze with AI
              </>
            )}
          </button>

          {/* Batch Status */}
          {batchStatuses.length > 0 && (
            <div className="mt-4 space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Processing Progress:</h3>
              {batchStatuses.map((batch) => (
                <div key={batch.batch_id} className="flex items-center gap-3 text-sm">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        batch.status === 'completed' ? 'bg-green-500' :
                        batch.status === 'failed' ? 'bg-red-500' :
                        'bg-sky-500'
                      }`}
                      style={{ width: `${(batch.processed_posts / batch.total_posts) * 100}%` }}
                    />
                  </div>
                  <span className="text-gray-600 min-w-[100px]">
                    {batch.processed_posts}/{batch.total_posts} posts
                  </span>
                  <span className={`min-w-[80px] font-medium ${
                    batch.status === 'completed' ? 'text-green-600' :
                    batch.status === 'failed' ? 'text-red-600' :
                    'text-sky-600'
                  }`}>
                    {batch.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {['all', 'medicine', 'drug', 'hospital', 'condition', 'symptom', 'procedure', 'general'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                filterType === type
                  ? 'bg-sky-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>

        {/* Categories Grid */}
        {loading && categories.length === 0 ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading categories...</p>
          </div>
        ) : categories.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No categories found</h3>
            <p className="text-gray-600">Process some search results to see categories here</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {categories.map((category) => (
                <CategoryCard
                  key={category.category_name}
                  category={category}
                  onClick={() => fetchCategoryDetails(category.category_name)}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Category Details Modal */}
      {selectedCategory && (
        <CategoryDetailsModal
          category={selectedCategory}
          onClose={() => setSelectedCategory(null)}
        />
      )}
    </div>
  );
}

// ============================================================================
// CATEGORY CARD COMPONENT
// ============================================================================

function CategoryCard({ category, onClick }: { category: Category; onClick: () => void }) {
  const typeColors = {
    medicine: 'bg-blue-100 text-blue-700 border-blue-200',
    drug: 'bg-indigo-100 text-indigo-700 border-indigo-200',
    hospital: 'bg-green-100 text-green-700 border-green-200',
    condition: 'bg-red-100 text-red-700 border-red-200',
    symptom: 'bg-orange-100 text-orange-700 border-orange-200',
    procedure: 'bg-purple-100 text-purple-700 border-purple-200',
    general: 'bg-gray-100 text-gray-700 border-gray-200',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-all"
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{category.category_name}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${typeColors[category.category_type]}`}>
          {category.category_type}
        </span>
      </div>
      
      <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>{category.total_entries} entries</span>
      </div>

      {category.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {category.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
              {tag}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}

// ============================================================================
// CATEGORY DETAILS MODAL
// ============================================================================

function CategoryDetailsModal({ category, onClose }: { category: CategoryDetails; onClose: () => void }) {
  const sentimentColors = {
    very_negative: 'text-red-600 bg-red-50',
    negative: 'text-orange-600 bg-orange-50',
    neutral: 'text-gray-600 bg-gray-50',
    positive: 'text-green-600 bg-green-50',
    very_positive: 'text-emerald-600 bg-emerald-50',
  };

  const severityColors = {
    low: 'text-blue-600 bg-blue-50',
    medium: 'text-yellow-600 bg-yellow-50',
    high: 'text-orange-600 bg-orange-50',
    critical: 'text-red-600 bg-red-50',
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{category.category_name}</h2>
              <p className="text-gray-600 mt-1">{category.total_entries} total entries</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {category.entries.map((entry) => (
              <div key={entry.entry_id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${sentimentColors[entry.sentiment]}`}>
                      {entry.sentiment.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${severityColors[entry.severity]}`}>
                      {entry.severity}
                    </span>
                    {entry.is_adverse_event && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700">
                        Adverse Event
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(entry.processed_at).toLocaleDateString()}
                  </span>
                </div>

                <p className="text-gray-900 mb-3">{entry.processed_text}</p>

                <div className="space-y-2">
                  <div className="bg-sky-50 border border-sky-200 rounded p-3">
                    <p className="text-xs font-medium text-sky-700 mb-1">💡 AI Suggestion</p>
                    <p className="text-sm text-gray-700">{entry.ai_suggestion}</p>
                  </div>

                  <div className="bg-purple-50 border border-purple-200 rounded p-3">
                    <p className="text-xs font-medium text-purple-700 mb-1">ℹ️ Additional Info</p>
                    <p className="text-sm text-gray-700">{entry.ai_info}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
