export default function PostCard({ post }) {
  const ts = new Date(post.timestamp).toLocaleString();

  return (
    <article className="post-card">
      <div className="post-meta">
        <span className={`badge ${post.platform}`}>{post.platform}</span>
        <span>{post.author}</span>
        <span>{ts}</span>
      </div>

      <p className="content">{post.content}</p>

      <div className="post-footer">
        <span>Engagement: {Math.round(post.engagement_score)}</span>
        <span>Rank: {post.rank_score.toFixed(3)}</span>
        <span>AI: {post.ai_category || "N/A"}</span>
        <a href={post.url} target="_blank" rel="noreferrer">
          Open
        </a>
      </div>
    </article>
  );
}
