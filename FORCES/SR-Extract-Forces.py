import sqlite3
import time
from patran_input import process_input
from xlsxwriter.workbook import Workbook

'''
Open and connect to database forces
'''
conn = sqlite3.connect('ResultsDataForces.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c = conn.cursor()
c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")

'''
Open excel file to write
'''
workbook = Workbook('ResultsForces.xlsx')
worksheet1 = workbook.add_worksheet('Data_Forces')
worksheet2 = workbook.add_worksheet('Summary_Forces')
worksheet3 = workbook.add_worksheet('Data_MPC')
worksheet5 = workbook.add_worksheet('Data_MPC_SUM')
worksheet4 = workbook.add_worksheet('Summary_MPC')
worksheet6 = workbook.add_worksheet('Summary_MPC_Sum')

'''
Function to read Forces values from pch file
and write them into database ResultsDataForces.db
'''


#Create Table for all CBUSH element forces in the pch file
def create_forces_table():
    c.execute('DROP TABLE IF EXISTS ElmForces')
    c.execute('CREATE TABLE IF NOT EXISTS ElmForces(eid INTEGER, subcase INTEGER, \
               Fx REAL, Fy REAL, Fz REAL,\
               Mx REAL, My REAL, Mz REAL)')

#Create table for all MPC node forces extracted from pch file
def create_mpc_forces_table():
    c.execute('DROP TABLE IF EXISTS ElmMPCForces')
    c.execute('CREATE TABLE IF NOT EXISTS ElmMPCForces(nid INTEGER, subcase INTEGER, \
               Fx REAL, Fy REAL, Fz REAL,\
               Mx REAL, My REAL, Mz REAL)')    
#Create table for all MPC node forces extracted from pch file
def create_mpcSUM_forces_table():
    c.execute('DROP TABLE IF EXISTS ElmMPCSumForces')
    c.execute('CREATE TABLE IF NOT EXISTS ElmMPCSumForces(name TEXT, subcase INTEGER, \
               Fx REAL, Fy REAL, Fz REAL,\
               Mx REAL, My REAL, Mz REAL)') 

#Insert cbush elm forces into ElmForces table
def forces_data_entry(eid, subcase, fx, fy, fz, mx, my, mz):
    c.execute("INSERT INTO ElmForces VALUES(?,?,?,?,?,?,?,?)",
              (eid, subcase, fx, fy, fz, mx, my, mz))
    conn.commit()

    
#Insert MPC node forces into ElmForces table
def mpc_forces_data_entry(nid, subcase, fx, fy, fz, mx, my, mz):
    c.execute("INSERT INTO ElmMPCForces VALUES(?,?,?,?,?,?,?,?)",
              (nid, subcase, fx, fy, fz, mx, my, mz))
    conn.commit()

#Insert MPC node forces into ElmForces table
def mpcSUM_forces_data_entry(name, subcase, fx, fy, fz, mx, my, mz):
    c.execute("INSERT INTO ElmMPCSumForces VALUES(?,?,?,?,?,?,?,?)",
              (name, subcase, fx, fy, fz, mx, my, mz))
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
                elements=line.split()
                if elements[0]!='-CONT-':
                    elmID=elements[0]
                    count=2
                    fxyz=elements[1:4]
                elif elements[0]=='-CONT-':
                    mxyz=elements[1:4]
                    forces_data_entry(elmID,caz,fxyz[0],fxyz[1],fxyz[2],mxyz[0],mxyz[1],mxyz[2])
                else:
                    continue
            else:
                continue


#Function to extract forces from pch file and write them into .db tables
def parse_mpc_forces(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        for line in f:
            if '$SUBCASE ID =' in line:
                x=line.split()
                if len(x)==5:
                    caz=x[3]
            if '$MPCF ' in line:
                parse = True
            elif line.startswith('$TITLE'):
                parse = False
            if parse:
                nodes=line.split()
                if nodes[0]!='-CONT-' and nodes[0]!='$REAL'\
                   and nodes[0]!='$SUBCASE':
                    nodeID=nodes[0]
                    fxyz=nodes[2:5]
                elif nodes[0]=='-CONT-':
                    mxyz=nodes[1:4]
                    mpc_forces_data_entry(nodeID,caz,fxyz[0],fxyz[1],fxyz[2],mxyz[0],mxyz[1],mxyz[2])
                else:
                    continue
            else:
                continue


# Function to write tables with elements and groups from CBUSH groups
def read_cbush_groups():
    with open('CBUSH_IF_Groups.txt','r') as file:
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

# Function to write tables with nodes groups from MPC groups
def read_mpc_groups():
    with open('MPC_Forces.txt','r') as file:
        listaGrupuriMPC=[]
        for line in file:
            linie=line.split(',')
            listaGrupuriMPC.append(linie[0])
            c.execute('DROP TABLE IF EXISTS {} '.format(linie[0]))
            c.execute('CREATE TABLE IF NOT EXISTS {} (nid INTEGER)'.format(linie[0]))
            lista=process_input(str(linie[1]))
            for i in lista:
                statement='INSERT OR REPLACE INTO '+linie[0]+' VALUES(?)'
                c.execute(statement,(i,))
                conn.commit()
    return listaGrupuriMPC

#function to create tables from MPC sum text file
def read_mpcSUM_groups():
    with open('MPC_Forces_Sum.txt','r') as file:
        listaGrupuriMPCsum=[]
        for line in file:
            linie=line.split(',')
            listaGrupuriMPCsum.append(linie[0])
            c.execute('DROP TABLE IF EXISTS {} '.format(linie[0]))
            c.execute('CREATE TABLE IF NOT EXISTS {} (nid INTEGER)'.format(linie[0]))
            lista=process_input(str(linie[1]))
            for i in lista:
                statement='INSERT OR REPLACE INTO '+linie[0]+' VALUES(?)'
                c.execute(statement,(i,))
                conn.commit()
    return listaGrupuriMPCsum

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
        
# function for writing mpc forces to excel based on groups
def write_mpc_forces(nume_group,coloana):
    statement='SELECT nid,subcase,Fx,Fy,Fz,Mx,My,Mz\
               FROM ElmMPCForces\
               WHERE nid IN (SELECT nid FROM '+nume_group+')'
    c.execute(statement)
    data=c.fetchall()
 
    #scrie header pentru rezultate
    worksheet3.write(0,coloana,nume_group)
    header=['NodeID','Subcase','Fx[N]','Fy[N]','Fz[N]','Mx[Nm]','My[Nm]','Mz[Nm]']
    for n,m in enumerate(header):
        worksheet3.write(1,n+coloana,m)

    #scrie in worksheetul de rezultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for i,row in enumerate(data):
        for x in range(len(row)):
           worksheet3.write(i+2, x+coloana, row[x]) 

def creat_mpcSUM_table(nume_groupSUM,subcase):
    statement2='SELECT SUM(abs(Fx)),SUM(abs(Fy)),SUM(abs(Fz)),\
                       SUM(abs(Mx)),SUM(abs(My)),SUM(abs(Mz))\
                FROM ElmMPCForces\
                WHERE nid IN (SELECT nid FROM '+nume_groupSUM+')\
                AND subcase=?'
    c.execute(statement2,(subcase,))
    data=c.fetchall()
    mpcSUM_forces_data_entry(nume_groupSUM,subcase,data[0][0],data[0][1],data[0][2],\
                             data[0][3],data[0][4],data[0][5]) 


def write_mpcSUM_forces():
    c.execute('SELECT * FROM ElmMPCSumForces')
    data=c.fetchall()
    header=['Name','Subcase','Fx[N]','Fy[N]','Fz[N]','Mx[Nm]','My[Nm]','Mz[Nm]']
    for n,m in enumerate(header):
        worksheet5.write(0,n,m)
    for i,row in enumerate(data):
        for x in range(len(row)):
           worksheet5.write(i+1, x, row[x]) 
    
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

    statement2 = 'SELECT eid,subcase,Fx,max(abs(Fy)),Fz,Mx,My,Mz\
               FROM ElmForces\
               WHERE eid IN (SELECT eid FROM '+group_name+')'
    c.execute(statement2)
    data2 = c.fetchone()
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

def write_max_mpc_forces(group_name,index,a):
    #scrie group, sari 3 poziti (variabila a)
    worksheet4.write(index+a,0,group_name)
    worksheet4.write(index+a+1,0,group_name)
    worksheet4.write(index+a+2,0,group_name)
    # select max(Fx)
    statement1='SELECT nid,subcase,max(abs(Fx)),Fy,Fz,Mx,My,Mz\
               FROM ElmMPCForces\
               WHERE nid IN (SELECT nid FROM '+group_name+')'
    c.execute(statement1)
    data=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data)):
        worksheet4.write(index+a, j+1, data[j]) 

    statement2 = 'SELECT nid,subcase,Fx,max(abs(Fy)),Fz,Mx,My,Mz\
               FROM ElmMPCForces\
               WHERE nid IN (SELECT nid FROM '+group_name+')'
    c.execute(statement2)
    data2 = c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data2)):
        worksheet4.write(index+1+a, j+1, data2[j])  
 

    statement3='SELECT nid,subcase,Fx,Fy,max(abs(Fz)),Mx,My,Mz\
               FROM ElmMPCForces\
               WHERE nid IN (SELECT nid FROM '+group_name+')'
    c.execute(statement3)
    data3=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data3)):
        worksheet4.write(index+2+a, j+1, data3[j]) 

