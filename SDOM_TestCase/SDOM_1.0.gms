$Title One node Optimal Technology Mix for VRE integration

$call echo "%gams.input%" | sed -e "s/.*\\\([^\\]*\)\\[^\\]*/$setglobal FNAME \1/" > blub
$include blub
$call rm blub

$OnText

This model determines optimal technology mix, including wind, solar PV, and
energy storage, to achieve a given VRE target.

$OffText

$if not set GenMix_TargetValue    $set GenMix_TargetValue   1.00
$if not set AlphaNuclearValue     $set AlphaNuclearValue    1


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


Set j energy storage technologies /Li-Ion, CAES, PHS, H2/
;

set b(j) storage technologies with coupled charging and discharging units /Li-Ion, PHS/

Set    sp properties of storage technologies /P_Capex, E_Capex, Eff, Min_Duration, Max_Duration, Max_P, FOM, VOM, lifetime, CostRatio/
;

Set Runs runs for the analysis /1/


Scalars
         FCR_VRE Fixed Charge Rate for VRE /0 /
         FCR_GasCC Fixed Charge Rate for Gas CC /0 /
         GenMix_Target /%GenMix_TargetValue%/
         CapexGasCC Capex for gas combined cycle units (US$ per kW) /940.6078576/
         HR Heat rate of gas combined cycle units (MMBtu per MWh) /6.4005/
         GasPrice Gas prices (US$ per MMBtu per) /4.113894393/
         FOM_GasCC FO&M for gas combined cycle units (US$ per kW-year) /13.2516707/
         VOM_GasCC VO&M for gas combined cycle units (US$ per MWh) /2.226321156/
         AlphaNuclear Activation of nuclear generation /%AlphaNuclearValue%/
         AlphaLargHy Activation of large hydro generation /1/
         AlphaOtheRe Activation of other renewable generation /1/
         MaxCycles Lifetime (100% DoD) of Li-Ion batteries (cycles) /3250/
         r discount rate /0.06/
;

FCR_VRE = (r*(1+r)**30)/((1+r)**30-1);

FCR_GasCC = (r*(1+r)**30)/((1+r)**30-1);


Parameter Load(h) Load for every hour in the analysis period (MW)
/
$Ondelim
*$include Load_hourly_2019.csv
$include Load_hourly_2050.csv
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
$include CFSolar_2050.csv
$Offdelim

Table CFWind(h,w) Hourly capacity factor for wind plants (fraction)
$Ondelim
$include CFWind_2050.csv
$Offdelim

Table CapSolar(k,l) Properties of the solar PV plants
$Ondelim
$include CapSolar_2050.csv
$Offdelim

Table CapWind(w,l) Properties of the wind plants
$Ondelim
$include CapWind_2050.csv
$Offdelim

Table StorageData(sp,j) Properties of storage technologies
$Ondelim
$include StorageData_2050.csv
$Offdelim
;

Parameter CRF(j) Capital recovery factor for storage technology j
;

CRF(j) = (r*(1+r)**StorageData('Lifetime',j))/((1+r)**StorageData('Lifetime',j)-1);

*Display CRF;

Free variable
         TSC Total electricity supply cost

Positive Variables
         PC(h,j) Charging power for storage technology j during hour h
         PD(h,j) Discharging power for storage technology j during hour h
         SOC(h,j) State-of-charge (SOC) for storage technology j during hour h
         Pcha(j) Charge power capacity for storage technology j
         Pdis(j) Discharge power capacity for storage technology j
         Ecap(j) Energy capacity for storage technology j


         GenPV(h) Generated solar PV power during hour h
         CurtPV(h) Generated solar PV power during hour h
         GenWind(h) Generated wind power during hour h
         CurtWind(h) Generated wind power during hour h
         CapCC Capacity requirements for backup gas combined cycle units (MW)
         GenCC(h) Generation from backup gas combined cycle units (MWh)
         Ypv(k) Capacity selection for solar PV plant k
         Ywind(w) Capacity selection for wind plant w ;


Ypv.up(k)   = 1;
Ywind.up(w) =1;


