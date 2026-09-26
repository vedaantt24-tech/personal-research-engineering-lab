'use client';
import {useMemo} from 'react';

const LONG_KEYS=new Set(['bio','tagline','current_learning','research_interests','problem_solving','summary','abstract','problem','motivation','solution','architecture','challenges','results','learned','future_work','question','existing_work','hypothesis','methodology','experiment','limitations','references_text','one_line','current_approach','proposed_concept','how_it_works','required_technology','assumptions','risks','open_questions','applications','setup','tools','procedure','data','result','observation','conclusion','next_step','excerpt','body','owner_notes']);
const SELECTS:any={
 state:['DRAFT','REVIEW','PUBLISHED','ARCHIVED'],
 visibility:['PUBLIC','UNLISTED','PRIVATE','CONFIDENTIAL'],
 classification:['PUBLIC','PROFESSIONAL','RESEARCH','EXPERIMENTAL','CONCEPT','DRAFT','PRIVATE','CONFIDENTIAL'],
 status:['Idea','Proposal','In Progress','Experiment','Preprint','Submitted','Under Review','Published','THOUGHT','CONCEPT','RESEARCHING','EXPERIMENTING','PROTOTYPING','TESTED','DEVELOPING','FAILED','PARTIAL','PROMISING','SUCCESSFUL','NEEDS_VALIDATION','In Development'],
 prototype_status:['None','Planned','Partial','Working'],
};
function labelize(k:string){return k.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}
export function RecordEditor({value,onChange,readOnly=[]}:{value:any,onChange:(next:any)=>void,readOnly?:string[]}){
  const keys=useMemo(()=>Object.keys(value||{}).filter(k=>!['id','created_at','updated_at','sha256','acceptance_ip_hash'].includes(k) && !readOnly.includes(k)),[value,readOnly]);
  function set(k:string,v:any){onChange({...value,[k]:v})}
  return <div className="grid gap-4 md:grid-cols-2">
    {keys.map(k=>{
      const v=value[k]; const select=SELECTS[k];
      if(typeof v==='boolean') return <label key={k} className="card flex items-center gap-3 p-4 text-sm"><input type="checkbox" checked={v} onChange={e=>set(k,e.target.checked)}/><span>{labelize(k)}</span></label>;
      if(select) return <label key={k} className="block"><span className="field-label">{labelize(k)}</span><select className="input" value={String(v??'')} onChange={e=>set(k,e.target.value)}>{select.map((x:string)=><option key={x} value={x}>{x}</option>)}</select></label>;
      if(typeof v==='number') return <label key={k} className="block"><span className="field-label">{labelize(k)}</span><input className="input" type="number" value={v??''} onChange={e=>set(k,e.target.value===''?null:Number(e.target.value))}/></label>;
      const long=LONG_KEYS.has(k) || String(v??'').length>180;
      return <label key={k} className={`${long?'md:col-span-2':''} block`}><span className="field-label">{labelize(k)}</span>{long?<textarea className="input min-h-28" value={String(v??'')} onChange={e=>set(k,e.target.value)}/>:<input className="input" value={String(v??'')} onChange={e=>set(k,e.target.value)}/>}</label>
    })}
  </div>
}
