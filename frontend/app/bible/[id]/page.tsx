'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface BibleFact {
  id: string;
  category: string;
  content: any;
  status: string;
}

export default function BiblePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [facts, setFacts] = useState<BibleFact[]>([]);
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/projects/${projectId}`).then(r => r.json()),
      fetch(`${API}/bible/${projectId}`).then(r => r.json()),
    ]).then(([proj, bible]) => {
      setProject(proj);
      setFacts(bible.bible || []);
      setLoading(false);
    });
  }, [projectId]);

  const characters = facts.filter(f => f.category === 'character');
  const worldFacts = facts.filter(f => f.category === 'world');
  const plotThreads = facts.filter(f => f.category === 'plot_thread');
  const established = facts.filter(f => f.category === 'established_fact');

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', color: 'var(--text)' }}>

      {/* Top bar */}
      <div style={{ height: '52px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', padding: '0 32px', gap: '20px' }}>
        <button onClick={() => router.push(`/editor/${projectId}`)}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '18px' }}>←</button>
        <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--accent)' }}>{project?.title || '...'}</div>
        <div style={{ flex: 1 }} />
        <button onClick={() => router.push(`/story/${projectId}`)}
          style={{ background: 'none', border: '1px solid var(--border)', color: 'var(--text-muted)', padding: '5px 14px', fontSize: '11px', letterSpacing: '2px', cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace' }}>
          STORY
        </button>
      </div>

      <div style={{ maxWidth: '960px', margin: '0 auto', padding: '60px 40px' }}>
        <div style={{ fontSize: '11px', letterSpacing: '4px', color: 'var(--accent)', marginBottom: '12px' }}>STORY BIBLE</div>
        <h1 style={{ fontFamily: 'Playfair Display, serif', fontSize: '40px', fontWeight: 400, margin: '0 0 60px' }}>
          {loading ? 'Loading...' : `${facts.length} facts extracted`}
        </h1>

        {/* Characters */}
        {characters.length > 0 && (
          <section style={{ marginBottom: '60px' }}>
            <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--text-muted)', marginBottom: '24px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              CHARACTERS — {characters.length}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
              {characters.map(f => (
                <div key={f.id} style={{ border: '1px solid var(--border)', padding: '24px', background: 'var(--surface)' }}>
                  <div style={{ fontFamily: 'Playfair Display, serif', fontSize: '20px', marginBottom: '16px', color: 'var(--text)' }}>
                    {f.content?.name || 'Unknown'}
                  </div>
                  {Object.entries(f.content || {}).filter(([k]) => k !== 'name').map(([k, v]) => (
                    v ? (
                      <div key={k} style={{ marginBottom: '10px' }}>
                        <div style={{ fontSize: '10px', letterSpacing: '2px', color: 'var(--accent-dim)', marginBottom: '3px' }}>{k.toUpperCase()}</div>
                        <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.6 }}>{String(v)}</div>
                      </div>
                    ) : null
                  ))}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Plot threads */}
        {plotThreads.length > 0 && (
          <section style={{ marginBottom: '60px' }}>
            <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--text-muted)', marginBottom: '24px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              PLOT THREADS — {plotThreads.length}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {plotThreads.map(f => (
                <div key={f.id} style={{ border: '1px solid var(--border)', padding: '20px 24px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                  <div style={{
                    fontSize: '10px', letterSpacing: '1px', padding: '3px 8px', border: '1px solid',
                    borderColor: f.content?.status === 'closed' ? 'var(--text-muted)' : 'var(--accent)',
                    color: f.content?.status === 'closed' ? 'var(--text-muted)' : 'var(--accent)',
                    whiteSpace: 'nowrap', marginTop: '2px',
                  }}>
                    {(f.content?.status || 'open').toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', color: 'var(--text)', marginBottom: '8px', lineHeight: 1.5 }}>{f.content?.thread}</div>
                    {f.content?.clues?.length > 0 && (
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        Clues: {f.content.clues.join(' · ')}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* World facts */}
        {worldFacts.length > 0 && (
          <section style={{ marginBottom: '60px' }}>
            <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--text-muted)', marginBottom: '24px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              WORLD — {worldFacts.length}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {worldFacts.map(f => (
                <div key={f.id} style={{ padding: '14px 20px', borderLeft: '2px solid var(--border)', fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {f.content?.fact || JSON.stringify(f.content)}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Established facts */}
        {established.length > 0 && (
          <section style={{ marginBottom: '60px' }}>
            <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--text-muted)', marginBottom: '24px', paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>
              ESTABLISHED FACTS — {established.length}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {established.map(f => (
                <div key={f.id} style={{ padding: '14px 20px', borderLeft: '2px solid var(--accent-dim)', fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {f.content?.fact || JSON.stringify(f.content)}
                </div>
              ))}
            </div>
          </section>
        )}

        {!loading && facts.length === 0 && (
          <div style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: 1.8 }}>
            No facts extracted yet. Approve your first scene to populate the bible.
          </div>
        )}
      </div>
    </div>
  );
}