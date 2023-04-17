
import pathlib

def validation_for_genandtest(filename,posscols,possheads,dataname,constraintset,relation):
    """
    Function to validate n in Glacier and GlacierCollection methods
    """
    my_file = pathlib.Path(filename)
    if not my_file.exists():
        raise ValueError("file not exists")

    # validation of posscols
    if not isinstance(posscols, list):
        raise TypeError("posscols should be a list")

    if len(posscols)<2:
        raise ValueError("posscols should be of length >= 2")

    # validation of possheads
    if not isinstance(possheads, list):
        raise TypeError("possheads should be a list")

    if len(possheads)!=1:
        raise ValueError("possheads should be of length 1")

    # validation for dataname
    data_file = pathlib.Path(dataname)
    if not data_file.exists():
        raise ValueError("dataname file not exists")

    # # validation for constraintset
    validation_for_constraintse(constraintset)\

    #relation
    if not isinstance(relation, list):
        raise TypeError("relation should be a list")

    if len(relation)!=len(posscols)-1:
        raise ValueError("the length of relation or posscols is not ture")

    for i in relation:
        if i not in [0,1]:
            raise ValueError("the value of relation is not ture")



def validation_for_constraintse(constraintset):
    if not isinstance(constraintset, set):
        raise TypeError("constraintset should be a set")

    for m in constraintset:
        for n in constraintset:
            if m+n <=1 and m+n not in constraintset:
                raise ValueError("the constraintset is not available")
            if m-n >=0 and m-n not in constraintset:
                raise ValueError("2-the constraintset is not available")

    if 1 not in constraintset or 0 not in constraintset:
        raise ValueError("constraintset should contain 0 and 1")





constraintse={0,0.25,0.5,0.75,1}
validation_for_genandtest("wiki4HE.csv",[1,2],[1],"wiki4HE.csv",constraintse,[1])

# constraintse={0,0.25,0.5,0.75,1}
# validation_for_constraintse(constraintse)


