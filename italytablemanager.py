###############################################################
###############################################################


import csv


###############################################################
###############################################################
###############################################################
###############################################################
###############################################################



def dodatadictionary(filename):
    dbrows = []
    with open(filename, 'rt') as f:
        csv_reader = csv.reader(f)
        for line in csv_reader:
            #print("\n")
            #print(line)
            dbrows.append(line)
    #print(str(dbrows[0]))
    #print(str(dbrows[1]))
    #print(str(dbrows[2]))
    mydictionarylist = []
    #headings = getcolnames(filename)
    headings = dbrows[0]
    #data = getdata(filename)
    data = dbrows[2:]
    limit = len(headings)
    newid = 0
    for x in data:
        #print(str(x))
        mydictionary = {}
        mydictionary["myid"] = str(newid)
        newid = newid+1
    #    content = x[1]
    #    contentlist = content.split(";")
        counter = 0
        while counter < limit:
            mydictionary[headings[counter]] = x[counter]
            counter = counter+1
        #print("\n")
        #print(str(mydictionary))
        mydictionarylist.append(mydictionary)
    return mydictionarylist
    # printlabels(dbrows)        
        
         
    
        
def printlabels(dbrows):
    i = 0
    label = dbrows[0]
    entry = dbrows[1]
    while i < len(label):
        print("\n"+label[i]+" = "+entry[i])
        i = i+1
    


###############################################################
###############################################################
###############################################################

    

if __name__ == "__main__":
    filename = "politicalattitudes.csv"
    mydictionarylist = dodatadictionary(filename)
    #print(str(mydictionarylist))
#    for x in mydictionarylist:
#        print("%%%%%%%%%%%%%%%%%%%")
#        print("\n\n\n"+str(x))
    


###############################################################
###############################################################
###############################################################

