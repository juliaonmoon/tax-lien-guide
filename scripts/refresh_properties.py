#!/usr/bin/env python3
from __future__ import annotations

import io, json, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROPS = DATA / "properties.json"
STATUS = DATA / "refresh-status.json"
REGISTRY = DATA / "county-sources.json"
DATA.mkdir(exist_ok=True)

UA = "TaxLienGuideBot/1.5 (daily public-record research prototype; no access-control bypass)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/json"}
TODAY = datetime.now(timezone.utc).date()

KING_HUMAN="https://kingcounty.gov/en/dept/executive-services/buildings-property/treasury-operations/tax-foreclosures/auctions"
SOURCES = [
    {"state":"FL","state_name":"Florida","county":"Brevard","source_url":"https://www.brevardclerk.us/tax-deed-sales","auction_url":"https://www.brevard.realforeclose.com/","collector":"brevard"},
    {"state":"TX","state_name":"Texas","county":"Tarrant","source_url":"https://www.tarrantcountytx.gov/en/constables/constable-3/delinquent-tax-sales/monthly-tax-sales-listings.html","auction_url":None,"collector":"tarrant"},
    {"state":"WA","state_name":"Washington","county":"King","source_url":"https://data.kingcounty.gov/Property-Assessments/Foreclosure-parcels/nx4x-daw6","feed_url":"https://data.kingcounty.gov/resource/nx4x-daw6.json","auction_url":"https://king.wa.realforeclose.com/","collector":"king"},
]


def get(url, timeout=30, **kwargs):
    headers=dict(HEADERS); headers.update(kwargs.pop("headers", {}) or {})
    r=requests.get(url, headers=headers, timeout=timeout, **kwargs); r.raise_for_status(); return r


def num(v):
    if v in (None, ""): return None
    try: return float(re.sub(r"[^0-9.\-]", "", str(v)))
    except Exception: return None


def parse_date(text):
    for fmt in ("%m/%d/%y","%m/%d/%Y","%B %d, %Y","%b %d, %Y"):
        try: return datetime.strptime(text.strip(), fmt).date()
        except ValueError: pass
    return None


def score(p):
    points, reasons = 50, []
    value=num(p.get("assessed_value") or p.get("market_value")); bid=num(p.get("opening_bid"))
    if value and bid and value>0:
        ratio=bid/value; p["bid_to_assessed_ratio"]=round(ratio,4)
        if ratio<=.10: points+=20; reasons.append("opening bid <=10% of appraisal value")
        elif ratio<=.25: points+=10; reasons.append("opening bid <=25% of appraisal value")
        elif ratio>=.70: points-=20; reasons.append("opening bid >=70% of appraisal value")
    elif value: reasons.append("official appraisal/tax-roll value captured; minimum bid not yet available")
    else: reasons.append("appraisal-value comparison not yet available")
    if p.get("opening_bid") is not None: points+=5; reasons.append("official opening/minimum bid captured")
    else: reasons.append(p.get("opening_bid_note") or "opening/minimum bid not published in this feed")
    t=(p.get("property_type") or "").lower()
    if any(x in t for x in ("residential","singlefamily","single family","condo","townhouse")): points+=5; reasons.append("recognizable residential property type")
    if any(x in t for x in ("right of way","vacant right","utility","road","tract")): points-=15; reasons.append("special-use parcel needs extra review")
    if p.get("sale_status","").lower() in {"active","for sale","foreclosure status"}: points+=5; reasons.append("currently listed by official source")
    if not p.get("parcel_id"): points-=15; reasons.append("missing parcel/account identifier")
    if not p.get("official_url"): points-=15; reasons.append("missing official source link")
    if p.get("title_review_status") in (None,"unknown","not_reviewed"): points-=10; reasons.append("title/surviving liens not reviewed")
    points=max(0,min(100,points))
    return {"score":points,"label":"High research priority" if points>=70 else "Medium research priority" if points>=45 else "Low research priority","reasons":reasons}


