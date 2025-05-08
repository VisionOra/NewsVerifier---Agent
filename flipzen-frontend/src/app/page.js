"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [query, setQuery] = useState('');
  const [enhancedSearch, setEnhancedSearch] = useState(false);
  const [nationality, setNationality] = useState('');
  const [industry, setIndustry] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [recent, setRecent] = useState([
    'Juan Perez',
    'Maria Rodriguez',
    'Banco Central',
  ]);
  const router = useRouter();

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Build search params
    const searchParams = new URLSearchParams();
    searchParams.append('client', query);
    
    // Add enhanced search params if enabled
    if (enhancedSearch) {
      if (nationality) searchParams.append('nationality', nationality);
      if (industry) searchParams.append('industry', industry);
      if (jobTitle) searchParams.append('jobTitle', jobTitle);
    }
    
    router.push(`/results?${searchParams.toString()}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 flex flex-col items-center">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2 text-center">Negative News Media Checker</h1>
        <p className="text-gray-500 mb-6 text-center">Spot reputational risks for your clients, fast and smart.</p>
        <form onSubmit={handleSearch} className="w-full flex flex-col items-center">
          <div className="w-full mb-4">
            <input
              type="text"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-400 outline-none text-lg transition"
              placeholder="Enter client name..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
            <div className="flex items-center mt-1">
              <label className="flex items-center text-sm text-gray-500 cursor-pointer">
                <input 
                  type="checkbox" 
                  className="mr-1 h-4 w-4 text-blue-600 rounded"
                  checked={enhancedSearch}
                  onChange={() => setEnhancedSearch(!enhancedSearch)}
                />
                Enhanced Search Mode
              </label>
            </div>
          </div>

          {enhancedSearch && (
            <div className="w-full space-y-3 mb-4 animate-fadeIn">
              <input
                type="text"
                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-400 outline-none text-base"
                placeholder="Nationality"
                value={nationality}
                onChange={e => setNationality(e.target.value)}
              />
              <input
                type="text"
                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-400 outline-none text-base"
                placeholder="Industry"
                value={industry}
                onChange={e => setIndustry(e.target.value)}
              />
              <input
                type="text"
                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-400 outline-none text-base"
                placeholder="Job Title"
                value={jobTitle}
                onChange={e => setJobTitle(e.target.value)}
              />
            </div>
          )}

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-blue-600 text-white font-semibold text-lg shadow hover:bg-blue-700 transition"
          >
            Search
          </button>
        </form>
        <div className="mt-8 w-full">
          <h2 className="text-gray-700 font-medium mb-2">Recent Searches</h2>
          <div className="flex flex-wrap gap-2">
            {recent.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setQuery(item)}
                className="px-3 py-1 bg-gray-100 rounded-full text-gray-600 hover:bg-gray-200 transition text-sm"
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>
      <footer className="mt-8 text-gray-400 text-xs">Inspired by Apple & Dribbble UI</footer>
    </div>
  );
} 