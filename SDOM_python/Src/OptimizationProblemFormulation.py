"""
One node Optimal Technology Mix for VRE integration

This model determines optimal technology mix, including wind, solar PV, and
energy storage, to achieve a given VRE target.
"""

import pandas as pd
from pyomo.environ import (ConcreteModel, Set, Param, Var, Objective, 
                           Constraint, NonNegativeReals, Binary, RangeSet, Table, sqrt, minimize, Reals)



#### Check for global variables ####
if 'GenMix_TargetValue' not in globals():
    GenMix_TargetValue = 1.00 # default value

if 'AlphaNuclearValue' not in globals():
    AlphaNuclearValue = 1 # default value


#### Load data from CSV files ####
load_hourly_2050_df = pd.read_csv("Load_hourly_2050.csv")
nucl_hourly_2019_df = pd.read_csv("Nucl_hourly_2019.csv")
lahy_hourly_2019_df = pd.read_csv("lahy_hourly_2019.csv")
otre_hourly_2019_df = pd.read_csv("otre_hourly_2019.csv")
CFSolar_2050_df = pd.read_csv("CFSolar_2050.csv")
CFWind_2050_df = pd.read_csv("CFWind_2050.csv")
CapSolar_2050_df = pd.read_csv("CapSolar_2050.csv")
CapWind_2050_df = pd.read_csv("CapWind_2050.csv")
StorageData_2050_df = pd.read_csv("StorageData_2050.csv")



#### Initialize model ####

model = ConcreteModel()


#### Define the sets ####

model.h = Set(initialize=range(1, 8761))  # set "h" for hours

with open('Set_k(SolarPV).txt', 'r') as file: 
    k_values = [line.strip() for line in file] 

model.k = Set(initialize=k_values) # set "k" for solar plants

with open('Set_w(Wind).txt', 'r') as file:
    w_values = [line.strip() for line in file]

model.w = Set(initialize=w_values) # set "w" for wind plants

with open('Set_l(Properties).txt', 'r') as file:
    l_values = [line.strip() for line in file]

model.l = Set(initialize=l_values) # set "l" for properties of power plants

model.j = Set(initialize=['Li-Ion', 'CAES', 'PHS', 'H2']) # set "j" for energy storage technologies
model.b = Set(within=model.j, initialize=['Li-Ion', 'PHS']) # set "b(j)" for storage technologies with coupled charging and discharging units
model.sp = Set(initialize=['P_Capex', 'E_Capex', 'Eff', 'Min_Duration', 'Max_Duration', 'Max_P', 'FOM', 'VOM', 'lifetime', 'CostRatio']) # set "sp" for properties of storage technologies
model.Runs = RangeSet(1) 


#### Setting Scalars ####

# Define the scalars 
model.FCR_VRE = Param(initialize=0, mutable=True) # (mutable parameters so that they can be changed without reconstructing entire model)
model.FCR_GasCC = Param(initialize=0, mutable=True)
model.GenMix_Target = Param(initialize=GenMix_TargetValue, mutable=True)
model.CapexGasCC = Param(initialize=940.6078576, mutable=True)
model.HR = Param(initialize=6.4005, mutable=True)
model.GasPrice = Param(initialize=4.113894393, mutable=True)
model.FOM_GasCC = Param(initialize=13.2516707, mutable=True)
model.VOM_GasCC = Param(initialize=2.226321156, mutable=True)
model.AlphaNuclear = Param(initialize=AlphaNuclearValue, mutable=True)
model.AlphaLargHy = Param(initialize=1, mutable=True)
model.AlphaOtheRe = Param(initialize=1, mutable=True)
model.MaxCycles = Param(initialize=3250, mutable=True)
model.r = Param(initialize=0.06, mutable=True)

# Calculate values for FCR_VRE and FCR_GasCC based on the given formula
def calculate_FCR(m, r):
    return (r*(1+r)**30)/((1+r)**30-1)

model.FCR_VRE = calculate_FCR(model, model.r)
model.FCR_GasCC = calculate_FCR(model, model.r)



#### Initialize parameters ####

# Parameters for hourly data
load_data = {row['*Hour']: row['Load'] for _, row in load_hourly_2050_df.iterrows()}
nuclear_data = {row['*Hour']: row['Nuclear'] for _, row in nucl_hourly_2019_df.iterrows()}
large_hydro_data = {row['*Hour']: row['LargeHydro'] for _, row in lahy_hourly_2019_df.iterrows()}
other_renewables_data = {row['*Hour']: row['OtherRenewables'] for _, row in otre_hourly_2019_df.iterrows()}

model.Load = Param(model.h, initialize=load_data)
model.Nuclear = Param(model.h, initialize=nuclear_data)
model.LargeHydro = Param(model.h, initialize=large_hydro_data)
model.OtherRenewables = Param(model.h, initialize=other_renewables_data)

