# -*- coding: utf-8 -*-
"""
Created on Oct 2023

@author: 

One node Optimal Technology Mix for VRE integration

This model determines optimal technology mix, including wind, solar PV, and
energy storage, to achieve a given VRE target.
"""

import pandas as pd
import os
from pyomo.environ import (ConcreteModel, Set, Param, Var, Objective, 
                           Constraint, NonNegativeReals, Binary, RangeSet, sqrt, minimize, Reals, SolverFactory)
from pyomo.opt import SolverStatus, TerminationCondition



#### Check for global variables ####
if 'GenMix_TargetValue' not in globals():
    GenMix_TargetValue = 1.00 # default value

if 'AlphaNuclearValue' not in globals():
    AlphaNuclearValue = 1 # default value

main_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #main directory

data_dir = os.path.join(main_dir, 'SDOM_TestCase') # base path for the data directory
print(data_dir)

# print(os.path.join(data_dir, 'Load_hourly_2050.csv'))

# Dynamic paths to read the input files
load_hourly_2050_df = pd.read_csv(os.path.join(data_dir, 'Load_hourly_2050.csv'))
nucl_hourly_2019_df = pd.read_csv(os.path.join(data_dir, 'Nucl_hourly_2019.csv'))
lahy_hourly_2019_df = pd.read_csv(os.path.join(data_dir, 'lahy_hourly_2019.csv'))
otre_hourly_2019_df = pd.read_csv(os.path.join(data_dir, 'otre_hourly_2019.csv'))
cfsolar_2050_df = pd.read_csv(os.path.join(data_dir, 'CFSolar_2050.csv'))
cfwind_2050_df = pd.read_csv(os.path.join(data_dir, 'CFWind_2050.csv'))
capsolar_2050_df = pd.read_csv(os.path.join(data_dir, 'CapSolar_2050.csv'))
capwind_2050_df = pd.read_csv(os.path.join(data_dir, 'CapWind_2050.csv'))
storagedata_2050_df = pd.read_csv(os.path.join(data_dir, 'StorageData_2050.csv'))

# print(cfsolar_2050_df)
# print(cfwind_2050_df.head())
# print(storagedata_2050_df)



#### Initialize model ####

separator = '=' * 50
print(f'\n{separator}\n{"Initializing the model ....".center(len(separator))}\n{separator}\n')

model = ConcreteModel()


#### Define the sets ####

separator = '=' * 50
print(f'\n{separator}\n{"Defining the sets ....".center(len(separator))}\n{separator}\n')

model.h = Set(initialize=range(1, 8761))  # set "h" : hours
print('Size of model.h:', len(model.h))  # check that defined correctly

with open(os.path.join(data_dir, 'Set_k(SolarPV).txt'), 'r') as file: 
    k_values = [line.strip() for line in file] 
model.k = Set(initialize=k_values) # set "k" : solar plants
print('Size of model.k:', len(model.k))  # check that defined correctly

with open(os.path.join(data_dir, 'Set_w(Wind).txt'), 'r') as file:
    w_values = [line.strip() for line in file]
model.w = Set(initialize=w_values) # set "w" : wind plants
print('Size of model.w:', len(model.w))  # check that defined correctly


with open(os.path.join(data_dir, 'Set_l(Properties).txt'), 'r') as file:
    l_values = [line.strip() for line in file]
model.l = Set(initialize=l_values) # set "l" : properties of power plants
print('Size of model.l:', len(model.l))  # check that defined correctly

model.j = Set(initialize=['Li-Ion', 'CAES', 'PHS', 'H2']) # set "j" : energy storage technologies
print('Size of model.j:', len(model.j))  # check that defined correctly

model.b = Set(within=model.j, initialize=['Li-Ion', 'PHS']) # set "b(j)" : storage technologies with coupled charging and discharging units
print('Size of model.b:', len(model.b))  # check that defined correctly

model.sp = Set(initialize=['P_Capex', 'E_Capex', 'Eff', 'Min_Duration', 'Max_Duration', 'Max_P', 'FOM', 'VOM', 'Lifetime', 'CostRatio']) # set "sp" : properties of storage technologies
print('Size of model.sp:', len(model.sp))  # check that defined correctly

model.Runs = RangeSet(1) 






#### Setting Scalars ####

separator = '=' * 50
print(f'\n{separator}\n{"Setting the scalars ....".center(len(separator))}\n{separator}\n')

# Define the scalars 
# model.FCR_VRE = Param(initialize=0, mutable=True) # (mutable parameters so that they can be changed without reconstructing entire model)
# model.FCR_GasCC = Param(initialize=0, mutable=True)
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
# model.r = Param(initialize=0.06, mutable=True)

print('Size of GenMix_Target:', len(model.GenMix_Target))  # check that defined correctly

r = 0.06  # Scalar value for the discount rate


