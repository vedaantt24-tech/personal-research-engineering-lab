'use client';
import {useEffect,useState} from 'react';
import {api} from '../lib/api';

export function RevisionPanel({collection,itemId,onRestored}:{collection:string;itemId:number;onRestored?:()=>void}){
  const [rows,setRows]=useState<any[]>([]); const [msg,setMsg]=useState(''); const [busy,setBusy]=useState(false);
  async function load(){try{setRows(await api<any[]>(`/admin/content/${collection}/${itemId}/revisions`));}catch(e:any){setMsg(e.message)}}
  useEffect(()=>{load()},[collection,itemId]);
  async function restore(revisionId:number){
    if(!confirm('Restore this revision? This creates a new revision and does not rewrite history. A previously public revision cannot be restored directly to PUBLIC.')) return;
    setBusy(true); setMsg('');
    try{await api(`/admin/content/${collection}/${itemId}/restore/${revisionId}`,{method:'POST'});await load();setMsg(`Revision #${revisionId} restored as a new version.`);onRestored?.();}
    catch(e:any){setMsg(e.message)} finally{setBusy(false)}
  }
  return <div className="mt-6 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-5">
    <div className="flex items-end justify-between gap-3"><div><div className="field-label">Revision history</div><p className="mt-1 text-xs leading-5 text-[var(--muted)]">History is append-only. Restoring creates a new revision rather than overwriting the old one.</p></div><span className="status">{rows.length} versions</span></div>
    <div className="mt-4 space-y-2">{rows.map(r=><div key={r.id} className="rounded-xl border border-[var(--line)] bg-white p-4">
      <div className="flex flex-col justify-between gap-3 sm:flex-row"><div><div className="font-medium">Version {r.version_no}</div><div className="text-xs text-[var(--muted)]">{r.actor_email} · {r.change_note||'No change note'}</div></div><button className="btn" disabled={busy} onClick={()=>restore(r.id)}>Restore</button></div>
      <div className="mt-3 text-[10px] font-mono text-[var(--muted)]">{new Date(r.created_at).toLocaleString()} · revision #{r.id}</div>
    </div>)}{!rows.length&&<div className="text-sm text-[var(--muted)]">No revision history yet.</div>}</div>
    {msg&&<div className="mt-3 text-xs text-[var(--muted)]">{msg}</div>}
  </div>
}
