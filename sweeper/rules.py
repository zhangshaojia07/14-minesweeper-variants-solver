import numpy as np
from ortools.sat.python.cp_model import CpModel,IntVar
from sweeper.util import *

################################ 雷数
def ruleNum(model:CpModel,Mine,n,num):
    model.Add(Mine.sum()==num)

################################ General规则
def ruleQ(model:CpModel,Mine,n):
    for i in range(n-1):
        for j in range(n-1):
            model.AddBoolOr(Mine[i+ii,j+jj] for jj in range(2) for ii in range(2))

def ruleC(model:CpModel,Mine,n):
# 每个位置开个变量 [0,map_size)
# 至多一个零标记,有零标记才能值为 0
# 每个位置要么不是雷,要么是0,要么相邻有一个标记是自己-1(或者小于也行)
    Zero=np.array([[model.NewBoolVar(f'zero_{i},{j}') for j in range(n)] for i in range(n)])
    model.Add(Zero.sum()==1)
    Tag=np.array([[model.NewIntVar(0,n*n-1,f'tag_{i},{j}') for j in range(n)] for i in range(n)])
    for i in range(n):
        for j in range(n):
            AddSelector(model,Tag[i,j]>0,Tag[i,j]==0,Zero[i,j])
            Expr=[[Mine[i,j]==0],[Zero[i,j]==1]]
            for k in Get8(n,i,j):
                if k:
                    Expr.append([Mine[*k]==1,Tag[k]==Tag[i,j]-1])
            AddOrAndExpr(model,Expr)

def ruleS(model:CpModel,Mine,n):
# 先保证雷四连通
# 每个雷度数<=2
# 要有度数=1的雷(cnt必然=2)
    Zero=np.array([[model.NewBoolVar(f'zero_{i},{j}') for j in range(n)] for i in range(n)])
    model.Add(Zero.sum()==1)
    Tag=np.array([[model.NewIntVar(0,n*n-1,f'tag_{i},{j}') for j in range(n)] for i in range(n)])
    for i in range(n):
        for j in range(n):
            AddSelector(model,Tag[i,j]>0,Tag[i,j]==0,Zero[i,j])
            Expr=[[Mine[i,j]==0],[Zero[i,j]==1]]
            for k in Get4(n,i,j):
                if k:
                    Expr.append([Mine[*k]==1,Tag[k]==Tag[i,j]-1])
            AddOrAndExpr(model,Expr)
    
    Deg1=np.array([[model.NewBoolVar(f'zero_{i},{j}') for j in range(n)] for i in range(n)])
    for i in range(n):
        for j in range(n):
            Neighbors=[Mine[*k] for k in Get4(n,i,j) if k]
            model.Add(sum(Neighbors)<=2).OnlyEnforceIf(Mine[i,j])
            model.AddImplication(Deg1[i,j],Mine[i,j])
            model.Add(sum(Neighbors)==1).OnlyEnforceIf(Deg1[i,j])
    model.Add(Deg1.sum()==1)

def ruleO(model:CpModel,Mine,n):
# 保证非雷四连通
# 雷和外部四连通
    Zero=np.array([[model.NewBoolVar(f'zero_{i},{j}') for j in range(n)] for i in range(n)])
    model.Add(Zero.sum()==1)
    Tag=np.array([[model.NewIntVar(0,n*n-1,f'tag_{i},{j}') for j in range(n)] for i in range(n)])
    for i in range(n):
        for j in range(n):
            AddSelector(model,Tag[i,j]>0,Tag[i,j]==0,Zero[i,j])
            Expr=[[Mine[i,j]==1],[Zero[i,j]==1]]
            for k in Get4(n,i,j):
                if k:
                    Expr.append([Mine[*k]==0,Tag[k]==Tag[i,j]-1])
            AddOrAndExpr(model,Expr)
    
    Tag=np.array([[model.NewIntVar(0,n*n-1,f'tag_{i},{j}') for j in range(n)] for i in range(n)])
    for i in range(n):
        for j in range(n):
            if i!=0 and i!=n-1 and j!=0 and j!=n-1:
                Expr=[[Mine[i,j]==0]]
                for k in Get4(n,i,j):
                    if k:
                        Expr.append([Mine[*k]==1,Tag[k]==Tag[i,j]-1])
                AddOrAndExpr(model,Expr)

def ruleT(model:CpModel,Mine,n):
    for i in range(n-2):
        for j in range(n-2):
            model.AddBoolOr(Mine[i+k,j+k].Not() for k in range(3))
            model.AddBoolOr(Mine[i+k,j+2-k].Not() for k in range(3))
    for i in range(n):
        for j in range(n-2):
            model.AddBoolOr(Mine[i,j+k].Not() for k in range(3))
    for i in range(n-2):
        for j in range(n):
            model.AddBoolOr(Mine[i+k,j].Not() for k in range(3))

def ruleB(model:CpModel,Mine,n):
    row_sum=[]
    for i in range(n):
        row_sum.append(sum(Mine[i,j] for j in range(n)))
    col_sum=[]
    for j in range(n):
        col_sum.append(sum(Mine[i,j] for i in range(n)))
    for i in range(n):
        model.Add(row_sum[i]==row_sum[1])
        model.Add(col_sum[i]==row_sum[1])

def ruleD(model:CpModel,Mine,n):
# 每个雷的度为1
    for i in range(n):
        for j in range(n):
            Neighbors=[Mine[*k] for k in Get4(n,i,j) if k]
            model.Add(sum(Neighbors)==1).OnlyEnforceIf(Mine[i,j])