# Calculate the FCR using the scalar value
def calculate_FCR(r):
    return (r * (1 + r)**30) / ((1 + r)**30 - 1)

fcr_value = calculate_FCR(r)

model.FCR_VRE = Param(initialize=fcr_value)
model.FCR_GasCC = Param(initialize=fcr_value)

print('Size of FCR_VRE:', len(model.FCR_VRE))  # check that defined correctly
print('Size of model.FCR_GasCC:', len(model.FCR_GasCC))  # check that defined correctly

fcr_value = calculate_FCR(r)
print(f"FCR calculated: {fcr_value}")



#### Create dictionaries from the dataframes which will be needed to define model.blabla ####

separator = '=' * 50
print(f'\n{separator}\n{"Creating necessary dictionaries ....".center(len(separator))}\n{separator}\n')

#--- Parameters for hourly data
load_data = {row['*Hour']: row['Load'] for _, row in load_hourly_2050_df.iterrows()} #  creating a dictionary where the keys are the values from the '*Hour' column, and the values are the corresponding 'Load' values from the load_hourly_2050_df DataFrame.
nuclear_data = {row['*Hour']: row['Nuclear'] for _, row in nucl_hourly_2019_df.iterrows()}
large_hydro_data = {row['*Hour']: row['Large Hydro'] for _, row in lahy_hourly_2019_df.iterrows()}
other_renewables_data = {row['*Hour']: row['OtherRenewables'] for _, row in otre_hourly_2019_df.iterrows()}

#--- Other Params

# GAMS command: Table CFSolar(h,k) Hourly capacity factor for solar PV plants (fraction)

cfsolar_data = {} # initialization
for index, row in cfsolar_2050_df.iterrows():
    hour = row['Hour']
    # Loop through each solar plant ID in the columns (excluding the 'Hour' column)
    for plant_id in cfsolar_2050_df.columns[1:]:
        cfsolar_data[(hour, plant_id)] = row[plant_id] # create a dictionary that maps each hour and plant ID to the corresponding capacity factor.

num_hours = 8760 # Number of hours should be 8760

num_solar_plants = len(cfsolar_2050_df.columns) - 1 # Number of solar PV plants is the number of columns minus 1 (for the 'Hour' column)

expected_num_items = num_hours * num_solar_plants # The expected number of items in the dictionary

# The actual number of items in the dictionary
actual_num_items = len(cfsolar_data)

# Check if the actual number of items matches the expected number
if actual_num_items == expected_num_items:
    print("The dictionary has the correct number of items.")
else:
    print("The number of items in the dictionary is incorrect.")
    print(f"Expected number of items: {expected_num_items}")
    print(f"Actual number of items: {actual_num_items}")


# GAMS command: Table CFWind(h,w) Hourly capacity factor for wind plants (fraction)

# cfwind_data = {(row['h'], row['w']): row['CFWind'] for _, row in cfwind_2050_df.iterrows()}

cfwind_data = {}
for _, row in cfwind_2050_df.iterrows():
    for col in cfwind_2050_df.columns:
        if col != 'Hour':  # don't want to use the 'Hour' column as a plant identifier
            cfwind_data[(row['Hour'], col)] = row[col]


# GAMS command: Table CapSolar(k,l) Properties of the solar PV plants

capsolar_data = {}
for _, row in capsolar_2050_df.iterrows():
    k_id = str(int(row['sc_gid'])) 
    for l_property in model.l:
        if l_property in capsolar_2050_df.columns:
            capsolar_data[(k_id, l_property)] = row[l_property]
        else:
            capsolar_data[(k_id, l_property)] = None  # or some default value
            print(f"Solar property {l_property} not found for plant {k_id}")

# Debugging: print out the first few keys to check their format
print(list(capsolar_data.keys())[:5])



# GAMS command: Table CapWind(w,l) Properties of the wind plants


capwind_data = {}
for _, row in capwind_2050_df.iterrows():
    w_id = str(int(row['sc_gid']))  
    for l_property in model.l:
        if l_property in capwind_2050_df.columns:
            capwind_data[(w_id, l_property)] = row[l_property]
        else:
            capwind_data[(w_id, l_property)] = None  # or some default value
            print(f"Wind property {l_property} not found for plant {w_id}")

# Debugging: print out the first few keys to check their format
print(list(capwind_data.keys())[:5])


# GAMS command: Table StorageData(sp,j) Properties of storage technologies

# storagedata_data = {(row['sp'], row['j']): row['StorageData'] for _, row in storagedata_2050_df.iterrows()}


storage_data = {}
for _, row in storagedata_2050_df.iterrows():
    property_name = row['Unnamed: 0']  
    for tech in model.j:
        storage_data[(property_name, tech)] = row[tech]

print(list(storage_data.keys()))



#### Initialize model parameters ####

separator = '=' * 50
print(f'\n{separator}\n{"Initializing model parameters ....".center(len(separator))}\n{separator}\n')


