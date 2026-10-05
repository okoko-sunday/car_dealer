import {NextRequest} from "next/server";

export function sameOrigin(request:NextRequest):boolean{
  const origin=request.headers.get("origin");
  if(!origin)return true; // Non-browser clients may omit Origin.
  try{
    return new URL(origin).host===request.headers.get("host");
  }catch{return false}
}
