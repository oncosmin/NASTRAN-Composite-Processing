import sqlite3
from sr_extract_stress import stress_to_database
from sr_extract_sr import sr_to_database
from sr_extract_vm import vm_stress_to_database
from sr_extract_solid import solid_stress_to_database
from patran_input import process_input
import time
from xlsxwriter.workbook import Workbook
from math import sqrt

# Creare fisier excel pentru scrierea rezultatelor
workbook = Workbook('ResultsSR.xlsx')
worksheet = workbook.add_worksheet('Data_Results_SR')
worksheet2 = workbook.add_worksheet('Summary_SR_MOS')
worksheet3 = workbook.add_worksheet('Data_Results_HC')
worksheet4 = workbook.add_worksheet('Summary_HC_MOS')
worksheet5 = workbook.add_worksheet('Data_Results_VM')
worksheet6 = workbook.add_worksheet('Summary_VM')

# Creare baza de date pentru stocarea datelor 
conn=sqlite3.connect('ResultsData.db')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()
c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")

def nrCazuri():
    c.execute('SELECT COUNT(DISTINCT subcase) FROM ElmStrengthRatio')
    nrCaz=c.fetchone()
    return nrCaz

def create_table_sr(group_name,index):
    '''
    Function to create table with min(SR) values for specific groups and all cases
    INPUT: Group Name - from GroupOutput.txt as STR
           FOSu SR - factor of saftey inputed by user for MOS calculation as FLOAT
           Index - subcase number as INTEGER
    OUTPUT: Table ElmSR_MOS in ResultsData.db
    '''
    #Creat table pentru stocat informatiile min(SR)
    c.execute('CREATE TABLE IF NOT EXISTS ElmSR_MOS (eid INTEGER, pid INTEGER, SR_min REAL, Subcase INTEGER, FOS_SR REAL, MOS REAL)')
    
    statement='SELECT eid,pid,min(sr),subcase\
               FROM ElmStrengthRatio\
               WHERE eid IN (SELECT eid FROM '+group_name+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)\
               AND subcase = ?'
    #selecteaza randul cu min(SR) pentru grupul de elemente  
    c.execute(statement,(index,))
    data=c.fetchall()
    c.execute('SELECT fos_sr FROM {}'.format(group_name))
    fosuSR=c.fetchone()
    for values in data:
        if values[2]==None:
            break
        else:            
            statement2='INSERT OR REPLACE INTO ElmSR_MOS VALUES(?,?,?,?,?,?)'
            c.execute(statement2,values+fosuSR+(values[2]/fosuSR[0]-1,))
            conn.commit()

def write_sr(group_name,rows,column,index_case):
    '''
    Function to write from database table ElmSR_MOS to Excel File
    INPUT: group_name - Group Name from GroupOutput.txt as STRING
           rows - row index to print summary results, max value equal to max number of groups
           column - column index for positioning when writing results for all cases (+6 increment)
           index_case - index of the case analyzed, used only for printing results based on nr of cases
                        starts from 1, INTEGER
    OUTPUT: Excel file with 2 worksheets, Data_Results_SR for all min(SR) and MOS based on number of
            subcases and groups. Summary_SR represents a summary of the min(SR) and coresponding MOS
            for each group of elements, disregarding the subcase number
    '''
    
    statement='SELECT eid,pid,SR_min,Subcase,FOS_SR,MOS\
               FROM ElmSR_MOS\
               WHERE eid IN (SELECT eid FROM '+group_name+')\
               AND Subcase = ?'
    
    #selecteaza randul cu min(SR) pentru grupul de elemente
    c.execute(statement,(index_case,))
    data=c.fetchall()

    #scrie nume grup pe prima linie de excel, row=0
    worksheet.write(0,column,group_name)
    # scriere header pe a doua linie, row=1, plus increment la coloana
    header=['EID','PID','SR','Subcase','FOS SR','MOS SR']
    for n,m in enumerate(header):
        worksheet.write(1,n+column,m)

    #scrie in worksheetul de calcule SR, valorile minime pentru SR pe group   
    for i in data:
        for col,val in enumerate(i):
            if val==None:
                continue
            else:
                worksheet.write(index_case+1, col+column, val)

    # Selectare elemente pentru scrierea summary
    statement2='SELECT eid,pid,min(SR_min),Subcase,FOS_SR,MOS\
               FROM ElmSR_MOS\
               WHERE eid IN (SELECT eid FROM '+group_name+')'
    
    #selecteaza elem cu min(SR) pentru grupul de elemente pentru printare summary
    c.execute(statement2)
    data2=c.fetchall()

    #scriere header pentru summary
    header=['Group Name','EID','PID','SR','Subcase','FOS SR','MOS SR']
    for n,m in enumerate(header):
        worksheet2.write(0,n,m)

    worksheet2.write(rows,0,group_name)
    for j in data2:
        for col2,val2 in enumerate(j):
            if val2==None:
                continue
            else:
                worksheet2.write(rows, col2+1, val2)    

