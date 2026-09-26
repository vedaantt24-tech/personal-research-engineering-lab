'use client';
export function ExperimentChart({rows}:{rows:any[]}){
 if(!rows?.length)return <div className="card p-6 text-sm text-[var(--muted)]">No numeric experiment data published.</div>;
 const series=Array.from(new Set(rows.map(r=>r.series||'default')));
 const width=760,height=300,pad=40;
 const vals=rows.map(r=>Number(r.y_value)).filter(Number.isFinite);
 const min=Math.min(...vals),max=Math.max(...vals),range=max-min||1;
 const xVals=rows.map((r,i)=>r.x_value==null?i:Number(r.x_value));
 const minX=Math.min(...xVals),maxX=Math.max(...xVals),xRange=maxX-minX||1;
 function pathFor(name:string){const pts=rows.filter(r=>(r.series||'default')===name).map((r,i)=>{const xv=r.x_value==null?i:Number(r.x_value);const x=pad+((xv-minX)/xRange)*(width-pad*2);const y=height-pad-((Number(r.y_value)-min)/range)*(height-pad*2);return `${x},${y}`});return pts.join(' ')}
 return <div className="card p-6 overflow-auto"><div className="mono text-[10px] uppercase tracking-[.18em] text-[var(--muted)]">MEASURED DATA</div><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Experiment numeric data chart" className="mt-4 min-w-[680px] w-full"><line x1={pad} y1={height-pad} x2={width-pad} y2={height-pad} stroke="currentColor" strokeOpacity=".18"/><line x1={pad} y1={pad} x2={pad} y2={height-pad} stroke="currentColor" strokeOpacity=".18"/>{series.map(name=><polyline key={name} fill="none" stroke="currentColor" strokeWidth="2.5" points={pathFor(name)} vectorEffect="non-scaling-stroke"/>)}<text x={pad} y={18} fontSize="11" fill="currentColor">max {max}</text><text x={pad} y={height-8} fontSize="11" fill="currentColor">min {min}</text></svg><div className="mt-4 flex flex-wrap gap-2">{series.map((name)=> <span className="status" key={name}>{name}</span>)}</div><div className="mt-4 text-xs text-[var(--muted)]">{rows.length} recorded point{rows.length===1?'':'s'}{rows[0]?.unit?` · unit: ${rows[0].unit}`:''}</div></div>
}
