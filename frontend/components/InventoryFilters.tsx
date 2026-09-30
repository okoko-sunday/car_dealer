"use client";

import {FormEvent,useEffect,useRef,useState} from "react";
import {usePathname,useRouter} from "next/navigation";

type Option={value:string;label:string;detail?:string};
const availability:Option[]=[
  {value:"",label:"All vehicles",detail:"Complete collection"},
  {value:"available",label:"Available now",detail:"Ready for enquiry"},
  {value:"reserved",label:"Reserved",detail:"Currently held"},
  {value:"sold",label:"Sold archive",detail:"Previously offered"},
];
const sorting:Option[]=[
  {value:"newest",label:"Latest arrivals",detail:"Recently published first"},
  {value:"price_low",label:"Price · low first",detail:"Ascending asking price"},
  {value:"price_high",label:"Price · high first",detail:"Descending asking price"},
];

function Choice({label,value,options,onChange}:{label:string;value:string;options:Option[];onChange:(value:string)=>void}){
  const [open,setOpen]=useState(false);const root=useRef<HTMLDivElement>(null);
  const selected=options.find(option=>option.value===value)||options[0];
  useEffect(()=>{function outside(event:MouseEvent){if(!root.current?.contains(event.target as Node))setOpen(false)}function key(event:KeyboardEvent){if(event.key==="Escape")setOpen(false)}document.addEventListener("mousedown",outside);document.addEventListener("keydown",key);return()=>{document.removeEventListener("mousedown",outside);document.removeEventListener("keydown",key)}},[]);
  return <div className={`filterChoice ${open?"isOpen":""}`} ref={root}>
    <span className="filterLabel">{label}</span>
    <button type="button" className="choiceTrigger" aria-expanded={open} aria-haspopup="listbox" onClick={()=>setOpen(current=>!current)}>
      <span>{selected.label}</span><i aria-hidden="true"/>
    </button>
    <div className="choiceMenu" role="listbox" aria-label={label}>
      {options.map(option=><button type="button" role="option" aria-selected={option.value===value} key={option.value||"all"} onClick={()=>{onChange(option.value);setOpen(false)}}>
        <span><strong>{option.label}</strong><small>{option.detail}</small></span><b aria-hidden="true">{option.value===value?"✓":""}</b>
      </button>)}
    </div>
  </div>
}

export function InventoryFilters({initialQuery="",initialAvailability="",initialSort="newest"}:{initialQuery?:string;initialAvailability?:string;initialSort?:string}){
  const router=useRouter();const pathname=usePathname();
  const [query,setQuery]=useState(initialQuery);const [status,setStatus]=useState(initialAvailability);const [sort,setSort]=useState(initialSort||"newest");const [loading,setLoading]=useState(false);
  function apply(event?:FormEvent){event?.preventDefault();const params=new URLSearchParams();if(query.trim())params.set("q",query.trim());if(status)params.set("availability",status);if(sort!=="newest")params.set("sort",sort);setLoading(true);router.push(`${pathname}${params.size?`?${params}`:""}`);window.setTimeout(()=>setLoading(false),450)}
  function clear(){setQuery("");setStatus("");setSort("newest");setLoading(true);router.push(pathname);window.setTimeout(()=>setLoading(false),450)}
  const active=Boolean(query.trim()||status||sort!=="newest");
  return <form className={`filterBar premiumFilters ${loading?"isLoading":""}`} onSubmit={apply}>
    <label className="searchField">
      <span className="filterLabel">Search collection</span>
      <span className="searchControl"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg><input type="search" value={query} onChange={event=>setQuery(event.target.value)} placeholder="Make, model or keyword"/><button type="button" aria-label="Clear search" className={query?"isVisible":""} onClick={()=>setQuery("")}>×</button></span>
    </label>
    <Choice label="Availability" value={status} options={availability} onChange={setStatus}/>
    <Choice label="Order by" value={sort} options={sorting} onChange={setSort}/>
    <div className="filterActions"><button className="filterSubmit" type="submit"><span>{loading?"Updating":"Apply filters"}</span><b aria-hidden="true">→</b></button>{active&&<button className="filterReset" type="button" onClick={clear}>Reset</button>}</div>
  </form>
}
