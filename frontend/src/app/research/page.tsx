import type {Metadata} from 'next';
import {Section} from '../../components/Section';
import {PublicCollection} from '../../components/PublicCollection';
export const metadata:Metadata={title:'Research',description:'Research questions, methods, experiments and findings.',alternates:{canonical:'/research'}};
export default function Page(){return <main className="fade"><Section eyebrow="RESEARCH" title="Questions, methods and findings"><p className="mb-10 max-w-3xl leading-7 text-[var(--muted)]">Research is separated from blog content and from peer-reviewed publication status.</p><PublicCollection kind="research"/></Section></main>}
