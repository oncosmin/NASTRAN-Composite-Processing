'''
Extras rezultate pentru Strength Ratio
'''
import csv
import time

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

    
