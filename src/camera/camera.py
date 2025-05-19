import glfw
import time
import numpy as np
from OpenGL.GL import *
from pyrr import Vector3, Matrix44, matrix44

class CAMERA:
    def __init__(
        self, window, camera_eye, camera_target, camera_up, camera_rot=[0.0, 0.0, 0.0]
    ):
        self.camera_eye = Vector3(camera_eye)
        self.camera_target = Vector3(camera_target)
        self.camera_up = Vector3(camera_up)
        self.camera_rot = Vector3(camera_rot)
        self.window = window
        self.start_time = time.time()

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
