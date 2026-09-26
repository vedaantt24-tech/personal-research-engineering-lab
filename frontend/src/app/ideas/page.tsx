import type {Metadata} from 'next';
import {Section} from '../../components/Section';
import {PublicCollection} from '../../components/PublicCollection';
export const metadata:Metadata={title:'Ideas Lab',description:'Concepts, inventions and future technology ideas under exploration.',alternates:{canonical:'/ideas'}};
export default function Page(){return <main className="fade"><Section eyebrow="IDEAS LAB" title="Concepts and inventions"><p className="mb-10 max-w-3xl leading-7 text-[var(--muted)]">Each public idea can carry its own visibility and permission workflow.</p><PublicCollection kind="ideas"/></Section></main>}
