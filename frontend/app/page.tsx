'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Project {
  id: string;
  title: string;
  premise: string;
  created_at: string;
}

export default function Home() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [title, setTitle] = useState('');
  const [premise, setPremise] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  async function fetchProjects() {
    try {
      const res = await fetch(`${API}/projects/`);
      const data = await res.json();
      setProjects(data.projects || []);
    } catch (e) {
      console.error('Failed to fetch projects', e);
    } finally {
      setFetching(false);
    }
  }

  async function createProject() {
    if (!title.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/projects/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, premise }),
      });
      const data = await res.json();
      router.push(`/editor/${data.id}`);
    } catch (e) {
      console.error('Failed to create project', e);
      setLoading(false);
    }
  }

  return (
    <main style={{ minHeight: '100vh', padding: '60px 40px', maxWidth: '900px', margin: '0 auto' }}>

      {/* Header */}
      <div style={{ marginBottom: '80px', animation: 'fadeIn 0.6s ease' }}>
        <div style={{ color: 'var(--accent)', fontSize: '11px', letterSpacing: '4px', marginBottom: '16px', fontWeight: 500 }}>
          STORY ASSISTANT
        </div>
        <h1 style={{ fontFamily: 'Playfair Display, serif', fontSize: 'clamp(36px, 6vw, 64px)', fontWeight: 400, lineHeight: 1.1, margin: 0, color: 'var(--text)' }}>
          Your stories,<br />
          <em style={{ color: 'var(--text-muted)' }}>remembered.</em>
        </h1>
      </div>

      {/* New project button / form */}
      <div style={{ marginBottom: '60px' }}>
        {!showForm ? (
          <button
            onClick={() => setShowForm(true)}
            style={{
              background: 'transparent',
              border: '1px solid var(--accent)',
              color: 'var(--accent)',
              padding: '12px 28px',
              fontSize: '12px',
              letterSpacing: '2px',
              cursor: 'pointer',
              fontFamily: 'JetBrains Mono, monospace',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => {
              (e.target as HTMLButtonElement).style.background = 'var(--accent)';
              (e.target as HTMLButtonElement).style.color = 'var(--bg)';
            }}
            onMouseLeave={e => {
              (e.target as HTMLButtonElement).style.background = 'transparent';
              (e.target as HTMLButtonElement).style.color = 'var(--accent)';
            }}
          >
            + NEW STORY
          </button>
        ) : (
          <div style={{
            border: '1px solid var(--border)',
            padding: '32px',
            background: 'var(--surface)',
            animation: 'fadeIn 0.3s ease',
          }}>
            <div style={{ marginBottom: '20px', fontSize: '11px', letterSpacing: '3px', color: 'var(--text-muted)' }}>
              NEW STORY
            </div>
            <input
              type="text"
              placeholder="Title"
              value={title}
              onChange={e => setTitle(e.target.value)}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                borderBottom: '1px solid var(--border)',
                color: 'var(--text)',
                fontSize: '24px',
                fontFamily: 'Playfair Display, serif',
                padding: '8px 0',
                marginBottom: '24px',
                outline: 'none',
              }}
            />
            <textarea
              placeholder="One paragraph premise — what is this story about?"
              value={premise}
              onChange={e => setPremise(e.target.value)}
              rows={3}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                borderBottom: '1px solid var(--border)',
                color: 'var(--text)',
                fontSize: '14px',
                fontFamily: 'JetBrains Mono, monospace',
                fontWeight: 300,
                padding: '8px 0',
                marginBottom: '32px',
                outline: 'none',
                resize: 'none',
                lineHeight: 1.6,
              }}
            />
            <div style={{ display: 'flex', gap: '16px' }}>
              <button
                onClick={createProject}
                disabled={loading || !title.trim()}
                style={{
                  background: 'var(--accent)',
                  border: 'none',
                  color: 'var(--bg)',
                  padding: '12px 28px',
                  fontSize: '12px',
                  letterSpacing: '2px',
                  cursor: loading ? 'wait' : 'pointer',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontWeight: 500,
                  opacity: !title.trim() ? 0.4 : 1,
                }}
              >
                {loading ? 'CREATING...' : 'CREATE STORY'}
              </button>
              <button
                onClick={() => { setShowForm(false); setTitle(''); setPremise(''); }}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  color: 'var(--text-muted)',
                  padding: '12px 28px',
                  fontSize: '12px',
                  letterSpacing: '2px',
                  cursor: 'pointer',
                  fontFamily: 'JetBrains Mono, monospace',
                }}
              >
                CANCEL
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Projects list */}
      <div>
        <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--text-muted)', marginBottom: '24px' }}>
          {fetching ? 'LOADING...' : `${projects.length} STOR${projects.length === 1 ? 'Y' : 'IES'}`}
        </div>

        {projects.length === 0 && !fetching && (
          <div style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: 1.8 }}>
            No stories yet. Every novel starts somewhere.
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          {projects.map((project, i) => (
            <div
              key={project.id}
              onClick={() => router.push(`/editor/${project.id}`)}
              style={{
                padding: '24px 28px',
                border: '1px solid transparent',
                cursor: 'pointer',
                transition: 'all 0.15s',
                animation: `fadeIn 0.4s ease ${i * 0.08}s both`,
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border)';
                (e.currentTarget as HTMLDivElement).style.background = 'var(--surface)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLDivElement).style.borderColor = 'transparent';
                (e.currentTarget as HTMLDivElement).style.background = 'transparent';
              }}
            >
              <div style={{ fontFamily: 'Playfair Display, serif', fontSize: '20px', marginBottom: '8px' }}>
                {project.title}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '12px' }}>
                {project.premise || 'No premise set'}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--accent-dim)', letterSpacing: '1px' }}>
                {new Date(project.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </main>
  );
}