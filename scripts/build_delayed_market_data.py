#!/usr/bin/env python3
"""Generate a public 31+ day delayed NSE/BSE market snapshot after rights are confirmed."""
import csv, io, json, os, re, sys, zipfile
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

OUT="data/market-quotes.json"
MIN_LAG=31
INDIA=ZoneInfo("Asia/Kolkata")
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; FinSimIndia-Education/1.0)",
         "Accept":"text/csv,application/zip,application/json,*/*",
         "Referer":"https://www.bseindia.com/"}
COMPANIES=[
("ADANIENT","Adani Enterprises Ltd."),("ADANIPORTS","Adani Ports and Special Economic Zone Ltd."),
("APOLLOHOSP","Apollo Hospitals Enterprise Ltd."),("ASIANPAINT","Asian Paints Ltd."),
("AXISBANK","Axis Bank Ltd."),("BAJAJ-AUTO","Bajaj Auto Ltd."),("BAJAJFINSV","Bajaj Finserv Ltd."),
("BAJFINANCE","Bajaj Finance Ltd."),("BEL","Bharat Electronics Ltd."),("BHARTIARTL","Bharti Airtel Ltd."),
("BSE","BSE Ltd."),("CIPLA","Cipla Ltd."),("COALINDIA","Coal India Ltd."),
("DRREDDY","Dr. Reddy's Laboratories Ltd."),("EICHERMOT","Eicher Motors Ltd."),
("ETERNAL","Eternal Ltd."),("GRASIM","Grasim Industries Ltd."),("HCLTECH","HCL Technologies Ltd."),
("HDFCBANK","HDFC Bank Ltd."),("HDFCLIFE","HDFC Life Insurance Company Ltd."),
("HINDALCO","Hindalco Industries Ltd."),("HINDUNILVR","Hindustan Unilever Ltd."),
("ICICIBANK","ICICI Bank Ltd."),("INDIGO","InterGlobe Aviation Ltd."),("INFY","Infosys Ltd."),
("ITC","ITC Ltd."),("JIOFIN","Jio Financial Services Ltd."),("JSWSTEEL","JSW Steel Ltd."),
("KOTAKBANK","Kotak Mahindra Bank Ltd."),("LT","Larsen & Toubro Ltd."),
("M&M","Mahindra & Mahindra Ltd."),("MARUTI","Maruti Suzuki India Ltd."),
("MAXHEALTH","Max Healthcare Institute Ltd."),("NESTLEIND","Nestle India Ltd."),
("NTPC","NTPC Ltd."),("ONGC","Oil & Natural Gas Corporation Ltd."),
("POWERGRID","Power Grid Corporation of India Ltd."),("RELIANCE","Reliance Industries Ltd."),
("SBILIFE","SBI Life Insurance Company Ltd."),("SBIN","State Bank of India"),
("SHRIRAMFIN","Shriram Finance Ltd."),("SUNPHARMA","Sun Pharmaceutical Industries Ltd."),
("TATACONSUM","Tata Consumer Products Ltd."),("TATASTEEL","Tata Steel Ltd."),
("TCS","Tata Consultancy Services Ltd."),("TECHM","Tech Mahindra Ltd."),
("TITAN","Titan Company Ltd."),("TMPV","Tata Motors Passenger Vehicles Ltd."),
("TRENT","Trent Ltd."),("ULTRACEMCO","UltraTech Cement Ltd.")]
SYMBOLS={s for s,_ in COMPANIES}
def norm(v): return re.sub(r"[^a-z0-9]","",str(v or "").lower().replace("&","and"))
NAME_MAP={norm(re.sub(r"\b(limited|ltd|company|co|corporation|corp|india)\b","",n.lower())):s for s,n in COMPANIES}
def get(row,aliases):
    d={norm(k):v for k,v in row.items()}
    for a in aliases:
        v=d.get(norm(a))
        if v is not None and str(v).strip(): return str(v).strip()
    return ""
def num(v):
    try:
        s=str(v or "").strip().replace(",","").replace("%","")
        return float(s) if s and s not in ("-","--","NA","N/A") else None
    except ValueError: return None
def parsedate(v):
    value = str(v or "").strip()
    for candidate in (value, value[:10]):
        for f in ("%Y-%m-%d","%Y%m%d","%d-%b-%Y","%d/%m/%Y","%d-%m-%Y"):
            try: return datetime.strptime(candidate,f).date()
            except ValueError: pass
    return None
def fetch(url):
    with urlopen(Request(url,headers=HEADERS),timeout=45) as r: b=r.read()
    if not b or b.lstrip().lower().startswith((b"<html",b"<!doctype html")): raise RuntimeError("Empty or HTML response: "+url)
    return b