Binary variables
         Ystorage(j,h) 1 if storage technology j is charging during hour h (0 otherwise)

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
         SOCBal(h,j) SOC balance storage technology j during hour h > 1
         IniBal(h,j) Initial (h = 1) SOC balance for storage technology j
         MaxPcha(j) Maximum charge power capacity for storage technology j
         MaxPdis(j) Maximum discharge power capacity for storage technology j
         PchaPdis(b) Coupling of charge and discharge power capacity for battery technology b
         MinEcap(j) Minimum energy capacity for storage technology j
         MaxEcap(j) Maximum energy capacity for storage technology j
         BackupGen(h) Required capacity from backup combined cycle units
         MaxCycleYear Maximum number of cycles per year for Li-Ion batteries
;

Obj..    TSC =e= sum(k, (FCR_VRE*(1000*CapSolar(k,'CAPEX_M') + CapSolar(k,'trans_cap_cost')) + 1000*CapSolar(k,'FOM_M'))*CapSolar(k,'capacity')*Ypv(k)) +

                 sum(w, (FCR_VRE*(1000*CapWind(w,'CAPEX_M') + CapWind(w,'trans_cap_cost')) + 1000*CapWind(w,'FOM_M'))*CapWind(w,'capacity')*Ywind(w))  +

                 sum(j, CRF(j)*(1000*StorageData('CostRatio',j)*StorageData('P_Capex',j)*Pcha(j) + 1000*(1-StorageData('CostRatio',j))*StorageData('P_Capex',j)*Pdis(j) + 1000*StorageData('E_Capex',j)*Ecap(j)))+

                 sum(j, 1000*StorageData('CostRatio',j)*StorageData('FOM',j)*Pcha(j) + 1000*(1-StorageData('CostRatio',j))*StorageData('FOM',j)*Pdis(j) + StorageData('VOM',j)*sum(h,PD(h,j)))+

                 FCR_GasCC*1000*CapexGasCC*CapCC + GasPrice*HR*sum(h, GenCC(h)) + FOM_GasCC*1000*CapCC + VOM_GasCC*sum(h, GenCC(h));

Supply(h)..      Load(h)+sum(j, PC(h,j))-AlphaNuclear*Nuclear(h)-AlphaLargHy*LargeHydro(h)-AlphaOtheRe*OtherRenewables(h)-GenPV(h)-GenWind(h)-sum(j,PD(h,j))-GenCC(h)=e=0;

GenMix_Share..   sum(h, GenCC(h)) =l= (1-GenMix_Target)*sum(h,Load(h) + sum(j, PC(h,j)) - sum(j,PD(h,j)) );

SolarBal(h)..    GenPV(h)+ CurtPV(h) =e= sum(k, CFSolar(h,k)*CapSolar(k,'capacity')*Ypv(k));

WindBal(h)..     GenWind(h)+ CurtWind(h) =e= sum(w, CFWind(h,w)*CapWind(w,'capacity')*Ywind(w));

ChargSt(h,j)..   PC(h,j) =l= StorageData('Max_P',j)*Ystorage(j,h);

DischargSt(h,j)..  PD(h,j) =l= StorageData('Max_P',j)*(1-Ystorage(j,h));

MaxPC(h,j)..     PC(h,j) =l= Pcha(j);

MaxPD(h,j)..     PD(h,j) =l= Pdis(j);

MaxSOC(h,j)..    SOC(h,j) =l= Ecap(j);

SOCBal(h,j)$(ord(h) > 1)..       SOC(h,j) =e= sum(hh$(ord(hh) = ord(h) -1), SOC(hh,j))+ sqrt(StorageData('Eff',j))*PC(h,j)-(1/sqrt(StorageData('Eff',j)))*PD(h,j);

IniBal(h,j)$(ord(h) = 1)..       SOC(h,j) =e= sum(hh $ (ord(hh) = card(hh)), SOC(hh,j)) + sqrt(StorageData('Eff',j))*PC(h,j)-(1/sqrt(StorageData('Eff',j)))*PD(h,j);

MaxPcha(j)..     Pcha(j) =l= StorageData('Max_P',j);

MaxPdis(j)..     Pdis(j) =l= StorageData('Max_P',j);

