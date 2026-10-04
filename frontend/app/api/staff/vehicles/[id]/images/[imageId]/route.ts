import {sameOrigin} from "@/lib/security";
import {cookies} from "next/headers";
import {NextRequest,NextResponse} from "next/server";
const api=process.env.API_INTERNAL_URL||"http://127.0.0.1:8000";
function host(request:NextRequest){return process.env.DEALER_HOST_OVERRIDE||request.headers.get("x-forwarded-host")||request.headers.get("host")||"atelier.localhost"}
async function forward(request:NextRequest,params:Promise<{id:string;imageId:string}>,method:"PATCH"|"DELETE"){if(!sameOrigin(request))return NextResponse.json({detail:"Cross-origin request blocked."},{status:403});
  const {id,imageId}=await params;const token=(await cookies()).get("dealer_token")?.value;
  if(!token)return NextResponse.json({detail:"Authentication required."},{status:401});
  const upstream=await fetch(`${api}/api/v1/staff/vehicles/${id}/images/${imageId}/`,{method,headers:{...(method==="PATCH"?{"Content-Type":"application/json"}:{}),"X-Dealer-Host":host(request),Authorization:`Token ${token}`},...(method==="PATCH"?{body:await request.text()}:{}),cache:"no-store"});
  return NextResponse.json(await upstream.json(),{status:upstream.status});
}
export async function PATCH(request:NextRequest,{params}:{params:Promise<{id:string;imageId:string}>}){return forward(request,params,"PATCH")}
export async function DELETE(request:NextRequest,{params}:{params:Promise<{id:string;imageId:string}>}){return forward(request,params,"DELETE")}
