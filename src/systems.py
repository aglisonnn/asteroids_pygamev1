# ASTEROIDE SINGLEPLAYER v1.0
# This file coordinates world state, spawning, collisions, scoring, and progression.

import math
from random import uniform

import pygame as pg

import config as C
from sprites import Asteroid, Boss, Laser, PowerUp, Ship, UFO
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:
    def __init__(self):
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.lasers = pg.sprite.Group()  # Raios laser do jogador
        self.all_sprites = pg.sprite.Group(self.ship)

        self.boss = None
        self.boss_bullets = pg.sprite.Group()
        self.boss_contact_cool = 0.0

        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0

        self.combo_timer = 0.0
        self.combo_mult = 1

        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY
        self.game_over = False

    def start_wave(self):
        self.wave += 1

        if self.wave % C.BOSS_WAVE_INTERVAL == 0:
            self.spawn_boss()
            return

        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str):
        a = Asteroid(pos, vel, size)
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def spawn_ufo(self):
        if self.ufos:
            return
        small = uniform(0, 1) < 0.5
        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        ufo.dir.xy = (1, 0) if x == 0 else (-1, 0)
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def spawn_boss(self):
        self.boss = Boss(Vec(C.WIDTH / 2, 140))
        self.all_sprites.add(self.boss)

    def boss_try_fire(self):
        if not self.boss or not self.boss.alive():
            return
        bullets = self.boss.fire_pattern()
        for bullet in bullets:
            self.boss_bullets.add(bullet)
            self.all_sprites.add(bullet)

    def boss_try_summon(self):
        if not self.boss or not self.boss.alive():
            return
        if not self.boss.can_summon():
            return

        for _ in range(2):
            offset = Vec(uniform(-70, 70), uniform(35, 90))
            pos = self.boss.pos + offset
            vel = rand_unit_vec() * uniform(C.AST_VEL_MIN * 1.1, C.AST_VEL_MAX * 1.3)
            self.spawn_asteroid(pos, vel, "S")

        self.boss.reset_summon()

    def ufo_try_fire(self):
        for ufo in self.ufos:
            bullet = ufo.fire_at(self.ship.pos)
            if bullet:
                self.ufo_bullets.add(bullet)
                self.all_sprites.add(bullet)

    def try_fire(self):
        """Dispara projéteis do jogador respeitando o limite MAX_BULLETS.

        Com tiro duplo ativo, tenta adicionar dois projéteis; com tiro
        simples, apenas um.  O limite é verificado antes de qualquer
        disparo para manter a contagem consistente.
        """
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        new_bullets = self.ship.fire()
        for b in new_bullets:
            self.bullets.add(b)
            self.all_sprites.add(b)

    def try_fire_laser(self):
        """Dispara um raio laser caso a nave tenha cargas disponíveis."""
        laser = self.ship.fire_laser()
        if laser:
            self.lasers.add(laser)
            self.all_sprites.add(laser)

    def hyperspace(self):
        self.ship.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def register_kill(self, base_score: int):
        if self.combo_timer > 0:
            self.combo_mult = min(self.combo_mult + 1, C.COMBO_MAX)
        else:
            self.combo_mult = 1

        self.combo_timer = C.COMBO_WINDOW
        self.score += base_score * self.combo_mult

    def update(self, dt: float, keys):
        self.ship.control(keys, dt)
        self.all_sprites.update(dt)

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_timer = 0
                self.combo_mult = 1

        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5

        if self.boss_contact_cool > 0:
            self.boss_contact_cool -= dt

        if self.ufos:
            self.ufo_try_fire()
        else:
            self.ufo_timer -= dt

        if not self.ufos and self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        if self.boss and self.boss.alive():
            self.boss_try_fire()
            self.boss_try_summon()

        self.handle_collisions()

        boss_alive = self.boss is not None and self.boss.alive()

        if not self.asteroids and not boss_alive and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids and not boss_alive:
            self.wave_cool -= dt

    def handle_collisions(self):
        power_hits = pg.sprite.spritecollide(
            self.ship,
            self.powerups,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < (a.r + b.r),
        )
        for p in power_hits:
            if p.p_type == "shield":
                self.ship.shield_time = C.SHIELD_DURATION
                self.score += 50
            elif p.p_type == "life":
                self.lives += 1
                self.score += 100
            elif p.p_type == "double_shot":
                self.ship.double_shot_time = C.DOUBLE_SHOT_DURATION
            elif p.p_type == "laser":
                self.ship.laser_charges += C.LASER_CHARGE_MAX

        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in hits.items():
            self.split_asteroid(ast)

        for laser in list(self.lasers):
            for ast in list(self.asteroids):
                if laser.hits(ast):
                    self.split_asteroid(ast)

        for laser in list(self.lasers):
            for ufo in list(self.ufos):
                if laser.hits(ufo):
                    score = C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"]
                    self.register_kill(score * C.LASER_SCORE_MULT)
                    ufo.kill()

        ufo_hits = pg.sprite.groupcollide(
            self.asteroids,
            self.ufo_bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in ufo_hits.items():
            self.split_asteroid(ast)

        boss_hits = pg.sprite.groupcollide(
            self.asteroids,
            self.boss_bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in boss_hits.items():
            self.split_asteroid(ast)

        if self.ship.invuln <= 0 and self.safe <= 0:
            for ast in self.asteroids:
                if (ast.pos - self.ship.pos).length() < (ast.r + self.ship.r):
                    self.take_damage()
                    break

            for ufo in self.ufos:
                if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                    self.take_damage()
                    break

            for bullet in self.ufo_bullets:
                if (bullet.pos - self.ship.pos).length() < (bullet.r + self.ship.r):
                    bullet.kill()
                    self.take_damage()
                    break

            for bullet in self.boss_bullets:
                if (bullet.pos - self.ship.pos).length() < (bullet.r + self.ship.r):
                    bullet.kill()
                    self.take_damage()
                    break

            if self.boss and self.boss.alive() and self.boss_contact_cool <= 0:
                if (self.boss.pos - self.ship.pos).length() < (self.boss.r + self.ship.r):
                    self.take_damage()
                    self.boss_contact_cool = C.BOSS_CONTACT_DAMAGE_COOLDOWN

        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    score = C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"]
                    self.register_kill(score)
                    ufo.kill()
                    b.kill()

        if self.boss and self.boss.alive():
            for b in list(self.bullets):
                if (self.boss.pos - b.pos).length() < (self.boss.r + b.r):
                    b.kill()
                    self.boss.hp -= 10
                    self.boss.hit_flash = 0.12

                    if self.boss.hp <= 0:
                        self.register_kill(C.BOSS_SCORE)
                        self.boss.kill()
                        self.boss = None
                        break

    def split_asteroid(self, ast: Asteroid):
        self.register_kill(C.AST_SIZES[ast.size]["score"])
        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)
        ast.kill()

        for s in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, s)

        if uniform(0, 1) < C.POWERUP_DROP_CHANCE:
            ptype = self._roll_powerup_type()
            p = PowerUp(pos, ptype)
            self.powerups.add(p)
            self.all_sprites.add(p)

    @staticmethod
    def _roll_powerup_type() -> str:
        """Sorteia um tipo de power-up baseado nos pesos de POWERUP_WEIGHTS."""
        roll = uniform(0, 1)
        cumulative = 0.0
        for ptype, weight in C.POWERUP_WEIGHTS.items():
            cumulative += weight
            if roll < cumulative:
                return ptype
        return list(C.POWERUP_WEIGHTS.keys())[-1]

    def take_damage(self):
        if self.ship.shield_time > 0:
            self.ship.shield_time = 0
            self.ship.invuln = 1.0
        else:
            self.ship_die()

    def ship_die(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            return

        self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
        self.ship.vel.xy = (0, 0)
        self.ship.angle = -90
        self.ship.invuln = C.SAFE_SPAWN_TIME
        self.ship.double_shot_time = 0.0  # Perde tiro duplo ao morrer
        self.ship.laser_charges = 0       # Perde cargas de laser ao morrer
        self.safe = C.SAFE_SPAWN_TIME

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), width=1)

        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))

        combo_txt = f"COMBO x{self.combo_mult}"
        combo_label = font.render(combo_txt, True, C.WHITE)
        surf.blit(combo_label, (10, 35))

        if self.boss and self.boss.alive():
            phase = self.boss.get_phase()

            bar_w = 320
            bar_h = 16
            x = (C.WIDTH - bar_w) // 2
            y = 40

            title = font.render(f"BOSS FASE {phase}", True, C.WHITE)
            surf.blit(title, (x - 110, y - 2))

            pg.draw.rect(surf, (80, 80, 80), (x, y, bar_w, bar_h), width=1)

            fill_w = int((self.boss.hp / self.boss.max_hp) * (bar_w - 4))
            pg.draw.rect(surf, C.WHITE, (x + 2, y + 2, fill_w, bar_h - 4))

        hud_x = C.WIDTH - 10
        hud_y = 10

        if self.ship.double_shot_time > 0:
            ds_label = font.render(
                f"2x {self.ship.double_shot_time:.1f}s", True, (255, 220, 80)
            )
            hud_x -= ds_label.get_width()
            surf.blit(ds_label, (hud_x, hud_y))
            hud_x -= 14

        if self.ship.laser_charges > 0:
            laser_label = font.render(
                f"LASER x{self.ship.laser_charges}", True, C.LASER_COLOR
            )
            hud_x -= laser_label.get_width()
            surf.blit(laser_label, (hud_x, hud_y))
