import type {Metadata} from 'next';
import {Section} from '../../components/Section';
import {PublicCollection} from '../../components/PublicCollection';
export const metadata:Metadata={title:'Notes',description:'Technical notes, learning, engineering thoughts and project updates.',alternates:{canonical:'/notes'}};
export default function Notes(){return <main className="fade"><Section eyebrow="NOTES" title="Technical notes & learning"><p className="mb-10 max-w-3xl leading-7 text-[var(--muted)]">Notes are distinct from formal research publications. They capture explanations, project updates, lessons learned and engineering thoughts.</p><PublicCollection kind="notes"/></Section></main>}
