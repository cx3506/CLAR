
from fileinput import filename
from hashlib import new
import spaintablemanager
import italytablemanager
import random

from utils import validation_for_genandtest


def genandtest(filename,posscols,possheads,dataname,constraintset,relation):
    
    if dataname == "spain":
        mydictionary = spaintablemanager.dodatadictionary(filename) #all data
    elif dataname == "italy":
        mydictionary = italytablemanager.dodatadictionary(filename)
    selecteddata = selectdata(mydictionary,posscols) #data of selected cols
    improveddata = improvedata(selecteddata,posscols) # Deleting rows with "?" and repeated rows
    dataset = transform(improveddata,posscols) #Transform data into probabilities
    splitdata= gettraintestsets(dataset) #split data into train and test sets
    trainingdata = splitdata[0] 
    testingdata = splitdata[1]
    
    allbestrules = []
    rulecount = 0
    num_rule_filter = 0
    for head in possheads:
        cols = posscols[:]
        if head in cols:
            cols.remove(head)
        allsets=genpowerset(cols) #cols's combination(influencer)
        for myset in allsets:
            if myset != [] and len(myset) < 4:
                reqcols = [head]+myset
                rules = genformulaset(reqcols,trainingdata) #generate a set of rules
                rationalrules = filtering(rules, posscols,relation) #generating a set of rational rules
                num_rule_filter = len(rules)- len(rationalrules) + num_rule_filter
                rulecount = rulecount + len(rationalrules)
                newrules = improveformulaset(rationalrules,constraintset)
                bestrules = choosebest(reqcols,trainingdata,newrules)
                allbestrules = allbestrules + bestrules #Generate all rational rules
    simplerules = choosesimplest(allbestrules) #Return a set of simplest rational rules
    
    # print(simplerules)
    # print(num_rule_filter)
     
    sumcover = 0
    sumaccuracy = 0
    sumlift = 0
    sumconditions = 0
    sumirrational = 0
    numberofrules = len(simplerules) # num of simplestbestrules
    # print(numberofrules)
    
    '''
    test
    '''
    for rule in simplerules:
        scores = getrulequality(reqcols,testingdata,rule) #obtain Support(R,D) and Confident(R,D)
        testcoverscore = scores[0] #Support(R,D) for test data
        testaccuracyscore = scores[1] #Confident(R,D) for test data 
        testliftscore = getliftscore(reqcols,testingdata,rule) #Lift(R,D)
        numberofconditions = getnumberofconditions(rule) 
        irrational = getrationalscore(rule, posscols,relation)
        sumirrational = sumirrational + irrational #Num of irrational rules
        sumcover = sumcover +testcoverscore
        sumaccuracy = sumaccuracy + testaccuracyscore
        sumlift = sumlift + testliftscore
        sumconditions = sumconditions + numberofconditions


    #average for parameters
    if sumcover > 0:
        avcover = sumcover/numberofrules
    else:
        avcover = 0

    if sumaccuracy > 0:
        avaccuracy = sumaccuracy/numberofrules
    else:
        avaccuracy = 0

    if sumlift > 0:
        avlift = sumlift/numberofrules
    else:
        avlift = 0

    if sumconditions > 0:
        avconditions = sumconditions/numberofrules
    else:
        avconditions = 0
    
    allscores = [numberofrules,avcover,avaccuracy,avlift,avconditions,sumirrational,num_rule_filter,simplerules] 
    return allscores
        

def belief_one(tails):
    num_belief = 0
    i = 0
    while i < len(tails):
        if tails[i][2] >= 0.5 and tails[i][1] == 'G':
            num_belief = num_belief + 1
        i = i + 1
    if num_belief == 0:
        return False
    else:
        return True
    
def getrationalscore_extension(rules,posscols,relation):
    irrational_score_extension = 0
    rational_identity = rational_extension(rules,relation,posscols)
    if rational_identity == False:
        irrational_score_extension = irrational_score_extension + 1
    return irrational_score_extension
     
'''
True ---> rational
False ---> irrational
'''
def rational_extension(rules,relation,posscols):
    check_para = check_rational_extension(rules, relation,posscols)
    print(check_para)
    if check_para[0] == check_para[1]:
        return True
    else:
        return False
'''
obtain (a,b)
if the rule is rational --> a=b
'''
def check_rational_extension(rule, relation,posscols):
    num_rational_extension = 0
    num_rules = 1
    newtails = genRelation(posscols,relation,rule)
    if rule[2][2] >= 0.5 and rule[2][1] == 'G':
        if belief_one(newtails[0]) or disbelief_one(newtails[1]):
            num_rational_extension = num_rational_extension + 1
    if rule[2][2] <= 0.5 and rule[2][1] == 'LE':
        if belief_one(newtails[1]) or disbelief_one(newtails[0]):
            num_rational_extension = num_rational_extension + 1
    return num_rational_extension, num_rules
                    
            