# Tables for capacity factors and properties
cfsolar_data = {(row['h'], row['k']): row['CFSolar'] for _, row in CFSolar_2050_df.iterrows()} #define cfsolar_data dictionary
cfwind_data = {(row['h'], row['w']): row['CFWind'] for _, row in CFWind_2050_df.iterrows()}
capsolar_data = {(row['k'], row['l']): row['CapSolar'] for _, row in CapSolar_2050_df.iterrows()}
capwind_data = {(row['w'], row['l']): row['CapWind'] for _, row in CapWind_2050_df.iterrows()}
storagedata_data = {(row['sp'], row['j']): row['StorageData'] for _, row in StorageData_2050_df.iterrows()}

model.CFSolar = Table(model.h, model.k, initialize=cfsolar_data)
model.CFWind = Table(model.h, model.w, initialize=cfwind_data)
model.CapSolar = Table(model.k, model.l, initialize=capsolar_data)
model.CapWind = Table(model.w, model.l, initialize=capwind_data)
model.StorageData = Table(model.sp, model.j, initialize=storagedata_data)

# Capital recovery factor for storage technology
def crf_rule(model, j):
    return (model.r * (1 + model.r) ** model.StorageData['Lifetime', j]) / ((1 + model.r) ** model.StorageData['Lifetime', j] - 1)

model.CRF = Param(model.j, initialize=crf_rule)


#### Setting Variables ####

model.TSC = Var(domain=Reals) # free variable
model.Ystorage = Var(model.j, model.h, domain=Binary) # binary variables

model.PC = Var(model.h, model.j, domain=NonNegativeReals)
model.PD = Var(model.h, model.j, domain=NonNegativeReals)
model.SOC = Var(model.h, model.j, domain=NonNegativeReals)
model.Pcha = Var(model.j, domain=NonNegativeReals)
model.Pdis = Var(model.j, domain=NonNegativeReals)
model.Ecap = Var(model.j, domain=NonNegativeReals)
model.GenPV = Var(model.h, domain=NonNegativeReals)
model.CurtPV = Var(model.h, domain=NonNegativeReals)
model.GenWind = Var(model.h, domain=NonNegativeReals)
model.CurtWind = Var(model.h, domain=NonNegativeReals)
model.CapCC = Var(domain=NonNegativeReals)
model.GenCC = Var(model.h, domain=NonNegativeReals)
model.Ypv = Var(model.k, domain=NonNegativeReals, bounds=(0, 1))
model.Ywind = Var(model.w, domain=NonNegativeReals, bounds=(0, 1))


# Define upper bound for CapCC
def capcc_bound_rule(model): 
    return sum(model.Load[h] - model.AlphaNuclear * model.Nuclear[h] - model.AlphaLargHy * model.LargeHydro[h] - model.AlphaOtheRe * model.OtherRenewables[h] for h in model.h)

model.CapCC.setub(capcc_bound_rule)


#### Setting Equations ####

# Objective Function (Eq 1)
model.TSC = Objective(expr=sum(
    (model.FCR_VRE * (1000 * model.CapSolar[k, 'CAPEX_M'] + model.CapSolar[k, 'trans_cap_cost']) + 1000 * model.CapSolar[k, 'FOM_M']) * model.CapSolar[k, 'capacity'] * model.Ypv[k] for k in model.k) +
    sum((model.FCR_VRE * (1000 * model.CapWind[w, 'CAPEX_M'] + model.CapWind[w, 'trans_cap_cost']) + 1000 * model.CapWind[w, 'FOM_M']) * model.CapWind[w, 'capacity'] * model.Ywind[w] for w in model.w) +
    sum(model.CRF[j] * (1000 * model.StorageData['CostRatio', j] * model.StorageData['P_Capex', j] * model.Pcha[j] + 1000 * (1 - model.StorageData['CostRatio', j]) * model.StorageData['P_Capex', j] * model.Pdis[j] + 1000 * model.StorageData['E_Capex', j] * model.Ecap[j]) for j in model.j) +
    sum(1000 * model.StorageData['CostRatio', j] * model.StorageData['FOM', j] * model.Pcha[j] + 1000 * (1 - model.StorageData['CostRatio', j]) * model.StorageData['FOM', j] * model.Pdis[j] + model.StorageData['VOM', j] * sum(model.PD[h, j] for h in model.h) for j in model.j) +
    model.FCR_GasCC * 1000 * model.CapexGasCC * model.CapCC + model.GasPrice * model.HR * sum(model.GenCC[h] for h in model.h) + model.FOM_GasCC * 1000 * model.CapCC + model.VOM_GasCC * sum(model.GenCC[h] for h in model.h),
    sense=minimize)