def tad_enrich(account):
    account=str(account).strip().zfill(8); url=f"https://www.tad.org/search-results?query={quote(account)}&searchType=AccountNumber"
    try: r=get(url,25)
    except Exception as e: return {}, f"TAD lookup failed: {type(e).__name__}"
    soup=BeautifulSoup(r.text,"html.parser"); row_cells=None
    for tr in soup.find_all("tr"):
        cells=[re.sub(r"\s+"," ",c.get_text(" ",strip=True)) for c in tr.find_all(["td","th"])]
        if account in cells: row_cells=cells; break
    if not row_cells: return {}, "No exact Tarrant Appraisal District match"
    idx=row_cells.index(account); tail=[x for x in row_cells[idx+1:] if x]
    if tail and re.fullmatch(r"\d{9}",tail[0]): tail=tail[1:]
    out={"appraisal_url":url,"appraisal_source":"Tarrant Appraisal District"}
    if len(tail)>=1: out["address"]=tail[0]
    if len(tail)>=2: out["city"]=tail[1]
    if out.get("address") and out.get("city"): out["address"]=f"{out['address']}, {out['city']}, TX"
    # Owner names are intentionally never collected in bulk (privacy convention,
    # see STATUS.md) even though TAD's public results table includes one at
    # tail[2] -- skip straight to market value.
    if len(tail)>=4:
        mv=num(tail[3])
        if mv is not None: out["market_value"]=mv; out["assessed_value"]=mv
    full=re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
    m=re.search(r"Legal Description:\s*(.+?)(?=\s+Agent:|\s+State Code:|$)",full,re.I)
    if m: out["legal_description"]=m.group(1).strip()
    m=re.search(r"State Code:\s*(.+?)(?=\s+Georeference:|\s+Subdivision:|\s+Neighborhood Code:|\s+Site Class Code:|$)",full,re.I)
    if m: out["property_type"]=m.group(1).strip()
    return out, "Enriched from Tarrant Appraisal District"


def brevard_properties():
    base=SOURCES[0]["source_url"]; soup=BeautifulSoup(get(base).text,"html.parser"); candidates=[]
    for a in soup.find_all("a",href=True):
        d=parse_date(a.get_text(" ",strip=True))
        if d and d>=TODAY and "tax-deed-sales" in a["href"]: candidates.append((d,urljoin(base,a["href"])))
    if not candidates: return [], "No upcoming Brevard tax-deed sale page found"
    sale_date,sale_page=sorted(candidates)[0]; sale_soup=BeautifulSoup(get(sale_page).text,"html.parser"); pdf_url=None
    for a in sale_soup.find_all("a",href=True):
        label=a.get_text(" ",strip=True).lower()
        if ".pdf" in label or "pdf" in a["href"].lower() or "file_id=" in a["href"].lower(): pdf_url=urljoin(sale_page,a["href"]); break
    if not pdf_url: return [], f"Upcoming Brevard sale {sale_date.isoformat()} found, but no official PDF list found"
    raw=get(pdf_url).content; rows=[]
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for rec in table:
                    vals=[re.sub(r"\s+"," ",(x or "")).strip() for x in rec]; joined=" | ".join(vals)
                    if not re.search(r"\bACTIVE\b",joined,re.I): continue
                    parcel=next((v for v in vals if re.fullmatch(r"\d{7,10}",v)),None)
                    if not parcel: continue
                    dates=[v for v in vals if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}",v)]
                    money_vals=[num(v) for v in vals if re.fullmatch(r"\$?[\d,]+(?:\.\d{1,2})?",v)]; plausible=[x for x in money_vals if x is not None and x>=100]
                    case=next((v for v in vals if re.fullmatch(r"\d{6}",v)),None)
                    rows.append({"state":"FL","state_name":"Florida","county":"Brevard","case_number":case,"parcel_id":parcel,"sale_date":dates[-1] if dates else sale_date.strftime("%m/%d/%Y"),"sale_status":"Active","opening_bid":plausible[-1] if plausible else None,"opening_bid_note":"Opening bid not parsed from sale list" if not plausible else None,"assessed_value":None,"market_value":None,"address":None,"owner":None,"property_type":None,"official_url":sale_page,"source_document":pdf_url,"auction_url":"https://www.brevard.realforeclose.com/","title_review_status":"not_reviewed","data_completeness":"auction list"})
    return rows, f"Parsed {len(rows)} properties from Brevard official sale list for {sale_date.isoformat()}"


