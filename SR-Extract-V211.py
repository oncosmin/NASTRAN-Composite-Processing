import csv
import sqlite3
from sr_extract_stress import stress_to_database
from sr_extract_sr import sr_to_database
from cleanf06 import clean_f06
from patran_input import process_input
import time
from xlsxwriter.workbook import Workbook

# Creare fisier excel pentru scrierea rezultatelor
workbook = Workbook('ResultsSR.xlsx')
worksheet = workbook.add_worksheet('Data_Results_SR')
worksheet2 = workbook.add_worksheet('Calculation_SR')

# Creare baza de date pentru stocarea datelor 
conn=sqlite3.connect('ResultsData.db')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()
c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")

def nrCazuri():
    c.execute('SELECT COUNT(DISTINCT subcase) FROM ElmStrengthRatio')
    nrCaz=c.fetchone()
    print(nrCaz)
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
    print(group_name)
    print(data)
    print(column)

    #scrie in worksheetul de resultate, toate datele
    worksheet.write(0,column,group_name)
    for row in data:
        for j, value in enumerate(row):
            if value==None:
                worksheet.write(index, j+column, 'None')
            else:
                worksheet.write(index, j+column, value)

    
def process_sr(group_name,rows):

    statement='SELECT eid,pid,min(sr),subcase\
               FROM ElmStrengthRatio\
               WHERE eid IN (SELECT eid FROM '+group_name+' )\
               AND eid NOT IN (SELECT eid FROM ElementeEliminate)'
    
    #selecteaza randul cu min(SR) pentru grupul de elemente
    c.execute(statement)
    data=c.fetchall()

    #scrie in worksheetul de resultate, toate datele
    worksheet2.write(rows,0,group_name)
    for i in data:
        for col,val in enumerate(i):
            if val==None:
                pass
            else:
                if col==2:
                    worksheet2.write(rows, col+1, val/2-1)
                else:
                    worksheet2.write(rows, col+1, val)




# FCreate Tables in database from GroupOutput.txt
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





    
def main():
    start_time = time.time()
    intro = '''
    ----------------------------------------------------
      Space Rider Cold Structure F06 Extraction Script
    ----------------------------------------------------
                    - Version 2.11 -
	
	Added functions:
	- break f06 file in 2 separate SR and Stress files
	- insert all result data in database resultsData.db
	- use input_groups.txt as group numbering order
	- output excel file with results 
	- output word document with table results
	
    '''
    print (intro)
        
    input_fisier=input('Type the f06 file name:')
    analysis = input('Create database from f06 file?(1-yes, 2-no) input number: ') 

    if analysis=='1':
        
        clean_f06(input_fisier)
        print("--- %s seconds to .f06 file split ---" % (time.time() - start_time))

        sr_to_database(input_fisier[:-4]+'_sr.f06')
        print("--- %s seconds to SR extraction---" % (time.time() - start_time))

        stress_to_database(input_fisier[:-4]+'_stress.f06')
        print("--- %s seconds to Stress extraction---" % (time.time() - start_time))
        
    else:
        pass

    condition=input('Do you want to process SR or Stress data? 1-Strength Ratio, 2-Stress, 3-Both:')
    print (condition)
    if condition == '1' or condition == '3': 
        groupNames=read_groups()
        print("--- %s seconds to create tables from group names ---" % (time.time() - start_time))
        nr_cazuri=nrCazuri()
        print ('Number of cases',nr_cazuri[0])
        col=0
        rows=0
        for group in groupNames:
            for i in range(nr_cazuri[0]):
                read_sr(group,col,i+1)
            process_sr(group,rows)
            col+=5
            rows+=1
        workbook.close()
        print("--- %s seconds to read and process SR data ---" % (time.time() - start_time))
    elif condition == '2':
        print('not processing Stress')
    else:
        pass

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
    
