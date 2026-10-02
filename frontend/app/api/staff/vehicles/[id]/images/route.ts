import {cookies} from "next/headers";
import {NextRequest,NextResponse} from "next/server";
const api=process.env.API_INTERNAL_URL||"http://127.0.0.1:8000";
function host(request:NextRequest){return process.env.DEALER_HOST_OVERRIDE||request.headers.get("x-forwarded-host")||request.headers.get("host")||"atelier.localhost"}
export async function POST(request:NextRequest,{params}:{params:Promise<{id:string}>}){
  const {id}=await params;const token=(await cookies()).get("dealer_token")?.value;
  if(!token)return NextResponse.json({detail:"Authentication required."},{status:401});
  const upstream=await fetch(`${api}/api/v1/staff/vehicles/${id}/images/`,{method:"POST",headers:{"X-Dealer-Host":host(request),Authorization:`Token ${token}`},body:await request.formData(),cache:"no-store"});
  return NextResponse.json(await upstream.json(),{status:upstream.status});
}
