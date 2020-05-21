'''
Extras rezultate pentru VonMises Stress, elemente metalice
'''
#import csv
import sqlite3
import re


'''
Open and connect to database
'''
conn=sqlite3.connect('ResultsData.db', isolation_level='DEFERRED')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")


'''
===============================================================================
Function for extracting and inserting values into Rezultate-VM-Stress.csv

- Extract values from .f06 output file
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

- Extract values from .f06 output file
================================================================================
'''

# DEOCMENTEAZA LINILE DE MAI JOS DACA VREI SA CITESTI DIN F06

##def create_vm_table():
##    c.execute('CREATE TABLE IF NOT EXISTS ElmVMstress(eid INTEGER, vm_stress REAL, layer TEXT, subcase INTEGER)')
##
##def vm_stress_data_entry(eid, vm_stress, layer, subcase):
##    c.execute("INSERT INTO ElmVMstress VALUES(?, ?, ?, ?)",
##              (eid, vm_stress, layer, subcase))
##    conn.commit()

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



'''
===============================================================================
Functions for extracting and inserting values into ResultsData.db databse
In table ElmVMstress

- Extract VM stress from QUAD,TRIA and HEXA elms from PCH output file
================================================================================
'''



def create_vm_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmVMstress(eid INTEGER, sig1 REAL, sig2 REAL, sig3 REAL,\
                 sig12 REAL, sig23 REAL, sig31 REAL, sigVM REAL, layer TEXT, subcase INTEGER)')

def vm_stress_data_entry(eid,sig1,sig2,sig3,sig12,sig23,sig31,vm_stress,layer,subcase):
    c.execute("INSERT INTO ElmVMstress VALUES(?,?,?,?,?,?,?,?,?,?)",
              (eid,sig1,sig2,sig3,sig12,sig23,sig31,vm_stress,layer,subcase))
    conn.commit()

# Functie de extragere a Von Mises stress din elemente QUAD si TRIA omogene, materiale metalice
def parse_vm_stress2(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        count=0
        for line in f:
            if '$SUBCASE ID =' in line:
                x=line.split()
                if len(x)==5:
                    caz=x[3]
            if ' QUAD4 ' in line:
                parse = True
            elif ' TRIA3 ' in line:
                parse = True
            elif line.startswith('$TITLE'):
                parse = False
            if parse:
                count+=1 #determin linia la care sunt
                elements=line.split()
                match_number=re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?.\d{1})?")
                elm=re.findall(match_number,line)
                if elements[0]!='-CONT-' and elements[0]!='$ELEMENT':
                    elmID=elements[0]
                    count=2
                    sig1_z1=elm[2]
                    sig2_z1=elm[3]
                elif elements[0]=='-CONT-' and count==3:
                    sig12_z1=elm[0]
                elif elements[0]=='-CONT-' and count==4:
                    vm_z1=elements[2]
                elif elements[0]=='-CONT-' and count==5:
                    sig1_z2=elm[0]
                    sig2_z2=elm[1]
                    sig12_z2=elm[2]
                elif elements[0]=='-CONT-' and count==7:
                    vm_z2=elements[1]
                    vm_stress_data_entry(elmID,sig1_z1,sig2_z1,0,sig12_z1,0,0,vm_z1,'Z1',caz)
                    vm_stress_data_entry(elmID,sig1_z2,sig2_z2,0,sig12_z2,0,0,vm_z2,'Z2',caz)
                else:
                    continue
            else:
                continue

    f.close()

#Functie de extragere a Von Mises stress din elemente solide omogene HEXA, mat metalice
def parse_vm_solid_stress2(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        count=0
        for line in f:
            if '$SUBCASE ID =' in line:
                x=line.split()
                if len(x)==5:
                    caz=x[3]
            if ' HEXA ' in line:
                parse = True
            if ' TETRA ' in line:
                parse = True
            elif line.startswith('$TITLE'):
                parse = False
            if parse:
                count+=1 #determin linia la care sunt
                elements=line.split() #split componente linie
                #folosim regex pentru a identifica nr real atunci cand id de linie
                # din pch devine prea mare si se leaga de elements[3]
                match_number=re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?.\d{1})?")
                elm=re.findall(match_number,line)
                if elements[0]!='-CONT-' and elements[0]!='$ELEMENT':
                    elmID=elements[0]
                    count=2
                elif elements[0]=='-CONT-' and count==3:
                    sig1_s=elm[1]
                    sig12_s=elm[2]
                elif elements[0]=='-CONT-' and count==5:
                    vm_solid=elm[2] #al 3 lea element din linie deoarece nu citeste CONT
                elif elements[0]=='-CONT-' and count==6:
                    sig2_s=elm[0]
                    sig23_s=elm[1]
                elif elements[0]=='-CONT-' and count==8:
                    sig3_s=elm[0]
                    sig31_s=elm[1]
                    vm_stress_data_entry(elmID,sig1_s,sig2_s,sig3_s,sig12_s,sig23_s,sig31_s,vm_solid,'Solid',caz)
                else:
                    continue
            else:
                continue

    f.close()


'''
Main call function
'''
def vm_stress_to_database(fisier_in):
    create_vm_table()
    parse_vm_stress2(fisier_in)
    parse_vm_solid_stress2(fisier_in)
    c.close()
    conn.close()

##test input
#vm_stress_to_database('testtempstress.pch')
##c.execute('DROP TABLE IF EXISTS ElmVMStress')
##create_vm_table()
#parse_vm_stress2('01_landing_load_case_13112019.pch')
#parse_vm_solid_stress2('01_landing_load_case_13112019.pch')
