import pygame
import random
import sys
import noise
import math

pygame.init()

# Low-res pixel grid
PIXEL_WIDTH, PIXEL_HEIGHT = 100, 100
pixel_surface = pygame.Surface((PIXEL_WIDTH, PIXEL_HEIGHT), pygame.SRCALPHA)

# Display scale
SCALE = 4
WINDOW_WIDTH = PIXEL_WIDTH * SCALE
WINDOW_HEIGHT = PIXEL_HEIGHT * SCALE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pastel Planet with Curved Shadow and City Lights")

# Pastel colors
WATER = (160, 196, 255)
BEACH = (255, 214, 165)
LAND = (181, 234, 215)
MOUNTAIN = (199, 206, 234)
SNOW = (255, 255, 255)
CLOUD = (255, 255, 255, 70)
CITY_LIGHT = (255, 245, 186)
SPACE = (25, 5, 35)

# Planet core settings
rotation = 0.0
rotation_speed = 0.01
clock = pygame.time.Clock()

# Noise seeds
seed = random.randint(0, 10000)
cloud_seed = random.randint(0, 10000)
light_seed = random.randint(0, 10000)
planet_radius = random.randint(25, 40)

def generate_planet(rotation_offset):
    pixel_surface.fill(SPACE)

    cx, cy = PIXEL_WIDTH // 2, PIXEL_HEIGHT // 2
    terrain_scale = 0.07
    cloud_scale = 0.4
    light_map_scale = 0.3

    for y in range(PIXEL_HEIGHT):
        for x in range(PIXEL_WIDTH):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist > planet_radius:
                continue  # outside the circle

            # Elevation noise
            nx = (x + rotation_offset) * terrain_scale
            ny = y * terrain_scale
            elevation = noise.pnoise2(nx + seed, ny + seed, octaves=6, persistence=0.5, lacunarity=2.0)
            norm = elevation + 0.5

            # City light map noise (stable)
            light_val = noise.pnoise2(nx + light_seed, ny + light_seed, octaves=2)

            # Determine base terrain color
            if norm < 0.5:
                shimmer = noise.pnoise2((x + rotation * 100) * 0.2, (y + rotation * 100) * 0.2, octaves=1)
                shimmer = (shimmer + 0.5) * 0.03

                wave = math.sin(x * 0.3 + rotation * 5) * 0.01 + math.sin(y * 0.2 + rotation * 3) * 0.1

                brightness = min(max(0.8 + shimmer + wave, 0.5), 0.8)
                base_color = tuple(int(c * brightness) for c in WATER)

            elif norm < 0.55:
                base_color = BEACH
            elif norm < 0.75:
                base_color = LAND
            elif norm < 0.85:
                base_color = MOUNTAIN
            else:
                base_color = SNOW

            # Curved shadow line (cos wave offset by y)
            wave_phase = rotation * 2
            shadow_center_x = cx + math.cos(wave_phase + math.radians(y)) * 8  # subtle curve
            is_day = x < shadow_center_x

            # Lighting effects
            if not is_day:
                # Darken color for night
                darkness = 0.3
                base_color = tuple(int(c * darkness) for c in base_color)

                # Add soft, stable city light
                if 0.45 <= norm < 0.85 and light_val > 0.25:
                    base_color = CITY_LIGHT

            # Apply terrain color
            pixel_surface.set_at((x, y), base_color)

            # Clouds (subtle)
            cloud_val = noise.pnoise2((x + rotation_offset * 1.5) * cloud_scale,
                                      y * cloud_scale + cloud_seed,
                                      octaves=3)
            if cloud_val > 0.3:
                alpha = 80 if is_day else 50
                pixel_surface.set_at((x, y), (*CLOUD[:3], alpha))

    # Scale up and draw
    scaled = pygame.transform.scale(pixel_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

# Initial render
generate_planet(rotation)

# Main loop
running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # New random planet
                seed = random.randint(0, 10000)
                cloud_seed = random.randint(0, 10000)
                light_seed = random.randint(0, 10000)
                planet_radius = random.randint(35, 50)
                rotation = 0

    generate_planet(rotation)
    rotation += rotation_speed

pygame.quit()
sys.exit()
