import pygame
import math

Sframelist = {
    "Shooting": (35, 0),
    "Walk": (24, 0), 
    "Idle": (74, 0),
    "Recharge": (29, 0)
}
Sdirlist = [0, 45, 90, 135, 180, 225, 270, 315]
Stextures = {}
for state in Sframelist:
    for d in Sdirlist:
        Stextures[(state, d)] = (pygame.image.load(f"res/Soldier/{state}/{d}/tex.png"), pygame.image.load(f"res/Soldier/{state}/{d}/sample.png"))

class Soldier:
    def __init__(self, name, state, direction, pos, hp, damage):
        self.name = name
        self.state = state
        self.frameCounter = 0
        self.delayCounter = 0
        self.pos = list(pos)
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.damage = damage
        self.framelist = Sframelist
        self.dirlist = Sdirlist
        self.textures = Stextures
        
        self.direction = float(direction)
        self.precise_angle = 0
        self.speed = 0.5
        self.attack_range = 40
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
            frame_num, delay = self.framelist[self.state]
            tex, sample = self.textures[(self.state, visual_direction)]

            tex_w, tex_h = tex.get_size()
            frame_w, frame_h = sample.get_size()

            col = tex_w // frame_w
            row = tex_h // frame_h
            total_frames = col * row

            frame_index = self.frameCounter % min(frame_num, total_frames)

            rect_x = (frame_index % col) * frame_w
            rect_y = (frame_index // col) * frame_h
            rect = pygame.Rect(rect_x, rect_y, frame_w, frame_h)

            return tex.subsurface(rect)

        except Exception as e:
            print(f"[RunAnimation Error] {self.state} | frame={self.frameCounter} | err={e}")
            return None

    def Rotate(self, delta_angle):
        self.direction = (self.direction + delta_angle + 360) % 360

    def UpdateRotation(self, DESIRED_OFFSET=150, ROTATION_EPSILON=5.0):
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
        frame_num, delay = self.framelist[self.state]
        self.delayCounter += 1
        if self.delayCounter >= delay:
            self.delayCounter = 0
            self.frameCounter += 1
            self.frameCounter %= frame_num


    def SetState(self, state):
        if self.state == state: return
        self.state = state
        self.frameCounter = 0
        self.delayCounter = 0

    def TakeDamage(self, damage):
        self.hp -= damage
        if self.hp < 0: self.alive = False

    def AniDone(self):
        frame_num, delay = self.framelist[self.state]
        return self.frameCounter % frame_num == 0

    def draw_health_bar(self, screen, iso_x, iso_y, zoom_scale):
        base_bar_width = 30
        base_bar_height = 5
        base_y_offset = 10
        base_shield_y_offset = 17
        base_shield_height = 4
        base_main_castle_y_offset = 50

        scaled_bar_width = int(base_bar_width * zoom_scale)
        scaled_bar_height = max(1, int(base_bar_height * zoom_scale))
        scaled_y_offset = int(base_y_offset * zoom_scale)
        scaled_shield_y_offset = int(base_shield_y_offset * zoom_scale)
        scaled_shield_height = max(1, int(base_shield_height * zoom_scale))

        health_bar_y = iso_y - scaled_y_offset

        pygame.draw.rect(screen, (50, 50, 50), (iso_x - scaled_bar_width // 2, health_bar_y, scaled_bar_width, scaled_bar_height))

        ratio = self.hp / self.max_hp
        if ratio > 0.9:
            color = (0, 255, 0)       # 💚 Xanh lá
        elif ratio > 0.5:
            color = (255, 255, 0)     # 🟡 Vàng
        elif ratio > 0.2:
            color = (255, 150, 0)     # 🟠 Cam
        else:
            color = (255, 0, 0)       # 🔴 Đỏ

        pygame.draw.rect(screen, color, (iso_x - scaled_bar_width // 2, health_bar_y, int(scaled_bar_width * ratio), scaled_bar_height))