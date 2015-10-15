from flask import Flask
from flask import request

import random, json, sys, os, noise, time

sys.stderr=open(os.devnull,'w')

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

app = MyServer(__name__)

solidblocks = (1,2,8820,-1)

def blockAt(x,y,gen=False):
    if (x//16,y//16) in app.chunks.keys():
        return app.chunks[(x//16,y//16)].blocks[x%16][y%16]
    
    if gen:
        app.chunks[(x//16,y//16)] = Chunk(x//16,y//16)
        return blockAt(x,y)
    
    return -1

def NextSid():
    return str(random.randint(0,2147000000))

def b94(i):
    return chr(i//94+32)+chr(i%94+32)

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
    
    def __str__(self):
        s=""
        for y in range(16):
            for x in range(16):
                if self.blocks[x][y] == 8820:
                    #s+=b96(9200+
                    #1*(not solid(16*self.x+x,16*self.y+y-1))+
                    #2*(not solid(16*self.x+x,16*self.y+y+1))+
                    #4*(not solid(16*self.x+x-1,16*self.y+y))+
                    #8*(not solid(16*self.x+x+1,16*self.y+y)))
                    s+=b94(8820+
                      int(not blockAt(16*self.x+x,16*self.y+y-1,1)in solidblocks)+
                    2*int(not blockAt(16*self.x+x,16*self.y+y+1,1)in solidblocks)+
                    4*int(not blockAt(16*self.x+x-1,16*self.y+y,1)in solidblocks)+
                    8*int(not blockAt(16*self.x+x+1,16*self.y+y,1)in solidblocks))
                    #j = 8200
                    #print blockAt(16*self.x+x+1,16*self.y+y)in solidblocks
                    #if not(blockAt(16*self.x+x,16*self.y+y-1)in solidblocks):
                    #    j+=1
                    #    print "found:", blockAt(16*self.x+x,16*self.y+y-1)
                    #if not(blockAt(16*self.x+x,16*self.y+y+1)in solidblocks):
                    #    j+=2
                    #    #print "found:", blockAt(16*self.x+x,16*self.y+y+1)
                    #if not(blockAt(16*self.x+x-1,16*self.y+y)in solidblocks):
                    #    j+=4
                    #    
                    #if not(blockAt(16*self.x+x+1,16*self.y+y)in solidblocks):
                    #    j+=8
                    #
                    #print j
                    #s+=b94(j)
                else:
                    s+=b94(self.blocks[x][y])
        return s

class Player:
    def __init__(self,username):
        self.username=username
        self.x, self.y = app.spawnpoint
        self.keys=''
        self.xv = self.yv = 0
        self.onground = True
        self.facing_left=False
    
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
            'oppl':oppl
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
        if solid(self.x-0.5,self.y-0.9) or solid(self.x-0.5,self.y+0.9) or solid(self.x-0.5,self.y):
            self.xv=max(0,self.xv)
        if solid(self.x+0.5,self.y-0.9) or solid(self.x+0.5,self.y+0.9) or solid(self.x+0.5,self.y):
            self.xv=min(0,self.xv)
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
    for usr in app.actvplrs:
        player=app.players[usr]
        player.tick(rt)

@app.route("/")
def index():
    return "hello world"

@app.route("/connect")
def connect():
    sid = NextSid()
    app.sid2usr[sid]=request.args["un"]
    if request.args["un"] not in app.players.keys():
        app.players[request.args["un"]] = Player(request.args["un"])
        app.actvplrs.append(request.args["un"])
    return "acpt"+sid

@app.route("/dat")
def pdat():
    tick()
    player = app.players[app.sid2usr[request.args['sid']]]
    player.keys=request.args.get('km','')
    return str(player)

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
