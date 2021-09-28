from sound_manager import SoundManager
import json
import pygame


class LevelTransition:
    """Displays a level transition"""
    TRANSITION_CHANNEL = 4

    def __init__(self, screen, score_controller, transition_time=5000):
        self.screen = screen
        self.score_controller = score_controller
        self.sound = SoundManager(['GetLoud.wav'], keys=['transition'],
                                  channel=LevelTransition.TRANSITION_CHANNEL, volume=0.6)
        self.font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 32)
        self.ready_msg = self.font.render('Get Ready!', True, ScoreBoard.SCORE_WHITE)
        self.ready_msg_rect = self.ready_msg.get_rect()
        ready_pos = screen.get_width() // 2, int(screen.get_height() * 0.65)
        self.ready_msg_rect.centerx, self.ready_msg_rect.centery = ready_pos
        self.level_msg = None
        self.level_msg_rect = None
        self.transition_time = transition_time     # total time to wait until the transition ends
        self.transition_begin = None
        self.transition_show = False

    def prep_level_msg(self):
        """Prepare a message for the current level number"""
        text = 'level ' + str(self.score_controller.level)
        self.level_msg = self.font.render(text, True, ScoreBoard.SCORE_WHITE)
        self.level_msg_rect = self.level_msg.get_rect()
        level_pos = self.screen.get_width() // 2, self.screen.get_height() // 2
        self.level_msg_rect.centerx, self.level_msg_rect.centery = level_pos

    def set_show_transition(self):
        """Begin the sequence for displaying the transition"""
        self.prep_level_msg()
        self.transition_begin = pygame.time.get_ticks()
        self.transition_show = True
        self.sound.play('transition')

    def draw(self):
        """Display the level transition to the screen"""
        if abs(self.transition_begin - pygame.time.get_ticks()) > self.transition_time:
            self.transition_show = False
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.level_msg, self.level_msg_rect)
            if abs(self.transition_begin - pygame.time.get_ticks()) >= self.transition_time // 2:
                self.screen.blit(self.ready_msg, self.ready_msg_rect)


class ScoreBoard:
    """Represents the score display for the screen"""

    SCORE_WHITE = (255, 255, 255)

    def __init__(self, screen, pos=(0, 0)):
        self.screen = screen
        self.score = 0
        self.color = ScoreBoard.SCORE_WHITE
        self.font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 36)
        self.image = None
        self.rect = None
        self.prep_image()
        self.pos = pos
        self.position()

    def position(self):
        """Re-position the scoreboard based on its pos value"""
        self.rect.centerx, self.rect.centery = self.pos

    def prep_image(self):
        """Render the score to a font image"""
        score_str = str(self.score)
        self.image = self.font.render(score_str, True, self.color)
        self.rect = self.image.get_rect()

    def update(self, n_score):
        """Increment the scoreboard and prepare a new image"""
        self.score += n_score
        self.prep_image()
        self.position()

    def reset(self):
        """Reset the scoreboard"""
        self.score = 0
        self.prep_image()
        self.position()

    def blit(self):
        """Blit the score to the screen"""
        self.screen.blit(self.image, self.rect)


class ItemCounter:
    """Displays a count of the number of a given item image to the screen"""
    def __init__(self, screen, image_name, pos=(0, 0)):
        self.screen = screen
        self.counter = 0
        self.item_image = pygame.image.load('images/' + image_name)
        self.item_rect = self.item_image.get_rect()
        self.font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 36)
        self.color = ScoreBoard.SCORE_WHITE
        self.text_image = None
        self.text_rect = None
        self.pos = pos
        self.prep_image()

    def add_items(self, n_items):
        """Increment the item counter by the given number of items"""
        self.counter += n_items
        self.prep_image()

    def reset_items(self):
        """Reset the item counter back to 0"""
        self.counter = 0
        self.prep_image()

    def prep_image(self):
        """Render the counter's image for future display"""
        text = str(self.counter) + ' X '
        self.text_image = self.font.render(text, True, self.color)
        self.text_rect = self.text_image.get_rect()
        self.position()

    def position(self):
        """Resets the position of the item counter to its stored position"""
        self.text_rect.centerx, self.text_rect.centery = self.pos
        x_offset = int(self.text_rect.width * 1.25)
        self.item_rect.centerx, self.item_rect.centery = self.pos[0] + x_offset, self.pos[1]

    def blit(self):
        """Blit the counter to the screen"""
        self.screen.blit(self.text_image, self.text_rect)
        self.screen.blit(self.item_image, self.item_rect)


class ScoreController:
    """Handles scoring and representation of scores"""
    def __init__(self, screen, items_image, sb_pos=(0, 0), itc_pos=(0, 0)):
        self.score = 0
        self.level = 1
        self.high_scores = []
        self.scoreboard = ScoreBoard(screen=screen, pos=sb_pos)
        self.item_counter = ItemCounter(screen=screen, pos=itc_pos, image_name=items_image)
        self.init_high_scores()

    def increment_level(self, up=1):
        """Add a number to the level"""
        self.level += up

    def reset_level(self):
        """Reset level back to its base value"""
        self.level = 1
        self.scoreboard.reset()
        self.item_counter.reset_items()

    def add_score(self, score, items=None):
        """Add new score and prepare for scoreboard display"""
        self.scoreboard.update(score)
        self.score = self.scoreboard.score
        if items:
            self.item_counter.add_items(items)

    def blit(self):
        """Blit all score related displays to the screen"""
        self.scoreboard.blit()
        self.item_counter.blit()

    def init_high_scores(self):
        """Read saved high scores from local storage"""
        try:
            with open('score_data.json', 'r') as file:
                self.high_scores = json.load(file)
                self.high_scores.sort(reverse=True)
        except (FileNotFoundError, ValueError, EOFError, json.JSONDecodeError) as e:
            print(e)
            self.high_scores = [0, 0, 0, 0, 0]

    def save_high_scores(self):
        """Save high scores to the disk"""
        for i in range(len(self.high_scores)):
            if self.score >= self.high_scores[i]:
                self.high_scores[i] = self.score
                break
        with open('score_data.json', 'w') as file:
            json.dump(self.high_scores, file)
