import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowLeft, Eye, EyeOff, Loader2, X } from 'lucide-react';
import './style.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const API = `${API_BASE_URL}/api/v1`;
const SESSION_KEY = 'resume_ai_session';

function formatApiError(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) return data.detail.map((d) => `${Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : 'field'}: ${d.msg}`).join(' | ');
  if (typeof data.message === 'string') return data.message;
  return fallback;
}
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(formatApiError(data, `Request failed: ${res.status}`));
  return data;
}
function saveSession(session) { session ? localStorage.setItem(SESSION_KEY, JSON.stringify(session)) : localStorage.removeItem(SESSION_KEY); }
function loadSession() { try { return JSON.parse(localStorage.getItem(SESSION_KEY)); } catch { return null; } }
function displayName(name) { const raw = (name || 'Candidate').trim(); return raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : 'Candidate'; }
function LogoMark({ onClick }) { return <button className="logo-mark" aria-label="AI Resume Intelligence home" onClick={onClick} type="button">AIR</button>; }
function BackButton({ onClick }) { return <button className="back-link" onClick={onClick} type="button"><ArrowLeft size={16}/> Back</button>; }
function CenterLogo({ onHome }) { return <div className="center-logo"><LogoMark onClick={onHome} /></div>; }
function PortalNav({ isGuest, tab, setTab, goAuth, logout }) {
  return <div className="top-actions">
    <button className={tab === 'workspace' ? 'active' : ''} onClick={() => setTab('workspace')}>Workspace</button>
    {!isGuest && <button className={tab === 'logs' ? 'active' : ''} onClick={() => setTab('logs')}>Application Logs</button>}
    {isGuest ? <button className="secondary-small" onClick={goAuth}>Login / Register</button> : <button className="secondary-small" onClick={logout}>Logout</button>}
  </div>;
}

function Landing({ session, onGuest, onAuth, onPortal }) {
  const words = ['ATS Score', 'Resume Tailoring', 'Cover Letters', 'Recruiter Email', 'LinkedIn Message', 'Interview Prep', 'Application Logs', 'PDF Upload', 'DOCX Upload', 'Job Match', 'Keyword Gap'];
  return <main className="landing-page">
    <section className="hero-card">
      <div className="floating-words" aria-hidden="true">{words.map((word, i) => <span key={word} className={`word word-${i}`}>{word}</span>)}</div>
      <div className="hero-brand"><LogoMark onClick={()=>{}}/><h2>AI Resume Intelligence</h2></div>
      <h1>Build a stronger application package in minutes.</h1>
      <div className="hero-actions">
        {session ? <button className="primary" onClick={onPortal}>Go to Candidate Portal</button> : <button className="primary" onClick={onAuth}>Login / Register</button>}
        <span className="tooltip-wrap"><button className="secondary" onClick={onGuest}>Continue as Guest</button><span className="tooltip">Guest mode generates packages but does not save application history.</span></span>
      </div>
    </section>
  </main>;
}

