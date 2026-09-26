import type {Metadata} from 'next';
import {Detail} from '../../../components/Detail';
import {serverApi} from '../../../lib/server-api';
import {absoluteUrl,cleanDescription,siteUrl} from '../../../lib/seo';
type Item={title?:string;abstract?:string;updated_at?:string};
export async function generateMetadata({params}:{params:Promise<{slug:string}>}):Promise<Metadata>{const {slug}=await params;const x=await serverApi<Item>(`/public/research/${encodeURIComponent(slug)}`);const title=x?.title||slug;const description=cleanDescription(x?.abstract,'Research record documenting questions, methods and findings.');return{title:`${title} — Research`,description,alternates:{canonical:absoluteUrl(`/research/${slug}`)},openGraph:{title,description,url:absoluteUrl(`/research/${slug}`),type:'article'}}}
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const x=await serverApi<Item>(`/public/research/${encodeURIComponent(slug)}`);return <><Detail kind="research" slug={slug}/>{x&&<script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify({"@context":"https://schema.org","@type":"ScholarlyArticle",headline:x.title,description:x.abstract,url:`${siteUrl}/research/${slug}`,dateModified:x.updated_at})}}/>}</>}
