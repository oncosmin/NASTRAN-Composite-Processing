'''
Extras rezultate pentru Stress Elements
'''
#import csv
import sqlite3
import re

conn=sqlite3.connect('ResultsData.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")


'''
===============================================================================
Function for extracting and inserting values into Rezultate-Elm-Stress.csv

-Extracting values from .f06 file
================================================================================
'''

def parse_stress(input_file):
    
    with open(input_file, 'r') as f:
        fisier = open('Rezultate-Elm-Stress.csv','w',newline='')
        iduri = ['EID','PID','NORMAL 1','NORMAL 2','SHEAR 12','SHEAR XZ','SHEAR YZ','ANGLE','MAJOR','MINOR','SHEAR','SUBCASE']
        writer = csv.writer(fisier, delimiter = ',')
        writer.writerow(iduri)
        parse=False
        text =[]
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
                        value=words[1:12]+[caz]
                        writer.writerow(value)
                    else:
                        pass
                text=[]
        fisier.close()
    f.close()

    print('Element Stress extracted!')


'''
===============================================================================
Functions for extracting and inserting values into resultsData.db databse
In table ElmStress

-Extracting values from .f06 file
================================================================================
'''

# DECOMENTEAZA LINILE DE MAI JOS DACA FOLOSESTI CITIRE DIN F06

##def create_table():
##    c.execute('CREATE TABLE IF NOT EXISTS ElmStress(eid INTEGER, pid INTEGER, normal1 REAL, normal2 REAL,\
##               shear12 REAL, shearXZ REAL, shearYZ REAL, angle REAL, major REAL,minor REAL, shear REAL, subcase INTEGER)')
##
##def stress_data_entry(eid, pid, normal1, normal2, shear12, shearXZ, shearYZ, angle, major, minor, shear, subcase):
##    c.execute("INSERT INTO ElmStress VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
##              (eid, pid, normal1, normal2, shear12, shearXZ, shearYZ, angle, major, minor, shear, subcase))
##    conn.commit()

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



'''
===============================================================================
Functions for extracting and inserting values into resultsData.db databse
In table ElmStress

-Extracting values from PCH output file
================================================================================
'''

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmStress(eid INTEGER, pid INTEGER, sig1 REAL, sig2 REAL, sig12 REAL,shearXZ REAL, shearYZ REAL, subcase INTEGER)')

def stress_data_entry(eid, pid, sig1, sig2, sig12, shearXZ, shearYZ, subcase):
    c.execute("INSERT INTO ElmStress VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
              (eid, pid, sig1, sig2, sig12, shearXZ, shearYZ, subcase))
    conn.commit()


def parse_stress3(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        count=0
        for line in f:
            if '$SUBCASE ID =' in line:
                x=line.split()
                if len(x)==5:
                    caz=x[3]
            if 'QUAD4LC' in line:
                parse = True
            elif 'TRIA3LC' in line:
                parse = True
            elif line.startswith('$TITLE'):
                parse = False
            if parse:
                count+=1 #determin linia la care sunt
                elements=line.split()
                #folosim regex pentru a identifica nr real atunci cand id de linie
                # din pch devine prea mare si se leaga de elements[3]
                match_number=re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?.\d{1})?")
                elm=re.findall(match_number,line)
                if elements[0]!='-CONT-' and len(elm)>=4:
                    elmID=elements[0]
                    plyID=elements[1]
                    sig1=elm[2]
                    sig2=elm[3]
                    count=2
                elif elements[0]=='-CONT-' and count==3:
                    sig12=elm[0]
                    shearYZ=elm[2]
                    shearXZ=elements[2]
                    stress_data_entry(elmID,plyID,sig1,sig2,sig12,shearXZ,shearYZ,caz)
                else:
                    continue
            else:
                continue
    f.close()

'''
Main call function
'''

def stress_to_database(fisier_in):
    create_table()
    parse_stress3(fisier_in)
    c.close()
    conn.close()
