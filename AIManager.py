def TowerAI(tower, all_enemy):
    for e in all_enemy:
        dist = math.hypot(tower.pos[0] - e.pos[0], tower.pos[2] - e.pos[2])
        if dist < tower.attack_range:
            current_time = pygame.time.get_ticks()
            if current_time - tower.last_attack_time > tower.attack_cooldown:
                tower.last_attack_time = current_time
                shoot_sound.play()
                if tower.is_main: e.TakeDamage(tower.damage + 20)   
                else : e.TakeDamage(tower.damage)
                return e

def ZombieAI(enemy, all_towers, all_soldier):
    ROTATION_EPSILON = 5.0
    if not enemy.alive or enemy.state == "Death":
        return

    # --- PHẦN ƯU TIÊN MỤC TIÊU ---
    target_soldier = None
    min_soldier_distance = float('inf')
    for s in all_soldier:
        if not s.alive:
            continue
        dist = math.hypot(enemy.pos[0] - s.pos[0], enemy.pos[2] - s.pos[2])
        if dist < min_soldier_distance:
            min_soldier_distance = dist
            target_soldier = s

    target_tower = None
    min_tower_distance = float('inf')
    for t in all_towers:
        dist = math.hypot(enemy.pos[0] - t.pos[0], enemy.pos[2] - t.pos[2])
        if dist < min_tower_distance:
            min_tower_distance = dist
            target_tower = t

    # Nếu có soldier gần hơn tower -> đổi mục tiêu sang soldier
    if target_soldier and min_soldier_distance < min_tower_distance:
        initial_target = target_soldier
        min_distance = min_soldier_distance
        target_type = "soldier"
    else:
        initial_target = target_tower
        min_distance = min_tower_distance
        target_type = "tower"

    if initial_target is None:
        if enemy.state != "Idle":
            enemy.SetState("Idle")
        return

    # --- PHẦN DI CHUYỂN, VA CHẠM, XOAY, TẤN CÔNG ---
    next_pos_3d = list(enemy.pos)
    if min_distance > 0:
        temp_dx = initial_target.pos[0] - enemy.pos[0]
        temp_dz = initial_target.pos[2] - enemy.pos[2]
        next_pos_3d[0] += (temp_dx / min_distance) * enemy.speed
        next_pos_3d[2] += (temp_dz / min_distance) * enemy.speed
        if tuple(next_pos_3d) in object_list:
            if enemy.state != "Idle":
                enemy.SetState("Idle")
            return

        nearby_enemies = grid.nearby(enemy.pos[0], enemy.pos[2], SEPARATION_RADIUS * 2.5)
        repel_strength = 0.25
        for other in nearby_enemies:
            if other is enemy or not other.alive:
                continue
            dx = next_pos_3d[0] - other.pos[0]
            dz = next_pos_3d[2] - other.pos[2]
            dist = math.hypot(dx, dz)
            if dist < SEPARATION_RADIUS and dist > 0:
                push = (SEPARATION_RADIUS - dist) / SEPARATION_RADIUS * repel_strength
                next_pos_3d[0] += (dx / dist) * push
                next_pos_3d[2] += (dz / dist) * push

    colliding_tower = None
    next_enemy_state = Enemy.Enemy("ghost", "Idle", 0, tuple(next_pos_3d), 1, 1)
    next_enemy_rect = get_screen_rect(next_enemy_state)
    if next_enemy_rect:
        for tower in all_towers:
            tower_rect = get_screen_rect(tower)
            if (tower_rect and next_enemy_rect.colliderect(tower_rect)) or EnemyCollision(tower, enemy):
                colliding_tower = tower
                break

    if colliding_tower:
        closest_tower = colliding_tower
        min_distance = math.hypot(enemy.pos[0] - closest_tower.pos[0], enemy.pos[2] - closest_tower.pos[2])
    else:
        closest_tower = initial_target

    dx = closest_tower.pos[0] - enemy.pos[0]
    dz = closest_tower.pos[2] - enemy.pos[2]
    target_angle = (-math.degrees(math.atan2(-dz, dx)) + 45) % 360

    angle_diff = target_angle - enemy.direction
    if angle_diff > 180: angle_diff -= 360
    elif angle_diff < -180: angle_diff += 360

    is_rotation_complete = abs(angle_diff) <= ROTATION_EPSILON

    if not is_rotation_complete:
        turn_direction = math.copysign(1, angle_diff)
        enemy.Rotate(enemy.rotation_speed * turn_direction)
        if enemy.state != "Run":
            enemy.SetState("Run")
        enemy.UpdateRotation()

    if is_rotation_complete:
        if min_distance <= enemy.attack_range:
            if enemy.state != "Attack":
                enemy.SetState("Attack")
            current_time = pygame.time.get_ticks()
            if current_time - enemy.last_attack_time > enemy.attack_cooldown:
                if target_type == "soldier":
                    initial_target.TakeDamage(enemy.damage)
                else:
                    closest_tower.damage_tower(enemy.damage)
                enemy.last_attack_time = current_time
                return initial_target
        else:
            if colliding_tower is None:
                if tower_alive_cnt == 0:
                    if enemy.state != "Idle":
                        enemy.SetState("Idle")
                else:
                    enemy.pos = next_pos_3d
                    if enemy.state != "Run":
                        enemy.SetState("Run")
            else:
                if enemy.state != "Attack":
                    enemy.SetState("Attack")
                current_time = pygame.time.get_ticks()
                if current_time - enemy.last_attack_time > enemy.attack_cooldown:
                    colliding_tower.damage_tower(enemy.damage)
                    enemy.last_attack_time = current_time
                    return colliding_tower