def tarrant_properties():
    base=SOURCES[1]["source_url"]; soup=BeautifulSoup(get(base).text,"html.parser"); candidates=[]
    for a in soup.find_all("a",href=True):
        d=parse_date(a.get_text(" ",strip=True).title())
        if d and d>=TODAY: candidates.append((d,urljoin(base,a["href"])))
    if not candidates: candidates=[(datetime(2026,9,1).date(),"https://www.tarrantcountytx.gov/en/constables/constable-3/delinquent-tax-sales/monthly-tax-sales-listings/september-1--2026.html")]
    sale_date,sale_url=sorted(candidates)[0]; psoup=BeautifulSoup(get(sale_url).text,"html.parser"); rows=[]; enriched=0
    for tr in psoup.find_all("tr"):
        c=[re.sub(r"\s+"," ",x.get_text(" ",strip=True)) for x in tr.find_all(["td","th"])]
        if len(c)<3: continue
        cause,account,status=c[0],c[1],c[2]
        if not re.match(r"^[A-Z]?\d",cause) or not re.fullmatch(r"\d+",account) or "for sale" not in status.lower(): continue
        account=account.zfill(8); extra,note=tad_enrich(account)
        if extra: enriched+=1
        row={"state":"TX","state_name":"Texas","county":"Tarrant","case_number":cause,"parcel_id":account,"sale_date":sale_date.strftime("%m/%d/%Y"),"sale_status":status,"opening_bid":None,"opening_bid_note":"Not published on Tarrant County's monthly sale listing","assessed_value":None,"market_value":None,"address":None,"owner":None,"property_type":None,"official_url":sale_url,"source_document":sale_url,"auction_url":None,"title_review_status":"not_reviewed","data_completeness":"sale listing + appraisal enrichment","enrichment_note":note}
        row.update(extra); rows.append(row); time.sleep(.15)
    return rows, f"Parsed {len(rows)} for-sale accounts; TAD enrichment matched {enriched}/{len(rows)}"


def socrata(dataset, params=None):
    return get(f"https://data.kingcounty.gov/resource/{dataset}.json",30,params=params or {},headers={"Accept":"application/json"}).json()


def king_enrich(parcel):
    out={"appraisal_url":f"https://gismaps.kingcounty.gov/parcelviewer2/?pin={parcel}","appraisal_source":"King County Assessor / Open Data","owner":"Not aggregated for WA investment screening"}; notes=[]
    try:
        legal=socrata("4854-i48r",{"$limit":5,"$where":f"parcel_number='{parcel}'"})
        if legal:
            out["legal_description"]=legal[0].get("legal_description"); out["account_number"]=legal[0].get("account_number"); notes.append("legal description")
    except Exception as e: notes.append(f"legal lookup {type(e).__name__}")
    try:
        account=out.get("account_number") or parcel
        tax=socrata("dkna-i698",{"$limit":200,"$where":f"account_number='{account}'"})
        if tax:
            def yr(x):
                try:return int(x.get("bill_year") or 0)
                except:return 0
            latest=max(tax,key=yr); lv=num(latest.get("land_value")) or 0; iv=num(latest.get("imps_value")) or 0
            if lv or iv:
                out["land_value"]=lv; out["improvement_value"]=iv; out["assessed_value"]=lv+iv; out["market_value"]=lv+iv; notes.append("tax-roll value")
            out["tax_status"]=latest.get("tax_status"); out["bill_year"]=latest.get("bill_year")
            billed=sum((num(x.get("billed_amount")) or 0) for x in tax); paid=sum((num(x.get("paid_amount")) or 0) for x in tax)
            out["tax_due_estimate"]=max(0,billed-paid); out["delinquent_years"]=sorted({x.get("bill_year") for x in tax if x.get("bill_year")}); notes.append("tax receivables")
    except Exception as e: notes.append(f"tax lookup {type(e).__name__}")
    return out, ", ".join(notes) if notes else "parcel listed; assessor enrichment unavailable"


