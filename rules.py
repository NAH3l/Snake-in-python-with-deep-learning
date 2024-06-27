import pygame
import random
from entities import SnakePlayer, Apple
import affichage         
import numpy as np
from bot_qlearning import Bot

class Jeu:
    def __init__(self, screen, rect_x, rect_y, rect_width, rect_height):
        self.screen = screen
        self.rect_x = rect_x
        self.rect_y = rect_y
        self.rect_width = rect_width
        self.rect_height = rect_height

        self.player = SnakePlayer(screen, rect_x, rect_y, rect_width, rect_height)
        self.apple = Apple(screen, rect_x, rect_y, rect_width, rect_height)
        self.actions = ["LEFT", "RIGHT", "UP", "DOWN"]
        self.bot = Bot(self.actions)
        self.font = pygame.font.Font(None, 24)  # Initialize font with smaller size

    #  Game Rules
    def check_collision(self):
        # Check collision with walls
        if (self.player.segments[0]["x"] < self.rect_x or 
            self.player.segments[0]["x"] >= self.rect_x + self.rect_width or
            self.player.segments[0]["y"] < self.rect_y or
            self.player.segments[0]["y"] >= self.rect_y + self.rect_height):
            self.reset_game()

        # Check collision with self
        for segment in self.player.segments[1:]:
            if self.player.segments[0]["x"] == segment["x"] and self.player.segments[0]["y"] == segment["y"]:
                self.reset_game()
                

        # Check collision with apple
        if self.player.segments[0]["x"] == self.apple.apple_position_x and self.player.segments[0]["y"] == self.apple.apple_position_y:
            self.apple.update_position()  # Mettre à jour la position de l'apple
            self.player.grow()  # Add a new segment
            self.player.score += 1  # Increment score by 1
            self.player.speed += 2  # Increment speed by 2
            

    # Draw the game
    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(self.rect_x, self.rect_y, self.rect_width, self.rect_height), 1)
        self.player.draw_player()
        self.apple.draw_apple()

        # Draw score, speed, and length
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        speed_text = self.font.render(f"Speed: {self.player.speed}", True, (255, 255, 255))
        length_text = self.font.render(f"Length: {len(self.player.segments)}", True, (255, 255, 255))

        self.screen.blit(score_text, (self.rect_x , self.rect_y - 40))
        self.screen.blit(speed_text, (self.rect_x + 150 , self.rect_y - 40))
        self.screen.blit(length_text, (self.rect_x + 300, self.rect_y - 40))

        pygame.display.flip()

    def run_game(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if running:
                state = self.bot.get_state(self.player, self.apple)
                action = self.bot.choose_action(state)
                
                # Convertir l'action en direction pour le serpent
                if action == "LEFT" and self.player.direction != "RIGHT":
                    self.player.direction = "LEFT"
                elif action == "RIGHT" and self.player.direction != "LEFT":
                    self.player.direction = "RIGHT"
                elif action == "UP" and self.player.direction != "DOWN":
                    self.player.direction = "UP"
                elif action == "DOWN" and self.player.direction != "UP":
                    self.player.direction = "DOWN"

                self.player.move_player()
                
                # Calcul de la récompense
                reward = 0
                if self.check_collision():
                    reward = -100  # Grosse pénalité pour avoir perdu
                elif self.player.segments[0]["x"] == self.apple.apple_position_x and self.player.segments[0]["y"] == self.apple.apple_position_y:
                    reward = 100  # Grosse récompense pour avoir mangé la pomme

                next_state = self.bot.get_state(self.player, self.apple)
                self.bot.update_q(state, action, reward, next_state)

                self.check_collision()
                self.draw()
                affichage.display_information(self)
            clock.tick(self.player.speed)  # Control the speed of the game

        pygame.quit()

    def reset_game(self):
        # Réinitialisation du jeu (remet les objets à leur état initial)
        self.player = SnakePlayer(self.screen, self.rect_x, self.rect_y, self.rect_width, self.rect_height)
        self.apple = Apple(self.screen, self.rect_x, self.rect_y, self.rect_width, self.rect_height)
        self.player.score = 0
        self.player.speed = 10

        # Relance de la partie
        self.run_game()         