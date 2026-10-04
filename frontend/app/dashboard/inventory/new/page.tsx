import Link from "next/link";
import {redirect} from "next/navigation";
import {DashboardNav} from "@/components/DashboardNav";
import {CreateVehicleForm} from "@/components/CreateVehicleForm";
import {getOverview} from "@/lib/api";

export default async function NewVehicle(){
  let overview;
  try{overview=await getOverview()}catch{redirect("/dashboard/login")}
  if(!["owner","manager"].includes(overview.user.role))redirect("/dashboard/inventory");
  return <><DashboardNav dealer={overview.dealer}/><main id="main" className="dashMain">
    <header className="dashHead"><div><span className="eyebrow">Inventory / New vehicle</span><h1>Add a vehicle</h1><p>Enter the facts buyers need to make an informed decision.</p></div>
      <Link className="lineLink" href="/dashboard/inventory">Back to inventory</Link></header>
    <CreateVehicleForm/>
  </main></>;
}
