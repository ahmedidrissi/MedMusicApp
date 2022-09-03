from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineAvatarListItem, OneLineAvatarIconListItem
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.properties import StringProperty, ObjectProperty


class SongsScreen(MDScreen):
    recycle_view = ObjectProperty(None)
    items_box = ObjectProperty(None)

    def on_enter(self):
        pass

    def on_leave(self):
        self.recycle_view.data = []
    
class Song(MDCard, RoundedRectangularElevationBehavior):
    pass

class Add_Song_Dialog(OneLineAvatarListItem):
    divider = None
    source = StringProperty()

class Choose_Song_Dialog(OneLineAvatarIconListItem):
    divider = None
    path = StringProperty()

class MusicPlayer(MDCard):
    pass

class ExpansedMusicPlayer(MDCard):
    pass
