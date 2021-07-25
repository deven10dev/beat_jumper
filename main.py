import pygame
import time
import aubio
import numpy as num
import pyaudio
import wave
from random import randrange

pygame.init()
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=1, rate=44100, input=True,
                frames_per_buffer=1024)
pDetection = aubio.pitch("default", 2048,
                         2048 // 2, 44100)
pDetection.set_unit("Hz")
pDetection.set_silence(-40)

# Loading all the images and setting the size of the window
opening_screen_image = pygame.image.load(r"assets/images/opening.png")
main_screen_image = pygame.image.load(r"assets/images/opening.png")
running_game_image = pygame.image.load(r"assets/images/runscreen.jpeg")
character_image = pygame.image.load(r"assets/images/tile.png")
obstacle_image = pygame.image.load(r"assets/images/obstacle000.png")
pause_image = pygame.image.load(r"assets/images/pause.png")
pause_screen_image = pygame.image.load(r"assets/images/pause_background.png")

# sound effect variable should be declared here
button_click_sound = pygame.mixer.Sound(r'assets/sounds/button_click.wav')
jumping_sound = pygame.mixer.Sound(r'assets/sounds/Mario_jump_sound.wav')

button_click_sound.set_volume(0.09)
jumping_sound.set_volume(0.02)

window_width = main_screen_image.get_width()
window_height = main_screen_image.get_height()
screen = pygame.display.set_mode((window_width, window_height))

# Title of the window
pygame.display.set_caption('Beat Jumper')
clock = pygame.time.Clock()

# All the colors should be declared here
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128,128,128)
box = (35, 41, 53)
green = (0,255,0)
red = (255, 46, 46)

# declare global variables here
global side, flag, score, high_score
side = -2.5
flag = 0
score = 0
high_score = 0

# global variables of run_game function
global character_x, character_y, obstacle_x1, obstacle_y1, counter


# general purpose text
def display_text(text, text_style, text_size, text_color, text_X, text_Y):
    font = pygame.font.Font(text_style, text_size)
    text = font.render(text, True, text_color)
    text_rect = text.get_rect()
    text_rect.center = (text_X, text_Y)
    screen.blit(text, text_rect)


