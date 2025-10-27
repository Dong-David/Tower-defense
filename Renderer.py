def DrawObjects():
    drawn_list.clear()
    render_list = sorted(object_list.items(), key=lambda item: (item[0][1], item[0][0] + item[0][2]))
    main_castle_pos = None

    for (x, y, z), obj in render_list:
        pw, ph = PROJECTION_WIDTH * zoom_scale, PROJECTION_HEIGHT * zoom_scale
        screen_x = MAP_CENTER_X + MAP_OFFSET_X + (x - z) * pw / 2
        screen_y = MAP_CENTER_Y + MAP_OFFSET_Y + (x + z) * ph / 2 - y * ph

        if isinstance(obj, int):
            tw, th = TILE_GRP_W * zoom_scale * GRASS_SCALE, TILE_GRP_H * zoom_scale * GRASS_SCALE
            render_pos = (screen_x - tw / 2, screen_y)
            if render_pos[0] + tw > 0 and render_pos[0] < WIDTH and render_pos[1] + th > 0 and render_pos[1] < HEIGHT:
                screen.blit(SCALED_TEX[obj], render_pos)
                drawn_list.append((x, y, z))
        
        elif isinstance(obj, Tower.Tower):
            tw, th = TILE_CST_W * zoom_scale, TILE_CST_H * zoom_scale
            render_pos = (screen_x - tw / 2, screen_y - th)
            if render_pos[0] + tw > 0 and render_pos[0] < WIDTH and render_pos[1] + th > 0 and render_pos[1] < HEIGHT:
                screen.blit(SCALED_TEX[obj.tex_id], render_pos)
                obj.draw_health_bar(screen, screen_x, render_pos[1] - 10, zoom_scale)
                if obj.is_main:
                    main_castle_pos = (screen_x, render_pos[1] + th / 2)
        
        elif isinstance(obj, Enemy.Enemy):
            tex = obj.RunAnimation()
            if tex is None or not obj.alive:
                continue  

            obj.UpdateCounter()
            scaled_tex = pygame.transform.scale(
                tex, 
                (int(tex.get_width() * zoom_scale * 0.5), int(tex.get_height() * zoom_scale * 0.5))
            )
            tw, th = scaled_tex.get_size()
            render_pos = (screen_x - tw / 2, screen_y - (th - EN_FOOT_OFFSET))
            if render_pos[0] + tw > 0 and render_pos[0] < WIDTH and render_pos[1] + th > 0 and render_pos[1] < HEIGHT:
                screen.blit(scaled_tex, render_pos)

        elif isinstance(obj, Soldier.Soldier):
            tex = obj.RunAnimation()
            if tex is None or not obj.alive:
                continue  

            obj.UpdateCounter()
            scaled_tex = pygame.transform.scale(
                tex, 
                (int(tex.get_width() * zoom_scale * 0.5), int(tex.get_height() * zoom_scale * 0.5))
            )
            tw, th = scaled_tex.get_size()
            render_pos = (screen_x - tw / 2, screen_y - (th - EN_FOOT_OFFSET))
            if render_pos[0] + tw > 0 and render_pos[0] < WIDTH and render_pos[1] + th > 0 and render_pos[1] < HEIGHT:
                obj.draw_health_bar(screen, screen_x, render_pos[1] - 10, zoom_scale)
                screen.blit(scaled_tex, render_pos)

    if main_castle_pos:
        main_tower = next((t for t in castle_list if t.is_main), None)
        if main_tower and main_tower.shield_hp > 0:
            shield_size = int(250 * zoom_scale)
            shield_tex = pygame.transform.scale(SHIELD_DOME_TEXTURE, (shield_size, shield_size))
            alpha = 200 + 55 * math.sin(pygame.time.get_ticks() * 0.005)
            shield_tex.set_alpha(alpha)
            shield_rect = shield_tex.get_rect(center=main_castle_pos)
            screen.blit(shield_tex, shield_rect, special_flags=pygame.BLEND_RGB_ADD)

def DrawLine(enemy, target_tower, color):
    if not enemy or not target_tower:
        return

    enemy_rect = get_screen_rect(enemy)
    if not enemy_rect:
        return
    enemy_center_pos = enemy_rect.center

    target_rect = get_screen_rect(target_tower)
    if not target_rect:
        return
    target_center_pos = target_rect.center
    pygame.draw.line(sub_layer, color, enemy_center_pos, target_center_pos, 2)

