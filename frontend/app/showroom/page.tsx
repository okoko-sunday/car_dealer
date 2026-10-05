import type {Metadata} from "next";
import Link from "next/link";
import {Footer} from "@/components/Footer";
import {Header} from "@/components/Header";
import {ShowroomFilters} from "@/components/ShowroomFilters";
import {VehicleCard} from "@/components/VehicleCard";
import {getDealer,getVehiclePage} from "@/lib/api";

export const metadata:Metadata={title:"Visit showroom",description:"Browse vehicles available to view now, find the showroom, and arrange a private appointment."};

type Params=Record<string,string|string[]|undefined>;
function value(input:string|string[]|undefined){return Array.isArray(input)?input[0]||"":input||""}
function pageHref(params:Params,page:number){const query=new URLSearchParams();for(const key of ["q","make","transmission","sort"]){const item=value(params[key]);if(item&&!(key==="sort"&&item==="newest"))query.set(key,item)}if(page>1)query.set("page",String(page));return `/showroom${query.size?`?${query}`:""}`}

export default async function Showroom({searchParams}:{searchParams:Promise<Params>}){
  const params=await searchParams;const query=new URLSearchParams({availability:"available"});for(const key of ["q","make","transmission","sort","page"]){const item=value(params[key]);if(item)query.set(key,item)}
  const [dealer,data]=await Promise.all([getDealer(),getVehiclePage(query.toString())]);
  const available=data.results;
  const lead=available.find(vehicle=>vehicle.is_featured)||available[0];
  const start=data.count?(data.page-1)*data.page_size+1:0;const end=Math.min(data.page*data.page_size,data.count);
  const pages=Array.from({length:data.pages},(_,index)=>index+1).filter(page=>page===1||page===data.pages||Math.abs(page-data.page)<=2);
  const phoneHref=`tel:${dealer.phone.replace(/\s/g,"")}`;
  const whatsappHref=`https://wa.me/${dealer.whatsapp.replace(/\D/g,"")}`;
  return <>
    <Header dealer={dealer}/>
    <main id="main" className="showroomPage" style={{"--brand":dealer.primary_color,"--accent":dealer.accent_color} as React.CSSProperties}>
      <section className="showroomHero">
        <div className="showroomHeroCopy">
          <span className="eyebrow light">Visit showroom · {dealer.name}</span>
          <h1>Available to view,<br/><span className="accentWord">here and now.</span></h1>
          <p>This page is for visiting the physical showroom: see cars currently available for viewing, check our location and hours, then arrange an appointment.</p>
          <a className="button light" href="#available-vehicles">Cars available to view <span>↓</span></a>
        </div>
        {lead?.images[0]?<div className="showroomHeroVehicle" aria-hidden="true"><img src={lead.images[0].url} alt=""/><span/></div>:<div className="showroomMonogram" aria-hidden="true"><span>{dealer.name.split(" ")[0]?.[0]||"D"}</span><span>{dealer.name.split(" ")[1]?.[0]||""}</span></div>}
        <div className="showroomHeroFoot"><span>Physical showroom &amp; appointments</span><span>{String(data.count).padStart(2,"0")} cars available to view</span><span>{dealer.address}</span></div>
      </section>
      <section className="showroomCollection" id="available-vehicles">
        <div className="showroomCollectionHead"><div><span className="eyebrow">Available to view · 01</span><h2>Here now.<br/><span className="accentWord">Ready when you are.</span></h2></div><div><p>Only vehicles currently marked Available appear here. Reserved and Sold cars remain in the full Inventory but are not presented as ready for a showroom appointment.</p><Link className="lineLink" href="/inventory">Browse full inventory <b>↗</b></Link></div></div>
        <ShowroomFilters initialQuery={value(params.q)} initialMake={value(params.make)} initialTransmission={value(params.transmission)} initialSort={value(params.sort)||"newest"} makes={data.filters.makes} transmissions={data.filters.transmissions}/>
        <div className="showroomResultBar" aria-live="polite"><span>{data.count?<>Showing <strong>{start}–{end}</strong> of <strong>{data.count}</strong> available vehicles</>:"No available vehicles match these filters"}</span><small>12 vehicles per page</small></div>
        {available.length?<><div className="showroomVehicleGrid">{available.map((vehicle,index)=><VehicleCard key={vehicle.id} vehicle={vehicle} index={index}/>)}</div>{data.pages>1&&<nav className="showroomPagination adminPagination" aria-label="Showroom pages"><Link className={!data.has_previous?"isDisabled":""} aria-disabled={!data.has_previous} href={pageHref(params,Math.max(1,data.page-1))}>← Previous</Link><div>{pages.map((page,index)=><span key={page}>{index>0&&page-pages[index-1]>1&&<i>…</i>}<Link className={page===data.page?"isCurrent":""} aria-current={page===data.page?"page":undefined} href={pageHref(params,page)}>{String(page).padStart(2,"0")}</Link></span>)}</div><Link className={!data.has_next?"isDisabled":""} aria-disabled={!data.has_next} href={pageHref(params,Math.min(data.pages,data.page+1))}>Next →</Link></nav>}</>:<div className="showroomEmpty"><span className="eyebrow">No matching vehicles</span><h2>Nothing fits those filters.</h2><p>Try a broader search, reset the filters, or contact the showroom and tell us what you are looking for.</p><div><Link className="button dark" href="/showroom">Reset showroom <span>↗</span></Link><a className="lineLink" href={phoneHref}>Call the showroom <b>↗</b></a></div></div>}
      </section>
      <section className="showroomDetails">
        <div><span className="eyebrow">Plan your visit · 02</span><h2>Good decisions<br/>need <span className="accentWord">room.</span></h2></div>
        <div className="visitDetails">
          <article><span>Address</span><p>{dealer.address}</p><a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(dealer.address)}`} target="_blank" rel="noreferrer">Open in maps ↗</a></article>
          <article><span>Opening hours</span><p>{dealer.opening_hours}</p><small>Appointments are recommended so the vehicle can be prepared before you arrive.</small></article>
          <article><span>Speak with us</span><p><a href={phoneHref}>{dealer.phone}</a><br/><a href={`mailto:${dealer.email}`}>{dealer.email}</a></p><a href={whatsappHref} target="_blank" rel="noreferrer">Continue on WhatsApp ↗</a></article>
        </div>
      </section>
      <section className="showroomPromise">
        <span className="eyebrow light">What to expect · 03</span>
        <div className="promiseGrid"><article><b>01</b><h3>Prepared arrival</h3><p>Tell us which car interests you and we will have it ready for a considered walk-around.</p></article><article><b>02</b><h3>Useful answers</h3><p>Review dealer-provided history, known issues, documentation, and the details that matter to you.</p></article><article><b>03</b><h3>No rushed decision</h3><p>A viewing or offer starts a conversation. Neither completes a sale or creates a hidden commitment.</p></article></div>
      </section>
      <section className="showroomClosing"><div><span className="eyebrow">Your next step · 04</span><h2>Seen something<br/>worth meeting?</h2></div><div><p>Open the vehicle and arrange a convenient viewing, or speak with the team if you would like help narrowing the available inventory.</p><a className="button dark" href={phoneHref}>Speak with the showroom <span>↗</span></a></div></section>
    </main>
    <Footer dealer={dealer}/>
  </>
}