def write_max_mpc_sum_forces(group_name,index,a):
    #scrie group, sari 3 poziti (variabila a)
    worksheet6.write(index+a,0,group_name)
    worksheet6.write(index+a+1,0,group_name)
    worksheet6.write(index+a+2,0,group_name)
    # select max(Fx)
    statement1='SELECT name,subcase,max(abs(Fx)),Fy,Fz,Mx,My,Mz\
               FROM ElmMPCSumForces\
               WHERE name=?'
    c.execute(statement1,(group_name,))
    data=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data)):
        worksheet6.write(index+a, j, data[j]) 

    statement2 = 'SELECT name,subcase,Fx,max(abs(Fy)),Fz,Mx,My,Mz\
               FROM ElmMPCSumForces\
               WHERE name=?'
    c.execute(statement2,(group_name,))
    data2 = c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data2)):
        worksheet6.write(index+1+a, j, data2[j])  
 

    statement3='SELECT name,subcase,Fx,Fy,max(abs(Fz)),Mx,My,Mz\
               FROM ElmMPCSumForces\
               WHERE name=?'
    c.execute(statement3,(group_name,))
    data3=c.fetchone()
    #scrie in worksheetul de resultate, toate datele de forte pentru fiecare caz corespunzator grupului
    for j in range(len(data3)):
        worksheet6.write(index+2+a, j, data3[j])     

