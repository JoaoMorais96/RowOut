from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
import random
from functools import partial
from pipe import Pipe

class Background(Widget):
    sky_texture = ObjectProperty(None)
    cloud_texture = ObjectProperty(None)
    floor_texture = ObjectProperty(None)
    top_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create textures
        self.sky_texture = Image(source="sky.png").texture
        self.sky_texture.wrap = 'repeat'
        self.sky_texture.uvsize = (Window.width / self.sky_texture.width, -1)

        # Create textures
        self.cloud_texture = Image(source="cloud.png").texture
        self.cloud_texture.wrap = 'repeat'
        self.cloud_texture.uvsize = (Window.width / self.cloud_texture.width, -1)

        self.floor_texture = Image(source="floor.png").texture
        self.floor_texture.wrap = 'repeat'
        self.floor_texture.uvsize = (Window.width / self.floor_texture.width, -1)

        self.top_texture = Image(source="floor.png").texture
        self.top_texture.wrap = 'repeat'
        self.top_texture.uvsize = (Window.width / self.top_texture.width, -1)

    def on_size(self, *args):
        self.cloud_texture.uvsize = (self.width / self.cloud_texture.width, -1)
        self.floor_texture.uvsize = (self.width / self.floor_texture.width, -1)
        self.top_texture.uvsize = (self.width / self.top_texture.width, -1)

    def scroll_textures(self, time_passed):
        # Update the uvpos of the texture
        self.cloud_texture.uvpos = ( (self.cloud_texture.uvpos[0] + time_passed/2.0)%Window.width , self.cloud_texture.uvpos[1])
        self.floor_texture.uvpos = ( (self.floor_texture.uvpos[0] + time_passed)%Window.width, self.floor_texture.uvpos[1])
        self.top_texture.uvpos = ( (self.top_texture.uvpos[0] + time_passed)%Window.width, self.top_texture.uvpos[1])

        # Redraw the texture
        texture = self.property('cloud_texture')
        texture.dispatch(self)

        texture = self.property('floor_texture')
        texture.dispatch(self)

        texture = self.property('top_texture')
        texture.dispatch(self)

from random import randint
from kivy.properties import NumericProperty

class Bird(Image):
    velocity = NumericProperty(0)
    sea_direction = 'Down'

    def on_touch_down(self, touch):
        self.source = "bird2.png"
        if self.sea_direction == 'Down':
            self.velocity = 150 #defines the amount of jump
        elif self.sea_direction == 'Up':
            self.velocity = -150 #defines the amount of jump
        super().on_touch_down(touch)

    
    def on_touch_up(self, touch):
        self.source = "bird1.png"
        super().on_touch_up(touch)



class MainApp(App):
    pipes = []
    was_colliding = False

    def move_bird(self, time_passed):
        bird = self.root.ids.bird
        bird.y = bird.y + bird.velocity * time_passed
        bird.velocity = bird.velocity - self.GRAVITY * time_passed
        self.check_collision()

    def check_collision(self):
        bird = self.root.ids.bird
        # Go through each pipe and check if it collides
        is_colliding = False
        for pipe in self.pipes:
            if pipe.collide_widget(bird):
                is_colliding = True
                # Check if bird is between the gap
                if bird.y < (pipe.pipe_center - pipe.GAP_SIZE/1.7):
                    self.game_over()
                if bird.top > (pipe.pipe_center + pipe.GAP_SIZE/1.7):
                    self.game_over()
        if bird.y < 96:
            self.game_over()
        if bird.top > Window.height:
            self.game_over()

        if self.was_colliding and not is_colliding:
            self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
        self.was_colliding = is_colliding

    def game_over(self):
        self.root.ids.bird.pos = (20, (self.root.height - 96) / 2.0)
        for pipe in self.pipes:
            self.root.remove_widget(pipe)
        self.frames.cancel()
        self.root.ids.start_button.disabled = False
        self.root.ids.start_button.opacity = 1


    def next_frame(self, time_passed):
        self.move_bird(time_passed)
        self.move_pipes(time_passed)
        self.root.ids.background.scroll_textures(time_passed)
        

        self.change_tides()

    #Random change of tide direction
    def change_tides(self):
        num = random.randrange(1, 3002, 1)

        if(num>3000):
            if self.sea_direction == 'Up':
                self.root.ids.background.sky_texture = Image(source="sky.png").texture
                Clock.schedule_once(self.inact_change_down, 2)

            elif self.sea_direction == 'Down':
                self.root.ids.background.sky_texture = Image(source="sky2.png").texture
                Clock.schedule_once(self.inact_change_up, 2)

    #Actutally changes the tide direction 2 minutes after the background change
    def inact_change_down(self, dt):
                self.sea_direction = 'Down'
                self.root.ids.bird.sea_direction= 'Down'
                self.GRAVITY = 300 
    def inact_change_up(self, dt):
                self.sea_direction = 'Up'
                self.root.ids.bird.sea_direction= 'Up'
                self.GRAVITY = -300 


    def start_game(self):
        self.root.ids.background.sky_texture = Image(source="sky.png").texture
        self.GRAVITY = 300
        self.sea_direction = 'Down'
        self.root.ids.bird.sea_direction= 'Down'
        self.root.ids.bird.velocity= 0
        self.root.ids.score.text = "0"
        self.was_colliding = False
        self.pipes = []
        #Clock.schedule_interval(self.move_bird, 1/60.)
        self.frames = Clock.schedule_interval(self.next_frame, 1/60.)

        

        # Create the pipes
        num_pipes = 5
        distance_between_pipes = Window.width / (num_pipes - 1)
        for i in range(num_pipes):
            pipe = Pipe()
            pipe.pipe_center = randint(96 + 100, self.root.height - 100)
            pipe.size_hint = (None, None)
            pipe.pos = (Window.width + i*distance_between_pipes, 96)
            pipe.size = (64, self.root.height - 96)

            self.pipes.append(pipe)
            self.root.add_widget(pipe)

        # Move the pipes
        #Clock.schedule_interval(self.move_pipes, 1/60.)

    def move_pipes(self, time_passed):
        # Move pipes
        for pipe in self.pipes:
            pipe.x -= time_passed * 100

        # Check if we need to reposition the pipe at the right side
        num_pipes = 5
        distance_between_pipes = Window.width / (num_pipes - 1)
        pipe_xs = list(map(lambda pipe: pipe.x, self.pipes))
        right_most_x = max(pipe_xs)
        if right_most_x <= Window.width - distance_between_pipes:
            most_left_pipe = self.pipes[pipe_xs.index(min(pipe_xs))]
            most_left_pipe.x = Window.width











MainApp().run()