# Funtion to create Tables in database from GroupOutput.txt
def read_groups():
    file=open('INPUT/GroupOutput.txt','r')
    listaGrupuri=[]
    for line in file:
        linie=line.split(',')
        listaGrupuri.append(linie[0])
        c.execute('DROP TABLE IF EXISTS {} '.format(linie[0]))
        c.execute('CREATE TABLE IF NOT EXISTS {} (eid INTEGER, fos_sr REAL, fos_hc REAL)'.format(linie[0]))
        lista=process_input(str(linie[3]))
        for i in lista:
            statement='INSERT OR REPLACE INTO '+linie[0]+' VALUES(?,?,?)'
            c.execute(statement,(i,linie[1],linie[2]))
            conn.commit()
    #return listaGrupuri[:-1] because we don't want to retrieve ElementeEliminate as a group name
    return listaGrupuri[:-1]


# Funtion to create Tables in database from GroupMetalic.txt
def read_groups_metalic():
    file=open('INPUT/GroupMetalic.txt','r')
    listaGrupuri=[]
    for line in file:
        linie=line.split(',')
        listaGrupuri.append(linie[0])
        c.execute('DROP TABLE IF EXISTS {} '.format(linie[0]))
        c.execute('CREATE TABLE IF NOT EXISTS {} (eid INTEGER,fos_y REAL,fos_u REAL)'.format(linie[0]))
        lista=process_input(str(linie[3]))
        for i in lista:
            statement='INSERT OR REPLACE INTO '+linie[0]+' VALUES(?,?,?)'
            c.execute(statement,(i,linie[1],linie[2]))
            conn.commit()
    #return listaGrupuri[:-1] because we don't want to retrieve ElementeEliminate as a group name
    return listaGrupuri[:-1]




# Function to create table with HC properties 
def read_hc_props():
    '''
    Function to create HCprops table from user input file GroupHCprop.txt
    where user specifies property name, HC ply number, allowables (FsL and FsW)
    and the elements in the respective properties.
    INPUT: GroupHCprop.txt file created by user, must be in the same directory
    OUTPUT: table HCprops in database
    '''
    file=open('INPUT/GroupHCprop.txt','r')
    c.execute('DROP TABLE IF EXISTS HCprops') 
    for line in file:
        if line!='\n':
            linie=line.split(',')
            c.execute('CREATE TABLE IF NOT EXISTS HCprops (eid INTEGER,pid INTEGER,FsL REAL,FsW REAL)')
            listaElm=process_input(str(linie[4]))
            for i in listaElm:
                statement='INSERT OR REPLACE INTO HCprops VALUES(?,?,?,?)'
                c.execute(statement,(i,linie[1],linie[2],linie[3]))
                conn.commit()
        else:
            continue

def read_metal_props():
    '''
    Function to create MetalProps table from user input file MetalicProperties.txt
    where user specifies Material Name, allowables Sigma Yield, Sigma Ultimate,
    and the elements in the respective properties.
    INPUT: MetalicProperties.txt file created by user, must be in the same directory
    OUTPUT: table MetalicProps in database
    '''
    file=open('INPUT/MetalicProperties.txt','r')
    c.execute('DROP TABLE IF EXISTS MetalicProps') 
    for line in file:
        if line!='\n':
            linie=line.split(',')
            c.execute('CREATE TABLE IF NOT EXISTS MetalicProps (eid INTEGER,material TEXT,sigY REAL,sigU REAL)')
            listaElm=process_input(str(linie[3]))
            for i in listaElm:
                statement='INSERT OR REPLACE INTO MetalicProps VALUES(?,?,?,?)'
                c.execute(statement,(i,linie[0],linie[1],linie[2]))
                conn.commit()
        else:
            continue

