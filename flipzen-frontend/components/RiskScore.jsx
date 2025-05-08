export default function RiskScore({ score, scoreNumber }) {
  // Determine color based on the score
  let color = 'bg-green-500';
  let textColor = 'text-green-700';
  
  if (typeof scoreNumber === 'number') {
    // Numeric score (0-10 scale)
    if (scoreNumber >= 7) {
      color = 'bg-red-500';
      textColor = 'text-red-700';
    } else if (scoreNumber >= 4) {
      color = 'bg-yellow-500';
      textColor = 'text-yellow-700';
    }
  } else {
    // Text score (High, Medium, Low)
    if (score === 'High') {
      color = 'bg-red-500';
      textColor = 'text-red-700';
    } else if (score === 'Medium') {
      color = 'bg-yellow-500';
      textColor = 'text-yellow-700';
    }
  }

  const percentFill = typeof scoreNumber === 'number' 
    ? (scoreNumber * 10) // scale 0-10 to 0-100%
    : score === 'High' ? 80 : score === 'Medium' ? 50 : 20;

  return (
    <div className="flex flex-col">
      {/* Risk indicator dot with label */}
      <div className="flex items-center gap-2 mb-1">
        <span className={`inline-block w-3 h-3 rounded-full ${color} shadow-sm`} />
        <span className="text-sm text-gray-700 font-medium">
          {typeof scoreNumber === 'number' 
            ? `Risk Score: ${scoreNumber.toFixed(1)}/10` 
            : `${score} Risk`}
        </span>
      </div>
      
      {/* Risk gauge */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1">
        <div 
          className={`h-2.5 rounded-full ${color}`} 
          style={{ width: `${percentFill}%` }}
        />
      </div>
    </div>
  );
} 