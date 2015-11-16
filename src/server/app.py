from flask import Flask
from flask import request

import random, json, sys, os, noise, time

sys.stderr=open(os.devnull,'w')

CONNECTION_TIMEOUT=8

class MyServer(Flask):

    def __init__(self, *args, **kwargs):
            super(MyServer, self).__init__(*args, **kwargs)

            self.players={}
            self.actvplrs=[]
            self.sid2usr={}
            self.chunks={}
            self.spawnpoint=(0,0)
            self.ltt=time.time()
            self.worldseed=random.randint(-1000000,1000000)
            self.entities=[]
            
            print("Server started")
            print("Word seed is: {}".format(self.worldseed))

app = MyServer(__name__)

solidblocks = (1,2,8820,-1,20,21,22,23)

def blockAt(x,y,gen=False):
    if (x//16,y//16) in app.chunks.keys():
        return app.chunks[(x//16,y//16)].blocks[x%16][y%16]
    
    if gen:
        app.chunks[(x//16,y//16)] = Chunk(x//16,y//16)
        return blockAt(x,y)
    
    return -1

def setBlock(x,y,b):
    if (x//16,y//16) in app.chunks.keys():
        app.chunks[(x//16,y//16)].blocks[x%16][y%16] = b
        app.chunks[(x//16,y//16)].dirty()
    else:
        app.chunks[(x//16,y//16)] = Chunk(x//16,y//16)
        setBlock(x,y,b)
        

def NextSid():
    return str(random.randint(0,2147483647))

def b94(i):
    return chr(i//94+32)+chr(i%94+32)

def btime(blk,itm,plr=None):
    if plr != None:
        if plr.mode == 'god':
            return 0.02
    if itm[0]==11000:
        if itm[2]['blade']=='wood':
            if blk == 1: return 3
            if blk in (2,8820): return 5
    
        
    if blk in (2, 8820): return 10
    return 1000000000

def geti(l,i,d):
    try: return l[i]
    except: return d

class Chunk:
    def __init__(self,X,Y):
        self.blocks=[]
        
        
        self.x=X
        self.y=Y
        
        for x in range(16):
            self.blocks.append([])
            for y in range(16):
                n = noise.pnoise2((x+16*self.x)/20.,app.worldseed+0.5)*16+16
                if y+16*self.y < n:
                    self.blocks[-1].append(0)
                elif y+16*self.y < n + 5:
                    self.blocks[-1].append(8820)
                else:
                    self.blocks[-1].append(1)
        
        try:
            if (Y > 3 and random.randint(1,3)==2):
                size = random.randint(3,20)
                todo = [(random.randint(4,12),random.randint(4,12))]
                while size > 0 and len(todo) > 0:
                    random.shuffle(todo)
                    x,y = todo.pop()
                    self.blocks[x][y] = 20
                    size -= 1
                    if x > 0  and self.blocks[x-1][y] == 1:
                        todo.append((x-1,y))
                    if y > 0  and self.blocks[x][y-1] == 1:
                        todo.append((x,y-1))
                    if x < 16 and self.blocks[x+1][y] == 1:
                        todo.append((x+1,y))
                    if y < 16 and self.blocks[x][y+1] == 1:
                        todo.append((x,y+1))
            if (Y > 4 and random.randint(1,7)==2):
                size = random.randint(3,10)
                todo = [(random.randint(4,12),random.randint(4,12))]
                while size > 0 and len(todo) > 0:
                    random.shuffle(todo)
                    x,y = todo.pop()
                    self.blocks[x][y] = 21
                    size -= 1
                    if x > 0  and self.blocks[x-1][y] == 1:
                        todo.append((x-1,y))
                    if y > 0  and self.blocks[x][y-1] == 1:
                        todo.append((x,y-1))
                    if x < 16 and self.blocks[x+1][y] == 1:
                        todo.append((x+1,y))
                    if y < 16 and self.blocks[x][y+1] == 1:
                        todo.append((x,y+1))
            if (Y > 4 and random.randint(1,9)==2):
                size = random.randint(3,8)
                todo = [(random.randint(4,12),random.randint(4,12))]
                while size > 0 and len(todo) > 0:
                    random.shuffle(todo)
                    x,y = todo.pop()
                    self.blocks[x][y] = 23
                    size -= 1
                    if x > 0  and self.blocks[x-1][y] == 1:
                        todo.append((x-1,y))
                    if y > 0  and self.blocks[x][y-1] == 1:
                        todo.append((x,y-1))
                    if x < 16 and self.blocks[x+1][y] == 1:
                        todo.append((x+1,y))
                    if y < 16 and self.blocks[x][y+1] == 1:
                        todo.append((x,y+1))
            if (Y > 5 and random.randint(1,10)==2):
                size = random.randint(3,7)
                todo = [(random.randint(4,12),random.randint(4,12))]
                while size > 0 and len(todo) > 0:
                    random.shuffle(todo)
                    x,y = todo.pop()
                    self.blocks[x][y] = 22
                    size -= 1
                    if x > 0  and self.blocks[x-1][y] == 1:
                        todo.append((x-1,y))
                    if y > 0  and self.blocks[x][y-1] == 1:
                        todo.append((x,y-1))
                    if x < 16 and self.blocks[x+1][y] == 1:
                        todo.append((x+1,y))
                    if y < 16 and self.blocks[x][y+1] == 1:
                        todo.append((x,y+1))
        except:
            pass
    
    def __str__(self):
        s=""
        for y in range(16):
            for x in range(16):
                if self.blocks[x][y] == 8820:
                    s+=b94(8820+
                      int(not blockAt(16*self.x+x,16*self.y+y-1,1)in solidblocks)+
                    2*int(not blockAt(16*self.x+x,16*self.y+y+1,1)in solidblocks)+
                    4*int(not blockAt(16*self.x+x-1,16*self.y+y,1)in solidblocks)+
                    8*int(not blockAt(16*self.x+x+1,16*self.y+y,1)in solidblocks))
                    if s[-2:] == '}n': self.blocks[x][y] = 2
                    
                else:
                    s+=b94(self.blocks[x][y])
        return s
    
    def dirty(self):
        for usr in app.actvplrs:
            if (self.x,self.y) not in app.players[usr].dirtyChunks:
                app.players[usr].dirtyChunks.append((self.x,self.y))

class Player:
    def __init__(self,username):
        self.username=username
        self.x, self.y = self.cur = app.spawnpoint
        self.keys=''
        self.xv = self.yv = 0
        self.onground = True
        self.facing_left=False
        self.dirtyChunks=[]
        self.inv=[]
        self.slot=0
        self.lastref=time.time()
        self.ctime=time.time()
    
    def __str__(self):
        oppl=[]
        for usr in app.actvplrs:
            if usr == self.username:
                continue
            oppl.append({
                'x':app.players[usr].x,
                'y':app.players[usr].y,
                'f':app.players[usr].facing_left
            })
        return json.dumps({
            'x':self.x,
            'y':self.y,
            'f':self.facing_left,
            'oppl':oppl,
            'dch':self.dirtyChunks,
            'inv':self.inv,
            'slot':self.slot,
            'a':(time.time()-self.ctime)/btime(blockAt(*self.cur),geti(self.inv,self.slot,(0,0,{})))
        })
    
    def calcwalkspeed(self):
        speed = 4
        if '-' in self.keys:
            speed *= 2.2
        return speed

    def calcjumppower(self):
        return 25

    def tick(self,rt):
        while (solid(self.x-0.4,self.y+0.95) or solid(self.x+0.4,self.y+0.95)) and\
        not (solid(self.x-0.4,self.y) or solid(self.x+0.4,self.y)):
            self.y-=0.05
        self.onground = solid(self.x-0.4,self.y+1) or solid(self.x+0.4,self.y+1)
        self.yv += 20*rt
        self.yv /= 5 ** rt
        if self.onground:
            self.xv /= 1200 ** rt
            self.yv = min(self.yv,0)
        else:
            self.xv /= 2 ** rt
        if 'l' in self.keys:
            self.xv=-self.calcwalkspeed()
            self.facing_left=True
        if 'r' in self.keys:
            self.xv=+self.calcwalkspeed()
            self.facing_left=False
        if 'j' in self.keys and self.onground:
            self.yv=-self.calcjumppower()
        if 'A' in self.keys:
            self.slot=0
        if 'B' in self.keys:
            self.slot=1
        if 'C' in self.keys:
            self.slot=2
        if 'D' in self.keys:
            self.slot=3
        if 'E' in self.keys:
            self.slot=4
        if 'F' in self.keys:
            self.slot=5
        if 'G' in self.keys:
            self.slot=6
        if 'H' in self.keys:
            self.slot=7
        if 'I' in self.keys:
            self.slot=8
        if 'J' in self.keys:
            self.slot=9
        if '1' in self.keys:
            if (self.cur[0]-self.x)*(self.cur[0]-self.x)+(self.cur[1]-self.y)*(self.cur[1]-self.y) < 80:
                if solid(*self.cur)and time.time()-self.ctime>btime(blockAt(*self.cur),geti(self.inv,self.slot,(0,0,{}))):
                    setBlock(*(self.cur+(0,)))
        else: self.ctime = time.time()
        if solid(self.x-0.5,self.y-0.9) or solid(self.x-0.5,self.y+0.9) or solid(self.x-0.5,self.y):
            self.xv=max(0,self.xv)
        if solid(self.x+0.5,self.y-0.9) or solid(self.x+0.5,self.y+0.9) or solid(self.x+0.5,self.y):
            self.xv=min(0,self.xv)
        if solid(self.x-0.4,self.y-1) or solid(self.x+0.4,self.y-1):
            self.yv=max(0,self.yv)
        self.x+=self.xv*rt
        self.y+=self.yv*rt

def solid(x,y):
    if x < 0:
        x -= 1
    x=int(x)
    y=int(y)
    
    if (x//16,y//16) in app.chunks.keys():
        return app.chunks[(x//16,y//16)].blocks[x%16][y%16] in solidblocks
        
    return True



def tick():
    t=time.time()
    if t - app.ltt < 1/50.:
        return
    rt = t - app.ltt
    app.ltt=t
    if rt > 0.5:
        rt = 0.5
    i=0
    while i < len(app.actvplrs):
        player=app.players[app.actvplrs[i]]
        player.tick(rt)
        if time.time()-player.lastref>CONNECTION_TIMEOUT:
            print("User {} left. Reason: Connection timed out.".format(app.actvplrs[i]))
            del app.actvplrs[i]
            i-=1
        i+=1

@app.route("/")
def index():
    return "kzzzzzsh - This is a squaremesh server - kzzzzzsh"

@app.route("/connect")
def connect():
    sid = NextSid()
    app.sid2usr[sid]=request.args["un"]
    if request.args["un"] not in app.players.keys():
        app.players[request.args["un"]] = Player(request.args["un"])
    else:
        app.players[request.args["un"]].lastref=time.time()
    if request.args["un"] not in app.actvplrs:
        app.actvplrs.append(request.args["un"])
    print("User {} joined. SID {}".format(request.args["un"],sid))
    return "acpt"+sid

@app.route("/quit")
def quit():
    print("User {} left. Reason: Quit.".format(app.sid2usr[request.args["sid"]]))
    app.actvplrs.remove(app.sid2usr[request.args["sid"]])
    del app.sid2usr[request.args["sid"]]
    return ""

@app.route("/dat")
def pdat():
    try:
        tick()
        player = app.players[app.sid2usr[request.args['sid']]]
        player.lastref=time.time()
        player.keys=request.args.get('km','')
        ocr = player.cur
        player.cur=request.args.get('cur','0x0').split('x')
        player.cur=(int(player.cur[0]),int(player.cur[1]))
        if ocr != player.cur:
            player.ctime = time.time()
        s = str(player)
        player.dirtyChunks = []
        return s
    except Exception as e:
        print e
        raise e

@app.route("/chunk")
def getchunk():
    try:
        if (int(request.args['x']),int(request.args['y'])) in app.chunks.keys():
            return str(app.chunks[(int(request.args['x']),int(request.args['y']))])
        else:
            app.chunks[(int(request.args['x']),int(request.args['y']))]=Chunk(int(request.args['x']),int(request.args['y']))
            return str(app.chunks[(int(request.args['x']),int(request.args['y']))])
    except Exception as e:
        print e
        raise e
        
app.run()
