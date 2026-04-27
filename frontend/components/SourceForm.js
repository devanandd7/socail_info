import { useState } from "react";

export default function SourceForm({ onCreate }) {
  const [type, setType] = useState("subreddit");
  const [name, setName] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;
    await onCreate({ type, name: name.trim() });
    setName("");
  }

  return (
    <form className="source-form" onSubmit={handleSubmit}>
      <select value={type} onChange={(e) => setType(e.target.value)}>
        <option value="subreddit">Subreddit</option>
        <option value="account">X Account</option>
      </select>
      <input
        placeholder="e.g. startups or elonmusk"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <button type="submit">Add source</button>
    </form>
  );
}
