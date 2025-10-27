import pygame
import sys
class Tower:
    def __init__(self, x, y, z, tex_id, shield = False, shield_hp = 100, hp = 300, is_main = False, damage = 30):
        self.x = x
        self.y = y
        self.z = z
        self.pos = (x, y, z)
        self.is_main = is_main
        self.hp = hp
        self.max_hp = self.hp
        self.shield = shield  
        self.shield_hp = shield_hp # 💙 lượng máu khiên
        self.max_shield_hp = shield_hp   
        self.tex_id = tex_id
        self.destroyed = False
        self.footprint_w = 2  # số tile rộng
        self.footprint_d = 2  # số tile sâu
        self.height = 2       # số tile cao
        self.attack_range = 65.0
        self.attack_cooldown = 1000
        self.last_attack_time = 0
        self.damage = damage

    def damage_tower(self, dmg):
        if self.hp <= 0:
            self.destroyed = True # << ĐÁNH DẤU LÀ ĐÃ BỊ PHÁ HỦY
            return

        if self.shield and self.shield_hp > 0:
            self.shield_hp = max(0, self.shield_hp - dmg)
            if self.shield_hp <= 0:
                self.shield = False  
                return

        if not self.shield: self.hp = max(0, self.hp - dmg)

    def draw_health_bar(self, screen, iso_x, iso_y, zoom_scale):
        base_bar_width = 30 if not self.is_main else 80
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

        if self.is_main:
            iso_y -= int(base_main_castle_y_offset * zoom_scale)

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

        if self.is_main and self.shield_hp > 0:
            shield_bar_y = iso_y - scaled_shield_y_offset
            ratio_s = self.shield_hp / self.max_shield_hp
            pygame.draw.rect(screen, (0, 200, 255), (iso_x - scaled_bar_width // 2, shield_bar_y, int(scaled_bar_width * ratio_s), scaled_shield_height))