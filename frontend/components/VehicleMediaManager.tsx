"use client";

import {FormEvent,useEffect,useState} from "react";
import type {Vehicle} from "@/lib/types";

function errorMessage(data:unknown){if(!data||typeof data!=="object")return "The image operation could not be completed.";const record=data as Record<string,unknown>;if(typeof record.detail==="string")return record.detail;for(const value of Object.values(record)){if(Array.isArray(value)&&value[0])return String(value[0])}return "Review the image and try again."}

export function VehicleMediaManager({vehicle,onChange,onNotice}:{vehicle:Vehicle;onChange:(vehicle:Vehicle)=>void;onNotice:(message:string)=>void}){
  const [open,setOpen]=useState(false);const [file,setFile]=useState<File|null>(null);const [preview,setPreview]=useState("");const [alt,setAlt]=useState("");const [busy,setBusy]=useState(false);
  useEffect(()=>{if(!file){setPreview("");return}const url=URL.createObjectURL(file);setPreview(url);return()=>URL.revokeObjectURL(url)},[file]);
  async function upload(event:FormEvent){event.preventDefault();if(!file)return;setBusy(true);onNotice("Uploading and processing image…");const body=new FormData();body.set("image",file);body.set("alt_text",alt);const response=await fetch(`/api/staff/vehicles/${vehicle.id}/images`,{method:"POST",body});const data=await response.json();if(response.ok){onChange(data);setFile(null);setAlt("");onNotice("Image uploaded. The listing and marketplace update were versioned.")}else onNotice(errorMessage(data));setBusy(false)}
  async function action(imageId:number,method:"PATCH"|"DELETE",direction?:"up"|"down"){if(method==="DELETE"&&!window.confirm("Remove this image from the vehicle listing?"))return;setBusy(true);onNotice(method==="DELETE"?"Removing image…":"Updating image order…");const response=await fetch(`/api/staff/vehicles/${vehicle.id}/images/${imageId}`,{method,headers:method==="PATCH"?{"Content-Type":"application/json"}:undefined,body:method==="PATCH"?JSON.stringify({direction}):undefined});const data=await response.json();if(response.ok){onChange(data);onNotice(method==="DELETE"?"Image removed and marketplace update queued.":"Image order updated.")}else onNotice(errorMessage(data));setBusy(false)}
  return <section className={`mediaManager ${open?"isOpen":""}`}>
    <button type="button" className="mediaToggle" aria-expanded={open} onClick={()=>setOpen(value=>!value)}><span><small>Vehicle media</small><strong>{vehicle.images.length?`${vehicle.images.length} photo${vehicle.images.length===1?"":"s"}`:"No photos yet"}</strong></span><b aria-hidden="true">{open?"−":"+"}</b></button>
    {open&&<div className="mediaWorkspace">
      <form className="mediaUploader" onSubmit={upload}>
        <label className={`dropField ${preview?"hasPreview":""}`}>
          {preview?<img src={preview} alt="Selected upload preview"/>:<><span className="uploadGlyph" aria-hidden="true">↑</span><strong>Choose a vehicle image</strong><small>JPEG, PNG or WebP · maximum 8 MB</small></>}
          <input type="file" accept="image/jpeg,image/png,image/webp" required onChange={event=>setFile(event.target.files?.[0]||null)}/>
          {preview&&<span className="replaceImage">Choose another</span>}
        </label>
        <label className="altField"><span>Image description</span><input value={alt} onChange={event=>setAlt(event.target.value)} required maxLength={180} placeholder="e.g. Front three-quarter view in daylight"/><small>Describe what is visible for buyers using screen readers.</small></label>
        <button className="button dark full" disabled={!file||!alt.trim()||busy}>{busy?"Working…":"Add to gallery"}<span>↗</span></button>
      </form>
      <div className="mediaGallery">
        <div className="mediaGalleryHead"><span>Current gallery</span><small>First photo becomes the listing cover</small></div>
        {vehicle.images.length?<div className="mediaGrid">{vehicle.images.map((image,index)=><figure key={image.id}>
          <div className="mediaThumb"><img src={image.url} alt={image.alt_text}/><span>{String(index+1).padStart(2,"0")}</span>{index===0&&<b>Cover</b>}</div>
          <figcaption>{image.alt_text}</figcaption>
          <div className="mediaActions"><button type="button" disabled={busy||index===0} onClick={()=>action(image.id,"PATCH","up")} aria-label={`Move ${image.alt_text} earlier`}>← <span>Earlier</span></button><button type="button" disabled={busy||index===vehicle.images.length-1} onClick={()=>action(image.id,"PATCH","down")} aria-label={`Move ${image.alt_text} later`}><span>Later</span> →</button><button type="button" disabled={busy} className="removeMedia" onClick={()=>action(image.id,"DELETE")}>Remove</button></div>
        </figure>)}</div>:<div className="mediaEmpty"><span>01</span><p>Add at least one clear exterior image before publishing this vehicle.</p></div>}
      </div>
    </div>}
  </section>
}