def DrawDebugInfo():
    for enemy in enemy_list:
        closest_tower = None
        min_dist = float('inf')
        for tower in castle_list:
            if not tower.destroyed:
                dist = math.hypot(enemy.pos[0] - tower.pos[0], enemy.pos[2] - tower.pos[2])
                if dist < min_dist:
                    min_dist = dist
                    closest_tower = tower
        if closest_tower:
            if not enemy or not closest_tower:
                return        

            enemy_rect = get_screen_rect(enemy)
            if not enemy_rect: return
            enemy_center_pos = enemy_rect.center        

            state_surface = DEBUG_FONT.render(f"State: {enemy.state}", True, (255, 255, 0)) 
            sub_layer.blit(state_surface, (enemy_center_pos[0] + 10, enemy_center_pos[1] - 30))
            
            dx = closest_tower.pos[0] - enemy.pos[0]
            dz = closest_tower.pos[2] - enemy.pos[2]
            target_angle = (-math.degrees(math.atan2(-dz, dx)) + 45) % 360        

            clockwise_offset = (target_angle - enemy.precise_angle + 360) % 360
            
            offset_text = f"Offset: {clockwise_offset:.1f}"
            offset_surface = DEBUG_FONT.render(offset_text, True, (200, 200, 255)) 
            sub_layer.blit(offset_surface, (enemy_center_pos[0] + 10, enemy_center_pos[1] - 15))
            
            len_line = 40
            drawing_angle_rad = math.radians(45 - enemy.precise_angle) 
            
            end_x = enemy_center_pos[0] + len_line * math.cos(drawing_angle_rad)
            end_y = enemy_center_pos[1] - len_line * math.sin(drawing_angle_rad) 
            
            pygame.draw.line(sub_layer, (0, 0, 255), enemy_center_pos, (end_x, end_y), 2)         

            target_rect = get_screen_rect(closest_tower)
            if not target_rect: return
            target_center_pos = target_rect.center
            pygame.draw.line(sub_layer, (255, 0, 0), enemy_center_pos, target_center_pos, 1) 

def Draw_Result(state, color, current_round=None):
    game_over_font = pygame.font.Font(None, 74)
    sub_font = pygame.font.Font(None, 48)
    
    text_surface = game_over_font.render(state, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30))
    
    dim_screen = pygame.Surface(screen.get_size())
    dim_screen.fill((40, 40, 60))
    dim_screen.set_alpha(128)
    screen.blit(dim_screen, (0, 0))
    screen.blit(text_surface, text_rect)
    
    if current_round is not None:
        round_text = f"Rounds Survived: {current_round}"
        round_surface = sub_font.render(round_text, True, (255, 255, 255))
        round_rect = round_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30))
        screen.blit(round_surface, round_rect)

