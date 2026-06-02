'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Scene {
  id: string;
  scene_number: number;
  content: string;
  created_at: string;
}

export default function StoryPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/projects/${projectId}`).then(r => r.json()),
      fetch(`${API}/story/${projectId}`).then(r => r.json()),
    ]).then(([proj, story]) => {
      setProject(proj);
      setScenes(story.scenes || []);
      setLoading(false);
    });
  }, [projectId]);

  function exportStory() {
    const text = scenes.map(s => `— Scene ${s.scene_number} —\n\n${s.content}`).join('\n\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project?.title || 'story'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const wordCount = scenes.reduce((acc, s) => acc + s.content.trim().split(/\s+/).length, 0);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', color: 'var(--text)' }}>

      {/* Top bar */}
      <div style={{ height: '52px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', padding: '0 32px', gap: '20px' }}>
        <button onClick={() => router.push(`/editor/${projectId}`)}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '18px' }}>←</button>
        <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--accent)' }}>{project?.title || '...'}</div>
        <div style={{ flex: 1 }} />
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '1px' }}>
          {scenes.length} scenes · {wordCount.toLocaleString()} words
        </div>
        <button onClick={() => router.push(`/bible/${projectId}`)}
          style={{ background: 'none', border: '1px solid var(--border)', color: 'var(--text-muted)', padding: '5px 14px', fontSize: '11px', letterSpacing: '2px', cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace' }}>
          BIBLE
        </button>
        <button onClick={exportStory}
          style={{ background: 'var(--accent)', border: 'none', color: 'var(--bg)', padding: '5px 14px', fontSize: '11px', letterSpacing: '2px', cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace', fontWeight: 500 }}>
          EXPORT
        </button>
      </div>

      {/* Manuscript */}
      <div style={{ maxWidth: '680px', margin: '0 auto', padding: '80px 40px' }}>
        {project && (
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h1 style={{ fontFamily: 'Playfair Display, serif', fontSize: '48px', fontWeight: 400, margin: '0 0 20px' }}>
              {project.title}
            </h1>
            {project.premise && (
              <div style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.7, fontStyle: 'italic' }}>
                {project.premise}
              </div>
            )}
          </div>
        )}

        {loading && <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Loading...</div>}

        {!loading && scenes.length === 0 && (
          <div style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: 1.8, textAlign: 'center' }}>
            No approved scenes yet.
          </div>
        )}

        {scenes.map((scene, i) => (
          <div key={scene.id} style={{ marginBottom: '72px', animation: `fadeIn 0.4s ease ${i * 0.06}s both` }}>
            <div style={{ fontSize: '10px', letterSpacing: '4px', color: 'var(--accent-dim)', marginBottom: '28px', textAlign: 'center' }}>
              — {scene.scene_number} —
            </div>
            <div style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: '18px',
              lineHeight: '1.9',
              color: 'var(--text)',
              whiteSpace: 'pre-wrap',
            }}>
              {scene.content}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}