# Function to process stress data and calculate HC MOS
def create_hc_table(case):
    '''
    Function to create HC_mos and HC_stress table by joining results from ElmStress table
    and HCprops tabel
    INPUT: fos_hc - parameter for calculating MOS, FLOAT number
           case - index for case number
    OUTPUT: write in Data_Results_HC worksheet, worksheet3
    '''
    #create table for all elements from HC with allowables and ply identification
    c.execute('CREATE TABLE IF NOT EXISTS HC_stress (eid INTEGER, pid INTEGER, shearXZ REAL,\
               shearYZ REAL, FsL REAL, FsW REAL, Subcase INTEGER)')

    statement = 'SELECT ElmStress.eid, ElmStress.pid, ElmStress.shearXZ, ElmStress.shearYZ,\
                        HCprops.FsL, HCprops.FsW, ElmStress.subcase\
                 FROM ElmStress\
                 INNER JOIN HCprops\
                 ON ElmStress.eid = HCprops.eid\
                 WHERE ElmStress.pid = HCprops.pid\
                 AND ElmStress.subcase = ?'

    c.execute(statement,(case,))
    dataHC = c.fetchall()
    statement2='INSERT OR REPLACE INTO HC_stress VALUES(?,?,?,?,?,?,?)'
    for line in dataHC:
        c.execute(statement2,line)
        conn.commit()

def create_hc_mos(caz,group_name):
    #create table with HC MOS based on calculation from input text allowables
    c.execute('CREATE TABLE IF NOT EXISTS HC_mos (eid INTEGER, pid INTEGER, shearXZ REAL,\
               shearYZ REAL, FsL REAL, FsW REAL, Subcase INTEGER,fos_hc REAL, MOS REAL)')
    
    c.execute('SELECT fos_hc FROM {}'.format(group_name))
    fosuHC=c.fetchone()

    statement3='SELECT * FROM HC_stress\
                WHERE eid IN (SELECT eid FROM '+group_name+')\
                AND Subcase = ?'
    
    c.execute(statement3,(caz,))
    dataHC_mos = c.fetchall()
    statement4='INSERT OR REPLACE INTO HC_mos VALUES(?,?,?,?,?,?,?,?,?)'
    for line2 in dataHC_mos:
        c.execute(statement4,line2+fosuHC+((1/(fosuHC[0]*sqrt((line2[2]/line2[4])**2+(line2[3]/line2[5])**2)))-1,))
        conn.commit()
        
        

# Functie pentru scrierea rezultatelor de la HC MOS pentru toate cazurile, pentru fiecare group de elm
def write_all_hc_mos(nume_group,coloana,index):
    '''
    Function to write all HC data in excel from table HC_mos
    INPUT: nume_group - group name from GroupOutput.txt
           coloana - index for column while printing groups +9 increment
           index - index for case number
    OUTPUT: write in Data_Results_HC worksheet, worksheet3
    '''
    statement3='SELECT eid,pid,shearXZ,shearYZ,FsL,FsW,Subcase,fos_hc,min(MOS)\
               FROM HC_mos\
               WHERE eid IN (SELECT eid FROM '+nume_group+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)\
               AND Subcase = ?'
    #selecteaza randul cu min(MOS pentru HC) pentru grupul de elemente  
    c.execute(statement3,(index,))
    data=c.fetchall()

    #scrie header pentru rezultate
    worksheet3.write(0,coloana,nume_group)
    header=['EID','PID','Shear XZ[Pa]','Shear YZ[Pa]','FsL[Pa]','FsW[Pa]','Subcase','FOS HC','MOS HC']
    for n,m in enumerate(header):
        worksheet3.write(1,n+coloana,m)

    #scrie in worksheetul de resultate, toate datele de min MOS pentru fiecare caz corespunzator grupului  
    for row in data:
        for j, value in enumerate(row):
            if value==None:
                continue
                #worksheet3.write(index, j+coloana, 'None')
            else:
                worksheet3.write(index+1, j+coloana, value)

