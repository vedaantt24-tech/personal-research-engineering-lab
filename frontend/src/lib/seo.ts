export const siteUrl=(process.env.NEXT_PUBLIC_SITE_URL||'http://localhost:3000').replace(/\/$/,'');
export function absoluteUrl(path:string){return `${siteUrl}${path.startsWith('/')?path:`/${path}`}`;}
export function cleanDescription(value:string|undefined|null,fallback:string){return String(value||fallback).replace(/\s+/g,' ').trim().slice(0,160);}
