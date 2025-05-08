import RiskScore from './RiskScore';
import NewsCard from './NewsCard';

export default function DetailedReport({ data }) {
  if (!data || !data.report) return null;
  
  const { report, entity } = data;
  
  return (
    <div className="w-full">
      {/* Risk Score Section */}
      <div className="bg-white rounded-2xl shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-900">Risk Assessment</h3>
          <div className="w-32">
            <RiskScore scoreNumber={report.risk_score} />
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-xl p-4 mb-4">
          <p className="text-gray-700">{report.summary}</p>
        </div>
        
        {report.key_concerns && report.key_concerns.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Concerns</h4>
            <ul className="list-disc list-inside">
              {report.key_concerns.map((concern) => (
                <li key={concern} className="text-gray-600">{concern}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {/* Entity Information */}
      <div className="bg-white rounded-2xl shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Entity Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium text-gray-500">Full Name</h4>
            <p className="text-gray-900">{entity.full_name || entity.name}</p>
          </div>
          
          {entity.nationality && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Nationality</h4>
              <p className="text-gray-900">{entity.nationality}</p>
            </div>
          )}
          
          {entity.job_title && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Job Title</h4>
              <p className="text-gray-900">{entity.job_title}</p>
            </div>
          )}
          
          {entity.industry && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Industry</h4>
              <p className="text-gray-900">{entity.industry}</p>
            </div>
          )}
          
          {entity.location && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Location</h4>
              <p className="text-gray-900">{entity.location}</p>
            </div>
          )}
          
          {entity.description && (
            <div className="col-span-2">
              <h4 className="text-sm font-medium text-gray-500">Description</h4>
              <p className="text-gray-900">{entity.description}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Findings / News Articles */}
      {report.findings && report.findings.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Findings</h3>
          {report.findings.map((finding) => (
            <NewsCard key={finding.url || finding.type} finding={finding} />
          ))}
        </div>
      )}
      
      {/* Recommendations */}
      {report.recommendations && report.recommendations.length > 0 && (
        <div className="bg-white rounded-2xl shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h3>
          <ul className="space-y-2">
            {report.recommendations.map((recommendation) => (
              <li key={recommendation} className="text-gray-700">
                <div className="flex items-start">
                  <span className="text-blue-500 text-lg mr-2">•</span>
                  <p>{recommendation}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 