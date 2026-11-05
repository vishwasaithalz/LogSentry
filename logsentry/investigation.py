"""Offline Windows event investigation helpers. No collection, uploads or privilege changes."""
from collections import Counter
from datetime import datetime, timezone

AUTH_FAILURE=4625
AUTH_SUCCESS=4624
ACCOUNT_LOCKOUT=4740

def _event_id(event):
    value=event.get("event_id",event.get("EventID",event.get("id")))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def _timestamp(event):
    value=event.get("timestamp",event.get("TimeCreated",event.get("time")))
    if not isinstance(value,str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z","+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None

def investigate(events, failure_threshold=5, window_minutes=15):
    """Return defensive triage findings from already-imported event dictionaries."""
    if not isinstance(events,list) or not isinstance(failure_threshold,int) or failure_threshold<1:
        raise ValueError("Expected a list of events and positive failure_threshold")
    timeline=sorted(((t,e) for e in events if isinstance(e,dict) if (t:=_timestamp(e)) is not None),key=lambda pair:pair[0])
    counts=Counter(_event_id(e) for e in events if isinstance(e,dict))
    findings=[]
    for idx,(time,event) in enumerate(timeline):
        if _event_id(event)!=AUTH_FAILURE:
            continue
        window=[e for t,e in timeline if time<=t and (t-time).total_seconds()<=window_minutes*60 and _event_id(e)==AUTH_FAILURE]
        if len(window)>=failure_threshold and (not findings or findings[-1].get("first_seen")!=time.isoformat()):
            findings.append({"type":"authentication_failure_burst","first_seen":time.isoformat(),"events_in_window":len(window),"severity":"review","note":"Correlate with authorised host and account context; not proof of compromise."})
            break
    if counts[ACCOUNT_LOCKOUT]:
        findings.append({"type":"account_lockouts","count":counts[ACCOUNT_LOCKOUT],"severity":"review","note":"Review account lockout context."})
    return {"event_count":len(events),"event_ids":{str(k):v for k,v in sorted(counts.items()) if k is not None},"findings":findings,"disclaimer":"Triage only. Never upload sensitive event records."}
