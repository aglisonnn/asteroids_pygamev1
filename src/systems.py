
# ASTEROIDE SINGLEPLAYER v1.0
# This file coordinates world state, spawning, collisions, scoring, and progression.

import math
from random import uniform

import pygame as pg

import config as C
from sprites import Asteroid, Laser, PowerUp, Ship, UFO
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:
    # Initialize the world state, entity groups, timers, and player progress.
    def __init__(self):
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.lasers = pg.sprite.Group()  # Raios laser do jogador
        self.all_sprites = pg.sprite.Group(self.ship)
        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY
        self.game_over = False  # Sinaliza fim de jogo para a cena principal

    def start_wave(self):
        # Spawn a new asteroid wave with difficulty based on the current round.
        self.wave += 1
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
        # Create an asteroid and register it in the world groups.
        a = Asteroid(pos, vel, size)
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def spawn_ufo(self):
        # Spawn a single UFO at a screen edge and send it across the playfield.
        if self.ufos:
            return
        small = uniform(0, 1) < 0.5
        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        ufo.dir.xy = (1, 0) if x == 0 else (-1, 0)
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def ufo_try_fire(self):
        # Let every active UFO attempt to fire at the ship.
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
        # Trigger the ship hyperspace action and apply its score penalty.
        self.ship.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def update(self, dt: float, keys):
        # Update the world simulation, timers, enemy behavior, and progression.
        self.ship.control(keys, dt)
        self.all_sprites.update(dt)
        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5
        if self.ufos:
            self.ufo_try_fire()
        else:
            self.ufo_timer -= dt
        if not self.ufos and self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        self.handle_collisions()

        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

    def handle_collisions(self):
        # 1. Nave coleta power-ups (Escudo, Vida, Tiro Duplo ou Laser)
        power_hits = pg.sprite.spritecollide(
            self.ship, self.powerups, True,
            collided=lambda a, b: (a.pos - b.pos).length() < (a.r + b.r)
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

        # 2. Tiros da nave acertam asteroides
        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in hits.items():
            self.split_asteroid(ast)

        # 3. Raio laser acerta asteroides (colisão geométrica ponto-linha)
        for laser in list(self.lasers):
            for ast in list(self.asteroids):
                if laser.hits(ast):
                    self.split_asteroid(ast)

        # 4. Raio laser acerta UFOs
        for laser in list(self.lasers):
            for ufo in list(self.ufos):
                if laser.hits(ufo):
                    score = (C.UFO_SMALL["score"] if ufo.small
                             else C.UFO_BIG["score"])
                    self.score += score
                    ufo.kill()

        # 5. Tiros dos UFOs acertam asteroides
        ufo_hits = pg.sprite.groupcollide(
            self.asteroids,
            self.ufo_bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in ufo_hits.items():
            self.split_asteroid(ast)

        # 6. Colisões letais com a nave (verificando o escudo)
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
                if (bullet.pos - self.ship.pos).length() < (bullet.r
                                                             + self.ship.r):
                    bullet.kill()
                    self.take_damage()
                    break

        # 7. Tiros da nave acertam UFOs
        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    score = (C.UFO_SMALL["score"] if ufo.small
                             else C.UFO_BIG["score"])
                    self.score += score
                    ufo.kill()
                    b.kill()

    def split_asteroid(self, ast: Asteroid):
        # Destroy an asteroid, award score, and spawn its smaller fragments.
        self.score += C.AST_SIZES[ast.size]["score"]
        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)
        ast.kill()
        for s in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, s)

        # Chance de dropar um power-up com pesos configuráveis
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
        # Fallback para o último tipo caso haja erro de arredondamento
        return list(C.POWERUP_WEIGHTS.keys())[-1]

    def take_damage(self):
        # Se a nave tem escudo ativo, ela perde o escudo e ganha invulnerabilidade
        if self.ship.shield_time > 0:
            self.ship.shield_time = 0
            self.ship.invuln = 1.0
        # Se não tem escudo, morre normalmente
        else:
            self.ship_die()

    def ship_die(self):
        # Remove uma vida; sinaliza game over ou reposiciona a nave.
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True  # Game.run() detecta e muda de cena
            return
        self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
        self.ship.vel.xy = (0, 0)
        self.ship.angle = -90
        self.ship.invuln = C.SAFE_SPAWN_TIME
        self.ship.double_shot_time = 0.0  # Perde tiro duplo ao morrer
        self.ship.laser_charges = 0       # Perde cargas de laser ao morrer
        self.safe = C.SAFE_SPAWN_TIME

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        # Draw all world entities and the current HUD information.
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), width=1)

        # Linha principal: score, vidas, wave
        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))

        # Indicadores de power-ups activos (canto superior direito)
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
