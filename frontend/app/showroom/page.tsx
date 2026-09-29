import type {Metadata} from "next";
import Link from "next/link";
import {Footer} from "@/components/Footer";
import {Header} from "@/components/Header";
import {getDealer,getVehicles} from "@/lib/api";

export const metadata:Metadata={title:"Showroom",description:"Visit the Atelier Motors showroom in Lagos, review opening hours, and arrange a private viewing."};

export default async function Showroom(){
  const [dealer,vehicles]=await Promise.all([getDealer(),getVehicles()]);
  const available=vehicles.filter(vehicle=>vehicle.availability==="available").length;
  const phoneHref=`tel:${dealer.phone.replace(/\s/g,"")}`;
  const whatsappHref=`https://wa.me/${dealer.whatsapp.replace(/\D/g,"")}`;
  return <>
    <Header dealer={dealer}/>
    <main id="main" className="showroomPage">
      <section className="showroomHero">
        <div className="showroomHeroCopy">
          <span className="eyebrow light">The showroom · Lagos</span>
          <h1>Come for a<br/><span className="accentWord">closer look.</span></h1>
          <p>A calm, unhurried place to experience the details, ask direct questions, and decide at your own pace.</p>
        </div>
        <div className="showroomMonogram" aria-hidden="true"><span>A</span><span>M</span></div>
        <div className="showroomHeroFoot"><span>Private viewings available</span><span>{String(available).padStart(2,"0")} vehicles available</span><span>Lagos, Nigeria</span></div>
      </section>
      <section className="showroomDetails">
        <div><span className="eyebrow">Plan your visit · 01</span><h2>Good decisions<br/>need <span className="accentWord">room.</span></h2></div>
        <div className="visitDetails">
          <article><span>Address</span><p>{dealer.address}</p><a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(dealer.address)}`} target="_blank" rel="noreferrer">Open in maps ↗</a></article>
          <article><span>Opening hours</span><p>{dealer.opening_hours}</p><small>Appointments are recommended so the vehicle can be prepared before you arrive.</small></article>
          <article><span>Speak with us</span><p><a href={phoneHref}>{dealer.phone}</a><br/><a href={`mailto:${dealer.email}`}>{dealer.email}</a></p><a href={whatsappHref} target="_blank" rel="noreferrer">Continue on WhatsApp ↗</a></article>
        </div>
      </section>
      <section className="showroomPromise">
        <span className="eyebrow light">What to expect · 02</span>
        <div className="promiseGrid"><article><b>01</b><h3>Prepared arrival</h3><p>Tell us which car interests you and we will have it ready for a considered walk-around.</p></article><article><b>02</b><h3>Useful answers</h3><p>Review dealer-provided history, known issues, documentation, and the details that matter to you.</p></article><article><b>03</b><h3>No rushed decision</h3><p>A viewing or offer starts a conversation. Neither completes a sale or creates a hidden commitment.</p></article></div>
      </section>
      <section className="showroomClosing"><div><span className="eyebrow">Your next step · 03</span><h2>Choose what<br/>to see first.</h2></div><div><p>Browse the current collection, then contact the team to reserve a convenient viewing time.</p><Link className="button dark" href="/inventory">Explore the collection <span>↗</span></Link></div></section>
    </main>
    <Footer dealer={dealer}/>
  </>
}
