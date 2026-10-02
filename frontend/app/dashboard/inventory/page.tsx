import Link from "next/link";
import {redirect} from "next/navigation";
import {DashboardNav} from "@/components/DashboardNav";
import {InventoryManager} from "@/components/InventoryManager";
import {getOverview,getStaffVehicles} from "@/lib/api";

type Params=Record<string,string|string[]|undefined>;
function value(input:string|string[]|undefined){return Array.isArray(input)?input[0]||"":input||""}
function pageHref(params:Params,page:number){const query=new URLSearchParams();for(const key of ["q","publication","availability"]){const item=value(params[key]);if(item)query.set(key,item)}if(page>1)query.set("page",String(page));return `/dashboard/inventory${query.size?`?${query}`:""}`}

export default async function StaffInventory({searchParams}:{searchParams:Promise<Params>}){
  const params=await searchParams;const query=new URLSearchParams();for(const key of ["q","publication","availability","page"]){const item=value(params[key]);if(item)query.set(key,item)}
  let overview,data;try{[overview,data]=await Promise.all([getOverview(),getStaffVehicles(query.toString())])}catch{redirect("/dashboard/login")}
  const start=data.count?(data.page-1)*data.page_size+1:0;const end=Math.min(data.page*data.page_size,data.count);const pages=Array.from({length:data.pages},(_,index)=>index+1).filter(page=>page===1||page===data.pages||Math.abs(page-data.page)<=2);
  return <><DashboardNav dealer={overview.dealer}/><main id="main" className="dashMain"><header className="dashHead"><div><span className="eyebrow">Stock</span><h1>Inventory controls</h1><p>Find and manage listings without loading the entire catalogue at once.</p></div></header>
    <form className="adminInventoryFilters" method="get"><label className="adminSearch"><span>Search inventory</span><input type="search" name="q" defaultValue={value(params.q)} placeholder="Make, model, location or listing slug"/></label><label><span>Website state</span><select name="publication" defaultValue={value(params.publication)}><option value="">All states</option><option value="published">Published</option><option value="draft">Draft</option><option value="unpublished">Unpublished</option></select></label><label><span>Availability</span><select name="availability" defaultValue={value(params.availability)}><option value="">Any availability</option><option value="available">Available</option><option value="reserved">Reserved</option><option value="sold">Sold</option></select></label><button className="button dark" type="submit">Find vehicles <span>→</span></button>{(value(params.q)||value(params.publication)||value(params.availability))&&<Link className="clearAdminFilters" href="/dashboard/inventory">Clear filters</Link>}</form>
    <div className="inventoryResultBar"><span>Showing <strong>{start}–{end}</strong> of <strong>{data.count}</strong> vehicles</span><small>12 listings per page</small></div>
    {data.results.length?<InventoryManager key={`${data.page}-${query}`} initial={data.results}/>:<div className="adminEmpty"><span className="eyebrow">No matching listings</span><h2>Nothing found.</h2><p>Try a broader search or clear the current filters.</p><Link className="lineLink" href="/dashboard/inventory">Show all inventory</Link></div>}
    {data.pages>1&&<nav className="adminPagination" aria-label="Inventory pages"><Link className={!data.has_previous?"isDisabled":""} aria-disabled={!data.has_previous} href={pageHref(params,Math.max(1,data.page-1))}>← Previous</Link><div>{pages.map((page,index)=><span key={page}>{index>0&&page-pages[index-1]>1&&<i>…</i>}<Link className={page===data.page?"isCurrent":""} aria-current={page===data.page?"page":undefined} href={pageHref(params,page)}>{String(page).padStart(2,"0")}</Link></span>)}</div><Link className={!data.has_next?"isDisabled":""} aria-disabled={!data.has_next} href={pageHref(params,Math.min(data.pages,data.page+1))}>Next →</Link></nav>}
  </main></>
}
