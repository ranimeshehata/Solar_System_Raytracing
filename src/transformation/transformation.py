from objects.planet import Planet
from transformation.orbit import Orbit
import numpy as np
import pyrr
from OpenGL.GL import *
from effects.saturn_ring import SaturnRing

class Transform:
    def __init__(self, data, sectors, stacks):
        self.sectors = sectors
        self.stacks = stacks
        self.planets_data = data
        self.planets = []
        self.orbits = []
        self._init_planets()
        self.saturn_ring = saturn_ring = SaturnRing(
            inner_radius=0.4,
            outer_radius=0.8,
            texture_path="assets/texture/planets/saturn/saturn ring.png",
        )

    def _init_planets(self):
        # --- Initialize the planets and orbits ---
        for data in self.planets_data:
            if len(data) == 7:
                name, r, texture, orbit_radius, orbit_speed, rotation_speed, parent = (
                    data
                )
            else:
                name, r, texture, orbit_radius, orbit_speed, rotation_speed = data
                parent = None
            planet = Planet(
                r=r,
                texture_path=texture,
                sectors=self.sectors,
                stacks=self.stacks,
                rotation_speed=rotation_speed,
                orbit_radius=orbit_radius,
                orbit_speed=orbit_speed,
                parent=parent,
            )
            planet.name = name
            self.planets.append(planet)

            # Add orbit for planets that orbit the sun (not the sun itself or moons)
            if orbit_radius > 0 and parent is None:
                self.orbits.append(Orbit(orbit_radius))

    def place_planets(self, time_elapsed, model_loc, use_solid_color_loc, solid_color_loc, shader):
        glUseProgram(shader)
        for planet in self.planets:
            if planet.parent == "Earth":
                # Moon orbits Earth
                earth = next(p for p in self.planets if p.name == "Earth")
                earth_angle = earth.orbit_speed * time_elapsed
                earth_pos = np.array(
                    [
                        earth.orbit_radius * np.cos(earth_angle),
                        0,
                        earth.orbit_radius * np.sin(earth_angle),
                    ]
                )
                moon_angle = planet.orbit_speed * time_elapsed
                moon_pos = earth_pos + np.array(
                    [
                        planet.orbit_radius * np.cos(moon_angle),
                        0,
                        planet.orbit_radius * np.sin(moon_angle),
                    ]
                )
                pos = moon_pos
            else:
                angle = planet.orbit_speed * time_elapsed
                pos = np.array(
                    [
                        planet.orbit_radius * np.cos(angle),
                        0,
                        planet.orbit_radius * np.sin(angle),
                    ]
                )
            model_matrix = pyrr.matrix44.create_from_translation(pos)
            planet.draw(model_loc, model_matrix, time_elapsed, planet.rotation_speed)

            if planet.name == "Saturn":
                saturn_model_matrix = pyrr.matrix44.create_from_translation(pos)
                self.saturn_ring.draw(model_loc, saturn_model_matrix)

            # --- Draw atmosphere for Earth ---
            if planet.name == "Earth":
                glUseProgram(shader)
                # camera.position_camera(view_loc)
                glUniform1i(use_solid_color_loc, 1)  # Enable solid color
                glUniform3f(solid_color_loc, 0.8, 0.9, 1.0)  # Light blue
                planet.draw_atmosphere(model_loc, model_matrix)
                glUniform1i(use_solid_color_loc, 0)  # Restore to textured mode
        
    def place_orbits(self, shader, use_solid_color_loc, solid_color_loc, model_loc):
        glUseProgram(shader)
        glUniform1i(use_solid_color_loc, 1)  # Enable solid color
        glUniform3f(solid_color_loc, 0.6235, 0.6314, 0.6235)

        # Draw orbits
        for orbit in self.orbits:
            orbit.draw(model_loc)

        glUniform1i(use_solid_color_loc, 0)  # Restore to textured mode for planets

