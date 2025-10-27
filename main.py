import os
import pygame
import sys
import random
import math
import Enemy
import Soldier
import Tower
from Audio import AudioManager
from Spatial import SpatialGrid
from config import *
def include(path):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, globals())
include("Renderer.py")
include("AIManager.py")

pygame.init()
pygame.mixer.init()
pygame.font.init() # Đảm bảo module font đã được khởi tạo
DEBUG_FONT = pygame.font.SysFont('Arial', 14)
sub_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")
SHIELD_DOME_TEXTURE = pygame.image.load("res/shield_dome_iso.png").convert_alpha()
GTEXTURE = pygame.image.load("res/grass.png").convert_alpha()
C1TEXTURE = pygame.image.load("res/castle/Castle1.png")
C2TEXTURE = pygame.image.load("res/castle/Castle2.png")
C3TEXTURE = pygame.image.load("res/castle/Castle3.png")
C4TEXTURE = pygame.image.load("res/castle/Castle4.png")
C5TEXTURE = pygame.image.load("res/castle/Castle5.png")
C6TEXTURE = pygame.image.load("res/castle/Castle6.png")
audio = AudioManager()
shoot_sound = pygame.mixer.Sound("res/sound/shoot.wav")
shoot_sound.set_volume(0.04)
background_playlist = ["res/music/background_music.ogg", 
                       "res/music/background_music1.ogg",
                       "res/music/background_music2.ogg",
                       "res/music/background_music3.ogg",
                       "res/music/background_music4.ogg",
                       "res/music/background_music5.ogg",
                       "res/music/background_music6.ogg",
                       ]
audio.set_playlist(random.sample(background_playlist, len(background_playlist)), volume=0.5)
audio.play_next()
clock = pygame.time.Clock()
grid = SpatialGrid()
main_cnt = True
setup_phase = True
tower_alive_cnt = 0
zoom_scale = 1
TILE_RECTS = {}
SCALED_TEX = {}
setup_timer_start = 0
round_number = 1
towers_to_place = 2
soldier_to_spawn = 2
game_state = "playing"
object_list = {}
drawn_list = []
enemy_list = []
castle_list = []
soldier_list = []


castle_definitions = {
    (0, 0, 0): 20, 

    
    (0, 0, 9): 33,
    (9, 0, 0): 34,
    (0, 0, -9): 35,
    (-9, 0, 0): 32,

   
    (9, 0, 9): 18,
    (9, 0, -9): 16,
    (-9, 0, -9): 16,
    (-9, 0, 9): 18,
}


