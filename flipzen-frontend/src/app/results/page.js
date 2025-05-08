"use client";
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Loader from '../../../components/Loader';
import DetailedReport from '../../../components/DetailedReport';
import { searchNews } from '../services/api';

export default function Results() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const client = searchParams.get('client');
  const nationality = searchParams.get('nationality');
  const industry = searchParams.get('industry');
  const jobTitle = searchParams.get('jobTitle');
  
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!client) {
      router.push('/');
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Create search object with client data
        const clientData = {
          name: client,
        };
        
        // Add enhanced search fields if they exist
        if (nationality) clientData.nationality = nationality;
        if (industry) clientData.industry = industry;
        if (jobTitle) clientData.jobTitle = jobTitle;
        
        const data = await searchNews(clientData);
        
        if (data.status === 'error') {
          throw new Error(data.message || 'Failed to load data');
        }
        
        setReportData(data);
      } catch (err) {
        console.error('Error fetching news:', err);
        setError(`Failed to load news data: ${err.message}. Please try again later.`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [client, nationality, industry, jobTitle, router]);

  // Build a readable search description
  const buildSearchDescription = () => {
    if (!nationality && !industry && !jobTitle) return null;
    
    const parts = [];
    if (nationality) parts.push(`Nationality: ${nationality}`);
    if (industry) parts.push(`Industry: ${industry}`);
    if (jobTitle) parts.push(`Job: ${jobTitle}`);
    
    return parts.join(' • ');
  };

  const searchDescription = buildSearchDescription();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 flex flex-col items-center px-4 py-8">
      <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl p-8 flex flex-col items-center">
        <div className="w-full flex justify-between items-center mb-6">
          <button
            onClick={() => router.push('/')}
            type="button"
            className="text-blue-600 hover:underline text-sm font-medium"
          >
            ← Back to Dashboard
          </button>
          
          <div className="text-right">
            <h2 className="text-xl font-semibold text-gray-900">{client}</h2>
            {searchDescription && (
              <p className="text-gray-600 text-xs">{searchDescription}</p>
            )}
          </div>
        </div>
        
        {loading ? (
          <div className="w-full py-12">
            <Loader />
            <p className="text-center text-gray-500 mt-4">Connecting to screening API...</p>
          </div>
        ) : error ? (
          <div className="text-red-500 p-8 text-center w-full">
            <div className="mb-4 text-3xl">⚠️</div>
            <h3 className="text-xl font-semibold mb-2">Error</h3>
            <p>{error}</p>
            <button
              onClick={() => router.push('/')}
              type="button"
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
            >
              Return to Search
            </button>
          </div>
        ) : (
          <DetailedReport data={reportData} />
        )}
      </div>
    </div>
  );
} 