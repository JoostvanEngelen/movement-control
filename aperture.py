import numpy as np
import matplotlib.pyplot as plt


class EllipcicalAperture:
    def __init__(self, height, width, center:tuple, angle=0) -> None:
        self.aperture_shape = 'elliptical' 
        self.height = height
        self.width = width
        self.center_x = center[0]
        self.center_y = center[1]
        self.center = center
        self.angle = angle
        
        self.cos_angle = np.cos(np.radians(180. - angle))
        self.sin_angle = np.sin(np.radians(180. - angle))


    def point_inside_aperture(self, point):
        xc = point[0] - self.center[0]
        yc = point[1] - self.center[1]

        xct = xc * self.cos_angle - yc * self.sin_angle
        yct = xc * self.sin_angle + yc * self.cos_angle 

        rad_cc = (xct**2/(self.width/2.)**2) + (yct**2/(self.height/2.)**2)

        return rad_cc < 1

    def remove_points_outside_aperture(self, seq):
        safe_seq = []
        removed_points = []
        for point in seq:
            if self.point_inside_aperture(point):
                safe_seq.append(point)
            else:
                removed_points.append(point)
        return safe_seq



def create_raster_sequence(center, size, resolution):
    # This is now just a square centered around the middle but could be anything
    xgrid = np.linspace(center[0] - size/2, center[0] + size/2, resolution) 
    ygrid = np.linspace(center[1] - size/2, center[1] + size/2, resolution)
    xscan = []
    yscan = []
    for i, yi in enumerate(ygrid):
        xscan.append(xgrid[::(-1)**i]) # reverse when i is odd
        yscan.append(np.ones_like(xgrid) * yi)
    xscan = np.concatenate(xscan)
    yscan = np.concatenate(yscan)
    sequence = []
    for i in range(len(xscan)):
        sequence.append((xscan[i], yscan[i]))
    return sequence


# def measurement_sequence(LTS_system, sequence):
#     for x_co, y_co in sequence:
#         LTS_system.move_to(x_co, y_co)
#         # HERE DO THE MEASUREMENT
#         time.sleep(0.5) # this is a replacement for some measurement
#     return




el = EllipcicalAperture(5, 10, (0,0))

seq = create_raster_sequence((0,0), 10, 20)
# plt.scatter(*zip(*seq))
# plt.xlim([-5, 5])
# plt.ylim([-5, 5])
# plt.show()


new_seq = el.remove_points_outside_aperture(seq)
plt.plot(*zip(*new_seq), '-bo')
plt.xlim([-5, 5])
plt.ylim([-5, 5])
plt.show()


