from ortools.sat.python.cp_model import FEASIBLE,OPTIMAL,CpSolver,CpModel
import numpy as np
from sweeper.rules import *
from rich.progress import track
import time

UNREVEAL=0
MINE=1
HIDDENCLUE=2

solver=CpSolver()
model:CpModel
n:int
Mine:np.ndarray

def init(input_n,GeneralRules:list[str]):
    global Mine,n,model,solver
    n=input_n
    model=CpModel()
    Mine=np.array([[model.NewBoolVar(f'mine_{i},{j}') for j in range(n)] for i in range(n)])
    for i in GeneralRules:
        eval(f'rule{i}')(model,Mine,n)

def update(x,y,val:int|tuple[str,any]):# get new clue
    if val==UNREVEAL:
        pass
    elif val==MINE:
        model.Add(Mine[x,y]==1)
    elif val==HIDDENCLUE:
        model.Add(Mine[x,y]==0)
    else:
        model.Add(Mine[x,y]==0)
        eval(f'rule{val[0]}')(model,Mine,n,x,y,val[1])

def updateMineCount(num):# total mine count
    ruleNum(model,Mine,n,num)

def solve(enable_log:bool=False):
    status=solver.solve(model)
    if status == FEASIBLE or status == OPTIMAL:
        if enable_log:
            print('Satisfiable')
            for row in Mine:
                for i in row:
                    print('x' if solver.value(i) else 'o',end='')
                print()
        return True
    else:
        if enable_log:
            print('Unsatisfiable')
        return False

def sweep(Unreveal:np.ndarray)->list[tuple[int,int,bool]]:
    res=[]
    pos=[]
    for i in range(n):
        for j in range(n):
            if Unreveal[i,j]:
                sub=1-Unreveal[max(i-1,0):min(i+2,n),max(j-1,0):min(j+2,n)]
                pos.append([sub.sum(),(i,j)])
    pos.sort(key=lambda x:x[0],reverse=True)
    pos=list(map(lambda x:x[1],pos))
    # cnt=time.time()+2
    for i,j in track(pos,description="[red]Sweeping..."):
        model.AddAssumption(Mine[i,j])
        if not solve():
            res.append((i,j,False))
        model.ClearAssumptions()
        model.AddAssumption(Mine[i,j].Not())
        if not solve():
            res.append((i,j,True))
        model.ClearAssumptions()
        # if time.time()>cnt and len(res)!=0:
        #     break
    return res

if __name__=='__main__':
    init(5,[])
    updateMineCount(10)
    qwq=np.ones((5,5),dtype=bool)
    while True:
        while True:
            res=sweep(qwq)
            if len(res)==0:
                break
            for x,y,w in res:
                qwq[x,y]=False
                if w:
                    print(f"{x},{y} mine")
                else:
                    print(f"{x},{y} safe")
        x,y,z=list(map(lambda x:int(x),input().split()))
        if z==-1:
            update(x,y,HIDDENCLUE)
        else:
            update(x,y,('P',z))
            qwq[x,y]=False