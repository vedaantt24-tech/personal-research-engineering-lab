const API=(process.env.INTERNAL_API_URL||process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export async function serverApi<T=unknown>(path:string):Promise<T|null>{
  try{
    const init:RequestInit={cache:'no-store',headers:{Accept:'application/json'}};
    const res=await fetch(`${API}${path}`,init);
    if(!res.ok) return null;
    return await res.json() as T;
  }catch{return null;}
}