# Functie pentru scrierea valorilor minime ale MOS pentru HC pentru fiecare Group de elem
def write_min_hc_mos(nume_group,rows):
    statement4='SELECT eid,pid,shearXZ,shearYZ,FsL,FsW,Subcase,fos_hc,min(MOS)\
               FROM HC_mos\
               WHERE eid IN (SELECT eid FROM '+nume_group+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)'
    
    #selecteaza randul cu min(hc) pentru grupul de elemente
    c.execute(statement4)
    data=c.fetchall()

    #scrie Headerul pentru tabelul de rezultate calculate
    header=['Group Name','EID','PID','Shear XZ[Pa]','Shear YZ[Pa]','FsL[Pa]','FsW[Pa]','Subcase','FOS HC','MOS HC']
    for n,m in enumerate(header):
        worksheet4.write(0,n,m)

    #scrie in worksheetul de calcule stress, valorile minime pentru mos HC pe group   
    worksheet4.write(rows,0,nume_group)
    for i in data:
        for col,val in enumerate(i):
            if val==None:
                continue
            else:
                worksheet4.write(rows, col+1, val)


def create_table_vm(index):
    '''
    Function to create table with stress and allowables for metalic parts values for  all vm elements
    INPUT: Index - subcase number as INTEGER
    OUTPUT: Table ElmVM_Stress in ResultsData.db
    '''

    #Creat table pentru stocat informatiile min(SR)
    c.execute('CREATE TABLE IF NOT EXISTS ElmVM_Stress (eid INTEGER, VM_stress REAL, sigY REAL, sigU REAL, layer TEXT, Subcase INTEGER)')
    #Select statement of elment stress and element allowables from MetalicProps group
    statement='SELECT ElmVMstress.eid,ElmVMstress.vm_stress,MetalicProps.sigY,MetalicProps.sigU,ElmVMstress.layer,ElmVMstress.subcase\
               FROM ElmVMstress\
               INNER JOIN MetalicProps\
               ON ElmVMstress.eid = MetalicProps.eid\
               WHERE ElmVMstress.subcase = ?'
    
    #selecteaza randul cu min(SR) pentru grupul de elemente  
    c.execute(statement,(index,))
    data=c.fetchall()
    for values in data:            
        statement2='INSERT OR REPLACE INTO ElmVM_STRESS VALUES(?,?,?,?,?,?)'
        c.execute(statement2,values)
        conn.commit()


def create_mos_vm(group_name,index):   
    c.execute('CREATE TABLE IF NOT EXISTS ElmVM_MOS (eid INTEGER, VM_stress REAL, sigY REAL, sigU REAL, layer TEXT, Subcase INTEGER,\
                fos_y REAL, fos_u REAL, MOSy REAL, MOSu REAL)')

    c.execute('SELECT fos_y FROM {}'.format(group_name))
    fosY=c.fetchone()
    c.execute('SELECT fos_u FROM {}'.format(group_name))
    fosU=c.fetchone()

    statement='SELECT * FROM ElmVM_Stress\
               WHERE eid IN (SELECT eid FROM '+group_name+')\
               AND Subcase = ?'

    c.execute(statement,(index,))
    dataVM_stress = c.fetchall()
    statement='INSERT OR REPLACE INTO ElmVM_MOS VALUES(?,?,?,?,?,?,?,?,?,?)'
    for values in dataVM_stress:
        if values[1]==None:
            continue
        else:
        #VM stress is given in Pa and we divided by 10^6 to transform it into MPa, for reading purposes
            c.execute(statement,(values[0],values[1]/1000000,values[2],values[3],values[4],values[5],\
                                 fosY[0],fosU[0],((values[2]*1000000)/(fosY[0]*values[1]))-1,\
                                 ((values[3]*1000000)/(fosU[0]*values[1]))-1))
            conn.commit()



