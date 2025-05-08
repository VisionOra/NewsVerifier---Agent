import RiskScore from './RiskScore';

export default function NewsCard({ finding }) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6 mb-4 flex flex-col gap-2 border border-gray-100 hover:shadow-lg transition">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{finding.source}</span>
        <span className="text-xs text-gray-400">{finding.published_at}</span>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-1">{finding.type}</h3>
      <p className="text-gray-600 mb-2 line-clamp-3">{finding.description}</p>
      
      <div className="flex justify-between items-center gap-3 mt-2">
        <div className="flex gap-4">
          <div>
            <span className="text-xs text-gray-500">Severity</span>
            <div className="flex items-center gap-1">
              <span className="text-base font-semibold text-gray-700">{finding.severity}/10</span>
            </div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Confidence</span>
            <div className="flex items-center gap-1">
              <span className="text-base font-semibold text-gray-700">{finding.confidence}/10</span>
            </div>
          </div>
        </div>
        
        <a 
          href={finding.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:underline"
        >
          View Source →
        </a>
      </div>
    </div>
  );
} 