"use client";

import {useEffect,useRef,useState} from "react";

type Option={value:string;label:string;detail:string;tone?:string};
export function InlineListingSelect({name,label,initial,options}:{name:string;label:string;initial:string;options:Option[]}){
  const [value,setValue]=useState(initial);const [open,setOpen]=useState(false);const root=useRef<HTMLDivElement>(null);const selected=options.find(option=>option.value===value)||options[0];
  useEffect(()=>setValue(initial),[initial]);
  useEffect(()=>{function outside(event:MouseEvent){if(!root.current?.contains(event.target as Node))setOpen(false)}function escape(event:KeyboardEvent){if(event.key==="Escape")setOpen(false)}document.addEventListener("mousedown",outside);document.addEventListener("keydown",escape);return()=>{document.removeEventListener("mousedown",outside);document.removeEventListener("keydown",escape)}},[]);
  return <div className={`inlineListingSelect ${open?"isOpen":""}`} ref={root}><input type="hidden" name={name} value={value}/><span className="inlineSelectLabel">{label}</span><button type="button" className="inlineSelectTrigger" aria-haspopup="listbox" aria-expanded={open} onClick={()=>setOpen(current=>!current)}><span><i className={selected.tone||selected.value}/><strong>{selected.label}</strong></span><b aria-hidden="true"/></button><div className="inlineSelectMenu" role="listbox" aria-label={label}>{options.map(option=><button type="button" role="option" aria-selected={option.value===value} key={option.value} onClick={()=>{setValue(option.value);setOpen(false)}}><i className={option.tone||option.value}/><span><strong>{option.label}</strong><small>{option.detail}</small></span><b aria-hidden="true">{option.value===value?"✓":""}</b></button>)}</div></div>
}
