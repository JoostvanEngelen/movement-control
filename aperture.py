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


class RectangularAperture:
    def __init__(self, height, width, center: tuple, angle=0):
        self.aperture_shape = 'rectangular'
        self.width = width
        self.height = height
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

        half_width = self.width / 2
        half_height = self.height / 2

        return abs(xct) <= half_width and abs(yct) <= half_height

    def remove_points_outside_aperture(self, seq):
        safe_seq = []
        removed_points = []
        for point in seq:
            if self.point_inside_aperture(point):
                safe_seq.append(point)
            else:
                removed_points.append(point)
        return safe_seq
  
def raster_sequence_entire_plane(step_size):
    steps = np.arange(0, 300 + step_size, step_size)
    xscan = []
    yscan = []
    for i, yi in enumerate(steps):
        xscan.append(steps[::(-1)**i]) # reverse when i is odd
        yscan.append(np.ones_like(steps) * yi)
    xscan = np.concatenate(xscan)
    yscan = np.concatenate(yscan)
    sequence = []
    for i in range(len(xscan)):
        sequence.append((xscan[i], yscan[i]))
    return sequence

def raster_given_aperture(aperture:object, step_size):
    seq = raster_sequence_entire_plane(step_size)
    return aperture.remove_points_outside_aperture(seq)



# el = EllipcicalAperture(150, 150, (150,100), angle=0)
# # el = RectangularAperture(50, 150, (150,150), angle=45)







# # plt.scatter(*zip(*seq))
# # plt.xlim([-5, 305])
# # plt.ylim([-5, 305])
# # plt.grid()
# # plt.show()


# new_seq = raster_given_aperture(el, 10)
# plt.plot(*zip(*new_seq), '-bo')
# plt.xlim([-5, 305])
# plt.ylim([-5, 305])
# plt.grid()
# plt.show()


