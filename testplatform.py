# -*- coding: utf-8 -*-
import epilearn
import datetime
import time

###############################################################################
###############################################################################
#from utils import validation_for_genandtest


def runbatch(tupleset,repetitions,dataname,constraintset,relation):
    for mytuple in tupleset:
        repeatrun(mytuple,repetitions,dataname,constraintset,relation)
        
        
        
        
def repeatrun(mytuple,repetitions,dataname,constraintset,relation):
    print("\n%%%%%%%%%%%%%%%%%%%%%%%%%\n")
    posscols = mytuple[0]
    posshead = mytuple[1]
    sumtime = 0
    sumrules = 0
    sumcover = 0
    sumaccuracy = 0
    sumlift = 0
    sumconditions = 0
    sumirrational = 0
    sumnumfilter = 0
    for x in range(0,repetitions):
        # print(str(datetime.datetime.now().time()))
        t0 = time.time()
        scores = runtuple(mytuple,dataname,constraintset,relation)
        t1 = time.time()
        sumtime = sumtime+(t1-t0)
        sumrules = sumrules + scores[0]
        sumcover = sumcover + scores[1]
        sumaccuracy = sumaccuracy + scores[2]
        sumlift = sumlift + scores[3]
        sumirrational = sumirrational + scores[5]
        sumconditions = sumconditions + scores[4]
        sumnumfilter = sumnumfilter + scores[6]
        simplebestrules = scores[7]
    avtime = doaverage(sumtime,repetitions)
    avrules = doaverage(sumrules,repetitions)
    avcover = doaverage(sumcover,repetitions)
    avaccuracy = doaverage(sumaccuracy,repetitions)
    avlift = doaverage(sumlift,repetitions)
    avconditions = doaverage(sumconditions,repetitions)
    avnumfilter = doaverage(sumnumfilter,repetitions)
    print("\n")
    print("Head = "+str(posshead))
    print("Tail = "+str(posscols))
    print("\n")
    print("Number of repetitions \t = "+str(repetitions))    
    print("Av time per rule set \t = "+str(round(avtime,2)))    
    print("Av number of rules \t = "+str(round(avrules,2)))
    print("Av cover of rules \t = "+str(round(avcover,2)))
    print("Av accuracy of rules \t = "+str(round(avaccuracy,2)))
    print("Av lift of rules \t = "+str(round(avlift,2)))
    print("Av conditions per rule \t = "+str(round(avconditions,2)))    
    print("Number of irrational rules \t = " + str(sumirrational))
    print("Number of rules being deleted \t = " + str(round(avnumfilter,2)))
    print("\n%%%%%%%%%%%%%%%%%%%%%%%%%\n")
    print("\n")    
    for x in simplebestrules:
        print(str(x))
        print("\n")
    print("\n")
    print("\n%%%%%%%%%%%%%%%%%%%%%%%%%\n")

        

def runtuple(mytuple,dataname,constraintset,relation):
    if dataname == "spain":
        filename = "wiki4HE.csv"
    elif dataname == "italy":
        filename = "politicalattitudes.csv"
    posscols = mytuple[0]
    posshead = mytuple[1]
    results = epilearn.genandtest(filename,posscols+posshead,posshead,dataname,constraintset,relation)
    return results
    

def doaverage(x,y):
    if x > 0 and y > 0:
        return x/y
    else:
        return 0
    
    
###############################################################################
###############################################################################

def run(code):    
    if code == 2:        
        dataname = "italy"
        source = ["sys1","sys3","sys4","sys5","sys6","sys7","sys8"]
        target = ["sys2"]
        relation= [1,0,1,1,1,0,1]
        constraintset= [0.5]
    
    
    if code == 4:
        dataname = "italy"
        source = ["dw1","dw2","dw3","dw4","dw5","dw7","dw8","dw9","dw10"]
        target = ["dw6"]
        relation= [0,1,1,0,0,0,1,0,1]
        constraintset= [0.5]
    
    
    if code == 7:
        dataname = "spain"
        source = ["JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","ENJ1"]
        target = ["Qu3"]
        relation= [1,1,1,1,1,1,1,1,1,1,1,1,1]
        constraintset= [0.5]
        
    
    if code == 10:
        dataname = "spain"
        source = ["JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
        target = ["BI1"]
        relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        constraintset= [0.5]
    
    if code == 11:
        dataname = "spain"
        source = ["BI1","BI2","JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
        target = ["Use3"]
        relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        constraintset= [0.5]
    
    if code == 12:
        dataname = "spain"
        source = ["BI1","BI2","JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
        target = ["Use2"]
        relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        constraintset= [0.5]

    
    # if code == 2:        
    #     dataname = "italy"
    #     source = ["sys1","sys3","sys4","sys5","sys6","sys7","sys8"]
    #     target = ["sys2"]
    #     relation= [1,0,1,1,1,0,1]
    #     constraintset= [0.25,0.5,0.75]
    
    
    # if code == 4:
    #     dataname = "italy"
    #     source = ["dw1","dw2","dw3","dw4","dw5","dw7","dw8","dw9","dw10"]
    #     target = ["dw6"]
    #     relation= [0,1,1,0,0,0,1,0,1]
    #     constraintset= [0.25,0.5,0.75]
        
    
    # if code == 7:
    #     dataname = "spain"
    #     source = ["JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","ENJ1"]
    #     target = ["Qu3"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.25,0.5,0.75]
    
    # if code == 10:
    #     dataname = "spain"
    #     source = ["JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
    #     target = ["BI1"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.25,0.5,0.75]
    
    # if code == 11:
    #     dataname = "spain"
    #     source = ["BI1","BI2","JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
    #     target = ["Use3"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.25,0.5,0.75]
    
    # if code == 12:
    #     dataname = "spain"
    #     source = ["BI1","BI2","JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
    #     target = ["Use2"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.25,0.5,0.75]

    # if code == 2:        
    #     dataname = "italy"
    #     source = ["sys1","sys3","sys4","sys5","sys6","sys7","sys8"]
    #     target = ["sys2"]
    #     relation= [1,0,1,1,1,0,1]
    #     constraintset= [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    
    
    # if code == 4:
    #     dataname = "italy"
    #     source = ["dw1","dw2","dw3","dw4","dw5","dw7","dw8","dw9","dw10"]
    #     target = ["dw6"]
    #     relation= [0,1,1,0,0,0,1,0,1]
    #     constraintset= [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        
    
    # if code == 7:
    #     dataname = "spain"
    #     source = ["JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","ENJ1"]
    #     target = ["Qu3"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    
    # if code == 10:
    #     dataname = "spain"
    #     source = ["JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
    #     target = ["BI1"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    
    # if code == 11:
    #     dataname = "spain"
    #     source = ["BI1","BI2","JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
    #     target = ["Use3"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    
    # if code == 12:
    #     dataname = "spain"
    #     source = ["BI1","BI2","JR1","JR2","SA1","SA2","SA3","Im1","Im2","Pf1","Pf2","Pf3","Qu1","Qu2","Qu3","ENJ1","ENJ2","PEU1","PEU2"]
    #     target = ["Use2"]
    #     relation= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #     constraintset= [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]

        
    

        
    tupleset = [[source,target]]
    repetitions = 10
    runbatch(tupleset,repetitions,dataname,constraintset,relation)
     
###############################################################################
###############################################################################


if __name__ == "__main__":
    codes = [2,4,7,10,11,12]
    # codes = [12]
    for code in codes:
        run(code)
    


###############################################################################
###############################################################################