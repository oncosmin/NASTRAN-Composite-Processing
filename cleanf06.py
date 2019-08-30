import time

def clean_f06(fisier_in):
    fisier_in=fisier_in[:-4]
    with open(fisier_in+'.f06') as infile, open(fisier_in+'_stress.f06', 'w') as outfile:
        copy = False
        for line in infile:
            if 'S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S' in line :
                copy = True
                outfile.write(line)
                continue
            elif "F A I L U R E   I N D I C E S   F O R   L A Y E R E D   C O M P O S I T E" in line:
                copy = False
                print('Stress output file created')
                break
            elif copy:
                outfile.write(line)

    with open(fisier_in+'.f06') as infile, open(fisier_in+'_sr.f06', 'w') as outfile:
        copy = False
        for line in infile:
            if 'S T R E N G T H   R A T I O S   F O R   L A Y E R E D   C O M P O S I T E   E L E M E N T S' in line :
                copy = True
                outfile.write(line)
                continue
            elif "S T R E S S E S   I N   B A R   E L E M E N T S" in line:
                copy = False
                print('Strength ratio output file created')
                break
            elif copy:
                outfile.write(line)

#time to completion
