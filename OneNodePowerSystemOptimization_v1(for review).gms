$Title One node Optimal Technology Mix for VRE integration

$OnText

This model determines optimal technology mix, including wind, solar PV, and
energy storage, to achieve a given VRE target.


$OffText


Set h hours in the analysis period /1*8760/

Alias (h, hh)

Set    k potential solar PV plants
/
$include Set_k(SolarPV).txt
/

Set    w potential wind plants
/
$include Set_w(Wind).txt
/

Set    l properties of power plants
/
$include Set_l(Properties).txt
/

Set j energy storage technologies /Li-Ion, PHS, CAES, H2/
;

Set    sp properties of storage technologies /P_Capex, E_Capex, Eff, Min_Duration, Max_Duration, Max_P, FOM, VOM, lifetime/
;

Set Runs runs for the analysis /1*1/


Scalars
         FCR_VRE Fixed Charge Rate for VRE /0.098/
         FCR_GasCC Fixed Charge Rate for Gas CC /0.081/
         GenMix_Target /0/
         MaxSolarPV_Units maximum number of selected solar PV plants /1200/
         MaxWind_Units maximum number of selected wind plants /2300/
         MaxSolarPV_Cap maximum total capacity (GW) of selected solar PV plants /85/
         MaxWind_Cap maximum total capacity (GW) of selected wind plants /55/
         CapexGasCC Capex for gas combined cycle units (US$ per kW) /927/
         HR Heat rate of gas combined cycle units (MMBtu per MWh) /6.45/
         GasPrice Gas prices (US$ per MMBtu per) /3.256/
         AlphaNuclear Activation of nuclear generation /1/
         AlphaLargHy Activation of large hydro generation /1/
         AlphaOtheRe Activation of other renewable generation /1/
         MaxCycles Lifetime (100% DoD) of Li-Ion batteries (cycles) /3250/
         r discount rate /0.07/
;


Parameter Load(h) Load for every hour in the analysis period (MW)
/
$Ondelim
$include Load_hourly_2019.csv
$Offdelim
/

Parameter Nuclear(h) Generation from nuclear power plants for every hour in the analysis period (MW)
/
$Ondelim
$include Nucl_hourly_2019.csv
$Offdelim
/

Parameter LargeHydro(h) Generation from large hydro power plants for every hour in the analysis period (MW)
/
$Ondelim
$include lahy_hourly_2019.csv
$Offdelim
/

Parameter OtherRenewables(h) Generation from other renewable power plants for every hour in the analysis period (MW)
/
$Ondelim
$include otre_hourly_2019.csv
$Offdelim
/


Table CFSolar(h,k) Hourly capacity factor for solar PV plants (fraction)
$Ondelim
$include CFSolar150GW_2012.csv
$Offdelim

Table CFWind(h,w) Hourly capacity factor for wind plants (fraction)
$Ondelim
$include CFWind150GW_2012.csv
$Offdelim

Table CapSolar(k,l) Properties of the solar PV plants
$Ondelim
$include CapSolar150GW_2012.csv
$Offdelim

Table CapWind(w,l) Properties of the wind plants
$Ondelim
$include CapWind150GW_2012.csv
$Offdelim

Table StorageData(sp,j) Properties of storage technologies
$Ondelim
$include StoorageData_2050_VarEcap.csv
$Offdelim
;

Parameter CRF(j) Capital recovery factor for storage technology j
;

CRF(j) = (r*(1+r)**StorageData('Lifetime',j))/((1+r)**StorageData('Lifetime',j)-1);

Display CRF;

Free variable
         TSC Total electricity supply cost

Positive Variables
         PC(h,j) Charging power for storage technology j during hour h
         PD(h,j) Discharging power for storage technology j during hour h
         SOC(h,j) State-of-charge (SOC) for storage technology j during hour h
         Pcap(j) Power capacity for storage technology j
         Ecap(j) Energy capacity for storage technology j


         GenPV(h) Generated solar PV power during hour h
         CurtPV(h) Generated solar PV power during hour h
         GenWind(h) Generated wind power during hour h
         CurtWind(h) Generated wind power during hour h
         CapCC Capacity requirements for backup gas combined cycle units (MW)
         GenCC(h) Generation from the backup gas combined cycle units (MWh)

Binary variables
         Ystorage(j,h) 1 if storage technology j is charging during hour h (0 otherwise)
         Ypv(k) 1 if solar PV plant k is selected (0 otherwise)
         Ywind(w) 1 if wind plant w is selected (0 otherwise)
