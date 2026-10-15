import itertools
import pytest
from fastapi.testclient import TestClient
from core.models import Scenario, Portfolio
from core.engine import simulate, appraise, optimize
from services.simulation import app

def test_paper_reference():
    q=2.1*6
    assert .5*q*(6+4)*40/60==pytest.approx(42)

def test_zero_closures():
    r=simulate(Scenario(trains_day=0))
    assert r["vehicle_hours_day"]==0
    assert r["arrivals"]==pytest.approx(r["departures"]+r["residual_queue"])

def test_overlap_and_backlog():
    s=Scenario(vehicles_day=100000,discharge_per_minute=1,closure_events=[[0,60],[30,90]])
    r=simulate(s)
    assert r["closed_minutes"]==pytest.approx(90)
    assert r["arrivals"]==pytest.approx(r["departures"]+r["residual_queue"])
    assert r["warnings"]

def test_observed_and_validation():
    r=simulate(Scenario(arrivals_10s=[0]*8640))
    assert r["arrivals"]==0
    with pytest.raises(ValueError):Scenario(arrivals_10s=[1])
    with pytest.raises(ValueError):Scenario(discount=float("nan"))
    assert TestClient(app).post("/v1/simulate",json={"vehicles_day":-1}).status_code==422

def test_discount_economics():
    s=Scenario(trains_day=0,safety_cost_year=100,safety_reduction=1,capital_rupees=100,maintenance_year=10,discount=0,years=2)
    a=appraise(s,simulate(s))
    assert a["npv_rupees"]==pytest.approx(80)
    assert a["bcr"]==pytest.approx(200/120)

def test_detour_can_be_negative():
    s=Scenario(trains_day=0,detour_minutes=10)
    assert appraise(s,simulate(s))["annual_components_rupees"]["road"]<0

def rows():
    return [dict(lc_id=lc,treatment=t,section_id=lc,capital_rupees=c,lifecycle_rupees=c,npv_rupees=v,safety_rupees=1,rural=True) for lc,t,c,v in [("a","ROB",6,10),("a","RUB",4,8),("b","RUB",5,9)]]
def test_optimum_matches_enumeration():
    r=optimize(Portfolio(candidates=rows(),budget_rupees=9))
    best=max(sum(x["npv_rupees"] for x,b in zip(rows(),bits) if b) for bits in itertools.product([0,1],repeat=3) if sum(x["capital_rupees"] for x,b in zip(rows(),bits) if b)<=9 and not(bits[0] and bits[1]))
    assert r["status"]=="optimal"
    assert r["objective_value"]==best==17
    assert len({x["lc_id"] for x in r["selected"]})==len(r["selected"])

def test_infeasible_and_retain():
    r=optimize(Portfolio(candidates=rows(),budget_rupees=0,min_rural=1))
    assert r["status"]=="infeasible"
    retain={**rows()[0],"treatment":"retain","capital_rupees":0}
    assert optimize(Portfolio(candidates=[retain],budget_rupees=0,min_rural=1))["selected"]==[]

def test_capacity_constraint():
    rs=rows()[1:]
    for x in rs:x.update(section_id="same",capacity_claim=True)
    assert len(optimize(Portfolio(candidates=rs,budget_rupees=100))["selected"])==1

def test_ui():
    from streamlit.testing.v1 import AppTest
    at=AppTest.from_file("../app.py",default_timeout=30).run()
    assert not at.exception
    at.button[0].click().run()
    assert not at.exception
    assert len(at.metric)==4
    at.button[1].click().run()
    assert not at.exception
