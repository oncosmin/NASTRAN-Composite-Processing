'''
Extras rezultate pentru VonMises Stress, elemente metalice
'''
import csv
import sqlite3
#import time



'''
===============================================================================
Function for extracting and inserting values into Rezultate-VM-Stress.csv
================================================================================
'''

def parse_stress_vm(input_file):
    
    with open(input_file, 'r') as f:
        fisier = open('Rezultate-VM-Stress.csv','w',newline='')
        iduri = ['EID','Layer','VonMises Stress','SUBCASE']
        writer = csv.writer(fisier, delimiter = ',')
        writer.writerow(iduri)
        parse=False
        text =[]
        for line in f:
            if '0' and 'SUBCASE' in line:
                x=line.split()
                if len(x)==3:
                    caz=x[2]
            if 'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S' in line:
                parse = True              
            elif line.startswith('1'):
                parse = False
            if parse:
                text.append(line)
            else:
                for i in range(len(text)):
                    # verifica daca linia este goala si treci peste
                    # Desi linia este goala, apar elemente in ea, nu inteleg de ce?
                    if len(text[i])!=2 and len(text[i])!=1:
                        words = text[i].split()
                        if words[0] == '0':
                            words2 = text[i+1].split()
                            if float(words[-1])>float(words2[-1]): #check if VM at z1 fiber is bigger than VM at z2 positon
                                value=[words[1],words[-1],caz]
                                value.insert(2,'Z1')
                                writer.writerow(value)
                            else:
                                value=[words[1],words2[-1],caz]
                                value.insert(2,'Z2')
                                writer.writerow(value)
                        else:
                            continue
                text=[]
        fisier.close()
    f.close()

    print('Element VonMises Stress extracted!')


parse_stress_vm('spacerider_landing_impact_loads.f06')


'''
===============================================================================
Functions for extracting and inserting values into resultsData.db databse
In table ElmStress
================================================================================
'''

conn=sqlite3.connect('ResultsData2.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")


def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmVMStress(eid INTEGER, pid INTEGER, normal1 REAL, normal2 REAL,\
               shear12 REAL, shearXZ REAL, shearYZ REAL, angle REAL, major REAL,minor REAL, shear REAL, subcase INTEGER)')

def stress_data_entry(eid, pid, normal1, normal2, shear12, shearXZ, shearYZ, angle, major, minor, shear, subcase):
    c.execute("INSERT INTO ElmStress VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (eid, pid, normal1, normal2, shear12, shearXZ, shearYZ, angle, major, minor, shear, subcase))
    conn.commit()

def parse_stress2(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        text =[]
        caz=1
        for line in f:
            if '0' and 'SUBCASE' in line:
                x=line.split()
                if len(x)==3:
                    caz=x[2]
            if 'S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S' in line:
                parse = True              
            elif line.startswith('1'):
                parse = False
            if parse:
                text.append(line)
            else:
                for lines in text:
                    words = lines.split()
                    if len(words)==12:
                        # value=words[1:12]+[caz]
                        stress_data_entry(words[1],words[2],words[3],words[4],words[5],words[6],words[7],words[8],words[9],words[10],words[11],caz)
                    else:
                        pass
                text=[]
    f.close()

    print('Element Stress extracted!')

##def stress_to_database(fisier_in):
##    create_table()
##    parse_stress2(fisier_in)
##    c.close()
##    conn.close()