PchaPdis(b)..    Pcha(b) =e= Pdis(b);

MinEcap(j)..     Ecap(j) =g= StorageData('Min_Duration',j)*(1/sqrt(StorageData('Eff',j)))*Pdis(j);

MaxEcap(j)..     Ecap(j) =l= StorageData('Max_Duration',j)*(1/sqrt(StorageData('Eff',j)))*Pdis(j);

BackupGen(h)..   CapCC =g= GenCC(h);

MaxCycleYear..   sum(h,PD(h,'Li-Ion')) =l= (MaxCycles/StorageData('Lifetime','Li-Ion'))*Ecap('Li-Ion') ;

*****************
$offlisting
$offsymxref offsymlist
*****************

Model TechMix /All/;

option optcr=0.03;

Option resLim = 1000000;

Option mip = CPLEX;
$onecho > cplex.opt
*lpmethod 4
submipscale 1
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
         TotalCapScha(Runs,j) Total charge power capacity of storage units j (MW)
         TotalCapSdis(Runs,j) Total discharge power capacity of storage units j (MW)
         TotalEcapS(Runs,j) Total energy capacity of storage units j (MW)
         TotalGenPV(Runs) Total generation from solar PV units (MWh)
         TotalGenWind(Runs) Total generation from wind units (MWh)
         TotalGenS(Runs,j) Total generation from storage units j (MWh)
         TotalCost(Runs) Total cost US$
         SummaryPC(Runs,h,j) Charging power for storage technology j during hour h (MW)
         SummaryPD(Runs,h,j) Discharging power for storage technology j during hour h (MW)
         SummarySOC(Runs,h,j) State-of-charge (SOC) for storage technology j during hour h (MWh)
         SummaryD(Runs,j) Discharge duration for storage technology j (h)
         SolarPVGen(Runs,h) Generation from solar PV plants
         WindGen(Runs,h) Generation from wind plants
         SolarPVCurt(Runs,h) Curtailment from solar PV plants
         WindCurt(Runs,h) Curtailment from wind plants
         GenGasCC(Runs,h) Generation from gas CC unit
         SelectedSolarPV(Runs,k) Selected Solar PV plants
         SelectedWind(Runs,w) Selected Wind plants
         SolarCapex(Runs) Total Capex for solar PV
         WindCapex(Runs) Total Capex for wind
         SolarFOM(Runs) Total FOM for solar PV
         WindFOM(Runs) Total FOM for wind
         Li_Ion_Pcapex(Runs) Total Power Capex for Li-Ion
         Li_Ion_Ecapex(Runs) Total Energy Capex for Li-Ion
         Li_Ion_FOM(Runs) Total FOM for Li-Ion
         Li_Ion_VOM(Runs) Total VOM for Li-Ion
         CAES_Pcapex(Runs) Total Power Capex for CAES
         CAES_Ecapex(Runs) Total Energy Capex for CAES
         CAES_FOM(Runs) Total FOM for CAES
         CAES_VOM(Runs) Total VOM for CAES
         PHS_Pcapex(Runs) Total Power Capex for PHS
         PHS_Ecapex(Runs) Total Energy Capex for PHS
         PHS_FOM(Runs) Total FOM for PHS
         PHS_VOM(Runs) Total VOM for PHS
         H2_Pcapex(Runs) Total Power Capex for H2
         H2_Ecapex(Runs) Total Energy Capex for H2
         H2_FOM(Runs) Total FOM for H2
         H2_VOM(Runs) Total VOM for H2
         GasCC_Capex(Runs) Total Gas CC Capex
         GasCC_FOM(Runs) Total Gas CC FOM
         GasCC_VOM(Runs) Total Gas CC VOM
         GasCC_FUEL(Runs) Total Gas CC fuel cost
;


