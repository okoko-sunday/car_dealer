import type {Metadata} from "next";import "@fontsource-variable/manrope";import "@fontsource-variable/newsreader";import "./globals.css";
export const metadata:Metadata={title:{default:"Atelier Motors",template:"%s — Atelier Motors"},description:"Considered cars, clearly presented.",robots:{index:true,follow:true}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><a className="skip" href="#main">Skip to content</a>{children}</body></html>}
