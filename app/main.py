""" """

import flask
import requests
from typing import Callable, List

# Config
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

REMOTE = f"{config['CONNECTION']['REMOTE_HOST']}:{config['CONNECTION']['REMOTE_PORT']}"

# Kivy
from kivy.app import App

## Kivy uix
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown 
from kivy.uix.camera import Camera

## MapView
from kivy.garden.mapview import MapView
from kivy.garden.mapview import MapMarker

## Behaviors
from kivy.uix.behaviors import ButtonBehavior  

## Lang
from kivy.lang import Builder  


# Global Variables

markers = list()
food_types = list()

current_marker = {"food_type": None}

def get_markers() -> List[MapMarker]:
    """ Gathers Marker information from Remote host
        and converts them into MapMarker Objects.
        
        When pressed, these MapMarkers will show a 
        popup, containing the relevant information
        such as an image, and the type of food the
        marker is representing.
    """

    markers = requests.get(f"http://{REMOTE}/markers")
    if markers.text == '':
        return list()

    for enum, marker in enumerate(markers.text.split('\n')):
        marker_info = marker.split(',')
        marker = MapMarker(lat = marker_info[0], lon = marker_info[1])
        marker.on_press = Popup(
                                title=marker_info[2],
                                content=Image(source=marker_info[3])
                            )
        markers[enum] = marker
    
    return markers

def get_food_types() -> List[str]:
    food_types = requests.get(f"http://{REMOTE}/food_types")
    if food_types.text == '':
        return list()
    else:
        return food_types.text.split(',')

def post_marker():
        marker_info = {"lat": 10, "lon": 10, "food_type": "blueverrt"}
        requests.put(f"http://{REMOTE}/markers", json = marker_info)

class ImageButton(ButtonBehavior, Image):  
    pass

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)

        self.add_widget(Label(text="loading..."))
        markers = get_markers()
        food_types = get_food_types()
        print(food_types)
        screen_manager.current = "MapScreen"

class LocateScreenTakeImage(Screen):
    def __init__(self, **kwargs):
        super(LocateScreenTakeImage, self).__init__(**kwargs)
        
        # Camera
        layout_cam = AnchorLayout(
            anchor_x = "center",
            anchor_y = "top"
        )

        self.cam = Camera(play=False, index=0, resolution=(640,480))

        # Berry Button
        layout = AnchorLayout(
            anchor_x = "center",
            anchor_y = "bottom"
        )

        locate_button = ImageButton(
            source="save_marker.png",
            on_press = self.take_picture,
            size_hint = (0.3, 0.3)
        )

        layout.add_widget(locate_button)
        self.add_widget(layout)
        self.add_widget(self.cam)

    def take_picture(self, *args):
        
        img = self.cam.texture
        current_marker['image'] = img
        screen_manager.current = "LocateScreenChoseType"

class LocateScreenChoseType(Screen):
    def __init__(self, **kwargs):
        super(LocateScreenChoseType, self).__init__(**kwargs)
        print("----------------------")

        print(food_types)
        dropdown = DropDown()
        for food_type in food_types:
            btn = Button(text=food_type, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        dropdown.bind(on_select=lambda instance, x: self.choose_type(x))
        
        # Berry Button
        layout = AnchorLayout(
            anchor_x = "center",
            anchor_y = "bottom"
        )

        locate_button = ImageButton(
            source="save_marker.png",
            on_press = self.choose_type,
            size_hint = (0.3, 0.3)
        )

        layout.add_widget(locate_button)
        
        self.add_widget(layout)
        self.add_widget(dropdown)

    def choose_type(self, x, *args):
        current_marker['food_type'] = x
        post_marker()
        screen_manager.current = "MapScreen"

    

class MapScreen(Screen):

    def __init__(self, **kwargs):

        super(MapScreen, self).__init__(**kwargs)

        lat=50.6394
        lon=3.057
        zoom = 11

        # OpenStreetMap
        mapview = MapView(zoom=zoom, lat=lat, lon=lon)
        print(markers)
        for marker in markers:
            mapview.add_marker(marker)
        self.add_widget(mapview)

        # Berry Button
        layout = AnchorLayout(
            anchor_x = "center",
            anchor_y = "bottom"
        )

        locate_button = ImageButton(
            source="save_marker.png",
            on_press = lambda _: setattr(screen_manager, "current", "LocateScreenTakeImage"),
            size_hint = (0.3, 0.3)
        )

        layout.add_widget(locate_button)
        self.add_widget(layout)

# Screen Management

screen_manager = ScreenManager(
    transition=SlideTransition(direction="up")
)

screen_3 = LocateScreenChoseType(name="LocateScreenChoseType")
screen_manager.add_widget(screen_3)

screen_2 = LocateScreenTakeImage(name="LocateScreenTakeImage")
screen_manager.add_widget(screen_2)

screen_1 = MapScreen(name="MapScreen")
screen_manager.add_widget(screen_1)

screen_0 = LoadingScreen(name="LoadingScreen")
screen_manager.add_widget(screen_0)

class Forager(App):
    def build(self):
        return screen_manager

    

Forager().run()