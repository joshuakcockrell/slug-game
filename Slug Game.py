import os
import math
import pygame
import random
from pygame.locals import *
pygame.init()

class Vector():
    '''
        Class:
            creates operations to handle vectors such
            as direction, position, and speed
        '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self): # used for printing vectors
        return "(%s, %s)"%(self.x, self.y)

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("This "+str(key)+" key is not a vector key!")

    def __sub__(self, o): # subtraction
        return Vector(self.x - o.x, self.y - o.y)

    def length(self): # get length (used for normalize)
        return math.sqrt((self.x**2 + self.y**2)) 

    def normalize(self): # divides a vector by its length
        l = self.length()
        if l != 0:
            return (self.x / l, self.y / l)
        return None
    
class Slug(pygame.sprite.Sprite):

    def __init__(self, leafs):
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.state = 'ALIVE'
        self.images_normal = load_sliced_sprites(260, 200, os.path.join('resources', 'slugtileset.png'))
        self.dead_image = self.images_normal.pop()
        self.images_flipped = load_sliced_sprites(260, 200, os.path.join('resources', 'slugtilesetflipped.png'))
        self.dead_image_flipped = self.images_flipped.pop()
        self.images_normal.reverse()
        self.images_flipped.reverse()
        self.current_image = 0
        self.image_is_flipped = False

        self.image = self.images_normal[self.current_image]
        self.rect = self.image.get_rect()

        self.start = (1150,500)
        leafs_list = leafs.sprites()
        self.target = leafs_list[0].rect.center

        self.trueX = self.start[0]
        self.trueY = self.start[1]

        self.rect.center = (self.trueX, self.trueY)
        self.speed = 2
        self.speedX = 0
        self.speedY = 0

        self.starting_life = 2500
        self.life = self.starting_life
        self.health = 100
        self.life_bar = Life_Bar(self.starting_life, self.life, self.rect.center, self.image.get_height(), self.image.get_width())
        self.health_percent = 1
        
        self.inventory = []

    def get_hit(self):
        self.life -= 1
        if self.life <= 0:
            self.get_killed()
            self.state = 'KILLED'

    def get_killed(self):
        if self.image_is_flipped:
            self.image = self.dead_image_flipped
        else:
            self.image = self.dead_image
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.life_bar.is_dead()
        
    def get_direction(self, target):
        
        if self.target: # if the square has a target
            position = Vector(self.rect.centerx, self.rect.centery) # create a vector from center x,y value
            target = Vector(target[0], target[1]) # and one from the target x,y
            self.dist = target - position # get total distance between target and position

            direction = self.dist.normalize() # normalize so its constant in all directions
            return direction

    def distance_check(self, dist):
        
        dist_x = dist[0] ** 2 # gets absolute value of the x distance
        dist_y = dist[1] ** 2 # gets absolute value of the y distance
        t_dist = dist_x + dist_y # gets total absolute value distance
        speed = self.speed ** 2 # gets aboslute value of the speed

        if t_dist < (speed):
            return True

    def update(self, leafs):
        if self.state == 'ALIVE':
            if self.current_image == 10:
                self.current_image = 9 # compensate
            if self.image_is_flipped:
                self.image = self.images_flipped[self.current_image]
            else:
                self.image = self.images_normal[self.current_image - 1]
            self.image.set_colorkey(self.image.get_at((0,0)))
            
            self.dir = self.get_direction(self.target) # get direction
            if self.dir: # if there is a direction to move
                
                if self.distance_check(self.dist): # if we need to stop
                    self.rect.center = self.target # center the sprite on the target
                    
                else: # if we need to move normal
                    self.trueX += (self.dir[0] * self.speed) # calculate speed from direction to move and speed constant
                    self.trueY += (self.dir[1] * self.speed)
                    self.rect.center = (round(self.trueX),round(self.trueY)) # apply values to sprite.center

            for l in leafs:
                if self.rect.center == l.rect.center:
                    if len(self.inventory) <= 0:
                        l.get_picked_up()
                        self.inventory.append(l)
                        self.target = self.start
                        self.image_is_flipped = True

            if self.rect.center == self.start:
                if self.inventory:
                    self.state = 'DONE'
                

            for i in self.inventory:
                i.set_position(self.rect.center)

            self.life_bar.update(self.starting_life, self.life, self.rect.center) # GET A LIFE!!!

            #change animation image
            self.health_percent = float(self.life) / float(self.starting_life)
            self.current_image = int((self.health_percent * 10) * 0.9)
        else:
            self.image.set_colorkey(self.image.get_at((0,0)))


class SaltShaker(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load(os.path.join('resources', 'saltshaker.png')).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.TIME_BETWEEN_SALT = 1
        self.time_between_salt = self.TIME_BETWEEN_SALT


        self.previous_position = pygame.mouse.get_pos()
        self.rect.center = pygame.mouse.get_pos()

        self.lid_width = 35

    def set_position(self, position):
        self.previous_position = self.rect.center
        self.rect.center = position

    def _dispense_salt(self):
        vector_prev = Vector(self.previous_position[0], self.previous_position[1])
        vector_curr = Vector(self.rect.centerx, self.rect.centery)

        dist_traveled = vector_curr - vector_prev

        # code for deciding the speed of the salt when it is despensed
        # and code for deciding how much salt to dispense
        X_traveled = dist_traveled[0]
        Y_traveled = dist_traveled[1]
        X_traveled_squared = X_traveled ** 2
        Y_traveled_squared = Y_traveled ** 2
        total_squared_distance = X_traveled_squared + Y_traveled_squared
        total_distance = math.sqrt(total_squared_distance)
        
        direction = dist_traveled.normalize()

        #create an ammount of salt
        ammount_of_salt = total_distance * 100 #/ 1#15
        for number in range(0,int(ammount_of_salt)):
            ammount_of_salt -= 1

            # get random position
            random_width = random.randrange(0,self.lid_width)
            random_width *= random.choice([-1,1])
            Xposition_of_salt = (self.rect.centerx + random_width)

            # get random speed
            random_number = (random.random() * 15)
            random_number *= random.choice([-1,1])
            total_distance += random_number
            
            SaltParticle((Xposition_of_salt, self.rect.centery + 50), direction, total_distance)
        
             
    def update(self):
        self.time_between_salt -= 1
        if self.time_between_salt <= 0:
            self.time_between_salt = self.TIME_BETWEEN_SALT
            self._dispense_salt()
        

class SaltParticle(pygame.sprite.Sprite):

    def __init__(self, position, direction, speed):
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load(os.path.join('resources', 'salt.png')).convert()
        self.rect = self.image.get_rect()
        self.trueX = position[0]
        self.trueY = position[1]
        self.rect.center = (self.trueX, self.trueY)

        if direction == None:
            direction = (0,0)
        speed *= .01
        self.speedX = (direction[0] * speed)
        self.speedY = (direction[1] * speed)
        self.direction = direction
        self.speed = speed

        self.air_resistance = .95
        self.gravity_speed = .3


    def update(self):

        self.speedX += (self.direction[0] * self.speed)
        self.speedY += (self.direction[1] * self.speed)
        self.speedX *= self.air_resistance
        self.speedY *= self.air_resistance
        self.speedY += self.gravity_speed

        self.trueX += self.speedX
        self.trueY += self.speedY
        self.rect.center = (round(self.trueX),round(self.trueY)) # apply values to sprite.center

        self.speedY += self.gravity_speed
        self.speed *= self.air_resistance

        #check if went out of bounds
        if self.rect.centery >= 650: # bottom of screen + 50
            self.kill()

    def collision_check(self, slug):
        hit_slug = pygame.sprite.collide_rect(self, slug)
        if hit_slug:
            slug.get_hit()
            self.kill()
        
    
class Leaf(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load(os.path.join('resources', 'leaf.png')).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(self.image.get_at((0,0)))

        self.rect.center = (150,500)

        self.part_of_host_inventory = False

    def get_picked_up(self):
        self.part_of_host_inventory = True

    def set_position(self, position):
        self.rect.center = position
          

class Life_Bar(pygame.sprite.Sprite):
    
    def __init__(self, starting_life, life, position, height, width):
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.bar_height = 4
        self.bar_width = (width - 40)
        self.health_percent = starting_life / life
        
        self.image = pygame.Surface((self.bar_width, self.bar_height))
        self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.host_height = height
        self.host_width = width
        
        self.rect.center = (position[0], position[1])
        self.starting_life = starting_life
        
    def is_dead(self):
        self.kill()
        
    def update(self, starting_life, life, position):
        self.health_percent = starting_life / float(life)
        
        self.image.fill((255,0,0)) # fill with red
        self.image.fill((255,255,255), # green
                    (0,0,(self.bar_width / self.health_percent), self.bar_height)) # size of green

        self.rect.center = position[0], (position[1] - (self.host_height / 2))

def load_sliced_sprites(w, h, filename):
    '''
    Function:
        Takes one big image and cuts it into smaller
        pieces to be used for animation
    Specs :
        Master can be any height.
        Sprites frames width must be the same width
        Master width must be len(frames)*frame.width
    '''
    images = [] # create empty images list
    master_image = pygame.image.load(os.path.join('', filename)).convert() # load image to be cut

    master_width, master_height = master_image.get_size() # get full image sixe
    for i in xrange(int(master_width/w)): # cut the image up
        images.append(master_image.subsurface((i*w,0,w,h))) # add images to list
    return images # sent the images list


def main():

    running_game = True
    while running_game:
        
        screen = pygame.display.set_mode((1000,600))
        pygame.display.set_caption('Slug Game')

        slugs = pygame.sprite.GroupSingle()
        life_bars = pygame.sprite.Group()
        leafs = pygame.sprite.Group()
        shakers = pygame.sprite.Group()
        salts = pygame.sprite.Group()

        Slug.groups = slugs
        Life_Bar.groups = life_bars
        Leaf.groups = leafs
        SaltShaker.groups = shakers
        SaltParticle.groups = salts
        
        background_image = pygame.image.load(os.path.join('resources', 'background.png')).convert() # load image
        Leaf()
        saltshaker = SaltShaker()
        slug = Slug(leafs)

        clock = pygame.time.Clock()

        running = True
        end_game_timer = 90

        while running:
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    quit_type = 'FULL'


            if slug.state == 'KILLED':
                end_game_timer -= 1
                if end_game_timer <=0:
                    running = False
                    quit_type = 'RESTART'

            if slug.state == 'DONE':
                running = False
                quit_type = 'RESTART'
                

            saltshaker.update()
            slug.update(leafs)
            salts.update()
            for s in salts:
                s.collision_check(slug)
                
            saltshaker.set_position(pygame.mouse.get_pos())
            
            screen.blit(background_image, (0,0))
            slugs.draw(screen)
            shakers.draw(screen)
            life_bars.draw(screen)
            leafs.draw(screen)
            salts.draw(screen)

            pygame.display.flip()

        if quit_type == 'FULL':
            running_game = False

        elif quit_type == 'RESTART':
            pass


if __name__ == '__main__':
    main()
    pygame.quit()
