# Storage Deployment Optimization Model (SDOM) 🔋
SDOM is an NREL open-source high-resolution grid planning framework designed to optimize the deployment and operation of energy storage technologies across diverse temporal and spatial scales. It is particularly suited for evaluating long-duration and seasonal storage applications, as well as the complementarity among variable renewable energy (VRE) sources.

## Table of contents
- [KEY FEATURES](#key-features)
  - [OPTIMIZATION SCOPE](#optimization-scope)
  - [NOTES ON MODEL EXPANSION](#notes-on-model-expansion)
- [PUBLICATIONS AND USE CASES OF SDOM](#publications-and-use-cases-of-sdom)
- [INPUTS](#-1.-inputs)

# Key Features
⚙️
- **Temporal Resolution:** Hourly simulations over a full year enable precise modeling of storage dynamics and renewable generation variability.

- **Spatial Resolution:** Fine-grained representation of VRE sources (e.g., solar, wind) captures geographic diversity and enhances system fidelity.

- **Copper Plate Modeling:** SDOM Model neglects transmission constraints to keep the model tractable from the computational standpoint. Future SDOM releases should include inter-regional transmission constraints.

- **Fixed Generation Profiles:** Nuclear, hydropower, and other non-variable renewables (e.g., biomass, geothermal) are treated as fixed inputs using year-long time series data.

- **System Optimization Objective:** Minimizes total system cost—including capital, fixed/variable O&M, and fuel costs—while satisfying user-defined carbon-free or renewable energy targets.

- **Modeling approach:** Formulated as a Mixed-Integer Linear Programming (MILP) model to allow rigorous optimization of discrete investment and operational decisions.

- **Platforms:** 
  - SDOM was originally developed in GAMS (https://github.com/NREL/SDOM). 
  
  - In order offer a full open-source solution also was developed this python package. This version will be released soon and it requires python 3.10+.

- **Solver Compatibility:** Currently the SDOM python version is only compatible with [open-source CBC solver](https://www.coin-or.org/Cbc/cbcuserguide.html). In this repo the [windows executable for cbc](./cbc.exe) is provided. You will need to provide the path of cbc solver to run SDOM as illustrated in our [script demonstration](#sdom-example-(demonstration-script))

## Optimization Scope
📉
SDOM performs cost minimization across a 1-year operation window using a copper plate assumption—i.e., no internal transmission constraints—making it computationally efficient while capturing major cost drivers. Conventional generators are used as balancing resources, and storage technologies serve to meet carbon or renewable penetration goals.

## Notes on Model Expansion
While SDOM currently supports a 1-year horizon, multiyear analyses could provide deeper insights into how interannual variability affects storage needs. Chronological, simulation-based approaches are better suited for this but present significant computational challenges—especially at hourly resolution. Extending SDOM to support multiyear optimization is left as future work.

# PUBLICATIONS AND USE CASES OF SDOM
📄
- **Original SDOM paper**:
  - [Guerra, O. J., Eichman, J., & Denholm, P. (2021). Optimal energy storage portfolio for high and ultrahigh carbon-free and renewable power systems. *Energy Environ. Sci.*, 14(10), 5132-5146. https://doi.org/10.1039/D1EE01835C.](https://pubs.rsc.org/en/content/articlelanding/2021/ee/d1ee01835c)
  - [NREL media relations (2021). Energy Storage Ecosystem Offers Lowest-Cost Path to 100% Renewable Power.](https://www.nrel.gov/news/detail/program/2021/energy-storage-ecosystem-offers-lowest-cost-path-to-100-renewable-power)

- [SDOM GAMS version software registration](https://www.osti.gov/biblio/code-111266)

- Uses cases in the "Renewables in Latin America and the Caribbean" or RELAC initiative (Uruguay, Peru, El Salvador):
  - [Guerra, O. J., et al. (2023). Accelerated Energy Storage Deployment in RELAC Countries. *National Renewable Energy Laboratory (NREL)*.](https://research-hub.nrel.gov/en/publications/accelerated-energy-storage-deployment-in-relac-countries)

- **Webinar video**:
 - [Guerra, O. J., et al. (2022). Optimizing Energy Storage for Ultra High Renewable Electricity Systems. Conference for Colorado Renewable Energy society.](https://www.youtube.com/watch?v=SYTnN6Z65kI) 


# 1. INPUTS
All the input files should be in a folder called "inputs".

## 1.1. Variable Renewable Energy (VRE) Generation

### 1.1.1.	CapSolar_ yyyy.csv and CapWind_ yyyy.csv
Each of these files contains the information of Capex for the installation of new Solar and wind power plants in the year “yyyy”. It includes the following columns, some of them mandatory and others are optional:
 - sc_gid (Mandatory): Unique identifier for each geographical area where new Wind/Solar can be installed.
 - mean_cf (optional): Mean Capacity Factor
 - mean_lcoe (optional): Mean Levelized Cost of Energy.
 - mean_res (optional):
 - Capacity (Mandatory): Maximum capacity in MW that it is possible to install at the geographical area identified by the “sc_gid”.
 - Latitude (optional): Latitude coordinates of the geographical area identified by the “sc_gid”.
 - Longitude (optional): Longitude coordinates of the geographical area identified by the “sc_gid”.
 - Lcot (optional): Annual Levelized Cost of Transmission.
 - total_lcoe (optional): Total Levelized Cost of Energy
 - lcoe (optional): Levelized Cost of Energy.
 - trans_cap_cost (Mandatory): CAPEX Cost of transmission needed to connect new Solar or Wind power plants to the grid from the geographical area identified by the “sc_gid”. This is given in USD/MW or monetary units per MW.
 - CAPEX_M (Mandatory): CAPEX in USD/MW or monetary units per MW – moderate.
 - FOM_M (Mandatory): Fixed operational maintenance in USD/kW-year or monetary units per MW – moderate.
 - CAPEX_A (optional): CAPEX in USD/MW or monetary units per MW – Advanced (Optimistic).
 - FOM_A (optional): Fixed operational maintenance in USD/kW-year or monetary units per MW – Advanced (Optimistic).
 - CAPEX_C (optional): CAPEX in USD/MW or monetary units per MW – Conservative (Pessimistic).
 - FOM_C (optional): Fixed operational maintenance in USD/kW-year or monetary units per MW – Conservative (Pessimistic).

### 1.1.2 CFSolar_ yyyy.csv and CFWind_ yyyy.csv
These files contain the hourly time series of each geographical area where new Wind/Solar can be installed.
In this way, each row (“sc_gid”) of the files CapSolar.csv/CapWind must have a column in the correspondent CFSolar.csv /CFWind.csv with 8760 entries which correspond to the capacity factor at each hour of the year.


### 1.1.3 Other renewables - otre_hourly_yyyy.csv.
The file “otre_hourly_yyyy.csv” contains the combined hourly time series other existent renewable power plants (Not large wind, solar and hydro) in MW, for the year “yyyy”. This results in a column with 8760 entries.
	
### 1.1.4 LARGE HYDRO - lahy_hourly_yyyy.csv
The file “lahy_hourly_yyyy.csv” contains the combined hourly time series considering the generation of all the existent large Hydro power plants in MW, for the year “yyyy”. This results in a column with 8760 entries.


## 1.3. LOAD TIME-SERIES - “Load_hourly_yyyy.csv”
The file “Load_hourly_yyyy.csv” contains the hourly total net load time series in MW, for the year “yyyy”. This results in a column with 8760 entries. Please inform here the net Load (Load_net) which correspond to the resulting load of subtracting the total load and the distributed generation (Load_net=Load_total-DG).

## 1.4. STORAGE - “StorageData_yyyy.csv”
The file “StorageData_yyyy.csv” contains the information related to different storage technologies.

## 1.5. Scalar parameters - scalars.csv
This CSV file includes the following parameters:

 - FCR_VRE = Fixed Charge Rate for VRE
 - LifeTimeVRE = Life time of VRE in years
 - FCR_GasCC =  Fixed Charge Rate for Gas CC
 - LifeTimeGasCC = Life time of VRE in years
 - GenMix_Target =  Renewable Energy Mix Target
 - CapexGasCC =  Capex for gas combined cycle units (US$ per kW)
 - HR =  Heat rate of gas combined cycle units (MMBtu per MWh)
 - GasPrice =  Gas prices (US$ per MMBtu per)
 - FOM_GasCC =  FO&M for gas combined cycle units (US$ per kW-year)
 - VOM_GasCC =  VO&M for gas combined cycle units (US$ per MWh)
 - AlphaNuclear =  Activation of nuclear generation
 - AlphaLargHy =  Activation of large hydro generation
 - AlphaOtheRe =  Activation of other renewable generation
 - MaxCycles =  Lifetime (100% DoD) of Li-Ion batteries (cycles)
 - r =  discount rate
