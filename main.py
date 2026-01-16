import random
import math

WIDTH = 960
HEIGHT = 540
TITLE = "Crazy Gravity Challenge"

GRAVITY_FORCE = 1800
MOVE_SPEED = 300
FLIP_COOLDOWN = 0.25

EDGE_BARRIER_MARGIN = 100

STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_GAME_OVER = "game_over"
state = STATE_MENU

music_on = True
sfx_on = True

GHOST_SPAWN_INTERVAL = 3.2
GHOST_LIFETIME = 7.5
GHOST_CHASE_SPEED = 140.0
GHOST_EXIT_SPEED = 260.0
GHOST_MAX_COUNT = 3
GHOST_HITBOX_SCALE = 0.62

ORB_SPAWN_INTERVAL = 0.95
ORB_MAX_COUNT = 6
ORB_RADIUS = 10
ORB_SCORE_VALUE = 1

ORB_PULSE_SPEED = 3.2
ORB_PULSE_AMPLITUDE = 0.35

PLAYER_IDLE_FPS = 10
PLAYER_WALK_FPS = 14
ENEMY_FPS = 12


def build_platforms():
    platforms = []
    platform_width = 320
    platform_height = 18
    center_x = (WIDTH - platform_width) // 2

    platforms.append(Rect(center_x, HEIGHT // 2 - 90, platform_width, platform_height))
    platforms.append(Rect(center_x, HEIGHT // 2 + 90, platform_width, platform_height))
    return platforms


platforms = build_platforms()


def player_frame_name(anim, i, facing, gravity_dir):
    """
    images/player/player_idle_(rd|ru|ld|lu)_0..10
    images/player/player_walk_(rd|ru|ld|lu)_0..11
    """
    lr = "r" if facing == 1 else "l"
    du = "d" if gravity_dir == 1 else "u"
    return f"player/player_{anim}_{lr}{du}_{i}"


def enemy_frame_name(i, facing):
    """
    images/enemy/enemy_right_0..9
    images/enemy/enemy_left_0..9
    """
    side = "right" if facing == 1 else "left"
    return f"enemy/enemy_{side}_{i}"


def set_sound_button_label():
    sound_button.text = "Sound: ON" if (music_on or sfx_on) else "Sound: OFF"


def play_music_if_enabled():
    if not music_on:
        return
    try:
        music.play("theme")
    except Exception as e:
        print("[MUSIC ERROR]", e)


def ensure_music():
    if not music_on:
        return
    try:
        music.play("theme")
    except Exception:
        pass


def stop_music():
    try:
        music.stop()
    except Exception:
        pass


def play_sfx(name):
    if not sfx_on:
        return

    try:
        snd = getattr(sounds, name)
        snd.play()
        return
    except Exception:
        pass

    try:
        sounds[name].play()
    except Exception as e:
        print(f"[SFX ERROR] '{name}' ->", e)


def toggle_sound():
    global music_on, sfx_on
    music_on = not music_on
    sfx_on = music_on

    if music_on:
        play_music_if_enabled()
    else:
        stop_music()

    set_sound_button_label()


def exit_game():
    raise SystemExit


class AnimatedSprite:
    def __init__(self, animations, default_anim):
        self.animations = animations
        self.anim = default_anim
        self.frame_index = 0
        self.acc = 0.0
        self._actors = {}

    def set_anim(self, name):
        if name == self.anim:
            return
        self.anim = name
        self.frame_index = 0
        self.acc = 0.0

    def update(self, dt):
        data = self.animations[self.anim]
        frames = data["frames"]
        fps = data["fps"]
        if fps <= 0 or len(frames) <= 1:
            return

        frame_time = 1.0 / fps
        self.acc += dt
        while self.acc >= frame_time:
            self.acc -= frame_time
            self.frame_index = (self.frame_index + 1) % len(frames)

    def current_frame(self):
        return self.animations[self.anim]["frames"][self.frame_index]

    def _get_actor(self, frame_name):
        a = self._actors.get(frame_name)
        if a is None:
            a = Actor(frame_name)
            self._actors[frame_name] = a
        return a

    def frame_size(self):
        a = self._get_actor(self.current_frame())
        return a.width, a.height

    def draw_centered(self, pos):
        a = self._get_actor(self.current_frame())
        a.pos = (int(pos[0]), int(pos[1]))
        a.draw()


class Button:
    def __init__(self, text, center, size=(260, 60)):
        self.text = text
        self.rect = Rect(0, 0, size[0], size[1])
        self.rect.center = center

    def draw(self):
        screen.draw.filled_rect(self.rect, (30, 30, 30))
        screen.draw.rect(self.rect, (220, 220, 220))
        screen.draw.text(self.text, center=self.rect.center, fontsize=36, color="white")

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)


start_button = Button("Start Game", (WIDTH // 2, 220))
sound_button = Button("Sound: ON", (WIDTH // 2, 300))
exit_button = Button("Exit", (WIDTH // 2, 380))


class Player:
    def __init__(self):
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity_dir = 1
        self.flip_timer = 0.0
        self.facing = 1

        self.sprite = AnimatedSprite(
            animations={
                "idle": {"frames": [], "fps": PLAYER_IDLE_FPS},
                "walk": {"frames": [], "fps": PLAYER_WALK_FPS},
            },
            default_anim="idle",
        )
        self.refresh_frames()

        w, h = self.sprite.frame_size()
        hitbox_scale = 0.85
        self.rect = Rect(0, 0, int(w * hitbox_scale), int(h * hitbox_scale))
        self.rect.topleft = (EDGE_BARRIER_MARGIN + 20, HEIGHT - self.rect.height)

    def refresh_frames(self):
        self.sprite.animations["idle"]["frames"] = [
            player_frame_name("idle", i, self.facing, self.gravity_dir) for i in range(11)
        ]
        self.sprite.animations["walk"]["frames"] = [
            player_frame_name("walk", i, self.facing, self.gravity_dir) for i in range(12)
        ]

    def reset(self):
        self.rect.x = EDGE_BARRIER_MARGIN + 20
        self.rect.bottom = HEIGHT
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity_dir = 1
        self.flip_timer = 0.0
        self.facing = 1
        self.sprite.set_anim("idle")
        self.refresh_frames()

    def update(self, dt):
        self.handle_input()
        self.apply_gravity(dt)
        self.move_and_collide(dt)
        self.apply_world_bounds()
        self.update_timers(dt)
        self.update_animation(dt)

    def handle_input(self):
        old_facing = self.facing

        self.vel_x = 0.0
        if keyboard.left:
            self.vel_x = -MOVE_SPEED
        if keyboard.right:
            self.vel_x = MOVE_SPEED

        if keyboard.space and self.flip_timer <= 0:
            self.flip_gravity()

        if self.vel_x > 1:
            self.facing = 1
        elif self.vel_x < -1:
            self.facing = -1

        if self.facing != old_facing:
            self.refresh_frames()

    def flip_gravity(self):
        self.gravity_dir *= -1
        self.vel_y = 0.0
        self.flip_timer = FLIP_COOLDOWN
        self.refresh_frames()

    def apply_gravity(self, dt):
        self.vel_y += GRAVITY_FORCE * self.gravity_dir * dt

    def move_and_collide(self, dt):
        self.rect.x += self.vel_x * dt
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_x > 0:
                    self.rect.right = p.left
                elif self.vel_x < 0:
                    self.rect.left = p.right

        self.rect.y += self.vel_y * dt
        for p in platforms:
            if self.rect.colliderect(p):
                if self.gravity_dir == 1 and self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0.0
                elif self.gravity_dir == -1 and self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0.0

        if self.gravity_dir == 1:
            if self.rect.bottom >= HEIGHT:
                self.rect.bottom = HEIGHT
                self.vel_y = 0.0
        else:
            if self.rect.top <= 0:
                self.rect.top = 0
                self.vel_y = 0.0

    def apply_world_bounds(self):
        if self.rect.left < EDGE_BARRIER_MARGIN:
            self.rect.left = EDGE_BARRIER_MARGIN
        if self.rect.right > WIDTH - EDGE_BARRIER_MARGIN:
            self.rect.right = WIDTH - EDGE_BARRIER_MARGIN

    def update_timers(self, dt):
        if self.flip_timer > 0:
            self.flip_timer -= dt

    def update_animation(self, dt):
        if abs(self.vel_x) > 1:
            self.sprite.set_anim("walk")
        else:
            self.sprite.set_anim("idle")
        self.sprite.update(dt)

    def draw(self):
        self.sprite.draw_centered(self.rect.center)


class Ghost:
    def __init__(self, x, y, initial_facing):
        self.life = GHOST_LIFETIME
        self.mode = "chase"
        self.exit_dir = initial_facing
        self.facing = initial_facing

        self.sprite = AnimatedSprite(
            animations={"move": {"frames": [], "fps": ENEMY_FPS}},
            default_anim="move",
        )
        self.refresh_frames()

        w, h = self.sprite.frame_size()
        self.rect = Rect(0, 0, int(w * GHOST_HITBOX_SCALE), int(h * GHOST_HITBOX_SCALE))
        self.rect.center = (x, y)

    def refresh_frames(self):
        self.sprite.animations["move"]["frames"] = [enemy_frame_name(i, self.facing) for i in range(10)]

    def start_exit(self):
        self.mode = "exit"
        self.exit_dir = -1 if self.rect.centerx < WIDTH / 2 else 1

        old = self.facing
        self.facing = 1 if self.exit_dir > 0 else -1
        if self.facing != old:
            self.refresh_frames()

    def update(self, dt, target_rect):
        self.life -= dt
        if self.mode == "chase" and self.life <= 0:
            self.start_exit()

        if self.mode == "chase":
            dx = target_rect.centerx - self.rect.centerx
            dy = target_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0.001:
                vx = (dx / dist) * GHOST_CHASE_SPEED
                vy = (dy / dist) * GHOST_CHASE_SPEED
                self.rect.x += vx * dt
                self.rect.y += vy * dt

                old = self.facing
                if vx > 1:
                    self.facing = 1
                elif vx < -1:
                    self.facing = -1
                if self.facing != old:
                    self.refresh_frames()
        else:
            self.rect.x += self.exit_dir * GHOST_EXIT_SPEED * dt

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        self.sprite.update(dt)

    def is_gone(self):
        return self.rect.right < -140 or self.rect.left > WIDTH + 140

    def draw(self):
        self.sprite.draw_centered(self.rect.center)


class Orb:
    def __init__(self, x, y, radius=ORB_RADIUS):
        self.x = float(x)
        self.y = float(y)
        self.base_radius = float(radius)
        self.phase = random.uniform(0.0, math.tau)

        d = int(self.base_radius * 2)
        self.rect = Rect(0, 0, d, d)
        self.rect.center = (int(self.x), int(self.y))
        self.visual_radius = self.base_radius

    def update(self, t):
        pulse = 1.0 + ORB_PULSE_AMPLITUDE * math.sin(t * ORB_PULSE_SPEED + self.phase)
        self.visual_radius = self.base_radius * pulse

    def draw(self):
        glow_r = self.visual_radius * 1.8
        screen.draw.filled_circle((int(self.x), int(self.y)), glow_r, (80, 60, 10))
        screen.draw.filled_circle((int(self.x), int(self.y)), self.visual_radius, (255, 220, 90))
        screen.draw.circle((int(self.x), int(self.y)), self.visual_radius, (120, 90, 20))


player = Player()
ghosts = []
ghost_spawn_timer = 0.0

orbs = []
orb_spawn_timer = 0.0
score = 0
game_time = 0.0


def spawn_ghost():
    side = random.choice(["left", "right"])
    y = random.randint(60, HEIGHT - 60)
    if side == "left":
        x = -120
        facing = 1
    else:
        x = WIDTH + 120
        facing = -1

    ghosts.append(Ghost(x, y, facing))


def random_orb_position():
    tries = 25
    while tries > 0:
        tries -= 1
        x = random.randint(EDGE_BARRIER_MARGIN + 40, WIDTH - EDGE_BARRIER_MARGIN - 40)
        y = random.randint(40, HEIGHT - 40)

        test_orb = Orb(x, y, ORB_RADIUS)
        blocked = False

        for p in platforms:
            if test_orb.rect.colliderect(p):
                blocked = True
                break

        if not blocked and test_orb.rect.colliderect(player.rect):
            blocked = True

        if not blocked:
            return x, y

    return WIDTH // 2, HEIGHT // 2


def spawn_orb():
    x, y = random_orb_position()
    orbs.append(Orb(x, y, ORB_RADIUS))


def start_game():
    global state, ghosts, ghost_spawn_timer, orbs, orb_spawn_timer, score, game_time
    state = STATE_PLAY
    player.reset()

    ghosts = []
    ghost_spawn_timer = 0.0

    orbs = []
    orb_spawn_timer = 0.0

    score = 0
    game_time = 0.0

    spawn_orb()
    spawn_orb()


def update(dt):
    global state, ghost_spawn_timer, ghosts, orb_spawn_timer, orbs, score, game_time

    if state == STATE_PLAY:
        game_time += dt

        player.update(dt)

        ghost_spawn_timer -= dt
        if ghost_spawn_timer <= 0 and len(ghosts) < GHOST_MAX_COUNT:
            spawn_ghost()
            ghost_spawn_timer = GHOST_SPAWN_INTERVAL

        for g in ghosts:
            g.update(dt, player.rect)
        ghosts = [g for g in ghosts if not g.is_gone()]

        orb_spawn_timer -= dt
        if orb_spawn_timer <= 0 and len(orbs) < ORB_MAX_COUNT:
            spawn_orb()
            orb_spawn_timer = ORB_SPAWN_INTERVAL

        for o in orbs:
            o.update(game_time)

        collected = [o for o in orbs if player.rect.colliderect(o.rect)]
        if collected:
            for o in collected:
                orbs.remove(o)
                score += ORB_SCORE_VALUE
            play_sfx("orb")

        for g in ghosts:
            if player.rect.colliderect(g.rect):
                play_sfx("hit")
                state = STATE_GAME_OVER
                break


def draw():
    screen.clear()
    if state == STATE_MENU:
        draw_menu()
    elif state == STATE_PLAY:
        draw_play()
    else:
        draw_game_over()


def draw_menu():
    screen.draw.text("Crazy Gravity Challenge", center=(WIDTH // 2, 120), fontsize=56, color="white")
    start_button.draw()
    sound_button.draw()
    exit_button.draw()


def draw_play():
    for p in platforms:
        screen.draw.filled_rect(p, (70, 70, 70))
        screen.draw.rect(p, (140, 140, 140))

    left_barrier = Rect(0, 0, EDGE_BARRIER_MARGIN, HEIGHT)
    right_barrier = Rect(WIDTH - EDGE_BARRIER_MARGIN, 0, EDGE_BARRIER_MARGIN, HEIGHT)
    screen.draw.filled_rect(left_barrier, (35, 15, 15))
    screen.draw.filled_rect(right_barrier, (35, 15, 15))

    for o in orbs:
        o.draw()

    for g in ghosts:
        g.draw()

    player.draw()

    screen.draw.text(f"Score: {score}", topright=(WIDTH - 10, 10), fontsize=36, color="white")
    screen.draw.text("Left/Right to move | SPACE to flip gravity",
                     bottomleft=(10, HEIGHT - 10), fontsize=26, color="white")


def draw_game_over():
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=64, color="red")
    screen.draw.text(f"Final Score: {score}", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=40, color="white")
    screen.draw.text("Click to return to menu", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=32, color="white")


def on_mouse_down(pos):
    global state
    if state == STATE_MENU:
        if start_button.collidepoint(pos):
            start_game()
        elif sound_button.collidepoint(pos):
            toggle_sound()
        elif exit_button.collidepoint(pos):
            exit_game()
    elif state == STATE_GAME_OVER:
        state = STATE_MENU


set_sound_button_label()
play_music_if_enabled()
