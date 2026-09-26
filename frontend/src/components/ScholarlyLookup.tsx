'use client';
import {useState} from 'react';
import {api} from '../lib/api';
export function ScholarlyLookup({onUse}:{onUse:(data:any)=>void}){
 const [doi,setDoi]=useState('');const [msg,setMsg]=useState('');const [busy,setBusy]=useState(false);
 async function lookup(){setBusy(true);setMsg('');try{const r=await api<any>(`/admin/scholarly/doi/${encodeURIComponent(doi.trim())}`);onUse(r);setMsg(`Found metadata from ${r.source}. Review it before saving.`)}catch(e:any){setMsg(e.message)}finally{setBusy(false)}}
 return <div className="mb-5 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-4"><div className="field-label">Optional DOI metadata lookup</div><div className="mt-3 flex flex-col gap-2 sm:flex-row"><input className="input" placeholder="10.xxxx/xxxxx" value={doi} onChange={e=>setDoi(e.target.value)}/><button type="button" className="btn" onClick={lookup} disabled={busy||!doi.trim()}>{busy?'Looking up…':'Lookup Crossref'}</button></div>{msg&&<div className="mt-2 text-xs leading-5 text-[var(--muted)]">{msg}</div>}</div>
}