def disbelief_one(tails):
    num_disbelief = 0
    i = 0
    while i <len(tails):
        if tails[i][2] <= 0.5 and tails[i][1] == 'LE':
            num_disbelief = num_disbelief + 1
        i = i+1
    if num_disbelief == 0:
        return False
    else:
        return True
    
'''
select data from database
'''
def selectdata(database,reqcols):
    selected = []
    for dictionary in database:
        sub = {}
        sub["myid"] = dictionary["myid"] 
        for col in reqcols:
            sub[col] = dictionary[col]
        #print(str(sub))
        selected.append(sub)
    return selected

'''
Deleting rows with '?' 
'''
def improvedata(selecteddata,posscols):
    improveddata = []
    for mydictionary in selecteddata:
        flag = "keep"
        for col in posscols:
            if mydictionary[col] == "?":
                flag = "delete"
        if flag == "keep":
            improveddata.append(mydictionary)
    return improveddata


'''
Delete repeated data
'''
def deduplicate_data(selecteddata,posscols):
    new = []
    i = 0
    for data in selecteddata:
        if notequaldata(data,new,posscols):
            new.append(data)
    return new
'''
Return not equal data
'''
def notequaldata(data,new,posscols):
    for other in new:
        if equalcheck_data(data,other,posscols):
            return False
    return True

'''
Return true if data1 and data2 are the same
'''
def equalcheck_data(data1,data2,posscols):
    countsame = 0
    i = 0
    while i < len(posscols):
        if data1[posscols[i]] == data2[posscols[i]]:
            countsame = countsame + 1
        i = i+1
    if str(countsame) == str(len(posscols)):
        return True
    else:
        return False
            

'''
Transform data into probabilities
'''
def transform(selecteddata,reqcols):
    transformdata = []
    for x in selecteddata:
        y = {}
        y["myid"] = x["myid"]
        for col in reqcols:
            short = col[:2]
            #print("short = "+short)
            if  short == "PO" or short == "cb":
                #print("change7")
                newvalue = change7(x[col])
            elif short == "sy" or short == "sd":
                #print("change8")
                newvalue = change8(x[col])
            elif short == "cj" or short == "rw" or short == "dw":
                #print("change10")
                newvalue = change10(x[col])
            else:
                #print("col = "+str(col)+"\tvalue = "+str(x[col]))
                newvalue = change(x[col])
            y[col] = newvalue
        transformdata.append(y)
        #print(str(y))
    return transformdata

def change(v):
    if v == "1":
        p = 0.1
    elif v == "2":
        p = 0.3
    elif v == "3":
        p = 0.5
    elif v == "4":
        p = 0.7
    elif v == "5":
        p = 0.9
    elif v == "?":
        p = "?"
    return p

def change7(v):
    if v == "1":
        p = 0
    elif v == "2":
        p = 0.1
    elif v == "3":
        p = 0.3
    elif v == "4":
        p = 0.5
    elif v == "5":
        p = 0.7
    elif v == "6":
        p = 0.9
    elif v == "7":
        p = 1.0
    return p      

def change8(v):
    if v == "1":
        p = 0
    elif v == "2":
        p = 0.2
    elif v == "3":
        p = 0.3
    elif v == "4":
        p = 0.4
    elif v == "5":
        p = 0.6
    elif v == "6":
        p = 0.7
    elif v == "7":
        p = 0.8
    elif v == "8":
        p = 1.0
    return p        

        
def change10(v):
    if v == "1":
        p = 0.1
    elif v == "2":
        p = 0.2
    elif v == "3":
        p = 0.3
    elif v == "4":
        p = 0.4
    elif v == "5":
        p = 0.5
    elif v == "6":
        p = 0.6
    elif v == "7":
        p = 0.7
    elif v == "8":
        p = 0.8
    elif v == "9":
        p = 0.9
    elif v == "10":
        p = 1.0
    return p       

'''
split selecteddata into traindata and testdata
'''
def gettraintestsets(selecteddata):
    alldatacount = len(selecteddata)
    requirement = 0.2 * alldatacount
    traindata = []
    testdata = []
    for item in selecteddata: 
        act = random.randrange(10)
        if act < 2 and len(testdata) < requirement:
            testdata.append(item)
        else:
            traindata.append(item)
    return [traindata,testdata]

'''
Combination
'''
def genpowerset(X):
    allsets = [[]]
    for x in X:
        newsets = []
        for s in allsets:
            t = s[:]
            t.append(x)
            newsets.append(t)
        allsets = allsets+newsets
    return allsets

