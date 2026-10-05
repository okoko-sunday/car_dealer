import {redirect} from "next/navigation";
import {DashboardNav} from "@/components/DashboardNav";
import {DealerSettingsForm} from "@/components/DealerSettingsForm";
import {getOverview} from "@/lib/api";

export default async function WebsiteSettings(){
  let overview;try{overview=await getOverview()}catch{redirect("/dashboard/login")}
  if(!["owner","manager"].includes(overview.user.role))redirect("/dashboard");
  return <div className="workspace"><DashboardNav dealer={overview.dealer}/><main id="main" className="dashMain settingsPage" style={{"--brand":overview.dealer.primary_color,"--accent":overview.dealer.accent_color} as React.CSSProperties}>
    <header className="dashHead"><div><span className="eyebrow">Website / Configuration</span><h1>Make it<br/><span className="accentWord">distinctly yours.</span></h1><p>One source of truth for your public identity, contact details, and visual character.</p></div><div className="dashHeadActions"><span>Owner and manager access</span><a className="button dark" href="/" target="_blank">Preview website <b>↗</b></a></div></header>
    <DealerSettingsForm dealer={overview.dealer}/>
  </main></div>;
}
