import sys; sys.path.insert(0,'.')
from gfx import *
from characters import Person, CAST
s = new_surface(); g = G(s.getCanvas())
g.vgrad(0,0,W,H,[(0,'#f6ead2'),(1,'#e9d3b0')])
cast = CAST()
row1 = [("lucia_baby","idle",{"brows":"angry","mouth":"frown"},True),("lucia_toddler","guard",{"brows":"angry","mouth":"frown"},False),
        ("lucia_kid","cross",{"brows":"determined","mouth":"smirk"},False),("lucia_preteen","guard",{"brows":"angry"},False),
        ("lucia_teen","hips",{"brows":"neutral","mouth":"smile"},False),("lucia","idle",{"brows":"determined","mouth":"smirk"},False),
        ("lucia_prison","cross",{"brows":"angry","mouth":"frown"},False)]
x=150
for k,pose,face,anger in row1:
    Person(cast[k]).draw(g, x, 500, 380 if k!='lucia_baby' else 300, t=1.0, pose=pose, face=face, anger=anger, held="gloves" if k in("lucia_toddler","lucia_preteen") else None)
    x+=265
row2=["jason_kid","jason_army","jason","mom","dad","officer","guard","brian","grifter1","grifter2","cashier","bully","lucia_night"]
x=90
for k in row2:
    Person(cast[k]).draw(g, x, 1040, 330, t=0.5, pose="idle", face={"mouth":"smile"}, look=0.3)
    x+=145
s.makeImageSnapshot().save('/tmp/claude-0/rig.png')
