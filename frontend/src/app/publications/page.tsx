import type {Metadata} from 'next';
import {Section} from '../../components/Section';
import {PublicCollection} from '../../components/PublicCollection';
export const metadata:Metadata={title:'Publications',description:'Papers, preprints, technical reports and posters.',alternates:{canonical:'/publications'}};
export default function Page(){return <main className="fade"><Section eyebrow="PUBLICATIONS" title="Papers, preprints and reports"><p className="mb-10 max-w-3xl leading-7 text-[var(--muted)]">Academic status is shown as actually claimed, never upgraded automatically.</p><PublicCollection kind="publications"/></Section></main>}
