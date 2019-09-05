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
        iduri = ['EID','VonMises Stress','Layer','SUBCASE']
        writer = csv.writer(fisier, delimiter = ',')
        writer.writerow(iduri)
        parse=False
        text =[]
        for line in f:
            if '0' and 'SUBCASE' in line:
                x=line.split()
                if len(x)==3:
                    caz=x[2]
            if 'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S' in line or\
               'S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S' in line:
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



'''
===============================================================================
Functions for extracting and inserting values into ResultsData.db databse
In table ElmVMstress
================================================================================
'''

conn=sqlite3.connect('ResultsData.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")


def create_vm_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmVMstress(eid INTEGER, vm_stress REAL, layer TEXT, subcase INTEGER)')

def vm_stress_data_entry(eid, vm_stress, layer, subcase):
    c.execute("INSERT INTO ElmVMstress VALUES(?, ?, ?, ?)",
              (eid, vm_stress, layer, subcase))
    conn.commit()

def parse_vm_stress(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        text =[]
        for line in f:
            if '0' and 'SUBCASE' in line:
                x=line.split()
                if len(x)==3:
                    caz=x[2]
            if 'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S' in line or\
               'S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S' in line:
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
                                vm_stress_data_entry(value[0],value[1],value[2],value[3])
                            else:
                                value=[words[1],words2[-1],caz]
                                value.insert(2,'Z2')
                                vm_stress_data_entry(value[0],value[1],value[2],value[3])
                        else:
                            continue
                text=[]
    f.close()

    print('Element Stress extracted!')

def vm_stress_to_database(fisier_in):
    create_vm_table()
    parse_vm_stress(fisier_in)
    c.close()
    conn.close()