def king_properties():
    data=socrata("nx4x-daw6",{"$limit":5000}); parcels=sorted({str(x.get("parcels") or "").strip() for x in data if re.fullmatch(r"\d{10}",str(x.get("parcels") or "").strip())})
    rows=[]; enriched=0
    for parcel in parcels:
        extra,note=king_enrich(parcel)
        if extra.get("assessed_value") or extra.get("legal_description"): enriched+=1
        p={"state":"WA","state_name":"Washington","county":"King","case_number":None,"parcel_id":parcel,"sale_date":"09/09/2026","sale_status":"Foreclosure status","opening_bid":None,"opening_bid_note":"King County says 2026 opening bids will be posted in mid-to-late August","assessed_value":None,"market_value":None,"address":None,"owner":"Not aggregated for WA investment screening","property_type":None,"official_url":KING_HUMAN,"source_document":"https://data.kingcounty.gov/Property-Assessments/Foreclosure-parcels/nx4x-daw6","auction_url":"https://king.wa.realforeclose.com/","title_review_status":"not_reviewed","data_completeness":"foreclosure list + King County open-data enrichment","enrichment_note":note,"property_viewer_url":f"https://gismaps.kingcounty.gov/parcelviewer2/?pin={parcel}"}
        p.update(extra); rows.append(p); time.sleep(.03)
    return rows, f"Parsed {len(rows)} King County foreclosure parcels; open-data enrichment matched {enriched}/{len(rows)}"


def prior_by_county():
    """Previously published rows for each (state, county), keyed for fallback.

    Each source in this script fully rebuilds its own rows every run. Without
    this, a transient fetch failure for one source silently erases that
    source's rows from the published file, with nothing to fall back on.
    """
    if not PROPS.exists():
        return {}
    try:
        doc = json.loads(PROPS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    result: dict[tuple, list] = {}
    for p in doc.get("properties", []):
        result.setdefault((p.get("state"), p.get("county")), []).append(p)
    return result


def main():
    now=datetime.now(timezone.utc).isoformat(); registry=[]; health=[]; properties=[]; collectors={"brevard":brevard_properties,"tarrant":tarrant_properties,"king":king_properties}
    previous = prior_by_county()
    for src in SOURCES:
        registry.append({"state":src["state"],"state_name":src["state_name"],"county":src["county"],"source_url":src["source_url"],"auction_url":src.get("auction_url"),"coverage":"property_feed_prototype"})
        h={"state":src["state"],"county":src["county"],"source_url":src["source_url"],"auction_url":src.get("auction_url"),"checked_at":now,"ok":False,"note":""}
        try:
            get(src.get("feed_url") or src["source_url"]); h["ok"]=True; rows,note=collectors[src["collector"]](); properties.extend(rows); h["note"]=note
        except Exception as e:
            retained = previous.get((src["state"], src["county"]), [])
            properties.extend(retained)
            h["note"]=f"{type(e).__name__}: {str(e)[:220]}; retained {len(retained)} prior rows"
            h["retained_previous_rows"]=bool(retained)
        health.append(h)
    for p in properties: p["research_priority"]=score(p)
    properties.sort(key=lambda x:(x.get("sale_date") or "",x.get("state") or "",x.get("county") or "",x.get("parcel_id") or ""))
    REGISTRY.write_text(json.dumps({"updated_at":now,"prototype":True,"counties":registry},indent=2),encoding="utf-8")
    PROPS.write_text(json.dumps({"updated_at":now,"prototype":True,"properties":properties},indent=2),encoding="utf-8")
    STATUS.write_text(json.dumps({"updated_at":now,"refresh_frequency":"daily","prototype":True,"states_tracked":len({x['state'] for x in SOURCES}),"counties_tracked":len(SOURCES),"official_sources_registered":len(registry),"property_count":len(properties),"source_health":health,"notes":["Prototype now prioritizes King County, Washington in addition to Brevard FL and Tarrant TX.","King County foreclosure parcels are enriched from King County Open Data for legal description, tax-roll value and receivable/tax information when available.","King County says 2026 opening bids will be posted in mid-to-late August; the collector will pick them up after an official source becomes available.","WA owner names are not bulk-aggregated into this investment screener because King County's eReal Property page warns that RCW 42.56.070(9) restricts use of lists of individuals for commercial purposes.","Research priority is a transparent triage score, not a recommendation to bid or purchase."]},indent=2),encoding="utf-8")

if __name__=="__main__": main()
