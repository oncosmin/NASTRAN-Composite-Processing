'''
Extras rezultate pentru Stress Elements
'''
import csv
import time

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