;


CapCC.up = smax (h, Load(h)-AlphaNuclear*Nuclear(h)-AlphaLargHy*LargeHydro(h)-AlphaOtheRe*OtherRenewables(h));

Display CapCC.up;

Equations
         Obj objective function
         Supply(h) Electricity supply during hour h
         GenMix_Share Equation for VRE target
         SolarBal(h) Balance of availability of solar PV power during hour h
         WindBal(h) Balance of availability of wind power during hour h
         ChargSt(h,j) Constraint for charging the storage devices
         DischargSt(h,j) Constraint for discharging the storage devices
         MaxPC(h,j) Maximum charging power for storage technology j during hour h
         MaxPD(h,j) Maximum discharging power for storage technology j during hour h
         MaxSOC(h,j) Maximum SOC for storage technology j during hour h
         EndVol(j) Constraint for the end-volume of storage technology j
         SOCBal(h,j) SOC balance storage technology j during hour h > 1
         IniBal(h,j) Initial (h = 1) SOC balance for storage technology j
         MaxPcap(j) Maximum power capacity for storage technology j
         MinEcap(j) Minimum energy capacity for storage technology j
         MaxEcap(j) Maximum energy capacity for storage technology j
         MaxSolarPV Maximum number of selected solar PV plants
         MaxWind Maximum number of selected wind plants
         MaxCapSolarPV Maximum total capacity of selected solar PV plants
         MaxCapWind Maximum total capacity of selected wind plants
         BackupGen(h) Required capacity from backup combined cycle units
         MaxCycleYear Maximum number of cycles per year for Li-Ion batteries
;

Obj..    TSC =e= sum(k, CapSolar(k,'total_lcoe')*sum(h,CFSolar(h,k)*CapSolar(k,'capacity'))*Ypv(k)) +

                 sum(w, CapWind(w,'total_lcoe')*sum(h,CFWind(h,w)*CapWind(w,'capacity'))*Ywind(w))  +

                 sum(j, CRF(j)*(1000*StorageData('P_Capex',j)*Pcap(j) + 1000*StorageData('E_Capex',j)*Ecap(j)))+

                 sum(j, 1000*StorageData('FOM',j)*Pcap(j) + StorageData('VOM',j)*Ecap(j))+

                 FCR_GasCC*1000*CapexGasCC*CapCC + GasPrice*HR*sum(h, GenCC(h));

Supply(h)..      Load(h)+sum(j, PC(h,j))-AlphaNuclear*Nuclear(h)-AlphaLargHy*LargeHydro(h)-AlphaOtheRe*OtherRenewables(h)-GenPV(h)-GenWind(h)-sum(j,PD(h,j))-GenCC(h)=e=0;

GenMix_Share..   sum(h, AlphaNuclear*Nuclear(h)+AlphaLargHy*LargeHydro(h)+AlphaOtheRe*OtherRenewables(h)+GenPV(h)+ GenWind(h)+sum(j,PD(h,j))) =g= GenMix_Target*sum(h,(Load(h)+ sum(j, PC(h,j))));

SolarBal(h)..    GenPV(h)+ CurtPV(h) =e= sum(k, CFSolar(h,k)*CapSolar(k,'capacity')*Ypv(k));

MaxSolarPV..     sum(k, Ypv(k)) =l= MaxSolarPV_Units;

MaxCapSolarPV..  sum(k, CapSolar(k,'capacity')*Ypv(k)) =l= 1000*MaxSolarPV_Cap;

WindBal(h)..     GenWind(h)+ CurtWind(h) =e= sum(w, CFWind(h,w)*CapWind(w,'capacity')*Ywind(w));

MaxWind..        sum(w, Ywind(w)) =l= MaxWind_Units;

MaxCapWind..     sum(w, CapWind(w,'capacity')*Ywind(w)) =l= 1000*MaxWind_Cap;

ChargSt(h,j)..   PC(h,j) =l= StorageData('Max_P',j)*Ystorage(j,h);

DischargSt(h,j)..  PD(h,j) =l= StorageData('Max_P',j)*(1-Ystorage(j,h));

MaxPC(h,j)..     PC(h,j) =l= Pcap(j);

MaxPD(h,j)..     PD(h,j) =l= Pcap(j);

MaxSOC(h,j)..    SOC(h,j) =l= Ecap(j);

EndVol(j)..      sum(h $ (ord(h) = card(h)), SOC(h,j)) =e= 0.5*Ecap(j);

