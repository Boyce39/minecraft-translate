import pygame
import sys
import random
import math
from pygame.locals import *

# 初始化pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空侵略者")

# 颜色定义
BACKGROUND = (5, 5, 25)
PLAYER_COLOR = (0, 200, 255)
ENEMY_COLORS = [(220, 50, 50), (200, 200, 50), (150, 50, 220)]
BULLET_COLOR = (255, 255, 100)
UI_BACKGROUND = (10, 10, 40, 200)
UI_TEXT = (200, 220, 255)
UI_HIGHLIGHT = (0, 180, 255)

# 字体
font_large = pygame.font.SysFont(None, 64)
font_medium = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 24)

# 玩家类
class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.speed = 6
        self.bullets = []
        self.cooldown = 0
        self.lives = 3
        self.score = 0
        self.weapon_level = 1
        self.weapon_timer = 0
        self.invincible = 0

    def draw(self):
        # 绘制飞船主体
        pygame.draw.polygon(screen, PLAYER_COLOR, [
            (self.x, self.y - self.height//2),
            (self.x - self.width//2, self.y + self.height//2),
            (self.x + self.width//2, self.y + self.height//2)
        ])
        
        # 绘制飞船引擎
        pygame.draw.rect(screen, (255, 100, 0), 
                        (self.x - 10, self.y + self.height//2, 20, 10))
        
        # 绘制飞船细节
        pygame.draw.circle(screen, (100, 255, 255), (self.x, self.y), 8)
        pygame.draw.line(screen, (200, 255, 255), 
                        (self.x - 15, self.y), (self.x + 15, self.y), 2)
        
        # 无敌效果
        if self.invincible > 0:
            pygame.draw.circle(screen, (255, 255, 100, 100), 
                              (self.x, self.y), 30, 2)

    def move(self, direction):
        if direction == "left" and self.x > self.width//2:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.width//2:
            self.x += self.speed

    def shoot(self):
        if self.cooldown <= 0:
            if self.weapon_level == 1:
                self.bullets.append(Bullet(self.x, self.y - 20))
            elif self.weapon_level == 2:
                self.bullets.append(Bullet(self.x - 10, self.y - 15))
                self.bullets.append(Bullet(self.x + 10, self.y - 15))
            elif self.weapon_level >= 3:
                self.bullets.append(Bullet(self.x - 15, self.y - 10))
                self.bullets.append(Bullet(self.x, self.y - 20))
                self.bullets.append(Bullet(self.x + 15, self.y - 10))
            self.cooldown = 15 - min(10, self.weapon_level * 2)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            
        if self.weapon_timer > 0:
            self.weapon_timer -= 1
        elif self.weapon_level > 1:
            self.weapon_level -= 1
            
        if self.invincible > 0:
            self.invincible -= 1
            
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)

# 子弹类
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.radius = 4
        self.damage = 1

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 255, 200), (self.x, self.y), self.radius - 1)

    def update(self):
        self.y -= self.speed

# 敌人类
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        
        if enemy_type == 0:  # 小型敌人
            self.width = 30
            self.height = 30
            self.speed = random.uniform(1.0, 2.0)
            self.health = 1
            self.color = ENEMY_COLORS[0]
            self.score_value = 10
        elif enemy_type == 1:  # 中型敌人
            self.width = 45
            self.height = 40
            self.speed = random.uniform(0.8, 1.5)
            self.health = 2
            self.color = ENEMY_COLORS[1]
            self.score_value = 20
        else:  # 大型敌人
            self.width = 60
            self.height = 50
            self.speed = random.uniform(0.5, 1.0)
            self.health = 3
            self.color = ENEMY_COLORS[2]
            self.score_value = 40
            
        self.direction = random.choice([-1, 1])
        self.shoot_timer = random.randint(60, 180)
        self.bullets = []

    def draw(self):
        # 绘制敌人主体
        pygame.draw.polygon(screen, self.color, [
            (self.x, self.y + self.height//2),
            (self.x - self.width//2, self.y - self.height//2),
            (self.x + self.width//2, self.y - self.height//2)
        ])
        
        # 绘制敌人细节
        pygame.draw.circle(screen, (50, 50, 50), (self.x, self.y), self.width//4)
        pygame.draw.line(screen, (100, 100, 100), 
                        (self.x - self.width//3, self.y), 
                        (self.x + self.width//3, self.y), 2)
        
        # 绘制血条
        bar_width = self.width
        health_width = (self.health / (self.type + 1)) * bar_width
        pygame.draw.rect(screen, (150, 0, 0), 
                        (self.x - bar_width//2, self.y - self.height//2 - 10, 
                         bar_width, 5))
        pygame.draw.rect(screen, (0, 200, 0), 
                        (self.x - bar_width//2, self.y - self.height//2 - 10, 
                         health_width, 5))

    def update(self):
        self.x += self.speed * self.direction
        
        # 边界检测
        if self.x < self.width//2 or self.x > WIDTH - self.width//2:
            self.direction *= -1
            self.y += 20
            
        # 射击逻辑
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = random.randint(120, 240)
            
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > HEIGHT:
                self.bullets.remove(bullet)

    def shoot(self):
        self.bullets.append(EnemyBullet(self.x, self.y + self.height//2))

# 敌人子弹类
class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.radius = 3
        self.damage = 1

    def draw(self):
        pygame.draw.circle(screen, (255, 100, 100), (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 150, 150), (self.x, self.y), self.radius - 1)

    def update(self):
        self.y += self.speed

# 爆炸效果类
class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.radius = 5
        self.max_radius = size * 5
        self.growth_rate = size * 0.8
        self.color = (255, 200, 0)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 100, 0), (self.x, self.y), self.radius * 0.7)

    def update(self):
        self.radius += self.growth_rate
        self.color = (
            max(0, self.color[0] - 4),
            max(0, self.color[1] - 6),
            max(0, self.color[2] - 2)
        )
        return self.radius < self.max_radius

# 道具类
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type  # 0: 武器升级, 1: 生命恢复, 2: 护盾
        self.speed = 2
        self.radius = 12
        
        if power_type == 0:
            self.color = (100, 200, 255)
        elif power_type == 1:
            self.color = (100, 255, 150)
        else:
            self.color = (255, 220, 100)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius, 2)
        
        # 绘制道具符号
        if self.type == 0:  # 武器升级
            pygame.draw.polygon(screen, (255, 255, 255), [
                (self.x, self.y - 5),
                (self.x - 4, self.y + 3),
                (self.x + 4, self.y + 3)
            ])
        elif self.type == 1:  # 生命恢复
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 4, 2)
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y - 4), 2)
        else:  # 护盾
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 6, 2)

    def update(self):
        self.y += self.speed
        return self.y < HEIGHT + self.radius

# 星星背景类
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2.0)
        self.speed = self.size * 0.5
        self.brightness = random.randint(150, 255)

    def draw(self):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

# 游戏类
class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.explosions = []
        self.powerups = []
        self.stars = [Star() for _ in range(100)]
        self.level = 1
        self.game_state = "start"  # start, playing, game_over
        self.spawn_timer = 0
        self.enemy_count = 0
        self.max_enemies = 8 + self.level * 2
        self.level_complete = False
        self.level_transition_timer = 0
        self.particles = []

    def spawn_enemies(self):
        if self.spawn_timer <= 0 and self.enemy_count < self.max_enemies:
            enemy_type = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
            x = random.randint(40, WIDTH - 40)
            y = random.randint(20, 150)
            self.enemies.append(Enemy(x, y, enemy_type))
            self.enemy_count += 1
            self.spawn_timer = 60 - min(40, self.level * 5)

    def check_collisions(self):
        # 玩家子弹与敌人碰撞
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                if dist < max(enemy.width//2, enemy.height//2):
                    enemy.health -= bullet.damage
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    
                    if enemy.health <= 0:
                        self.player.score += enemy.score_value
                        self.explosions.append(Explosion(enemy.x, enemy.y, enemy.type + 1))
                        self.enemies.remove(enemy)
                        self.enemy_count -= 1
                        
                        # 掉落道具 (30% 概率)
                        if random.random() < 0.3:
                            self.powerups.append(PowerUp(enemy.x, enemy.y, random.randint(0, 2)))
                        break
        
        # 敌人子弹与玩家碰撞
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                dist = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
                if dist < 25 and self.player.invincible == 0:
                    self.player.lives -= bullet.damage
                    enemy.bullets.remove(bullet)
                    self.player.invincible = 90  # 1.5秒无敌时间
                    self.explosions.append(Explosion(self.player.x, self.player.y, 2))
                    
                    if self.player.lives <= 0:
                        self.game_state = "game_over"
                    break
        
        # 玩家与道具碰撞
        for powerup in self.powerups[:]:
            dist = math.sqrt((powerup.x - self.player.x)**2 + (powerup.y - self.player.y)**2)
            if dist < 25:
                if powerup.type == 0:  # 武器升级
                    self.player.weapon_level = min(4, self.player.weapon_level + 1)
                    self.player.weapon_timer = 600  # 10秒
                elif powerup.type == 1:  # 生命恢复
                    self.player.lives = min(5, self.player.lives + 1)
                else:  # 护盾
                    self.player.invincible = 180  # 3秒无敌
                self.powerups.remove(powerup)
                break

    def update(self):
        if self.game_state == "playing":
            # 更新玩家
            self.player.update()
            
            # 生成敌人
            if self.spawn_timer > 0:
                self.spawn_timer -= 1
            self.spawn_enemies()
            
            # 更新敌人
            for enemy in self.enemies[:]:
                enemy.update()
                
                # 更新敌人子弹
                for bullet in enemy.bullets:
                    bullet.update()
            
            # 更新爆炸效果
            for explosion in self.explosions[:]:
                if not explosion.update():
                    self.explosions.remove(explosion)
            
            # 更新道具
            for powerup in self.powerups[:]:
                if not powerup.update():
                    self.powerups.remove(powerup)
            
            # 更新星星
            for star in self.stars:
                star.update()
            
            # 检测碰撞
            self.check_collisions()
            
            # 检查关卡完成
            if self.enemy_count == 0 and len(self.enemies) == 0 and self.spawn_timer <= 0:
                self.level_complete = True
                self.level_transition_timer = 180  # 3秒
            
            # 关卡过渡
            if self.level_complete:
                self.level_transition_timer -= 1
                if self.level_transition_timer <= 0:
                    self.level += 1
                    self.max_enemies = 8 + self.level * 2
                    self.level_complete = False

    def draw(self):
        # 绘制背景
        screen.fill(BACKGROUND)
        
        # 绘制星星
        for star in self.stars:
            star.draw()
        
        if self.game_state == "start":
            self.draw_start_screen()
        elif self.game_state == "playing":
            # 绘制玩家
            self.player.draw()
            
            # 绘制玩家子弹
            for bullet in self.player.bullets:
                bullet.draw()
            
            # 绘制敌人
            for enemy in self.enemies:
                enemy.draw()
                
                # 绘制敌人子弹
                for bullet in enemy.bullets:
                    bullet.draw()
            
            # 绘制爆炸效果
            for explosion in self.explosions:
                explosion.draw()
            
            # 绘制道具
            for powerup in self.powerups:
                powerup.draw()
            
            # 绘制UI
            self.draw_ui()
            
            # 绘制关卡过渡
            if self.level_complete:
                self.draw_level_complete()
        elif self.game_state == "game_over":
            self.draw_game_over()

    def draw_ui(self):
        # 绘制半透明背景
        s = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        s.fill((10, 10, 40, 200))
        screen.blit(s, (0, 0))
        
        s = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        s.fill((10, 10, 40, 200))
        screen.blit(s, (0, HEIGHT - 40))
        
        # 绘制分数
        score_text = font_medium.render(f"分数: {self.player.score}", True, UI_TEXT)
        screen.blit(score_text, (20, 20))
        
        # 绘制关卡
        level_text = font_medium.render(f"关卡: {self.level}", True, UI_TEXT)
        screen.blit(level_text, (WIDTH - level_text.get_width() - 20, 20))
        
        # 绘制生命
        for i in range(self.player.lives):
            pygame.draw.polygon(screen, (255, 100, 100), [
                (30 + i * 30, HEIGHT - 20),
                (20 + i * 30, HEIGHT - 10),
                (40 + i * 30, HEIGHT - 10)
            ])
        
        # 绘制武器状态
        weapon_text = font_small.render(f"武器等级: {self.player.weapon_level}", True, UI_HIGHLIGHT)
        screen.blit(weapon_text, (WIDTH - weapon_text.get_width() - 20, HEIGHT - 30))
        
        # 绘制武器计时条
        if self.player.weapon_timer > 0:
            bar_width = 100
            bar_height = 10
            fill_width = (self.player.weapon_timer / 600) * bar_width
            pygame.draw.rect(screen, (50, 50, 80), 
                           (WIDTH - bar_width - 25, HEIGHT - 15, bar_width, bar_height))
            pygame.draw.rect(screen, UI_HIGHLIGHT, 
                           (WIDTH - bar_width - 25, HEIGHT - 15, fill_width, bar_height))

    def draw_start_screen(self):
        title = font_large.render("太空侵略者", True, UI_HIGHLIGHT)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        subtitle = font_medium.render("按空格键开始游戏", True, UI_TEXT)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2))
        
        controls = [
            "方向键: 移动飞船",
            "空格键: 发射子弹",
            "P键: 暂停游戏",
            "ESC键: 退出游戏"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = font_small.render(text, True, UI_TEXT)
            screen.blit(ctrl_text, (WIDTH//2 - ctrl_text.get_width()//2, HEIGHT//1.8 + i * 30))
        
        # 绘制动画飞船
        pygame.draw.polygon(screen, PLAYER_COLOR, [
            (WIDTH//2, HEIGHT//1.3 - 15),
            (WIDTH//2 - 25, HEIGHT//1.3 + 15),
            (WIDTH//2 + 25, HEIGHT//1.3 + 15)
        ])

    def draw_level_complete(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0, 0))
        
        level_text = font_large.render(f"关卡 {self.level} 完成!", True, UI_HIGHLIGHT)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//3))
        
        next_text = font_medium.render(f"下一关: {self.level + 1}", True, UI_TEXT)
        screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2))
        
        score_text = font_medium.render(f"当前分数: {self.player.score}", True, UI_TEXT)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//1.8))

    def draw_game_over(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        screen.blit(s, (0, 0))
        
        game_over = font_large.render("游戏结束", True, (220, 50, 50))
        screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//3))
        
        score_text = font_medium.render(f"最终分数: {self.player.score}", True, UI_TEXT)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        restart_text = font_medium.render("按R键重新开始", True, UI_HIGHLIGHT)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//1.5))

# 主游戏循环
def main():
    clock = pygame.time.Clock()
    game = Game()
    paused = False
    
    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if game.game_state == "start" and event.key == K_SPACE:
                    game.game_state = "playing"
                
                if game.game_state == "game_over" and event.key == K_r:
                    game = Game()
                
                if event.key == K_p and game.game_state == "playing":
                    paused = not paused
        
        if not paused and game.game_state == "playing":
            # 键盘输入
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                game.player.move("left")
            if keys[K_RIGHT]:
                game.player.move("right")
            if keys[K_SPACE]:
                game.player.shoot()
            
            # 更新游戏状态
            game.update()
        
        # 绘制游戏
        game.draw()
        
        # 显示暂停状态
        if paused:
            pause_text = font_large.render("游戏暂停", True, UI_HIGHLIGHT)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//3))
            
            continue_text = font_medium.render("按P键继续", True, UI_TEXT)
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()