loop ( Runs ,
*     GenMix_Target = 0.70 + 0.05*ord(Runs);
     Display GenMix_Target;
     Solve TechMix using mip minimizing TSC;
     TotalCost(Runs) = TSC.l;
     TotalCapCC(Runs) = CapCC.l;
     TotalCapPV(Runs) = sum(k, CapSolar(k,'capacity')*Ypv.l(k));
     TotalCapWind(Runs) = sum(w, CapWind(w,'capacity')*Ywind.l(w));
     TotalCapScha(Runs,j) = Pcha.l(j);
     TotalCapSdis(Runs,j) = Pdis.l(j);
     TotalEcapS(Runs,j) = Ecap.l(j);
     TotalGenPV(Runs) = sum(h, GenPV.l(h));
     TotalGenWind(Runs) = sum(h, GenWind.l(h));
     TotalGenS(Runs,j) = sum((h),PD.l(h,j));
     SummaryPC(Runs,h,j) = PC.l(h,j);
     SummaryPD(Runs,h,j) = PD.l(h,j);
     SummarySOC(Runs,h,j) = SOC.l(h,j);
     SummaryD(Runs,j) = sqrt(StorageData('Eff',j))*Ecap.l(j)/(Pdis.l(j) + 1e-15);
     SolarPVGen(Runs,h) = GenPV.l(h);
     WindGen(Runs,h) = GenWind.l(h);
     SolarPVCurt(Runs,h) = CurtPV.l(h);
     WindCurt(Runs,h) = CurtWind.l(h);
     GenGasCC(Runs,h) = GenCC.l(h);
     SelectedSolarPV(Runs,k) = Ypv.l(k);
     SelectedWind(Runs,w) = Ywind.l(w);
     SolarCapex(Runs) = sum(k, (FCR_VRE*(1000*CapSolar(k,'CAPEX_M') + CapSolar(k,'trans_cap_cost'))*CapSolar(k,'capacity')*Ypv.l(k)));
     WindCapex(Runs) = sum(w, (FCR_VRE*(1000*CapWind(w,'CAPEX_M') + CapWind(w,'trans_cap_cost'))*CapWind(w,'capacity')*Ywind.l(w)));
     SolarFOM(Runs) = sum(k, 1000*CapSolar(k,'FOM_M')*CapSolar(k,'capacity')*Ypv.l(k));
     WindFOM(Runs) = sum(w, 1000*CapWind(w,'FOM_M')*CapWind(w,'capacity')*Ywind.l(w));
     Li_Ion_Pcapex(Runs) = CRF('Li-Ion')*(1000*StorageData('CostRatio','Li-Ion')*StorageData('P_Capex','Li-Ion')*Pcha.l('Li-Ion') + 1000*(1-StorageData('CostRatio','Li-Ion'))*StorageData('P_Capex','Li-Ion')*Pdis.l('Li-Ion') );
     Li_Ion_Ecapex(Runs)  = CRF('Li-Ion')*1000*StorageData('E_Capex','Li-Ion')*Ecap.l('Li-Ion');
     CAES_Pcapex(Runs) = CRF('CAES')*(1000*StorageData('CostRatio','CAES')*StorageData('P_Capex','CAES')*Pcha.l('CAES') + 1000*(1-StorageData('CostRatio','CAES'))*StorageData('P_Capex','CAES')*Pdis.l('CAES') );
     CAES_Ecapex(Runs)  = CRF('CAES')*1000*StorageData('E_Capex','CAES')*Ecap.l('CAES');
     PHS_Pcapex(Runs) = CRF('PHS')*(1000*StorageData('CostRatio','PHS')*StorageData('P_Capex','PHS')*Pcha.l('PHS') + 1000*(1-StorageData('CostRatio','PHS'))*StorageData('P_Capex','PHS')*Pdis.l('PHS') );
     PHS_Ecapex(Runs)  = CRF('PHS')*1000*StorageData('E_Capex','PHS')*Ecap.l('PHS');
     H2_Pcapex(Runs) = CRF('H2')*(1000*StorageData('CostRatio','H2')*StorageData('P_Capex','H2')*Pcha.l('H2') + 1000*(1-StorageData('CostRatio','H2'))*StorageData('P_Capex','H2')*Pdis.l('H2') );
     H2_Ecapex(Runs)  = CRF('H2')*1000*StorageData('E_Capex','H2')*Ecap.l('H2');
     Li_Ion_FOM(Runs) = 1000*StorageData('CostRatio','Li-Ion')*StorageData('FOM','Li-Ion')*Pcha.l('Li-Ion') + 1000*(1-StorageData('CostRatio','Li-Ion'))*StorageData('FOM','Li-Ion')*Pdis.l('Li-Ion') ;
     Li_Ion_VOM(Runs) = StorageData('VOM','Li-Ion')*sum(h,PD.l(h,'Li-Ion'));
     CAES_FOM(Runs) = 1000*StorageData('CostRatio','CAES')*StorageData('FOM','CAES')*Pcha.l('CAES') + 1000*(1-StorageData('CostRatio','CAES'))*StorageData('FOM','CAES')*Pdis.l('CAES') ;
     CAES_VOM(Runs) = StorageData('VOM','CAES')*sum(h,PD.l(h,'CAES'));
     PHS_FOM(Runs) = 1000*StorageData('CostRatio','PHS')*StorageData('FOM','PHS')*Pcha.l('PHS') + 1000*(1-StorageData('CostRatio','PHS'))*StorageData('FOM','PHS')*Pdis.l('PHS') ;
     PHS_VOM(Runs) = StorageData('VOM','PHS')*sum(h,PD.l(h,'PHS'));
     H2_FOM(Runs) = 1000*StorageData('CostRatio','H2')*StorageData('FOM','H2')*Pcha.l('H2') + 1000*(1-StorageData('CostRatio','H2'))*StorageData('FOM','H2')*Pdis.l('H2') ;
     H2_VOM(Runs) = StorageData('VOM','H2')*sum(h,PD.l(h,'H2'));
     GasCC_Capex(Runs) = FCR_GasCC*1000*CapexGasCC*CapCC.l;
     GasCC_FOM(Runs) = FOM_GasCC*1000*CapCC.l;
     GasCC_VOM(Runs) = VOM_GasCC*sum(h, GenCC.l(h));
     GasCC_FUEL(Runs) = GasPrice*HR*sum(h, GenCC.l(h));

);