def main():
    start_time = time.time()
    intro = '''
    =====================================================
    Extract CBUSH Forces from pch file and write to Excel
    =====================================================
    Extract MPC Forces from pch file and write to Excel
    =====================================================
    
    CBUSH_IF_Groups.txt - group of elem to extract forces
    MPC_Forces - group of nodes to extract forces
    MPC_Forces_Sum - group of nodes to extract and add forces
    '''

    print(intro)
    input_fisier=input('Type the .pch file name:')
    print('Started execution...')
    errors=False
    

    '''
    Write CBUSH forces to exel file
    '''
    #condition1=input('Do you want to extract cbush elm forces?(1=yes) :')
    #if condition1=='1':
    create_forces_table()
    try:
        parse_forces(input_fisier)
        print("--- %s seconds to parse forces into Database  ---" % (time.time() - start_time))
    except FileNotFoundError:
        errors=True
        print('++++++++++++++++++++++++++++++++++++++++++++++++')
        print('FILE not FOUND! Make sure you write the name correct!')
        print('++++++++++++++++++++++++++++++++++++++++++++++++')
    read_cbush_groups()
    print("--- %s seconds to parse cbush groups  ---" % (time.time() - start_time))
    
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

    # Number of cases based on disctinct subcases present in ElmForces Table
    nr_cazuri=nrCazuri()
    print ('Number of cases',nr_cazuri[0])

    '''
    Write MPC forces to excel
    '''
    condition2=input('Do you want to write MPC nodes from MPC_Forces.txt ?(1=Yes) :')
    if condition2=='1':
        create_mpc_forces_table()
        try:
            parse_mpc_forces(input_fisier)
        except FileNotFoundError:
            errors=True
            print('++++++++++++++++++++++++++++++++++++++++++++++++')
            print('FILE not FOUND! Make sure you write the name correct!')
            print('++++++++++++++++++++++++++++++++++++++++++++++++')
        read_mpc_groups()
        print("--- %s seconds to parse mpc groups  ---" % (time.time() - start_time))
        # Write values to excel
        c.execute('DROP INDEX IF EXISTS index_mpc_forces')
        c.execute('CREATE INDEX index_mpc_forces ON ElmMPCForces(nid,subcase)')
        # write all values to excel
        col2=0
        row2=1
        groupNames2=read_mpc_groups()
        for group2 in groupNames2:
            write_mpc_forces(group2,col2)
            col2+=10

        #write summary of forces based on groups
        header=['Group Name','NodeID','Subcase','Fx[N]','Fy[N]','Fz[N]','Mx[Nm]','My[Nm]','Mz[Nm]']
        for p,r in enumerate(header):
            worksheet4.write(0,p,r)
        b=1
        for x,group3 in enumerate(groupNames2):
            write_max_mpc_forces(group3,x,b)
            b+=3
        
    print("--- %s seconds to write all mpc forces data ---" % (time.time() - start_time))

        
    condition3=input('Do you want to write MPC nodes sum from MPC_Forces_Sum.txt ?(1=Yes) :')
    if condition3=='1':
        create_mpcSUM_forces_table()
        read_mpcSUM_groups()
        groupNames3=read_mpcSUM_groups()
        for group4 in groupNames3:
            for j in range(nr_cazuri[0]):
                creat_mpcSUM_table(group4,j+1)
        #write all mpc summed from MPC_Sum_Groups.txt
        write_mpcSUM_forces()

        #write mpc summed to summary 
        header=['Name','Subcase','Fx[N]','Fy[N]','Fz[N]','Mx[Nm]','My[Nm]','Mz[Nm]']
        for g,h in enumerate(header):
            worksheet6.write(0,g,h)
        d=1
        for y,group5 in enumerate(groupNames3):
            write_max_mpc_sum_forces(group5,y,d)
            d+=3
            
    print("--- %s seconds to write all mpc sum forces data ---" % (time.time() - start_time))

    try:
        workbook.close()
    except PermissionError:
        print('++++++++++++++++++++++++++++++++++++++++++++++++')
        print('Close workbook before atempting to write to it !')
        print('++++++++++++++++++++++++++++++++++++++++++++++++')
        errors=True
    c.close()
    conn.close()
    end = time.time()
    if errors:
        print('=====================')
        print('Finished with ERRORS!')
        print('=====================')
    else:
        print('Finished with no Errors')
    print ('Execution Time:')
    print (str(end - start_time)+' seconds') 
    input('Press Enter to close.')

main()
