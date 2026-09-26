import './globals.css';
import {Header,Footer} from '../components/SiteChrome';
import {Analytics} from '../components/Analytics';
import {serverApi} from '../lib/server-api';
import type {Metadata} from 'next';

export async function generateMetadata():Promise<Metadata>{
 const profile=await serverApi<any>('/public/profile').catch(()=>null);
 const name=profile?.name||'[OWNER NAME]';
 const title=profile?.tagline?`${name} — ${profile.tagline}`:`${name} — Research, Ideas & Engineering`;
 const description=profile?.bio||profile?.tagline||'A personal engineering laboratory documenting research, ideas, experiments and technical work.';
 return {title,description,metadataBase:new URL(process.env.NEXT_PUBLIC_SITE_URL||'http://localhost:3000'),openGraph:{title,description,type:'website'},robots:{index:true,follow:true}};
}

export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><Analytics/><a href="#content" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-xl focus:bg-black focus:px-4 focus:py-2 focus:text-white">Skip to content</a><Header/><div id="content">{children}</div><Footer/></body></html>}