def SoldierAI(soldier, all_enemy, all_towers):
    ROTATION_EPSILON = 5.0 
    if not soldier.alive:
        return
    if game_state == "game_over" or game_state == "round_won":
        if soldier.state != "Idle": soldier.SetState("Idle")
        return

    target_enemy = None
    min_distance = float('inf')
    for enemy in all_enemy:
        if not enemy.alive:
            continue
        dist = math.hypot(enemy.pos[0] - soldier.pos[0], enemy.pos[2] - soldier.pos[2])
        if dist < min_distance:
            min_distance = dist
            target_enemy = enemy

    if target_enemy is None:
        if soldier.state != "Idle":
            soldier.SetState("Idle")
        return

    next_pos_3d = soldier.pos.copy()
    if min_distance > 0:
        temp_dx = target_enemy.pos[0] - soldier.pos[0]
        temp_dz = target_enemy.pos[2] - soldier.pos[2]
        next_pos_3d[0] += (temp_dx / min_distance) * soldier.speed
        next_pos_3d[2] += (temp_dz / min_distance) * soldier.speed

        if tuple(next_pos_3d) in object_list:
            if soldier.state != "Idle":
                soldier.SetState("Idle")
            return

        nearby_soldiers = grid.nearby(soldier.pos[0], soldier.pos[2], SEPARATION_RADIUS * 2.5)
        repel_strength = 0.25
        for other in nearby_soldiers:
            if other is soldier or not other.alive:
                continue
            dx = next_pos_3d[0] - other.pos[0]
            dz = next_pos_3d[2] - other.pos[2]
            dist = math.hypot(dx, dz)
            if dist < SEPARATION_RADIUS and dist > 0:
                push = (SEPARATION_RADIUS - dist) / SEPARATION_RADIUS * repel_strength
                next_pos_3d[0] += (dx / dist) * push
                next_pos_3d[2] += (dz / dist) * push

    colliding_tower = None
    next_soldier_state = Soldier.Soldier("ghost", "Idle", 0, tuple(next_pos_3d), 1, 1)
    next_soldier_rect = get_screen_rect(next_soldier_state)
    if next_soldier_rect:
        for tower in all_towers:
            tower_rect = get_screen_rect(tower)
            if (tower_rect and next_soldier_rect.colliderect(tower_rect)) or SoldierCollision(tower, soldier):
                colliding_tower = tower
                break

    dx = target_enemy.pos[0] - soldier.pos[0]
    dz = target_enemy.pos[2] - soldier.pos[2]
    target_angle = (-math.degrees(math.atan2(-dz, dx)) + 45) % 360

    angle_diff = target_angle - soldier.direction
    if angle_diff > 180: angle_diff -= 360
    elif angle_diff < -180: angle_diff += 360

    is_rotation_complete = abs(angle_diff) <= ROTATION_EPSILON

    if not is_rotation_complete:
        turn_direction = math.copysign(1, angle_diff)
        soldier.Rotate(soldier.rotation_speed * turn_direction)
        if soldier.state != "Walk":
            soldier.SetState("Walk")
        soldier.UpdateRotation()

    if is_rotation_complete:
        if min_distance <= soldier.attack_range:
            if soldier.state != "Shooting":
                soldier.SetState("Shooting")
            current_time = pygame.time.get_ticks()
            if current_time - soldier.last_attack_time > soldier.attack_cooldown:
                shoot_sound.play()
                target_enemy.TakeDamage(soldier.damage)
                soldier.last_attack_time = current_time
                return target_enemy
        else:
            if colliding_tower is None:
                soldier.pos = next_pos_3d
                if soldier.state != "Walk":
                    soldier.SetState("Walk")
            else:
                if soldier.state != "Idle":
                    soldier.SetState("Idle")
