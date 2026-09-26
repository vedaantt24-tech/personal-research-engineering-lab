import Link from 'next/link';
import {serverApi} from '../lib/server-api';
export async function FeaturedLive(){
  const [projects,research,ideas]=await Promise.all([serverApi<any[]>('/public/projects'),serverApi<any[]>('/public/research'),serverApi<any[]>('/public/ideas')]);
  const items=[...(projects||[]).slice(0,3).map((x:any)=>({...x,kind:'Work',href:`/work/${x.slug}`,desc:x.summary})),...(research||[]).slice(0,2).map((x:any)=>({...x,kind:'Research',href:`/research/${x.slug}`,desc:x.abstract})),...(ideas||[]).slice(0,2).map((x:any)=>({...x,kind:'Idea',href:`/ideas/${x.slug}`,desc:x.one_line}))].slice(0,6);
  if(!items.length)return <div className="card p-7 text-sm text-[var(--muted)]">No featured work is published yet. Add and intentionally publish items from the owner dashboard.</div>;
  return <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{items.map((x:any)=><Link key={`${x.kind}-${x.id}`} href={x.href} className="card group p-6 transition hover:-translate-y-1"><div className="flex justify-between gap-4"><span className="mono text-[10px] uppercase tracking-[.18em] text-[var(--muted)]">{x.kind}</span>{x.status&&<span className="status">{x.status}</span>}</div><h3 className="mt-12 text-2xl font-semibold">{x.title}</h3><p className="mt-3 line-clamp-3 leading-7 text-[var(--muted)]">{x.desc}</p><div className="mt-7 text-sm underline underline-offset-4">Explore →</div></Link>)}</div>;
}
