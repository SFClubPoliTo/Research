"""Read-only underlying-history acquisition; local licensed data, no orders.

Daily observations support physical estimation; this is distinct from sparse
option strike selection. Continuous futures are diagnostic only until their
roll and adjustment policy is reconciled. No P model is estimated here.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from ib_insync import IB,Stock,Contract,Future,ContFuture,util


def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=7497)
    p.add_argument('--client-id',type=int,default=104);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    manifest=dict(provider='IB API',acquired_at=datetime.now(timezone.utc).isoformat(),readonly=True,
                  forecast_cutoff='2026-09-02',status='RAW_NOT_ADMITTED_TO_PHYSICAL_ESTIMATION',requests=[],errors=[])
    ib=IB();ib.RequestTimeout=25
    def persist(): (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2,default=str),encoding='utf-8')
    def err(req,code,message,contract):
        if code not in {2104,2106,2158}:manifest['errors'].append(dict(request=req,code=code,message=message,symbol=getattr(contract,'localSymbol','')))
    ib.errorEvent+=err
    ib.connect('127.0.0.1',a.port,clientId=a.client_id,readonly=True,timeout=15)
    specs=[('gld',Stock('GLD','SMART','USD'),'TRADES','5 Y','20260903 00:00:00 UTC'),
           ('gold_spot',Contract(symbol='XAUUSD',secType='CMDTY',exchange='SMART',currency='USD'),'MIDPOINT','5 Y','20260903 00:00:00 UTC'),
           ('hg_dec2026',Future('HG','202612','COMEX',currency='USD'),'TRADES','3 Y','20260903 00:00:00 UTC'),
           ('hg_continuous_diagnostic',ContFuture('HG','COMEX',currency='USD'),'TRADES','5 Y','')]
    try:
        for name,c,what,duration,end in specs:
            row=dict(name=name,whatToShow=what,duration=duration,end=end,bar_size='1 day',useRTH=False)
            manifest['requests'].append(row);persist()
            try:
                qualified=ib.qualifyContracts(c)
                if len(qualified)!=1:row['status']='QUALIFICATION_FAILED';persist();continue
                c=qualified[0];row['contract']=util.dataclassAsDict(c)
                bars=ib.reqHistoricalData(c,endDateTime=end,durationStr=duration,barSizeSetting='1 day',whatToShow=what,useRTH=False,formatDate=2,keepUpToDate=False,timeout=45)
                df=util.df(bars)
                if df is None or df.empty:row['status']='NO_BARS';persist();print(name,'NO_BARS',flush=True);continue
                dest=a.output/(name+'.csv');df.to_csv(dest,index=False)
                row.update(status='ACQUIRED',rows=len(df),first=str(df.date.iloc[0]),last=str(df.date.iloc[-1]),file=dest.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
                print(name,row['rows'],row['first'],row['last'],flush=True)
            except Exception as exc:
                row['status']='FAILED';row['error']=type(exc).__name__+': '+str(exc);print(name,row['error'],flush=True)
            persist();ib.sleep(1)
    finally:
        persist();ib.disconnect()

if __name__=='__main__':main()
