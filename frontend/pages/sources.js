import { useEffect, useState } from "react";

import Layout from "../components/Layout";
import SourceForm from "../components/SourceForm";
import {
  createHashtag,
  createSource,
  deleteHashtag,
  deleteSource,
  fetchHashtags,
  fetchSources,
  updateHashtag,
  updateSource,
} from "../utils/api";

export default function SourcesPage() {
  const [sources, setSources] = useState([]);
  const [hashtags, setHashtags] = useState([]);
  const [error, setError] = useState("");
  const [editingSourceId, setEditingSourceId] = useState(null);
  const [editingHashtagId, setEditingHashtagId] = useState(null);
  const [sourceDraft, setSourceDraft] = useState({ type: "subreddit", name: "", enabled: true });
  const [newHashtagDraft, setNewHashtagDraft] = useState("");
  const [editingHashtagDraft, setEditingHashtagDraft] = useState("");

  async function loadAll() {
    try {
      setError("");
      const [sourceData, hashtagData] = await Promise.all([fetchSources(), fetchHashtags()]);
      setSources(sourceData);
      setHashtags(hashtagData);
    } catch (e) {
      setError(e.message || "Failed to load source data");
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleCreateSource(payload) {
    try {
      setError("");
      await createSource(payload);
      await loadAll();
    } catch (e) {
      setError(e.message || "Could not add source");
    }
  }

  async function handleSaveSource(sourceId) {
    try {
      setError("");
      await updateSource(sourceId, sourceDraft);
      setEditingSourceId(null);
      await loadAll();
    } catch (e) {
      setError(e.message || "Could not update source");
    }
  }

  async function handleRemoveSource(sourceId) {
    try {
      setError("");
      await deleteSource(sourceId);
      if (editingSourceId === sourceId) {
        setEditingSourceId(null);
      }
      await loadAll();
    } catch (e) {
      setError(e.message || "Could not delete source");
    }
  }

  function startEditSource(source) {
    setEditingSourceId(source.id);
    setSourceDraft({ type: source.type, name: source.name, enabled: source.enabled });
  }

  async function handleCreateHashtag(e) {
    e.preventDefault();
    if (!newHashtagDraft.trim()) return;
    try {
      setError("");
      await createHashtag({ name: newHashtagDraft.trim() });
      setNewHashtagDraft("");
      await loadAll();
    } catch (err) {
      setError(err.message || "Could not add hashtag");
    }
  }

  async function handleSaveHashtag(id) {
    try {
      setError("");
      await updateHashtag(id, { name: editingHashtagDraft.trim() });
      setEditingHashtagId(null);
      setEditingHashtagDraft("");
      await loadAll();
    } catch (err) {
      setError(err.message || "Could not update hashtag");
    }
  }

  async function handleToggleHashtag(tag) {
    try {
      setError("");
      await updateHashtag(tag.id, { enabled: !tag.enabled });
      await loadAll();
    } catch (err) {
      setError(err.message || "Could not toggle hashtag");
    }
  }

  async function handleRemoveHashtag(id) {
    try {
      setError("");
      await deleteHashtag(id);
      if (editingHashtagId === id) {
        setEditingHashtagId(null);
      }
      await loadAll();
    } catch (err) {
      setError(err.message || "Could not delete hashtag");
    }
  }

  function startEditHashtag(tag) {
    setEditingHashtagId(tag.id);
    setEditingHashtagDraft(tag.name);
  }

  return (
    <Layout title="Source Management">
      <SourceForm onCreate={handleCreateSource} />
      {error ? <p className="error">{error}</p> : null}

      <section className="admin-grid">
        <div className="admin-panel">
          <div className="section-head">
            <h2>Sources</h2>
            <span>{sources.length} total</span>
          </div>
          <div className="sources-list">
            {sources.map((source) => (
              <div className="source-item" key={source.id}>
                {editingSourceId === source.id ? (
                  <div className="source-edit">
                    <select value={sourceDraft.type} onChange={(e) => setSourceDraft((d) => ({ ...d, type: e.target.value }))}>
                      <option value="subreddit">Subreddit</option>
                      <option value="account">X Account</option>
                    </select>
                    <input
                      value={sourceDraft.name}
                      onChange={(e) => setSourceDraft((d) => ({ ...d, name: e.target.value }))}
                    />
                    <label className="toggle compact">
                      <input
                        type="checkbox"
                        checked={sourceDraft.enabled}
                        onChange={(e) => setSourceDraft((d) => ({ ...d, enabled: e.target.checked }))}
                      />
                      Enabled
                    </label>
                    <div className="action-row">
                      <button type="button" onClick={() => handleSaveSource(source.id)}>Save</button>
                      <button type="button" className="ghost" onClick={() => setEditingSourceId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <span>{source.type}</span>
                    <strong>{source.name}</strong>
                    <span>{source.enabled ? "Enabled" : "Disabled"}</span>
                    <div className="action-row">
                      <button type="button" className="ghost" onClick={() => startEditSource(source)}>Edit</button>
                      <button type="button" className="ghost danger" onClick={() => handleRemoveSource(source.id)}>Delete</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="admin-panel">
          <div className="section-head">
            <h2>Hashtags</h2>
            <span>{hashtags.filter((tag) => tag.enabled).length} active</span>
          </div>
          <form className="hashtag-form" onSubmit={handleCreateHashtag}>
            <input
              placeholder="#launch or launch"
              value={newHashtagDraft}
              onChange={(e) => setNewHashtagDraft(e.target.value)}
            />
            <button type="submit">Add hashtag</button>
          </form>
          <div className="sources-list">
            {hashtags.map((tag) => (
              <div className="source-item" key={tag.id}>
                {editingHashtagId === tag.id ? (
                  <div className="source-edit">
                    <input value={editingHashtagDraft} onChange={(e) => setEditingHashtagDraft(e.target.value)} />
                    <div className="action-row">
                      <button type="button" onClick={() => handleSaveHashtag(tag.id)}>Save</button>
                      <button type="button" className="ghost" onClick={() => setEditingHashtagId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <strong>#{tag.name}</strong>
                    <span>{tag.enabled ? "Tracking" : "Paused"}</span>
                    <div className="action-row">
                      <button type="button" className="ghost" onClick={() => handleToggleHashtag(tag)}>
                        {tag.enabled ? "Pause" : "Resume"}
                      </button>
                      <button type="button" className="ghost" onClick={() => startEditHashtag(tag)}>Edit</button>
                      <button type="button" className="ghost danger" onClick={() => handleRemoveHashtag(tag.id)}>Delete</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  );
}
