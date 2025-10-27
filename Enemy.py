import pygame
import math

Zframelist = {
    "Attack": (4, 5, 0), "Death": (6, 4, 0), "Hit": (4, 4, 0),
    "Idle": (4, 5, 0), "Lookup": (6, 5, 0), "Roar": (6, 4, 0),
    "Run": (4, 5, 0),
}
Zdirlist = [0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337]
Ztextures = {}
for state in Zframelist:
    for d in Zdirlist:
        Ztextures[(state, d)] = pygame.image.load(f"res/Zombie/{state}/{state} Body {d}.png")

class Enemy:
    def __init__(self, name, state, direction, pos, hp, damage):
        self.name = name
        self.state = state
        self.frameCounter = 0
        self.delayCounter = 0
        self.pos = list(pos)
        self.hp = hp
        self.alive = True
        self.damage = damage
        self.framelist = Zframelist
        self.dirlist = Zdirlist
        self.textures = Ztextures
        
        self.direction = float(direction)
        self.precise_angle = 0
        
        self.speed = 0.5
        self.attack_range = 6.0
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        self.rotation_speed = 5.0

    def find_closest_visual_direction(self):
        def angle_diff(a1, a2):
            diff = abs(a1 - a2)
            return min(diff, 360 - diff)
        return min(self.dirlist, key=lambda d: angle_diff(d, self.precise_angle))

    def RunAnimation(self):
        try:
            visual_direction = self.find_closest_visual_direction()
            col, row, delay = self.framelist[self.state]
            tex = self.textures[(self.state, visual_direction)]
            width, height = tex.get_size()
            framesize = (width // col, height // row)
            rect = pygame.Rect(self.frameCounter % col * framesize[0], self.frameCounter // col * framesize[1], framesize[0], framesize[1])
            return tex.subsurface(rect)
        except:
            print(self.state, rect)

    def Rotate(self, delta_angle):
        self.direction = (self.direction + delta_angle + 360) % 360

    def UpdateRotation(self, DESIRED_OFFSET=290.0, ROTATION_EPSILON=5.0):
        max_iterations = 72  
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            current_offset = (self.direction - self.precise_angle + 360) % 360
            
            distance_to_target_offset = abs(current_offset - DESIRED_OFFSET)
            if distance_to_target_offset > 180:
                distance_to_target_offset = 360 - distance_to_target_offset
            
            if distance_to_target_offset <= ROTATION_EPSILON:
                break
            
            offset_error = DESIRED_OFFSET - current_offset
            if offset_error > 180: 
                offset_error -= 360
            elif offset_error < -180: 
                offset_error += 360
            
            turn_direction = math.copysign(1, -offset_error)
            self.precise_angle = (self.precise_angle + self.rotation_speed * turn_direction + 360) % 360

    def UpdateCounter(self):
        c, r, delay = self.framelist[self.state]
        self.delayCounter += 1
        if self.delayCounter >= delay:
            self.delayCounter = 0
            self.frameCounter += 1

            if self.state == "Death":
                if self.frameCounter >= c * r:
                    self.frameCounter %= c * r
                    self.alive = False
                    return 
            self.frameCounter %= c * r


    def SetState(self, state):
        if self.state == state: return
        self.state = state
        self.frameCounter = 0
        self.delayCounter = 0

    def TakeDamage(self, damage):
        self.hp -= damage
        if self.hp > 0:
            self.SetState("Roar")
        else:
            if self.state != "Death":
                self.SetState("Death")

    def AniDone(self):
        c, r, delay = self.framelist[self.state]
        return self.frameCounter % (c * r) == 0