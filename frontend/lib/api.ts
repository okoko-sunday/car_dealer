import {headers,cookies} from "next/headers";
import type {Dealer,Overview,Vehicle,BuyerRequest,PaginatedVehicles} from "./types";
const api=process.env.API_INTERNAL_URL||process.env.NEXT_PUBLIC_API_URL||"http://127.0.0.1:8000";
export async function dealerHost(){const h=await headers();return process.env.DEALER_HOST_OVERRIDE||h.get("x-forwarded-host")||h.get("host")||"atelier.localhost"}
async function request<T>(path:string, authenticated=false):Promise<T>{const host=await dealerHost();const token=authenticated?(await cookies()).get("dealer_token")?.value:undefined;const response=await fetch(`${api}/api/v1${path}`,{headers:{"X-Dealer-Host":host,...(token?{Authorization:`Token ${token}`}:{})},cache:"no-store"});if(!response.ok)throw new Error(`${response.status}`);return response.json()}
export const getDealer=()=>request<Dealer>("/site/");
export const getVehicles=(query="")=>request<Vehicle[]>(`/vehicles/${query?`?${query}`:""}`);
export const getVehicle=(slug:string)=>request<Vehicle>(`/vehicles/${slug}/`);
export const getOverview=()=>request<Overview>("/staff/overview/",true);
export const getStaffVehicles=(query="")=>request<PaginatedVehicles>("/staff/vehicles/"+(query?"?"+query:""),true);
export const getStaffRequests=()=>request<BuyerRequest[]>("/staff/requests/",true);
export {api};