model.Load = Param(model.h, initialize=load_data)  
model.Nuclear = Param(model.h, initialize=nuclear_data)
model.LargeHydro = Param(model.h, initialize=large_hydro_data)
model.OtherRenewables = Param(model.h, initialize=other_renewables_data)


model.CFSolar = Param(model.h, model.k, initialize=cfsolar_data)  
model.CFWind = Param(model.h, model.w, initialize=cfwind_data)
model.CapSolar = Param(model.k, model.l, initialize=capsolar_data)

model.CapWind = Param(model.w, model.l, initialize=capwind_data)

model.StorageData = Param(model.sp, model.j, initialize=storage_data)


print('Size of model.CFSolar:', len(model.CFSolar))  # check that defined correctly
print('Size of model.CFWind:', len(model.CFWind))  # check that defined correctly
print('Size of model.CapSolar:', len(model.CapSolar))  # check that defined correctly
print('Size of model.CapWind:', len(model.CapWind))  # check that defined correctly
print('Size of model.StorageData:', len(model.StorageData))  # check that defined correctly



r = 0.06  # Scalar value for the discount rate

def crf_rule(model, j):
    n = model.StorageData['Lifetime', j]
    # return (r * (1 + r)**n) / ((1 + r)**n - 1)
    print(f"crf_rule called for storage technology {j} with lifetime {n}")
    crf = (r * (1 + r)**n) / ((1 + r)**n - 1)
    print(f"CRF for {j} with lifetime {n}: {crf}")
    return crf

# Initialize the CRF parameter with the updated rule
model.CRF = Param(model.j, initialize=crf_rule)



#### Setting Variables ####

separator = '=' * 50
print(f'\n{separator}\n{"Setting model variables ....".center(len(separator))}\n{separator}\n')

# model.TSC = Var(domain=Reals) # free variable
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

separator = '=' * 50
print(f'\n{separator}\n{"Setting equations ....".center(len(separator))}\n{separator}\n')

#actual objective function
model.TotalSystemCost = Objective(
    expr=sum(
        (model.FCR_VRE * (1000 * model.CapSolar[k, 'CAPEX_M'] + model.CapSolar[k, 'trans_cap_cost']) + 1000 * model.CapSolar[k, 'FOM_M']) * model.CapSolar[k, 'capacity'] * model.Ypv[k] for k in model.k
    ) +
    sum(
        (model.FCR_VRE * (1000 * model.CapWind[w, 'CAPEX_M'] + model.CapWind[w, 'trans_cap_cost']) + 1000 * model.CapWind[w, 'FOM_M']) * model.CapWind[w, 'capacity'] * model.Ywind[w] for w in model.w
    ) +
    sum(
        model.CRF[j] * (1000 * model.StorageData['CostRatio', j] * model.StorageData['P_Capex', j] * model.Pcha[j] + 1000 * (1 - model.StorageData['CostRatio', j]) * model.StorageData['P_Capex', j] * model.Pdis[j] + 1000 * model.StorageData['E_Capex', j] * model.Ecap[j]) for j in model.j
    ) +
    sum(
        1000 * model.StorageData['CostRatio', j] * model.StorageData['FOM', j] * model.Pcha[j] + 1000 * (1 - model.StorageData['CostRatio', j]) * model.StorageData['FOM', j] * model.Pdis[j] + model.StorageData['VOM', j] * sum(model.PD[h, j] for h in model.h) for j in model.j
    ) +
    model.FCR_GasCC * 1000 * model.CapexGasCC * model.CapCC + model.GasPrice * model.HR * sum(model.GenCC[h] for h in model.h) + model.FOM_GasCC * 1000 * model.CapCC + model.VOM_GasCC * sum(model.GenCC[h] for h in model.h),
    sense=minimize
)
#end



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


## End of opt. problem definition




#### Solver Configuration and Execution ####

separator = '=' * 50
print(f'\n{separator}\n{"Solver configuration and execution ....".center(len(separator))}\n{separator}\n')


# Solver stuff: 

# Create a solver
solver = SolverFactory('cbc')

# Setting solver options if necessary 
solver.options['ratioGap'] = 0.03 # Equivalent to optcr in GAMS
solver.options['sec'] = 1000000 # Equivalent to resLim in GAMS, but this is a very high limit
solver.options['threads'] = 4 # Assuming CBC supports this option for parallel processing

# Solve the model
result = solver.solve(model, tee=True, logfile='solver.log')

# Check the results
if (result.solver.status == SolverStatus.ok) and (result.solver.termination_condition == TerminationCondition.optimal):
    # detailed_results = extract_and_store_results(model) #df for results
    print("Solver found an optimal solution!")
elif result.solver.termination_condition == TerminationCondition.infeasible:
    print("Solver declared model infeasible.")
else:
    # Something else is wrong
    print("Solver Status: ", result.solver.status)


print("Finished everything")