'''
Generate a formula
'''
def genformula(argnames,data):
    head = [argnames[0],"E",data[argnames[0]]]
    tail = ""
    for n in range(1,len(argnames)):
        conjunct = [argnames[n],"E",data[argnames[n]]]
        if n == 1:
            tail = conjunct
        else:
            tail = [conjunct,"AND",tail]
    formula = [tail,"IMPLIES",head]
    return formula

def genformulaset(argnames,dataset):
    formulaset = []
    for data in dataset:
        formula = genformula(argnames,data)
        formulaset.append(formula)
    return formulaset
####################################################
####################################################
####################################################    
# def filtering(rules, posscols,relation):
#     rationalRule = []
#     for rule in rules:
#         if supportCase(relation):
#             if support_rational(rule) == False:
#                 rationalRule.append(rule)
#         if attackCase(relation):
#             if attack_rational(rule)== False:
#                 rationalRule.append(rule)
#         if bipolarCase(relation):
#             if bipolar_rational(rule,posscols,relation) == False:
#                 rationalRule.append(rule)
#     return deduplicate(rationalRule)
def filtering(rules, posscols,relation):
    rationalRule = rules.copy()
    for rule in rules:
        if supportCase(relation):
            if support_rational(rule):
                rationalRule.remove(rule)
        if attackCase(relation):
            if attack_rational(rule):
                rationalRule.remove(rule)
        if bipolarCase(relation):
            if bipolar_rational(rule,posscols,relation):
                rationalRule.remove(rule)
    return rationalRule
    
'''
Filtering rational data for all support ralations situation
irrational data --> True
rational data --> False
'''
def support_rational(rule):
    if non_conclusive(rule) or non_ground(rule):
        return True
    else:
        return False

'''
Check non_conclusive
satisfy non_conclusive --> True
do not satisfy --> False
'''
def non_conclusive(rule):
    head_value  = rule[2][2]
    if head_value < 0.5 and belief_data(rule):
        return True
    else:
        return False
'''
Check non_ground
satisfy non_ground --> True
do not satisfy --> False
'''
def non_ground(rule):
    head_value  = rule[2][2]
    if head_value > 0.5 and disbelief_data(rule):
        return True
    else:
        return False

'''
Filtering rational data for all attack relations situation
irrational data --> True
rational data -->False
'''
def attack_rational(rule):
    if incoherent(rule) or inacceptability(rule):
        return True
    else:
        return False
    
'''
Check inacceptability
satisfy inacceptability --> True
do not satisfy --> False
'''
def inacceptability(rule):
    head_value = rule[2][2]
    if head_value < 0.5 and disbelief_data(rule):
        return True
    else:
        return False

'''
Check whether all of the influencers are disblieved
return True if all of the influencers are disbelieved
'''
def disbelief_data(rule):
    tails = getconjuncts(rule[0])
    num_belief = 0
    i = 0
    while i <len(tails):
        if tails[i][2] < 0.5:
            num_belief = num_belief +1
        i = i+1
    if num_belief == len(tails):
        return True
    else:
        return False
    
'''
Check incoherent
satisfy incoherent --> True
do not satisfy --> False
'''
def incoherent(rule):
    head_value = rule[2][2]
    if head_value > 0.5 and belief_data(rule):
        return True
    else:
        return False

'''
Check whether any one of the influencers is believed
return True if there is at least one argument is believd
'''
def belief_data(rule):
    tails = getconjuncts(rule[0])
    num_belief = 0
    i = 0
    while i < len(tails):
        if tails[i][2] >0.5:
            num_belief = num_belief + 1
        i = i + 1
    if num_belief == 0:
        return False
    else:
        return True

'''
Filtering rational data for situations when attackers and supporters both exists
irrational data --> True
rational data -->False
'''
def bipolar_rational(rule,posscols,relation):
    if gen_inconclusive(rule,posscols,relation) or gen_incoherent(rule,posscols,relation):
        return True
    else:
        return False
'''
Check gen_incoherent
satisfy gen_incoherent --> True
do not satisfy --> False
'''
def gen_incoherent(rule,posscols,relation):
    head_value = rule[2][2]
    newtails = genRelation(posscols,relation,rule)
    if newtails[0] != [] and newtails[1] != []:
        if head_value > 0.5 and disbelief_biData(newtails[0]) and belief_biData(newtails[1]):
            return True
        else:
            return False
    if newtails[0] == []:
        if head_value > 0.5 and belief_biData(newtails[1]):
            return True
        else:
            return False
    if newtails[1] == []:
        if head_value > 0.5 and disbelief_biData(newtails[0]):
            return True
        else:
            return False
    
    
