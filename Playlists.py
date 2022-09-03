from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.properties import StringProperty, ObjectProperty

class PlaylistsScreen(MDScreen):
    recycle_view = ObjectProperty(None)
    items_box = ObjectProperty(None)

    def on_enter(self):
        pass

    def on_leave(self):
        self.recycle_view.data = []

class Playlist(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()
    playlist_image = StringProperty()
    songs_number = StringProperty()

class Add_Playlist_Dialog(MDBoxLayout):
    pass

class Rename_Playlist_Dialog(MDBoxLayout):
    pass