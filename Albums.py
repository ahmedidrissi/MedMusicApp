from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.properties import StringProperty, ObjectProperty


class AlbumsScreen(MDScreen):
    recycle_view = ObjectProperty(None)
    items_box = ObjectProperty(None)

    def on_enter(self):
        pass

    def on_leave(self):
        self.recycle_view.data = []

class Album(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()
    album_image = StringProperty()
    songs_number = StringProperty()
    