"""Acquire fixed-delivery copper histories for explicit, auditable rolling."""
from pathlib import Path
import json,hashlib
from ib_insync import IB,Future,util

def main():
    out=next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())/'data/raw/ib_local/physical_history_20261005/copper_strip'
    out.mkdir(parents=True,exist_ok=True);records=[];errors=[]
    ib=IB();ib.RequestTimeout=20
    ib.errorEvent+=lambda req,code,msg,c: errors.append(dict(code=code,message=msg)) if code not in {2104,2106,2158} else None
    ib.connect('127.0.0.1',7497,clientId=104,readonly=True,timeout=15)
    try:
        for month in ['202412','202503','202505','202507','202509','202512','202603','202605','202607','202609','202612']:
            row=dict(month=month);records.append(row)
            try:
                contracts=ib.qualifyContracts(Future('HG',month,'COMEX',currency='USD',includeExpired=True))
                if len(contracts)!=1:row['status']='UNAVAILABLE';continue
                c=contracts[0];row['contract']=util.dataclassAsDict(c)
                end=min(c.lastTradeDateOrContractMonth[:8],'20260902')+' 23:59:59 UTC'
                bars=ib.reqHistoricalData(c,endDateTime=end,durationStr='1 Y',barSizeSetting='1 day',whatToShow='TRADES',useRTH=False,formatDate=2,timeout=35)
                df=util.df(bars)
                if df is None:row['status']='NO_DATA';continue
                path=out/(month+'.csv');df.to_csv(path,index=False)
                row.update(status='ACQUIRED',rows=len(df),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),end=end)
                print(month,len(df),flush=True)
            except Exception as e:row.update(status='ERROR',error=str(e));print(month,type(e).__name__,flush=True)
            finally:(out/'manifest.json').write_text(json.dumps(dict(provider='IB API',readonly=True,cutoff='2026-09-02',requests=records,errors=errors),indent=2,default=str),encoding='utf-8')
            ib.sleep(.5)
    finally:ib.disconnect()
if __name__=='__main__':main()
