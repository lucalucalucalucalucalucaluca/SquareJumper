# SQUARE JUMPER GAME
# Authors: Ivan Flühmann, Amelio Della Torre, Luca Bachmann
# Codebase inspired by https://coderslegacy.com/python/pygame-platformer-game-development/

#Imports
import pygame
from pygame.locals import *
import sys
import random
import time
import json
from settings import WIDTH, HEIGHT, ACC, FRIC, FPS, BACKGROUND_IMAGES, MUSIC_FILE, FONT, LOGO, CHAR #Loading assets from asstes folder

#initializing game data, music, background, etc...
pygame.init()
vec = pygame.math.Vector2

platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

FramePerSec = pygame.time.Clock()

pygame.mixer.music.load(MUSIC_FILE)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square Jumper")

background_images = [pygame.image.load(img).convert() for img in BACKGROUND_IMAGES]
current_bg_index = 0
next_bg_index = 0
background_image = background_images[current_bg_index]
transition_alpha = 0
is_transitioning = False
transition_speed = 5

transition_surface = pygame.Surface((WIDTH, HEIGHT))
transition_surface.set_alpha(transition_alpha)

highscore_file = "highscores.json"

#Save Highscore
def save_score(name, score):
    try:
        with open(highscore_file, "r") as f:
            data = json.load(f) #loading highscores.json
    except (FileNotFoundError, json.JSONDecodeError):
        data = [] #set data empty
    data.append({"name": name, "score": score}) #append new name
    with open(highscore_file, "w") as f:
        json.dump(data, f, indent=4)

#Load Highscore
def load_highscores():
    for _ in range(3):  # 3reading tries
        try:
            with open(highscore_file, "r") as f:
                data = json.load(f)
            break
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
            break
        except PermissionError:
            time.sleep(0.05)  #sleep timer to avoid multiple reads, would throw permission error
    return sorted(data, key=lambda x: x['score'], reverse=True)[:10] #return sorted names

#Highscore List Screen
def show_highscores():
    font = pygame.font.Font(FONT, 30) #set font sizes
    small_font = pygame.font.Font(FONT, 20)
    while True:
        displaysurface.fill((0, 0, 0))
        title = font.render("Highscores", True, (255, 255, 0))
        displaysurface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50)) #display text

        highscores = load_highscores() #get highscores
        for idx, entry in enumerate(highscores):
            text = small_font.render(f"{idx+1}. {entry['name']} - {entry['score']}", True, (255, 255, 255))
            displaysurface.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + idx * 30)) #diplay name list

        back_text = small_font.render("Press M to return to menu", True, (255, 255, 255))
        delete_text = small_font.render("Press DELETE to clear highscores", True, (255, 0, 0)) #display buttons
        displaysurface.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 70))
        displaysurface.blit(delete_text, (WIDTH // 2 - delete_text.get_width() // 2, HEIGHT - 40))
        pygame.display.update()

        for event in pygame.event.get(): #check button presses
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_m: #track M
                    return
                elif event.key == K_DELETE: #track DEL
                    try:
                        with open(highscore_file, "w") as f:
                            json.dump([], f)
                    except PermissionError:
                        print("Deletion failed due to timing error") #catch weird error that happens sometimes, probably because of timing

#Story Screen
def show_story():
    font = pygame.font.Font(FONT, 20) #set font
    while True:
        displaysurface.fill((0, 0, 0))
        story_lines = [
            "You are a brave student at HSG,",
            "the learning phase has started",
            "",
            "Your Goal:",
            "Find a place to study",
            "in the Square Building at HSG",        #story
            "",
            "Jump up the different levels",
            "to find the glorious COZY COUCH.",
            "Avoid falling into despair!",
            "Your Uni degree depends on it...",
            "",
            "Press M to return to the main menu."
        ]
        for idx, line in enumerate(story_lines):
            text = font.render(line, True, (255, 255, 255))
            displaysurface.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + idx * 30)) #display in lines so text doesnt overlap

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_m: #catch M for back to Menu
                return

