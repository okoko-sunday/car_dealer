"use client";

import Link from "next/link";
import {useEffect, useState} from "react";
import type {Dealer} from "@/lib/types";

export function Header({dealer}:{dealer:Dealer}){
  const [open,setOpen]=useState(false);
  const [departing,setDeparting]=useState(false);
  const [session,setSession]=useState<{authenticated:boolean;user?:{name:string;role:string}}>({authenticated:false});
  const initials=dealer.name.split(" ").map(x=>x[0]).join("").slice(0,2);

  useEffect(()=>{
    document.body.classList.toggle("menuOpen",open);
    return ()=>document.body.classList.remove("menuOpen");
  },[open]);
  useEffect(()=>{let active=true;fetch("/api/session",{cache:"no-store"}).then(response=>response.json()).then(data=>{if(active)setSession(data)}).catch(()=>{});return()=>{active=false}},[]);

  function close(){setOpen(false)}
  function animateDeparture(){setDeparting(true);window.setTimeout(()=>setDeparting(false),650)}

  return <header className="siteHeader">
    <Link className="brandLockup" href="/" aria-label={`${dealer.name} home`} onClick={close}>
      <span className={`brandMark ${dealer.logo_url?"hasLogo":""}`}>{dealer.logo_url?<img src={dealer.logo_url} alt=""/>:initials}</span>
      <span className="wordmark">{dealer.name}<small>Independent motor atelier</small></span>
    </Link>
    <nav className="desktopNav" aria-label="Main navigation">
      <Link href="/inventory">Inventory</Link>
      <Link href="/#approach">Our approach</Link>
      <Link href="/showroom">Visit showroom</Link>
    </nav>
    {session.authenticated&&<Link className="sessionDashboard" href="/dashboard"><span>Dashboard</span><b aria-hidden="true">↗</b></Link>}
    <Link className={`headerCta ${departing?"isDeparting":""}`} href="/inventory" onClick={animateDeparture}>
      <span className="ctaWords"><span>Browse inventory</span><span>View full catalogue</span></span>
      <b aria-hidden="true">↗</b>
    </Link>
    <button className={`menuToggle ${open?"isOpen":""}`} type="button" aria-expanded={open} aria-controls="mobile-menu" aria-label={open?"Close navigation":"Open navigation"} onClick={()=>setOpen(v=>!v)}>
      <span/><span/><span/>
    </button>
    <div className={`mobileMenu ${open?"isOpen":""}`} id="mobile-menu" aria-hidden={!open}>
      <div className="mobileMenuInner">
        <span className="menuKicker">Navigate / {dealer.name}</span>
        <nav aria-label="Mobile navigation">
          <Link href="/" onClick={close}><small>01</small><span>Home</span><b>↗</b></Link>
          <Link href="/inventory" onClick={close}><small>02</small><span>Inventory</span><b>↗</b></Link>
          <Link href="/#approach" onClick={close}><small>03</small><span>Our approach</span><b>↗</b></Link>
          <Link href="/showroom" onClick={close}><small>04</small><span>Visit showroom</span><b>↗</b></Link>
          {session.authenticated&&<Link className="mobileDashboardLink" href="/dashboard" onClick={close}><small>05</small><span>Dashboard</span><b>↗</b></Link>}
        </nav>
        <div className="mobileMenuFoot"><span>{session.authenticated?`Signed in · ${session.user?.name||"Dealer staff"}`:dealer.address}</span><a href={`tel:${dealer.phone}`}>{dealer.phone}</a></div>
      </div>
    </div>
  </header>
}
