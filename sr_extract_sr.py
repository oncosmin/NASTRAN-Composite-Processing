'''
Extras rezultate pentru Strength Ratio
'''
#import csv
import sqlite3
#import time



'''
===============================================================================
Function for extracting and inserting values into Rezultate-Elm-SR.csv

- Extracting values from .f06 files by PARAM SRCOMPS YES output.
================================================================================
'''

def parse_sr(input_file):
    with open(input_file, 'r') as f:
        fisier2 = open('Rezultate-Elm-SR.csv','w',newline='')
        iduri2 = ['EID', 'PID', 'SR','SUBCASE']
        writer2 = csv.writer(fisier2, delimiter = ',')
        writer2.writerow(iduri2)
        parse=False
        text =[]
        for line in f:
            if '0' and 'SUBCASE' in line:
                x=line.split()
                if len(x)==3:
                    caz=x[2]
            if 'S T R E N G T H   R A T I O S   F O R ' in line:
                parse = True              
            elif line.startswith('1'):
                parse = False
            if parse:
                text.append(line)
            else:
                for lines in text:
                    words = lines.split()
                    if len(words)==4:
                        elmID=[words[0]]
                        value=elmID+words[2:4]+[caz]
                        writer2.writerow(value)
                    elif len(words)==2 and words[1]!='***':
                        value2 = elmID+words+[caz]
                        writer2.writerow(value2)
                    else:
                        pass
                text=[]
        fisier2.close()
    f.close()
    print ('Element Strength Ratio extracted!')


'''
===============================================================================
Functions for extracting and inserting values into resultsData.db databse
In table ElmStrengthRatio
================================================================================
'''

#Comenteaza daca sunt probleme la connectarea bazei de date

conn=sqlite3.connect('ResultsData.db')
conn.execute('pragma journal_mode=wal')
c=conn.cursor()

c.execute('''PRAGMA synchronous = OFF''')
c.execute("BEGIN TRANSACTION")

    
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS ElmStrengthRatio(eid INTEGER, pid INTEGER, sr REAL, subcase INTEGER)')

def sr_data_entry(eid, pid, sr, subcase):
    c.execute("INSERT INTO ElmStrengthRatio VALUES(?, ?, ?, ?)",
              (eid, pid, sr, subcase))
    conn.commit()


def parse_data2(fisier_input):
    # ATENTIE - modifica input file daca folosesti mai departe scrierea in db
    with open(fisier_input, 'r') as f:
        parse=False
        text =[]
        # Daca spargi fisierul .f06 in mai multe separate, scoate commentul de jos.
        #caz=1
        for line in f:
            if '0' and 'SUBCASE' in line:
                x=line.split()
                if len(x)==3:
                    caz=x[2]
            if 'S T R E N G T H   R A T I O S   F O R ' in line:
                parse = True              
            elif line.startswith('1'):
                parse = False
            if parse:
                text.append(line)
            else:
                for lines in text:
                    words = lines.split()
                    if len(words)==4:
                        elmID=words[0]
                        # value=elmID+words[2:4]+[caz]
                        sr_data_entry(elmID, words[2], words[3], caz)
                    elif len(words)==2 and words[1]!='***':
                        # value2 = elmID+words+[caz]
                        sr_data_entry(elmID, words[0], words[1], caz)
                    else:
                        pass
                text=[]
    f.close()
    print ('Element Strength Ratio extracted!')


def sr_to_database(fisier_in):
    create_table()
    parse_data2(fisier_in)
    c.close()
    conn.close()



