import tkinter as tk
import gurobipy as grb
from gurobipy import GRB
import pyautogui as pag
from PIL import Image
import time
import os
import numpy as np

pth=os.path.dirname(__file__)
timestamp = str(int(time.time()))
cur_pth=os.path.join(pth, timestamp)
std_pth=os.path.join(pth, 'std')
round_num=1
n=8
default_m={5:10,6:14,7:20,8:26}
m=default_m[n]
m=24
default_next_icon={5:(880,590),6:(900,620),7:(930,640),8:(960,670)}
next_icon=default_next_icon[n]
local_type='V'
shot_mode=False
def DefaultRules():
    ruleSum()
    ruleB()
env = grb.Env(params={"OutputFlag":0})
model = grb.Model('MyModel',env=env)
mp=model.addVars(n,n,vtype=GRB.BINARY,name="x")

padding_x,padding_y=700,300
err_x,err_y=11,45
block_size=50
margin=4

def create_transparent_window():
    # 创建主窗口
    root = tk.Tk()
    root.title("Locate helper")
    
    # 设置窗口大小 (宽度x高度)
    window_size = int(n*block_size)
    root.geometry(f"{window_size}x{window_size}")
    
    # 设置窗口位置 (x+y)
    root.geometry(f"+{padding_x}+{padding_y}")
    
    # 设置窗口透明度 (0.0完全透明, 1.0完全不透明)
    transparency = 0.7  # 70%不透明
    root.attributes('-alpha', transparency)
    
    # 设置窗口固定大小 (禁止调整)
    root.resizable(False, False)
    
    # root.overrideredirect(True)
    
    # 设置窗口始终在最前面 (可选)
    root.attributes('-topmost', True)
    
    # 运行主循环
    root.mainloop()

def ruleSum():
    val=0
    for i in range(n):
        for j in range(n):
            val+=mp[i,j]
    model.addConstr(val==m)
def ruleT():
    model.addConstrs( ( mp[i,j]+mp[i,j+1]+mp[i,j+2]<=2 for j in range(n-2) for i in range(n) ) , 'no triple row' )
    model.addConstrs( ( mp[i,j]+mp[i+1,j]+mp[i+2,j]<=2 for j in range(n) for i in range(n-2) ) , 'no triple col' )
    model.addConstrs( ( mp[i,j]+mp[i+1,j+1]+mp[i+2,j+2]<=2 for j in range(n-2) for i in range(n-2) ) , 'no triple diag' )
    model.addConstrs( ( mp[i,j+2]+mp[i+1,j+1]+mp[i+2,j]<=2 for j in range(n-2) for i in range(n-2) ) , 'no triple counter-diag' )
def ruleQ():
    model.addConstrs( ( mp[i,j]+mp[i,j+1]+mp[i+1,j]+mp[i+1,j+1]>=1 for j in range(n-1) for i in range(n-1) ) , 'no empty square' )
def ruleB():
    assert(m%n==0)
    w=m//n
    model.addConstrs( ( eval('+'.join([f'mp[{i},{j}]' for j in range(n)]))==w for i in range(n) ) , 'B row sum' )
    model.addConstrs( ( eval('+'.join([f'mp[{i},{j}]' for i in range(n)]))==w for j in range(n) ) , 'B col sum' )
# M,L,N,X
def clue(x,y,w):
    model.addConstr(mp[x,y]==0)
    if w==-1:
        return 
    val=0
    if local_type=='V':
        for i,j in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            i+=x
            j+=y
            if i>=0 and i<n and j>=0 and j<n:
                val+=mp[i,j]
        model.addConstr(val==w)
    elif local_type=='X':
        for i,j in [(-2,0),(-1,0),(1,0),(2,0),(0,-2),(0,-1),(0,1),(0,2)]:
            i+=x
            j+=y
            if i>=0 and i<n and j>=0 and j<n:
                val+=mp[i,j]
        model.addConstr(val==w)
    elif local_type=='M':
        for i,j in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            i+=x
            j+=y
            if i>=0 and i<n and j>=0 and j<n:
                val+=mp[i,j]*(1 if (i+j)%2==0 else 2)
        model.addConstr(val==w)

def mine(x,y):
    model.addConstr(mp[x,y]==1)

class MyError(Exception):
    pass

std_dict={}
char_dict={}
def load_std():
    for i in os.listdir(std_pth):
        img_pth=os.path.join(std_pth,i)
        # img=Image.open(img_pth)
        # img=Image.fromarray(norm(img))
        # img.save(img_pth)
        j=i.split('.')[0]
        num_j=int(j)
        std_dict[num_j]=np.array(Image.open(img_pth))
        if num_j==-1:
            tmp='?'
        elif num_j==-2:
            tmp='_'
        elif num_j==-3:
            tmp='$'
        else:
            tmp=j
        char_dict[num_j]=tmp