# Power Balance (Eq 6)
model.Supply = Constraint(model.h, 
                          rule=lambda model, h: (model.Load[h] 
                          + sum(model.PC[h, j] for j in model.j) 
                          - model.AlphaNuclear * model.Nuclear[h] 
                          - model.AlphaLargHy * model.LargeHydro[h] 
                          - model.AlphaOtheRe * model.OtherRenewables[h] 
                          - model.GenPV[h] - model.GenWind[h] 
                          - sum(model.PD[h, j] for j in model.j) 
                          - model.GenCC[h] == 0))

# Carbon free/renewable request target (Eq 7)
model.GenMix_Share = Constraint(rule=lambda model: (sum(model.GenCC[h] for h in model.h) 
                            <= (1 - model.GenMix_Target) * 
                            sum(model.Load[h] + sum(model.PC[h, j] for j in model.j) 
                                - sum(model.PD[h, j] for j in model.j) for h in model.h)))

model.SolarBal = Constraint(model.h, rule=lambda model, h: model.GenPV[h] + model.CurtPV[h] == sum(model.CFSolar[h,k] * model.CapSolar[k,'capacity'] * model.Ypv[k] for k in model.k))
model.WindBal = Constraint(model.h, rule=lambda model, h: model.GenWind[h] + model.CurtWind[h] == sum(model.CFWind[h,w] * model.CapWind[w,'capacity'] * model.Ywind[w] for w in model.w))
model.ChargSt = Constraint(model.h, model.j, rule=lambda model, h, j: model.PC[h,j] <= model.StorageData['Max_P',j] * model.Ystorage[j,h])
model.DischargSt = Constraint(model.h, model.j, rule=lambda model, h, j: model.PD[h,j] <= model.StorageData['Max_P',j] * (1 - model.Ystorage[j,h]))
model.MaxPC = Constraint(model.h, model.j, rule=lambda model, h, j: model.PC[h,j] <= model.Pcha[j])
model.MaxPD = Constraint(model.h, model.j, rule=lambda model, h, j: model.PD[h,j] <= model.Pdis[j])
model.MaxSOC = Constraint(model.h, model.j, rule=lambda model, h, j: model.SOC[h,j] <= model.Ecap[j])

# SOC balance for storage technology j during hour h > 1
def soc_balance_rule(model, h, j):
    if h > 1:
        return model.SOC[h, j] == model.SOC[h-1, j] + sqrt(model.StorageData['Eff', j]) * model.PC[h, j] - (1 / sqrt(model.StorageData['Eff', j])) * model.PD[h, j]
    return Constraint.Skip

model.SOCBal = Constraint(model.h, model.j, rule=soc_balance_rule)

# Initial SOC balance for storage technology j
def ini_balance_rule(model, h, j):
    if h == 1:
        return model.SOC[h, j] == model.SOC[max(model.h), j] + sqrt(model.StorageData['Eff', j]) * model.PC[h, j] - (1 / sqrt(model.StorageData['Eff', j])) * model.PD[h, j]
    return Constraint.Skip

# Initial (h = 1) SOC balance for storage technology j
model.IniBal = Constraint(model.h, model.j, rule=ini_balance_rule)

# Maximum charge power capacity for storage technology j
model.MaxPcha = Constraint(model.j, rule=lambda model, j: model.Pcha[j] <= model.StorageData['Max_P', j])

# Maximum discharge power capacity for storage technology j
model.MaxPdis = Constraint(model.j, rule=lambda model, j: model.Pdis[j] <= model.StorageData['Max_P', j])

# Coupling of charge and discharge power capacity for battery technology b
model.PchaPdis = Constraint(model.b, rule=lambda model, b: model.Pcha[b] == model.Pdis[b])

# Minimum energy capacity for storage technology j
model.MinEcap = Constraint(model.j, rule=lambda model, j: model.Ecap[j] >= model.StorageData['Min_Duration', j] * (1 / sqrt(model.StorageData['Eff', j])) * model.Pdis[j])

# Maximum energy capacity for storage technology j
model.MaxEcap = Constraint(model.j, rule=lambda model, j: model.Ecap[j] <= model.StorageData['Max_Duration', j] * (1 / sqrt(model.StorageData['Eff', j])) * model.Pdis[j])

# Required capacity from backup combined cycle units
model.BackupGen = Constraint(model.h, rule=lambda model, h: model.CapCC >= model.GenCC[h])

# Maximum number of cycles per year for Li-Ion batteries
model.MaxCycleYear = Constraint(rule=lambda model: sum(model.PD[h, 'Li-Ion'] for h in model.h) <= (model.MaxCycles / model.StorageData['Lifetime', 'Li-Ion']) * model.Ecap['Li-Ion'])



