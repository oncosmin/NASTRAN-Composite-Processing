"""
+++++++++++++++++++++ PATRAN INPUT CONVERTER +++++++++++++++++++++++++++++++++

This function takes the input for the elements selected in MSC Patran notation
system and converts it to a list of elements that will be further used in the
program for creating the group of elements for each part/assembly.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

def read_input(patran_input):
    alist=patran_input.split(' ')[1:]
    return(alist)

def process_input(gui_list):
    first_list=read_input(gui_list)
    last_list=[]
    for elms in first_list:
        if ':' in elms:
            inside_list=elms.split(':')
            a = int(inside_list[0])
            last_list.append(a)
            if len(inside_list)==3:
                while a != int(inside_list[1]):
                    a += int(inside_list[2])
                    last_list.append(a)
            else:
                while a != int(inside_list[1]):
                    a += 1
                    last_list.append(a)
        else:
            last_list.append(int(elms))

    return last_list
        
if __name__ == '__main__':
    process_input(file)