def MouseReset():
    pag.moveTo(10,10)
    # time.sleep(0.05)
    
def norm(a):
    b=a
    b=np.array(b.convert('L'))
    b=b[margin:-margin,margin:-margin]
    b=b>200
    x=0
    while x<b.shape[0] and b[x].sum()==0:
        x+=1
    if x==b.shape[0]:
        return np.zeros((block_size,block_size),dtype=bool)
    b=b[x:]
    # x=b.shape[0]-1
    # while b[x].sum()==0:
    #     x-=1
    # b=b[:x+1]
    x=0
    while b[:,x].sum()==0:
        x+=1
    b=b[:,x:]
    # x=b.shape[1]-1
    # while b[:,x].sum()==0:
    #     x-=1
    # b=b[:,:x+1]
    b=np.vstack([b,np.zeros((block_size-b.shape[0],b.shape[1]),dtype=bool)])
    b=np.hstack([b,np.zeros((b.shape[0],block_size-b.shape[1]),dtype=bool)])
    return b
def getScreenshot(is_save=False):
    if is_save:
        os.mkdir(cur_pth)
    MouseReset()
    img = pag.screenshot()
    im=img.crop((padding_x+err_x,padding_y+err_y,padding_x+err_x+n*block_size,padding_y+err_y+n*block_size))
    lst=[]
    for i in range(n):
        row=[]
        for j in range(n):
            cr=im.crop((j*block_size,i*block_size,(j+1)*block_size,(i+1)*block_size))
            cr=norm(cr)
            if is_save:
                new_cr=Image.fromarray(cr)
                new_cr.save(os.path.join(cur_pth,f'{i}{j}.png'))
            row.append(cr)
        lst.append(row)
    return lst

def similarity(a,b):
    return (a==b).sum()
def match(a):
    ans,val=-114,-1
    for i,j in std_dict.items():
        cur=similarity(a,j)
        if cur>val:
            val=cur
            ans=i
    return ans
def match_list(a):
    for i in range(n):
        for j in range(n):
            a[i][j]=match(a[i][j])
    return a
def MouseMoveTo(x,y):
    pag.moveTo(padding_x+err_x+block_size*(y+.5),padding_y+err_y+block_size*(x+.5))
def printGrid(a):
    print()
    for i in range(n):
        for j in range(n):
            print(char_dict[a[i][j]],end='')
        print()


load_std()
create_transparent_window()
if shot_mode:
    getScreenshot(is_save=True)
    exit()
    
for epoch in range(round_num):
    try:
        while True:
            model.remove(model.getConstrs())
            # model.update()
            # print(len(model.getConstrs()))
            DefaultRules()
            grid=match_list(getScreenshot())
            # grid[0][2]=-1
            printGrid(grid)
            avail=[[0 for j in range(n)] for i in range(n)]
            avail_cnt=0
            for i in range(n):
                for j in range(n):
                    cur=grid[i][j]
                    if cur==-2:
                        avail[i][j]=1
                        avail_cnt+=1
                    elif cur==-3:
                        mine(i,j)
                    else:
                        clue(i,j,cur)

            # model.addConstr(mp[5,1]==1)
            # model.optimize()
            # print(model.status,len(model.getConstrs()))
            # fcnt=0
            # for tmp in model.getVars():
            #     print(tmp.VarName,int(tmp.x),end='  ')
            #     fcnt+=1
            #     if fcnt%5==0:
            #         print()
            # exit()

            # is_mine=None
            for i in range(n):
                for j in range(n):
                    if avail[i][j]:
                        for k in range(2):
                            temp=model.addConstr(mp[i,j]==k)
                            model.optimize()
                            if model.status==GRB.INFEASIBLE:
                                print(i+1,chr(ord('A')+j),'safe' if k else 'mine',sep='')
                                MouseMoveTo(i,j)
                                if not k:# mine
                                    pag.rightClick()
                                else:
                                    pag.click()
                                avail_cnt-=1
                            model.remove(temp)
                            if avail_cnt==0:
                                raise MyError
            # if is_mine:
            #     mine(*is_mine)
            # else:
            #     inp=input()
            #     print('\n'*3,end='')
            #     op=[int(inp[0])-1,ord(inp[1].upper())-ord('A'),int(inp[2:])]
            #     clue(*op)
    except MyError:
        pass
    # exit()
    if epoch!=round_num-1:
        # time.sleep(1)
        pag.click(*next_icon)
