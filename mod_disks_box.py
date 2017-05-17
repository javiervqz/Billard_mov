import random, math, os
import pylab as pl

o_dir = 'Ball_movie'
colors = ['orange','b','r','g']

def wall_time(pos_a, vel_a, radius):
    if vel_a > 0.0: #is aproaching to a right/upper wall
        del_t = (1.0 -radius-pos_a)/vel_a
    elif vel_a < 0.0: #is approaching to the left/down wall
        del_t = (pos_a - radius)/abs(vel_a)
    else: #if velocity is zero will never get to the wall
        del_t = float('inf')
    return del_t

def pair_time(pos_a, vel_a, pos_b, vel_b, radius):
    # Difference in position x_i(t)-x_j(t)
    # where x_j is the position a every time
    dif_pos = [pos_b[0] - pos_a[0], pos_b[1] - pos_a[1]]
    #square of the distance between disks
    dist_sq = dif_pos[0]**2 + dif_pos[1]**2
    #Same thing but with velocities
    dif_v = [vel_b[0]-vel_a[0], vel_b[1]-vel_a[1]]
    speed_sq = dif_v[0]**2 + dif_v[1]**2
    #Indicates if the disks are aproaching (negative)
    #or moving away(positive) this comes
    # up naturaly squaring dif_pos and solving for t
    approach = dif_pos[0]*dif_v[0] + dif_pos[1]*dif_v[1]
    #Comes from de second order equation for t, is the discriminant
    discr_sq = approach**2 - speed_sq*(dist_sq - 4.0*radius**2)
    if approach < 0.0 and discr_sq > 0.0:
        del_t = -(approach + math.sqrt(discr_sq))/speed_sq
    else:
        del_t = float('inf')
    return del_t

pl.subplots_adjust(left = 0.10, right = 0.90, top = 0.90, bottom = 0.10)
pl.gcf().set_size_inches(6, 6)
img = 0
if not os.path.exists(o_dir):
    os.makedirs(o_dir)

def snap (t, position, velocity, colors, arrow_scale = .2):
    global img
    pl.cla()
    pl.axis([0, 1, 0, 1])
    pl.setp(pl.gca(), xticks = [0,1], yticks = [0,1])
    for (x, y), (dx, dy), c in zip(position, velocity, colors):
        dx *= arrow_scale
        dy *= arrow_scale
        circle = pl.Circle((x,y), radius = radius, fc = c)
        pl.gca().add_patch(circle)
        pl.arrow(x, y, dx, dy, fc ='k', ec = 'k', head_width = 0.05, head_length=0.05)
    pl.text(0.5, 1.03, 't = %.2f' % t, ha='center')
    pl.savefig(os.path.join(o_dir, '%04i.png' % img))
    img += 1


radius = 0.1
position = [[0.25, 0.25], [0.75, 0.25]]
#velocity = [[random.uniform(-0.5, 1.0),random.uniform(-1.0, 0.5)],
#            [random.uniform(-0.5, 1.0),random.uniform(-1.0, 0.5)]]

velocity = [[0.101, 0.5],[0.0,-0.5]]

#takes every disk and the corresponding component
#of position/velocity (Disk, Direction of Pos/vel)
single = [(0,0), (0,1),(1,0),(1,1)]
#takes every disk respective to the other
pairs = [(0,1),(1,0)]

t = 0.0
dt = 0.1

steps = 100
snap(t, position,velocity,colors)

for step in range(steps):
    #every time a disk may hit a wall/otherdisk (not considering the other disks)
    wall_times = [wall_time(position[k][l], velocity[k][l], radius) for k, l in single]
    pair_times = [pair_time(position[k], velocity[k], position[l], velocity[l], radius) for k, l in pairs]
    next_event = min(wall_times+pair_times) #what happens next is what it takes less time

    print next_event + t
    next_t = t + dt

    while t + next_event <= next_t:
        t += next_event
        for k, l in single:
            position[k][l] += velocity[k][l]*next_event
        if min(wall_times) < min(pair_times):
            collision_disk, direction = single[wall_times.index(next_event)]
            velocity[collision_disk][direction] *= -1.0

        else:
            a, b = pairs[pair_times.index(next_event)]
            del_x = [position[b][0] - position[a][0], position[b][1] - position[a][1]]
            abs_x = math.sqrt(del_x[0]**2 + del_x[1]**2)
            e_perp = [c/abs_x for c in del_x]
            del_v = [velocity[b][0]-velocity[a][0], velocity[b][1]-velocity[a][1]]
            scal = del_v[0]*e_perp[0] + del_v[1]*e_perp[1]
            for k in range(2):
                velocity[a][k] += e_perp[k]*scal
                velocity[b][k] -= e_perp[k]*scal
        #every time a disk may hit a wall/otherdisk (not considering the other disks)
        wall_times = [wall_time(position[k][l], velocity[k][l], radius) for k, l in single]
        pair_times = [pair_time(position[k], velocity[k], position[l], velocity[l], radius) for k, l in pairs]
        next_event = min(wall_times + pair_times) #what happens next is what it takes less timec


    remain_t = next_t - t
    for k, l in single:
        position[k][l] += velocity[k][l]*remain_t
    t += remain_t
    next_event -= remain_t
    snap(t,position,velocity,colors)
print "animating..."
os.system("convert -delay 6 -dispose Background +page " + str(o_dir) + "/*.png -loop 0 " + str(o_dir) + "/animation.gif")
print "Done at " + str(o_dir)
