'''
Extras rezultate pentru Stress Elements
'''
import csv
import sqlite3
import time

start_time = time.time()

'''
===============================================================================
Function for extracting and inserting values into Rezultate-Elm-Stress.csv
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
================================================================================
'''

conn=sqlite3.connect('resultsData.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
#c.execute('''PRAGMA journal_mode = WAL''')
c.execute("BEGIN TRANSACTION")


def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmStress(eid INTEGER, pid INTEGER, normal1 REAL, normal2 REAL,\
               shear12 REAL, shearXZ REAL, shearYZ REAL, angle REAL, major REAL,minor REAL, shear REAL, subcase INTEGER)')

def stress_data_entry(eid, pid, normal1, normal2, shear12, shearXZ, shearYZ, angle, major, minor, shear, subcase):
    c.execute("INSERT INTO ElmStress VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (eid, pid, normal1, normal2, shear12, shearXZ, shearYZ, angle, major, minor, shear, subcase))
    conn.commit()

def parse_stress2():
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open('02_launch load case.f06', 'r') as f:
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
                        # value=words[1:12]+[caz]
                        stress_data_entry(words[1],words[2],words[3],words[4],words[5],words[6],words[7],words[8],words[9],words[10],words[11],caz)
                    else:
                        pass
                text=[]
    f.close()

    print('Element Stress extracted!')

create_table()
parse_stress2()
c.close()
conn.close()
print("--- %s seconds ---" % (time.time() - start_time))
    
##parse_stress('02_launch load case.f06')
##print("--- %s seconds ---" % (time.time() - start_time))
