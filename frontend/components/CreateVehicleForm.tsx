"use client";

import {FormEvent,useState} from "react";
import {useRouter} from "next/navigation";

type ErrorResponse={detail?:string|Record<string,string[]>;[key:string]:unknown};

export function CreateVehicleForm(){
  const router=useRouter();
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);

  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();
    setError("");setBusy(true);
    const data=new FormData(event.currentTarget);
    const fields=Object.fromEntries(data.entries());
    const payload={
      ...fields,
      year:Number(fields.year),
      price:String(fields.price),
      mileage_km:Number(fields.mileage_km),
      is_featured:data.has("is_featured"),
      publication_status:"draft",
      availability:"available",
    };
    try{
      const response=await fetch("/api/staff/vehicles",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload),
      });
      const result=await response.json() as ErrorResponse & {id?:string};
      if(!response.ok||!result.id){
        const details=Object.entries(result).filter(([key])=>key!=="detail").map(([key,value])=>`${key}: ${Array.isArray(value)?value.join(", "):String(value)}`);
        setError(details.join(" · ")||String(result.detail||"Could not create the vehicle."));
        return;
      }
      router.push("/dashboard/inventory");
      router.refresh();
    }catch{
      setError("The connection failed. Your vehicle was not confirmed as saved; check inventory before trying again.");
    }finally{setBusy(false)}
  }

  return <form className="panel createVehicleForm" onSubmit={submit}>
    <p>Save the listing as a draft, add photographs from Inventory, then publish it when ready.</p>
    <div className="createVehicleGrid">
      <label><span>Make</span><input name="make" required maxLength={80} placeholder="Lexus"/></label>
      <label><span>Model</span><input name="model" required maxLength={100} placeholder="RX 350"/></label>
      <label><span>Year</span><input name="year" type="number" min="1900" max="2100" required/></label>
      <label><span>Price (NGN)</span><input name="price" type="number" min="0" step="0.01" required/></label>
      <label><span>Mileage (km)</span><input name="mileage_km" type="number" min="0" required/></label>
      <label><span>Transmission</span><input name="transmission" required placeholder="Automatic"/></label>
      <label><span>Fuel type</span><input name="fuel_type" required placeholder="Petrol"/></label>
      <label><span>Condition (dealer provided)</span><input name="condition" required placeholder="Foreign used"/></label>
      <label><span>Location</span><input name="location" required placeholder="Lagos"/></label>
      <label><span>Video URL (optional)</span><input name="video_url" type="url" placeholder="https://"/></label>
    </div>
    <label><span>Description</span><textarea name="description" rows={5} required/></label>
    <label><span>Features (one per line)</span><textarea name="features" rows={3}/></label>
    <label><span>Known issues</span><textarea name="known_issues" rows={3}/></label>
    <label><span>Seller provided history</span><textarea name="seller_history" rows={3}/></label>
    <label className="createCheckbox"><input name="is_featured" type="checkbox"/> <span>Feature this vehicle on the dealer website</span></label>
    {error&&<p role="alert" className="loginError">{error}</p>}
    <button className="button dark" type="submit" disabled={busy}>{busy?"Saving…":"Save draft"} <span>↗</span></button>
  </form>;
}
