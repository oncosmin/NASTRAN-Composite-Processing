import csv
import sqlite3
from sr_extract_stress import stress_to_database
from sr_extract_sr import sr_to_database
from cleanf06 import clean_f06
from patran_input import process_input
import time
from xlsxwriter.workbook import Workbook
from math import sqrt

# Creare fisier excel pentru scrierea rezultatelor
workbook = Workbook('ResultsSR.xlsx')
worksheet = workbook.add_worksheet('Data_Results_SR')
worksheet2 = workbook.add_worksheet('Calculation_SR')
worksheet3 = workbook.add_worksheet('Data_Results_Stress')
worksheet4 = workbook.add_worksheet('Calculation_Stress')

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

def read_sr(group_name,column,index):

    statement='SELECT eid,pid,min(sr),subcase\
               FROM ElmStrengthRatio\
               WHERE eid IN (SELECT eid FROM '+group_name+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)\
               AND subcase = ?'
    #selecteaza randul cu min(SR) pentru grupul de elemente  
    c.execute(statement,(index,))
    data=c.fetchall()
    
    #scrie in worksheetul de resultate, toate datele
    worksheet.write(0,column,group_name)
    for row in data:
        for j, value in enumerate(row):
            if value==None:
                worksheet.write(index, j+column, 'None')
            else:
                worksheet.write(index, j+column, value)

    
def process_sr(group_name,rows,fosuSR):

    statement='SELECT eid,pid,min(sr),subcase\
               FROM ElmStrengthRatio\
               WHERE eid IN (SELECT eid FROM '+group_name+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)'
    
    #selecteaza randul cu min(SR) pentru grupul de elemente
    c.execute(statement)
    data=c.fetchall()

    #scrie Headerul pentru tabelul de rezultate calculate
    header=['Group Name','EID','PID','MOS SR','Subcase']
    for n,m in enumerate(header):
        worksheet2.write(0,n,m)

    #scrie in worksheetul de calcule SR, valorile minime pentru SR pe group   
    worksheet2.write(rows,0,group_name)
    for i in data:
        for col,val in enumerate(i):
            if val==None:
                pass
            else:
                if col==2:
                    worksheet2.write(rows, col+1, val/float(fosuSR)-1)
                else:
                    worksheet2.write(rows, col+1, val)




# Funtion to create Tables in database from GroupOutput.txt
def read_groups():
    file=open('GroupOutput.txt','r')
    listaGrupuri=[]
    for line in file:
        linie=line.split(',')
        listaGrupuri.append(linie[0])
        c.execute('DROP TABLE IF EXISTS {} '.format(linie[0]))
        c.execute('CREATE TABLE IF NOT EXISTS {} (eid INTEGER)'.format(linie[0]))
        lista=process_input(str(linie[1]))
        for i in lista:
            statement='INSERT OR REPLACE INTO '+linie[0]+' VALUES(?)'
            c.execute(statement,(i,))
            conn.commit()
    return listaGrupuri


# Function to create table with HC properties 
def read_hc_props():
    file=open('GroupHCprop.txt','r')
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
    

# Function to process stress data and calculate HC MOS
def create_hc_mos(case,fos_hc):

    c.execute('CREATE TABLE IF NOT EXISTS HC_mos (eid INTEGER, pid INTEGER, shearXZ REAL,\
               shearYZ REAL, FsL REAL, FsW REAL, Subcase INTEGER, MOS REAL)')
    
    statement = 'SELECT ElmStress.eid, ElmStress.pid, ElmStress.shearXZ, ElmStress.shearYZ,\
                        HCprops.FsL, HCprops.FsW, ElmStress.subcase\
                 FROM ElmStress\
                 INNER JOIN HCprops\
                 ON ElmStress.eid = HCprops.eid\
                 WHERE ElmStress.pid = HCprops.pid\
                 AND ElmStress.subcase = ?'

    c.execute(statement,(case,))
    dataHC = c.fetchall()
    statement2='INSERT OR REPLACE INTO HC_mos VALUES(?,?,?,?,?,?,?,?)'
    for line in dataHC:
        c.execute(statement2,line+((1/(float(fos_hc)*sqrt((line[2]/line[4])**2+(line[3]/line[5])**2)))-1,))
        conn.commit()
        

# Functie pentru scrierea rezultatelor de la HC MOS pentru toate cazurile, pentru fiecare group de elm
def write_all_hc_mos(nume_group,coloana,index):
    statement3='SELECT eid,pid,shearXZ,shearYZ,FsL,FsW,Subcase,min(MOS)\
               FROM HC_mos\
               WHERE eid IN (SELECT eid FROM '+nume_group+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)\
               AND subcase = ?'
    #selecteaza randul cu min(MOS pentru HC) pentru grupul de elemente  
    c.execute(statement3,(index,))
    data=c.fetchall()

    #scrie in worksheetul de resultate, toate datele de min MOS pentru fiecare caz corespunzator grupului
    worksheet3.write(0,coloana,nume_group)
    for row in data:
        for j, value in enumerate(row):
            if value==None:
                worksheet3.write(index, j+coloana, 'None')
            else:
                worksheet3.write(index, j+coloana, value)

