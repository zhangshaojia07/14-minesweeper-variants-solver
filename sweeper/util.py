from ortools.sat.python.cp_model import CpModel,BoundedLinearExpression,IntVar

def AddOrAndExpr(model:CpModel,OrAndExpr:list[list[BoundedLinearExpression|tuple[BoundedLinearExpression|bool,list[IntVar]]]]):
# OrAndExpr: 由 AndExpr 组成的 list,求它们的 OR
# AndExpr: 由 item 组成的 list,求它们的 AND
# item 要么是一个限制,要么是一个 tuple
# tuple 前者是限制(或者就是bool),后者是一个条件(布尔变量)列表,表示这些布尔变量都取 1 时该限制才有效
    vars=[]
    for AndExpr in OrAndExpr:
        cur=model.NewBoolVar('')
        vars.append(cur)
        for item in AndExpr:
            if isinstance(item,tuple):
                Expr,Cond=item
                model.Add(Expr).OnlyEnforceIf(Cond,cur)
            else:
                model.Add(item).OnlyEnforceIf(cur)
    model.Add(sum(vars)==1)

def AddSelector(model:CpModel,Expr0:BoundedLinearExpression,Expr1:BoundedLinearExpression,sel:IntVar):
    model.Add(Expr0).OnlyEnforceIf(sel.Not())
    model.Add(Expr1).OnlyEnforceIf(sel)

def Get8(n,x,y):
    res=[]
    for i,j in [(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]:
        i+=x
        j+=y
        if i<0 or i>=n or j<0 or j>=n:
            res.append(None)
        else:
            res.append((i,j))
    return res

def Get4(n,x,y):
    res=[]
    for i,j in [(-1,0),(0,1),(1,0),(0,-1)]:
        i+=x
        j+=y
        if i<0 or i>=n or j<0 or j>=n:
            res.append(None)
        else:
            res.append((i,j))
    return res

def IsDye(x,y):
    return (x+y)%2==1