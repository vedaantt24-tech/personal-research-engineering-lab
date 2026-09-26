import type {Metadata} from 'next';
import {Detail} from '../../../components/Detail';
import {serverApi} from '../../../lib/server-api';
import {absoluteUrl,cleanDescription,siteUrl} from '../../../lib/seo';
type Item={title?:string;question?:string;updated_at?:string};
export async function generateMetadata({params}:{params:Promise<{slug:string}>}):Promise<Metadata>{const {slug}=await params;const x=await serverApi<Item>(`/public/experiments/${encodeURIComponent(slug)}`);const title=x?.title||slug;const description=cleanDescription(x?.question,'Engineering experiment notebook entry.');return{title:`${title} — Experiments`,description,alternates:{canonical:absoluteUrl(`/experiments/${slug}`)},openGraph:{title,description,url:absoluteUrl(`/experiments/${slug}`),type:'article'}}}
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const x=await serverApi<Item>(`/public/experiments/${encodeURIComponent(slug)}`);return <><Detail kind="experiments" slug={slug}/>{x&&<script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify({"@context":"https://schema.org","@type":"TechArticle",headline:x.title,description:x.question,url:`${siteUrl}/experiments/${slug}`,dateModified:x.updated_at})}}/>}</>}
