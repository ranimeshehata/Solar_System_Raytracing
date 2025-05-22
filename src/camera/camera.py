import glfw
import time
import numpy as np
from OpenGL.GL import *
from pyrr import Vector3, Matrix44, matrix44

from ray_tracing.vectors import normalize

class CAMERA:
    def __init__(
        self, window, camera_eye, camera_target, camera_up, camera_rot=[0.0, 0.0, 0.0],width=1000,
        height=300,  
    ):
        self.camera_eye = Vector3(camera_eye)
        self.camera_target = Vector3(camera_target)
        self.camera_up = Vector3(camera_up)
        self.camera_rot = Vector3(camera_rot)
        self.window = window
        self.start_time = time.time()
        self.width = width  
        self.height = height  
        self.aspect_ratio = self.width / self.height 

    def _handle_input(self):
        current_time = time.time()
        delta_time = current_time - self.start_time
        self.start_time = current_time

        move_speed = 5.0 * delta_time
        rot_speed = 60.0 * delta_time

        forward = (self.camera_target - self.camera_eye).normalized
        right = np.cross(forward, self.camera_up).astype(np.float32)

        # Translation
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera_eye += forward * move_speed
            self.camera_target += forward * move_speed
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera_eye -= forward * move_speed
            self.camera_target -= forward * move_speed
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera_eye -= right * move_speed
            self.camera_target -= right * move_speed
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera_eye += right * move_speed
            self.camera_target += right * move_speed
        if glfw.get_key(self.window, glfw.KEY_Q) == glfw.PRESS:
            self.camera_eye -= self.camera_up * move_speed
            self.camera_target -= self.camera_up * move_speed
        if glfw.get_key(self.window, glfw.KEY_E) == glfw.PRESS:
            self.camera_eye += self.camera_up * move_speed
            self.camera_target += self.camera_up * move_speed

        # Rotation
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            self.camera_rot[0] += rot_speed
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            self.camera_rot[0] -= rot_speed
        if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
            self.camera_rot[1] += rot_speed
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.camera_rot[1] -= rot_speed
        if glfw.get_key(self.window, glfw.KEY_Z) == glfw.PRESS:
            self.camera_rot[2] += rot_speed
        if glfw.get_key(self.window, glfw.KEY_X) == glfw.PRESS:
            self.camera_rot[2] -= rot_speed

    def position_camera(self, view_loc):
        self._handle_input()

        view = Matrix44.look_at(
            eye=self.camera_eye, target=self.camera_target, up=self.camera_up
        )

        rotation_matrix = matrix44.multiply(
            matrix44.multiply(
                Matrix44.from_x_rotation(np.radians(self.camera_rot.x)),
                Matrix44.from_y_rotation(np.radians(self.camera_rot.y)),
            ),
            Matrix44.from_z_rotation(np.radians(self.camera_rot.z)),
        )

        view = matrix44.multiply(rotation_matrix, view)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    def get_view_matrix(self):
        """
        Returns the current view matrix (with rotation applied).
        """
        view = Matrix44.look_at(
            eye=self.camera_eye, target=self.camera_target, up=self.camera_up
        )
        rotation_matrix = matrix44.multiply(
            matrix44.multiply(
                Matrix44.from_x_rotation(np.radians(self.camera_rot.x)),
                Matrix44.from_y_rotation(np.radians(self.camera_rot.y)),
            ),
            Matrix44.from_z_rotation(np.radians(self.camera_rot.z)),
        )
        return matrix44.multiply(rotation_matrix, view)
    
    def get_ray(self, x, y, dx=0.5, dy=0.5, fov=60.0):
        # ndc from -1 , 1
        ndc_x = ((x + dx) / self.width) * 2.0 - 1.0
        ndc_y = 1.0 - ((y + dy) / self.height) * 2.0

        # ndc to viewport 
        scale = np.tan(np.radians(fov * 0.5))
        viewport_x = ndc_x * self.aspect_ratio * scale
        viewport_y = ndc_y * scale

        # ray in camera space
        ray_dir_camera = np.array([viewport_x, viewport_y, -1.0])
        ray_dir_camera = normalize(ray_dir_camera)

        # transform ray_dir_camera to world space
        forward = normalize(self.camera_target - self.camera_eye)
        right = normalize(np.cross(forward, self.camera_up))
        up = normalize(np.cross(right, forward))

        # construct world ray
        ray_dir_world = normalize(
            ray_dir_camera[0] * right +
            ray_dir_camera[1] * up +
            ray_dir_camera[2] * -forward  
        )

        return self.camera_eye, ray_dir_world