def ruleDapo(model:CpModel,Mine,n):
# 对角不能有
# 横竖五连不能有
    for i in range(n-1):
        for j in range(n-1):
            model.AddBoolOr(Mine[i,j].Not(),Mine[i+1,j+1].Not())
            model.AddBoolOr(Mine[i,j+1].Not(),Mine[i+1,j].Not())
    for i in range(n):
        for j in range(n-4):
            model.AddBoolOr(Mine[i,j+k].Not() for k in range(5))
    for i in range(n-4):
        for j in range(n):
            model.AddBoolOr(Mine[i+k,j].Not() for k in range(5))

################################ Local规则
#################### (注意:这里不约束x,y位置为非雷)
def ruleV(model:CpModel,Mine,n,x,y,clue:int):
    Neighbors=[Mine[*i] for i in Get8(n,x,y) if i]
    model.Add(sum(Neighbors)==clue)

def ruleM(model:CpModel,Mine,n,x,y,clue:int):
    Neighbors=[Mine[*i]*(2 if IsDye(*i) else 1) for i in Get8(n,x,y) if i]
    model.Add(sum(Neighbors)==clue)

def ruleN(model:CpModel,Mine,n,x,y,clue:int):
    Neighbors=[Mine[*i]*(-1 if IsDye(*i) else 1) for i in Get8(n,x,y) if i]
    model.AddAbsEquality(clue,sum(Neighbors))
    # AddOrAndExpr(model,[[sum(Neighbors)==clue],[sum(Neighbors)==-clue]])

def ruleL(model:CpModel,Mine,n,x,y,clue:int):
    Neighbors=[Mine[*i] for i in Get8(n,x,y) if i]
    AddOrAndExpr(model,[[sum(Neighbors)==clue-1],[sum(Neighbors)==clue+1]])
    
def ruleX(model:CpModel,Mine,n,x,y,clue:int):
    Neighbors=[]
    for i,j in [(-1,0),(0,1),(1,0),(0,-1),(-2,0),(0,2),(2,0),(0,-2)]:
        i+=x
        j+=y
        if not (i<0 or i>=n or j<0 or j>=n):
            Neighbors.append(Mine[i,j])
    model.Add(sum(Neighbors)==clue)

# W W' P:
# 对每个标记 2^8 枚举合法情况(别忘了边界的mask)
# 然后用提供的API导入即可
def BitsToNpArray(x:int):
    res=[]
    for i in range(8):
        res.append((x>>i)&1)
    return np.array(res,dtype=bool)

def RunLengthEncoding(x:int)->list[int]:
    y=BitsToNpArray(x)
    z=0
    while z<8 and y[z]:
        z+=1
    if z==8:
        return [8]
    y=np.hstack([y[z:],y[:z]])
    res=[]
    z=0
    for i in range(8+1):
        if i<8 and y[i]:
            z+=1
        elif z:
            res.append(z)
            z=0
    return res

def CyclicEqual(x:list[int],y:list[int]):
    for i in range(len(x)):
        if x[i:]+x[:i]==y:
            return True
    return False   

def ruleP(model:CpModel,Mine,n,x,y,clue:int):
    Neighbors=Get8(n,x,y)
    mask=0
    for i in range(8):
        if Neighbors[i]:
            mask|=1<<i
    Filter=BitsToNpArray(mask)
    Acc=[]
    for i in range(1<<8):
        if (i|mask)==mask:
            if len(RunLengthEncoding(i))==clue:
                Acc.append(BitsToNpArray(i))
    NeighborsShrink=[Mine[*i] for i in Neighbors if i]
    AccShrink=list(map(lambda x:x[Filter],Acc))
    model.AddAllowedAssignments(NeighborsShrink,AccShrink)

ruleE_model=-1
E_X_map=[None,None]
E_Y_map=[None,None]

def ruleE_unit(model,x:IntVar,y:IntVar,z:IntVar):
# x=(y+1)*(!z)
    AddSelector(model,x==y+1,x==0,z)

def ruleE(model:CpModel,Mine,n,x,y,clue:int):
    if ruleE_model!=id(model):
        for i in range(2):
            E_X_map[i]=np.array([[model.NewIntVar(0,n,'') for j in range(n)] for i in range(n)])
            E_Y_map[i]=np.array([[model.NewIntVar(0,n,'') for j in range(n)] for i in range(n)])
        for i in range(n):
            for j in range(n):
                if i!=0:
                    ruleE_unit(model,E_X_map[0][i,j],E_X_map[0][i-1,j],Mine[i,j])
                else:
                    model.Add(E_X_map[0][i,j]==Mine[i,j].Not())
                if i!=n-1:
                    ruleE_unit(model,E_X_map[1][i,j],E_X_map[1][i+1,j],Mine[i,j])
                else:
                    model.Add(E_X_map[1][i,j]==Mine[i,j].Not())
                if j!=0:
                    ruleE_unit(model,E_Y_map[0][i,j],E_Y_map[0][i,j-1],Mine[i,j])
                else:
                    model.Add(E_Y_map[0][i,j]==Mine[i,j].Not())
                if j!=n-1:
                    ruleE_unit(model,E_Y_map[1][i,j],E_Y_map[1][i,j+1],Mine[i,j])
                else:
                    model.Add(E_Y_map[1][i,j]==Mine[i,j].Not())
        ruleE_called=True
    model.Add(E_X_map[0][x,y]+E_X_map[1][x,y]+E_Y_map[0][x,y]+E_Y_map[1][x,y]==clue+3)