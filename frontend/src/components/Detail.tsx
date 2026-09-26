import Link from 'next/link';
import type {Metadata} from 'next';
import {Status} from './Section';
import {ExperimentChart} from './ExperimentChart';
import {serverApi} from '../lib/server-api';

type Kind='work'|'research'|'ideas'|'experiments';
const maps:any={work:'/public/projects',research:'/public/research',ideas:'/public/ideas',experiments:'/public/experiments'};
const fields:any={
  work:[['Problem','problem'],['Motivation','motivation'],['Solution','solution'],['Architecture','architecture'],['Challenges','challenges'],['Results','results'],['What I Learned','learned'],['Future','future_work']],
  research:[['Research Question','question'],['Problem','problem'],['Existing Work','existing_work'],['Hypothesis','hypothesis'],['Methodology','methodology'],['Experiment','experiment'],['Results','results'],['Limitations','limitations'],['Future Work','future_work'],['References','references_text']],
  ideas:[['The Question','question'],['Problem','problem'],['Current Approach','current_approach'],['Proposed Concept','proposed_concept'],['Prototype','prototype_status']],
  experiments:[['Question','question'],['Hypothesis','hypothesis'],['Setup','setup'],['Tools','tools'],['Procedure','procedure'],['Data','data'],['Result','result'],['Observation','observation'],['Conclusion','conclusion'],['Next Step','next_step']]
};
const apiOrigin=(process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000/api/v1').replace(/\/api\/v1\/?$/,'');

export async function detailMetadata(kind:Kind, slug:string):Promise<Metadata>{
  const x=await serverApi<any>(`${maps[kind]}/${encodeURIComponent(slug)}`);
  const title=x?.title||'Not found';
  const description=x?.summary||x?.abstract||x?.one_line||x?.question||'Engineering portfolio content.';
  const path=`/${kind==='work'?'work':kind}/${slug}`;
  return {title,description,alternates:{canonical:path},openGraph:{title,description,type:'article',url:path}};
}

export async function Detail({kind,slug}:{kind:Kind;slug:string}){
  const x=await serverApi<any>(`${maps[kind]}/${encodeURIComponent(slug)}`);
  if(!x) return <main className="mx-auto max-w-5xl px-5 py-24"><div className="card p-7">This published record could not be found.</div></main>;
  const tech=kind==='work'?await serverApi<any[]>(`/public/projects/${x.id}/technologies`)||[]:[];
  const refs=kind==='research'?await serverApi<any[]>(`/public/research/${x.id}/references`)||[]:[];
  const data=kind==='experiments'?await serverApi<any[]>(`/public/experiments/${x.id}/data`)||[]:[];
  const media=await serverApi<any[]>(`/public/media-links/${kind==='work'?'project':kind}/${x.id}`)||[];
  const back=kind==='work'?'work':kind;
  return <main className="mx-auto max-w-5xl px-5 py-20 md:px-8">
    <Link href={`/${back}`} className="text-sm underline underline-offset-4">← Back</Link>
    <div className="mt-10"><div className="mono text-[11px] uppercase tracking-[.2em] text-[var(--muted)]">{x.public_id||x.area||x.date_label||kind}</div><h1 className="mt-3 text-5xl font-semibold tracking-[-.04em] md:text-7xl">{x.title}</h1>{x.status&&<div className="mt-5"><Status>{x.status}</Status></div>}{(x.summary||x.abstract||x.one_line)&&<p className="mt-7 max-w-3xl text-xl leading-8 text-[var(--muted)]">{x.summary||x.abstract||x.one_line}</p>}</div>
    {kind==='work'&&tech.length>0&&<section className="mt-10"><h2 className="text-sm font-medium uppercase tracking-[.15em]">Technology</h2><div className="mt-3 flex flex-wrap gap-2">{tech.map((v:any)=><span className="status" key={v.technology||v}>{v.technology||v}</span>)}</div></section>}
    {media.length>0&&<section className="mt-10"><h2 className="text-2xl font-semibold">Media</h2><div className="mt-4 grid gap-4 md:grid-cols-2">{media.map((m:any)=>{const src=`${apiOrigin}${m.url}`;return <a key={m.id} className="card overflow-hidden" href={src} target="_blank" rel="noreferrer">{m.mime_type?.startsWith('image/')?<img src={src} alt={m.filename} className="aspect-[16/10] w-full object-cover"/>:<div className="p-6"><div className="mono text-[10px] text-[var(--muted)]">{m.mime_type}</div><div className="mt-2 underline">{m.filename} →</div></div>}</a>})}</div></section>}
    {kind==='experiments'&&data.length>0&&<section className="mt-10"><h2 className="text-2xl font-semibold">Experiment data</h2><div className="mt-4"><ExperimentChart rows={data}/></div></section>}
    {kind==='research'&&refs.length>0&&<section className="mt-10"><h2 className="text-2xl font-semibold">Structured references</h2><div className="mt-4 space-y-3">{refs.map((r:any)=><article className="card p-5" key={r.id}><div className="font-medium">{r.title}</div><div className="mt-1 text-sm text-[var(--muted)]">{r.authors}{r.venue?` · ${r.venue}`:''}{r.year?` · ${r.year}`:''}</div>{r.url&&<a rel="noreferrer" className="mt-2 inline-block text-sm underline" href={r.url} target="_blank">Source →</a>}</article>)}</div></section>}
    <div className="mt-16 space-y-12">{fields[kind].map(([label,key]:string[])=>(x[key]?<section key={key}><h2 className="text-2xl font-semibold">{label}</h2><div className="prose-lite mt-4 whitespace-pre-wrap"><p>{x[key]}</p></div></section>:null))}</div>
    {kind==='ideas'&&<div className="mt-16 rounded-2xl border border-dashed border-[var(--line)] bg-white p-7"><div className="font-semibold">Want to work on this idea?</div><p className="mt-2 text-sm leading-7 text-[var(--muted)]">Public viewing does not itself grant implementation or commercial permission. Submit a collaboration request and the owner can review the exact proposed use.</p><Link className="btn btn-dark mt-5 inline-flex" href={`/collaborate?idea=${encodeURIComponent(x.public_id||x.slug)}`}>Request permission / collaborate</Link></div>}
  </main>;
}
