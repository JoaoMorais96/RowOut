from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
import random
from functools import partial
from pipe import Pipe
from kivy.config import Config
from kivy.utils import platform

class Background(Widget):
    sky_texture = ObjectProperty(None)
    cloud_texture = ObjectProperty(None)
    floor_texture = ObjectProperty(None)
    top_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_zipped_png_files_left = Image(
            source = 'to_left_frames.zip', 
            anim_delay = 0,
            allow_stretch = True, 
            keep_ratio = False,
            keep_data = True)
        load_zipped_png_files_right = Image(
            source = 'to_right_frames.zip', 
            anim_delay = 0,
            allow_stretch = True, 
            keep_ratio = False,
            keep_data = True)
        # Create textures
        self.sky_texture = Image(source="transparent.png").texture


        # Create textures
        self.cloud_texture = Image(source="cloud.png").texture
        self.cloud_texture.wrap = 'repeat'
        self.cloud_texture.uvsize = (Window.width / self.cloud_texture.width, -1)

    def on_size(self, *args):
        self.cloud_texture.uvsize = (self.width / self.cloud_texture.width, -1)

    def scroll_textures(self, time_passed):
        # Update the uvpos of the texture
        self.cloud_texture.uvpos = ( (self.cloud_texture.uvpos[0] + time_passed/2.0)%Window.width , self.cloud_texture.uvpos[1])

        # Redraw the texture
        texture = self.property('cloud_texture')
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
    def build(self):
        self.wall_thickness = 0
        if(platform == 'android' or platform == 'ios'):
            Window.maximize()
        else:
            Window.size = (620, 1024)
            
    def move_bird(self, time_passed):
        bird = self.root.ids.bird
        bird.x = bird.x + bird.velocity * time_passed
        bird.velocity = bird.velocity - self.GRAVITY * time_passed
        self.check_collision()

    def check_collision(self):
        bird = self.root.ids.bird

        # Go through each pipe and check if it collides
        is_colliding = False
        for pipe in self.pipes:

            if  bird.y>=pipe.y-32 and bird.y<=pipe.y+32:

                is_colliding = True
                # Check if bird is between the gap
                if bird.x < (pipe.pipe_center - pipe.GAP_SIZE/2.0):
                    self.game_over()
                if bird.x > (pipe.pipe_center + pipe.GAP_SIZE/2.0):
                    self.game_over()
        if bird.x < self.wall_thickness:
            self.game_over()
        if bird.x > Window.width-self.wall_thickness:
            self.game_over()

        if self.was_colliding and not is_colliding:
            self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
        self.was_colliding = is_colliding

    def game_over(self):
        self.root.ids.bird.pos = ((self.root.width-50)/2.0, (self.root.height - self.wall_thickness) / 2.0)
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
                self.root.ids.gif.source = "to_left_frames.zip"
                Clock.schedule_once(self.inact_change_down, 2)

            elif self.sea_direction == 'Down':
                self.root.ids.gif.source = source="to_right_frames.zip"
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
        self.root.ids.gif.source = "to_left_frames.zip"
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
        distance_between_pipes = Window.height / (num_pipes - 1)
        for i in range(num_pipes):
            pipe = Pipe(self.root.width)
            const_spacing = self.wall_thickness
            pipe.pipe_center = randint(const_spacing+100, self.root.width - 100-self.wall_thickness)
            #pipe.pipe_center = randint( self.root.width,0)
            pipe.size_hint = (None, None)
            pipe.pos = (self.wall_thickness, Window.height + i*distance_between_pipes)#AQUI
            pipe.size = (64, self.root.width - (const_spacing))#AQUI


            self.pipes.append(pipe)
            self.root.add_widget(pipe)

    def move_pipes(self, time_passed):
        # Move pipes
        for pipe in self.pipes:
            pipe.y -= time_passed * 100

        # Check if we need to reposition the pipe at the right side
        num_pipes = 5
        distance_between_pipes = Window.height / (num_pipes - 1)
        pipe_ys = list(map(lambda pipe: pipe.y, self.pipes))
        right_most_y = min(pipe_ys)
        if right_most_y <= 0:

            most_down_pipe = self.pipes[pipe_ys.index(min(pipe_ys))]
            self.pipes.remove(most_down_pipe)
            self.root.remove_widget(most_down_pipe)

            pipe = Pipe(self.root.width)
            const_spacing = self.wall_thickness
            pipe.pipe_center = randint(const_spacing+100, self.root.width - 100-self.wall_thickness)

            pipe.size_hint = (None, None)
            pipe.pos = (self.wall_thickness, Window.height + distance_between_pipes)#AQUI
            pipe.size = (64, self.root.width - (const_spacing))#AQUI
            self.pipes.append(pipe)
            self.root.add_widget(pipe)

MainApp().run()
