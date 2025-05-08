import NewsCard from './NewsCard';
import EmptyState from './EmptyState';

export default function NewsList({ articles }) {
  if (!articles || articles.length === 0) {
    return <EmptyState message="No negative news found for this client." />;
  }
  return (
    <div className="flex flex-col gap-4 mt-4">
      {articles.map((article, idx) => (
        <NewsCard key={article.url || idx} article={article} />
      ))}
    </div>
  );
} 