'''
Check gen_inconclusive
satisfy gen_inconclusive --> True
do not satisfy --> False
'''
def gen_inconclusive(rule,posscols,relation):
    head_value = rule[2][2]
    newtails = genRelation(posscols,relation,rule)
    if newtails[0] != [] and newtails[1] != []:
        if head_value <= 0.5 and disbelief_biData(newtails[1]) and belief_biData(newtails[0]):
            return True
        else:
            return False
    if newtails[0] == []:
        if head_value <= 0.5 and disbelief_biData(newtails[1]):
            return True
        else:
            return False
    if newtails[1] == []:
        if head_value <= 0.5 and belief_biData(newtails[0]):
            return True
        else:
            return False
        
     
'''
Check whether all of the influencers are disblieved for bipolar situation
return True if all of the influencers are disbelieved
''' 
def disbelief_biData(tails):
    num_belief = 0
    i = 0
    while i <len(tails):
        if tails[i][2] <= 0.5:
            num_belief = num_belief +1
        i = i+1
    if num_belief == len(tails):
        return True
    else:
        return False
    
'''
Check whether any one of the influencers is believed for bipolar situation
return True if there is at least one argument is believd
'''
def belief_biData(tails):
    num_belief = 0
    i = 0
    while i < len(tails):
        if tails[i][2] > 0.5:
            num_belief = num_belief + 1
        i = i + 1
    if num_belief == 0:
        return False
    else:
        return True


'''
Generate a set of supporters and a set of attackers out of the posscols 
'''
def genRelation(posscols,relation,rule):
    supp_set = []
    attack_set = []
    tails = getconjuncts(rule[0])
    i = 0
    while i < len(tails):
        if relation[posscols.index(tails[i][0])] == 1:
            supp_set.append(tails[i])
        if relation[posscols.index(tails[i][0])] == 0:
            attack_set.append(tails[i])
        i = i+1
    return supp_set,attack_set


'''
Check whether the situation is support for all relations
support --> True
'''
def supportCase(relation):
    countsupport = 0
    for rel in relation:
        if rel == 1:
            countsupport = countsupport + 1
    if str(countsupport) == str(len(relation)):
        return True
    else:
        return False
    
'''
Check whether the situation is attack for all relations
attack --> True
'''
def attackCase(relation):
    countattack = 0
    for rel in relation:
        if rel == 0:
            countattack = countattack + 1
    if str(countattack) == str(len(relation)):
        return True
    else:
        return False  
'''
Check whetehr the situation is bipolar
bipolar --> True
'''
def bipolarCase(relation):
    countsame = 0
    i = 0
    while i+1 < len(relation):
        if relation[i] == relation[i+1]:
            countsame = countsame + 1
        i = i+1
    if str(countsame) == str(len(relation)-1):
        return False
    else:
        return True 

def getconjuncts(tail):
    if tail[1] == "AND":
        return [tail[0]] + getconjuncts(tail[2]) 
    else:
        return [tail]
####################################################
####################################################
####################################################
'''
generate a set of pi s.t. a<=pi<=0.5
'''
def smallerSet(a,P):
    new_P = []
    i = 0
    while i < len(P):
        if P[i]<=0.5 and P[i]>= a:
            new_P.append(P[i])
        else:
            new_P = new_P
        i = i + 1
    return new_P

'''
generate a set of pi s.t. 0.5<=pi<=a
'''        
def largerSet(a,P):
    new_P = []
    i = 0
    while i < len(P):
        if P[i]>=0.5 and P[i]<= a:
            new_P.append(P[i])
        else:
            new_P = new_P
        i = i + 1
    return new_P

'''
Closest(d,\Pi)
'''
def closest(a,P):
    new = []
    i = 0
    if a <= 0.5:
        while i < len(smallerSet(a,P)):
            if len(new) == 0:
                new = [smallerSet(a,P)[i]]
            else:
                if abs(smallerSet(a,P)[i]-a) < abs(new[0] - a):
                    new = [smallerSet(a,P)[i]]
                else:
                    new = new
            i = i + 1
    if a > 0.5:
        while i < len(largerSet(a,P)):
            if len(new) == 0:
                new = [largerSet(a,P)[i]]
            else:
                if abs(largerSet(a,P)[i]-a) < abs(new[0] - a):
                    new = [largerSet(a,P)[i]]
                else:
                    new = new
            i = i + 1
    return new
    


'''
change the real value to the constraint value
'''
def improveformulaset(rules,constraintset):
    generalrules = headgeneralize(rules,constraintset)  #generalize new rules with new head
    moregeneralrules = tailgeneralize(generalrules,constraintset) # 
    return deduplicate(moregeneralrules)
