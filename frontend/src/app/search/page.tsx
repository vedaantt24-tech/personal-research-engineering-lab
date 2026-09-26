'use client';
import Link from 'next/link';
import {useSearchParams} from 'next/navigation';
import {Suspense,useEffect,useState} from 'react';
import {Section} from '../../components/Section';
import {api} from '../../lib/api';
function SearchInner(){
 const sp=useSearchParams(); const initial=sp.get('q')||''; const [q,setQ]=useState(initial); const [rows,setRows]=useState<any[]>([]); const [msg,setMsg]=useState('');
 useEffect(()=>{if(initial.trim().length>=2) api<any>(`/public/search?q=${encodeURIComponent(initial.trim())}`).then(x=>setRows(x.results||[])).catch(e=>setMsg(e.message));},[initial]);
 async function submit(e:React.FormEvent){e.preventDefault();const value=q.trim();if(value.length<2){setMsg('Enter at least 2 characters.');return}window.history.replaceState({},'',`/search?q=${encodeURIComponent(value)}`);try{const x=await api<any>(`/public/search?q=${encodeURIComponent(value)}`);setRows(x.results||[]);setMsg('')}catch(e:any){setMsg(e.message)}}
 return <main className="fade"><Section eyebrow="SEARCH" title="Find published work"><form onSubmit={submit} className="flex flex-col gap-3 md:flex-row"><input className="input" aria-label="Search published content" placeholder="Projects, research, ideas, experiments, publications…" value={q} onChange={e=>setQ(e.target.value)}/><button className="btn btn-dark md:w-28">Search</button></form><div className="mt-8 space-y-4">{rows.map(r=><Link href={r.url} key={`${r.type}-${r.id}`} className="card block p-6 transition hover:-translate-y-0.5"><div className="flex flex-wrap items-center justify-between gap-3"><span className="mono text-[10px] uppercase tracking-[.18em] text-[var(--muted)]">{r.type}</span>{r.status&&<span className="status">{r.status}</span>}</div><h2 className="mt-3 text-2xl font-semibold">{r.title}</h2><p className="mt-2 leading-7 text-[var(--muted)]">{r.description}</p></Link>)}{!rows.length&&<div className="card p-7 text-sm text-[var(--muted)]">{initial.trim().length>=2?'No published results found.':'Search published content by title or topic.'}</div>}{msg&&<div className="card p-4 text-sm">{msg}</div>}</div></Section></main>
}
export default function Search(){return <Suspense fallback={<main className="mx-auto max-w-7xl px-5 py-24 text-[var(--muted)]">Loading search…</main>}><SearchInner/></Suspense>}