# Functie pentru scrierea rezultatelor de la VonMises MOS pentru toate cazurile, pentru fiecare group de elm din MetalicGroups
def write_all_vm_mos(nume_group,coloana,index):
    '''
    Function to write all VM MOS data in excel from table ElmVM_MOS based on subcase number
    INPUT: nume_group - group name from GroupOutput.txt
           coloana - index for column while printing groups +9 increment
           index - index for case number
    OUTPUT: write in Data_Results_HC worksheet, worksheet3
    '''
    statement3='SELECT eid,VM_stress,sigY,sigU,layer,Subcase,fos_y,fos_u,MOSy,min(MOSu)\
               FROM ElmVM_MOS\
               WHERE eid IN (SELECT eid FROM '+nume_group+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate2)\
               AND subcase = ?'
    #selecteaza randul cu min(MOS pentru HC) pentru grupul de elemente  
    c.execute(statement3,(index,))
    data=c.fetchall()

    #scrie header pentru rezultate
    worksheet5.write(0,coloana,nume_group)
    header=['EID','Von Mises Stress[MPa]','SigY[MPa]','SigU[MPa]','Layer','Subcase','FOSy','FOSu','MOSy','MOSu']
    for n,m in enumerate(header):
        worksheet5.write(1,n+coloana,m)

    #scrie in worksheetul de resultate, toate datele de min MOS pentru fiecare caz corespunzator grupului  
    for row in data:
        for j, value in enumerate(row):
            if value==None:
                continue
            else:
                worksheet5.write(index+1, j+coloana, value)


# Functie pentru scrierea valorilor minime ale MOS pentru HC pentru fiecare Group de elem
def write_min_vm_mos(nume_group,rows):
    statement4='SELECT eid,VM_stress,sigY,sigU,layer,Subcase,fos_y,fos_u,MOSy,min(MOSu)\
               FROM ElmVM_MOS\
               WHERE eid IN (SELECT eid FROM '+nume_group+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate2)'
    
    #selecteaza randul cu min(hc) pentru grupul de elemente
    c.execute(statement4)
    data=c.fetchall()

    #scrie Headerul pentru tabelul de rezultate calculate
    header=['Part Name','EID','Von Mises Stress[MPa]','SigY[MPa]','SigU[MPa]','Layer','Subcase','FOSy','FOSu','MOSy','MOSu']
    for n,m in enumerate(header):
        worksheet6.write(0,n,m)

    #scrie in worksheetul de calcule stress, valorile minime pentru mos HC pe group   
    worksheet6.write(rows,0,nume_group)
    for i in data:
        for col,val in enumerate(i):
            if val==None:
                continue
            else:
                worksheet6.write(rows, col+1, val)


