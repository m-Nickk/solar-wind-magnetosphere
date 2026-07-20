import pygame
import math
from math import cos, sin, sqrt
import random

R_E = 0.4
R_S = 1.8
x_S = -5.0
m_diopole = 2.0
q_over_m = 2.5
v0 = 2.0
dt = 0.005
scale = 200
cam_x = -1.4

pygame.init()

def magnetic_field(x, y, z):
        r2 = x*x + y*y + z*z
        r = sqrt(r2)

        if r < 0.001:
            return 0, 0, 0

        r5 = r**5

        factor = 3 * m_diopole / r5 

        Bx = factor * x * z
        By = factor * y * z
        Bz = m_diopole * (3*z*z - r2) / r5

        return Bx, By, Bz
class Particle: 
    def __init__(self, x=0, y=0, z=0 , vx=0, vy=0, vz=0):
        self.x = x 
        self.y = y
        self.z = z
        self.vx = vx 
        self.vy = vy
        self.vz = vz
        self.alive = True
        self.history = []

    def update(self, dt, q_over_m):
        Bx, By, Bz = magnetic_field(self.x, self.y, self.z)
        ax = q_over_m * (self.vy * Bz - self.vz * By)
        ay = q_over_m * (self.vz * Bx - self.vx * Bz)
        az = q_over_m * (self.vx * By - self.vy * Bx)

        self.vx += ax * dt
        self.vy += ay * dt
        self.vz += az * dt

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        r = sqrt(self.x**2 + self.y**2 + self.z**2)

        self.history.append((self.x, self.z))

        if len(self.history) > 8:
            self.history.pop(0)

        if r < R_E or self.x > 10 or abs(self.z) > 8:
            self.alive = False

def create_particle():
    theta = random.uniform(-math.pi/2, math.pi/2)
    phi = random.uniform(-0.2, 0.2)

    x0 = x_S + R_S * cos(phi)
    y0 = R_S * sin(phi)
    z0 = R_S * sin(theta)

    vx = v0 + random.uniform(-0.02, 0.02)
    vy = random.uniform(-0.03, 0.03)
    vz = random.uniform(-0.03, 0.03)

    return Particle(x0, y0, z0, vx, vy, vz)

height = 720
width = 1280
center_x = width // 2
center_y = height // 2

screen = pygame.display.set_mode((1280, 720))

clock = pygame.time.Clock()
running = True

particles = []
for i in range(300):
    p = create_particle()

    start_x_surface = x_S + R_S
    p.x = random.uniform(start_x_surface, 10.0)

    p.history = [(p.x, p.z)]

    particles.append(p)   

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for i, p in enumerate(particles):
        p.update(dt, q_over_m)
        if not p.alive:
            particles[i] = create_particle()

    screen.fill((0, 0, 0))

    sun_center = (int((x_S - cam_x) * scale) + center_x, center_y)
    pygame.draw.circle(screen, (255, 255, 255), sun_center, int(R_S * scale))

    history_len = len(p.history)

    for p in particles:
        if p.y < 0:
            for i, (hist_x, hist_z) in enumerate(p.history):
                hx = int((hist_x - cam_x) * scale) + center_x
                hz = height//2 - int(hist_z * scale)

                depth_factor = 1.0 / (1.0 + abs(p.y) * 0.4)
                trail_factor = (i + 1) / max(1, history_len) 
                final_factor = depth_factor * trail_factor

                r_color = int(max(30, min(255, 255 * final_factor)))
                g_color = int(max(15, min(255, 120 * final_factor)))
                h_radius = int(max(1, 3 * final_factor))

                pygame.draw.circle(screen, (r_color, g_color, 0), (hx, hz), h_radius)

            px = int((p.x - cam_x) * scale) + center_x
            py = height//2 - int(p.z * scale)
            radius = max(1, int(3 / (1 + abs(p.y) * 0.3)))
            pygame.draw.circle(screen, (255, 165, 0), (px, py), radius)

    earth_center = (int((0 - cam_x) * scale) + center_x, center_y)
    pygame.draw.circle(screen, (100, 150, 255), earth_center, int(R_E * scale))

    for p in particles:
        if p.y >= 0:
            for i, (hist_x, hist_z) in enumerate(p.history):
                hx = int((hist_x - cam_x) * scale) + center_x
                hz = height//2 - int(hist_z * scale)

                depth_factor = 1.0 / (1.0 + abs(p.y) * 0.4)
                trail_factor = (i + 1) / max(1, history_len) 
                final_factor = depth_factor * trail_factor

                r_color = int(max(30, min(255, 255 * final_factor)))
                g_color = int(max(15, min(255, 120 * final_factor)))
                h_radius = int(max(1, 3 * final_factor))

                pygame.draw.circle(screen, (r_color, g_color, 0), (hx, hz), h_radius)

            px = int((p.x - cam_x) * scale) + center_x
            py = height//2 - int(p.z * scale)
            radius = max(1, int(3 / (1 + abs(p.y) * 0.3)))
            pygame.draw.circle(screen, (255, 165, 0), (px, py), radius)

    pygame.display.flip()

pygame.quit()
