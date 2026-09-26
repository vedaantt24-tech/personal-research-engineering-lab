import Link from 'next/link';
import {Status} from './Section';
import {serverApi} from '../lib/server-api';

type Item={id:number;title:string;summary?:string;abstract?:string;one_line?:string;question?:string;excerpt?:string;status?:string;date_label?:string;slug?:string;area?:string;public_id?:string;year?:number;authors?:string;venue?:string;visibility?:string;image_url?:string;requires_permission?:boolean};
const config:any={
  work:{endpoint:'/public/projects',detail:'/work',desc:(x:Item)=>x.summary,meta:(x:Item)=>x.status||'Project'},
  research:{endpoint:'/public/research',detail:'/research',desc:(x:Item)=>x.abstract,meta:(x:Item)=>`${x.area||'Research'} · ${x.status||''}`},
  ideas:{endpoint:'/public/ideas',detail:'/ideas',desc:(x:Item)=>x.one_line,meta:(x:Item)=>`${x.public_id||''} · ${x.status||''}`},
  experiments:{endpoint:'/public/experiments',detail:'/experiments',desc:(x:Item)=>x.question,meta:(x:Item)=>`${x.date_label||''} · ${x.status||''}`},
  publications:{endpoint:'/public/publications',detail:'/publications',desc:(x:Item)=>x.abstract,meta:(x:Item)=>`${x.year||''} · ${x.status||''}`},
  notes:{endpoint:'/public/notes',detail:'/notes',desc:(x:Item)=>x.excerpt,meta:(x:Item)=>x.status||'Note'},
};
export async function PublicCollection({kind}:{kind:keyof typeof config}){
  const c=config[kind];
  const items=(await serverApi<Item[]>(c.endpoint))||[];
  if(!items.length) return <div className="card p-7 text-[var(--muted)]">Nothing published here yet. The owner can add content from the private dashboard.</div>;
  return <div className="grid gap-5 md:grid-cols-2">{items.map(x=><Link key={x.id} href={`${c.detail}/${kind==='publications'?x.id:(x.slug||x.id)}`} className="card group overflow-hidden transition hover:-translate-y-1">{x.image_url&&<div className="aspect-[16/8] overflow-hidden border-b border-[var(--line)] bg-[var(--bg)]"><img src={x.image_url} alt={`${x.title} cover image`} loading="lazy" className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.02]"/></div>}<div className="p-6"><div className="flex items-start justify-between gap-4"><div className="mono text-[10px] uppercase tracking-[.18em] text-[var(--muted)]">{c.meta(x)}</div>{x.status&&<Status>{x.status}</Status>}</div><h3 className="mt-8 text-2xl font-semibold tracking-[-.025em]">{x.title}</h3><p className="mt-3 leading-7 text-[var(--muted)]">{c.desc(x)||''}</p>{kind==='ideas'&&x.requires_permission&&<div className="mt-4 text-xs text-[var(--muted)]">Permission required for use beyond ordinary viewing.</div>}<div className="mt-7 text-sm underline underline-offset-4">Open →</div></div></Link>)}</div>;
}