function AuthPanel({ setSession, onAuthenticated, onGuest, onBack }) {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [identifier, setIdentifier] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [fieldError, setFieldError] = useState({ username: '', identifier: '', email: '', password: '' });
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);
  function clearMessages(){ setFieldError({ username: '', identifier: '', email: '', password: '' }); setFormError(''); }
  function switchMode(next){ setMode(next); clearMessages(); }
  function validate(){
    const err = { username: '', identifier: '', email: '', password: '' };
    if (mode === 'register') {
      if (!username.trim()) err.username = 'Username is required.'; else if (username.trim().length < 3) err.username = 'Use at least 3 characters.';
      if (!email.trim()) err.email = 'Email is required.'; else if (!/^\S+@\S+\.\S+$/.test(email.trim())) err.email = 'Enter a valid email address.';
      if (!password) err.password = 'Password is required.'; else if (password.length < 6) err.password = 'Use at least 6 characters.';
    } else {
      if (!identifier.trim()) err.identifier = 'Email or username is required.';
      if (!password) err.password = 'Password is required.';
    }
    setFieldError(err); return !Object.values(err).some(Boolean);
  }
  async function submit(){
    clearMessages(); if (!validate()) return; setLoading(true);
    try {
      const payload = mode === 'register' ? { username: username.trim(), email: email.trim(), password } : { identifier: identifier.trim(), password };
      const data = await apiFetch(`/auth/${mode}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const session = { token: data.access_token, username: data.username || username || identifier, email: data.email || email };
      saveSession(session); setSession(session); onAuthenticated();
    } catch (err) {
      const msg = err.message || 'Something went wrong.';
      if (msg.toLowerCase().includes('username')) setFieldError(p => ({ ...p, username: msg, identifier: msg }));
      else if (msg.toLowerCase().includes('email') || msg.toLowerCase().includes('account')) setFieldError(p => ({ ...p, email: msg, identifier: msg }));
      else if (msg.toLowerCase().includes('password') || msg.toLowerCase().includes('credential')) setFieldError(p => ({ ...p, password: msg }));
      else setFormError(msg);
    } finally { setLoading(false); }
  }
  function guest(){ saveSession(null); setSession(null); onGuest(); }
  return <main className="auth-page">
    <BackButton onClick={onBack}/>
    <CenterLogo onHome={onBack} />
    <section className="card auth-card">
      <div className="section-title"><h2>Candidate Access</h2><span>Secure workspace</span></div>
      <div className="toggle"><button className={mode==='login'?'active':''} onClick={()=>switchMode('login')}>Login</button><button className={mode==='register'?'active':''} onClick={()=>switchMode('register')}>Register</button></div>
      {mode === 'register' && <div className="field-wrap"><input className={fieldError.username?'input-error':''} value={username} onChange={e=>{setUsername(e.target.value); clearMessages();}} placeholder="Username" autoComplete="username" />{fieldError.username && <div className="field-message">{fieldError.username}</div>}</div>}
      {mode === 'register'
        ? <div className="field-wrap"><input className={fieldError.email?'input-error':''} value={email} onChange={e=>{setEmail(e.target.value); clearMessages();}} placeholder="Email address" autoComplete="email" />{fieldError.email && <div className="field-message">{fieldError.email}</div>}</div>
        : <div className="field-wrap"><input className={fieldError.identifier?'input-error':''} value={identifier} onChange={e=>{setIdentifier(e.target.value); clearMessages();}} placeholder="Email address or username" autoComplete="username" />{fieldError.identifier && <div className="field-message">{fieldError.identifier}</div>}</div>}
      <div className="field-wrap password-wrap"><input className={fieldError.password?'input-error':''} value={password} type={showPassword?'text':'password'} onChange={e=>{setPassword(e.target.value); clearMessages();}} placeholder="Password" autoComplete={mode==='login'?'current-password':'new-password'} onKeyDown={e=>{if(e.key==='Enter') submit();}}/><button className="eye-button" onClick={()=>setShowPassword(!showPassword)} type="button" aria-label={showPassword?'Hide password':'Show password'}>{showPassword?<EyeOff size={19}/>:<Eye size={19}/>}</button>{fieldError.password && <div className="field-message">{fieldError.password}</div>}</div>
      {formError && <div className="form-error">{formError}</div>}
      <div className="auth-actions"><button className="primary" onClick={submit} disabled={loading}>{loading && <Loader2 className="spin" size={18}/>} {mode==='login'?'Login':'Create Account'}</button><button className="text-button" onClick={guest}>Continue as Guest</button></div>
    </section>
  </main>;
}

function UploadBox({ label, onText }) {
  const [status,setStatus] = useState('');
  async function upload(file){
    if (!file) return; setStatus(`Reading ${file.name}...`);
    const form = new FormData(); form.append('file', file);
    try { const data = await apiFetch('/documents/extract-text', { method: 'POST', body: form }); onText(data.text); setStatus(`Loaded ${data.characters.toLocaleString()} characters from ${data.filename}`); }
    catch (err) { setStatus(err.message); }
  }
  return <div className="upload-box"><label>{label}</label><input type="file" accept=".pdf,.docx,.txt" onChange={e=>upload(e.target.files?.[0])}/><small>{status || 'Upload PDF, DOCX, or TXT, or paste text below.'}</small></div>;
}
function TextBlock({ title, value }) {
  if (!value) return null;
  const text = Array.isArray(value) ? value.map((v,i)=>`${i+1}. ${typeof v==='string'?v:JSON.stringify(v)}`).join('\n') : String(value);
  return <div className="result-block"><h3>{title}</h3><pre>{text}</pre></div>;
}
function formatElapsed(ms) {
  if (!ms) return "";
  const seconds = ms / 1000;
  return seconds < 60 ? `${seconds.toFixed(1)}s` : `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}
function ResultsPanel({ result, elapsedMs }) {
  const pkg = result?.package || {}; const links = result?.interview_preparation_links || [];
  if (!result) return null;
  return <section className="card result-card"><div className="result-title-row"><h1>Tailored Application Package</h1>{elapsedMs ? <span>Generated in {formatElapsed(elapsedMs)}</span> : null}</div>{result?.provider_error && <div className="warning">Generated with local fallback because Ollama/cloud AI was unavailable. Details: {result.provider_error}</div>}<div className="score-row"><div><span>Uploaded Resume ATS</span><strong>{result?.ats_score_uploaded_resume}</strong></div><div><span>Tailored Resume ATS</span><strong>{result?.ats_score_tailored_resume}</strong></div><div><span>Keyword Match</span><strong>{result?.keyword_score}</strong></div></div><TextBlock title="ATS-Friendly Resume" value={pkg.ats_friendly_resume || pkg.raw_generation}/><TextBlock title="Cover Letter" value={pkg.cover_letter}/><TextBlock title="Recruiter Email" value={pkg.recruiter_email}/><TextBlock title="LinkedIn Message" value={pkg.linkedin_message}/><TextBlock title="Top Interview Questions" value={pkg.interview_questions}/><div className="result-block"><h3>Useful Interview Preparation Links</h3><ul className="link-list">{links.map((l,i)=><li key={i}><a href={l.url} target="_blank" rel="noreferrer">{l.label}</a></li>)}</ul></div></section>;
}

function ApplicationLogs({ onWorkspace }) {
  const [logs,setLogs] = useState([]);
  const [selected,setSelected] = useState(null);
  const [tab,setTab] = useState('summary');
  const [editing,setEditing] = useState(null);
  async function refresh(){ try { setLogs(await apiFetch('/applications')); } catch { setLogs([]); } }
  useEffect(()=>{ refresh(); }, []);
  async function openLog(id){ const data = await apiFetch(`/applications/${id}`); setSelected(data); setTab('summary'); }
  async function saveEdit(){ await apiFetch(`/applications/${editing.id}`, { method:'PATCH', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ company: editing.company, title: editing.title, status: editing.status }) }); setEditing(null); refresh(); }
  const summaryText = (log) => log.summary || log.notes || 'Tailored package generated.';
  return <>
    <section className="card logs-card"><div className="logs-title"><h2>Application Tracker</h2><button className="secondary" onClick={onWorkspace}>Back to Workspace</button></div><span className="badge">Auto-generated from Analyze + Tailor</span><div className="table"><div className="row head"><span>Company</span><span>Title</span><span>Status</span><span>Summary</span><span>Action</span></div>{logs.length===0 && <div className="row empty"><span>No applications yet. Run Analyze + Tailor to create your first log.</span></div>}{logs.map(log=><div className="row" key={log.id}><span>{log.company || 'Company not specified'}</span><span>{log.title || 'Untitled role'}</span><span>{log.status}</span><span>{summaryText(log)}</span><span className="actions"><button className="small-button" onClick={()=>openLog(log.id)}>View</button><button className="small-button secondary-small" onClick={()=>setEditing(log)}>Edit</button></span></div>)}</div></section>
    {editing && <div className="modal" onMouseDown={()=>setEditing(null)}><div className="modal-card edit-modal" onMouseDown={e=>e.stopPropagation()}><button className="close" onClick={()=>setEditing(null)}><X size={22}/></button><h2>Edit Application Log</h2><label className="edit-label">Company</label><input value={editing.company||''} onChange={e=>setEditing({...editing, company:e.target.value})} placeholder="Company"/><label className="edit-label">Title</label><input value={editing.title||''} onChange={e=>setEditing({...editing, title:e.target.value})} placeholder="Title"/><label className="edit-label">Status</label><select value={editing.status||'draft'} onChange={e=>setEditing({...editing, status:e.target.value})}><option value="draft">draft</option><option value="applied">applied</option><option value="interviewing">interviewing</option><option value="offer">offer</option><option value="rejected">rejected</option></select><button className="primary" onClick={saveEdit}>Save Changes</button></div></div>}
    {selected && <div className="modal" onMouseDown={()=>setSelected(null)}><div className="modal-card" onMouseDown={e=>e.stopPropagation()}><button className="close" onClick={()=>setSelected(null)}><X size={22}/></button><h2>{selected.title || 'Application Log'}</h2><p>{selected.company || 'Company not specified'} · {selected.status}</p><div className="toggle tabs"><button className={tab==='summary'?'active':''} onClick={()=>setTab('summary')}>Summary</button><button className={tab==='resume'?'active':''} onClick={()=>setTab('resume')}>Resume Used</button><button className={tab==='job'?'active':''} onClick={()=>setTab('job')}>Job Description</button></div>{tab==='summary'?<div className="modal-package"><TextBlock title="ATS-Friendly Resume" value={selected.result?.package?.ats_friendly_resume}/><TextBlock title="Cover Letter" value={selected.result?.package?.cover_letter}/><TextBlock title="Recruiter Email" value={selected.result?.package?.recruiter_email}/><TextBlock title="LinkedIn Message" value={selected.result?.package?.linkedin_message}/><TextBlock title="Top Interview Questions" value={selected.result?.package?.interview_questions}/><div className="result-block"><h3>Useful Interview Preparation Links</h3><ul className="link-list">{(selected.result?.interview_preparation_links||[]).map((l,i)=><li key={i}><a href={l.url} target="_blank" rel="noreferrer">{l.label}</a></li>)}</ul></div></div>:tab==='resume'?<pre>{selected.resume_text}</pre>:<pre>{selected.job_description}</pre>}</div></div>}
  </>;
}

