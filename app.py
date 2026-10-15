import os, json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import httpx
from core.models import Scenario, Portfolio
from core.engine import simulate, appraise, optimize
st.set_page_config(page_title="LC Grade Separation",layout="wide")
st.title("Level Crossing Grade Separation Laboratory")
st.caption("Concept, methodology and authorship: R. Gopalakrishnan | Illustrative planning simulator v1.0")
st.info("Demo master data and economic assumptions require local validation. Results support appraisal; they do not constitute project sanction.")
remote=os.getenv("SERVICE_MODE","local")=="remote"
def request(url,path,data=None):
    r=httpx.get(url+path,timeout=45) if data is None else httpx.post(url+path,json=data,timeout=45)
    r.raise_for_status();return r.json()
def master(name):
    if remote:return request(os.getenv("MASTER_URL","http://localhost:8001"),"/v1/master/"+name)
    return json.loads((Path(__file__).parent/"master_data"/(name+".json")).read_text())
tabs=st.tabs(["Single LC simulator","Portfolio selection","Master data & assumptions"])
with tabs[0]:
    treatment=st.selectbox("Intervention",list(master("treatments")["treatments"]))
    defaults=master("treatments")["treatments"][treatment]
    s=Scenario(**defaults); values=s.model_dump()
    groups={"Traffic and gate operation":["vehicles_day","trains_day","closure_minutes","discharge_per_minute","peak_factor","occupancy"],"Economics and rail operations":["value_time","freight_share","freight_cost_hour","rail_delay_minutes","rail_cost_hour","additional_paths_day","path_value"],"Safety, environment and distribution":["safety_cost_year","fatalities_year","injuries_year","safety_reduction","delay_reduction","detour_minutes","idling_co2_kg_hour","co2_price_kg","accessibility_index_gain","vulnerable_benefit_share"],"Project and appraisal":["capital_rupees","maintenance_year","discount","growth","years"]}
    for title,fields in groups.items():
        with st.expander(title,expanded=title.startswith("Traffic")):
            cols=st.columns(3)
            for j,key in enumerate(fields):
                values[key]=cols[j%3].number_input(key.replace("_"," "),value=values[key],key=key+"_"+treatment)
    upload=st.file_uploader("Optional observed day JSON: arrivals_10s (8640 counts), closure_events ([start,end] minutes)",type="json")
    if st.button("Simulate and appraise",type="primary"):
        try:
            if upload:values.update(json.load(upload))
            scenario=Scenario(**values)
            if remote:out=request(os.getenv("APPRAISAL_URL","http://localhost:8003"),"/v1/appraise",scenario.model_dump())
            else:
                sim=simulate(scenario);out={"simulation":sim,"appraisal":appraise(scenario,sim),"input":scenario.model_dump(),"model_version":"1.0"}
            st.session_state["result"]=out
        except Exception as e:st.error(str(e))
    if "result" in st.session_state:
        out=st.session_state["result"];q=out["simulation"];a=out["appraisal"]
        cols=st.columns(4)
        for col,label,value in zip(cols,["TVU","Road vehicle-hours/day","NPV (₹ crore)","BCR"],[q["tvu"],q["vehicle_hours_day"],a["npv_rupees"]/1e7,a["bcr"]]):col.metric(label,"—" if value is None else f"{value:,.2f}")
        st.plotly_chart(px.line(pd.DataFrame(q["series"]),x="minute",y="queue",title="Queue throughout the representative day"),use_container_width=True)
        st.plotly_chart(px.bar(pd.DataFrame({"component":a["annual_components_rupees"].keys(),"₹/year":a["annual_components_rupees"].values()}),x="component",y="₹/year"),use_container_width=True)
        st.json({k:v for k,v in a.items() if k!="annual_components_rupees"})
        for warning in q["warnings"]:st.warning(warning)
        st.download_button("Download reproducible scenario and results",json.dumps(out,indent=2),"lc_scenario.json","application/json")
        multipliers=[.5,.75,1,1.25,1.5]
        st.line_chart(pd.DataFrame({"traffic multiplier":multipliers,"NPV ₹ crore":[appraise(Scenario(**{**out["input"],"vehicles_day":out["input"]["vehicles_day"]*m,"arrivals_10s":None}),simulate(Scenario(**{**out["input"],"vehicles_day":out["input"]["vehicles_day"]*m,"arrivals_10s":None})))["npv_rupees"]/1e7 for m in multipliers]}).set_index("traffic multiplier"))
with tabs[1]:
    st.write("Upload treatment-level candidate CSV; an unselected LC implicitly retains its existing condition.")
    sample=pd.DataFrame([{"lc_id":"DEMO-001","treatment":"RUB","section_id":"DEMO-SECTION","capital_rupees":60000000,"lifecycle_rupees":63300000,"npv_rupees":50000000,"safety_rupees":950000,"rural":True,"congested":True,"strategic_score":.8,"feasible":True,"capacity_claim":False},{"lc_id":"DEMO-002","treatment":"ROB","section_id":"DEMO-SECTION-2","capital_rupees":120000000,"lifecycle_rupees":126000000,"npv_rupees":75000000,"safety_rupees":800000,"rural":False,"congested":True,"strategic_score":.7,"feasible":True,"capacity_claim":True}])
    st.download_button("Candidate CSV template",sample.to_csv(index=False),"candidates.csv")
    f=st.file_uploader("Candidate CSV",type="csv")
    frame=pd.read_csv(f) if f else sample
    frame=st.data_editor(frame,num_rows="dynamic",use_container_width=True)
    budget=st.number_input("Budget ₹ crore",min_value=0.,value=15.)*1e7
    basis=st.selectbox("Budget basis",["capital","lifecycle"])
    objective=st.selectbox("Objective",["npv","strategic"])
    rural=st.number_input("Minimum rural projects",min_value=0,value=0)
    congested=st.number_input("Minimum congested corridor projects",min_value=0,value=0)
    safety=st.number_input("Minimum annual safety benefit ₹",min_value=0.,value=0.)
    if st.button("Optimize portfolio"):
        try:
            inputs=Portfolio(candidates=frame.to_dict("records"),budget_rupees=budget,budget_basis=basis,objective=objective,min_rural=rural,min_congested=congested,min_safety_rupees=safety)
            result=request(os.getenv("PORTFOLIO_URL","http://localhost:8004"),"/v1/optimize",inputs.model_dump()) if remote else optimize(inputs)
            st.json(result);st.download_button("Download portfolio",json.dumps(result,indent=2),"portfolio.json")
        except Exception as e:st.error(str(e))
with tabs[2]:
    st.json(master("lcs"));st.json(master("treatments"))
    st.markdown("Master files are separate from source code. Service deployment mounts them read-only. Editing scenario controls never changes master data. See docs/user-manual.md for units and limitations.")
