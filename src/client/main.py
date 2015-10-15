#! /usr/bin/env python

import sys, urllib, os, json

NAME = "squaremesh"

IP = "http://localhost:5000/"

importerr=False

try:
    import pygame
except ImportError:
    importerr=True
    print("Missing dependency 'pygame'")


if importerr:
    print("\nYou are missing some dependencies of "+NAME+".\n"+
    "Try running 'Installreqs.sh' (Unix) or 'Installreqs.bat' (Windows) to fix this.\n")
    sys.exit(-1)

pygame.init()

screen = pygame.display.set_mode((1000,700),pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)

pygame.display.set_caption(NAME)

IMAGES = {}

def b94(i):
    return (ord(i[0])-32)*94+(ord(i[1])-32)

class Player:
    def __init__(self):
        self.x=self.y=None

class Chunk:
    def updateImg(self):
        self.img.fill((0,0,0,0))
        for i in range(256):
            self.img.blit(blockimg(self.blocks[i]),(32*(i%16),32*(i//16)))
    def set(self,blocks):
        self.blocks = []
        #print blocks
        for i in range(256):
            self.blocks.append(b94(blocks[i*2:i*2+2]))
        self.updateImg()
    def __init__(self,blocks):
        self.img=pygame.Surface((512,512),pygame.SRCALPHA)
        self.set(blocks)

def image(path):
    if path in IMAGES.keys():
        return IMAGES[path]
    else:
        IMAGES[path] = pygame.image.load(path).convert_alpha()
        return image(path)

def blockimg(i):

    if i > 8819:
        img = blockimg(2).copy()
        sides = i - 8820
        sides = (bool(sides&1),bool(sides&2),bool(sides&4),bool(sides&8))
        #print sides
        if sides[0]:
            img.blit(image(os.path.join("resources","images","blocks","grass.png")),(0,0))
        if sides[1]:
            img.blit(pygame.transform.flip(image(os.path.join("resources","images","blocks","grass.png")),0,1),(0,32-5))
        if sides[2]:
            img.blit(pygame.transform.rotate(image(os.path.join("resources","images","blocks","grass.png")),90),(0,0))
        if sides[3]:
            img.blit(pygame.transform.rotate(image(os.path.join("resources","images","blocks","grass.png")),-90),(32-5,0))
        return img

    return image(os.path.join("resources","images","blocks","blocks_"+str(i//100)+"_"+str(i//100+99)+".png"))\
    .subsurface((32*(i%10),32*(i//10),32,32))

def loadifnot(x,y):
    if (x,y) not in loadedchunks.keys():
        u=urllib.urlopen(IP+"chunk?x="+str(x)+"&y="+str(y))
        loadedchunks[(x,y)]=Chunk(u.read())
        u.close()

MENU = "connect"

UNAME= sys.argv[1]

player=Player()

keyopt = {
'right':pygame.K_RIGHT,
'left' :pygame.K_LEFT,
'run'  :pygame.K_z,
'jump' :pygame.K_UP
}

def drawBG():
    screen.fill((0,150,255))

loadedchunks = {}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict["size"],pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)
    
    keys = pygame.key.get_pressed();
    
    if MENU == "connect":
        u=urllib.urlopen(IP+"connect?un="+UNAME);
        resp=u.read()
        u.close()
        if resp.startswith("acpt"):
            SID = resp[4:]
        elif resp.startswith("uniu"):
            pass
        else:
            print(resp)
            sys.exit(-1)
        MENU="game"
    
    if MENU == "game":
        skeys=""
        if keys[keyopt['right']]:
            skeys+='r'
        if keys[keyopt['left']]:
            skeys+='l'
        if keys[keyopt['run']]:
            skeys+='-'
        if keys[keyopt['jump']]:
            skeys+='j'
        u=urllib.urlopen(IP+"dat?sid="+SID+"&km="+skeys);
        resp=json.loads(u.read())
        u.close()
        player.x=resp['x']
        player.y=resp['y']
        
        drawBG()
        
        for i in range(-2,3):
            for j in range(-2,3):
                loadifnot(int(i+player.x//16),int(j+player.y//16))
            
        
        
        
        for chunk in loadedchunks.keys():
            screen.blit(loadedchunks[chunk].img,(32*(chunk[0]*16-player.x)+screen.get_width()/2,
            32*(chunk[1]*16-player.y)+screen.get_height()/2))
            if chunk[0] < player.x//16 - 5\
            or chunk[0] > player.x//16 + 5\
            or chunk[1] < player.y//16 - 5\
            or chunk[1] > player.y//16 + 5:
                del loadedchunks[chunk]
        
        for pp in resp['oppl']:
            screen.blit(image(os.path.join("resources","images","player",('',"flipped_")[pp['f']]+"player.gif")),
            (screen.get_width()/2-16+32*(pp['x']-player.x),screen.get_height()/2-32+32*(pp['y']-player.y)))
        
        screen.blit(image(os.path.join("resources","images","player",('',"flipped_")[resp['f']]+"player.gif")),
        (screen.get_width()/2-16,screen.get_height()/2-32))
        
        
    
    pygame.display.flip()
