"""R. Gopalakrishnan — LC grade separation planning framework."""
import math
from .models import Scenario, Portfolio

def simulate(s: Scenario):
    dt=1/6; n=8640
    # Smooth daily peaks; normalize to the requested daily total.
    profile=[1+(s.peak_factor-1)*(math.exp(-((i*dt-480)/100)**2)+math.exp(-((i*dt-1080)/100)**2)) for i in range(n)]
    arrivals=s.arrivals_10s if s.arrivals_10s is not None else [s.vehicles_day*x/sum(profile) for x in profile]
    events=s.closure_events if s.closure_events is not None else [[j*1440/s.trains_day,min(1440,j*1440/s.trains_day+s.closure_minutes)] for j in range(s.trains_day)]
    closed=[False]*n
    for a,b in events:
        for i in range(n):
            if i*dt<b and (i+1)*dt>a:closed[i]=True
    q=0.; area=0.; history=[]; waits=[]; departed=0.; maximum=0.
    for i,a in enumerate(arrivals):
        before=q; available=q+a
        d=0 if closed[i] else min(available,s.discharge_per_minute*dt)
        q=available-d; maximum=max(maximum,q); departed+=d; area+=(before+q)*dt/2
        waits.append(q/s.discharge_per_minute)
        if i%6==0:history.append({"minute":i*dt,"queue":q,"closed":int(closed[i])})
    hours=area/60
    sorted_wait=sorted(waits)
    return {"vehicle_hours_day":hours,"person_hours_day":hours*s.occupancy,"max_queue":maximum,"residual_queue":q,"arrivals":sum(arrivals),"departures":departed,"closed_minutes":sum(closed)*dt,"p95_queue_clearance_minutes":sorted_wait[int(.95*(n-1))],"tvu":s.trains_day*sum(arrivals),"series":history,"warnings":(["Residual queue remains at midnight: daily benefits exclude subsequent clearance delay."] if q>.01 else [])}

def appraise(s:Scenario, result:dict):
    h=result["vehicle_hours_day"]
    net_hours=h*s.delay_reduction-sum(s.arrivals_10s or [s.vehicles_day])*s.detour_minutes/60
    road=365*net_hours*(s.occupancy*s.value_time+s.freight_share*s.freight_cost_hour)
    rail=365*s.trains_day*s.rail_delay_minutes/60*s.rail_cost_hour*s.delay_reduction
    capacity=365*s.additional_paths_day*s.path_value
    safety=s.safety_cost_year*s.safety_reduction
    co2=365*h*s.delay_reduction*s.idling_co2_kg_hour
    components={"road":road,"rail_delay":rail,"capacity":capacity,"safety":safety,"environment":co2*s.co2_price_kg}
    annual=sum(components.values())
    cash=[annual*(1+s.growth)**(t-1)-s.maintenance_year for t in range(1,s.years+1)]
    pv_b=sum(annual*(1+s.growth)**(t-1)/(1+s.discount)**t for t in range(1,s.years+1))
    pv_c=s.capital_rupees+sum(s.maintenance_year/(1+s.discount)**t for t in range(1,s.years+1))
    irr=None
    if s.capital_rupees>0 and any(x>0 for x in cash):
        def f(r):return -s.capital_rupees+sum(v/(1+r)**t for t,v in enumerate(cash,1))
        lo,hi=-.99,10.
        if f(lo)*f(hi)<0:
            for _ in range(150):
                m=(lo+hi)/2
                if f(lo)*f(m)<=0:hi=m
                else:lo=m
            irr=(lo+hi)/2
    return {"annual_components_rupees":components,"pv_benefits_rupees":pv_b,"pv_cost_rupees":pv_c,"npv_rupees":pv_b-pv_c,"bcr":pv_b/pv_c if pv_c else None,"eirR":irr,"co2_kg_year":co2,"fatalities_avoided_year":s.fatalities_year*s.safety_reduction,"injuries_avoided_year":s.injuries_year*s.safety_reduction,"accessibility_index_gain":s.accessibility_index_gain,"vulnerable_benefit_share":s.vulnerable_benefit_share,"net_vehicle_hours_saved_day":net_hours}

def optimize(p:Portfolio):
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    if p.budget_basis not in ("capital","lifecycle") or p.objective not in ("npv","strategic"):
        raise ValueError("Unsupported budget basis or objective")
    candidates=[c for c in p.candidates if c.feasible and c.treatment.lower()!="retain"]
    if not candidates:return {"status":"empty","selected":[]}
    if len({(c.lc_id,c.treatment) for c in candidates})!=len(candidates):raise ValueError("Duplicate LC/treatment")
    n=len(candidates);rows=[];lower=[];upper=[]
    def add(values,lo,hi):rows.append(values);lower.append(lo);upper.append(hi)
    add([c.capital_rupees if p.budget_basis=="capital" else c.lifecycle_rupees for c in candidates],0,p.budget_rupees)
    for lc in sorted({c.lc_id for c in candidates}):add([int(c.lc_id==lc) for c in candidates],0,1)
    # Conservative MVP rule: at most one independent capacity claim per section.
    for section in {c.section_id for c in candidates if c.capacity_claim}:
        add([int(c.section_id==section and c.capacity_claim) for c in candidates],0,1)
    add([c.safety_rupees for c in candidates],p.min_safety_rupees,np.inf)
    add([int(c.rural) for c in candidates],p.min_rural,np.inf)
    add([int(c.congested) for c in candidates],p.min_congested,np.inf)
    objective=np.array([c.npv_rupees if p.objective=="npv" else c.strategic_score for c in candidates])
    res=milp(-objective,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(np.array(rows),lower,upper),options={"time_limit":30})
    if res.x is None:return {"status":"infeasible" if res.status==2 else "solver_failed","message":res.message,"selected":[]}
    selected=[c.model_dump() for c,x in zip(candidates,res.x) if x>.5]
    return {"status":"optimal" if res.status==0 else "feasible_not_proven_optimal","selected":selected,"objective_value":float(objective@res.x),"capital_rupees":sum(c["capital_rupees"] for c in selected),"mip_gap":float(res.mip_gap) if res.mip_gap is not None else None}
