const BASE=(process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export async function api<T=any>(path:string,init:RequestInit={}) : Promise<T>{
 const headers=new Headers(init.headers); const method=(init.method||'GET').toUpperCase(); if(!['GET','HEAD','OPTIONS'].includes(method)){const csrf=document.cookie.split('; ').find(x=>x.startsWith('csrf_token='))?.split('=')[1]; if(csrf) headers.set('X-CSRF-Token',decodeURIComponent(csrf));} if(!headers.has('Content-Type') && init.body && !(init.body instanceof FormData)) headers.set('Content-Type','application/json');
 const res=await fetch(`${BASE}${path}`,{...init,headers,credentials:'include',cache:'no-store'});
 let data:any=null; const text=await res.text(); try{data=text?JSON.parse(text):null}catch{data=text};
 if(!res.ok){const detail=data?.detail||data?.message||`Request failed (${res.status})`;throw new Error(detail)}
 return data as T;
}
export {BASE as API_BASE};