def Draw_Range():
    for tower in castle_list:
        if tower.destroyed or not isinstance(tower, Tower.Tower):
            continue

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # ===== Tính vị trí thật của tower trên màn hình =====
        x, y, z = tower.pos
        pw, ph = PROJECTION_WIDTH * zoom_scale, PROJECTION_HEIGHT * zoom_scale
        screen_x = MAP_CENTER_X + MAP_OFFSET_X + (x - z) * pw / 2
        screen_y = MAP_CENTER_Y + MAP_OFFSET_Y + (x + z) * ph / 2 - y * ph

        tw, th = TILE_CST_W * zoom_scale, TILE_CST_H * zoom_scale
        draw_rect = pygame.Rect(screen_x - tw / 2, screen_y - th, tw, th)

        # Hover kiểm tra chuột
        if not draw_rect.collidepoint(mouse_x, mouse_y):
            continue

        # ===== CHUYỂN tầm bắn (attack_range) từ world → màn hình =====
        # Ta tính khoảng cách từ tower đến 1 điểm cách tower attack_range
        # ở các hướng, rồi lấy trung bình để xác định bán kính hiển thị thực
        dx, dz = tower.attack_range, 0
        sx1 = MAP_CENTER_X + MAP_OFFSET_X + (x + dx - z) * pw / 2
        sy1 = MAP_CENTER_Y + MAP_OFFSET_Y + (x + dx + z) * ph / 2 - y * ph

        dx, dz = 0, tower.attack_range
        sx2 = MAP_CENTER_X + MAP_OFFSET_X + (x - (z + dz)) * pw / 2
        sy2 = MAP_CENTER_Y + MAP_OFFSET_Y + (x + (z + dz)) * ph / 2 - y * ph

        # Tính khoảng cách pixel thật (theo hướng X và Z)
        radius_x = abs(screen_x - sx1)
        radius_y = abs(screen_y - sy2)

        # ===== Vẽ hình tròn tương ứng với tầm bắn =====
        range_surface = pygame.Surface((radius_x * 2 + 4, radius_y * 2 + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(
            range_surface,
            (150, 255, 150, 160),
            (2, 2, radius_x * 2, radius_y * 2),
            3
        )

        # Căn giữa vòng tròn vào tâm tháp
        sub_layer.blit(range_surface, (screen_x - radius_x - 2, screen_y - radius_y - 2))

def DrawCastleOutline(target_pos_3d, tex_id=18, color=(0, 255, 0, 180)):
    if target_pos_3d is None:
        return

    x, y, z = target_pos_3d
    tower_pos_3d = (x, y + 1, z)
    radius = 1.5
    pw = PROJECTION_WIDTH * zoom_scale
    ph = PROJECTION_HEIGHT * zoom_scale

    screen_x_center = MAP_CENTER_X + MAP_OFFSET_X + (tower_pos_3d[0] - tower_pos_3d[2]) * pw / 2
    screen_y_anchor = MAP_CENTER_Y + MAP_OFFSET_Y + (tower_pos_3d[0] + tower_pos_3d[2]) * ph / 2 - tower_pos_3d[1] * ph

    scaled_tw = TILE_CST_W * zoom_scale
    scaled_th = TILE_CST_H * zoom_scale

    render_pos_x = screen_x_center - scaled_tw / 2
    render_pos_y = screen_y_anchor - scaled_th

    atlas = get_castle_atlas(tex_id)
    tile_rect_in_atlas = TILE_RECTS.get(tex_id)

    if not tile_rect_in_atlas:
        return

    base_texture = atlas.subsurface(tile_rect_in_atlas).copy()
    scaled_texture = pygame.transform.scale(base_texture, (scaled_tw, scaled_th))

    mask = pygame.mask.from_surface(scaled_texture)
    outline_points = mask.outline()

    outline_surface = pygame.Surface((scaled_tw + 4, scaled_th + 4), pygame.SRCALPHA)

    for px, py in outline_points:
        outline_surface.set_at((px + 1, py + 1), color)
        outline_surface.set_at((px + 2, py + 1), color)
        outline_surface.set_at((px + 1, py + 2), color)

    sub_layer.blit(outline_surface, (render_pos_x - 1, render_pos_y - 1))

def Draw_UI(enemy_alive_cnt, soldier_alive_cnt, tower_alive_cnt, build_mode, spawn_mode):
    round_font = pygame.font.Font(None, 36)
    white = (255, 255, 255)

    # Xác định mode hiện tại
    if build_mode:
        mode_text = "Mode: BUILD"
    elif spawn_mode:
        mode_text = "Mode: SPAWN"
    else:
        mode_text = "Mode: VIEW"

    # Các dòng thông tin
    zombies_text   = f"Zombies Alive: {enemy_alive_cnt}"
    towers_text    = f"Towers Alive: {tower_alive_cnt}"
    soldiers_text  = f"Soldiers Alive: {soldier_alive_cnt}"
    mode_display   = f"{mode_text}"
    build_text     = f"Build Left: {towers_to_place}"
    spawn_text     = f"Spawn Left: {soldier_to_spawn}"

    # Render từng dòng
    texts = [
        zombies_text,
        towers_text,
        soldiers_text,
        mode_display,
        build_text,
        spawn_text
    ]
    
    y = 10
    line_height = 30
    for t in texts:
        surf = round_font.render(t, True, white)
        screen.blit(surf, (10, y))
        y += line_height

