'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Project {
  id: string;
  title: string;
  premise: string;
}

interface Scene {
  id: string;
  scene_number: number;
  content: string;
  created_at: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function EditorPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [approvedScenes, setApprovedScenes] = useState<Scene[]>([]);
  const [currentText, setCurrentText] = useState('');
  const [sceneNumber, setSceneNumber] = useState(1);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [approveStatus, setApproveStatus] = useState('');
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);

  // Enhance state
  const [enhancedContent, setEnhancedContent] = useState('');
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [showEnhanceReview, setShowEnhanceReview] = useState(false);

  const chatBottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    fetchProject();
    fetchScenes();
  }, [projectId]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  async function fetchProject() {
    try {
      const res = await fetch(`${API}/projects/${projectId}`);
      const data = await res.json();
      setProject(data);
    } catch (err) {
      console.error('Failed to fetch project', err);
    }
  }

  async function fetchScenes() {
    try {
      const res = await fetch(`${API}/story/${projectId}`);
      const data = await res.json();
      const scenes = data.scenes || [];
      setApprovedScenes(scenes);
      setSceneNumber(scenes.length + 1);
    } catch (err) {
      console.error('Failed to fetch scenes', err);
    }
  }

  async function sendChat() {
    if (!chatInput.trim() || chatLoading) return;
    const question = chatInput.trim();
    setChatInput('');

    // Append user message first so history is current when we send
    const updatedMessages: ChatMessage[] = [...chatMessages, { role: 'user', content: question }];
    setChatMessages(updatedMessages);
    setChatLoading(true);

    const fullQuestion = currentText.trim()
      ? `Current scene draft:\n"${currentText.slice(0, 400)}${currentText.length > 400 ? '...' : ''}"\n\nWriter's question: ${question}`
      : question;

    // Build history from all messages BEFORE this new question
    // (updatedMessages includes the new user msg at the end — exclude it,
    // since the backend treats the question param as the final turn)
    const historyToSend = chatMessages.map(m => ({ role: m.role, content: m.content }));

    try {
      const res = await fetch(`${API}/bible/${projectId}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: fullQuestion,
          chat_history: historyToSend,
        }),
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (e) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Try again.' }]);
    } finally {
      setChatLoading(false);
    }
  }

  async function enhanceScene() {
    if (!currentText.trim() || isEnhancing) return;
    setIsEnhancing(true);

    try {
      const res = await fetch(`${API}/scene/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          content: currentText,
        }),
      });
      const data = await res.json();
      setEnhancedContent(data.enhanced);
      setShowEnhanceReview(true);
    } catch (e) {
      console.error('Enhance failed', e);
    } finally {
      setIsEnhancing(false);
    }
  }

  function acceptEnhancement() {
    setCurrentText(enhancedContent);
    setShowEnhanceReview(false);
    setEnhancedContent('');
  }

  function rejectEnhancement() {
    setShowEnhanceReview(false);
    setEnhancedContent('');
  }

  async function approveScene() {
    if (!currentText.trim() || approving) return;
    setApproving(true);
    setApproveStatus('Saving...');

    try {
      await fetch(`${API}/scene/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          scene_number: sceneNumber,
          content: currentText,
        }),
      });

      setApproveStatus('✓ Scene saved. Bible updating...');
      await fetchScenes();
      setCurrentText('');
      setShowEnhanceReview(false);
      setEnhancedContent('');

      setTimeout(() => setApproveStatus(''), 4000);
    } catch (e) {
      setApproveStatus('Failed to save. Try again.');
    } finally {
      setApproving(false);
    }
  }

  async function exportStory() {
    const res = await fetch(`${API}/story/${projectId}`);
    const data = await res.json();
    const scenes = data.scenes || [];
    const text = scenes.map((s: Scene) => `— Scene ${s.scene_number} —\n\n${s.content}`).join('\n\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project?.title || 'story'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)', overflow: 'hidden' }}>

      {/* Top bar */}
      <div style={{
        height: '52px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        gap: '16px',
        flexShrink: 0,
      }}>
        <button
          onClick={() => router.push('/')}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '18px', padding: '0 4px' }}
        >←</button>

        <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'var(--accent)', fontWeight: 500 }}>
          {project?.title || '...'}
        </div>

        <div style={{ flex: 1 }} />

        <div style={{ fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '1px' }}>
          SCENE {sceneNumber}
        </div>

        {approveStatus && (
          <div style={{ fontSize: '11px', color: 'var(--accent)', letterSpacing: '1px' }}>
            {approveStatus}
          </div>
        )}

        {/* Enhance button */}
        <button
          onClick={enhanceScene}
          disabled={isEnhancing || !currentText.trim() || showEnhanceReview}
          style={{
            background: 'transparent',
            border: '1px solid var(--accent)',
            color: 'var(--accent)',
            padding: '6px 18px',
            fontSize: '11px',
            letterSpacing: '2px',
            cursor: isEnhancing || !currentText.trim() || showEnhanceReview ? 'default' : 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
            opacity: !currentText.trim() || showEnhanceReview ? 0.35 : 1,
            transition: 'all 0.2s',
          }}
        >
          {isEnhancing ? 'ENHANCING...' : '✦ ENHANCE'}
        </button>

        <button
          onClick={approveScene}
          disabled={approving || !currentText.trim()}
          style={{
            background: currentText.trim() ? 'var(--accent)' : 'transparent',
            border: '1px solid var(--accent)',
            color: currentText.trim() ? 'var(--bg)' : 'var(--accent)',
            padding: '6px 18px',
            fontSize: '11px',
            letterSpacing: '2px',
            cursor: approving || !currentText.trim() ? 'default' : 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
            opacity: !currentText.trim() ? 0.4 : 1,
            transition: 'all 0.2s',
          }}
        >
          {approving ? 'SAVING...' : 'APPROVE SCENE'}
        </button>

        <button
          onClick={() => router.push(`/bible/${projectId}`)}
          style={{ background: 'none', border: '1px solid var(--border)', color: 'var(--text-muted)', padding: '6px 14px', fontSize: '11px', letterSpacing: '2px', cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace' }}
        >
          BIBLE
        </button>

        <button
          onClick={() => router.push(`/story/${projectId}`)}
          style={{ background: 'none', border: '1px solid var(--border)', color: 'var(--text-muted)', padding: '6px 14px', fontSize: '11px', letterSpacing: '2px', cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace' }}
        >
          STORY
        </button>

        <button
          onClick={exportStory}
          style={{
            background: 'none',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
            padding: '6px 14px',
            fontSize: '11px',
            letterSpacing: '2px',
            cursor: 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
          }}
        >
          EXPORT
        </button>

        <button
          onClick={() => setLeftOpen(o => !o)}
          title="Toggle scenes panel"
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '14px', padding: '0 4px' }}
        >☰</button>

        <button
          onClick={() => setRightOpen(o => !o)}
          title="Toggle chat panel"
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '14px', padding: '0 4px' }}
        >💬</button>
      </div>

      {/* Main area */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

        {/* Left panel — approved scenes */}
        {leftOpen && (
          <div style={{
            width: '240px',
            borderRight: '1px solid var(--border)',
            overflowY: 'auto',
            flexShrink: 0,
            padding: '20px 0',
          }}>
            <div style={{ fontSize: '10px', letterSpacing: '3px', color: 'var(--text-muted)', padding: '0 20px', marginBottom: '16px' }}>
              APPROVED SCENES
            </div>

            {approvedScenes.length === 0 && (
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '0 20px', lineHeight: 1.6 }}>
                No scenes yet.<br />Write and approve your first scene.
              </div>
            )}

            {approvedScenes.map(scene => (
              <div
                key={scene.id}
                style={{
                  padding: '14px 20px',
                  borderBottom: '1px solid var(--border)',
                  cursor: 'default',
                }}
              >
                <div style={{ fontSize: '10px', color: 'var(--accent)', letterSpacing: '2px', marginBottom: '6px' }}>
                  SCENE {scene.scene_number}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' }}>
                  {scene.content}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Center — writing area OR enhance review */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {showEnhanceReview ? (
            /* ── Enhance review: side-by-side ── */
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

              {/* Review header */}
              <div style={{
                padding: '14px 32px',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                gap: '24px',
                flexShrink: 0,
              }}>
                <div style={{ fontSize: '10px', letterSpacing: '3px', color: 'var(--text-muted)' }}>
                  ENHANCE REVIEW
                </div>
                <div style={{ flex: 1 }} />
                <button
                  onClick={acceptEnhancement}
                  style={{
                    background: 'var(--accent)',
                    border: '1px solid var(--accent)',
                    color: 'var(--bg)',
                    padding: '6px 20px',
                    fontSize: '11px',
                    letterSpacing: '2px',
                    cursor: 'pointer',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                >
                  ACCEPT
                </button>
                <button
                  onClick={rejectEnhancement}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    color: 'var(--text-muted)',
                    padding: '6px 20px',
                    fontSize: '11px',
                    letterSpacing: '2px',
                    cursor: 'pointer',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                >
                  REJECT
                </button>
              </div>

              {/* Side by side */}
              <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

                {/* Original */}
                <div style={{ flex: 1, borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                  <div style={{ padding: '16px 32px 8px', fontSize: '10px', letterSpacing: '3px', color: 'var(--text-muted)', flexShrink: 0 }}>
                    ORIGINAL
                  </div>
                  <div style={{
                    flex: 1,
                    overflow: 'auto',
                    padding: '8px 32px 40px',
                    fontSize: '16px',
                    lineHeight: '1.9',
                    fontFamily: 'Playfair Display, serif',
                    color: 'var(--text-muted)',
                    whiteSpace: 'pre-wrap',
                  }}>
                    {currentText}
                  </div>
                </div>

                {/* Enhanced */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                  <div style={{ padding: '16px 32px 8px', fontSize: '10px', letterSpacing: '3px', color: 'var(--accent)', flexShrink: 0 }}>
                    ENHANCED
                  </div>
                  <div style={{
                    flex: 1,
                    overflow: 'auto',
                    padding: '8px 32px 40px',
                    fontSize: '16px',
                    lineHeight: '1.9',
                    fontFamily: 'Playfair Display, serif',
                    color: 'var(--text)',
                    whiteSpace: 'pre-wrap',
                  }}>
                    {enhancedContent}
                  </div>
                </div>

              </div>
            </div>
          ) : (
            /* ── Normal writing area ── */
            <>
              <textarea
                ref={textareaRef}
                value={currentText}
                onChange={e => setCurrentText(e.target.value)}
                placeholder={`Scene ${sceneNumber}. Begin writing...`}
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  resize: 'none',
                  color: 'var(--text)',
                  fontSize: '17px',
                  lineHeight: '1.9',
                  fontFamily: 'Playfair Display, serif',
                  padding: '60px 80px',
                  caretColor: 'var(--accent)',
                }}
              />
              <div style={{
                padding: '12px 80px',
                borderTop: '1px solid var(--border)',
                fontSize: '11px',
                color: 'var(--text-muted)',
                display: 'flex',
                gap: '24px',
              }}>
                <span>{currentText.trim() ? currentText.trim().split(/\s+/).length : 0} words</span>
                <span>{currentText.length} characters</span>
              </div>
            </>
          )}
        </div>

        {/* Right panel — chat */}
        {rightOpen && (
          <div style={{
            width: '340px',
            borderLeft: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0,
          }}>
            <div style={{ fontSize: '10px', letterSpacing: '3px', color: 'var(--text-muted)', padding: '20px 20px 12px', borderBottom: '1px solid var(--border)' }}>
              STORY COLLABORATOR
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
              {chatMessages.length === 0 && (
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                  Ask anything about your story.<br /><br />
                  <span style={{ color: 'var(--border)', fontSize: '12px' }}>
                    &ldquo;What has Elena been through so far?&rdquo;<br />
                    &ldquo;I&apos;m stuck — what should happen next?&rdquo;<br />
                    &ldquo;What plot threads are unresolved?&rdquo;<br />
                    &ldquo;Suggest a direction for this scene.&rdquo;
                  </span>
                </div>
              )}

              {chatMessages.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    marginBottom: '20px',
                    animation: 'fadeIn 0.3s ease',
                  }}
                >
                  <div style={{
                    fontSize: '10px',
                    letterSpacing: '2px',
                    color: msg.role === 'user' ? 'var(--accent)' : 'var(--text-muted)',
                    marginBottom: '6px',
                  }}>
                    {msg.role === 'user' ? 'YOU' : 'COLLABORATOR'}
                  </div>
                  <div style={{
                    fontSize: '13px',
                    lineHeight: '1.7',
                    color: msg.role === 'user' ? 'var(--text)' : 'var(--text-muted)',
                    whiteSpace: 'pre-wrap',
                  }}>
                    {msg.content}
                  </div>
                </div>
              ))}

              {chatLoading && (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                  thinking...
                </div>
              )}

              <div ref={chatBottomRef} />
            </div>

            {/* Chat input */}
            <div style={{ borderTop: '1px solid var(--border)', padding: '16px' }}>
              <textarea
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChat();
                  }
                }}
                placeholder="Ask about your story... (Enter to send)"
                rows={3}
                style={{
                  width: '100%',
                  background: 'var(--surface)',
                  border: '1px solid var(--border)',
                  color: 'var(--text)',
                  fontSize: '13px',
                  fontFamily: 'JetBrains Mono, monospace',
                  padding: '10px 12px',
                  resize: 'none',
                  outline: 'none',
                  lineHeight: 1.5,
                  marginBottom: '8px',
                  boxSizing: 'border-box',
                }}
              />
              <button
                onClick={sendChat}
                disabled={chatLoading || !chatInput.trim()}
                style={{
                  width: '100%',
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  color: chatInput.trim() ? 'var(--text)' : 'var(--text-muted)',
                  padding: '8px',
                  fontSize: '11px',
                  letterSpacing: '2px',
                  cursor: chatLoading || !chatInput.trim() ? 'default' : 'pointer',
                  fontFamily: 'JetBrains Mono, monospace',
                  opacity: !chatInput.trim() ? 0.4 : 1,
                }}
              >
                {chatLoading ? 'THINKING...' : 'SEND'}
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
