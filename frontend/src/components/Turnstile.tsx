'use client';
import {useEffect} from 'react';

export function Turnstile({onToken}:{onToken:(token:string)=>void}){
 const siteKey=process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
 useEffect(()=>{
  if(!siteKey)return;
  const script=document.createElement('script');script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';script.async=true;script.defer=true;
  document.head.appendChild(script);
  const render=()=>{const w=window as any;if(w.turnstile){const el=document.getElementById('turnstile-widget');if(el&&!el.dataset.rendered){w.turnstile.render(el,{sitekey:siteKey,callback:onToken,'expired-callback':()=>onToken(''),'error-callback':()=>onToken('')});el.dataset.rendered='1';}}};
  script.addEventListener('load',render);const timer=window.setInterval(render,500);return()=>{window.clearInterval(timer);script.removeEventListener('load',render);};
 },[siteKey,onToken]);
 if(!siteKey)return null;
 return <div id="turnstile-widget" className="mt-2" aria-label="Human verification"/>;
}
