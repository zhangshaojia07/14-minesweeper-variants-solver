import tkinter as tk
from sweeper.main import *
import pyautogui as pag
from PIL import Image
import time
import os
import numpy as np

pth=os.path.dirname(__file__)
timestamp = str(int(time.time()))
cur_pth=os.path.join(pth, timestamp)
std_pth=os.path.join(pth, 'std')
round_num=6
n=5
default_m={5:10,6:14,7:20,8:26}
m=default_m[n]
default_next_icon={5:(880,590),6:(900,620),7:(930,640),8:(960,670)}
next_icon=default_next_icon[n]
shot_mode=False

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

# b_size=40
# xx,yy=587,261
# col_name='MLWNXPE'
# row_name='QCTODSB'
# MouseReset()
# img = pag.screenshot()
# img=np.array(img.convert('1'))

# def play(c1,c2):
#     while True:
#         local_type=c2
#         init(n,[c1])
#         updateMineCount(14 if c1=='D' else (21 if c1=='B' else 20))
#         grid=match_list(getScreenshot())
#         printGrid(grid)
#         avail=[[0 for j in range(n)] for i in range(n)]
#         avail_cnt=0
#         for i in range(n):
#             for j in range(n):
#                 cur=grid[i][j]
#                 if cur==-1:
#                     update(i,j,HIDDENCLUE)
#                 elif cur==-2:
#                     avail[i][j]=1
#                     avail_cnt+=1
#                 elif cur==-3:
#                     update(i,j,MINE)
#                 else:
#                     update(i,j,(local_type,cur))
#         lst=sweep(np.array(avail))    
#         avail_cnt-=len(lst)    
#         for x,y,w in lst:
#             print(x+1,chr(ord('A')+y),'mine' if w else 'safe',sep='')
#             MouseMoveTo(x,y)
#             if w:# mine
#                 pag.rightClick()
#             else:
#                 pag.click()
#         if avail_cnt==0:
#             break

# for j in range(7):
#     for i in range(7):
#         if col_name[j]=='W' or row_name[i]=='C' or row_name[i]=='S' or row_name[i]=='O' or row_name[i]=='D':
#             continue
#         cx,cy=int(xx+b_size*(j+.5)),int(yy+b_size*(i+.5))
#         if img[cy-10:cy+10,cx-10:cx+10].sum()==0:
#             pag.click(cx,cy)
#             pag.click(1200,647)
#             time.sleep(1)
#             play(row_name[i],col_name[j])
#             pag.click(1173,646)
#             time.sleep(1)


round_num=7
for epoch in range(round_num):
    while True:
        local_type='V'
        m=10
        init(n,['B'])
        updateMineCount(m)
        grid=match_list(getScreenshot())
        printGrid(grid)
        avail=[[0 for j in range(n)] for i in range(n)]
        avail_cnt=0
        for i in range(n):
            for j in range(n):
                cur=grid[i][j]
                if cur==-1:
                    update(i,j,HIDDENCLUE)
                elif cur==-2:
                    avail[i][j]=1
                    avail_cnt+=1
                elif cur==-3:
                    update(i,j,MINE)
                else:
                    update(i,j,(local_type,cur))
        lst=sweep(np.array(avail))    
        avail_cnt-=len(lst)    
        for x,y,w in lst:
            print(x+1,chr(ord('A')+y),'mine' if w else 'safe',sep='')
            MouseMoveTo(x,y)
            if w:# mine
                pag.rightClick()
            else:
                pag.click()
        if avail_cnt==0:
            break

    if epoch!=round_num-1:
        # time.sleep(1)
        pag.click(*next_icon)
