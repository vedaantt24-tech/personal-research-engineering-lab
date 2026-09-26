'use client';
import {useEffect, useMemo, useState, type ComponentType} from 'react';
import {AtSign, BookOpen, Facebook, Github, Globe, GraduationCap, Instagram, Linkedin, Mail, MessageCircle, Music, Send, Youtube, ExternalLink, X} from 'lucide-react';

type Social = {id:number; platform:string; url:string; label?:string|null};

type Props = {links?:Social[]; mode?:'button'|'icons'; className?:string};

const iconMap: Record<string, ComponentType<{size?:number; strokeWidth?:number}>> = {
  instagram: Instagram,
  linkedin: Linkedin,
  github: Github,
  youtube: Youtube,
  facebook: Facebook,
  telegram: Send,
  whatsapp: MessageCircle,
  discord: MessageCircle,
  music: Music,
  tiktok: Music,
  orcid: GraduationCap,
  'google scholar': GraduationCap,
  scholar: GraduationCap,
  arxiv: BookOpen,
  email: Mail,
  mail: Mail,
  website: Globe,
  web: Globe,
  x: AtSign,
  twitter: AtSign,
};

function normalized(platform:string){return platform.trim().toLowerCase();}
function iconFor(platform:string){
  const key=normalized(platform);
  const exact=iconMap[key];
  if(exact)return exact;
  if(key.includes('instagram'))return Instagram;
  if(key.includes('linkedin'))return Linkedin;
  if(key.includes('github'))return Github;
  if(key.includes('youtube'))return Youtube;
  if(key.includes('facebook'))return Facebook;
  if(key.includes('telegram'))return Send;
  if(key.includes('whatsapp'))return MessageCircle;
  if(key.includes('orcid'))return GraduationCap;
  if(key.includes('scholar'))return GraduationCap;
  if(key.includes('arxiv'))return BookOpen;
  if(key.includes('email')||key.includes('mail'))return Mail;
  return Globe;
}

function cleanLabel(s:Social){return (s.label||s.platform||'Social profile').trim();}

export function SocialHub({links=[],mode='button',className='' }:Props){
  const visible=useMemo(()=>links.filter(x=>x?.url&&x.platform).slice(0,24),[links]);
  const [open,setOpen]=useState(false);
  const [selected,setSelected]=useState<Social|null>(null);
  const [copied,setCopied]=useState(false);

  useEffect(()=>{
    if(!open)return;
    const onKey=(e:KeyboardEvent)=>{if(e.key==='Escape'){setOpen(false);setSelected(null);}};
    window.addEventListener('keydown',onKey);
    return ()=>window.removeEventListener('keydown',onKey);
  },[open]);

  useEffect(()=>{
    if(!open)document.body.style.overflow='';
    else document.body.style.overflow='hidden';
    return ()=>{document.body.style.overflow='';};
  },[open]);

  if(!visible.length)return null;

  return <>
    {mode==='button' ? (
      <button type="button" className={`btn ${className}`} onClick={()=>setOpen(true)} aria-haspopup="dialog" aria-expanded={open}>
        Connect <ExternalLink size={14}/>
      </button>
    ) : (
      <div className={`flex flex-wrap items-center gap-2 ${className}`} aria-label="Social profiles">
        {visible.map((social)=>{const Icon=iconFor(social.platform); return <button type="button" key={social.id} title={cleanLabel(social)} aria-label={`Open ${cleanLabel(social)}`} onClick={()=>{setSelected(social);setOpen(true);setCopied(false);}} className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] bg-[var(--card)] text-[var(--muted)] transition hover:-translate-y-0.5 hover:text-[var(--fg)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-current"><Icon size={17} strokeWidth={1.8}/></button>})}
      </div>
    )}

    {open&&<div className="fixed inset-0 z-[100] flex items-end justify-center bg-black/45 p-3 backdrop-blur-sm sm:items-center" role="dialog" aria-modal="true" aria-labelledby="social-hub-title" onMouseDown={(e)=>{if(e.target===e.currentTarget){setOpen(false);setSelected(null)}}}>
      <div className="w-full max-w-xl rounded-[28px] border border-[var(--line)] bg-[var(--card)] p-6 shadow-2xl sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="mono text-[10px] uppercase tracking-[.2em] text-[var(--muted)]">REACH OUT</div>
            <h2 id="social-hub-title" className="mt-2 text-2xl font-semibold">Connect across platforms</h2>
            <p className="mt-2 max-w-lg text-sm leading-6 text-[var(--muted)]">Choose a platform to open the owner’s configured profile. Only links intentionally published by the owner appear here.</p>
          </div>
          <button type="button" className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] text-[var(--muted)] hover:text-[var(--fg)]" aria-label="Close" onClick={()=>{setOpen(false);setSelected(null)}}><X size={18}/></button>
        </div>

        {selected ? <div className="mt-6 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-5">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-[var(--line)] bg-[var(--card)]"><IconGlyph platform={selected.platform}/></div>
            <div className="min-w-0 flex-1"><div className="font-semibold">{cleanLabel(selected)}</div><div className="mt-1 truncate text-xs text-[var(--muted)]">{selected.url}</div></div>
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            <a className="btn btn-dark" href={selected.url} target="_blank" rel="noreferrer noopener" onClick={()=>setOpen(false)}>Open profile <ExternalLink size={14}/></a>
            <button type="button" className="btn" onClick={async()=>{try{await navigator.clipboard.writeText(selected.url);setCopied(true)}catch{setCopied(false)}}}>{copied?'Copied':'Copy link'}</button>
            <button type="button" className="btn" onClick={()=>setSelected(null)}>See all platforms</button>
          </div>
        </div> : <div className="mt-6 grid gap-2 sm:grid-cols-2">
          {visible.map((social)=>{const Icon=iconFor(social.platform);return <button type="button" key={social.id} onClick={()=>{setSelected(social);setCopied(false)}} className="group flex items-center gap-3 rounded-2xl border border-[var(--line)] bg-[var(--bg)] p-4 text-left transition hover:-translate-y-0.5 hover:border-[var(--fg)]">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-[var(--line)] bg-[var(--card)] text-[var(--muted)] group-hover:text-[var(--fg)]"><Icon size={19}/></span>
            <span className="min-w-0 flex-1"><span className="block font-medium">{cleanLabel(social)}</span><span className="mt-1 block truncate text-xs text-[var(--muted)]">{social.platform}</span></span>
            <ExternalLink size={15} className="text-[var(--muted)]"/>
          </button>})}
        </div>}
      </div>
    </div>}
  </>;
}

function IconGlyph({platform}:{platform:string}){const Icon=iconFor(platform);return <Icon size={21} strokeWidth={1.8}/>}
