'use client';
import {useEffect,useState} from 'react';
export function ThemeToggle(){
  const [dark,setDark]=useState(false);
  useEffect(()=>{const stored=localStorage.getItem('theme'); const enabled=stored==='dark'||(!stored&&window.matchMedia('(prefers-color-scheme: dark)').matches); setDark(enabled); document.documentElement.dataset.theme=enabled?'dark':'light';},[]);
  function toggle(){const next=!dark; setDark(next); document.documentElement.dataset.theme=next?'dark':'light'; localStorage.setItem('theme',next?'dark':'light');}
  return <button type="button" aria-label={dark?'Switch to light theme':'Switch to dark theme'} aria-pressed={dark} className="btn px-3" onClick={toggle}>{dark?'Light':'Dark'}</button>;
}