'''
Add 'And' 
'''
def formconjunction(conjuncts):
    if len(conjuncts) == 1:
        return conjuncts[0]
    else:
        return [conjuncts[0],"AND",formconjunction(conjuncts[1:])]
    
    
    
'''
get rid of AND
e.g. 'a>0.5', 'and', 'b<0.3' to 'a>0.5', 'b<0.3'
'''  
def getconjuncts(tail):
    if tail[1] == "AND":
        return [tail[0]] + getconjuncts(tail[2]) 
    else:
        return [tail]


    
def tailgeneralize(rules,constraintset):
    finalrules = []
    for formula in rules:
        newrules = []
        newrule = tailgen(formula,constraintset)
        newrules.append(newrule)
        for a in newrules[0]:
            finalrules.append(a)
    return finalrules  

        
def tail_constraint(formula,constraintset):
    tail=getconjuncts(formula[0])
    newtail = []
    i = 0
    if len(constraintset) == 1 and constraintset[0] == 0.5:
        while i <len(tail):
            set_1 = []
            for t in constraintset:
                newset = []
                if tail[i][2] > t:
                    newset.append(tail[i][0])
                    newset.append('G')
                    newset.append(t)
                elif tail[i][2] <= t:
                    newset.append(tail[i][0])
                    newset.append('LE')
                    newset.append(t)
                set_1.append(newset)
            newtail.append(set_1)     
            i = i+1
        
    else:
        while i <len(tail):
            set_1 = []
            for t in closest(tail[i][2],constraintset):
                newset = []
                if tail[i][2] > t:
                    newset.append(tail[i][0])
                    newset.append('G')
                    newset.append(t)
                elif tail[i][2] < t:
                    newset.append(tail[i][0])
                    newset.append('L')
                    newset.append(t)
                elif tail[i][2] == t:
                    if tail[i][2]>0.5:
                        newset.append(tail[i][0])
                        newset.append('GE')
                        newset.append(t)
                    elif tail[i][2]<=0.5:
                        newset.append(tail[i][0])
                        newset.append('LE')
                        newset.append(t)
                set_1.append(newset)
            newtail.append(set_1)     
            i = i+1
    return newtail

'''
Combination for tail
'''
def combination(formula,constraintset):
    lists = tail_constraint(formula,constraintset)
    result = [[]]
    for list_pool in lists:
        lis = []
        for i in result:
            for j in list_pool:
                lis.append( i +[j])
        result = lis
    return result

'''
translate tails into formulas 
'''

def tailgen(formula,constraintset):
    set_tail = combination(formula,constraintset)
    newformula = []
    i = 0
    while i < len(set_tail):
        conjoined = formconjunction(set_tail[i])
        formula[0] = conjoined
        newformula.append(formula.copy())
        i = i+1
    return newformula

'''
Generalize newrules with new head
'''

def headgeneralize(rules, constraintset):
    finalrules = []
    for formula in rules:
        newrules = []
        newrule = headgen(formula, constraintset)
        newrules.append(newrule)
        for a in newrules[0]:
            finalrules.append(a)
    return finalrules
'''
Change the rule by comparing the head with the restricted values
''' 

def headgen(formula,constraintset):
    head = formula[2]
    allformula = []
    if len(constraintset) == 1 and constraintset[0] == 0.5:
        for constraint in constraintset:
            newformula = []
            newhead = []
            newhead.append(head[0])
            if (head[1] == "E") and float(head[2])> constraint:
                newhead.append("G")
            if (head[1] == "L" or head[1] == "E") and float(head[2])<=constraint:
                newhead.append("LE")
            newhead.append(constraint)
            
            newformula.append(formula[0])
            newformula.append(formula[1])
            newformula.append(newhead)
            allformula.append(newformula)
        
    else:
        for constraint in closest(head[2],constraintset):
            newformula = []
            newhead = []
            newhead.append(head[0])
            if (head[1] == "E") and float(head[2])> constraint:
                newhead.append("G")
            elif (head[1] == "L" or head[1] == "E") and float(head[2])< constraint:
                newhead.append("L")
            elif (head[1] == "E") and float(head[2]) == constraint:
                if head[2] > 0.5:
                    newhead.append("GE")
                elif head[2] <= 0.5:
                    newhead.append("LE")
            newhead.append(constraint)
            newformula.append(formula[0])
            newformula.append(formula[1])
            newformula.append(newhead)
            allformula.append(newformula)
    return allformula    



'''
return formulae in formulae that are not the same
'''
def deduplicate(formulae):
    new = []
    for formula in formulae:
        if notequalmember(formula,new):
            new.append(formula)
    return new

