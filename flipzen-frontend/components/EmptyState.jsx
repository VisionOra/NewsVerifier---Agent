export default function EmptyState({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <svg width="48" height="48" fill="none" viewBox="0 0 24 24" className="mb-3 text-gray-300">
        <title>No Results</title>
        <path stroke="currentColor" strokeWidth="1.5" d="M12 17v.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9Zm-4-2a4 4 0 1 1-8 0"/>
      </svg>
      <p className="text-gray-500 text-lg font-medium">{message}</p>
    </div>
  );
} 