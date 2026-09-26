import type {Metadata} from 'next';
import {Detail} from '../../../components/Detail';
import {serverApi} from '../../../lib/server-api';
import {absoluteUrl,cleanDescription,siteUrl} from '../../../lib/seo';
type Item={title?:string;one_line?:string;updated_at?:string};
export async function generateMetadata({params}:{params:Promise<{slug:string}>}):Promise<Metadata>{const {slug}=await params;const x=await serverApi<Item>(`/public/ideas/${encodeURIComponent(slug)}`);const title=x?.title||slug;const description=cleanDescription(x?.one_line,'Engineering concept and innovation note.');return{title:`${title} — Ideas Lab`,description,alternates:{canonical:absoluteUrl(`/ideas/${slug}`)},openGraph:{title,description,url:absoluteUrl(`/ideas/${slug}`),type:'article'}}}
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const x=await serverApi<Item>(`/public/ideas/${encodeURIComponent(slug)}`);return <><Detail kind="ideas" slug={slug}/>{x&&<script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify({"@context":"https://schema.org","@type":"Article",headline:x.title,description:x.one_line,url:`${siteUrl}/ideas/${slug}`,dateModified:x.updated_at})}}/>}</>}
