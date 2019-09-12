'''
Script to extract Shear XZ and YZ Stress from solid elements HEXA
'''

import sqlite3
#import time

'''
===============================================================================
Functions for extracting and inserting values into ResultsData.db databse
In existing table ElmStress

- Reading from PCH output file
================================================================================
'''

conn=sqlite3.connect('ResultsData.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")

def create_solid_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmStress(eid INTEGER, pid INTEGER, shearXZ REAL, shearYZ REAL, subcase INTEGER)')

def solid_stress_data_entry(eid, pid, ShearXZ, ShearYZ, subcase):
    c.execute("INSERT INTO ElmStress VALUES(?, ?, ?, ?, ?)",
              (eid,pid,ShearXZ,ShearYZ,subcase))
    conn.commit()

def parse_solid_stress(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        count=0
        for line in f:
            if '$SUBCASE ID =' in line:
                x=line.split()
                if len(x)==5:
                    caz=x[3]
            if '$ELEMENT TYPE' and 'HEXA' in line:
                parse = True
            elif line.startswith('$TITLE'):
                parse = False
            if parse:
                count+=1 #determin linia la care sunt
                elements=line.split()
                if elements[0]!='-CONT-':
                    elmID=elements[0]
                    count=2
                elif elements[0]=='-CONT-' and count==6:
                    shearYZ=elements[2]
                elif elements[0]=='-CONT-' and count==8:
                    shearXZ=elements[2]
                    solid_stress_data_entry(elmID,0,shearXZ,shearYZ,caz)
                else:
                    continue
            else:
                continue
                    
 
    f.close()

def solid_stress_to_database(fisier_in):
    create_solid_table()
    parse_solid_stress(fisier_in)
    c.close()
    conn.close()

