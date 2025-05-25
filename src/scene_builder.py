import numpy as np
from utils.json_parser import parse_json

PLANET_DATA = [
    # name, radius, texture, orbit_radius, orbit_speed, rotation_speed, parent
    ("Sun",     1.0,    "assets/texture/sun.png",                    0.0,       0.0,         0.04),
    ("Mercury", 0.35,   "assets/texture/planets/mer_nasa.png",       2.0,       4.15,        0.3),
    ("Venus",   0.38,   "assets/texture/planets/ven_nasa.jpg",       3.0,       1.62,        0.2),
    ("Earth",   0.40,   "assets/texture/planets/earth_nasa.png",     4.0,       1.0,         0.5),
    ("Mars",    0.37,   "assets/texture/planets/mars_nasa.jpg",      5.5,       0.53,        0.4),
    ("Jupiter", 0.60,   "assets/texture/planets/jupiter.png",        7.5,       0.08,        0.6),
    ("Saturn",  0.55,   "assets/texture/planets/saturn/saturn.png",  9.0,       0.03,        0.7),
    ("Uranus",  0.48,   "assets/texture/planets/uranus.png",         11.0,      0.011,       0.8),
    ("Neptune", 0.47,   "assets/texture/planets/nep_nasa.jpg",       13.0,      0.006,       0.9),
    ("Moon",    0.27,   "assets/texture/moon.png",                   0.5,       12.0,        1.0,             "Earth"),
]

def get_camera_config():
    time, eye, target, up = parse_json()
    return time, eye, target, up

def calculate_planet_position(planet, t, planets_dict=None):
    name, radius, texture, orbit_radius, orbit_speed, rotation_speed = planet[:6]
    parent = planet[6] if len(planet) == 7 else None

    if parent:
        parent_planet = planets_dict[parent]
        parent_pos = calculate_planet_position(parent_planet, t, planets_dict)
        angle = orbit_speed * t
        pos = parent_pos + np.array([
            orbit_radius * np.cos(angle),
            0,
            orbit_radius * np.sin(angle),
        ])
    else:
        angle = orbit_speed * t
        pos = np.array([
            orbit_radius * np.cos(angle),
            0,
            orbit_radius * np.sin(angle),
        ])
    return pos

def build_planet_dict():
    return {p[0]: p for p in PLANET_DATA}