def rows(payload):
    if zipfile.is_zipfile(io.BytesIO(payload)):
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            names=[n for n in z.namelist() if n.lower().endswith(".csv")]
            if not names: raise RuntimeError("ZIP has no CSV file")
            payload=z.read(names[0])
    lines=payload.decode("utf-8-sig",errors="replace").splitlines()
    header=None
    for i,line in enumerate(lines[:30]):
        k={norm(x) for x in next(csv.reader([line]))}
        if (k&{"tckrsymb","symbol","scripcd","sccode","scname","indexname","index"}) and (k&{"clspric","close","closeprice","closingprice","closingindexvalue","closingvalue"}):
            header=i; break
    if header is None: raise RuntimeError("CSV headers not recognised")
    return list(csv.DictReader(io.StringIO("\n".join(lines[header:]))))
def symbol_for(r,exchange):
    raw=get(r,("TckrSymb","SYMBOL","Security Id","Scrip Code","SCRIP_CD","SC_CODE")).strip().upper()
    name=norm(get(r,("FinInstrmNm","SC_NAME","SCRIP_NAME","Security Name","Company Name","NAME")))
    # Keep the existing human-readable NIFTY 50 symbols where a BSE issuer can be
    # matched confidently. For the rest of BSE, use the exchange's unique scrip code.
    if exchange=="BSE":
        if name in NAME_MAP: return NAME_MAP[name]
        matches=[(len(k),v) for k,v in NAME_MAP.items() if len(name)>=8 and (k.startswith(name) or name.startswith(k))]
        if matches: return max(matches)[1]
        code=get(r,("SCRIP_CD","SC_CODE","Security Code","Scrip Code")).strip()
        return code or raw
    # NSE symbols are the exchange's searchable cash-equity identifiers.
    return raw if re.fullmatch(r"[A-Z0-9&._-]{1,30}",raw) else ""

SECTOR_BY_SYMBOL={
 "ADANIENT":"Other","ADANIPORTS":"Other","APOLLOHOSP":"Healthcare","ASIANPAINT":"Consumer",
 "AXISBANK":"Financial Services","BAJAJ-AUTO":"Automobile","BAJAJFINSV":"Financial Services",
 "BAJFINANCE":"Financial Services","BEL":"Other","BHARTIARTL":"Other","BSE":"Other","CIPLA":"Healthcare",
 "COALINDIA":"Power & Energy","DRREDDY":"Healthcare","EICHERMOT":"Automobile","ETERNAL":"Consumer",
 "GRASIM":"Other","HCLTECH":"Information Technology","HDFCBANK":"Financial Services",
 "HDFCLIFE":"Financial Services","HINDALCO":"Metals & Mining","HINDUNILVR":"Consumer",
 "ICICIBANK":"Financial Services","INDIGO":"Other","INFY":"Information Technology","ITC":"Consumer",
 "JIOFIN":"Financial Services","JSWSTEEL":"Metals & Mining","KOTAKBANK":"Financial Services",
 "LT":"Other","M&M":"Automobile","MARUTI":"Automobile","MAXHEALTH":"Healthcare","NESTLEIND":"Consumer",
 "NTPC":"Power & Energy","ONGC":"Power & Energy","POWERGRID":"Power & Energy","RELIANCE":"Power & Energy",
 "SBILIFE":"Financial Services","SBIN":"Financial Services","SHRIRAMFIN":"Financial Services",
 "SUNPHARMA":"Healthcare","TATACONSUM":"Consumer","TATASTEEL":"Metals & Mining",
 "TCS":"Information Technology","TECHM":"Information Technology","TITAN":"Consumer",
 "TMPV":"Automobile","TRENT":"Consumer","ULTRACEMCO":"Other"
}
def sector_for(symbol,name):
    return SECTOR_BY_SYMBOL.get(symbol,"Other")

def equity(payload,exchange,d):
    found={}
    # Cash-market equity series. Debt, currency, commodity and derivatives instruments
    # are not included in this equity directory.
    equity_series={"EQ","BE","BZ","SM","ST","SZ","E1"}
    for r in rows(payload):
        series=get(r,("SctySrs","SERIES","SC_GROUP","GROUP")).upper()
        if exchange=="NSE" and series and series not in equity_series: continue
        s=symbol_for(r,exchange)
        name=get(r,("FinInstrmNm","SC_NAME","SCRIP_NAME","Security Name","Company Name","NAME")) or s
        close=num(get(r,("ClsPric","CLOSE","CLOSE_PRICE","Close Price","Closing Price")))
        prev=num(get(r,("PrvsClsgPric","PREVCLOSE","PREV_CLOSE","Previous Close","Prev Close")))
        if not s or close is None or close<=0: continue
        change=close-prev if prev not in (None,0) else None
        key=exchange+":"+s
        item={"key":key,"exchange":exchange,"symbol":s,"name":name,"sector":sector_for(s,name),
          "type":"equity","series":series,"price":round(close,4),
          "previousClose":round(prev,4) if prev is not None else None,
          "change":round(change,4) if change is not None else None,
          "changePercent":round(change/prev*100,6) if change is not None else None,
          "date":d.isoformat(),"source":"Official "+exchange+" historical cash-equity bhavcopy"}
        old=found.get(key)
        # Prefer the primary EQ series when a symbol appears more than once.
        if old is None or (series=="EQ" and old.get("series")!="EQ"): found[key]=item
    if len(found)<100:
        raise RuntimeError(exchange+" bhavcopy matched only "+str(len(found))+" cash-equity securities; refusing to publish a partial market snapshot")
    return list(found.values())
