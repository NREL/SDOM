# Storage Deployment Optimization Model (SDOM).
SDOM is designed to accurately represent the operation of energy storage across different timescales, including long-duration and seasonal applications, and the spatiotemporal diversity and complementarity among VRE sources. SDOM uses an hourly temporal resolution, a fine spatial resolution for VRE sources, and a 1-year optimization window. SDOM assumes that all builds of VRE are accompanied by sufficient additional transmission capacity to allow full utilization of these additional resources. Nuclear, hydropower, and other renewable generation (e.g., biomass and geothermal energy sources) are fixed based on operational data (time series) for a given year; thus, SDOM minimizes total system cost using conventional generators as balancing units and using VRE and storage technologies to achieve a user-defined carbon-free or renewable energy target. The total system cost includes capital costs, fixed operation-and-maintenance (FO&M) costs, variable operation-and-maintenance (VO&M) costs, and fuel cost for power generation and storage technologies.
Associated publication: Optimal energy storage portfolio for high and ultrahigh carbon-free and renewable power systems (https://pubs.rsc.org/en/content/articlelanding/2021/ee/d1ee01835c)

# 1. INPUTS
All the input files should be in a folder called "inputs".

## 1.1. Variable Renewable Energy (VRE) Generation

### 1.1.1.	CapSolar_ yyyy.csv and CapWind_ yyyy.csv
Each of these files contains the information of Capex for the installation of new Solar and wind power plants in the year “yyyy”. It includes the following columns, some of them mandatory and others are optional:
	sc_gid (Mandatory): Unique identifier for each geographical area where new Wind/Solar can be installed.
	mean_cf (optional): Mean Capacity Factor
	mean_lcoe (optional): Mean Levelized Cost of Energy.
	mean_res (optional):
	Capacity (Mandatory): Maximum capacity in MW that it is possible to install at the geographical area identified by the “sc_gid”.
	Latitude (optional): Latitude coordinates of the geographical area identified by the “sc_gid”.
	Longitude (optional): Longitude coordinates of the geographical area identified by the “sc_gid”.
	Lcot (optional): Annual Levelized Cost of Transmission.
	total_lcoe (optional): Total Levelized Cost of Energy
	lcoe (optional): Levelized Cost of Energy.
	trans_cap_cost (Mandatory): CAPEX Cost of transmission needed to connect new Solar or Wind power plants to the grid from the geographical area identified by the “sc_gid”. This is given in USD/MW or monetary units per MW.
	CAPEX_M (Mandatory): CAPEX in USD/MW or monetary units per MW – moderate.
	FOM_M (Mandatory): Fixed operational maintenance in USD/kW-year or monetary units per MW – moderate.
	CAPEX_A (optional): CAPEX in USD/MW or monetary units per MW – Advanced (Optimistic).
	FOM_A (optional): Fixed operational maintenance in USD/kW-year or monetary units per MW – Advanced (Optimistic).
	CAPEX_C (optional): CAPEX in USD/MW or monetary units per MW – Conservative (Pessimistic).
	FOM_C (optional): Fixed operational maintenance in USD/kW-year or monetary units per MW – Conservative (Pessimistic).

### 1.1.2 CFSolar_ yyyy.csv and CFWind_ yyyy.csv
These files contain the hourly time series of each geographical area where new Wind/Solar can be installed.
In this way, each row (“sc_gid”) of the files CapSolar.csv/CapWind must have a column in the correspondent CFSolar.csv /CFWind.csv with 8760 entries which correspond to the capacity factor at each hour of the year.


### 1.1.3 Other renewables - otre_hourly_yyyy.csv.
The file “otre_hourly_yyyy.csv” contains the combined hourly time series other existent renewable power plants (Not large wind, solar and hydro) in MW, for the year “yyyy”. This results in a column with 8760 entries.
	LARGE HYDRO - lahy_hourly_yyyy.csv
The file “lahy_hourly_yyyy.csv” contains the combined hourly time series considering the generation of all the existent large Hydro power plants in MW, for the year “yyyy”. This results in a column with 8760 entries.


## 1.3. LOAD TIME-SERIES - “Load_hourly_yyyy.csv”
The file “Load_hourly_yyyy.csv” contains the hourly total net load time series in MW, for the year “yyyy”. This results in a column with 8760 entries. Please inform here the net Load (Load_net) which correspond to the resulting load of subtracting the total load and the distributed generation (Load_net=Load_total-DG).

## 1.4. STORAGE - “StorageData_yyyy.csv”
The file “StorageData_yyyy.csv” contains the information related to different storage technologies.

## 1.5. Scalar parameters - scalars.csv
This CSV file includes the following parameters:

 - FCR_VRE = Fixed Charge Rate for VRE
 - LifeTimeVRE = Life time of VRE in years
 - FCR_GasCC =  Fixed Charge Rate for Gas CC /0 /
 - LifeTimeGasCC = Life time of VRE in years
 - GenMix_Target =  /%GenMix_TargetValue%/
 - CapexGasCC =  Capex for gas combined cycle units (US$ per kW) /940.6078576/
 - HR =  Heat rate of gas combined cycle units (MMBtu per MWh) /6.4005/
 - GasPrice =  Gas prices (US$ per MMBtu per) /4.113894393/
 - FOM_GasCC =  FO&M for gas combined cycle units (US$ per kW-year) /13.2516707/
 - VOM_GasCC =  VO&M for gas combined cycle units (US$ per MWh) /2.226321156/
 - AlphaNuclear =  Activation of nuclear generation /%AlphaNuclearValue%/
 - AlphaLargHy =  Activation of large hydro generation /1/
 - AlphaOtheRe =  Activation of other renewable generation /1/
 - MaxCycles =  Lifetime (100% DoD) of Li-Ion batteries (cycles) /3250/
 - r =  discount rate