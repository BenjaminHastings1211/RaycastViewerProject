from tkinter import *
import math, time, random

# W,H = 1440,900
W,H = 400,400
walls = []
viewingDistance = 100
#hello
def dist(p1,p2):
    return math.sqrt((p1[1]-p2[1])**2 + (p1[0]-p2[0])**2)

def mapVal(s,a1,a2,b1,b2):
    return b1 + ((s - a1)*(b2-b1))/(a2-a1)

class Box():
    def __init__(self,center,radius,rotation,color='#fff'):
        self.center = center
        self.color = color
        self.radius = radius*math.sqrt(2)
        if rotation % 90 == 0:
            rotation += 0.1
        self.angle = math.radians(rotation+45)

        self.render()

    def generateCorners(self):
        corners = []
        for i in range(4):
            corners.append((math.sin(self.angle)*self.radius+self.center[0],math.cos(self.angle)*self.radius+self.center[1]))
            self.angle += math.radians(90)

        return corners

    def render(self):
        c = self.generateCorners()

        Wall(c[0],c[1],self.color,self) # 0 - 1
        Wall(c[1],c[2],self.color,self) # 1 - 2
        Wall(c[2],c[3],self.color,self) # 2 - 3
        Wall(c[3],c[0],self.color,self) # 3 - 0

class Viewer():
    def __init__(self,pos,fov):
        self.pos = pos
        self.fov = fov
        self.rays = []
        self.connections = []

        for step,i in enumerate(self.generateRange()):
            if i % 90 == 0:
                continue
            self.rays.append(Ray(self.pos,i,fov))
            if step != 0:
                self.connections.append(Connection(self.rays[step-1],self.rays[step]))
            else:
                self.connections.append(Connection(self.rays[0],self.rays[0]))

        self.connections[0].p2 = self.rays[-1]

        print(len(self.connections))
        print(len(self.rays))

        root.bind("<Motion>",self.updatePos)

    def generateRange(self):
        upperLimit = 420
        for i in range(0,upperLimit,1):
            newVal = mapVal(i,0,upperLimit,0,360)
            if newVal % 90 != 0:
                yield newVal

    def updatePos(self,e):
        self.pos = [e.x,e.y]
        for r in self.rays:
            r.update(self.pos);

    def drawRays(self):
        points = []
        for i, r in enumerate(self.rays):
            r.checkWallCollide(walls)

        for c in self.connections:
            c.update()

class Ray():
    def __init__(self,origin,angle,fov):
        self.ray = screen.create_line(0,0,0,0,fill='red',width=1)
        self.endPoint = screen.create_oval(0,0,0,0,fill='#000')

        self.fov = fov
        self.data = {
            'p'         : origin,
            'theta'     : math.radians(angle),
            'd'         : self.determineLimits(origin[0],origin[0] + math.cos(math.radians(angle)),W),
            'r'         : self.determineLimits(origin[1],origin[1] + math.sin(math.radians(angle)),H),
            'm'         : None,
            'b'         : None,
            'collisions': []
        }

        if self.data['theta'] % 90 != 0:
            self.data['m'] = math.tan(self.data['theta'])

            self.data['b'] = self.data['m'] * (-1*self.data['p'][0]) + self.data['p'][1]


    def determineLimits(self,origin,nextStep,max):
        if origin < nextStep:
            return [origin,max]
        else:
            return [0,origin]

    def finalCollisionsLocation(self):
        try:
            if self.data['collisions'][0].distance > self.fov:
                col = (math.cos(self.data['theta'])*self.fov+self.data['p'][0],math.sin(self.data['theta'])*self.fov+self.data['p'][1])
            else:
                col = self.data['collisions'][0].location
        except:
            col = (math.cos(self.data['theta'])*self.fov+self.data['p'][0],math.sin(self.data['theta'])*self.fov+self.data['p'][1])

        return col

    def checkWallCollide(self,walls):

        for wall in walls:

            xIntersect = (wall.data['b']-self.data['b'])/(self.data['m'] - wall.data['m'])
            yIntersect = (xIntersect*self.data['m']) + self.data['b']

            if (wall.data['d'][0] <= xIntersect <= wall.data['d'][1]) and (self.data['d'][0] <= xIntersect <= self.data['d'][1]):
                col = Collision((xIntersect,yIntersect),dist((xIntersect,yIntersect),self.data['p']),wall)
                self.data['collisions'].append(col)

        self.data['collisions'] = list(sorted(self.data['collisions'],key = lambda x : x.distance))

    def update(self,pos):
        self.data['collisions'] = []
        self.data['p'] = pos
        self.data['d'] = self.determineLimits(self.data['p'][0],self.data['p'][0]+math.cos(self.data['theta']),W)
        self.data['r'] = self.determineLimits(self.data['p'][1],self.data['p'][1]+math.sin(self.data['theta']),H)
        self.data['b'] = self.data['m'] * (-1*self.data['p'][0]) + self.data['p'][1]

class Connection():
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2
        self.obj = screen.create_polygon(0,0,0,0,0,0,fill='#fff',outline='#fff')

    def update(self):
        center = self.p1.data['p']
        c1 = self.p1.finalCollisionsLocation();
        c2 = self.p2.finalCollisionsLocation();

        screen.coords(self.obj,center[0],center[1],c1[0],c1[1],c2[0],c2[1])


class Collision():
    def __init__(self,location,distance,object):
        self.location = location;
        self.distance = distance;
        self.object = object;

        self.checkForParent();

    def checkForParent(self):
        if self.object.parent != None:
            self.object = self.object.parent

class Wall():
    def __init__(self,pos1,pos2,color,parent=None):
        self.color = color
        self.parent = parent
        self.data = {
            'p' : [pos1,pos2],
            'd' : [p[0] for p in sorted([pos1,pos2],key=lambda x : x[0])],
            'r' : [p[1] for p in sorted([pos1,pos2],key=lambda x : x[1])]
        }

        self.data['m'] = self.getSlope()
        self.data['b'] = self.getYInt()

        self.draw()

        walls.append(self)

    def getSlope(self):
        yDiff = self.data['p'][1][1] - self.data['p'][0][1]
        xDiff = self.data['p'][1][0] - self.data['p'][0][0]
        return yDiff / xDiff

    def getYInt(self):
        return (self.data['m'] * (-1*self.data['p'][0][0])) + self.data['p'][0][1]

    def draw(self,thickness=1):
        screen.create_line(self.data['p'][0][0],self.data['p'][0][1],self.data['p'][1][0],self.data['p'][1][1],width=thickness,fill=self.color)

root = Tk()
root.geometry('%sx%s'%(W,H))
root.title('Raycasting Demo')
root.wm_attributes('-topmost',1)
root.resizable(0,0)

screen = Canvas(root,width=W,height=H,bd=0,highlightthickness=0,bg='#000')
screen.pack()

#Wall((50,50),(350,200),'#000')
#Wall((350,150),(500,100),'#000')
#Wall((600,500),(700,100),'#000')
#Wall((100,500),(450,500),'#000')
#Wall((475,300),(800,500),'#000')
#Wall((120,700),(800,800),'#000')

margin = 50
for i in range(1):
    Box((random.randint(margin,W-margin),random.randint(margin,H-margin)),random.randint(50,150),random.randint(0,360),'#000')

o = Viewer((250,250),viewingDistance)

while 1:
    o.drawRays();
    root.update()
    root.update_idletasks()
    time.sleep(0.01)
