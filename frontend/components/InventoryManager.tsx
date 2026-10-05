"use client";
import {FormEvent,useState} from "react";
import type {Vehicle} from "@/lib/types";
import {VehicleMediaManager} from "./VehicleMediaManager";
import {InlineListingSelect} from "./InlineListingSelect";

function message(data:unknown){if(data&&typeof data==="object"&&"detail" in data)return String((data as {detail:unknown}).detail);return "Could not save changes."}
export function InventoryManager({initial}:{initial:Vehicle[]}){
  const [items,setItems]=useState(initial);const [notice,setNotice]=useState("");
  function replace(vehicle:Vehicle){setItems(current=>current.map(item=>item.id===vehicle.id?vehicle:item))}
  async function save(event:FormEvent<HTMLFormElement>,id:string){event.preventDefault();setNotice("Saving listing changes…");const form=new FormData(event.currentTarget);const body={...Object.fromEntries(form),is_featured:form.has("is_featured")};const response=await fetch(`/api/staff/vehicles/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const data=await response.json();if(response.ok){replace(data);setNotice(`${data.title} saved. Homepage hero and marketplace updates are queued.`)}else setNotice(message(data))}
  return <><p role="status" className="notice inventoryNotice">{notice||"Choose which published, non-sold vehicles appear in the homepage hero. Selecting several creates a slideshow."}</p><div className="inventoryManagerList">{items.map(vehicle=><article className="panel manageCard premiumManageCard" key={vehicle.id}>
    <div className="manageCardIdentity"><div className="manageCover">{vehicle.images[0]?<img src={vehicle.images[0].url} alt=""/>:<span>{vehicle.make[0]}</span>}</div><div><span className={`status ${vehicle.availability}`}>{vehicle.availability}</span><h2>{vehicle.title}</h2><small>Version {vehicle.version} · {vehicle.location}</small></div></div>
    <form className="quickControls heroQuickControls" onSubmit={event=>save(event,vehicle.id)}><label><span>Price (NGN)</span><input name="price" type="number" min="0" step="0.01" defaultValue={vehicle.price}/></label><InlineListingSelect name="publication_status" label="Website publication" initial={vehicle.publication_status} options={[{value:"draft",label:"Draft",detail:"Private and editable"},{value:"published",label:"Published",detail:"Visible on dealer website"},{value:"unpublished",label:"Unpublished",detail:"Withdraw from website"}]}/><InlineListingSelect name="availability" label="Availability" initial={vehicle.availability} options={[{value:"available",label:"Available",detail:"Open to buyer enquiries"},{value:"reserved",label:"Reserved",detail:"Temporarily held"},{value:"sold",label:"Sold",detail:"No longer available"}]}/><label className="heroFeatureToggle"><input name="is_featured" type="checkbox" defaultChecked={vehicle.is_featured}/><span><b>Homepage hero</b><small>{vehicle.is_featured?"Selected for slideshow":"Not selected"}</small></span><i aria-hidden="true"/></label><button className="button dark">Save listing <span>↗</span></button></form>
    <VehicleMediaManager vehicle={vehicle} onChange={replace} onNotice={setNotice}/>
  </article>)}</div></>
}
