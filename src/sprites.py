# ASTEROIDE SINGLEPLAYER v1.0
# This file defines the interactive game entities and their local behaviors.

import math
from random import random, uniform

import pygame as pg

import config as C
from utils import Vec, angle_to_vec, draw_circle, draw_poly, wrap_pos


class Bullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.ttl = C.BULLET_TTL
        self.r = C.BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r)


class PowerUp(pg.sprite.Sprite):
    def __init__(self, pos: Vec, p_type: str = "shield"):
        super().__init__()
        self.pos = Vec(pos)
        self.p_type = p_type
        self.ttl = C.POWERUP_TTL
        self.r = C.POWERUP_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        if self.p_type == "shield":
            p1 = self.pos + Vec(0, -self.r)
            p2 = self.pos + Vec(self.r, 0)
            p3 = self.pos + Vec(0, self.r)
            p4 = self.pos + Vec(-self.r, 0)
            draw_poly(surf, [p1, p2, p3, p4])
        elif self.p_type == "life":
            draw_circle(surf, self.pos, self.r)
            p_top = self.pos + Vec(0, -self.r + 2)
            p_bot = self.pos + Vec(0, self.r - 2)
            p_left = self.pos + Vec(-self.r + 2, 0)
            p_right = self.pos + Vec(self.r - 2, 0)
            pg.draw.line(surf, C.WHITE, p_top, p_bot, width=2)
            pg.draw.line(surf, C.WHITE, p_left, p_right, width=2)


class UfoBullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.ttl = C.UFO_BULLET_TTL
        self.r = C.BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r)


class BossBullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.ttl = C.BOSS_BULLET_TTL
        self.r = C.BOSS_BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r)


class Asteroid(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec, size: str):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.size = size
        self.r = C.AST_SIZES[size]["r"]
        self.poly = self._make_poly()
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def _make_poly(self):
        steps = 12 if self.size == "L" else 10 if self.size == "M" else 8
        pts = []
        for i in range(steps):
            ang = i * (360 / steps)
            jitter = uniform(0.75, 1.2)
            r = self.r * jitter
            v = Vec(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
            pts.append(v * r)
        return pts

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        pts = [self.pos + p for p in self.poly]
        pg.draw.polygon(surf, C.WHITE, pts, width=1)


class Ship(pg.sprite.Sprite):
    def __init__(self, pos: Vec):
        super().__init__()
        self.shield_time = 0.0
        self.alive = True
        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.angle = -90.0
        self.cool = 0.0
        self.invuln = 0.0
        self.r = C.SHIP_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def control(self, keys: pg.key.ScancodeWrapper, dt: float):
        if keys[pg.K_LEFT]:
            self.angle -= C.SHIP_TURN_SPEED * dt
        if keys[pg.K_RIGHT]:
            self.angle += C.SHIP_TURN_SPEED * dt
        if keys[pg.K_UP]:
            self.vel += angle_to_vec(self.angle) * C.SHIP_THRUST * dt
        self.vel *= C.SHIP_FRICTION

    def fire(self) -> Bullet | None:
        if self.cool > 0:
            return None
        dirv = angle_to_vec(self.angle)
        pos = self.pos + dirv * (self.r + 6)
        vel = self.vel + dirv * C.SHIP_BULLET_SPEED
        self.cool = C.SHIP_FIRE_RATE
        return Bullet(pos, vel)

    def hyperspace(self):
        self.pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        self.vel.xy = (0, 0)
        self.invuln = 1.0

    def update(self, dt: float):
        if self.cool > 0:
            self.cool -= dt
        if self.invuln > 0:
            self.invuln -= dt
        if self.shield_time > 0:
            self.shield_time -= dt
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        dirv = angle_to_vec(self.angle)
        left = angle_to_vec(self.angle + 140)
        right = angle_to_vec(self.angle - 140)
        p1 = self.pos + dirv * self.r
        p2 = self.pos + left * self.r * 0.9
        p3 = self.pos + right * self.r * 0.9
        draw_poly(surf, [p1, p2, p3])
        if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
            draw_circle(surf, self.pos, self.r + 6)
        if self.shield_time > 0:
            draw_circle(surf, self.pos, self.r + 12)


class UFO(pg.sprite.Sprite):
    def __init__(self, pos: Vec, small: bool):
        super().__init__()
        self.pos = Vec(pos)
        self.small = small
        profile = C.UFO_SMALL if small else C.UFO_BIG
        self.r = profile["r"]
        self.aim = profile["aim"]
        self.speed = C.UFO_SPEED
        self.cool = C.UFO_FIRE_EVERY
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)
        self.dir = Vec(1, 0) if uniform(0, 1) < 0.5 else Vec(-1, 0)

    def update(self, dt: float):
        self.pos += self.dir * self.speed * dt
        self.cool -= dt
        if self.pos.x < -self.r * 2 or self.pos.x > C.WIDTH + self.r * 2:
            self.kill()
        self.rect.center = self.pos

    def fire_at(self, target_pos: Vec) -> UfoBullet | None:
        if self.cool > 0:
            return None
        aim_vec = Vec(target_pos) - self.pos
        if aim_vec.length_squared() == 0:
            aim_vec = self.dir.normalize()
        else:
            aim_vec = aim_vec.normalize()
        max_error = (1.0 - self.aim) * 60.0
        shot_dir = aim_vec.rotate(uniform(-max_error, max_error))
        self.cool = C.UFO_FIRE_EVERY
        spawn_pos = self.pos + shot_dir * (self.r + 6)
        vel = shot_dir * C.UFO_BULLET_SPEED
        return UfoBullet(spawn_pos, vel)

    def draw(self, surf: pg.Surface):
        w, h = self.r * 2, self.r
        rect = pg.Rect(0, 0, w, h)
        rect.center = self.pos
        pg.draw.ellipse(surf, C.WHITE, rect, width=1)
        cup = pg.Rect(0, 0, w * 0.5, h * 0.7)
        cup.center = (self.pos.x, self.pos.y - h * 0.3)
        pg.draw.ellipse(surf, C.WHITE, cup, width=1)