SOCBal(h,j)$(ord(h) > 1)..       SOC(h,j) =e= sum(hh$(ord(hh) = ord(h) -1), SOC(hh,j))+ sqrt(StorageData('Eff',j))*PC(h,j)-(1/sqrt(StorageData('Eff',j)))*PD(h,j);

IniBal(h,j)$(ord(h) = 1)..       SOC(h,j) =e= 0.5*Ecap(j) + sqrt(StorageData('Eff',j))*PC(h,j)-(1/sqrt(StorageData('Eff',j)))*PD(h,j);

MaxPcap(j)..     Pcap(j) =l= StorageData('Max_P',j);

MinEcap(j)..     Ecap(j) =g= StorageData('Min_Duration',j)*(1/sqrt(StorageData('Eff',j)))*Pcap(j);

MaxEcap(j)..     Ecap(j) =l= StorageData('Max_Duration',j)*(1/sqrt(StorageData('Eff',j)))*Pcap(j);

BackupGen(h)..   CapCC =g= GenCC(h);

MaxCycleYear..   sum(h,PD(h,'Li-Ion')) =l= (MaxCycles/StorageData('Lifetime','Li-Ion'))*Ecap('Li-Ion') ;

*****************
$offlisting
$offsymxref offsymlist
*****************

Model TechMix /All/;

option optcr=0.01;

Option resLim = 1000000;

Option mip = CPLEX;
$onecho > cplex.opt
threads 4
$offecho
TechMix.OptFile = 1;

*$ONTEXT
option limrow=0;
option limcol=0;
option solprint = off;
option sysout = off;
*$OFFTEXT


Parameter
         TotalCapCC(Runs) Total capacity of gas combined cycle units (MW)
         TotalCapPV(Runs) Total capacity of solar PV units (MW)
         TotalCapWind(Runs) Total capacity of wind units (MW)
         TotalCapS(Runs,j) Total power capacity of storage units j (MW)
         TotalEcapS(Runs,j) Total energy capacity of storage units j (MW)
         TotalGenPV(Runs) Total generation from solar PV units (MWh)
         TotalGenWind(Runs) Total generation from wind units (MWh)
         TotalGenS(Runs,j) Total generation from storage units j (MWh)
         TotalCost(Runs) Total cost US$
         SummaryPC(Runs,h,j) Charging power for storage technology j during hour h (MW)
         SummaryPD(Runs,h,j) Discharging power for storage technology j during hour h (MW)
         SummarySOC(Runs,h,j) State-of-charge (SOC) for storage technology j during hour h (MWh)
         SolarPVGen(Runs,h) Generation from solar PV plants
         WindGen(Runs,h) Generation from wind plants
         SolarPVCurt(Runs,h) Curtailment from solar PV plants
         WindCurt(Runs,h) Curtailment from wind plants
         GenGasCC(Runs,h) Generation from gas CC unit
         StorageGasCC2Storage(Runs,h) Power from Storage and Gas CC to Storage
;

loop ( Runs ,
     GenMix_Target = 0.95;
     Display GenMix_Target;
     Solve TechMix using mip minimizing TSC;
     TotalCost(Runs) = TSC.l;
     TotalCapCC(Runs) = CapCC.l;
     TotalCapPV(Runs) = sum(k, CapSolar(k,'capacity')*Ypv.l(k));
     TotalCapWind(Runs) = sum(w, CapWind(w,'capacity')*Ywind.l(w));
     TotalCapS(Runs,j) = Pcap.l(j);
     TotalEcapS(Runs,j) = Ecap.l(j);
     TotalGenPV(Runs) = sum(h, GenPV.l(h));
     TotalGenWind(Runs) = sum(h, GenWind.l(h));
     TotalGenS(Runs,j) = sum((h),PD.l(h,j));
     SummaryPC(Runs,h,j) = PC.l(h,j);
     SummaryPD(Runs,h,j) = PD.l(h,j);
     SummarySOC(Runs,h,j) = SOC.l(h,j);
     SolarPVGen(Runs,h) = GenPV.l(h);
     WindGen(Runs,h) = GenWind.l(h);
     SolarPVCurt(Runs,h) = CurtPV.l(h);
     WindCurt(Runs,h) = CurtWind.l(h);
     GenGasCC(Runs,h) = GenCC.l(h);
     StorageGasCC2Storage(Runs,h) = (sum(j, PD.l(h,j)) + GenCC.l(h))$(Load(h)-AlphaNuclear*Nuclear(h)-AlphaLargHy*LargeHydro(h)-AlphaOtheRe*OtherRenewables(h)-GenPV.l(h)-GenWind.l(h) <= 0) +
                                     sum(j, PC.l(h,j))$(Load(h)-AlphaNuclear*Nuclear(h)-AlphaLargHy*LargeHydro(h)-AlphaOtheRe*OtherRenewables(h)-GenPV.l(h)-GenWind.l(h) > 0)
     );

