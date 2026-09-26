'use client';
import {useEffect,useState} from 'react';
import {api} from '../lib/api';
export function ExperimentDataEditor({experimentId}:{experimentId:number}){
 const [rows,setRows]=useState<any[]>([]); const [text,setText]=useState(''); const [msg,setMsg]=useState('');
 useEffect(()=>{api<any[]>(`/admin/experiments/${experimentId}/data`).then(r=>{setRows(r);setText(r.map(x=>[x.series,x.x_label??'',x.x_value??'',x.y_value,x.unit??'',x.note??''].join(',')).join('\n'))}).catch(()=>{})},[experimentId]);
 async function save(){
  const next=text.split(/\r?\n/).map(x=>x.trim()).filter(Boolean).map(line=>{const [series,x_label,x_value,y_value,unit,note]=line.split(',').map(x=>x.trim());return {series,x_label,x_value:x_value===''?null:Number(x_value),y_value:Number(y_value),unit,note}});
  if(next.some(x=>!Number.isFinite(x.y_value)|| (x.x_value!==null&&!Number.isFinite(x.x_value)))){setMsg('Each row must have numeric y and optional numeric x values.');return}
  try{const r=await api<any[]>(`/admin/experiments/${experimentId}/data`,{method:'PUT',body:JSON.stringify({data:next})});setRows(r);setMsg(`Saved ${r.length} data points.`)}catch(e:any){setMsg(e.message)}
 }
 return <div className="mt-5 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-5"><div className="mono text-[10px] uppercase tracking-[.18em] text-[var(--muted)]">EXPERIMENT DATA</div><h4 className="mt-1 text-lg font-semibold">Numeric measurements</h4><p className="mt-2 text-xs leading-5 text-[var(--muted)]">One point per line: series,x_label,x_value,y_value,unit,note. Values are stored as measurements, not fabricated metrics.</p><textarea className="input mt-4 min-h-40 font-mono text-xs" value={text} onChange={e=>setText(e.target.value)} placeholder={'default,Trial 1,1,0.42,V,'}/><button className="btn btn-dark mt-3" onClick={save}>Save measurements</button>{msg&&<div className="mt-3 text-sm text-[var(--muted)]">{msg}</div>}{rows.length>0&&<div className="mt-4 text-xs text-[var(--muted)]">{rows.length} stored points.</div>}</div>
}
