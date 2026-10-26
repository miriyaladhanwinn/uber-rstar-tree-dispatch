# Web trip simulator coordinate interpolation
# Author: Miriyala Dhanwin

def interpolate_trip(start, end, t):
    return (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)
