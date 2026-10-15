from pydantic import BaseModel, Field, model_validator, ConfigDict
class Scenario(BaseModel):
    model_config=ConfigDict(allow_inf_nan=False, extra="forbid")
    vehicles_day: float = Field(3000, ge=0, le=200000)
    trains_day: int = Field(40, ge=0, le=500)
    closure_minutes: float = Field(6, ge=0, le=120)
    discharge_per_minute: float = Field(5.25, gt=0, le=500)
    occupancy: float = Field(1.8, gt=0, le=100)
    value_time: float = Field(100, ge=0)
    freight_share: float = Field(.15, ge=0, le=1)
    freight_cost_hour: float = Field(300, ge=0)
    rail_delay_minutes: float = Field(1, ge=0)
    rail_cost_hour: float = Field(10000, ge=0)
    additional_paths_day: float = Field(0, ge=0)
    path_value: float = Field(0, ge=0)
    safety_cost_year: float = Field(1000000, ge=0)
    fatalities_year: float = Field(.05, ge=0)
    injuries_year: float = Field(.2, ge=0)
    safety_reduction: float = Field(.95, ge=0, le=1)
    delay_reduction: float = Field(1, ge=0, le=1)
    detour_minutes: float = Field(0, ge=0)
    idling_co2_kg_hour: float = Field(1.5, ge=0)
    co2_price_kg: float = Field(0, ge=0)
    accessibility_index_gain: float = Field(0, ge=0)
    vulnerable_benefit_share: float = Field(.3, ge=0, le=1)
    capital_rupees: float = Field(60000000, ge=0)
    maintenance_year: float = Field(300000, ge=0)
    discount: float = Field(.08, ge=0, le=.5)
    growth: float = Field(0, ge=-.5, le=.2)
    years: int = Field(30, ge=1, le=60)
    peak_factor: float = Field(1.5, ge=1, le=8)
    closure_events: list[list[float]] | None = None
    arrivals_10s: list[float] | None = None
    @model_validator(mode="after")
    def valid_arrays(self):
        if self.arrivals_10s is not None and (len(self.arrivals_10s)!=8640 or any(x<0 for x in self.arrivals_10s)):
            raise ValueError("arrivals_10s must have 8640 nonnegative vehicle counts")
        if self.closure_events is not None and any(len(e)!=2 or not 0<=e[0]<e[1]<=1440 for e in self.closure_events):
            raise ValueError("closure events must be [start,end] minutes within the day")
        return self
class Candidate(BaseModel):
    model_config=ConfigDict(allow_inf_nan=False, extra="forbid")
    lc_id: str
    treatment: str
    section_id: str
    capital_rupees: float = Field(ge=0)
    lifecycle_rupees: float = Field(ge=0)
    npv_rupees: float
    safety_rupees: float = Field(ge=0)
    rural: bool = False
    congested: bool = False
    strategic_score: float = Field(0, ge=0, le=1)
    feasible: bool = True
    capacity_claim: bool = False
class Portfolio(BaseModel):
    model_config=ConfigDict(allow_inf_nan=False, extra="forbid")
    candidates: list[Candidate] = Field(max_length=3000)
    budget_rupees: float = Field(ge=0)
    budget_basis: str = "capital"
    min_safety_rupees: float = Field(0, ge=0)
    min_rural: int = Field(0, ge=0)
    min_congested: int = Field(0, ge=0)
    objective: str = "npv"
