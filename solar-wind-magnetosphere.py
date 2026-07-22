import pygame
import math
from math import cos, sin, sqrt
import random
import numpy as np

R_E = 0.4
R_S = 1.8
x_S = -5.0
m_diopole = 0.08
v0 = 3.5
dt = 0.005
scale = 200
cam_x = -1.4

pygame.init()

def magnetic_field(x, y, z):
    r2 = x*x + y*y + z*z
    r = sqrt(r2)
    if r < 0.001: return 0, 0, 0

    r5 = r**5

    if x < 0:
        compression_factor = 1.0 + 5.0 * ((2.2 - r) / 2.2)
    else:
        compression_factor = 1.0 / (1.0 + 0.5 * x)
    compression_factor = np.clip(compression_factor, 0.1, 10.0)

    effective_m = m_diopole * compression_factor
    
    B_sw_x = -0.02
    B_sw_y = 0.002
    B_sw_z = -0.01

    Bx = -3 * effective_m * x * z / r5
    By = -3 * effective_m * y * z / r5
    Bz = -effective_m * (3 * z * z - r2) / r5

    return Bx + B_sw_x, By + B_sw_y, Bz + B_sw_z

class Particle: 
    def __init__(self, x=0, y=0, z=0, vx=0, vy=0, vz=0):
        self.x = x 
        self.y = y
        self.z = z
        self.vx = vx 
        self.vy = vy
        self.vz = vz
        self.alive = True
        self.history = []
        
        if random.random() < 0.5:
            self.q_over_m = 4.0
            self.color = (255, 100, 100)
        else:
            self.q_over_m = -40.0
            self.color = (100, 100, 255)

    def update(self, dt):
        Bx, By, Bz = magnetic_field(self.x, self.y, self.z)

        vx_minus = self.vx
        vy_minus = self.vy
        vz_minus = self.vz

        t_x = 0.5 * self.q_over_m * Bx * dt
        t_y = 0.5 * self.q_over_m * By * dt
        t_z = 0.5 * self.q_over_m * Bz * dt
        t2 = t_x**2 + t_y**2 + t_z**2

        s_x = 2 * t_x / (1 + t2)
        s_y = 2 * t_y / (1 + t2)
        s_z = 2 * t_z / (1 + t2)

        cx = vy_minus * t_z - vz_minus * t_y
        cy = vz_minus * t_x - vx_minus * t_z
        cz = vx_minus * t_y - vy_minus * t_x

        vx_prime = vx_minus + cx
        vy_prime = vy_minus + cy
        vz_prime = vz_minus + cz

        self.vx = vx_minus + (vy_prime * s_z - vz_prime * s_y)
        self.vy = vy_minus + (vz_prime * s_x - vx_prime * s_z)
        self.vz = vz_minus + (vx_prime * s_y - vy_prime * s_x)

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        r = sqrt(self.x**2 + self.y**2 + self.z**2)
        self.history.append((self.x, self.z))

        if len(self.history) > 15:
            self.history.pop(0)

        if r < R_E or self.x > 10 or abs(self.z) > 500:
            self.alive = False

def create_particle():
    theta = random.uniform(-math.pi/2, math.pi/2)
    phi = random.uniform(-0.3, 0.3)

    x0 = x_S + R_S * cos(phi)
    y0 = R_S * sin(phi)
    z0 = R_S * sin(theta)

    vx = v0 + random.uniform(0.1, 0.5)
    vy = random.uniform(-0.02, 0.02)
    vz = random.uniform(-0.02, 0.02)

    return Particle(x0, y0, z0, vx, vy, vz)

height = 720
width = 1280
center_x = width // 2
center_y = height // 2

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

particles = []
for i in range(200):
    p = create_particle()
    start_x_surface = x_S + R_S
    p.x = random.uniform(start_x_surface, 10.0)
    p.history = [(p.x, p.z)]
    particles.append(p)   

field_lines_pixels = []
for r_max in np.linspace(0.6, 3.2, 12):
    for sign_z in [1, -1]:
        line_points = []

        for angle_deg in np.linspace(10, 170, 260):
            rad = math.radians(angle_deg)
            
            r_base = r_max * (sin(rad) ** 2)
            cx = r_base * (-cos(rad))  
            cz = r_base * sin(rad) * sign_z
            
            if cx < 0:
                cx *= 1.45
                cz *= 0.55
            else:
                cx *= 3.0
                tail_flattening = 1.0 / (1.0 + 0.4 * cx)
                cz *= 0.48 * tail_flattening

            px = int((cx - cam_x) * scale) + center_x
            py = center_y - int(cz * scale)
            
            if 0 <= py <= height:
                line_points.append((px, py))
                if px > width:
                    break
            else:
                break
                
        if len(line_points) > 1:
            field_lines_pixels.append(line_points)

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for i, p in enumerate(particles):
        p.update(dt)
        if not p.alive:
            particles[i] = create_particle()

    screen.fill((10, 10, 15))

    sun_center = (int((x_S - cam_x) * scale) + center_x, center_y)
    pygame.draw.circle(screen, (255, 255, 220), sun_center, int(R_S * scale))

    earth_center = (int((0 - cam_x) * scale) + center_x, center_y)

    render_queue = []
    render_queue.append({"type": "earth", "z_depth": 9999, "pos": earth_center})

    for p in particles:
        render_queue.append({"type": "particle", "z_depth": p.y, "obj": p})

    for points in field_lines_pixels:
        render_queue.append({"type": "field_line", "z_depth": 9998, "points": points})

    render_queue.sort(key=lambda item: item["z_depth"])

    for item in render_queue:
        if item["type"] == "field_line":
            points = item["points"]
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i+1]
                color = (90, 25, 25) if p1[0] < 960 else (0, 70, 100)
                pygame.draw.line(screen, color, p1, p2, 1)

        elif item["type"] == "particle":
            p = item["obj"]
            history_len = len(p.history)

            for i, (hist_x, hist_z) in enumerate(p.history):
                hx = int((hist_x - cam_x) * scale) + center_x
                hz = height // 2 - int(hist_z * scale)

                depth_factor = 1.0 / (1.0 + abs(p.y) * 0.4)
                trail_factor = (i + 1) / max(1, history_len)

                final_factor = depth_factor * trail_factor

                r_color = int(max(20, min(255, p.color[0] * final_factor)))
                g_color = int(max(20, min(255, p.color[1] * final_factor)))
                b_color = int(max(20, min(255, p.color[2] * final_factor)))

                h_radius = int(max(1, 3 * final_factor))

                pygame.draw.circle(screen, (r_color, g_color, b_color), (hx, hz), h_radius)

            px = int((p.x - cam_x) * scale) + center_x
            py = height // 2 - int(p.z * scale)
            radius = max(1, int(3 / (1 + abs(p.y) * 0.3)))
            pygame.draw.circle(screen, p.color, (px, py), radius)

        elif item["type"] == "earth":
            pygame.draw.circle(screen, (100, 150, 255), item["pos"], int(R_E * scale))

    pygame.display.flip()

pygame.quit()