# Functie pentru scrierea valorilor minime ale MOS pentru HC pentru fiecare Group de elem
def write_min_hc_mos(nume_group,rows):
    statement4='SELECT eid,pid,shearXZ,shearYZ,FsL,FsW,Subcase,min(MOS)\
               FROM HC_mos\
               WHERE eid IN (SELECT eid FROM '+nume_group+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)'
    
    #selecteaza randul cu min(hc) pentru grupul de elemente
    c.execute(statement4)
    data=c.fetchall()

    #scrie Headerul pentru tabelul de rezultate calculate
    header=['Group Name','EID','PID','Shear XZ','Shear YZ','FsL','FsW','Subcase','MOS HC']
    for n,m in enumerate(header):
        worksheet4.write(0,n,m)

    #scrie in worksheetul de calcule stress, valorile minime pentru mos HC pe group   
    worksheet4.write(rows,0,nume_group)
    for i in data:
        for col,val in enumerate(i):
            if val==None:
                pass
            else:
                worksheet4.write(rows, col+1, val)
                    
    
def main():
    start_time = time.time()
    intro = '''
    ------------------------------------------------------------------
                 Space Rider Cold Structure Data Analysis
    ------------------------------------------------------------------
                            - Version 2.11 -
	
	Added functions:
	- Insert all result data in database resultsData.db
	- Use GroupsOutput.txt as element clasification by groups
	- Use GroupHCproperties.txt as input for hc props for Elm
	- Use GroupAL.txt as input for AL parts Elm groups
	- Output excel file with results 
	- Output word document with table results
	
    '''
    print (intro)
        
    input_fisier=input('Type the f06 file name:')


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
        print("--- %s seconds to SR extraction---" % (time.time() - start_time))

        # Adauga in paranteze input_fisier[:-4]+'_stress.f06' daca ai spart in fisiere separate
        stress_to_database(input_fisier)
        print("--- %s seconds to Stress extraction---" % (time.time() - start_time))
        
    else:
        pass


    '''
    Create tables with group names and specific EID, based on GroupOuput.txt
    - if tables exist, they will be deleted and written again
    '''
    groupNames=read_groups()
    print("--- %s seconds to create tables from group names ---" % (time.time() - start_time))


    # Number of cases based on disctinct subcases present in ElmStrengthRatio Table
    nr_cazuri=nrCazuri()
    print ('Number of cases',nr_cazuri[0])


    '''
    Create Table based on HC properties with plyID, FsL, FsW and eid for every pcomp elem with HC
    '''
    read_hc_props()
    print("--- %s seconds to create tables with HC properties ---" % (time.time() - start_time))


    '''
    Process SR data and write to excel the results
    
    '''
    condition = input('Do you want to process SR data and write the results to the excel file ? 1-Yes, 2-No: ')

    if condition == '1':
        fosu_sr = input('Insert FOS for SR facing MOS calculation = ')
        col=0
        rows=1
        for group in groupNames:
            for i in range(nr_cazuri[0]):
                read_sr(group,col,i+1)
            process_sr(group,rows,fosu_sr)
            col+=5
            rows+=1
        workbook.close()
        print("--- %s seconds to read and process SR data ---" % (time.time() - start_time))
    elif condition == '2':
        print('NO SR ouput written to excel results file!')



    '''
    Process Stress data for HC MOS calculation and write to excel the results
    
    '''
    condition2 = input('Do you want to process Stress data for HC MOS calculation and ouput results to excel ? 1-Yes, 2-No: ')
    
    if condition2 == '1':
        rows2=1
        col2=0
        fosu_hc = input('Insert FOS for HoneyComb MOS calculation = ')
        c.execute('DROP TABLE IF EXISTS HC_mos') 
        for i in range(nr_cazuri[0]):
            # cazul de input trebuie sa porneasca de la 1 pentru statement de SELECT
            create_hc_mos(i+1,fosu_hc)
        print("--- %s seconds to create HC MOS table in database ---" % (time.time() - start_time))

        for group in groupNames:
            for j in range(nr_cazuri[0]):
                write_all_hc_mos(group,col2,j+1)
            write_min_hc_mos(group,rows2)
            col2+=9
            rows2+=1
        workbook.close()    
        print("--- %s seconds to write HC MOS results to Excel file ---" % (time.time() - start_time))  
    elif condition == '2':
        print('NO HC ouput written to excel results file!')






    
    fosy_parts = input('Insert FOSyield for VonMises MOSyield calculation for AL parts = ')
    fosu_parts = input('Insert FOSultimate for VonMises MOSultimate calculation for AL parts = ')
    



    word=input('Do you want to write word document with results in table form? 1-yes, 2-no: ')

    if word=='1':
        print('not writing')




    c.close()
    conn.close()
    end = time.time()
    print ('Execution Time:')
    print (str(end - start_time)+' seconds') 
    input('Press Enter to close.')


main()
    
