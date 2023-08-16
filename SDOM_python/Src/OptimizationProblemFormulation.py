from pyomo.environ import *
import pandas as pd
import numpy as np

# TODO: check paths dynamic

# Parameters
hours = range(1, 8761)
k = np.loadtxt('Set_k_SolarPV.txt')
w = np.loadtxt('Set_w_Wind.txt')
l = np.loadtxt('Set_l_Properties.txt')
j_storage = ['Li-Ion', 'CAES', 'PHS', 'H2']
b = ['Li-Ion', 'PHS']
sp = ['P_Capex', 'E_Capex', 'Eff', 'Min_Duration', 'Max_Duration',
      'Max_P', 'FOM', 'VOM', 'lifetime', 'CostRatio']
Runs = 1

Load = np.loadtxt('Load_hourly_2050.csv', delimiter=',')
Nuclear = np.loadtxt('Nucl_hourly_2019.csv', delimiter=',')
LargeHydro = np.loadtxt('lahy_hourly_2019.csv', delimiter=',')
OtherRenewables = np.loadtxt('otre_hourly_2019.csv', delimiter=',')
CFSolar = np.loadtxt('CFSolar_2050.csv', delimiter=',')
CFWind = np.loadtxt('CFWind_2050.csv', delimiter=',')
CapSolar = np.loadtxt('CapSolar_2050.csv', delimiter=',')
CapWind = np.loadtxt('CapWind_2050.csv', delimiter=',')
StorageData = np.loadtxt('StorageData_2050.csv', delimiter=',')

FCR_VRE = (r * (1 + r) ** 30) / ((1 + r) ** 30 - 1)
FCR_GasCC = (r * (1 + r) ** 30) / ((1 + r) ** 30 - 1)
CRF = (r * (1 + r) ** StorageData[:, -1]) / ((1 + r) ** StorageData[:, -1] - 1)

# Scalars
FCR_VRE = 0
FCR_GasCC = 0
GenMix_Target = 1.00
CapexGasCC = 940.6078576
HR = 6.4005
GasPrice = 4.113894393
FOM_GasCC = 13.2516707
VOM_GasCC = 2.226321156
AlphaNuclear = 1
AlphaLargHy = 1
AlphaOtheRe = 1
MaxCycles = 3250
r = 0.06

# Variables

# TODO


# Constraints

def load_balance_rule(model, h):  # Load Balance
    return Load[h] + sum(PC[h, :]) - AlphaNuclear * Nuclear[h] - AlphaLargHy * LargeHydro[h] - AlphaOtheRe * OtherRenewables[h] - GenPV[h] - GenWind[h] - sum(PD[h, :]) - GenCC[h] == 0


model.load_balance = Constraint(range(len(Load)), rule=load_balance_rule)


def gencc_rule(model):  # GenCC
    return sum(GenCC) <= (1 - GenMix_Target) * sum(Load + sum(PC, 2) - sum(PD, 2))


model.gencc_constraint = Constraint(rule=gencc_rule)


def genpv_rule(model, h):  # GenPV
    return GenPV[h] + CurtPV[h] == sum(CFSolar[h, :] * CapSolar[:, 'capacity'] * Ypv)


model.genpv_constraint = Constraint(range(len(GenPV)), rule=genpv_rule)


def genwind_rule(model, h):  # GenWind
    return GenWind[h] + CurtWind[h] == sum(CFWind[h, :] * CapWind[:, 'capacity'] * Ywind)


model.genwind_constraint = Constraint(range(len(GenWind)), rule=genwind_rule)


def storage_data_rule(model, h, j):  # StorageData
    model.pc_constraint = Constraint(
        expr=PC[h, j] <= StorageData['Max_P', j] * Ystorage[j, h])
    model.pd_constraint = Constraint(
        expr=PD[h, j] <= StorageData['Max_P', j] * (1 - Ystorage[j, h]))
    model.pc_pcha_constraint = Constraint(expr=PC[h, j] <= Pcha[j])
    model.pd_pdis_constraint = Constraint(expr=PD[h, j] <= Pdis[j])
    model.soc_ecap_constraint = Constraint(expr=SOC[h, j] <= Ecap[j])
    if h > 1:
        model.soc_dynamic_constraint = Constraint(expr=SOC[h, j] == sum(SOC[h-1, j]) + sqrt(
            StorageData['Eff', j]) * PC[h, j] - (1 / sqrt(StorageData['Eff', j])) * PD[h, j])
    if h == 1:
        model.soc_initial_constraint = Constraint(expr=SOC[h, j] == sum(SOC[end, j]) + sqrt(
            StorageData['Eff', j]) * PC[h, j] - (1 / sqrt(StorageData['Eff', j])) * PD[h, j])


model.storage_data_constraint = Constraint(
    range(len(PC)), range(size(StorageData, 2)), rule=storage_data_rule)

model.pcha_constraint = Constraint(expr=Pcha <= StorageData['Max_P', :])

model.pdis_constraint = Constraint(expr=Pdis <= StorageData['Max_P', :])

model.pcha_pdis_equality_constraint = Constraint(expr=Pcha == Pdis)

model.ecap_min_duration_constraint = Constraint(
    expr=Ecap >= StorageData['Min_Duration', :] * (1 / sqrt(StorageData['Eff', :])) * Pdis)

model.ecap_max_duration_constraint = Constraint(
    expr=Ecap <= StorageData['Max_Duration', :] * (1 / sqrt(StorageData['Eff', :])) * Pdis)

model.capcc_gencc_constraint = Constraint(expr=CapCC >= GenCC)

model.pd_li_ion_constraint = Constraint(expr=sum(
    PD[:, 'Li-Ion']) <= (MaxCycles / StorageData['Lifetime', 'Li-Ion']) * Ecap['Li-Ion'])
