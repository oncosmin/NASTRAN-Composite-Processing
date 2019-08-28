import time
start_time = time.time()

fisier=input('introdu numele fisierului .f06:')
fisier=fisier[:-4]
with open(fisier+'.f06') as infile, open(fisier+'_stress.f06', 'w') as outfile:
    copy = False
    for line in infile:
        if 'S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S' in line :
            copy = True
            outfile.write(line)
            continue
        elif "F A I L U R E   I N D I C E S   F O R   L A Y E R E D   C O M P O S I T E" in line:
            copy = False
            print('stress output executed')
            break
        elif copy:
            outfile.write(line)

with open(fisier+'.f06') as infile, open(fisier+'_sr.f06', 'w') as outfile:
    copy = False
    for line in infile:
        if 'S T R E N G T H   R A T I O S   F O R   L A Y E R E D   C O M P O S I T E   E L E M E N T S' in line :
            copy = True
            outfile.write(line)
            continue
        elif "S T R E S S E S   I N   B A R   E L E M E N T S" in line:
            copy = False
            print('strength ratio output executed')
            break
        elif copy:
            outfile.write(line)

#time to completion
print("--- %s seconds ---" % (time.time() - start_time))
