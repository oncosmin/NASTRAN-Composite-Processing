import csv
import sqlite3
import time
from patran_input import process_input
from xlsxwriter.workbook import Workbook

'''
Open and connect to database forces
'''
conn=sqlite3.connect('ResultsDataForces.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")

'''
Open excel file to write
'''
workbook = Workbook('ResultsForces.xlsx')
worksheet1 = workbook.add_worksheet('Data_Forces')
worksheet2 = workbook.add_worksheet('Summary_Forces')


'''
Function to read Forces values from pch file
and write them into database ResultsDataForces.db
'''

#Create Table for all element forces in the pch file
def create_forces_table():
    c.execute('DROP TABLE IF EXISTS ElmForces')
    c.execute('CREATE TABLE IF NOT EXISTS ElmForces(eid INTEGER, subcase INTEGER, Fx REAL, Fy REAL, Fz REAL,\
                Mx REAL, My REAL, Mz REAL)')

def forces_data_entry(eid, subcase, fx, fy, fz, mx, my, mz):
    c.execute("INSERT INTO ElmForces VALUES(?,?,?,?,?,?,?,?)",
              (eid, subcase, fx, fy, fz, mx, my, mz))
    conn.commit()

#Function to determine number of subcases
def nrCazuri():
    c.execute('SELECT COUNT(DISTINCT subcase) FROM ElmForces')
    nrCaz=c.fetchone()
    return nrCaz

#Function to extract forces from pch file and write them into .db tables
def parse_forces(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        count=0
        for line in f:
            if '$SUBCASE ID =' in line:
                x=line.split()
                if len(x)==5:
                    caz=x[3]
            if ' BUSH ' in line:
                parse = True
            elif line.startswith('$TITLE'):
                parse = False
            if parse:
                count+=1 #determin linia la care sunt
                elements=line.split()
                if elements[0]!='-CONT-':
                    elmID=elements[0]
                    count=2
                    fxyz=elements[1:4]
                elif elements[0]=='-CONT-':
                    mxyz=elements[1:4]
                    print
                    forces_data_entry(elmID,caz,fxyz[0],fxyz[1],fxyz[2],mxyz[0],mxyz[1],mxyz[2])
                else:
                    continue
            else:
                continue

    f.close()

# Function to write tables with elements and groups from CBUSH groups
def read_cbush_groups():
    file=open('CBUSH_IF_Groups.txt','r')
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
    #return listaGrupuri[:-1] because we don't want to retrieve ElementeEliminate as a group name
    return listaGrupuri[:-1]

def write_forces (nume_group,coloana):
    statement='SELECT eid,subcase,Fx,Fy,Fz,Mx,My,Mz\
               FROM ElmForces\
               WHERE eid IN (SELECT eid FROM '+nume_group+')'

    
    c.execute(statement)
    data=c.fetchall()
    #scrie header pentru rezultate
    worksheet1.write(0,coloana,nume_group)
    header=['EID','Subcase','Fx[N]','Fy[N]','Fz[N]','Mx[Nm]','My[Nm]','Mz[Nm]']
    for n,m in enumerate(header):
        worksheet1.write(1,n+coloana,m)

    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for i,row in enumerate(data):
        for x in range(len(row)):
           worksheet1.write(i+2, x+coloana, row[x]) 
        

    
    
def write_max_forces(group_name,index,a):
    #scrie group, sari 3 poziti (variabila a)
    worksheet2.write(index+a,0,group_name)
    worksheet2.write(index+a+1,0,group_name)
    worksheet2.write(index+a+2,0,group_name)
    # select max(Fx)
    statement1='SELECT eid,subcase,max(abs(Fx)),Fy,Fz,Mx,My,Mz\
               FROM ElmForces\
               WHERE eid IN (SELECT eid FROM '+group_name+')'
    c.execute(statement1)
    data=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data)):
        worksheet2.write(index+a, j+1, data[j]) 
 
    
    statement2='SELECT eid,subcase,Fx,max(abs(Fy)),Fz,Mx,My,Mz\
               FROM ElmForces\
               WHERE eid IN (SELECT eid FROM '+group_name+')'
    c.execute(statement2)
    data2=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data2)):
        worksheet2.write(index+1+a, j+1, data2[j])  
 

    statement3='SELECT eid,subcase,Fx,Fy,max(abs(Fz)),Mx,My,Mz\
               FROM ElmForces\
               WHERE eid IN (SELECT eid FROM '+group_name+')'
    c.execute(statement3)
    data3=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data3)):
        worksheet2.write(index+2+a, j+1, data3[j]) 


def main():
    start_time = time.time()
    intro = '''
    =====================================================
    Extract CBUSH Forces from pch file and write to Excel
    =====================================================

    '''

    print(intro)
    input_fisier=input('Type the .pch file name:')
    print('Started execution...')
    create_forces_table()
    parse_forces(input_fisier)
    print("--- %s seconds to parse forces into Database  ---" % (time.time() - start_time))
    read_cbush_groups()

    # Number of cases based on disctinct subcases present in ElmStrengthRatio Table
    nr_cazuri=nrCazuri()
    print ('Number of cases',nr_cazuri[0])

    # Write values to excel
    c.execute('DROP INDEX IF EXISTS index_forces')
    c.execute('CREATE INDEX index_forces ON ElmForces(eid,subcase)')
    #Create table of results for min(SR) and MOS based on groups and subcases
    #c.execute('DROP TABLE IF EXISTS ElmSR_MOS')
    col=0
    row=1
    groupNames=read_cbush_groups()
    for group in groupNames:
        write_forces(group,col)
        #write_max_forces(group)
        col+=10
    print("--- %s seconds to write all forces data ---" % (time.time() - start_time))

    header=['Group Name','EID','Subcase','Fx[N]','Fy[N]','Fz[N]','Mx[Nm]','My[Nm]','Mz[Nm]']
    for n,m in enumerate(header):
        worksheet2.write(0,n,m)
    a=1
    for j,group in enumerate(groupNames):
        write_max_forces(group,j,a)
        a+=3
    workbook.close()

    
    c.close()
    conn.close()
    end = time.time()
    print('Finished with no errors!')
    print ('Execution Time:')
    print (str(end - start_time)+' seconds') 
    input('Press Enter to close.')

main()
