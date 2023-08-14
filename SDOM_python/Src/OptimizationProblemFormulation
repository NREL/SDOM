from pyomo.environ import *
import pandas as pd
import numpy as np

# Parameters
hours = range(1, 8761)
k = np.loadtxt('Set_k_SolarPV.txt')
w = np.loadtxt('Set_w_Wind.txt')
l = np.loadtxt('Set_l_Properties.txt')
j_storage = ['Li-Ion', 'CAES', 'PHS', 'H2']
b = ['Li-Ion', 'PHS']
sp = ['P_Capex', 'E_Capex', 'Eff', 'Min_Duration', 'Max_Duration', 'Max_P', 'FOM', 'VOM', 'lifetime', 'CostRatio']
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

#Variables 

###TODO
##TODO: check paths dynamic