'''
return not equal formula
'''
def notequalmember(formula,new):
    for other in new:
        if equalcheck(formula,other):
            return False
    return True


'''
Check whether rule1 and rule2 are the same
'''    
def equalcheck(form1,form2):
    if str(form1) == str(form2):
        return True
    else:
        return False

####################################################
####################################################
####################################################
'''
Generate best rules out of a set of rules
'''
def choosebest(reqcols,dataset,rules):
    best = []
    for rule in rules:
        scores = firescore(reqcols,dataset,rule)
        
        correct = scores[0]
        incorrect = scores[1]
        nocoverage = scores[2]
        coverage = len(dataset) - nocoverage #num of rules that are fired
    
        goodcover = coverageratio(dataset,rule,coverage) #Check whether Support(R,D) obeys BestRules
        goodcorrect = correctratio(correct,incorrect) #Check whether Confident(R,D) obeys BestRules
        liftscore = getliftscore(reqcols,dataset,rule) #Check whether Lift(R,D) > 1
        
        if goodcover and goodcorrect and liftscore >1:
        # if goodcover >0.5 and goodcorrect >0.5 and liftscore >1:
            best.append(rule)
    return best

'''
Check whether Support(R,D) obeys BestRules
True --> Obeys
'''
def coverageratio(dataset,rule,coverage):
    coverratio = float(coverage)/len(dataset) #Calculate Support(R,D)
    if coverratio > 0.4:
        return True
    else:
        return False

'''
Check whether Confidence(R,D) obeys BestRules
True --> Obeys
'''
def correctratio(correct,incorrect):
    correctratio = float(correct)/(incorrect+correct)
    if correctratio > 0.8:
        return True
    else:
        return False

'''
return Lift(R,D)
'''
def getliftscore(argnames,dataset,rule):
    f = numberfirings(argnames,dataset,rule)
    e = numbererrorfree(argnames,dataset,rule)
    g = correctfirecount(argnames,dataset,rule)
    n = len(dataset)
    lift = ((g * n ) / (e * f))
    return lift
        
'''
return the num of correct rules
'''
def correctfirecount(argnames,dataset,formula):
    count = 0
    for data in dataset:
        reply = satformula(argnames,data,formula)
        if  reply == "Y":
            count = count + 1
    return count

'''
return the num of fired rules
'''
def numberfirings(argnames,dataset,rule):
    ftuple = firescore(argnames,dataset,rule)
    return ftuple[0] + ftuple[1]

'''
return number of agreed rules
'''
def numbererrorfree(argnames,dataset,formula):
    count = 0
    for data in dataset:
        error = errorhead(argnames,data,formula)
        if error == 0:
            count = count + 1
    return count

'''
Decide whether a rule agrees
agrees --> 0
'''
def errorhead(argnames,data,formula):
    head = formula[2]
    if data[head[0]] == "?" or head[2] == "?":
        error = 0
    else:
        if head[1] == "E":
            error = diff(float(data[head[0]]),float(head[2]))
        elif head[1] == "G" or head[1] == "GE":
            error = below(float(data[head[0]]),head[2])
        elif head[1] == "L" or head[1] == "LE":
            error = above(float(data[head[0]]),head[2])
    return error        

def diff(x,y):
    if x == y:
        return 0
    elif x > y:
        return x - y
    else:
        return y - x

def below(x,y):
    if y > x:
        return y - x
    else:
        return 0
def above(x,y):
    if x > y:
        return x-y
    else:
        return 0
    

'''
correct(Y): number of rules that are correct
incorrect(N): number of rules that are fired but not agrees:
nofire(NA): number of rules that are not fired
'''
def firescore(argnames,dataset,formula):    
    correct = 0
    incorrect = 0
    nofire = 0
    for data in dataset:
        reply = satformula(argnames,data,formula)
        if  reply == "Y":
            correct = correct + 1
        elif  reply == "N":
            incorrect = incorrect + 1
        elif  reply == "NA":
            nofire = nofire + 1
    return [correct,incorrect,nofire]

'''
correct: Y
fired not agrees: N 
not fired: NA
'''
def satformula(argnames,data,formula):
    if sattail(argnames,data,formula[0]):
        if sathead(argnames,data,formula[2]):
            return "Y"
        else:
            return "N"
    else:
        return "NA"

'''
Decide agrees (head)
agrees --> True
not agrees --> False
'''
def sathead(argnames,data,head):
    if nonsatatom(argnames,data,head):
        return False
    else:
        return True

'''
Decide fired (tails)
fired --> True
not fired --> False
'''
def sattail(argnames,data,tail):
    conjuncts = getconjuncts(tail)
    for atom in conjuncts:
        if nonsatatom(argnames,data,atom):
            return False
    return True
        