FILE csv Report File /OutputSummary.csv/;
csv.pc = 5;
PUT csv;

PUT 'Run','Optimal'/;

PUT 'Total cost US$', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCost(Runs) /);

PUT 'Total capacity of gas combined cycle units (MW)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCapCC(Runs) /);

PUT 'Total capacity of solar PV units (MW)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCapPV(Runs) /);

PUT 'Total capacity of wind units (MW)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCapWind(Runs) /);

PUT 'Total generation from solar PV units (MWh)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalGenPV(Runs) /);

PUT 'Total generation from wind units (MWh)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalGenWind(Runs) /);

PUT 'Total power capacity of storage units j (MW)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalCapS(Runs,j) /);

PUT 'Total energy capacity of storage units j (MWh)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalEcapS(Runs,j) /);

PUT 'Total generation from storage units j (MWh)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalGenS(Runs,j) /);

Putclose ;

FILE csvPC Report File /Output_Storage_Charging.csv/;
csvPC.pc = 5;
PUT csvPC;

PUT 'Charging power for storage technology j during hour h (MW)', ' '/;
loop ((Runs,h,j),
     PUT Runs.tl, j.tl, h.tl, SummaryPC(Runs,h,j) /);
Putclose ;

FILE csvPD Report File /Output_Storage_Discharging.csv/;
csvPD.pc = 5;
PUT csvPD;

PUT 'Discharging power for storage technology j during hour h (MW)', ' '/;
loop ((Runs,h,j),
     PUT Runs.tl, j.tl, h.tl, SummaryPD(Runs,h,j) /);
Putclose ;

FILE csvSOC Report File /Output_state-of-charge.csv/;
csvSOC.pc = 5;
PUT csvSOC;

PUT 'State-of-charge (SOC) for storage technology j during hour h (MWh)', ' '/;
loop ((Runs,h,j),
     PUT Runs.tl, j.tl, h.tl, SummarySOC(Runs,h,j) /);
Putclose ;

FILE csvSolarPVGen Report File /Output_SolarPV_Generation.csv/;
csvSolarPVGen.pc = 5;
PUT csvSolarPVGen;

PUT 'Generation from solar PV plants', ' '/;
loop ((Runs,h),
     PUT Runs.tl, h.tl, SolarPVGen(Runs,h) /);
Putclose ;

FILE csvWindGen Report File /Output_Wind_Generation.csv/;
csvWindGen.pc = 5;
PUT csvWindGen;

PUT 'Generation from wind plants', ' '/;
loop ((Runs,h),
     PUT Runs.tl, h.tl, WindGen(Runs,h) /);
Putclose ;

FILE csvSolarPVCurt Report File /Output_SolarPV_Curtailment.csv/;
csvSolarPVCurt.pc = 5;
PUT csvSolarPVCurt;

PUT 'Curtailment from solar PV plants', ' '/;
loop ((Runs,h),
     PUT Runs.tl, h.tl, SolarPVCurt(Runs,h) /);
Putclose ;

FILE csvWindCurt Report File /Output_Wind_Curtailment.csv/;
csvWindCurt.pc = 5;
PUT csvWindCurt;

PUT 'Curtailment from wind plants', ' '/;
loop ((Runs,h),
     PUT Runs.tl, h.tl, WindCurt(Runs,h) /);
Putclose ;

FILE csvGenGasCC Report File /Output_GenGasCC_Generation.csv/;
csvGenGasCC.pc = 5;
PUT csvGenGasCC;

PUT 'Generation from gas CC unit', ' '/;
loop ((Runs,h),
     PUT Runs.tl, h.tl, GenGasCC(Runs,h) /);
Putclose ;

FILE csvStorGasCCToStor Report File /Output_StorageGasCC_Storage.csv/;
csvStorGasCCToStor.pc = 5;
PUT csvStorGasCCToStor;

PUT 'Power from Storage and Gas CC to Storage', ' '/;
loop ((Runs,h),
     PUT Runs.tl, h.tl, StorageGasCC2Storage(Runs,h) /);
Putclose ;
