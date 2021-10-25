import sys
import pandas as pd


def compare(df1, df2):
    flag=False
    if len(df1)!=len(df2):
        flag=True
        print('Files have different length!. File1 length is {}, and File2 length is {}'.format(len(df1), len(df2)))
        return
    if set(df1.columns.tolist())!=set(df2.columns.tolist()):
        flag=True
        print('Files do not have the same column names!')
        return
    column_names = df1.columns.tolist()
    for name in column_names:
        list1 = [str(entry).strip() for entry in df1[name].tolist()]
        list2 = [str(entry).strip() for entry in df2[name].tolist()]
        for idx, (el1, el2) in enumerate(zip(list1, list2)):
            if el1!=el2:
                flag=True
                print('Column: {}, Line: {}, File1: {}, File2: {}'.format(name, idx+2, el1, el2))
    if flag==False:
        print('The files are the same!')




if __name__ == '__main__':

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    compare(df1, df2)
