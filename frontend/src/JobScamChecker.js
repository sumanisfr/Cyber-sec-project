import React, { useState } from 'react';
import axios from './api';

function JobScamChecker() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const applyExample = (value) => {
    setContent(value);
    setResult(null);
    setError('');
  };

  const analyze = async () => {
    setError('');
    setResult(null);

    if (!content.trim()) {
      setError('Paste the recruiter message or job description first.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/job-scam/check', { title, content });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to analyze this job post right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">Verification Lab</span>
          <h1>Job Scam Checker</h1>
          <p>Paste a recruiter message, job post, or offer note to see whether it looks genuine or risky.</p>
        </div>
        <div className="hero-card compact">
          <strong>Checks included</strong>
          <span>Upfront payment requests, fake urgency, suspicious banking asks, and hiring process quality.</span>
        </div>
      </section>

      <section className="content-grid">
        <div className="glass-card">
          <h3>Analyze a Job Message</h3>
          <div className="mb-3">
            <label className="form-label">Role or source</label>
            <input
              className="form-control"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Frontend Intern - Example Corp"
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Job description or recruiter text</label>
            <textarea
              className="form-control text-area-lg"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste the full message here..."
            />
          </div>
          <div className="d-flex flex-wrap gap-2">
            <button className="btn btn-primary" onClick={analyze} disabled={loading}>
              {loading ? 'Checking...' : 'Check Job'}
            </button>
            <button
              className="btn btn-outline-light"
              onClick={() =>
                applyExample('Work from home. Earn $500 per day. Immediate joining. Send training fee today via UPI.')
              }
            >
              Scam Example
            </button>
            <button
              className="btn btn-outline-light"
              onClick={() =>
                applyExample(
                  'Apply on our official career page. No fee is required. Screening call and technical interview will follow.'
                )
              }
            >
              Legit Example
            </button>
          </div>
          {error && <div className="alert alert-danger mt-3">{error}</div>}
        </div>

        <div className="glass-card">
          <h3>Risk Result</h3>
          {!result ? (
            <p className="text-muted mb-0">Run a check to see the risk level, red flags, and recommended next steps.</p>
          ) : (
            <>
              <div className="risk-banner">
                <span className={`risk-pill risk-${result.risk_level?.toLowerCase()}`}>{result.risk_level} Risk</span>
                <strong>Score: {result.score}/100</strong>
              </div>
              <p className="mt-3">{result.verdict}</p>

              <h6>Red Flags</h6>
              {result.red_flags?.length ? (
                <div className="stack-list">
                  {result.red_flags.map((flag) => (
                    <div className="stack-item" key={flag.title}>
                      <strong>{flag.title}</strong>
                      <p>{flag.explanation}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No major red flags detected.</p>
              )}

              <h6 className="mt-4">Recommendations</h6>
              <div className="stack-list">
                {result.recommendations?.map((item) => (
                  <div className="stack-item" key={item}>
                    <p>{item}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}

export default JobScamChecker;
