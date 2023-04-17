from fileinput import filename
import spaintablemanager
import italytablemanager
import random

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
                allbestrules = allbestrules + newrules #Generate all rational rules
    simplebestrules = choosesimplest(allbestrules) #Return a set of simplest rational rules
    print(simplebestrules)


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
'''
Filtering rational rules
'''
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

if __name__ == "__main__":
    
    filename = "politicalattitudes.csv"
    dataname = "italy"
    posscols = ["dw2","dw5","dw3"]
    possheads = ["dw6"]
    constraintset = [0.5]
    relation = [1,0,1]
    
    allscores = genandtest(filename, posscols + possheads, possheads, dataname,constraintset,relation)   
   