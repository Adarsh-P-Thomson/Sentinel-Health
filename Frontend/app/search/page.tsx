"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Plus,
  X,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Database,
  TrendingUp,
  FileText,
  ExternalLink,
} from "lucide-react";

interface Source {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  description: string;
  auth_required: boolean;
}

interface SearchResult {
  total_pages_found: number;
  total_posts_extracted: number;
  results_by_source: Record<string, any>;
  errors: string[];
}

export default function SearchPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [keywords, setKeywords] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch available sources on mount
  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/sources`);
      const data = await response.json();
      setSources(data.sources.filter((s: Source) => s.enabled));
    } catch (err) {
      console.error("Failed to fetch sources:", err);
    }
  };

  const toggleSource = (sourceId: string) => {
    setSelectedSources((prev) =>
      prev.includes(sourceId)
        ? prev.filter((id) => id !== sourceId)
        : [...prev, sourceId]
    );
  };

  const addKeyword = () => {
    if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
      setKeywords([...keywords, keywordInput.trim()]);
      setKeywordInput("");
    }
  };

  const removeKeyword = (keyword: string) => {
    setKeywords(keywords.filter((k) => k !== keyword));
  };

  const executeSearch = async () => {
    if (!query.trim() || selectedSources.length === 0) {
      setError("Please enter a search query and select at least one source");
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResult(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_id: "00000000-0000-0000-0000-000000000001", // Demo project ID
          source_ids: selectedSources,
          query: query,
          keywords: keywords.length > 0 ? keywords : [query],
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setSearchResult(data);
    } catch (err: any) {
      setError(err.message || "Search failed");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-display font-bold text-2xl text-neutral-900">
                Multi-Source Search
              </h1>
              <p className="text-neutral-600 text-sm">
                Search across social media and forums for patient safety signals
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Search Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Search Query */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl border border-neutral-200 p-6"
            >
              <label className="block text-sm font-semibold text-neutral-900 mb-3">
                Search Query
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Drug-Y side effects"
                className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                onKeyPress={(e) => e.key === "Enter" && executeSearch()}
              />
            </motion.div>

            {/* Keywords */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl border border-neutral-200 p-6"
            >
              <label className="block text-sm font-semibold text-neutral-900 mb-3">
                Keywords (Optional)
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  placeholder="Add keyword..."
                  className="flex-1 px-4 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                  onKeyPress={(e) => e.key === "Enter" && addKeyword()}
                />
                <button
                  onClick={addKeyword}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {keywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm"
                  >
                    {keyword}
                    <button
                      onClick={() => removeKeyword(keyword)}
                      className="hover:bg-primary-100 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </motion.div>

            {/* Source Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl border border-neutral-200 p-6"
            >
              <label className="block text-sm font-semibold text-neutral-900 mb-4">
                Select Sources
              </label>
              <div className="grid md:grid-cols-2 gap-3">
                {sources.map((source) => (
                  <button
                    key={source.id}
                    onClick={() => toggleSource(source.id)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      selectedSources.includes(source.id)
                        ? "border-primary-600 bg-primary-50"
                        : "border-neutral-200 hover:border-primary-300"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-neutral-900">
                          {source.name}
                        </div>
                        <div className="text-sm text-neutral-600 mt-1">
                          {source.description}
                        </div>
                      </div>
                      {selectedSources.includes(source.id) && (
                        <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0 ml-2" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Search Button */}
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              onClick={executeSearch}
              disabled={isSearching || !query.trim() || selectedSources.length === 0}
              className="w-full px-6 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary-600/20"
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Execute Search
                </>
              )}
            </motion.button>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
                >
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-semibold text-red-900">Error</div>
                    <div className="text-sm text-red-700">{error}</div>
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right Column - Search Results */}
          <div className="space-y-6">
            <AnimatePresence>
              {searchResult && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="space-y-4"
                >
                  {/* Summary Stats */}
                  <div className="bg-white rounded-xl border border-neutral-200 p-6">
                    <h3 className="font-display font-semibold text-lg text-neutral-900 mb-4">
                      Search Results
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-neutral-600">
                          <Database className="w-4 h-4" />
                          <span className="text-sm">Pages Found</span>
                        </div>
                        <span className="font-semibold text-neutral-900">
                          {searchResult.total_pages_found}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-neutral-600">
                          <FileText className="w-4 h-4" />
                          <span className="text-sm">Posts Extracted</span>
                        </div>
                        <span className="font-semibold text-neutral-900">
                          {searchResult.total_posts_extracted}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Results by Source */}
                  {Object.entries(searchResult.results_by_source).map(
                    ([sourceId, result]: [string, any]) => (
                      <div
                        key={sourceId}
                        className="bg-white rounded-xl border border-neutral-200 p-6"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="font-semibold text-neutral-900 capitalize">
                            {sourceId}
                          </h4>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${
                              result.status === "completed"
                                ? "bg-green-100 text-green-700"
                                : result.status === "failed"
                                ? "bg-red-100 text-red-700"
                                : "bg-yellow-100 text-yellow-700"
                            }`}
                          >
                            {result.status}
                          </span>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-neutral-600">Pages</span>
                            <span className="font-medium text-neutral-900">
                              {result.pages_found || 0}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-neutral-600">Posts</span>
                            <span className="font-medium text-neutral-900">
                              {result.posts_extracted || 0}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-neutral-600">Duration</span>
                            <span className="font-medium text-neutral-900">
                              {result.duration_ms
                                ? `${(result.duration_ms / 1000).toFixed(2)}s`
                                : "N/A"}
                            </span>
                          </div>
                          {result.errors && result.errors.length > 0 && (
                            <div className="mt-3 p-2 bg-red-50 rounded text-xs text-red-700">
                              {result.errors.join(", ")}
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  )}

                  {/* View Details Button */}
                  <button className="w-full px-4 py-3 bg-neutral-100 text-neutral-900 rounded-lg hover:bg-neutral-200 transition-colors font-medium flex items-center justify-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    View Detailed Results
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Empty State */}
            {!searchResult && !isSearching && (
              <div className="bg-white rounded-xl border border-neutral-200 p-8 text-center">
                <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Search className="w-8 h-8 text-neutral-400" />
                </div>
                <h3 className="font-semibold text-neutral-900 mb-2">
                  No Results Yet
                </h3>
                <p className="text-sm text-neutral-600">
                  Configure your search and click "Execute Search" to begin
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
