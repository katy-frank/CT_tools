#! /bin/env python
# -*- coding: utf-8 -*-
"""
Module is for reading and writing data in the Morphosource Batch Import Worksheet format.
"""
from builtins import range
import pandas as pd
import copy

#read in blank worksheet
def read_mbs_worksheet(Rows):
    WorksheetRaw = pd.read_excel('MorphoSourceBatchImportWorksheet.xlsx',header = None)
    WorksheetBlank = pd.DataFrame(index=list(range(0, Rows[-1]+1)), columns=WorksheetRaw.columns)
    WorksheetBlank.iloc[0:3,:] = WorksheetRaw.iloc[0:3,:]
    return WorksheetBlank
#%% Fill in inital description column, as well as media description column. Same text.
#0th column is "Description", should read: 'microCT volume and derivatives of ###'
#Worksheet is the output of read_mbs_worksheet() or some partially-filled derivative
#SpecimensRaw is an object, a column of specimen numbers (ex: UF 12345, UF 23456): 
def fill_description(Worksheet, SpecimensRaw):
    Description = 'microCT volume and derivatives'
    Description2 = copy.deepcopy(SpecimensRaw)
    for i in range(len(SpecimensRaw)):
        Description2[i] = Description + f' of {SpecimensRaw[i]}'
    Worksheet.iloc[3:,0] = Description2.values
    Worksheet.iloc[3:,46] = Description #46 = Media group description
    return Worksheet
#%% Fill in IDs, knowing that the occurrence ID trumps all.
#Worksheet is the output of read_mbs_worksheet() or some partially-filled derivative
#SpecimenDf is a dataframe derived from code to pull Occurrence IDs
def fill_ids(Worksheet, SpecimenDf):
    Worksheet.iloc[3:,2] = SpecimenDf.iloc[:,3].values #2= OccurrenceID
    Worksheet.iloc[3:,3] = SpecimenDf.iloc[:,0].values #3= Institution Code
    Worksheet.iloc[3:,4] = SpecimenDf.iloc[:,1].values #4= Collections Code
    Worksheet.iloc[3:,5] = SpecimenDf.iloc[:,2].values #5= Specimen Number
    Worksheet.iloc[3:,27] = SpecimenDf.iloc[:,4].values #27= Genus
    Worksheet.iloc[3:,28] = SpecimenDf.iloc[:,5].values #28= Species
    return Worksheet
#%% Fill in Genus species taxonomy in the absence of occurrence ID.
def fill_taxonomy(Worksheet, Genus, Species):
    Worksheet.iloc[3:,27] = Genus.values #27= Genus
    Worksheet.iloc[3:,28] = Species.values #28= Species
    return Worksheet

#%% Fill in download permissions
def fill_downloads(Worksheet, DownloadPolicy):
    Worksheet.iloc[3:,47] = DownloadPolicy #47 Publication Status
    return Worksheet    
#%% Fill in element
def fill_element(Worksheet, ElementText, SideText):
    Worksheet.iloc[3:,48] = ElementText #48 Element
    if ElementText is not None:
        Worksheet.iloc[3:,49] = SideText #49 Side [of element]
    return Worksheet
#%% Fill in grant, copyright info
def fill_permissions(Worksheet, GrantText, Provider, CopyPerm,MediaPol):
    Worksheet.iloc[3:,51] = GrantText #51= Funding information
    Worksheet.iloc[3:,52] = Provider
    Worksheet.iloc[3:,54] = f", the collection of which was funded by {GrantText}."
    Worksheet.iloc[3:,55] = True #55= Is it copyrighted?
    Worksheet.iloc[3:,56] = CopyPerm #56= Who gave permission?
    Worksheet.iloc[3:,57] = MediaPol #57= Media license
    Worksheet.iloc[3:,58] = Provider #58= Copyright holder
    return Worksheet
#%% Scan settings
def fill_ctmetadata(Worksheet, CT_metadata_dataframe):
    Worksheet.iloc[3:,59] = CT_metadata_dataframe['X_voxel_size_mm'].values
    Worksheet.iloc[3:,60] = CT_metadata_dataframe['Y_voxel_size_mm'].values
    Worksheet.iloc[3:,61] = CT_metadata_dataframe['Z_voxel_size_mm'].values
    Worksheet.iloc[3:,62] = CT_metadata_dataframe['voltage_kv'].values
    Worksheet.iloc[3:,63] = CT_metadata_dataframe['amperage_ua'].values
    Worksheet.iloc[3:,64] = CT_metadata_dataframe['watts'].values
    Worksheet.iloc[3:,65] = CT_metadata_dataframe['exposure_time'].values
    Worksheet.iloc[3:,66] = CT_metadata_dataframe['filter'].values
    Worksheet.iloc[3:,67] = CT_metadata_dataframe['projections'].values
    Worksheet.iloc[3:,68] = CT_metadata_dataframe['frame_averaging'].values
    Worksheet.iloc[3:,69] = CT_metadata_dataframe['wedge'].values
    Worksheet.iloc[3:,70] = CT_metadata_dataframe['shade_calib'].values
    Worksheet.iloc[3:,71] = CT_metadata_dataframe['flux_calib'].values
    Worksheet.iloc[3:,72] = CT_metadata_dataframe['geom_calib'].values
    Worksheet.iloc[3:,73] = CT_metadata_dataframe['calib_descrip'].values
    Worksheet.iloc[3:,74] = CT_metadata_dataframe['technician'].values
    return Worksheet
#59-74: scan settings
#%% first media object: zipped tiff stack
def fill_zip(Worksheet,FileNames,Title):
    Worksheet.iloc[3:,75] = FileNames #75= file name
    #given that these are zipped tiff stacks or similar, no preview file
    Worksheet.iloc[3:,76] = None #76= preview file name
    Worksheet.iloc[3:,77] = Title #77 = file title [tiff stack, mesh, etc.]
    Worksheet.iloc[3:,81] = "raw" #81= file type [raw or derivative]
    return Worksheet
#%% additional media objects: meshes
def fill_meshes(Worksheet,MeshFileObject):
    File = [[] for _ in range(len(MeshFileObject[0]))] 
    Preview = [[] for _ in range(len(MeshFileObject[0]))]
    Title = [[] for _ in range(len(MeshFileObject[0]))]
    Type = [[] for _ in range(len(MeshFileObject[0]))]
    for level1 in MeshFileObject:
        for level2 in range(len(MeshFileObject[0])):
            File[level2].extend(level1[level2][0])
            Preview[level2].extend(level1[level2][1])
            Title[level2].extend(level1[level2][2])
            Type[level2].extend(level1[level2][3])
    #84-92: second media object, after tiff stack
    #for loop allows iterative filling for infinite number of surfaces
    for i in range(len(MeshFileObject[0])):
        Worksheet.iloc[3:,(84+(9*i))] = File[i] #84= file name #2
        Worksheet.iloc[3:,(85+(9*i))] = Preview[i] #85= preview file name #2
        Worksheet.iloc[3:,(86+(9*i))] = Title[i] #86 = file title [tiff stack, mesh, etc.]
        Worksheet.iloc[3:,(90+(9*i))] = Type[i]
    return Worksheet


#%% additional media objects
#Worksheet.iloc[1,93:] #shows column names

#MeshFileObject = MeshData
