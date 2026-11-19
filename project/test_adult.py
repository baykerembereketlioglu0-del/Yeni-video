import sys; sys.path.insert(0,'.')
from gfx import *
from realistic import Adult, ADULTS
s = new_surface(); g = G(s.getCanvas())
g.vgrad(0,0,W,H,[(0,'#3a2a5a'),(1,'#ff9a6c')])
A = {k: Adult(v, i+1) for i,(k,v) in enumerate(ADULTS().items())}
# close-up busts
A['lucia'].draw(g, 330, 2900, 2600, 1.0, pose='idle', face={'brows':'determined','mouth':'smirk'}, look=0.15)
A['jason'].draw(g, 900, 2900, 2600, 1.0, pose='idle', face={'mouth':'smile','brows':'raised'}, look=-0.2)
# full bodies
for i,k in enumerate(['lucia_prison','lucia_night','brian','officer','guard','mom','dad','grifter1']):
    A[k].draw(g, 1260+ i*85 if False else 1240 + (i%4)*170, 520 + (i//4)*540, 500, 0.5, pose=['cross','guard','hold_r','hold_front','hips','idle','cross','idle'][i], held='beer' if k=='brian' else None, face={'brows':'angry' if i<2 else 'neutral','mouth':'flat'})
s.makeImageSnapshot().save('/tmp/claude-0/adult.png')
