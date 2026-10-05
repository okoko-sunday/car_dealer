"use client";

import {FormEvent,useEffect,useRef,useState} from "react";
import {useRouter} from "next/navigation";

type Option={value:string;label:string;detail:string};
const sortOptions:Option[]=[
  {value:"newest",label:"Latest arrivals",detail:"Recently published first"},
  {value:"price_low",label:"Price · low first",detail:"Lowest asking price first"},
  {value:"price_high",label:"Price · high first",detail:"Highest asking price first"},
];
function Choice({label,value,options,onChange}:{label:string;value:string;options:Option[];onChange:(value:string)=>void}){
  const [open,setOpen]=useState(false);const root=useRef<HTMLDivElement>(null);const selected=options.find(item=>item.value===value)||options[0];
  useEffect(()=>{function outside(event:MouseEvent){if(!root.current?.contains(event.target as Node))setOpen(false)}function keyboard(event:KeyboardEvent){if(event.key==="Escape")setOpen(false)}document.addEventListener("mousedown",outside);document.addEventListener("keydown",keyboard);return()=>{document.removeEventListener("mousedown",outside);document.removeEventListener("keydown",keyboard)}},[]);
  return <div className={`filterChoice ${open?"isOpen":""}`} ref={root}><span className="filterLabel">{label}</span><button type="button" className="choiceTrigger" aria-expanded={open} aria-haspopup="listbox" onClick={()=>setOpen(current=>!current)}><span>{selected.label}</span><i aria-hidden="true"/></button><div className="choiceMenu" role="listbox" aria-label={label}>{options.map(option=><button key={option.value||"all"} type="button" role="option" aria-selected={option.value===value} onClick={()=>{onChange(option.value);setOpen(false)}}><span><strong>{option.label}</strong><small>{option.detail}</small></span><b aria-hidden="true">{option.value===value?"✓":""}</b></button>)}</div></div>;
}
export function ShowroomFilters({initialQuery="",initialMake="",initialTransmission="",initialSort="newest",makes,transmissions}:{initialQuery?:string;initialMake?:string;initialTransmission?:string;initialSort?:string;makes:string[];transmissions:string[]}){
  const router=useRouter();const [query,setQuery]=useState(initialQuery);const [make,setMake]=useState(initialMake);const [transmission,setTransmission]=useState(initialTransmission);const [sort,setSort]=useState(initialSort||"newest");const [loading,setLoading]=useState(false);
  const makeOptions=[{value:"",label:"Every make",detail:"All available marques"},...makes.map(value=>({value,label:value,detail:`Available ${value} vehicles`}))];
  const transmissionOptions=[{value:"",label:"Any transmission",detail:"All transmission types"},...transmissions.map(value=>({value,label:value,detail:`${value} vehicles`}))];
  function go(event?:FormEvent){event?.preventDefault();const params=new URLSearchParams();if(query.trim())params.set("q",query.trim());if(make)params.set("make",make);if(transmission)params.set("transmission",transmission);if(sort!=="newest")params.set("sort",sort);setLoading(true);router.push(`/showroom${params.size?`?${params}`:""}`)}
  function reset(){setQuery("");setMake("");setTransmission("");setSort("newest");setLoading(true);router.push("/showroom")}
  const active=Boolean(query.trim()||make||transmission||sort!=="newest");
  return <form className={`showroomFilterBar premiumFilters ${loading?"isLoading":""}`} onSubmit={go}><label className="searchField"><span className="filterLabel">Search available cars</span><span className="searchControl"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg><input type="search" value={query} onChange={event=>setQuery(event.target.value)} placeholder="Make, model or keyword"/><button type="button" aria-label="Clear search" className={query?"isVisible":""} onClick={()=>setQuery("")}>×</button></span></label><Choice label="Make" value={make} options={makeOptions} onChange={setMake}/><Choice label="Transmission" value={transmission} options={transmissionOptions} onChange={setTransmission}/><Choice label="Order by" value={sort} options={sortOptions} onChange={setSort}/><div className="filterActions"><button className="filterSubmit" type="submit"><span>{loading?"Updating":"Show results"}</span><b aria-hidden="true">→</b></button>{active&&<button className="filterReset" type="button" onClick={reset}>Reset</button>}</div></form>;
}