'''
fired or agrees --> False
not fired or not agrees ---> True
'''
def nonsatatom(argnames,data,atom):
    if atom[1] == "E":
        if float(data[atom[0]]) == atom[2]:
            return False
        else:
            return True
    if atom[1] == "G":
        if float(data[atom[0]]) > atom[2]:
            return False
        else:
            return True
    if atom[1] == "GE":
        if float(data[atom[0]]) >= atom[2]:
            return False
        else:
            return True
    if atom[1] == "L":
        if float(data[atom[0]]) < atom[2]:
            return False
        else:
            return True
    if atom[1] == "LE":
        if float(data[atom[0]]) <= atom[2]:
            return False
        else:
            return True

####################################################
####################################################
####################################################
'''
Return a set of simplest rules
'''
def choosesimplest(rules):
    simplest = []
    for rule in rules:
        if mincondition(rule,rules):
            simplest.append(rule)
    return simplest
            
'''
Return the simpler rule with the same influence target(head)
'''
def mincondition(rule,rules):
    for other in rules:
        if rule[2] == other[2] and set(atoms(other[0])) < set(atoms(rule[0])):        
            return False
    return True

'''
return influencers
i.e. 'PU3'
''' 
def atoms(con):
    if con[1] != "AND":
        return [con[0]]
    else:
        return atoms(con[0])+atoms(con[2])
    
    
####################################################
####################################################
####################################################
'''
Calculate the Support(R,D) and Confident(R,D)
'''
def getrulequality(reqcols,dataset,rule):
    scores = firescore(reqcols,dataset,rule)
    correct = scores[0]
    incorrect = scores[1]
    nocoverage = scores[2]
    coverage = len(dataset) - nocoverage
    coverratio = float(coverage)/len(dataset)
    correctratio = float(correct)/(incorrect+correct)
    return [coverratio,correctratio]

'''
Return the num of conditions for the rule
'''

def getnumberofconditions(rule):
    rulestring = str(rule)
    andcount = rulestring.count("AND")
    return andcount+1



def satcount(argnames,dataset,formula):
    count = 0
    for data in dataset:
        reply = satformula(argnames,data,formula)
        if  reply == "Y" or reply == "NA":
            count = count + 1
    return count

def errorformula(argnames,data,formula):
    error = 0
    if sattail(argnames,data,formula[0]):
        head = formula[2]
        if data[head[0]] == "?" or head[2] == "?":
            error = 0
        else:
            if head[1] == "E":
                error = diff(float(data[head[0]]),float(head[2]))
            elif head[1] == "G" or head[1] == "GE":
                error = below(float(data[head[0]]),head[2])
            elif head[1] == "L" or head[1] == "LE":
                error = above(float(data[head[0]]),head[2])
    return error

def sumerror(argnames,dataset,formula):
    sumerror = 0
    for data in dataset:
        error = errorformula(argnames,data,formula)
        sumerror = error + sumerror
    return sumerror

def gentails(rule):
    poss_set = []
    tails = getconjuncts(rule[0])
    i = 0
    while i < len(tails):
        poss_set.append(tails[i][0])
        i = i+1
    return poss_set

def genpositions(rule,posscols):
    positions = []
    poss = gentails(rule)
    i = 0
    while i < len(poss):
        positions.append(posscols.index(poss[i]))
        i = i + 1
    return positions

'''
return relations for tails in a rule
'''
def genrelations(rule,posscols,relation):
    rel = []
    positions = genpositions(rule,posscols)
    
    i = 0
    while i < len(positions):
        rel.append(relation[positions[i]])
        i = i + 1
    return rel


def getrationalscore(rule, posscols,relation):
    relation_rule = genrelations(rule,posscols,relation)
    irrational = 0
    if supportCase(relation_rule):
            if supportrational(rule):
                irrational = irrational + 1
    if attackCase(relation_rule):
            if attackrational(rule):
                irrational = irrational + 1
    if bipolarCase(relation_rule):
            if birational(rule,posscols,relation):
                irrational = irrational + 1
    return irrational
'''
True --> The rule is irrational for support case for test
'''
def supportrational(rule):
    if check_nonconclusive(rule) or check_nongrounded(rule):
        return True
    else:
        return False
    
'''
True --> The rule is irrational for attack case for test
'''

def attackrational(rule):
    if check_incoherent(rule) or check_nonreinstated(rule):
        return True
    else:
        return False
    
'''
True --> The rule is irrational for bipolar case for test
'''
def birational(rule,posscols,relation):
    if check_gen_inconclusive(rule,posscols,relation) or check_gen_incoherent(rule,posscols,relation):
        return True
    else:
        return False