def flatten(v):
    if isinstance(v,list): return [r for x in v for r in flatten(x)]
    if isinstance(v,dict):
        k={norm(x) for x in v}
        if k&{"indexname","index","close","closingindexvalue"}: return [v]
        return [r for x in v.values() for r in flatten(x)]
    return []
def index(payload,exchange,name,d):
    txt=payload.decode("utf-8-sig",errors="replace")
    try: rr=flatten(json.loads(txt))
    except json.JSONDecodeError: rr=rows(payload)
    chosen=None
    for r in rr:
        n=get(r,("Index Name","IndexName","Index","Index_Name"))
        if n and name.lower().replace(" ","") not in n.lower().replace(" ",""): continue
        dt=parsedate(get(r,("Index Date","Date","HistoricalDate","Trade Date")))
        if dt and dt!=d: continue
        chosen=r; break
    if not chosen: raise RuntimeError("No "+name+" record in "+exchange+" index data")
    close=num(get(chosen,("Closing Index Value","Close","Closing Value","ClosingIndexValue")))
    prev=num(get(chosen,("Previous Closing Index Value","Previous Close","Prev Close","Previous Closing Index")))
    change=num(get(chosen,("Points Change","Change","PointsChange")))
    pct=num(get(chosen,("Change (%)","Change(%)","% Change","Percentage Change","Percent Change","ChangePercent")))
    if close is None or close<=0: raise RuntimeError(name+" close value missing")
    if prev is None and change is not None: prev=close-change
    if change is None and prev is not None: change=close-prev
    if pct is None and prev and change is not None: pct=change/prev*100
    sym="^NSEI" if exchange=="NSE" else "^BSESN"
    return {"key":"INDEX:"+sym,"exchange":exchange,"symbol":sym,"type":"index","price":round(close,4),
      "previousClose":round(prev,4) if prev is not None else None,
      "change":round(change,4) if change is not None else None,
      "changePercent":round(pct,6) if pct is not None else None,
      "date":d.isoformat(),"source":"Official "+exchange+" historical index report"}
def build(d):
    ymd=d.strftime("%Y%m%d")
    nse="https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_"+ymd+"_F_0000.csv.zip"
    bse="https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_"+ymd+"_F_0000.CSV"
    nifty="https://nsearchives.nseindia.com/content/indices/ind_close_all_"+d.strftime("%d%m%Y")+".csv"
    sensex="https://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?"+urlencode({"strIndex":"SENSEX","dtFromDate":d.strftime("%d/%m/%Y"),"dtToDate":d.strftime("%d/%m/%Y"),"period":"D"})
    q=equity(fetch(nse),"NSE",d)+equity(fetch(bse),"BSE",d)
    q += [index(fetch(nifty),"NSE","Nifty 50",d),index(fetch(sensex),"BSE","SENSEX",d)]
    lag=(datetime.now(INDIA).date()-d).days
    if lag<MIN_LAG: raise RuntimeError("Refusing to publish a date inside the 31-day delay")
    return {"schemaVersion":1,"status":"ok","generatedAt":datetime.now(timezone.utc).isoformat(),
      "dataDate":d.isoformat(),"lagDays":lag,"quoteCount":len(q),
      "sources":{"NSE equities":nse,"BSE equities":bse,"NIFTY 50":nifty,"SENSEX":sensex},
      "quotes":sorted(q,key=lambda x:x["key"])}
def main():
    if os.environ.get("FINSIM_MARKET_DATA_AUTHORIZED","").lower()!="true":
        print("Feed disabled. Confirm public data-sharing rights before enabling it.")
        return 0
    start=datetime.now(INDIA).date()-timedelta(days=MIN_LAG)
    errors=[]
    for i in range(15):
        d=start-timedelta(days=i)
        if d.weekday()>=5: continue
        try:
            data=build(d); os.makedirs(os.path.dirname(OUT),exist_ok=True)
            with open(OUT,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,separators=(",",":")); f.write("\n")
            print("Published "+str(data["quoteCount"])+" quotes for "+data["dataDate"]+"; lag "+str(data["lagDays"])+" days.")
            return 0
        except Exception as e: errors.append(d.isoformat()+": "+str(e))
    print("No complete NSE/BSE dataset found:\n"+"\n".join(errors))
    return 1
if __name__=="__main__": sys.exit(main())
