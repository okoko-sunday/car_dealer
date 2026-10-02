"use client";
import {FormEvent,useState} from "react";
import type {Vehicle} from "@/lib/types";
import {VehicleMediaManager} from "./VehicleMediaManager";

function message(data:unknown){if(data&&typeof data==="object"&&"detail" in data)return String((data as {detail:unknown}).detail);return "Could not save changes."}
export function InventoryManager({initial}:{initial:Vehicle[]}){
  const [items,setItems]=useState(initial);const [notice,setNotice]=useState("");
  function replace(vehicle:Vehicle){setItems(current=>current.map(item=>item.id===vehicle.id?vehicle:item))}
  async function save(event:FormEvent<HTMLFormElement>,id:string){event.preventDefault();setNotice("Saving listing changes…");const body=Object.fromEntries(new FormData(event.currentTarget));const response=await fetch(`/api/staff/vehicles/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const data=await response.json();if(response.ok){replace(data);setNotice(`${data.title} saved and marketplace sync queued.`)}else setNotice(message(data))}
  return <><p role="status" className="notice inventoryNotice">{notice||"Select a listing to update its website state, price, or gallery."}</p><div className="inventoryManagerList">{items.map(vehicle=><article className="panel manageCard premiumManageCard" key={vehicle.id}>
    <div className="manageCardIdentity"><div className="manageCover">{vehicle.images[0]?<img src={vehicle.images[0].url} alt=""/>:<span>{vehicle.make[0]}</span>}</div><div><span className={`status ${vehicle.availability}`}>{vehicle.availability}</span><h2>{vehicle.title}</h2><small>Version {vehicle.version} · {vehicle.location}</small></div></div>
    <form className="quickControls" onSubmit={event=>save(event,vehicle.id)}><label><span>Price (NGN)</span><input name="price" type="number" min="0" step="0.01" defaultValue={vehicle.price}/></label><label><span>Website publication</span><select name="publication_status" defaultValue={vehicle.publication_status}><option value="draft">Draft</option><option value="published">Published</option><option value="unpublished">Unpublished / withdrawn</option></select></label><label><span>Availability</span><select name="availability" defaultValue={vehicle.availability}><option value="available">Available</option><option value="reserved">Reserved</option><option value="sold">Sold</option></select></label><button className="button dark">Save listing <span>↗</span></button></form>
    <VehicleMediaManager vehicle={vehicle} onChange={replace} onNotice={setNotice}/>
  </article>)}</div></>
}
