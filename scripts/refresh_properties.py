#!/usr/bin/env python3
from __future__ import annotations
import json, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
PROPS = DATA / "properties.json"
STATUS = DATA / "refresh-status.json"
REGISTRY = DATA / "county-sources.json"

COUNTIES = [
"Alachua","Baker","Bay","Bradford","Brevard","Broward","Calhoun","Charlotte","Citrus","Clay",
"Collier","Columbia","DeSoto","Dixie","Duval","Escambia","Flagler","Franklin","Gadsden","Gilchrist",
"Glades","Gulf","Hamilton","Hardee","Hendry","Hernando","Highlands","Hillsborough","Holmes","Indian River",
"Jackson","Jefferson","Lafayette","Lake","Lee","Leon","Levy","Liberty","Madison","Manatee","Marion","Martin",
"Miami-Dade","Monroe","Nassau","Okaloosa","Okeechobee","Orange","Osceola","Palm Beach","Pasco","Pinellas",
"Polk","Putnam","Santa Rosa","Sarasota","Seminole","St. Johns","St. Lucie","Sumter","Suwannee","Taylor","Union",
"Volusia","Wakulla","Walton","Washington"
]

# Verified official starting points. More county-specific property adapters can be added over time.
SOURCES = {
"Brevard":{"source_url":"https://www.brevardclerk.us/tax-deed-sales"},
"Broward":{"source_url":"https://www.broward.org/RecordsTaxesTreasury/Pages/Default.aspx","auction_url":"https://broward.realtaxdeed.com/"},
"Duval":{"source_url":"https://www.duvalclerk.gov/departments/county-services/tax-deed-files","auction_url":"https://duval.realtaxdeed.com/"},
"Flagler":{"source_url":"https://flaglerclerk.gov/sales/tax-deeds-sales/"},
"Lake":{"source_url":"https://www.lakecountyclerkfl.gov/departments/records-administrative-services/official-records/tax-deeds/","auction_url":"https://www.lake.realtaxdeed.com/"},
"Lee":{"source_url":"https://www.leeclerk.org/departments/courts/property-sales/tax-deed-sales"},
"Leon":{"source_url":"https://leonclerk.com/divisions/property-sales/tax-deeds/"},
"Miami-Dade":{"source_url":"https://www.miamidadeclerk.gov/clerk/property-tax-deeds.page?submit=true"},
"Volusia":{"source_url":"https://www.clerk.org/tax-deeds.aspx","auction_url":"https://www.volusia.realtaxdeed.com/"},
"Walton":{"source_url":"https://taxsmart.clerkofcourts.co.walton.fl.us/"}
}

UA = "TaxLienGuideBot/1.0 (daily public-record source check; no access-control bypass)"

def fetch(url, timeout=25):
    req = Request(url, headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml"})
    with urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Type",""), r.read(2_000_000)

def textify(raw):
    s = raw.decode("utf-8","replace")
    s = re.sub(r"(?is)<script.*?</script>|<style.*?</style>"," ",s)
    s = re.sub(r"(?s)<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",s).strip()

def num(v):
    if v in (None,""): return None
    try: return float(re.sub(r"[^0-9.\-]","",str(v)))
    except Exception: return None

def score(p):
    """Transparent research-priority score. This is not a buy recommendation."""
    points=50; reasons=[]
    av=num(p.get("assessed_value")); bid=num(p.get("opening_bid"))
    if av and bid and av>0:
        ratio=bid/av; p["bid_to_assessed_ratio"]=round(ratio,4)
        if ratio<=.10: points+=20; reasons.append("opening bid <=10% of assessed value")
        elif ratio<=.25: points+=10; reasons.append("opening bid <=25% of assessed value")
        elif ratio>=.70: points-=20; reasons.append("opening bid >=70% of assessed value")
    else: reasons.append("bid/value comparison incomplete")
    t=(p.get("property_type") or "").lower()
    if any(x in t for x in ("single family","residential","condo","townhouse")):
        points+=8; reasons.append("recognizable residential use")
    if any(x in t for x in ("strip","right of way","common area","wetland")):
        points-=20; reasons.append("possible difficult-use parcel")
    if p.get("homestead") is False:
        points+=4; reasons.append("non-homestead flag")
    elif p.get("homestead") is True:
        points-=6; reasons.append("homestead/occupancy needs extra review")
    if not p.get("parcel_id"): points-=15; reasons.append("missing parcel ID")
    if not p.get("official_url"): points-=15; reasons.append("missing official property source")
    if p.get("title_review_status") in (None,"unknown","not_reviewed"):
        points-=10; reasons.append("title/liens not reviewed")
    points=max(0,min(100,points))
    label="High research priority" if points>=70 else "Medium research priority" if points>=45 else "Low research priority"
    return {"score":points,"label":label,"reasons":reasons}

def main():
    now=datetime.now(timezone.utc).isoformat()
    registry=[]; health=[]
    for county in COUNTIES:
        src=SOURCES.get(county,{})
        entry={"state":"FL","county":county,"source_url":src.get("source_url"),"auction_url":src.get("auction_url"),
               "coverage":"source_registered" if src.get("source_url") else "research_needed"}
        registry.append(entry)
        row={"county":county,"source_url":entry["source_url"],"auction_url":entry["auction_url"],"checked_at":now,"ok":False,"http_status":None,"note":""}
        if not entry["source_url"]:
            row["note"]="Official source not yet normalized"
        else:
            try:
                st,ct,raw=fetch(entry["source_url"]); row["http_status"]=st; row["ok"]=200<=st<400
                txt=textify(raw).lower(); hints=[k for k in ("tax deed","auction","tax sale","lands available") if k in txt]
                row["note"]="Official page reachable"+(f"; detected: {', '.join(hints)}" if hints else "")
            except Exception as e:
                row["note"]=f"{type(e).__name__}: {str(e)[:150]}"
            time.sleep(.35)
        health.append(row)

    props=[]
    if PROPS.exists():
        try: props=json.loads(PROPS.read_text(encoding="utf-8")).get("properties",[])
        except Exception: props=[]
    for p in props: p["research_priority"]=score(p)

    REGISTRY.write_text(json.dumps({"updated_at":now,"state":"Florida","counties":registry},indent=2),encoding="utf-8")
    PROPS.write_text(json.dumps({"updated_at":now,"state":"Florida","properties":props},indent=2),encoding="utf-8")
    STATUS.write_text(json.dumps({
      "updated_at":now,"refresh_frequency":"daily","total_florida_counties":67,
      "official_sources_registered":sum(1 for x in registry if x["source_url"]),
      "property_count":len(props),"source_health":health,
      "notes":[
        "Properties are published only from official public sources that can be normalized without bypassing access controls.",
        "Research priority is a transparent screening score, not investment advice or a buy recommendation."
      ]},indent=2),encoding="utf-8")

if __name__=="__main__": main()
