import type {MetadataRoute} from 'next';
import {serverApi} from '../lib/server-api';
import {siteUrl} from '../lib/seo';
type Item={slug?:string;id?:number;updated_at?:string};
export default async function sitemap():Promise<MetadataRoute.Sitemap>{
 const staticPaths=['/','/about','/work','/research','/ideas','/experiments','/publications','/notes','/resume','/open-to','/collaborate','/contact','/search','/timeline','/terms','/privacy','/intellectual-property'];
 const sources:[string,string][]=[['/public/projects','/work'],['/public/research','/research'],['/public/ideas','/ideas'],['/public/experiments','/experiments'],['/public/notes','/notes'],['/public/publications','/publications']];
 const entries:MetadataRoute.Sitemap=staticPaths.map(path=>({url:`${siteUrl}${path}`}));
 for(const [endpoint,base] of sources){const rows=await serverApi<Item[]>(endpoint);for(const row of rows||[]){const key=row.slug||String(row.id||'');if(key)entries.push({url:`${siteUrl}${base}/${key}`,lastModified:row.updated_at?new Date(row.updated_at):undefined});}}
 return entries;
}
