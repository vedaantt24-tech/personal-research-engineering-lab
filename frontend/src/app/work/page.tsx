import type {Metadata} from 'next';
import {Section} from '../../components/Section';
import {PublicCollection} from '../../components/PublicCollection';
export const metadata:Metadata={title:'Work',description:'Technical projects and engineering case studies.',alternates:{canonical:'/work'}};
export default function Page(){return <main className="fade"><Section eyebrow="WORK" title="Projects and technical case studies"><p className="mb-10 max-w-3xl leading-7 text-[var(--muted)]">Projects are published only after the owner chooses to make them public.</p><PublicCollection kind="work"/></Section></main>}
