import type {Metadata} from 'next';
import {Detail} from '../../../components/Detail';
import {serverApi} from '../../../lib/server-api';
import {absoluteUrl,cleanDescription,siteUrl} from '../../../lib/seo';
type Item={title?:string;summary?:string;image_url?:string;updated_at?:string};
export async function generateMetadata({params}:{params:Promise<{slug:string}>}):Promise<Metadata>{const {slug}=await params;const x=await serverApi<Item>(`/public/projects/${encodeURIComponent(slug)}`);const title=x?.title||slug;const description=cleanDescription(x?.summary,'Engineering project case study.');return{title:`${title} — Work`,description,alternates:{canonical:absoluteUrl(`/work/${slug}`)},openGraph:{title,description,url:absoluteUrl(`/work/${slug}`),type:'article',images:x?.image_url?[x.image_url]:undefined}}}
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const x=await serverApi<Item>(`/public/projects/${encodeURIComponent(slug)}`);return <><Detail kind="work" slug={slug}/>{x&&<script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify({"@context":"https://schema.org","@type":"TechArticle",headline:x.title,description:x.summary,url:`${siteUrl}/work/${slug}`,dateModified:x.updated_at})}}/>}</>}
