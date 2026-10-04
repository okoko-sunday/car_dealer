import type {Metadata} from "next";
import "@fontsource-variable/manrope";
import "@fontsource-variable/newsreader";
import "./globals.css";
import {getDealer} from "@/lib/api";

export async function generateMetadata():Promise<Metadata>{
  try{
    const dealer=await getDealer();
    return {
      title:{default:dealer.name,template:`%s — ${dealer.name}`},
      description:dealer.tagline||`Browse available vehicles from ${dealer.name}.`,
      robots:{index:true,follow:true},
    };
  }catch{
    return {title:"Dealer showroom",robots:{index:false,follow:false}};
  }
}
export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en"><body><a className="skip" href="#main">Skip to content</a>{children}</body></html>;
}
