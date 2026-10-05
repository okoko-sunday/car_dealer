"use client";

import {FormEvent,useState} from "react";
import {useRouter} from "next/navigation";
import type {Dealer} from "@/lib/types";

export function DealerSettingsForm({dealer}:{dealer:Dealer}){
  const router=useRouter();
  const [busy,setBusy]=useState(false);
  const [message,setMessage]=useState("");
  const [error,setError]=useState("");
  const [logo,setLogo]=useState(dealer.logo_url);

  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();setBusy(true);setMessage("");setError("");
    try{
      const response=await fetch("/api/staff/site",{method:"PATCH",body:new FormData(event.currentTarget)});
      const result=await response.json() as Dealer&{detail?:string;[key:string]:unknown};
      if(!response.ok){
        const details=Object.entries(result).filter(([key])=>key!=="detail").map(([key,value])=>`${key.replaceAll("_"," ")}: ${Array.isArray(value)?value.join(", "):String(value)}`);
        setError(details.join(" · ")||result.detail||"The website settings could not be saved.");return;
      }
      setLogo(result.logo_url);setMessage("Website settings saved. The public site now uses these details.");router.refresh();
    }catch{setError("The connection failed. Your changes were not confirmed as saved.")}
    finally{setBusy(false)}
  }

  return <form className="settingsForm" onSubmit={submit}>
    <section className="panel settingsIdentity">
      <div className="settingsSectionHead"><div><span className="eyebrow">Identity · 01</span><h2>How buyers know you</h2></div><p>Your name and logo appear throughout your website. Use a clear PNG or WebP mark with enough breathing room.</p></div>
      <div className="logoEditor"><div className="logoPreview">{logo?<img src={logo} alt="Current dealer logo"/>:<span>{dealer.name.split(" ").map(x=>x[0]).join("").slice(0,2)}</span>}</div><label><span>Dealer logo</span><input name="logo" type="file" accept="image/png,image/jpeg,image/webp"/><small>PNG, JPEG or WebP · maximum 4 MB</small></label></div>
      <div className="settingsGrid"><label><span>Dealer name</span><input name="name" defaultValue={dealer.name} required maxLength={160}/></label><label><span>Tagline</span><input name="tagline" defaultValue={dealer.tagline} maxLength={240}/></label></div>
      <label><span>Dealer story</span><textarea name="story" defaultValue={dealer.story} rows={6}/></label>
    </section>
    <section className="panel">
      <div className="settingsSectionHead"><div><span className="eyebrow">Contact · 02</span><h2>Where conversations begin</h2></div><p>These details are shown publicly. Keep them current so buyers always reach the right team.</p></div>
      <div className="settingsGrid"><label><span>Email address</span><input name="email" type="email" defaultValue={dealer.email} required/></label><label><span>Telephone</span><input name="phone" type="tel" defaultValue={dealer.phone} required/></label><label><span>WhatsApp</span><input name="whatsapp" type="tel" defaultValue={dealer.whatsapp}/></label><label><span>Opening hours</span><input name="opening_hours" defaultValue={dealer.opening_hours} maxLength={240}/></label></div>
      <label><span>Showroom address</span><textarea name="address" defaultValue={dealer.address} rows={3} required/></label>
    </section>
    <section className="panel">
      <div className="settingsSectionHead"><div><span className="eyebrow">Brand system · 03</span><h2>Your site palette</h2></div><p>These restrained accents personalise the site while preserving contrast, typography, and the premium layout.</p></div>
      <div className="colourGrid"><label><span>Primary colour</span><div><input name="primary_color" type="color" defaultValue={dealer.primary_color}/><code>{dealer.primary_color}</code></div></label><label><span>Accent colour</span><div><input name="accent_color" type="color" defaultValue={dealer.accent_color}/><code>{dealer.accent_color}</code></div></label></div>
    </section>
    <div className="settingsSave"><div aria-live="polite">{error&&<p role="alert" className="loginError">{error}</p>}{message&&<p className="settingsSuccess">{message}</p>}</div><button className="button dark" type="submit" disabled={busy}>{busy?"Saving changes…":"Save website settings"}<span>↗</span></button></div>
  </form>;
}
