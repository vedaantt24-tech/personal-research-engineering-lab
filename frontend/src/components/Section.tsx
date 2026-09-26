import { ReactNode } from 'react';
export function Section({eyebrow,title,children}:{eyebrow:string,title:string,children:ReactNode}){return <section className="mx-auto max-w-7xl px-5 py-20 md:px-8"><div className="mb-8"><div className="mono text-[11px] uppercase tracking-[.22em] text-[var(--muted)]">{eyebrow}</div><h2 className="mt-2 text-3xl font-semibold tracking-[-.03em] md:text-5xl">{title}</h2></div>{children}</section>}
export function Status({children}:{children:ReactNode}){return <span className="status">{children}</span>}
