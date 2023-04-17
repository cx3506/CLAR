###############################################################
###############################################################


import csv


###############################################################
###############################################################



def dodatadictionary(filename):
    mydictionarylist = []
    headings = getcolnames(filename)
    data = getdata(filename)
    limit = len(headings)
    for x in data:
        mydictionary = {}
        mydictionary["myid"] = x[0]
        content = x[1]
        contentlist = content.split(";")
        counter = 1
        while counter < limit:
            mydictionary[headings[counter]] = contentlist[counter]
            counter = counter+1
        #print(str(mydictionary))
        mydictionarylist.append(mydictionary)
    return mydictionarylist


def domydb(filename):
    mydb = []
    myid = 0
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != '':
                myrow = []
                #print(str(row[0]))
                myrow.append(myid)
                myid = myid+1
                for c in row:
                    myrow.append(c)
                mydb.append(myrow)
        return mydb

def getcolnames(filename):
    mydb = domydb(filename)
    col = mydb[0]
    cola = col[1]
    colnames = cola.split(";")
    #print(str(colnames))
    return colnames


def getdata(filename):
    mydb = domydb(filename)
    data = []
    for i in range(1,len(mydb)):
        row = mydb[i]
        data.append(row)
    return data



###############################################################
###############################################################
###############################################################

    

if __name__ == "__main__":
    filename = "wiki4HE.csv"
    mydictionarylist = dodatadictionary(filename)
    #print(str(mydictionarylist))
    for x in mydictionarylist:
        print("%%%%%%%%%%%%%%%%%%%")
        print("\n\n\n"+str(x))
    


###############################################################
###############################################################
###############################################################