function guessTitle(jd){
  const text = (jd || '').replace(/\s+/g, ' ').trim();
  const roles = ['Backend Engineer','Back-End Developer','Python Developer','Python Engineer','Software Engineer','Full-Stack Engineer','Full-Stack Developer','Frontend Engineer','Front-End Developer','Data Engineer','Machine Learning Engineer','DevOps Engineer','Cloud Engineer','GenAI Engineer','AI Engineer'];
  const lower = text.toLowerCase();
  for (const role of roles) {
    if (lower.includes(role.toLowerCase())) return role;
  }
  const explicit = text.match(/(?:job title|position|title|role)[:\-]\s*([^|•.]{3,80})/i);
  if (explicit) return explicit[1].trim();
  const looking = text.match(/(?:looking for|hiring|seeking)\s+(?:a|an)?\s*([^\.]{3,120})/i);
  if (looking) {
    const cleaned = looking[1]
      .replace(/^(talented|experienced|senior|junior|intermediate|strong)\s+/i, '')
      .split(/\s+(?:to|who|with|for|that)\s+/i)[0]
      .trim();
    if (cleaned.length >= 3 && cleaned.length <= 70) return cleaned.replace(/\b\w/g, c => c.toUpperCase());
  }
  return 'Target Role';
}
function guessCompany(jd){ const m=(jd||'').match(/(?:company|at)\s+([A-Z][A-Za-z0-9& .-]{2,40})/); return m ? m[1].trim() : ''; }
function Workspace({ isGuest, session, setSession, goAuth, goBack }) {
  const [tab,setTab] = useState('workspace');
  const [resume,setResume] = useState('');
  const [jd,setJd] = useState('');
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState('');
  const [result,setResult] = useState(null);
  const [elapsedMs,setElapsedMs] = useState(null);
  const username = isGuest ? 'Guest' : displayName(session?.username || 'Candidate');
  async function tailor(){
    setError(''); setResult(null); setElapsedMs(null); if (!resume.trim() || !jd.trim()) { setError('Please provide both a resume and job description.'); return; }
    setLoading(true);
    const startedAt = performance.now();
    try {
      const candidate = await apiFetch('/candidates', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ full_name: username, target_role: 'Target Role', location: '', resume_text: resume, skills: '' }) });
      const job = await apiFetch('/jobs', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ company: guessCompany(jd), title: guessTitle(jd), description: jd, seniority: '' }) });
      const generated = await apiFetch('/ai/tailor', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ candidate_id: candidate.id, job_id: job.id, provider: 'ollama', model: null, create_application_log: !isGuest }) });
      setElapsedMs(performance.now() - startedAt);
      setResult(generated);
      setTimeout(()=>document.getElementById('tailored-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    } catch (err) { setError(err.message || 'Unable to generate package.'); }
    finally { setLoading(false); }
  }
  function logout(){ saveSession(null); setSession(null); goAuth(); }
  return <main className="workspace-page"><div className="workspace-shell"><BackButton onClick={goBack}/><PortalNav isGuest={isGuest} tab={tab} setTab={setTab} goAuth={goAuth} logout={logout}/><CenterLogo onHome={goBack}/><h1>Hi, {username}!</h1>{tab==='logs' && !isGuest ? <ApplicationLogs onWorkspace={()=>setTab('workspace')}/> : <><div className="grid"><section className="card"><h2>Candidate Resume</h2><UploadBox label="Resume file" onText={setResume}/><textarea value={resume} onChange={e=>setResume(e.target.value)} placeholder="Paste resume text here, or upload a PDF/DOCX/TXT resume above..."/></section><section className="card"><h2>Job Description</h2><UploadBox label="Job description file" onText={setJd}/><textarea value={jd} onChange={e=>setJd(e.target.value)} placeholder="Paste the job description here, or upload a PDF/DOCX/TXT job description above..."/></section></div><section className="card cta"><div><h2>Generate Tailored Package</h2><p>Creates ATS score, ATS-friendly resume, cover letter, recruiter email, LinkedIn message, and interview prep links.</p></div><button className="primary analyze-button" onClick={tailor} disabled={loading || !resume || !jd}>{loading && <Loader2 className="spin" size={18}/>} {loading?'Analyzing...':'Analyze + Tailor'}</button></section>{error && <section className="alert">{error}</section>}<div id="tailored-results"><ResultsPanel result={result} elapsedMs={elapsedMs}/></div></>}</div></main>;
}

function App(){
  const [session,setSession] = useState(loadSession);
  const [view,setView] = useState('landing');
  const guest = () => { saveSession(null); setSession(null); setView('workspace-guest'); };
  if (view === 'landing') return <Landing session={session} onGuest={guest} onAuth={()=>setView('auth')} onPortal={()=>setView('workspace-auth')}/>;
  if (view === 'auth') return <AuthPanel setSession={setSession} onAuthenticated={()=>setView('workspace-auth')} onGuest={guest} onBack={()=>setView('landing')}/>;
  return <Workspace isGuest={view==='workspace-guest'} session={session} setSession={setSession} goAuth={()=>setView('auth')} goBack={()=>setView('landing')}/>;
}

createRoot(document.getElementById('root')).render(<App/>);
