# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 09:52:49 2018

@author: Omar J. Guerra F.
"""
#from urllib import urlretrieve
import pandas as pd

#dir = '//Nrelqnap02/PLEXOS/Projects/EPRI_storage/OneNodeOptimization/'
dir = '//nrelnas01/PLEXOS/Projects/EPRI_storage/OneNodeOptimization/'



#Solalr cases
iso = ['CAISO', 'ERCOT', 'ISONE', 'MISO', 'NYISO', 'PJM', 'SPP']
nuclear = ['0', '1']
target = ['0.00', '0.75', '0.80', '0.85', '0.90', '0.95', '1.00']

SummaryData = pd.DataFrame()
StorageChargePowerCapData = pd.DataFrame()
StorageDischargePowerCapData = pd.DataFrame()
StorageEnergyCapData = pd.DataFrame()
StorageDurationData = pd.DataFrame()
SolarGenData  = pd.DataFrame()
SolarCurtData = pd.DataFrame()
WindGenData   = pd.DataFrame()
WindCurtData  = pd.DataFrame()
GasCCGenData  = pd.DataFrame()
SGCC2SData  =  pd.DataFrame()
LiIonChargingData = pd.DataFrame()
LiIonDischargingData = pd.DataFrame() 
LiIonSOCData = pd.DataFrame() 
CAESChargingData = pd.DataFrame()
CAESDischargingData = pd.DataFrame() 
CAESSOCData = pd.DataFrame()
PHSChargingData = pd.DataFrame()
PHSDischargingData = pd.DataFrame() 
PHSSOCData = pd.DataFrame()
H2ChargingData = pd.DataFrame()
H2DischargingData = pd.DataFrame() 
H2SOCData = pd.DataFrame()
Load_genmix_data = pd.DataFrame()


for j in iso:
    for i in nuclear:
        for k in target:
            case = j + ' Nuclear ' + i + ' Target ' + k
            print(case)
            summaryfile = dir + j +'/OutputUpdatedSummary_SDOM_' + j + '_Nuclear_' + i + '_Target_' + k + '_.csv'
            Summary = pd.read_csv(summaryfile, nrows=12)
            Summary.Optimal = Summary.Optimal[Summary.Optimal.str.strip() != ''].fillna(method='bfill')
            Summary.Optimal = Summary.Optimal.fillna(method='bfill')
            Summary = Summary[Summary['Run'] != '1'].set_index('Run')
            Summary = Summary.rename(columns={'Optimal': case})
            SummaryData = pd.concat([SummaryData, Summary], axis=1)

            StorageChargePowerCap = pd.read_csv(summaryfile, skiprows=13, nrows=4)
            StorageChargePowerCap = StorageChargePowerCap.set_index('Total charge power capacity of storage units j (MW)')
            StorageChargePowerCap = StorageChargePowerCap.rename(columns = {list(StorageChargePowerCap)[0]: case})
            StorageChargePowerCapData = pd.concat([StorageChargePowerCapData, StorageChargePowerCap], axis=1)

            StorageDischargePowerCap = pd.read_csv(summaryfile, skiprows=18, nrows=4)
            StorageDischargePowerCap = StorageDischargePowerCap.set_index('Total discharge power capacity of storage units j (MW)')
            StorageDischargePowerCap = StorageDischargePowerCap.rename(columns = {list(StorageDischargePowerCap)[0]: case})
            StorageDischargePowerCapData = pd.concat([StorageDischargePowerCapData, StorageDischargePowerCap], axis=1)   

            StorageEnergyCap = pd.read_csv(summaryfile, skiprows=23, nrows=4)
            StorageEnergyCap = StorageEnergyCap.set_index('Total energy capacity of storage units j (MWh)')
            StorageEnergyCap = StorageEnergyCap.rename(columns = {list(StorageEnergyCap)[0]: case})
            StorageEnergyCapData = pd.concat([StorageEnergyCapData, StorageEnergyCap], axis=1)
            
            StorageDuration = pd.read_csv(summaryfile, skiprows=28, nrows=4)
            StorageDuration = StorageDuration.set_index('Discharge duration for storage technology j (h)')
            StorageDuration = StorageDuration.rename(columns = {list(StorageDuration)[0]: case})
            StorageDurationData = pd.concat([StorageDurationData, StorageDuration], axis=1)   

            Genfile = dir + j +'/OutputUpdatedGeneration_SDOM_' + j + '_Nuclear_' + i + '_Target_' + k + '_.csv'
            Gen = pd.read_csv(Genfile )
            Gen = Gen.drop(['Scenario'], 1).set_index('Hour')
            
            SolarGen  = pd.DataFrame(Gen['Solar PV Generation (MW)'])
            SolarGen  = SolarGen.rename(columns = {list(SolarGen)[0]: case})
            SolarGenData = pd.concat([SolarGenData, SolarGen], axis=1) 
            
            SolarCurt = pd.DataFrame(Gen['Solar PV Curtailment (MW)'])
            SolarCurt = SolarCurt.rename(columns = {list(SolarCurt)[0]: case})
            SolarCurtData = pd.concat([SolarCurtData, SolarCurt], axis=1)

            
            WindGen   = pd.DataFrame(Gen['Wind Generation (MW)'])
            WindGen   = WindGen.rename(columns = {list(WindGen)[0]: case})
            WindGenData = pd.concat([WindGenData, WindGen], axis=1) 
            
            WindCurt  = pd.DataFrame(Gen['Wind Curtailment (MW)'])
            WindCurt  = WindCurt.rename(columns = {list(WindCurt)[0]: case})
            WindCurtData = pd.concat([WindCurtData, WindCurt], axis=1) 
            
            GasCCGen  = pd.DataFrame(Gen['Gas CC Generation (MW)'])
            GasCCGen  = GasCCGen.rename(columns = {list(GasCCGen )[0]: case})
            GasCCGenData = pd.concat([GasCCGenData, GasCCGen], axis=1) 
            
            SGCC2S  =  pd.DataFrame(Gen['Power from Storage and Gas CC to Storage (MW)'])
            SGCC2S  =  SGCC2S.rename(columns = {list(SGCC2S)[0]: case})
            SGCC2SData = pd.concat([SGCC2SData, SGCC2S], axis=1) 
            
            Storagefile = dir + j +'/OutputUpdatedStorage_SDOM_' + j + '_Nuclear_' + i + '_Target_' + k + '_.csv'
            Storage = pd.read_csv(Storagefile)
            Storage = Storage.drop(['Scenario'], 1).set_index('Hour')
            StorageLiIon = Storage.loc[Storage['Technology'] == 'Li-Ion']
            StorageCAES = Storage.loc[Storage['Technology'] == 'CAES']
            StoragePHS = Storage.loc[Storage['Technology'] == 'PHS']
            StorageH2 = Storage.loc[Storage['Technology'] == 'H2']
            
            LiIonCharging = pd.DataFrame(StorageLiIon['Charging power (MW)'])
            LiIonCharging = LiIonCharging.rename(columns = {list(LiIonCharging)[0]: case})
            LiIonChargingData = pd.concat([LiIonChargingData, LiIonCharging ], axis=1)

            LiIonDischarging = pd.DataFrame(StorageLiIon['Disharging power (MW)'])
            LiIonDischarging = LiIonDischarging.rename(columns = {list(LiIonDischarging)[0]: case})
            LiIonDischargingData = pd.concat([LiIonDischargingData, LiIonDischarging ], axis=1)
            
            LiIonSOC = pd.DataFrame(StorageLiIon['State of charge (MWh)'])
            LiIonSOC = LiIonSOC.rename(columns = {list(LiIonSOC)[0]: case})
            LiIonSOCData = pd.concat([LiIonSOCData, LiIonSOC ], axis=1)
            
            CAESCharging = pd.DataFrame(StorageCAES['Charging power (MW)'])
            CAESCharging = CAESCharging.rename(columns = {list(CAESCharging)[0]: case})
            CAESChargingData = pd.concat([CAESChargingData, CAESCharging ], axis=1)

            CAESDischarging = pd.DataFrame(StorageCAES['Disharging power (MW)'])
            CAESDischarging = CAESDischarging.rename(columns = {list(CAESDischarging)[0]: case})
            CAESDischargingData = pd.concat([CAESDischargingData, CAESDischarging ], axis=1)
            
            CAESSOC = pd.DataFrame(StorageCAES['State of charge (MWh)'])
            CAESSOC = CAESSOC.rename(columns = {list(CAESSOC)[0]: case})
            CAESSOCData = pd.concat([CAESSOCData, CAESSOC ], axis=1)

            PHSCharging = pd.DataFrame(StoragePHS['Charging power (MW)'])
            PHSCharging = PHSCharging.rename(columns = {list(PHSCharging)[0]: case})
            PHSChargingData = pd.concat([PHSChargingData, PHSCharging ], axis=1)

            PHSDischarging = pd.DataFrame(StoragePHS['Disharging power (MW)'])
            PHSDischarging = PHSDischarging.rename(columns = {list(PHSDischarging)[0]: case})
            PHSDischargingData = pd.concat([PHSDischargingData, PHSDischarging ], axis=1)
            
            PHSSOC = pd.DataFrame(StoragePHS['State of charge (MWh)'])
            PHSSOC = PHSSOC.rename(columns = {list(PHSSOC)[0]: case})
            PHSSOCData = pd.concat([PHSSOCData, PHSSOC ], axis=1)
            
            H2Charging = pd.DataFrame(StorageH2['Charging power (MW)'])
            H2Charging = H2Charging.rename(columns = {list(H2Charging)[0]: case})
            H2ChargingData = pd.concat([H2ChargingData, H2Charging ], axis=1)

            H2Discharging = pd.DataFrame(StorageH2['Disharging power (MW)'])
            H2Discharging = H2Discharging.rename(columns = {list(H2Discharging)[0]: case})
            H2DischargingData = pd.concat([H2DischargingData, H2Discharging ], axis=1)
            
            H2SOC = pd.DataFrame(StorageH2['State of charge (MWh)'])
            H2SOC = H2SOC.rename(columns = {list(H2SOC)[0]: case})
            H2SOCData = pd.concat([H2SOCData, H2SOC ], axis=1)


SummaryGasCCGen = GasCCGenData.sum(axis=0).to_frame().transpose()
SummaryGasCCGen.index = ['Gas CC Generation (MWh)']

SummarySolarCurt = SolarCurtData.sum(axis=0).to_frame().transpose()
SummarySolarCurt.index = ['Solar PV curtailment (MWh)']

SummaryWindCurt  = WindCurtData.sum(axis=0).to_frame().transpose()
SummaryWindCurt.index = ['Wind curtailment (MWh)']

SummaryStorageChargePowerCap = StorageChargePowerCapData.rename(index = lambda x: x+' charge power capacity (MW)')
SummaryStorageDischargePowerCap = StorageDischargePowerCapData.rename(index = lambda x: x+' discharge power capacity (MW)')
SummaryStorageEnergyCap = StorageEnergyCapData.rename(index = lambda x: x+' energy capacity (MWh)')
SummaryStorageDuration = StorageDurationData.rename(index = lambda x: x+' discharge duration (h)')

SummaryLiIonCharging = LiIonChargingData.sum(axis=0).to_frame().transpose()
SummaryLiIonCharging.index = ['Li-Ion total charging power (MWh)']
SummaryCAESCharging = CAESChargingData.sum(axis=0).to_frame().transpose()
SummaryCAESCharging.index = ['CAES total charging power (MWh)']
SummaryPHSCharging = PHSChargingData.sum(axis=0).to_frame().transpose()
SummaryPHSCharging.index = ['PHS total charging power (MWh)']
SummaryH2Charging = H2ChargingData.sum(axis=0).to_frame().transpose()
SummaryH2Charging.index = ['H2 total charging power (MWh)']

SummaryLiIonDischarging = LiIonDischargingData.sum(axis=0).to_frame().transpose()
SummaryLiIonDischarging.index = ['Li-Ion total discharging power (MWh)']
SummaryCAESDischarging = CAESDischargingData.sum(axis=0).to_frame().transpose()
SummaryCAESDischarging.index = ['CAES total discharging power (MWh)']
SummaryPHSDischarging = PHSDischargingData.sum(axis=0).to_frame().transpose()
SummaryPHSDischarging.index = ['PHS total discharging power (MWh)']
SummaryH2Discharging = H2DischargingData.sum(axis=0).to_frame().transpose()
SummaryH2Discharging.index = ['H2 total discharging power (MWh)']



SummaryData = SummaryData.append([SummaryGasCCGen, SummarySolarCurt, SummaryWindCurt,
                                  SummaryStorageChargePowerCap, SummaryStorageDischargePowerCap, SummaryStorageEnergyCap, SummaryStorageDuration,
                                  SummaryLiIonCharging, SummaryCAESCharging, SummaryPHSCharging, SummaryH2Charging,
                                  SummaryLiIonDischarging, SummaryCAESDischarging, SummaryPHSDischarging, SummaryH2Discharging ])

SummaryData.to_csv( dir + 'Summary_Final_Updated' + "/SummaryData.csv",  encoding='utf-8-sig')
StorageChargePowerCapData.to_csv( dir + 'Summary_Final_Updated' + "/StorageChargePowerCapData.csv",  encoding='utf-8-sig')
StorageDischargePowerCapData.to_csv( dir + 'Summary_Final_Updated' + "/StorageDischargePowerCapData.csv",  encoding='utf-8-sig')
StorageEnergyCapData.to_csv( dir + 'Summary_Final_Updated' + "/StorageEnergyCapData.csv",  encoding='utf-8-sig')
StorageDurationData.to_csv( dir + 'Summary_Final_Updated' + "/StorageDurationData.csv",  encoding='utf-8-sig')
SolarGenData.to_csv( dir + 'Summary_Final_Updated' + "/SolarGenData.csv",  encoding='utf-8-sig')
SolarCurtData.to_csv( dir + 'Summary_Final_Updated' + "/SolarCurtData.csv",  encoding='utf-8-sig')
WindGenData.to_csv( dir + 'Summary_Final_Updated' + "/WindGenData.csv",  encoding='utf-8-sig')
WindCurtData.to_csv( dir + 'Summary_Final_Updated' + "/WindCurtData.csv",  encoding='utf-8-sig')
GasCCGenData.to_csv( dir + 'Summary_Final_Updated' + "/GasCCGenData.csv",  encoding='utf-8-sig')
SGCC2SData.to_csv( dir + 'Summary_Final_Updated' + "/SGCC2SData.csv",  encoding='utf-8-sig')
LiIonChargingData.to_csv( dir + 'Summary_Final_Updated' + "/LiIonChargingData.csv",  encoding='utf-8-sig')
LiIonDischargingData.to_csv( dir + 'Summary_Final_Updated' + "/LiIonDischargingData.csv",  encoding='utf-8-sig')
LiIonSOCData.to_csv( dir + 'Summary_Final_Updated' + "/LiIonSOCData.csv",  encoding='utf-8-sig')
CAESChargingData.to_csv( dir + 'Summary_Final_Updated' + "/CAESChargingData.csv",  encoding='utf-8-sig')
CAESDischargingData.to_csv( dir + 'Summary_Final_Updated' + "/CAESDischargingData.csv",  encoding='utf-8-sig')
CAESSOCData.to_csv( dir + 'Summary_Final_Updated' + "/CAESSOCData.csv",  encoding='utf-8-sig')
PHSChargingData.to_csv( dir + 'Summary_Final_Updated' + "/PHSChargingData.csv",  encoding='utf-8-sig')
PHSDischargingData.to_csv( dir + 'Summary_Final_Updated' + "/PHSDischargingData.csv",  encoding='utf-8-sig')
PHSSOCData.to_csv( dir + 'Summary_Final_Updated' + "/PHSSOCData.csv",  encoding='utf-8-sig')
H2ChargingData.to_csv( dir + 'Summary_Final_Updated' + "/H2ChargingData.csv",  encoding='utf-8-sig')
H2DischargingData.to_csv( dir + 'Summary_Final_Updated' + "/H2DischargingData.csv",  encoding='utf-8-sig')
H2SOCData.to_csv( dir + 'Summary_Final_Updated' + "/H2SOCData.csv",  encoding='utf-8-sig')



#Combine all Summary Results
if 1==1:
    Items = [['StorageChargePowerCapData'   ,'Storage Charge Power Capacity'],
             ['StorageDischargePowerCapData','Storage Discharge Power Capacity'],
             ['StorageEnergyCapData'        ,'Storage Energy Capacity'],
             ['StorageDurationData'         ,'Storage Duration']]    
    c1 = 0
    for i1 in Items:  
        Interim1 = eval(i1[0]+'.copy(deep=True)')
        Interim1['Technology']=Interim1.index
        Interim1 = Interim1.melt(id_vars=['Technology'])
        Interim1['Property'] = pd.DataFrame([[i1[1]]], index=Interim1.index)
        if c1==0:
            CombinedData = Interim1.copy(deep=True)
        else:
            CombinedData = CombinedData.append(Interim1,ignore_index=True)
        c1 = c1+1        
    CombinedData[['Region','Delete1','Nuclear','Delete2','Target']] = CombinedData.variable.str.split(" ",expand=True) 
    CombinedData.drop(['Delete1','Delete2','variable'], axis=1, inplace=True)
    CombinedData.to_csv( dir + 'Summary_Final_Updated' + "/CombinedData.csv", index=False)

#Combine all Interval Results
if 1==1:
    Items2 = [['SolarGenData'           ,'Solar'    ,'Generation'],
              ['SolarCurtData'          ,'Solar'    ,'Curtailment'],
              ['WindGenData'            ,'Wind'     ,'Generation'],
              ['WindCurtData'           ,'Wind'     ,'Curtailment'],
              ['GasCCGenData'           ,'Gas CC'   ,'Generation'],
              ['LiIonChargingData'      ,'Li-Ion'   ,'Charging'],
              ['LiIonDischargingData'   ,'Li-Ion'   ,'Discharging'],
              ['LiIonSOCData'           ,'Li-Ion'   ,'SOC'],
              ['CAESChargingData'       ,'CAES'     ,'Charging'],
              ['CAESDischargingData'    ,'CAES'     ,'Discharging'],
              ['CAESSOCData'            ,'CAES'     ,'SOC'],
              ['PHSChargingData'        ,'PHS'      ,'Charging'],
              ['PHSDischargingData'     ,'PHS'      ,'Discharging'],
              ['PHSSOCData'             ,'PHS'      ,'SOC'],
              ['H2ChargingData'         ,'H2'       ,'Charging'],
              ['H2DischargingData'      ,'H2'       ,'Discharging'],
              ['H2SOCData'              ,'H2'       ,'SOC']]    
    c1 = 0
    for i1 in Items2:   
        Interim1 = eval(i1[0]+'.copy(deep=True)')
        Interim1['Interval']=Interim1.index
        Interim1 = Interim1.melt(id_vars=['Interval'])
        Interim1[['Technology', 'Property']] = pd.DataFrame([[i1[1],i1[2]]], index=Interim1.index)
        Interim1[['Region','Delete1','Nuclear','Delete2','Target']] = Interim1.variable.str.split(" ",expand=True) 
        Interim1.drop(['Delete1','Delete2','variable'], axis=1, inplace=True)    
        if c1==0:
            CombinedDataInterval = Load_genmix_data
            CombinedDataInterval = CombinedDataInterval.append(Interim1,sort=False,ignore_index=True)
        else:
            CombinedDataInterval = CombinedDataInterval.append(Interim1,sort=False,ignore_index=True)
        c1 = c1+1
        print(i1[0])
    CombinedDataInterval = CombinedDataInterval.astype({'Nuclear': 'int64', 'Target': 'float64'})
#    CombinedDataInterval.dtypes
    CombinedDataInterval.to_csv( dir + 'Summary_Final_Updated' + "/CombinedDataInterval.csv", index=False)
#    CombinedDataInterval.to_csv("C:/Users/jeichman/Documents/Publications/SPIA FY20 Long duration storage/OneNodeOptimization/CombinedDataInterval.csv",index=False)
     


