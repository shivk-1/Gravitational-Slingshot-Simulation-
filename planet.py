import pygame
import math

pygame.init()

screen_width, screen_height = 800, 600
surface = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gravitational Slingshot Effect Simulation ")

mass_planet = 100
mass_ship = 5
gravity_constant = 5
frame_rate = 60
radius_planet = 70
radius_meteor = 30
radius_object = 5
velocity_scale = 100

background_image = pygame.transform.scale(pygame.image.load("space.png"), (screen_width, screen_height))
planet_image = pygame.transform.scale(pygame.image.load("planet.png"), (radius_planet * 2, radius_planet * 2))
meteor_image = pygame.transform.scale(pygame.image.load("meteor.png"), (radius_meteor * 2, radius_meteor * 2))
explosion_image = pygame.transform.scale(pygame.image.load("explosion.png"), (radius_planet * 2, radius_planet * 2))

pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("boom.mp3")

color_white = (255, 255, 255)

class CelestialBody:
    def __init__(self, x, y, mass):
        self.position_x = x
        self.position_y = y
        self.mass = mass
    
    def render(self):
        surface.blit(planet_image, (self.position_x - radius_planet, self.position_y - radius_planet))

class Spacecraft:
    def __init__(self, x, y, velocity_x, velocity_y, mass):
        self.position_x = x
        self.position_y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.mass = mass

    def update_position(self, planet=None):
        distance = math.sqrt((self.position_x - planet.position_x)**2 + (self.position_y - planet.position_y)**2)
        gravitational_force = (gravity_constant * self.mass * planet.mass) / distance ** 2
        
        acceleration = gravitational_force / self.mass
        angle = math.atan2(planet.position_y - self.position_y, planet.position_x - self.position_x)

        acceleration_x = acceleration * math.cos(angle)
        acceleration_y = acceleration * math.sin(angle)

        self.velocity_x += acceleration_x
        self.velocity_y += acceleration_y

        self.position_x += self.velocity_x
        self.position_y += self.velocity_y
    
    def render(self):
        surface.blit(meteor_image, (int(self.position_x - radius_meteor), int(self.position_y - radius_meteor)))

def create_spacecraft(initial_position, mouse_position):
    start_x, start_y = initial_position
    target_x, target_y = mouse_position
    velocity_x = (target_x - start_x) / velocity_scale
    velocity_y = (target_y - start_y) / velocity_scale
    spacecraft = Spacecraft(start_x, start_y, velocity_x, velocity_y, mass_ship)
    return spacecraft

def main():
    running = True
    clock = pygame.time.Clock()

    planet = CelestialBody(screen_width // 2, screen_height // 2, mass_planet)
    spacecrafts = []
    temp_spacecraft_position = None
    explosions = []

    while running:
        clock.tick(frame_rate)

        mouse_position = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if temp_spacecraft_position:
                    spacecraft = create_spacecraft(temp_spacecraft_position, mouse_position)
                    spacecrafts.append(spacecraft)
                    temp_spacecraft_position = None
                else:
                    temp_spacecraft_position = mouse_position

        surface.blit(background_image, (0, 0))

        if temp_spacecraft_position:
            pygame.draw.line(surface, color_white, temp_spacecraft_position, mouse_position, 2)
            surface.blit(meteor_image, (temp_spacecraft_position[0] - radius_meteor, temp_spacecraft_position[1] - radius_meteor))
        
        for spacecraft in spacecrafts[:]:
            spacecraft.render()
            spacecraft.update_position(planet)
            out_of_bounds = spacecraft.position_x < 0 or spacecraft.position_x > screen_width or spacecraft.position_y < 0 or spacecraft.position_y > screen_height
            collision = math.sqrt((spacecraft.position_x - planet.position_x)**2 + (spacecraft.position_y - planet.position_y)**2) <= radius_planet
            if collision:
                # Calculate the surface point for the explosion
                angle = math.atan2(spacecraft.position_y - planet.position_y, spacecraft.position_x - planet.position_x)
                explosion_x = planet.position_x + radius_planet * math.cos(angle)
                explosion_y = planet.position_y + radius_planet * math.sin(angle)
                explosions.append((explosion_x, explosion_y, pygame.time.get_ticks()))
                explosion_sound.play()
                spacecrafts.remove(spacecraft)
            elif out_of_bounds:
                spacecrafts.remove(spacecraft)

        current_time = pygame.time.get_ticks()
        explosions = [(x, y, start_time) for x, y, start_time in explosions if current_time - start_time <= 1500]

        for explosion in explosions:
            explosion_x, explosion_y, _ = explosion
            surface.blit(explosion_image, (explosion_x - radius_planet, explosion_y - radius_planet))

        planet.render()

        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()