def main():
    start_time = time.time()
    intro = '''
 
                                                              
              @@@@@@@     @@@@@@@@@@            @@@@@@      @    
           @@@@@@@@@@@    @@@@@@@@@@@@        @@@@@@      @@     
          @@@@@           @@@@     @@@@     @@@@@@       @@       
          @@@@@           @@@@     @@@@    @@@@@       @@@    @@
           @@@@@@@        @@@@    @@@@    @@@@@      @@@@    @@@@
             @@@@@@@@     @@@@@@@@@@@     @@@@@@    @@@@     @@@@@ 
                 @@@@@@   @@@@   @@@@      @@@@@  @@@@@@    @@@@@  
                 @@@@@@   @@@@    @@@@      @@@@@         @@@@@@   
          @@@@@@@@@@@@    @@@@     @@@@      @@@@@@@@@@@@@@@@@@    
          @@@@@@@@@@@     @@@@      @@@@       @@@@@@@@@@@@@@      
                                                  @@@@@@@@
                                                  
    ==================================================================
                 Space Rider Cold Structure Data Analysis
    ==================================================================
                            - Version 2.13 -
	
	Added functions:
	- Read .f06 for strength ratio
	- Read .pch for all stress (QUAD, TRIA, HEXA and TETRA)
	- Insert all result data in database ResultsData.db
	- Use GroupsOutput.txt to define composite part groups
	- Use GroupHCproperties.txt as input for HC properties
	- Use GroupMetalic.txt as input for metalic part groups
	- Use MetalicProperties.txt as input for metalic properties
	- Implemented FOS into input text, no user input requested

        Workflow:
        - Insert name of .f06 file with extension included
        - Insert name of .pch file with extension included
        - Create database with stress and strength ratio values
        - Process data, calculate MOS
        - Output results into excel file 
	
    '''
    print (intro)
        
    input_fisier=input('Type the f06 file name:')
    pch_fisier=input('Type the pch file name:')


    '''
    Create Database from f06 input
    '''
    analysis = input('Create database from f06 file?(1-yes, 2-no) input number: ') 

    if analysis=='1':

        # Daca vrei sa separi f06 in stress si sr, scoate comentarile de mai jos .
        #clean_f06(input_fisier)
        #print("--- %s seconds to .f06 file split ---" % (time.time() - start_time))


        # Adauga in paranteze input_fisier[:-4]+'_stress.f06' daca ai spart in fisiere separate
        sr_to_database(input_fisier)
        print("--- %s seconds to SR extraction ---" % (time.time() - start_time))

        #Adauga in paranteze input_fisier[:-4]+'_stress.f06' daca ai spart in fisiere separate
        stress_to_database(pch_fisier)
        print("--- %s seconds to HC Stress from quads extraction ---" % (time.time() - start_time))

        # Adauga in paranteze input_fisier[:-4]+'_stress.f06' daca ai spart in fisiere separate
        solid_stress_to_database(pch_fisier)
        print("--- %s seconds to HC Stress from solid extraction ---" % (time.time() - start_time))
        
        #introducerea rezultatelor pentru stress VonMises ale elm din material metalic
        vm_stress_to_database(pch_fisier)
        print("--- %s seconds to Von Mises Stress extraction ---" % (time.time() - start_time))
        
    else:
        pass


    '''---------------------------------------------------------------------
    Create tables with group names and specific EID, based on GroupOuput.txt
    and GroupMetalic.txt
    - if tables exist, they will be deleted and written again
    ----------------------------------------------------------------------'''
    groupNames=read_groups()
    groupNamesMetal=read_groups_metalic()
    print("--- %s seconds to create tables from group names ---" % (time.time() - start_time))


    '''-----------------------------------------------------------------------------------------
    Create Table based on HC properties with plyID, FsL, FsW and eid for every pcomp elem with HC
    ------------------------------------------------------------------------------------------'''
    read_hc_props()
    print("--- %s seconds to create tables with HC properties ---" % (time.time() - start_time))


    '''-----------------------------------------------------------------------------------------
    Create Table based on Metalic properties for allwoables based on eid
    ------------------------------------------------------------------------------------------'''
    read_metal_props()
    print("--- %s seconds to create tables with Metalic properties ---" % (time.time() - start_time))



    # Number of cases based on disctinct subcases present in ElmStrengthRatio Table
    nr_cazuri=nrCazuri()
    print ('Number of cases',nr_cazuri[0])




    '''-----------------------------------------------------
    Process SR data and create table with results plus MOS
    -----------------------------------------------------'''
    condition = input('Do you want to process SR data and calculate MOS? 1-Yes, 2-No: ')


    if condition == '1':
        c.execute('DROP INDEX IF EXISTS index_sr')
        c.execute('CREATE INDEX index_sr ON ElmStrengthRatio(eid,subcase)')
        #Create table of results for min(SR) and MOS based on groups and subcases
        c.execute('DROP TABLE IF EXISTS ElmSR_MOS')
        for group in groupNames:
            for i in range(nr_cazuri[0]):
                create_table_sr(group,i+1)
        print("--- %s seconds to read and process SR data ---" % (time.time() - start_time))
    elif condition == '2':
        print('NO SR file read and processed!')


    '''-------------------------------------------------------------------------
    Process Stress data for HC MOS calculation 
    -------------------------------------------------------------------------'''
    condition2 = input('Do you want to process Stress data for HC MOS calculation  ? 1-Yes, 2-No: ')
    
    if condition2 == '1':
        
        c.execute('DROP INDEX IF EXISTS index_stress')
        c.execute('CREATE INDEX index_stress ON ElmStress(eid,pid,subcase)')
        #fosu_hc = input('Insert FOS for HoneyComb MOS calculation = ')
        c.execute('DROP TABLE IF EXISTS HC_stress')
        for j in range(nr_cazuri[0]):
            # cazul de input trebuie sa porneasca de la 1 pentru statement de SELECT
            create_hc_table(j+1)
        print("--- %s seconds to create HC stress table in database ---" % (time.time() - start_time))

        c.execute('DROP INDEX IF EXISTS index_hc')
        c.execute('CREATE INDEX index_hc ON HC_stress(eid,Subcase)')
        c.execute('DROP TABLE IF EXISTS HC_mos')
        for groups in groupNames:
            for k in range(nr_cazuri[0]):
                # cazul de input trebuie sa porneasca de la 1 pentru statement de SELECT
                create_hc_mos(k+1,groups)
        print("--- %s seconds to create HC MOS table in database ---" % (time.time() - start_time))

    elif condition2 == '2':
        print('NO HC values processed!')
    
    '''-----------------------------------------------------------
    Process Von Mises data and create table with results and MOS
    -----------------------------------------------------------'''
    condition4 = input('Do you want to process Von Mises stress data and calculate MOS? 1-Yes, 2-No:')

    if condition4 == '1':
        #fosy_vm = input('Insert FOSy for VonMises MOSy calculation = ')
        #fosu_vm = input('Insert FOSu for VonMises MOSu calculation = ')
        c.execute('DROP INDEX IF EXISTS vm_stress')
        c.execute('CREATE INDEX vm_stress ON ElmVMstress(eid,subcase)')
        c.execute('DROP TABLE IF EXISTS ElmVM_Stress')
        for m in range(nr_cazuri[0]):
            create_table_vm(m+1)
        print("--- %s seconds to read and process VM stress data ---" % (time.time() - start_time))

        c.execute('DROP INDEX IF EXISTS vm_stress')
        c.execute('CREATE INDEX vm_stress ON ElmVM_Stress(eid,Subcase)')
        c.execute('DROP TABLE IF EXISTS ElmVM_MOS')
        for groupb in groupNamesMetal:
            for n in range(nr_cazuri[0]):
                create_mos_vm(groupb,n+1)
        print("--- %s seconds to read and process VM MOS data ---" % (time.time() - start_time))
    elif condition4 == '2':
        print('NO VM stress data  read and processed!')


    '''-------------------------------------------------------------------------
    Write SR and Stress data results to excel 
    -------------------------------------------------------------------------'''  
    condition3 = input('Do you want to write MOS results data to excel? 1-Yes, 2-No: ')
    if condition3 == '1':
        rows=1
        rows_vm=1
        col_sr=0
        col_stress=0
        col_vm=0
        #Index for MOS tables for faster query and writing
        c.execute('DROP INDEX IF EXISTS sr_mos')
        c.execute('CREATE INDEX sr_mos ON ElmSR_MOS(eid,Subcase)')
        c.execute('DROP INDEX IF EXISTS idx_hc_mos')
        c.execute('CREATE INDEX idx_hc_mos ON HC_mos(eid,Subcase)')
        c.execute('DROP INDEX IF EXISTS vm_mos')
        c.execute('CREATE INDEX vm_mos ON ElmVM_MOS(eid,Subcase)')        
        # Write results from ElmSR_MOS table in db to excel
        for group in groupNames:
            for i in range(nr_cazuri[0]):
                write_sr(group,rows,col_sr,i+1)
                write_all_hc_mos(group,col_stress,i+1)
            write_min_hc_mos(group,rows)
            col_sr+=7
            col_stress+=10
            rows+=1
        for groupM in groupNamesMetal:
            for j in range(nr_cazuri[0]):
                write_all_vm_mos(groupM,col_vm,j+1)
            write_min_vm_mos(groupM,rows_vm)
            col_vm+=11
            rows_vm+=1
        workbook.close()
        print("--- %s seconds to write excel file with SR and HC MOS results ---" % (time.time() - start_time))
    elif condition3 == '2':
        print('NO excel file printed!')


    '''-------------------------------------------------------------------------
    Copy tables from excel to word 
    -------------------------------------------------------------------------'''  
    #word=input('Do you want to write word document with results in table form? 1-yes, 2-no: ')
    
    c.close()
    conn.close()
    end = time.time()
    print ('Execution Time:')
    print (str(end - start_time)+' seconds') 
    input('Press Enter to close.')


main()
    
