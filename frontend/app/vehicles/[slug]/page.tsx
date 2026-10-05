import Link from "next/link";
import {notFound} from "next/navigation";
import {Footer} from "@/components/Footer";
import {Header} from "@/components/Header";
import {InquiryForm} from "@/components/InquiryForm";
import {VehicleInquiryModal} from "@/components/VehicleInquiryModal";
import {VehicleCard} from "@/components/VehicleCard";
import {getDealer,getVehicle,getVehicles} from "@/lib/api";
import type {Vehicle} from "@/lib/types";

const money=(value:string)=>new Intl.NumberFormat("en-NG",{style:"currency",currency:"NGN",maximumFractionDigits:0}).format(Number(value));
function relatedVehicles(current:Vehicle,vehicles:Vehicle[]){const price=Number(current.price);return vehicles.filter(item=>item.id!==current.id&&item.availability==="available").sort((a,b)=>{const sameMakeA=a.make.toLowerCase()===current.make.toLowerCase()?1:0;const sameMakeB=b.make.toLowerCase()===current.make.toLowerCase()?1:0;if(sameMakeA!==sameMakeB)return sameMakeB-sameMakeA;const priceGap= Math.abs(Number(a.price)-price)-Math.abs(Number(b.price)-price);if(priceGap!==0)return priceGap;return new Date(b.created_at).getTime()-new Date(a.created_at).getTime()}).slice(0,3)}

export default async function Detail({params}:{params:Promise<{slug:string}>}){
  const {slug}=await params;
  try{
    const [dealer,vehicle,vehicles]=await Promise.all([getDealer(),getVehicle(slug),getVehicles()]);const related=relatedVehicles(vehicle,vehicles);
    return <><Header dealer={dealer}/><main id="main" className="vehiclePage" style={{"--brand":dealer.primary_color} as React.CSSProperties}>
      <div className="detailCrumb"><Link href="/inventory">Inventory</Link><span>/</span><span>{vehicle.make} {vehicle.model}</span></div>
      <section className="detailHero"><div className="detailGallery">{vehicle.images.length?vehicle.images.map((image,index)=><figure key={image.id} className={index===0?"primary":""}><img src={image.url} alt={image.alt_text}/><figcaption>{String(index+1).padStart(2,"0")} / {String(vehicle.images.length).padStart(2,"0")}</figcaption></figure>):<div className="placeholder large">{vehicle.make[0]}</div>}</div><aside className="summary"><div><span className={`status ${vehicle.availability}`}>{vehicle.availability}</span><span className="eyebrow">{vehicle.year} · {vehicle.condition}</span><h1>{vehicle.make}<br/><span className="accentWord">{vehicle.model}</span></h1></div><div><div className="price">{money(vehicle.price)}</div><p className="priceNote">Dealer asking price · subject to conversation</p><VehicleInquiryModal slug={slug} title={vehicle.title} price={money(vehicle.price)} sold={vehicle.availability==="sold"}/></div><dl><div><dt>Mileage</dt><dd>{vehicle.mileage_km.toLocaleString()} km</dd></div><div><dt>Transmission</dt><dd>{vehicle.transmission}</dd></div><div><dt>Power</dt><dd>{vehicle.fuel_type}</dd></div><div><dt>Location</dt><dd>{vehicle.location}</dd></div></dl></aside></section>
      <section className="detailNarrative"><div><span className="eyebrow">The overview · 01</span><h2>A closer<br/><span className="accentWord">look.</span></h2></div><div className="narrativeCopy"><p className="leadCopy">{vehicle.description}</p><div className="detailColumns"><div><h3>Notable specification</h3><ul>{vehicle.features.map(feature=><li key={feature}>{feature}</li>)}</ul></div><div><h3>Known issues</h3><p>{vehicle.known_issues||"The dealer has not listed known issues. Ask for current condition details."}</p><h3>Seller-provided history</h3><p>{vehicle.seller_history||"No seller history has been supplied."}</p></div></div></div></section>
      {related.length>0&&<section className="relatedSection"><div className="relatedHead"><div><span className="eyebrow">From the inventory · 02</span><h2>Also worth<br/><span className="accentWord">a look.</span></h2></div><div><p>{vehicle.availability==="sold"?"This vehicle has sold, but these available alternatives remain in the dealer’s inventory.":"Available alternatives selected by make, asking-price proximity, and recency."}</p><Link className="lineLink" href="/inventory">Browse full inventory <b>↗</b></Link></div></div><div className={`relatedGrid count${related.length}`}>{related.map((item,index)=><VehicleCard key={item.id} vehicle={item} index={index}/>)}</div></section>}
      <section className="requestSection" id="enquire"><div><span className="eyebrow light">Private viewing · 03</span><h2>{vehicle.availability==="sold"?"Find something equally considered.":"Experience it yourself."}</h2><p>Tell us how you would like to continue. A member of the team will confirm the next step personally—no request reserves or purchases a vehicle.</p></div><InquiryForm slug={slug} sold={vehicle.availability==="sold"}/></section>
    </main><Footer dealer={dealer}/></>
  }catch{return notFound()}
}
