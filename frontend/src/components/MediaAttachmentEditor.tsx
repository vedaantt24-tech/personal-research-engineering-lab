'use client';
import {useEffect,useState} from 'react';
import {api} from '../lib/api';
export function MediaAttachmentEditor({entityType,entityId}:{entityType:string;entityId:number}){
 const [media,setMedia]=useState<any[]>([]);const [selected,setSelected]=useState<number[]>([]);const [msg,setMsg]=useState('');
 useEffect(()=>{Promise.all([api<any[]>('/admin/media'),api<any[]>(`/admin/media-links/${entityType}/${entityId}`)]).then(([all,links])=>{setMedia(all);setSelected(links.map(x=>x.media_id))}).catch(e=>setMsg(e.message))},[entityType,entityId]);
 function toggle(id:number){setSelected(v=>v.includes(id)?v.filter(x=>x!==id):[...v,id])}
 async function save(){try{await api(`/admin/media-links/${entityType}/${entityId}`,{method:'PUT',body:JSON.stringify({media_ids:selected})});setMsg('Media attachments saved.')}catch(e:any){setMsg(e.message)}}
 return <div className="mt-6 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-5"><div className="field-label">Media attachments</div><p className="mt-2 text-xs leading-5 text-[var(--muted)]">Only files marked PUBLIC can appear on the public site. Private files remain stored but are not exposed by public media endpoints.</p><div className="mt-4 grid gap-2 sm:grid-cols-2">{media.map(m=><label className="flex gap-3 rounded-xl border border-[var(--line)] bg-white p-3 text-sm" key={m.id}><input type="checkbox" checked={selected.includes(m.id)} onChange={()=>toggle(m.id)}/><span className="min-w-0"><span className="block truncate">{m.filename}</span><span className="text-xs text-[var(--muted)]">#{m.id} · {m.visibility}</span></span></label>)}{!media.length&&<div className="text-sm text-[var(--muted)]">Upload media from the Media tab first.</div>}</div><button type="button" className="btn btn-dark mt-4" onClick={save} disabled={!media.length}>Save attachments</button>{msg&&<div className="mt-3 text-xs text-[var(--muted)]">{msg}</div>}</div>
}