def check_gen_inconclusive(rule,posscols,relation):
    newtails = genRelation(posscols,relation,rule)
    if belief_head(rule) == False and all_disbelief_biData(newtails[1]) and one_belief_biData(newtails[0]):
        return True
    else:
        return False

def check_gen_incoherent(rule,posscols,relation):
    newtails = genRelation(posscols,relation,rule)
    if belief_head(rule) and all_disbelief_biData(newtails[0]) and one_belief_biData(newtails[1]):
        return True
    else:
        return False

'''
True --> satisfy non-reinstated for test
False --> do not satisfy non-reinstated for test
'''
def check_nonreinstated(rule):
    if all_disbelief_tail(rule) and belief_head(rule) == False:
        return True
    else:
        return False

'''
True --> satisfy incoherent for test
False --> do not satisfy incoherent for test
'''
def check_incoherent(rule):
    if one_belief_tail(rule) and belief_head(rule):
        return True
    else:
        return False
      
'''
True --> satisfy non-grounded for test
False --> do not satisfy non-grounded for test
'''
def check_nongrounded(rule):
    if all_disbelief_tail(rule) and belief_head(rule):
        return True
    else:
        return False

'''
True --> satisfy non-conclusive for test
False --> do not satisfy non-conclusive for test
'''
def check_nonconclusive(rule):
    if belief_head(rule) == False and one_belief_tail(rule):
        return True
    else:
        return False


'''
False --> Head disbelieve for test
True --> Head believe for test
'''
def belief_head(rule):
    if rule[2][2] <= 0.5 and rule[2][1] == 'LE':
        return False
    if rule[2][2] >= 0.5 and rule[2][1] == 'G':
        return True

'''
True --> Any one of the tail is believed (outcome rules) for test
False --> all tails are not believed for test
'''
def one_belief_tail(rule):
    tails = getconjuncts(rule[0])
    num_belief = 0
    i = 0
    while i < len(tails):
        if tails[i][2] >= 0.5 and tails[i][1] == 'G':
            num_belief = num_belief + 1
        i = i + 1
    if num_belief == 0:
        return False
    else:
        return True

'''
True --> All tails are disbelieved for test
False -- not tails arguments are disbelieved for test
'''
def all_disbelief_tail(rule):
    tails = getconjuncts(rule[0])
    num_belief = 0
    i = 0
    while i<len(tails):
        if tails[i][2] <= 0.5 and tails[i][1] == 'LE':
            num_belief = num_belief + 1
        i = i + 1
    if num_belief == len(tails):
        return True
    else:
        return False


'''
Check whether all of the influencers are disblieved for bipolar situation for test
return True if all of the influencers are disbelieved for test
''' 
def all_disbelief_biData(tails):
    num_belief = 0
    i = 0
    while i <len(tails):
        if tails[i][2] <= 0.5 and tails[i][1] == 'LE':
            num_belief = num_belief +1
        i = i+1
    if num_belief == len(tails):
        return True
    else:
        return False

'''
Check whether any one of the influencers is believed for bipolar situation for test
return True if there is at least one argument is believd for test
'''
def one_belief_biData(tails):
    num_belief = 0
    i = 0
    while i < len(tails):
        if tails[i][2] >= 0.5 and tails[i][1] == 'G':
            num_belief = num_belief + 1
        i = i + 1
    if num_belief == 0:
        return False
    else:
        return True


if __name__ == "__main__":
    
    
    # filename = "politicalattitudes.csv"
    # dataname = "italy"
    # posscols = ["sys4","sys7","sys8","POP5"]
    # possheads = ["dw6"]
    # constraintset = [0.5]
    # relation = [0,1,0,1]
    
    filename = "politicalattitudes.csv"
    dataname = "italy"
    posscols = ["sys1","sys2","sys4","sys5","sys6","sys7","sys8"]
    possheads = ["sys3"]
    constraintset = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    relation = [0,0,0,0,0,1,0]
 

    # filename = "wiki4HE.csv"
    # dataname = "spain"
    # posscols = ["SA2","Use3","Use1","Use4","SA1"]
    # possheads = ["Use2"]
    # relation = [1,1,1,1,1,1,1,1,1,1]
    # constraintset = [0.5]
    
    # filename = "wiki4HE.csv"
    # dataname = "spain"
    # posscols = ["SA2","Use3","Use1","Use4"]
    # possheads = ["Use2"]
    # relation = [1,1,1,1]
    # constraintset = [0.5]
        
    allscores = genandtest(filename, posscols + possheads, possheads, dataname,constraintset,relation)   
   