# general purpose button
# add another argument to change font style if needed
def button(message, message_size, active_color, inactive_color, message_color, X_co, Y_co, button_width, button_height,
           action=None):
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()
    ev = pygame.event.get()

    if X_co < mouse_pos[0] < X_co+button_width and Y_co < mouse_pos[1] < Y_co+button_height:
        pygame.draw.rect(screen, active_color, (X_co, Y_co, button_width, button_height))
        display_text(message, 'freesansbold.ttf', message_size, message_color, X_co + button_width // 2,
                     Y_co + button_height // 2)

        if mouse_clicked[0] == 1 and action != None:
            pygame.mixer.Sound.play(button_click_sound)
            time.sleep(0.25)
            screen.fill(black)
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (X_co, Y_co, button_width, button_height))
        display_text(message, 'freesansbold.ttf', message_size, message_color, X_co + button_width // 2,
                 Y_co + button_height // 2)


def pause_screen():
    pause_screen_x = 230
    pause_screen_y = 130

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.blit(pause_screen_image, (pause_screen_x, pause_screen_y))

        button("Resume", 16, gray, green, black, pause_screen_x + 95, pause_screen_y + 15, 100, 40, action=resume_game)
        button("New Game", 16, gray, green, black, pause_screen_x + 95, pause_screen_y + 65, 100, 40, action=new_game)
        button("Main Menu", 16, gray, green, black, pause_screen_x + 95, pause_screen_y + 115, 100, 40, action=main_screen)

        pygame.display.update()
        clock.tick(90)


def crash():
    global score, high_score, character_image, character_x, character_y, obstacle_x1, obstacle_y1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if score > high_score:
            high_score = score

        screen.blit(pause_screen_image, (230, 130))
        display_text("You Crashed", 'freesansbold.ttf', 30, white, 230+pause_screen_image.get_width()//2, 150)
        button("New Game", 16, gray, green, black, 230+100, 130 + 50, 100, 40, action=new_game)
        button("Main Menu", 16, gray, green, black, 230+100, 130 + 100, 100, 40,
               action=main_screen)


        pygame.display.update()
        clock.tick(90)


def move_left(xco):
    return xco-8


# Front page or main screen of the game
# Add anything that should be on front page here
# It is independent function and can run on its own
def main_screen():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.blit(main_screen_image, (0, 0))

        button("New Game", 16, green, red, black, window_width//2-50, window_height//2,  100, 40,
               action=new_game)

        button("Quit", 16, green, red, black, window_width//2-50, window_height//2+50, 100, 40, action=quit_game)

        pygame.display.update()
        clock.tick(90)


def opening_screen():

    screen.blit(opening_screen_image, (0, 0))
    pygame.display.update()
    time.sleep(1)
    screen.fill(black)
    main_screen()


# This function is to quit game
def quit_game():
    pygame.quit()
    quit()


def new_game():
    global character_x, character_y, obstacle_x1, obstacle_y1, counter
    global side, score

    character_x = 20
    character_y = 270
    obstacle_x1 = 750
    obstacle_y1 = character_y
    counter = 3

    score = 0
    side = -2.5

    run_game()


def resume_game():

    run_game()


def run_game():
    global character_x, character_y, obstacle_x1, obstacle_y1, counter
    global side, flag, score
    global character_image, obstacle_image
    global high_score, type_of_obstacle

    topleft_corner_cx = character_x; topleft_corner_cy = character_y
    topright_corner_cx = character_x + 60; topright_corner_cy = character_y
    bottomleft_corner_cx = character_x; bottomleft_corner_cy = character_y + 86
    bottomright_corner_cx = character_x + 60; bottomright_corner_cy = character_y + 86

    topleft_corner_ox = obstacle_x1; topleft_corner_oy = obstacle_y1
    type_of_obstacle = randrange(0, 3, 1)
    rotate = 0

    character_image = pygame.image.load(r"assets/images/tile.png")
    while True:
        topleft_corner_ox = obstacle_x1; topright_corner_cx = character_x + 60
        bottomright_corner_cy = character_y + 86; bottomleft_corner_cy = character_y + 86
        topleft_corner_oy = obstacle_y1; topright_corner_cy = character_y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # pitch detection code
        data = stream.read(1024)
        samples = num.fromstring(data,
                                 dtype=aubio.float_type)
        pitch = pDetection(samples)[0]
        volume = num.sum(samples ** 2) / len(samples)
        volume = "{:.6f}".format(volume)
        volume = float(volume) * 10000

        #print(pitch)
        if 300 < pitch < 5500 and 20 < volume:
            if flag == 0:
                pygame.mixer.Sound.play(jumping_sound)

            flag = 1

        if flag == 1:
            character_image = pygame.image.load(r"assets/images/tile.png")
            if character_y == 120:
                # down
                side = 6
            elif character_y == 270:
                flag = 0
                # up
                side = -6

            character_y += side

        if topleft_corner_ox-topright_corner_cx <= 0:
            if topleft_corner_oy-topright_corner_cy == 6:
                character_image = pygame.image.load(r"assets/images/tile002.png")
            elif bottomright_corner_cy-topleft_corner_oy > 0 and topleft_corner_cx < topleft_corner_ox and topleft_corner_cx+character_image.get_width()//2 < topleft_corner_ox+obstacle_image.get_width()//2:
                if bottomright_corner_cy-4 - topleft_corner_oy+20 >= 50 and topright_corner_cx-topleft_corner_ox <= 5:
                    character_image = pygame.image.load(r"assets/images/tile002.png")
            elif topleft_corner_oy-bottomleft_corner_cy <= 10:
                if 0 <= type_of_obstacle <=2:
                    if 0 < topleft_corner_ox+50-bottomleft_corner_cx+30 <= 80:
                        character_image = pygame.image.load(r"assets/images/tile002.png")

        screen.blit(running_game_image, (0, 0))
        screen.blit(pause_image, (640, 10))
        screen.blit(character_image, (character_x, character_y))
        screen.blit(obstacle_image, (obstacle_x1, obstacle_y1))

        button("Score:{}".format((int(score))), 20, box, box, white, 10, 10, 120, 25, action=None)
        button("High Score:{}".format((int(high_score))), 20, box, box, white, 10, 45, 170, 25, action=None)

        # counter at the start of the game
        if counter >= 0:
            character_image = pygame.image.load(r"assets/images/tile.png")
            if counter >= 0:
                if counter >= 0:
                    if counter >= 0:
                        display_text("{}".format(counter), 'freesansbold.ttf', 90, black, window_width // 2 + 2, window_height // 2 - 13)
            time.sleep(0.8)
            counter -= 1

        # add obstacles here
        obstacle_x1 = move_left(obstacle_x1)
        if obstacle_x1 <= -90:
            obstacle_x1 = 730
            type_of_obstacle = randrange(0, 3, 1)
            obstacle_image = pygame.image.load(r"assets/images/obstacle00{}.png".format(type_of_obstacle))

        if 640 < pygame.mouse.get_pos()[0] <704 and 10 < pygame.mouse.get_pos()[1] <74 and pygame.mouse.get_pressed()[0] == 1:

            pygame.mixer.Sound.play(button_click_sound)
            pause_screen()

        # add highscore calculating code here and also display new high score on crash screen
        if topleft_corner_ox-topright_corner_cx <= 0:
            if topleft_corner_oy-topright_corner_cy == 6:
                crash()

            elif bottomright_corner_cy-topleft_corner_oy > 0 and topleft_corner_cx < topleft_corner_ox and topleft_corner_cx+character_image.get_width()//2 < topleft_corner_ox+obstacle_image.get_width()//2:
                if bottomright_corner_cy-4 - topleft_corner_oy+20 >= 50 and topright_corner_cx-topleft_corner_ox <= 5:
                    crash()
                else:
                    pass
            elif topleft_corner_oy-bottomleft_corner_cy <= 10:
                if 0 <= type_of_obstacle <=2:
                    if 0 < topleft_corner_ox+50-bottomleft_corner_cx+30 <= 80:
                        crash()
                    else:
                        pass
                elif 3 <= type_of_obstacle <= 5:
                    if topright_corner_cx < topleft_corner_ox+20:
                        if bottomright_corner_cy-topleft_corner_oy <= 10:
                            crash()
                        else:
                            pass
                    elif 0 < topleft_corner_ox+25-bottomleft_corner_cx+30 <= 10:
                        if bottomleft_corner_cx-topleft_corner_ox+50 > 10:
                            pass
                        else:
                            crash()
                    else:
                        pass

        score += 0.1
        rotate += 1

        if counter < 0:
            character_image = pygame.image.load(r"assets/images/tile00{}.png".format(int((rotate//6) % 2)))

        pygame.display.update()
        clock.tick(90+score//9)


# Call opening_screen function since the game starts from that point
opening_screen()