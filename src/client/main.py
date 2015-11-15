#! /usr/bin/env python

import sys, urllib, os, json, time

NAME = "squaremesh"

IP = "localhost:5000"

mpos = (0,0)

importerr=False

slot = 0

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
        self.x=self.y=0
        self.inv=[]

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

def inr(p,r):
    return p[0]>r[0]and p[1]>r[1]and p[0]<r[0]+r[2]and p[1]<r[1]+r[3]

def blockimg(i,x=None):

    if i == 11000:
        img = pygame.Surface((32,32),pygame.SRCALPHA)
        img.blit(image(os.path.join("resources","images","blocks","tools","handles",x['rod']+".png")),(0,0))
        img.blit(image(os.path.join("resources","images","blocks","tools","pickblades",x['blade']+".png")),(0,0))
        return img

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

    return image(os.path.join("resources","images","blocks","blocks_"+str((i//100)*100)+"_"+str(99+100*(i//100))+".png"))\
    .subsurface((32*(i%10),32*((i%100)//10),32,32))

def loadifnot(x,y):
    if (x,y) not in loadedchunks.keys():
        u=urllib.urlopen(IP+"chunk?x="+str(x)+"&y="+str(y))
        loadedchunks[(x,y)]=Chunk(u.read())
        u.close()

kbtxt = u""

selbox = 0;

MENU = "login"

UNAME= ""

player=Player()

font = pygame.font.Font(os.path.join("resources","fonts","Font.ttf"),20)

smallfont = pygame.font.Font(os.path.join("resources","fonts","Font.ttf"),10)

keyopt = {
'right' :pygame.K_RIGHT,
'left'  :pygame.K_LEFT,
'run'   :pygame.K_z,
'jump'  :pygame.K_UP,
's1'    :pygame.K_1,
's2'    :pygame.K_2,
's3'    :pygame.K_3,
's4'    :pygame.K_4,
's5'    :pygame.K_5,
's6'    :pygame.K_6,
's7'    :pygame.K_7,
's8'    :pygame.K_8,
's9'    :pygame.K_9,
's10'    :pygame.K_0,
}

def drawBG():
    screen.fill((0,150,255))

loadedchunks = {}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if MENU == "game":
                urllib.urlopen(IP+"quit?sid="+SID).close()
            sys.exit(0)
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict["size"],pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(kbtxt) > 0:
                    kbtxt = kbtxt[:-1]
            elif len(kbtxt) < 127:
                kbtxt += event.unicode
        if event.type == pygame.MOUSEMOTION:
            mpos = event.pos
        clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True
    
    keys = pygame.key.get_pressed();
    
    if MENU == "login":
        screen.fill((150,70,22))
        screen.blit(font.render("Username:",False,(255,255,255)),(screen.get_width()/4-font.size("Username:")[0],
        screen.get_height()/3))
        pygame.draw.rect(screen,(0,0,0),(screen.get_width()/4,screen.get_height()/3-10,screen.get_width()/2,40))
        screen.blit(font.render(UNAME+('','_')[selbox==1 and time.time() % 0.5 < 0.25],False,(255,255,255)),
        (screen.get_width()/4+5,screen.get_height()/3))
        
        if clicked and inr(mpos,(screen.get_width()/4,screen.get_height()/3-10,screen.get_width()/2,40)):
            selbox = 1
            kbtxt = UNAME
        
        if selbox == 1:
            UNAME = kbtxt
            if len(UNAME) > 0 and UNAME[-1] == '\r':
                UNAME=UNAME[:-1]
                selbox = 0
        
        screen.blit(font.render("Server IP:",False,(255,255,255)),(screen.get_width()/4-font.size("Server IP:")[0],
        2*screen.get_height()/3))
        pygame.draw.rect(screen,(0,0,0),(screen.get_width()/4,2*screen.get_height()/3-10,screen.get_width()/2,40))
        screen.blit(font.render(IP+('','_')[selbox==2 and time.time() % 0.5 < 0.25],False,(255,255,255)),
        (screen.get_width()/4+5,2*screen.get_height()/3))
        
        if clicked and inr(mpos,(screen.get_width()/4,2*screen.get_height()/3-10,screen.get_width()/2,40)):
            selbox = 2
            kbtxt = IP
        
        if selbox == 2:
            IP = kbtxt
            if len(IP) > 0 and IP[-1] == '\r':
                IP=IP[:-1]
                selbox = 0
        
        pygame.draw.rect(screen,(100,100,100),(screen.get_width()/2-75,screen.get_height()*3/4,150,40))
        screen.blit(font.render("Connect",False,(255,255,255)),(screen.get_width()/2-font.size("Connect")[0]/2,
        screen.get_height()*3/4+10))
        
        if clicked and inr(mpos,(screen.get_width()/2-75,screen.get_height()*3/4,150,40)):
            MENU = "connect"
            continue
        
    
    if MENU == "connect":
        if not (IP.startswith("http://") or IP.startswith("https://")):
            IP = "http://" + IP
        if IP[-1] != '/':
            IP+='/'
        u=urllib.urlopen(IP)
        resp=u.read()
        u.close()
        if resp != "kzzzzzsh - This is a squaremesh server - kzzzzzsh":
            MENU = "login"
            continue
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
        continue
    
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
        for i in range(1,11):
            if keys[keyopt['s'+str(i)]]:
                skeys+=chr(64+i)
        if pygame.mouse.get_pressed()[0]:
            skeys+="1"
        if pygame.mouse.get_pressed()[1]:
            skeys+="2"
        if pygame.mouse.get_pressed()[2]:
            skeys+="3"
        u=urllib.urlopen(IP+"dat?sid="+SID+"&km="+skeys+"&cur="+
        str(int(mpos[0]-screen.get_width()/2+player.x*32)/32)
        +"x"+
        str(int(mpos[1]-screen.get_height()/2+player.y*32)/32)
        )
        resp=json.loads(u.read())
        u.close()
        player.x=resp['x']
        player.y=resp['y']
        player.inv=resp['inv']
        slot=resp['slot']
        
        for chunk in resp['dch']:
            if tuple(chunk) in loadedchunks.keys():
                del loadedchunks[tuple(chunk)]
        
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
        
        pygame.draw.arc(screen,(200,200,200,200),(mpos[0]-16,mpos[1]-16,32,32),
        -1.57079632679,resp['a']*6.28318530718-1.57079632679,10)
        
        pygame.draw.rect(screen,(180,180,180),(screen.get_width()/2-200,screen.get_height()-40,400,40))
        for i in range(10):
            pygame.draw.rect(screen,(40,40,40),(screen.get_width()/2-198+i*40,screen.get_height()-38,36,36))
            if i < len(player.inv):
                screen.blit(blockimg(player.inv[i][0],player.inv[i][2]),
                (screen.get_width()/2-196+i*40, screen.get_height()-36))
            if i == slot:
                pygame.draw.rect(screen,(255,255,255),(screen.get_width()/2-198+i*40,screen.get_height()-45,36,5))
        
    
    pygame.display.flip()
