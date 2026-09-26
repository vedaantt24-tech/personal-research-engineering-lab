'use client';
import {useEffect} from 'react';
import {usePathname} from 'next/navigation';
import {api} from '../lib/api';
export function Analytics(){
  const pathname=usePathname();
  useEffect(()=>{ if(pathname) api('/analytics/event',{method:'POST',body:JSON.stringify({event_type:'page_view',path:pathname})}).catch(()=>{}); },[pathname]);
  return null;
}
