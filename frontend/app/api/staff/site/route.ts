import {sameOrigin} from "@/lib/security";
import {cookies} from "next/headers";
import {NextRequest,NextResponse} from "next/server";

const api=process.env.API_INTERNAL_URL||"http://127.0.0.1:8000";

export async function PATCH(request:NextRequest){
  if(!sameOrigin(request))return NextResponse.json({detail:"Cross-origin request blocked."},{status:403});
  const token=(await cookies()).get("dealer_token")?.value;
  if(!token)return NextResponse.json({detail:"Authentication required."},{status:401});
  const host=process.env.DEALER_HOST_OVERRIDE||request.headers.get("x-forwarded-host")||request.headers.get("host")||"atelier.localhost";
  const contentType=request.headers.get("content-type")||"application/octet-stream";
  const upstream=await fetch(`${api}/api/v1/staff/site/`,{method:"PATCH",headers:{"Content-Type":contentType,"X-Dealer-Host":host,Authorization:`Token ${token}`},body:await request.arrayBuffer(),cache:"no-store"});
  return NextResponse.json(await upstream.json(),{status:upstream.status});
}