FILE csv Report File /OutputSummary.csv/;
PUT csv
put_utility 'ren' / 'OutputSummary_SDOM_%FNAME%_Nuclear_' AlphaNuclear:0:0 '_Target_' GenMix_Target:00 '_.csv';
csv.pc = 5;
PUT csv;

PUT 'Run','Optimal'/;

PUT 'Total cost US$', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCost(Runs):0:5 /);

PUT 'Total capacity of gas combined cycle units (MW)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCapCC(Runs):0:5 /);

PUT 'Total capacity of solar PV units (MW)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCapPV(Runs):0:5 /);

PUT 'Total capacity of wind units (MW)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalCapWind(Runs):0:5 /);

PUT 'Total generation from solar PV units (MWh)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalGenPV(Runs):0:5 /);

PUT 'Total generation from wind units (MWh)', ' '/;
loop (Runs,
     PUT Runs.tl, TotalGenWind(Runs):0:5 /);

PUT 'Total charge power capacity of storage units j (MW)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalCapScha(Runs,j):0:5 /);

PUT 'Total discharge power capacity of storage units j (MW)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalCapSdis(Runs,j):0:5 /);

PUT 'Total energy capacity of storage units j (MWh)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalEcapS(Runs,j):0:5 /);

PUT 'Discharge duration for storage technology j (h)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, SummaryD(Runs,j):0:5 /);

PUT 'Total generation from storage units j (MWh)', ' '/;
loop ((Runs,j),
     PUT Runs.tl, j.tl, TotalGenS(Runs,j):0:5 /);

PUT 'Solar Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, SolarCapex(Runs):0:5 /);

PUT 'Solar FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, SolarFOM(Runs):0:5 /);

PUT 'Wind Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, WindCapex(Runs):0:5 /);

PUT 'Wind FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, WindFOM(Runs):0:5 /);

PUT 'Li-Ion Power Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, Li_Ion_Pcapex(Runs):0:5 /);

PUT 'Li-Ion Energy Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, Li_Ion_Ecapex(Runs):0:5 /);

PUT 'Li-Ion FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, Li_Ion_FOM(Runs):0:5 /);

PUT 'Li-Ion VOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, Li_Ion_VOM(Runs):0:5 /);

PUT 'CAES Power Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, CAES_Pcapex(Runs):0:5 /);

