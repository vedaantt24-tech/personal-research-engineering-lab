import type {Metadata} from 'next';
import {Section} from '../../components/Section';
import {PublicCollection} from '../../components/PublicCollection';
export const metadata:Metadata={title:'Experiments',description:'Engineering experiments, measurements, failures and next steps.',alternates:{canonical:'/experiments'}};
export default function Page(){return <main className="fade"><Section eyebrow="EXPERIMENTS" title="Engineering notebook"><p className="mb-10 max-w-3xl leading-7 text-[var(--muted)]">Failures and partial results are allowed; the record is more important than polish.</p><PublicCollection kind="experiments"/></Section></main>}