def Init():
    object_list.clear()
    enemy_list.clear()
    castle_list.clear()

    for x in range(-GRID_SIZE//2, GRID_SIZE//2):
        for z in range(-GRID_SIZE//2, GRID_SIZE//2):
            object_list[(x * GRASS_SCALE, 0, z * GRASS_SCALE)] = 1

    for (x, y, z), tex_id in castle_definitions.items():
        is_main_castle = (x == 0 and y == 0 and z == 0)
        tower = Tower.Tower(
            x * 2, y + 1, z * 2, tex_id, 
            shield=is_main_castle, 
            shield_hp=1000 if is_main_castle else 0, 
            hp=2000 if is_main_castle else 500, 
            is_main = is_main_castle,
            damage = 100
        )
        castle_list.append(tower)

    for tower in castle_list:
        if not tower.destroyed:
            object_list[tower.pos] = tower
    
    castle_rects = [get_screen_rect(t) for t in castle_list]
    
    newly_spawned = []
    for _ in range(NUM_ENEMIES):
        while True:
            x_3d = random.choice([random.randint(-GRID_SIZE//2 * GRASS_SCALE, -GRID_SIZE//4 * GRASS_SCALE), random.randint(GRID_SIZE//4 * GRASS_SCALE, GRID_SIZE//2 * GRASS_SCALE)])
            z_3d = random.choice([random.randint(-GRID_SIZE//2 * GRASS_SCALE, -GRID_SIZE//4 * GRASS_SCALE), random.randint(GRID_SIZE//4 * GRASS_SCALE, GRID_SIZE//2 * GRASS_SCALE)])
            
            temp_enemy = Enemy.Enemy("temp", "Idle", 0, (x_3d, 1, z_3d), 1, 1)
            temp_enemy_rect = get_screen_rect(temp_enemy)
            
            is_overlapping = False
            if temp_enemy_rect:
                for castle_rect in castle_rects:
                    if castle_rect and temp_enemy_rect.colliderect(castle_rect):
                        is_overlapping = True
                        break
            if not is_overlapping:
                for e in newly_spawned:
                    dist = math.hypot(temp_enemy.pos[0] - e.pos[0], temp_enemy.pos[2] - e.pos[2])
                    if dist < 3*SEPARATION_RADIUS:
                        is_overlapping = True
                        break
            
            if not is_overlapping:
                direction = random.choice([0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337])
                e = Enemy.Enemy("zom", "Run", direction, (x_3d, 1, z_3d), 100, 5)
                newly_spawned.append(e)
                break

    for e in newly_spawned:
        grid.insert(e, e.pos[0], e.pos[2])
        enemy_list.append(e)
        object_list[tuple(e.pos)] = e
    for s in soldier_list:
        grid.insert(s, s.pos[0], s.pos[2])
        object_list[tuple(s.pos)] = s

def get_screen_rect(obj):
    if not hasattr(obj, 'pos'): return None
    
    x, y, z = obj.pos
    pw = PROJECTION_WIDTH * zoom_scale
    ph = PROJECTION_HEIGHT * zoom_scale
   
    screen_x = MAP_CENTER_X + MAP_OFFSET_X + (x - z) * pw / 2
    screen_y = MAP_CENTER_Y + MAP_OFFSET_Y + (x + z) * ph / 2 - y * ph

    if isinstance(obj, Tower.Tower):
        tw = TILE_CST_W * zoom_scale
        th = TILE_CST_H * zoom_scale
        top_left_x = screen_x - tw / 2
        top_left_y = screen_y - th
        return pygame.Rect(top_left_x, top_left_y, tw, th)
    
    
    elif isinstance(obj, Enemy.Enemy):
        tw = ENEMY_BASE_W * zoom_scale * 0.5
        th = ENEMY_BASE_H * zoom_scale * 0.5
        top_left_x = screen_x - tw / 2
        top_left_y = screen_y - (th - EN_FOOT_OFFSET)
        return pygame.Rect(top_left_x, top_left_y, tw, th)

    elif isinstance(obj, Soldier.Soldier):
        tw = ENEMY_BASE_W * zoom_scale * 0.5
        th = ENEMY_BASE_H * zoom_scale * 0.5
        top_left_x = screen_x - tw / 2
        top_left_y = screen_y - (th - EN_FOOT_OFFSET)
        return pygame.Rect(top_left_x, top_left_y, tw, th)
    
    return None

def UpdateZoom():
    for tile_id in TILE_RECTS:
        rect = TILE_RECTS[tile_id]
        if tile_id <= 15:
            tw, th = TILE_GRP_W * zoom_scale * GRASS_SCALE, TILE_GRP_H * zoom_scale * GRASS_SCALE
            tex = GTEXTURE.subsurface(rect).copy()
        else:
            tw, th = TILE_CST_W * zoom_scale, TILE_CST_H * zoom_scale
            if 16 <= tile_id < 20: tex = C1TEXTURE.subsurface(rect).copy()
            elif 20 <= tile_id < 24: tex = C2TEXTURE.subsurface(rect).copy()
            elif 24 <= tile_id < 28: tex = C3TEXTURE.subsurface(rect).copy()
            elif 28 <= tile_id < 32: tex = C4TEXTURE.subsurface(rect).copy()
            elif 32 <= tile_id < 36: tex = C5TEXTURE.subsurface(rect).copy()
            else: tex = C6TEXTURE.subsurface(rect).copy()
        SCALED_TEX[tile_id] = pygame.transform.scale(tex, (tw, th))

def LoadGroundTex():
    for i in range(16):
        TILE_RECTS[i] = pygame.Rect((i % 4) * TILE_GRP_W, (i // 4) * TILE_GRP_H, TILE_GRP_W, TILE_GRP_H)

def LoadCastleTex():
    cnt = 16
    for _ in range(6):
        for j in range(4):
            TILE_RECTS[cnt] = pygame.Rect(0, j * TILE_CST_H, TILE_CST_W, TILE_CST_H)
            cnt += 1

def PickBlock():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for (x_3d, y, z_3d) in reversed(drawn_list):
        obj = object_list.get((x_3d, y, z_3d))
        pw, ph = PROJECTION_WIDTH * zoom_scale, PROJECTION_HEIGHT * zoom_scale

        if isinstance(obj, Tower.Tower):
            tw, th = TILE_CST_W * zoom_scale, TILE_CST_H * zoom_scale
           
            screen_x = MAP_CENTER_X + MAP_OFFSET_X + (x_3d - z_3d) * pw / 2
            screen_y = MAP_CENTER_Y + MAP_OFFSET_Y + (x_3d + z_3d) * ph / 2 - y * ph
            
            draw_rect = pygame.Rect(screen_x - tw / 2, screen_y - th, tw, th)
            
            if draw_rect.collidepoint(mouse_x, mouse_y): return (x_3d, y, z_3d)

        elif isinstance(obj, int): 
            tw, th = TILE_GRP_W * zoom_scale * GRASS_SCALE, TILE_GRP_H * zoom_scale * GRASS_SCALE
            
            screen_x = MAP_CENTER_X + MAP_OFFSET_X + (x_3d - z_3d) * pw / 2
            screen_y = MAP_CENTER_Y + MAP_OFFSET_Y + (x_3d + z_3d) * ph / 2 - y * ph
            
            draw_rect = pygame.Rect(screen_x - tw / 2, screen_y, tw, th)
            
            if draw_rect.collidepoint(mouse_x, mouse_y): return (x_3d, y, z_3d)
            
    return None

def FullRestart():
    global object_list, enemy_list, castle_list, MAP_OFFSET_X, MAP_OFFSET_Y, zoom_scale, tower_alive_cnt, main_cnt, round_number, towers_to_place, game_state
    
    MAP_OFFSET_X = 0
    MAP_OFFSET_Y = 0
    zoom_scale = 1
    tower_alive_cnt = 0
    main_cnt = True
    
    round_number = 1
    towers_to_place = 2
    game_state = "playing"

    object_list.clear()
    enemy_list.clear()
    castle_list.clear()

    Init()
    UpdateZoom()
    pygame.time.delay(100)
    print("=== GAME RESTARTED ===")

def get_castle_atlas(tex_id):
    if 16 <= tex_id < 20: return C1TEXTURE
    if 20 <= tex_id < 24: return C2TEXTURE
    if 24 <= tex_id < 28: return C3TEXTURE
    if 28 <= tex_id < 32: return C4TEXTURE
    if 32 <= tex_id < 36: return C5TEXTURE
    return C6TEXTURE

def TowerCollision(tw1, tw2):
	pos1, pos2 = list(tw1.pos), list(tw2.pos)
	distance = math.hypot(pos1[0] - pos2[0], pos1[2] - pos2[2])
	return distance < 2*CASTLE_RADIUS

def EnemyCollision(tw, en):
	pos1, pos2 = list(tw.pos), en.pos
	distance = math.hypot(pos1[0] - pos2[0], pos1[2] - pos2[2])
	return distance < CASTLE_RADIUS + 4*SEPARATION_RADIUS

def SoldierCollision(tw, so):
    pos1, pos2 = list(tw.pos), so.pos
    distance = math.hypot(pos1[0] - pos2[0], pos1[2] - pos2[2])
    return distance < CASTLE_RADIUS + 4*SEPARATION_RADIUS

def SpawnEnemies(amount):
    castle_rects = [get_screen_rect(t) for t in castle_list if not t.destroyed]
    newly_spawned = []
    for _ in range(amount):
        while True:
            x_3d = random.randint(-GRID_SIZE//2 * GRASS_SCALE, GRID_SIZE//2 * GRASS_SCALE)
            z_3d = random.randint(-GRID_SIZE//2 * GRASS_SCALE, GRID_SIZE//2 * GRASS_SCALE)
            
            temp_enemy = Enemy.Enemy("temp", "Idle", 0, (x_3d, 1, z_3d), 1, 1)
            temp_enemy_rect = get_screen_rect(temp_enemy)
            
            is_overlapping = False
            if temp_enemy_rect:
                for castle_rect in castle_rects:
                    if castle_rect and temp_enemy_rect.colliderect(castle_rect):
                        is_overlapping = True
                        break
            
            if not is_overlapping:
                for e in newly_spawned:
                    dist = math.hypot(abs(temp_enemy.pos[0] - e.pos[0]), abs(temp_enemy.pos[2] - e.pos[2]))
                    if dist < 0.5:
                        is_overlapping = True
                        break
            
            if not is_overlapping:
                direction = random.choice([0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337])
                e = Enemy.Enemy("zom", "Run", direction, (x_3d, 1, z_3d), 100, 5)
                newly_spawned.append(e)
                break
    
    for e in newly_spawned:
        grid.insert(e, e.pos[0], e.pos[2])
        enemy_list.append(e)
        object_list[tuple(e.pos)] = e

def StartNextRound():
    global round_number, towers_to_place, enemy_list, object_list, grid, game_state, castle_list, soldier_to_spawn, soldier_list

    round_number += 1
    towers_to_place = round_number * 2
    soldier_to_spawn = round_number * 2
    saved_towers = [t for t in castle_list if isinstance(t, Tower.Tower)]
    enemy_list.clear()
    castle_list.clear()

    Init()         
    UpdateZoom()
    pygame.time.delay(100)
    num_new_enemies = NUM_ENEMIES + (round_number - 1) * 5
    SpawnEnemies(num_new_enemies)

    for pos, obj in list(object_list.items()):
        if isinstance(obj, Tower.Tower):
            del object_list[pos]

    castle_list[:] = saved_towers

    for tower in castle_list:
        object_list[tower.pos] = tower
        if tower.is_main:
            tower.hp = 2000
            tower.shield = True
            tower.shield_hp = 1000


    game_state = "playing"

def main():
    global MAP_OFFSET_X, MAP_OFFSET_Y, zoom_scale, object_list, enemy_list, soldier_list, tower_alive_cnt, main_cnt, grid, round_number, towers_to_place, game_state, soldier_to_spawn
    
    Init()
    LoadGroundTex()
    LoadCastleTex()
    UpdateZoom()
    
    pausing = False
    running = True
    build_mode = False
    spawn_mode = False
    castle_chosen = 16
    castle_dir = 0
    placment_collided = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if build_mode:
                    if event.button == 4: castle_dir = (castle_dir + 1) % 4
                    elif event.button == 5: castle_dir = (castle_dir - 1 + 4) % 4
                    elif event.button == 1:
                        if PickBlock() is not None and not placment_collided and towers_to_place > 0:
                            x, y, z = PickBlock()
                            new_tower = Tower.Tower(x, y + 1, z, castle_chosen + castle_dir, shield=False, shield_hp=0, hp=500, is_main=False)
                            object_list[new_tower.pos] = new_tower
                            castle_list.append(new_tower)
                            towers_to_place -= 1
                if spawn_mode:
                    if event.button == 1:
                        if PickBlock() is not None and not placment_collided and soldier_to_spawn > 0:
                            x, y, z = PickBlock()
                            new_soldier = Soldier.Soldier("sol", "Idle", 0, (x, y + 1, z), 100, 100)
                            object_list[tuple(new_soldier.pos)] = new_soldier
                            soldier_list.append(new_soldier)
                            soldier_to_spawn -= 1
                else:
                    if event.button == 4: zoom_scale = min(6.0, zoom_scale + 0.5); UpdateZoom()
                    elif event.button == 5: zoom_scale = max(0.5, zoom_scale - 0.5); UpdateZoom()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_b] and not spawn_mode: 
            build_mode = not build_mode
            pygame.time.delay(200)
        elif keys[pygame.K_f] and not build_mode: 
            spawn_mode = not spawn_mode
            pygame.time.delay(200)

        screen.fill((40, 40, 60))
        
        tower_collided = False
        blockpos = PickBlock()
        blockposCondition = blockpos is not None and isinstance(object_list.get(blockpos), int)
        
        if not pausing:
            new_object_list = {}
            main_cnt = False
            towers_alive = [obj for obj in object_list.values() if isinstance(obj, Tower.Tower) and not obj.destroyed]
            tower_alive_cnt = len(towers_alive)
            soldier_alive = [obj for obj in object_list.values() if isinstance(obj, Soldier.Soldier) and obj.alive]
            soldier_alive_cnt = len(soldier_alive)
            enemy_alive = [obj for obj in object_list.values() if isinstance(obj, Enemy.Enemy) and obj.alive]
            enemy_alive_cnt = len(enemy_alive)
            tempGrid = SpatialGrid()
            
            if blockposCondition: tempCastle = Tower.Tower(*blockpos, castle_chosen + castle_dir, shield=False, shield_hp=0, hp=500, is_main=False)
            
            for old_pos, obj in object_list.items():
                if isinstance(obj, Enemy.Enemy):
                    if obj.alive:
                        if blockposCondition and EnemyCollision(tempCastle, obj): tower_collided = True
                        tempGrid.insert(obj, obj.pos[0],obj.pos[2])
                        AttackedTower = ZombieAI(obj, towers_alive, soldier_alive)
                        new_object_list[tuple(obj.pos)] = obj
                elif isinstance(obj, Tower.Tower):
                    if not obj.destroyed:
                        if blockposCondition and TowerCollision(tempCastle, obj): tower_collided = True
                        new_object_list[old_pos] = obj
                        AttackedEnemy = TowerAI(obj, enemy_alive)
                        DrawLine(AttackedEnemy, obj, LIGHT_BLUE)
                        if obj.is_main: main_cnt = True
                elif isinstance(obj, Soldier.Soldier):
                    if obj.alive:
                        if blockposCondition and SoldierCollision(tempCastle, obj): tower_collided = True
                        tempGrid.insert(obj, obj.pos[0],obj.pos[2])
                        AttackedZombie = SoldierAI(obj, enemy_alive, towers_alive)
                        DrawLine(AttackedZombie, obj, YELLOW)
                        new_object_list[tuple(obj.pos)] = obj
                else:
                    new_object_list[old_pos] = obj

            object_list = new_object_list
            enemy_list = [obj for obj in object_list.values() if isinstance(obj, Enemy.Enemy)]
            soldier_list = [obj for obj in object_list.values() if isinstance(obj, Soldier.Soldier)]
            grid = tempGrid
            placment_collided = tower_collided

        if game_state in ["game_over", "round_won"]:
            for soldier in soldier_list:
                if soldier.state != "Idle": soldier.SetState("Idle")

        
        DrawObjects()
        Draw_Range()
        
        if build_mode and blockposCondition:
            color = (0, 255, 0, 180)
            if placment_collided or towers_to_place <= 0:
                color = (255, 0, 0, 200)
            DrawCastleOutline(blockpos, castle_chosen + castle_dir, color)

        if spawn_mode:
            spawn_collided = False
            blockpos = PickBlock()
            blockposCondition = blockpos is not None and isinstance(object_list.get(blockpos), int)
            if blockposCondition:
                tempSoldier = Soldier.Soldier("temp", "Idle", 0, (blockpos[0], blockpos[1]+1, blockpos[2]), 100, 100)
                for obj in object_list.values():
                    if isinstance(obj, Tower.Tower) and SoldierCollision(obj, tempSoldier):
                        spawn_collided = True
                        break
                    if isinstance(obj, Soldier.Soldier) and SoldierCollision(obj, tempSoldier):
                        spawn_collided = True
                        break

        enemy_alive_now = [obj for obj in object_list.values() if isinstance(obj, Enemy.Enemy) and obj.alive]
        enemy_alive_cnt = len(enemy_alive_now)

        if not main_cnt and game_state == "playing":
            game_state = "game_over"
            pausing = True
        
        if not enemy_alive_cnt and game_state == "playing" and len(enemy_list) > 0:
            game_state = "round_won"
            pausing = True

        if pausing:
            if game_state == "game_over":
                Draw_Result("GAME OVER",RED, round_number)
            elif game_state == "round_won":
                Draw_Result(f"ROUND {round_number} COMPLETE",LIGHT_BLUE)

        effective_speed = MAP_MOVE_SPEED / zoom_scale
        if keys[pygame.K_a]: MAP_OFFSET_X += effective_speed
        if keys[pygame.K_d]: MAP_OFFSET_X -= effective_speed
        if keys[pygame.K_w]: MAP_OFFSET_Y += effective_speed
        if keys[pygame.K_s]: MAP_OFFSET_Y -= effective_speed
        
        if build_mode:
            if keys[pygame.K_1]: castle_chosen = 16
            if keys[pygame.K_2]: castle_chosen = 20
            if keys[pygame.K_3]: castle_chosen = 24
            if keys[pygame.K_4]: castle_chosen = 28
            if keys[pygame.K_5]: castle_chosen = 32
            if keys[pygame.K_6]: castle_chosen = 36

        if keys[pygame.K_SPACE] and pausing:
            if game_state == "game_over":
                FullRestart()
            elif game_state == "round_won":
                StartNextRound()
            pausing = False

        Draw_UI(enemy_alive_cnt, soldier_alive_cnt, tower_alive_cnt, build_mode, spawn_mode)
        screen.blit(sub_layer, (0, 0))
        sub_layer.fill((0, 0, 0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()