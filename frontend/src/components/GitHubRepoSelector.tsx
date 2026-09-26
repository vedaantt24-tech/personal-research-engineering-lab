'use client';
import {useEffect,useState} from 'react';
import {api} from '../lib/api';

export function GitHubRepoSelector({username,selectedValue,onSaved}:{username:string;selectedValue:string;onSaved:(value:string)=>void}){
  const [repos,setRepos]=useState<any[]>([]); const [selected,setSelected]=useState<string[]>([]); const [msg,setMsg]=useState(''); const [loading,setLoading]=useState(false);
  useEffect(()=>{setSelected(()=>{try{const x=JSON.parse(selectedValue||'[]');return Array.isArray(x)?x:[]}catch{return []}})},[selectedValue]);
  async function discover(){
    if(!username.trim()){setMsg('Add a GitHub username to discover repositories.');return}
    setLoading(true);setMsg('');
    try{const r=await api<any>('/admin/github/repositories');setRepos(r.repositories||[]);setSelected(r.selected||[]);setMsg(`${(r.repositories||[]).length} public repositories available.`)}catch(e:any){setMsg(e.message)}finally{setLoading(false)}
  }
  async function save(){const json=JSON.stringify(selected);onSaved(json);try{await api('/admin/profile',{method:'PUT',body:JSON.stringify({github_featured_repos:json})});setMsg('Featured repository selection saved.')}catch(e:any){setMsg(e.message)}}
  function toggle(name:string){setSelected(v=>v.includes(name)?v.filter(x=>x!==name):[...v,name])}
  return <div className="mt-6 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-5">
    <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end"><div><div className="field-label">GitHub repository selection</div><p className="mt-1 text-xs leading-5 text-[var(--muted)]">Only public repositories are queried. Select which repositories the public profile may show.</p></div><div className="flex gap-2"><button className="btn" type="button" onClick={discover} disabled={loading}>{loading?'Loading…':'Discover public repos'}</button><button className="btn btn-dark" type="button" onClick={save} disabled={!repos.length}>Save selection</button></div></div>
    {repos.length>0&&<div className="mt-4 grid gap-2 md:grid-cols-2">{repos.map(r=><label key={r.name} className="flex items-start gap-3 rounded-xl border border-[var(--line)] bg-white p-3 text-sm"><input type="checkbox" checked={selected.includes(r.name)} onChange={()=>toggle(r.name)}/><span><span className="font-medium">{r.name}</span><span className="mt-1 block text-xs leading-5 text-[var(--muted)]">{r.description||'No description.'}</span></span></label>)}</div>}
    {msg&&<div className="mt-3 text-xs text-[var(--muted)]">{msg}</div>}
  </div>
}