#Main Menu Screen
def title_screen():
    try:
        logo = pygame.image.load(LOGO).convert_alpha() #get logo
        logo = pygame.transform.scale(logo, (300, 300)) # force size
    except:
        logo = None

    font = pygame.font.Font(FONT, 20) #font

    while True:
        displaysurface.fill((0, 0, 0))
        if logo:
            displaysurface.blit(logo, (WIDTH // 2 - logo.get_width() // 2, 50)) #logo coordinates

        startPrompt = font.render("Press ENTER to start", True, (255, 0, 0))
        storyPrompt = font.render("Press S to see the story", True, (255, 0, 0))
        scorePrompt = font.render("Press H to view highscores", True, (255, 0, 0))
        controlsPrompt = font.render("Arrow keys to move, Spacebar to jump", True, (255, 255, 255)) #buttons

        displaysurface.blit(startPrompt, (WIDTH // 2 - startPrompt.get_width() // 2, 400))
        displaysurface.blit(storyPrompt, (WIDTH // 2 - storyPrompt.get_width() // 2, 450))
        displaysurface.blit(scorePrompt, (WIDTH // 2 - scorePrompt.get_width() // 2, 480))
        displaysurface.blit(controlsPrompt, (WIDTH // 2 - controlsPrompt.get_width() // 2, 520)) #button coordinates

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN: #start game
                    main()
                elif event.key == K_s: #story page
                    show_story()
                elif event.key == K_h: #highscore list
                    show_highscores()

        FramePerSec.tick(FPS) #standard FPS set to 80, dont go too much higher bcs may get crashy

#Game Over Screen
def game_over_screen(score):
    pygame.mixer.music.stop() #stop music
    font = pygame.font.Font(FONT, 40)
    small_font = pygame.font.Font(FONT, 20)
    input_font = pygame.font.Font(FONT, 30)
    name = "" #start with no name
    active = True
    while True:
        displaysurface.fill((0, 0, 0))
        msg = font.render("Game Over", True, (255, 0, 0))
        score_display = small_font.render(f"Your score: {score}", True, (255, 255, 255))
        name_prompt = small_font.render("Enter your name:", True, (255, 255, 255))                  #texts
        name_input = input_font.render(name + ("_" if active else ""), True, (255, 255, 0))
        restart_prompt = small_font.render("Press ENTER to go back to MENU", True, (255, 255, 255))
        displaysurface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 100))
        displaysurface.blit(score_display, (WIDTH // 2 - score_display.get_width() // 2, 160))
        displaysurface.blit(name_prompt, (WIDTH // 2 - name_prompt.get_width() // 2, 220))
        displaysurface.blit(name_input, (WIDTH // 2 - name_input.get_width() // 2, 260))
        displaysurface.blit(restart_prompt, (WIDTH // 2 - restart_prompt.get_width() // 2, 320))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if name.strip(): #if name exists save score
                        save_score(name, score)
                    pygame.mixer.music.play(-1)
                    title_screen() #if no name just dont save anything and return anyways
                elif event.key == K_BACKSPACE:
                    name = name[:-1] #delete letter from name
                else:
                    if len(name) < 12 and event.unicode.isprintable(): #add letter to name up to 12
                        name += event.unicode

#Background transition
def draw_background():
    global transition_alpha, is_transitioning, current_bg_index, next_bg_index, background_image #get variables from draw_background()

    displaysurface.blit(background_image, (0, 0)) #draw background

    if is_transitioning: #function for transition between backgrounds
        transition_alpha += transition_speed
        if transition_alpha >= 255: #transition between pictures is in 255 grades
            transition_alpha = 0
            is_transitioning = False #after transistion reset alpha and boolean
            current_bg_index = next_bg_index
            background_image = background_images[current_bg_index] #set next background
        else:
            transition_surface.set_alpha(transition_alpha) #true while in transition until alpha reaches 255
            displaysurface.blit(transition_surface, (0, 0)) #display transitioning surface

#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load(CHAR).convert_alpha() #get jumpy guy from assets
        self.rect = self.surf.get_rect()
        self.pos = vec((10, 500)) #starting position
        self.vel = vec(0, 0)
        self.acc = vec(0, 0) #starting speed 0
        self.jumping = False #starting standing still
        self.score = 0 #starting with 0 score

    #movment function
    def move(self):
        self.acc = vec(0, 0.5) #can accelerate to left or right
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]: #negative horizontal acc for going left
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]: #positive horizontal acc for going right
            self.acc.x = ACC
        self.acc.x += self.vel.x * FRIC #cant accelerate forever
        self.vel += self.acc #set speed
        self.pos += self.vel + 0.5 * self.acc #position up to date with movement
        if self.pos.x > WIDTH: #cant go out of screen just stops at max width
            self.pos.x = 0
        if self.pos.x < 0: #also stops at min width
            self.pos.x = WIDTH
        self.rect.midbottom = self.pos

    #jumping function
    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False) #tracker to check if you hit plattform
        if hits and not self.jumping: #falling check
            self.jumping = True #start jump
            self.vel.y = -20 #falling velocity

    def cancel_jump(self): #makes weak jumps possible, if spacebar only slightly tapped
        if self.jumping and self.vel.y < -3:
            self.vel.y = -3

    def update(self): #score, position and background updater
        global current_bg_index, next_bg_index, background_image, is_transitioning
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            for platform in hits: #check for every platform
                if self.rect.bottom <= platform.rect.top + 15 and self.rect.bottom >= platform.rect.top - 15: #check if landed on platform
                    if platform.point:
                        platform.point = False
                        self.score += 1 #add point

                        if self.score in [15, 30, 45, 60] and current_bg_index < len(background_images) - 1: #change background at 15, 30, 45, 60 points. space background stays forever after that
                            next_bg_index = current_bg_index + 1 # +1 index
                            is_transitioning = True #to start function from above
                            transition_surface.blit(background_images[next_bg_index], (0, 0)) #display transition

                    self.pos.y = platform.rect.top + 1 #set position of player above plattform
                    self.vel.y = 0 #stop fall
                    self.jumping = False #stop jumping

#Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        width = random.randint(75, 150) #random size of plattform
        height = 20 #height is always same
        self.surf = pygame.Surface((width, height))
        self.surf.fill((50, 50, 50)) #color of plattform
        pygame.draw.rect(self.surf, (255, 255, 255), self.surf.get_rect(), 2) #white border of platform
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10), random.randint(0, HEIGHT - 30))) #random position to spawn
        self.speed = random.randint(-1, 1) #random speed either to left or right
        self.point = True #set pointable
        self.moving = True

    #platform movement
    def move(self):
        if self.moving:
            self.rect.move_ip(self.speed, 0) #set speed
            if self.speed > 0 and self.rect.left > WIDTH: #if reaches border of screen just spawn again on other side, like in doodle jump
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0: #same for other side
                self.rect.left = WIDTH

#function to stop platforms from spawning on each other
def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True #return true if they would collide
    for entity in groupies:
        if entity == platform:
            continue
        if (abs(platform.rect.top - entity.rect.bottom) < 40) and (abs(platform.rect.bottom - entity.rect.top) < 40): #check for height overlap
            return True
    return False

#for generating the platforms
def plat_gen():
    while len(platforms) < 6: #spawn 6 at max, seems ok for difficulty and performance
        width = random.randrange(50, 100) #for random width
        p = Platform() #create platform
        C = True #for collision check
        while C:
            p = Platform() #spawn
            p.rect.center = (random.randrange(0, WIDTH - width), random.randrange(-50, 0)) #set spawnpoint
            C = check(p, platforms) #collision check
        platforms.add(p) #add to group to stop at 6
        all_sprites.add(p) #for main function

#main game loop
def main():
    global all_sprites, platforms, background_image, P1
    all_sprites.empty() #reset at start of new game
    platforms.empty() #reset

    P1 = Player() #initialize player

    #starting plattform
    PT1 = pygame.sprite.Sprite()
    PT1.surf = pygame.Surface((WIDTH, 20))
    PT1.surf.fill((0, 0, 0))
    PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT))
    PT1.moving = False
    PT1.point = False

    #add starter platform
    all_sprites.add(PT1)
    all_sprites.add(P1)
    platforms.add(PT1)

    #loop for platform gen
    for _ in range(random.randint(6, 7)):
        C = True
        pl = Platform()
        while C:
            pl = Platform()
            C = check(pl, platforms)
        platforms.add(pl)
        all_sprites.add(pl)

    #movement tracker
    while True:
        P1.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                P1.jump() #full jump
            if event.type == KEYUP and event.key == K_SPACE:
                P1.cancel_jump() #if only pressed for short time smaller jump

        #if fall out of screen
        if P1.rect.top > HEIGHT:
            for entity in all_sprites:
                entity.kill()
            game_over_screen(P1.score) #go to game over killed
            return

        #kill platforms that leave screen to make place for new ones
        if P1.rect.top <= HEIGHT / 3:
            P1.pos.y += abs(P1.vel.y)
            for plat in platforms: #position checker
                plat.rect.y += abs(P1.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()

        #generate platforms, draw current bg, set font for score
        plat_gen()
        draw_background()
        f = pygame.font.Font(FONT, 15)

        #display score, uses shadow on font for better readability
        g_shadow = f.render(f"Score:{P1.score}", True, (0, 0, 0))
        g_text = f.render(f"Score:{P1.score}", True, (255, 255, 255))
        displaysurface.blit(g_shadow, (WIDTH - 130 + 1, 11))
        displaysurface.blit(g_text, (WIDTH - 130, 10))

        #loop for movment
        for entity in all_sprites:
            displaysurface.blit(entity.surf, entity.rect)
            if hasattr(entity, "move"):
                entity.move()

        #updater in main loop to make game work
        pygame.display.update()
        FramePerSec.tick(FPS) #set to update loop at set FPS

#starting the game initially go to title screen and main
title_screen()
main()