PUT 'CAES Energy Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, CAES_Ecapex(Runs):0:5 /);

PUT 'CAES FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, CAES_FOM(Runs):0:5 /);

PUT 'CAES VOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, CAES_VOM(Runs):0:5 /);

PUT 'PHS Power Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, PHS_Pcapex(Runs):0:5 /);

PUT 'PHS Energy Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, PHS_Ecapex(Runs):0:5 /);

PUT 'PHS FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, PHS_FOM(Runs):0:5 /);

PUT 'PHS VOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, PHS_VOM(Runs):0:5 /);

PUT 'H2 Power Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, H2_Pcapex(Runs):0:5 /);

PUT 'H2 Energy Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, H2_Ecapex(Runs):0:5 /);

PUT 'H2 FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, H2_FOM(Runs):0:5 /);

PUT 'H2 VOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, H2_VOM(Runs):0:5 /);

PUT 'GasCC Capex US$', ' '/;
loop (Runs,
     PUT Runs.tl, GasCC_Capex(Runs):0:5 /);

PUT 'GasCC FUEL US$', ' '/;
loop (Runs,
     PUT Runs.tl, GasCC_FUEL(Runs):0:5 /);

PUT 'GasCC FOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, GasCC_FOM(Runs):0:5 /);

PUT 'GasCC VOM US$', ' '/;
loop (Runs,
     PUT Runs.tl, GasCC_VOM(Runs):0:5 /);

Putclose ;

FILE csvStorage Report File /OutputStorage.csv/;
PUT csvStorage
put_utility 'ren' / 'OutputStorage_SDOM_%FNAME%_Nuclear_' AlphaNuclear:0:0 '_Target_' GenMix_Target:00 '_.csv';
csvStorage.pc = 5;
PUT csvStorage;

PUT 'Scenario', 'Technology', 'Hour', 'Charging power (MW)', 'Disharging power (MW)', 'State of charge (MWh)'  /;
loop ((Runs,h,j),
     PUT Runs.tl, j.tl, h.tl, SummaryPC(Runs,h,j):0:5, SummaryPD(Runs,h,j):0:5, SummarySOC(Runs,h,j):0:5 /);
Putclose ;


FILE csvGen Report File /OutputGeneration.csv/;
PUT csvGen
put_utility 'ren' / 'OutputGeneration_SDOM_%FNAME%_Nuclear_' AlphaNuclear:0:0 '_Target_' GenMix_Target:00 '_.csv';
csvGen.pc = 5;
PUT csvGen;

PUT 'Scenario', 'Hour','Solar PV Generation (MW)', 'Solar PV Curtailment (MW)', 'Wind Generation (MW)', 'Wind Curtailment (MW)', 'Gas CC Generation (MW)', 'Power from Storage and Gas CC to Storage (MW)' /;
loop ((Runs,h),
     PUT Runs.tl, h.tl, SolarPVGen(Runs,h):0:5, SolarPVCurt(Runs,h):0:5, WindGen(Runs,h):0:5, WindCurt(Runs,h):0:5, GenGasCC(Runs,h):0:5 /);
Putclose ;


FILE csvVRE Report File /OutputSelectedVRE.csv/;
PUT csvVRE
put_utility 'ren' / 'OutputSelectedVRE_SDOM_%FNAME%_Nuclear_' AlphaNuclear:0:0 '_Target_' GenMix_Target:00 '_.csv';
csvVRE.pc = 5;
PUT csvVRE;

PUT 'Scenario', 'VRE unit ID', 'Technology', 'Selection ', 'latitude', 'longitude','Capacity (MW)'  /;
loop ((Runs,k),
     PUT Runs.tl, k.tl, 'Solar PV', SelectedSolarPV(Runs,k):0:5,CapSolar(k,'latitude'):0:5,CapSolar(k,'longitude'):0:5, CapSolar(k,'capacity'):0:5 /);

loop ((Runs,w),
     PUT Runs.tl, w.tl, 'Wind', SelectedWind(Runs,w):0:5,CapWind(w,'latitude'):0:5,CapWind(w,'longitude'):0:5, CapWind(w,'capacity'):0:5 /);
Putclose ;