class Boss(pg.sprite.Sprite):
    def __init__(self, pos: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.r = C.BOSS_RADIUS
        self.max_hp = C.BOSS_HP
        self.hp = C.BOSS_HP
        self.dir = 1
        self.hit_flash = 0.0
        self.fire_cool = C.BOSS_FIRE_COOLDOWN_PHASE1
        self.summon_cool = C.BOSS_PHASE2_SUMMON_COOLDOWN
        self.spiral_angle = 0.0
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)
        self.poly = self._make_poly()

    def _make_poly(self):
        pts = []
        sides = 10 if random() < 0.5 else 12
        for i in range(sides):
            ang = math.radians(i * (360 / sides))
            jitter = uniform(0.82, 1.18)
            rr = self.r * jitter
            pts.append(Vec(math.cos(ang), math.sin(ang)) * rr)
        return pts

    def hp_ratio(self):
        return self.hp / self.max_hp

    def get_phase(self):
        ratio = self.hp_ratio()
        if ratio <= 0.25:
            return 3
        elif ratio <= 0.5:
            return 2
        return 1

    def get_speed(self):
        phase = self.get_phase()
        if phase == 1:
            return C.BOSS_SPEED_PHASE1
        if phase == 2:
            return C.BOSS_SPEED_PHASE2
        return C.BOSS_SPEED_PHASE3

    def get_fire_cooldown(self):
        phase = self.get_phase()
        if phase == 1:
            return C.BOSS_FIRE_COOLDOWN_PHASE1
        if phase == 2:
            return C.BOSS_FIRE_COOLDOWN_PHASE2
        return C.BOSS_FIRE_COOLDOWN_PHASE3

    def get_core_color(self):
        phase = self.get_phase()
        if self.hit_flash > 0:
            return (255, 180, 180)
        if phase == 1:
            return (240, 240, 240)
        if phase == 2:
            return (255, 220, 80)
        return (255, 80, 80)

    def update(self, dt: float):
        self.pos.x += self.dir * self.get_speed() * dt

        if self.pos.x < self.r:
            self.pos.x = self.r
            self.dir = 1
        elif self.pos.x > C.WIDTH - self.r:
            self.pos.x = C.WIDTH - self.r
            self.dir = -1

        if self.hit_flash > 0:
            self.hit_flash -= dt

        if self.fire_cool > 0:
            self.fire_cool -= dt

        if self.summon_cool > 0:
            self.summon_cool -= dt

        self.rect.center = self.pos

    def fire_pattern(self):
        if self.fire_cool > 0:
            return []

        phase = self.get_phase()
        bullets = []

        if phase == 1:
            for ang in range(0, 360, 45):
                dirv = Vec(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
                pos = self.pos + dirv * (self.r + 8)
                vel = dirv * C.BOSS_BULLET_SPEED
                bullets.append(BossBullet(pos, vel))

        elif phase == 2:
            for offset in (0, 45, 90, 135):
                ang = self.spiral_angle + offset
                dirv = Vec(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
                pos = self.pos + dirv * (self.r + 8)
                vel = dirv * C.BOSS_BULLET_SPEED
                bullets.append(BossBullet(pos, vel))
            self.spiral_angle = (self.spiral_angle + 25) % 360

        else:
            for ang in range(0, 360, 30):
                dirv = Vec(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
                pos = self.pos + dirv * (self.r + 8)
                vel = dirv * (C.BOSS_BULLET_SPEED * 1.15)
                bullets.append(BossBullet(pos, vel))

        self.fire_cool = self.get_fire_cooldown()
        return bullets

    def can_summon(self):
        return self.get_phase() == 2 and self.summon_cool <= 0

    def reset_summon(self):
        self.summon_cool = C.BOSS_PHASE2_SUMMON_COOLDOWN

    def draw(self, surf: pg.Surface):
        pts = [self.pos + p for p in self.poly]
        pg.draw.polygon(surf, C.WHITE, pts, width=2)

        core_color = self.get_core_color()
        pg.draw.circle(surf, core_color, self.pos, 18, width=1)
        pg.draw.circle(surf, core_color, self.pos, 8, width=1)
        