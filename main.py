#--------------------------------------------------------------------------------
# Bug in kivymd.uix.dialog.dialog.MDDialog class
#--------------------------------------------------------------------------------
import os
import shutil
import glob
from PIL import Image
import time
import mutagen
from mutagen.wave import WAVE
from mutagen.mp3 import MP3
import webbrowser

#from android.storage import primary_external_storage_path
#primary_ext_storage = primary_external_storage_path()
#from android.permissions import request_permissions, Permission
#request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

from kivy import utils
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
#from kivy.animation import Animation
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineAvatarListItem, TwoLineAvatarListItem, OneLineAvatarIconListItem
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.filemanager import MDFileManager

from pygame import mixer
mixer.init()
from pytube import YouTube    
from kivymd.toast import toast
from kivy.config import Config
from kivy.core.window import Window

from kivy.storage.jsonstore import JsonStore

colors = {
    "Purple": {
        "50": "efe5fd",
        "100": "d5bff9",
        "200": "b894f6",
        "300": "9a66f4",
        "400": "803ff2",
        "500": "6300ee",
        "600": "5600e8",
        "700": "4100e0",
        "800": "2300db",
        "900": "0000d6",
        "A100": "B00020",
        "A200": "FFFFFF",
        "A400": "000000",
        "A700": "121212",
    },
    "Teal": {
        "50": "d4f6f2",
        "100": "92e9dc",
        "200": "03dac4",
        "300": "00c7ab",
        "400": "00b798",
        "500": "00a885",
        "600": "009a77",
        "700": "008966",
        "800": "007957",
        "900": "005b39",
        "A100": "bdedf0",
        "A200": "97e2e8",
        "A400": "6dcbd6",
        "A700": "5b9ca3",
    },
    "Red": {
        "50": "FFEBEE",
        "100": "FFCDD2",
        "200": "EF9A9A",
        "300": "E57373",
        "400": "EF5350",
        "500": "F44336",
        "600": "E53935",
        "700": "D32F2F",
        "800": "C62828",
        "900": "B71C1C",
        "A100": "FF8A80",
        "A200": "FF5252",
        "A400": "FF1744",
        "A700": "D50000",
    },
    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "F5F5F5",
        "Background": "FAFAFA",
        "CardsDialogs": "FFFFFF",
        "FlatButtonDown": "cccccc",
    },
    "Dark": {
        "StatusBar": "000000",
        "AppBar": "212121",
        "Background": "121212",
        "CardsDialogs": "424242",
        "FlatButtonDown": "999999",
    }
}

class Item(OneLineAvatarListItem):
    divider = None
    source = StringProperty()

class ItemConfirm(OneLineAvatarIconListItem):
    divider = None
    path = StringProperty()

class MedMusic(MDApp):

#--------------------------------- GENERAL FUNCTIONS ----------------------------------
    bg_color = ListProperty() 
    text_color = ListProperty()
    toolbar_title = StringProperty() 
    image = StringProperty() 
    snackbar_text = ''
    message_dialog = None
    first_screen = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Config.set('graphics', 'width', '330')
        Config.set('graphics', 'height', '630')
        Config.set('graphics', 'resizable', 0)
        Config.write()
        self.primary_ext_storage = "C:\\Users\\idris\\Desktop"
        Window.bind(on_keyboard=self.events)
        self.albums_manager_open = False
        self.images_manager_open = False
        self.albums_file_manager = MDFileManager(
            exit_manager=self.exit_albums_manager,
            select_path=self.add_album,
            preview=True,
        )
        self.images_file_manager = MDFileManager(
            exit_manager=self.exit_images_manager,
            select_path=self.choose_image,
            preview=True,
        )

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.albums_manager_open:
                self.albums_file_manager.back()
            if self.images_manager_open:
                self.images_file_manager.back()
        return True

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.theme_style = "Light" 
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.primary_hue = "500" 
        self.theme_cls.accent_hue = "200"
        self.bg_color = self.theme_cls.primary_color
        self.text_color = get_color_from_hex("#FAFAFA")

        return Builder.load_file("main.kv")

    def switch_theme(self):
        theme = self.theme_cls.theme_style
        if theme == 'Light':
            self.theme_cls.theme_style = 'Dark'
            self.theme_cls.primary_hue = "200"
            self.bg_color = get_color_from_hex("#212121")
            self.text_color = self.theme_cls.primary_color
        else:
            self.theme_cls.theme_style = 'Light'
            self.theme_cls.primary_hue = "500"
            self.bg_color = self.theme_cls.primary_color
            self.text_color = get_color_from_hex("#FAFAFA")

    def open_settings(self, button):
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
            "About us": "badge-account-horizontal-outline",
            "LinkedIn": "linkedin",
            "Facebook": "facebook",
            "Instagram": "instagram",
            "(+212)622406448": "whatsapp",
            
        }
        for item in data.items():
            bottom_sheet_menu.add_item(
                item[0],
                lambda x, y=item[0]: self.settings_callback(y),
                icon=item[1],
            )
        bottom_sheet_menu.sheet_list.ids.box_sheet_list.padding = 0
        bottom_sheet_menu.open()        

    def settings_callback(self, item):
        link = None
        if item == "About us":
            pass
        elif item == "LinkedIn":
            link = "https://www.linkedin.com/in/ahmed-idrissi-87508a249/"
        elif item == "Facebook":
            link = "https://www.facebook.com/Ahmed.Idrissi.2002/"
        elif item == "Instagram":
            link = "https://www.instagram.com/idrissi_ahmed02/"
        elif item == "WhatsApp":
            pass
        try:
            webbrowser.open(link)
        except Exception as e:
            print(str(e))

    def open_snackbar(self):
        Snackbar(text=self.snackbar_text, 
            snackbar_x="0dp",
            snackbar_y="0dp",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(22)).open()

    def open_images_file_manager(self):
        self.images_file_manager.show(self.primary_ext_storage)
        self.images_manager_open = True

    def choose_image(self, path):
        self.choosen_image = path
        Clock.schedule_once(self.change_image_callback, 1)
        self.exit_images_manager()

    def change_image_callback(self, *args):
        if self.first_screen == "PlaylistsScreen":
            json_file = JsonStore(f"Playlists/{self.current_playlist}.json")
            json_file.put("<image_key>", path=self.choosen_image, type="image")
            self.root.ids.playlists_box.clear_widgets()
            self.create_playlists(1)
        else:
            json_file = JsonStore(f"Albums/{self.current_playlist}.json")
            json_file.put("<image_key>", path=self.choosen_image, type="image")
            self.root.ids.albums_box.clear_widgets()
            self.create_albums(1)
        
    def exit_images_manager(self, *args):
        self.images_manager_open = False
        self.images_file_manager.close()

    def on_start(self):
        folders = os.listdir()
        if "Albums" not in folders:
            os.mkdir("Albums")
        if "Playlists" not in folders:
            os.mkdir("Playlists")
        if "Titles" not in folders:
            os.mkdir("Titles")
        if "Youtube" not in folders:
            os.mkdir("Youtube")
        Clock.schedule_once(self.create_playlists, 1)
        Clock.schedule_once(self.create_albums, 1)
        self.collect_titles()

    def back(self, screen):
        if screen == "PlaylistsScreen":
            self.root.ids.music_player.clear_widgets()
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"
            self.pause()

        elif screen == "SongsScreen":
            if self.first_screen == "PlaylistsScreen":
                self.toolbar_title = "Playlists"
                self.songs_number = "0"
                self.root.ids.screen_manager.current = "PlaylistsScreen"
                self.root.ids.screen_manager.transition.direction = "right"
                self.root.ids.songs_container.clear_widgets()
            else:
                self.toolbar_title = "Albums"
                self.songs_number = "0"
                self.root.ids.screen_manager.current = "AlbumsScreen"
                self.root.ids.screen_manager.transition.direction = "right"
                self.root.ids.songs_container.clear_widgets()

        elif screen == "AlbumsScreen":
            self.root.ids.music_player.clear_widgets()
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"
            self.pause()

        elif screen == "TitlesScreen":
            self.root.ids.music_player.clear_widgets()
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"
            self.root.ids.titles_box.clear_widgets()
            self.pause()

        elif screen == "ConverterScreen":
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"

#--------------------------------- ALBUMS FUNCTIONS ----------------------------------
    albums = []
    chosen_album = StringProperty("")
    album_songs = []

    def create_albums(self, *args):
        self.albums = os.listdir("Albums")
        for album_file in self.albums:
            json_file = JsonStore(f"Albums/{album_file}")
            self.root.ids.albums_box.add_widget(
                Album(
                    title = album_file[:-5],
                    album_image = json_file.get("<image_key>")["path"],
                )
            )

    def show_album_bottom_sheet(self, album):
        self.current_playlist = album
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
            "Play the album": "playlist-play",
            "Change the image": "image-edit-outline",
            "Remove the album": "trash-can-outline",
        }
        for item in data.items():
            bottom_sheet_menu.add_item(
                item[0],
                lambda x, y=item[0]: self.album_bottom_sheet_callback(y),
                icon=item[1],
            )
        bottom_sheet_menu.sheet_list.ids.box_sheet_list.padding = 0
        bottom_sheet_menu.open()

    def album_bottom_sheet_callback(self, item):
        if item == "Play the album":
            self.running_playlist = self.current_playlist
            self.running_songs = self.current_songs
            self.running_song = self.running_songs[0]
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            audio = MP3(self.running_song)
            self.song_length = audio.info.length 
            self.play()
        elif item == "Change the image":
            self.open_images_file_manager()
        elif item == "Remove the album":
            self.remove_album()

    def open_album(self, title):
        self.toolbar_title = ""
        self.current_playlist = title
        album_file = JsonStore(f"Albums/{title}.json")
        songs = album_file.find(type="song")
        self.current_songs = [song_tuple[1]["path"] for song_tuple in songs]
        self.songs_number = str(len(self.current_songs))
        self.image = album_file.get("<image_key>")["path"]
        self.snackbar_text = f"Opening {title} ..."
        self.open_snackbar()
        Clock.schedule_once(self.create_list_songs, 1)
        self.root.ids.screen_manager.current = "SongsScreen"
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.music_player.clear_widgets()
        self.show_music_player()

    def open_albums_file_manager(self):
        self.albums_file_manager.show(self.primary_ext_storage)
        self.albums_manager_open = True

    def add_album(self, path):
        self.chosen_album = path
        Clock.schedule_once(self.add_album_callback, 1)
        self.exit_albums_manager()
    
    def add_album_callback(self, *args):
        if os.path.isdir(self.chosen_album):
            self.album_songs = glob.glob(f"{self.chosen_album}/*.mp3") + glob.glob(f"{self.chosen_album}/*.wav")
            if self.album_songs!=[]:
                try:
                    album_title = self.chosen_album.split("\\")[-1]
                    album_file = JsonStore(f"Albums/{album_title}.json")
                    image = "Images\\default_image.jpg" 
                    album_file.put("<image_key>", path=image, type="image")  
                    for song in self.album_songs:
                        album_file.put(song.split("\\")[-1][:-4], path=song, type="song")
                    text = "Album added successfully"
                except Exception as e:
                    text = "Error"
                finally:
                    self.root.ids.albums_box.clear_widgets()
                    self.create_albums(1)
                    self.collect_titles()
                    self.snackbar_text = text
                    self.open_snackbar()
            else:
                self.snackbar_text = "No music is found"
                self.open_snackbar()
        else:
            self.snackbar_text = "Not a folder"
            self.open_snackbar()
    
    def exit_albums_manager(self, *args):
        self.albums_manager_open = False
        self.albums_file_manager.close()

    def remove_album(self):
        try:
            os.remove(f"Albums/{self.current_playlist}.json")
            text = "Album removed successfully"
        except:
            text = "Error"
        finally:
            self.root.ids.albums_box.clear_widgets()
            self.create_albums(1)
            self.collect_titles()
            self.snackbar_text = text
            self.open_snackbar()

#--------------------------------- PLAYLISTS FUNCTIONS ----------------------------------
    playlists = []
    current_playlist = StringProperty("")
    running_playlist = StringProperty("")
    add_playlist_dialog = None
    rename_playlist_dialog = None
    choosen_image = ""

    def create_playlists(self, *args):
        self.playlists = os.listdir("Playlists")    
        if self.playlists != []:
            self.running_playlist = self.playlists[0][:-5]
            playlist_file = JsonStore(f"Playlists/{self.running_playlist}.json")
            playlist_songs_tuples = playlist_file.find(type="song")
            self.running_songs = [song_tuple[1]["path"] for song_tuple in playlist_songs_tuples]
            for playlist_file in self.playlists:
                json_file = JsonStore(f"Playlists/{playlist_file}")
                self.root.ids.playlists_box.add_widget(
                    Playlist(
                        title = playlist_file[:-5],
                        playlist_image = json_file.get("<image_key>")["path"]
                    )
                )
        
    def show_playlist_bottom_sheet(self, playlist):
        self.current_playlist = playlist
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
            "Play the playlist": "playlist-play",
            "Add to the playlist": "playlist-plus",
            "Rename the playlist": "pencil-outline",
            "Change the image": "image-edit-outline",
            "Remove the playlist": "trash-can-outline",
        }
        for item in data.items():
            bottom_sheet_menu.add_item(
                item[0],
                lambda x, y=item[0]: self.playlist_bottom_sheet_callback(y),
                icon=item[1],
            )
        bottom_sheet_menu.sheet_list.ids.box_sheet_list.padding = 0
        bottom_sheet_menu.open()

    def playlist_bottom_sheet_callback(self, item):
        if item == "Play the playlist":
            self.running_playlist = self.current_playlist
            self.running_songs = self.current_songs
            self.running_song = self.running_songs[0]
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            audio = MP3(self.running_song)
            self.song_length = audio.info.length 
            self.play()
        elif item == "Add to the playlist":
            self.add_song()
        elif item == "Rename the playlist":
            self.rename_playlist()
        elif item == "Change the image":
            self.open_images_file_manager()
        elif item == "Remove the playlist":
            self.remove_playlist()

    def open_playlist(self, title):
        self.toolbar_title = ""
        self.current_playlist = title
        playlist_file = JsonStore(f"Playlists/{title}.json")
        songs = playlist_file.find(type="song")
        self.current_songs = [song_tuple[1]["path"] for song_tuple in songs]
        self.songs_number = str(len(self.current_songs))
        self.image = playlist_file.get("<image_key>")["path"]
        self.snackbar_text = f"Opening {title} ..."
        self.open_snackbar()
        Clock.schedule_once(self.create_list_songs, 1)
        self.root.ids.screen_manager.current = "SongsScreen"
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.music_player.clear_widgets()
        self.show_music_player()
      
    def add_playlist(self):
        if not self.add_playlist_dialog:
            self.add_playlist_dialog = MDDialog(
                title="Add playlist :",
                type="custom",
                content_cls=Add_Playlist_Dialog(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = lambda x : self.add_playlist_dialog.dismiss(force=True)
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.add_playlist_callback
                    ),
                ],
            )
        self.add_playlist_dialog.open()

    def add_playlist_callback(self, *args):
        title = self.add_playlist_dialog.content_cls.ids.playlist_name_input.text
        self.add_playlist_dialog.content_cls.ids.playlist_name_input.text = ''
        if len(title) <= 20:
            try:
                playlist_file = JsonStore(f"Playlists/{title}.json")
                image = "Images\\default_image.jpg" 
                playlist_file.put("<image_key>", path=image, type="image")
                text = "Playlist added successfully"
            except FileExistsError as e:
                text = "Playlist already existing"
            except OSError as e:
                text = "Invalid name"
            except Exception as e:
                text = "Error"
                print(str(e))
            finally:
                self.add_playlist_dialog.dismiss(force=True)
                self.root.ids.playlists_box.clear_widgets()
                self.create_playlists(1)
                self.snackbar_text = text
                self.open_snackbar()
        else:    
            self.snackbar_text = "The name is too long"
            self.open_snackbar()

    def remove_playlist(self):
        try:
            os.remove(f"Playlists/{self.current_playlist}.json")
            text = "Playlist removed successfully"
        except:
            text = "Error"
        finally:
            self.root.ids.playlists_box.clear_widgets()
            self.create_playlists(1)
            self.snackbar_text = text
            self.open_snackbar()

    def rename_playlist(self):
        if not self.rename_playlist_dialog:
            self.rename_playlist_dialog = MDDialog(
                title="Rename playlist :",
                type="custom",
                content_cls=Rename_Playlist_Dialog(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = lambda x : self.rename_playlist_dialog.dismiss(force=True)
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.rename_playlist_callback
                    ),
                ],
            )
        self.rename_playlist_dialog.open()

    def rename_playlist_callback(self, *args):
        new_title = self.rename_playlist_dialog.content_cls.ids.playlist_newname_input.text
        self.rename_playlist_dialog.content_cls.ids.playlist_newname_input.text = ''
        if len(new_title) <= 20:
            try:
                os.rename(
                    f"Playlists/{self.current_playlist}.json",
                    f"Playlists/{new_title}.json"
                    )
                self.current_playlist = new_title
                text = "Playlist renamed successfully"
            except:
                text = "Error"
            finally:
                self.rename_playlist_dialog.dismiss(force=True)
                self.root.ids.playlists_box.clear_widgets()
                self.create_playlists(1)
                self.snackbar_text = text
                self.open_snackbar()
        else:    
            self.snackbar_text = "The name is too long"
            self.open_snackbar()

#--------------------------------- SONGS FUNCTIONS ----------------------------------
    running_songs = []
    current_songs = []
    songs_number = StringProperty("0")
    running_song = StringProperty("")
    running_song_title = StringProperty("")
    current_song = StringProperty("")
    current_song_title = StringProperty("")
    song_length = 0
    
    expansed_music_player = BooleanProperty(False)
    progress_bar_value = ObjectProperty(0)
    left_time = StringProperty("00:00")
    right_time = StringProperty("00:00")
    current_time = 0
    
    play_pause_icon = StringProperty("play")
    repeat_icon = StringProperty("repeat-off")
    
    pause_pressed = False
    repeated = False
    
    add_songs_dialog = None
    choose_songs_dialog = None
    
    def create_list_songs(self, x):
        for title in self.current_songs:
            if os.path.isfile(title):
                self.root.ids.songs_container.add_widget(
                    Song(title=title)
                )

    def show_music_player(self):
        if self.running_songs !=[]:
            if self.running_song == '':
                self.running_song = self.running_songs[0]
                self.running_song_title = self.running_song.split("\\")[-1][:-4]
                audio = MP3(self.running_song)
                self.song_length = audio.info.length 
            self.root.ids.music_player.clear_widgets()
            self.root.ids.music_player.height = dp(67)
            self.root.ids.music_player.add_widget(
                MusicPlayer()
                )
            self.expansed_music_player = False
        else:
            albums = os.listdir("Albums")
            if albums == []:
                self.root.ids.music_player.add_widget(
                    MDLabel(text="No music found", bold=True, halign="center",
                        pos_hint= {"center_y": .5})
                    )
            else:
                album_file = JsonStore(f"Albums/{albums[0]}")
                self.running_playlist = albums[0][:-5]
                songs = album_file.find(type="song")
                self.running_songs = [song_tuple[1]["path"] for song_tuple in songs]
                self.running_song = self.running_songs[0]
                self.running_song_title = self.running_song.split("\\")[-1][:-4]
                audio = MP3(self.running_song)
                self.song_length = audio.info.length 
                self.root.ids.music_player.clear_widgets()
                self.root.ids.music_player.height = dp(67)
                self.root.ids.music_player.add_widget(
                    MusicPlayer()
                    )
                self.expansed_music_player = False

    def show_expansed_music_player(self):
        if self.running_songs != []:
            self.root.ids.music_player.clear_widgets()
            self.root.ids.music_player.height = dp(180)
            self.root.ids.music_player.add_widget(
                ExpansedMusicPlayer()
                )
            self.expansed_music_player = True
            self.update_right_time()
    
    def show_song_bottom_sheet(self, song):
        self.current_song = song
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
            "Play": "play",
            "Remove": "trash-can-outline",
        }
        for item in data.items():
            bottom_sheet_menu.add_item(
                item[0],
                lambda x, y=item[0]: self.song_bottom_sheet_callback(y),
                icon=item[1],
            )
        bottom_sheet_menu.sheet_list.ids.box_sheet_list.padding = 0
        bottom_sheet_menu.open()

    def song_bottom_sheet_callback(self, item):
        if item == 'Remove':
            if self.running_song == self.current_song:
                self.next()
            Clock.schedule_once(self.remove_song, 1)
        else:
            self.running_song = self.current_song
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            self.play()

    def add_song(self):
        if not self.add_songs_dialog:
            self.albums = os.listdir("Albums")
            self.add_songs_dialog = MDDialog(
                title="Add song :",
                type="simple",
                items=[
                    Item(
                        text = album_file[:-5],
                        source = list(x[1] for x in JsonStore(f"Albums/{album_file}").find(type="image"))[0]["path"],
                    ) for album_file in self.albums
                ],
            )
        self.add_songs_dialog.open()

    def choose_songs(self, album):
        self.add_songs_dialog.dismiss(force=True)
        self.add_songs_dialog = None
        if not self.choose_songs_dialog:
            album_file = JsonStore(f"Albums/{album}.json")
            playlist_file = JsonStore(f"Playlists/{self.current_playlist}.json")
            album_songs_generator = album_file.find(type="song")
            playlist_songs_generator = playlist_file.find(type="song")
            self.album_songs = [song_tuple[1]["path"] for song_tuple in album_songs_generator]
            self.current_songs = [song_tuple[1]["path"] for song_tuple in playlist_songs_generator]
            self.choose_songs_dialog = MDDialog(
                title="Choose songs :",
                type="confirmation",
                items=[
                    ItemConfirm(
                        text = title.split("\\")[-1],
                        path = title
                    ) for title in self.album_songs if title not in self.current_songs
                ],
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = lambda x : self.choose_songs_dialog.dismiss(force=True)
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release = self.add_songs_callback
                    ),
                ],
            )
        self.choose_songs_dialog.open()
    
    paths = []
    def checkbox_click(self, instance, active, title):
        if active == True:
            self.paths.append(title)
        else:
            self.paths.remove(title)

    def add_songs_callback(self, *args):
        self.current_songs += self.paths
        self.current_songs.sort()
        playlist_file = JsonStore(f"Playlists/{self.current_playlist}.json")
        for song in self.paths:
            playlist_file.put(song.split("\\")[-1][:-4], path=song, type="song")
        self.root.ids.songs_container.clear_widgets()
        self.songs_number = str(len(self.current_songs))
        self.create_list_songs(1)
        self.choose_songs_dialog.dismiss(force=True)
        self.choose_songs_dialog = None
        self.paths = []

    def remove_song(self, x):
        self.current_songs.remove(self.current_song)
        playlist_file = JsonStore(f"Playlists/{self.current_playlist}.json")
        playlist_file.delete(self.current_song.split("\\")[-1][:-4])
        self.songs_number = str(len(self.current_songs))
        self.root.ids.songs_container.clear_widgets()
        self.create_list_songs(1)

    def set_song(self, song):
        self.running_playlist = self.current_playlist
        self.running_songs = self.current_songs
        self.running_song = song
        self.running_song_title = self.running_song.split("\\")[-1][:-4]
        self.play()

    def update_progress_bar(self, x):
        if self.progress_bar_value < 100:
            self.progress_bar_value += 100/self.song_length
        else:
            self.next()

    def update_right_time(self):
        minutes = int(self.song_length/60)
        seconds = int(self.song_length%60)
        if (len(str(minutes)) == 1) and (len(str(seconds)) == 1):
            self.right_time = f"0{minutes}:0{seconds}"
        elif (len(str(minutes)) == 2) and (len(str(seconds)) == 1):
            self.right_time = f"{minutes}:0{seconds}"
        elif (len(str(minutes)) == 1) and (len(str(seconds)) == 2):
            self.right_time = f"0{minutes}:{seconds}"
        else:
            self.right_time = f"{minutes}:{seconds}"

    def update_left_time(self, x):
        self.current_time = self.current_time + 1
        minutes = int(self.current_time/60)
        seconds = int(self.current_time%60)
        if (len(str(minutes)) == 1) and (len(str(seconds)) == 1):
            self.left_time = f"0{minutes}:0{seconds}"
        elif (len(str(minutes)) == 2) and (len(str(seconds)) == 1):
            self.left_time = f"{minutes}:0{seconds}"
        elif (len(str(minutes)) == 1) and (len(str(seconds)) == 2):
            self.left_time = f"0{minutes}:{seconds}"
        else:
            self.left_time = f"{minutes}:{seconds}"

    def play(self):
        self.play_pause_icon = "pause"
        audio = MP3(self.running_song)
        self.song_length = audio.info.length
        self.progress_bar_value = 0
        self.current_time = 0
        self.update_right_time()
        Clock.unschedule(self.update_progress_bar)
        Clock.unschedule(self.update_left_time)
        mixer.music.load(self.running_song)
        mixer.music.play()
        Clock.schedule_interval(self.update_progress_bar, 1)
        Clock.schedule_interval(self.update_left_time, 1)
    
    def pause(self):
        self.play_pause_icon = "play"
        self.pause_pressed = True
        mixer.music.pause()
        Clock.unschedule(self.update_progress_bar)
        Clock.unschedule(self.update_left_time)

    def play_pause(self):
        if self.play_pause_icon == "play":
            self.play_pause_icon = "pause"
            if self.pause_pressed:
                mixer.music.unpause()
                Clock.schedule_interval(self.update_progress_bar, 1)
                Clock.schedule_interval(self.update_left_time, 1)
                self.pause_pressed = False
            else:
                self.play()       
        else:
            self.pause()
        
    def stop(self):
        mixer.music.stop()
        self.progress_bar_value = 0
        self.current_time = 0
        Clock.unschedule(self.update_progress_bar)
        Clock.unschedule(self.update_left_time)
        self.running_song = ''
        self.running_song_title = ''
        self.play_pause_icon = "play"

    def next(self):
        mixer.music.stop()
        self.play_pause_icon = "pause"
        if self.running_songs.index(self.running_song) < len(self.running_songs)-1:
            self.running_song = self.running_songs[self.running_songs.index(self.running_song)+1]
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            self.play()
        else:
            if self.repeat_icon == "repeat":
                self.running_song = self.running_songs[0]
                self.running_song_title = self.running_song.split("\\")[-1][:-4]
                self.play()

            elif self.repeat_icon == "repeat-once":
                if not self.repeated:
                    self.repeated = True
                    self.running_song = self.running_songs[0]
                    self.running_song_title = self.running_song.split("\\")[-1][:-4]
                    self.play()
                else:
                    self.play_pause_icon = "play"
                    Clock.unschedule(self.update_progress_bar)
                    Clock.unschedule(self.update_left_time)
                    self.repeated = False

            else:
                self.play_pause_icon = "play"
                Clock.unschedule(self.update_progress_bar)
                Clock.unschedule(self.update_left_time)

    def previous(self):
        mixer.music.stop()
        self.play_pause_icon = "pause"
        self.running_song = self.running_songs[max(self.running_songs.index(self.running_song)-1, 0)]
        self.running_song_title = self.running_song.split("\\")[-1][:-4]
        self.play()

    def repeat(self):
        if self.repeat_icon == "repeat-off":
            self.repeat_icon = "repeat"

        elif self.repeat_icon == "repeat":
            self.repeat_icon = "repeat-once"
            self.repeated = False

        elif self.repeat_icon == "repeat-once":
            self.repeat_icon = "repeat-off"

#--------------------------------- TITLES FUNCTIONS ----------------------------------
    all_songs = []
    titles = []

    def collect_titles(self):
        self.titles = os.listdir("Titles")
        self.albums = os.listdir("Albums")
        titles_file = JsonStore("Titles/Titles.json")
        self.all_songs = []
        for album_file in self.albums:
            json_file = JsonStore(f"Albums/{album_file}")
            self.all_songs += [song_tuple[1]["path"] for song_tuple in json_file.find(type="song")]
        for song in self.all_songs:
            titles_file.put(song.split("\\")[-1][:-4], path=song, type="song")

    def create_list_titles(self):
        Clock.schedule_once(self.create_list_titles_callback, 1)

    def create_list_titles_callback(self, *args):
        self.current_playlist = "Titles"
        self.current_songs = self.all_songs
        for title in self.all_songs:
            if os.path.isfile(title):
                self.root.ids.titles_box.add_widget(
                    Title(title=title)
                )
#--------------------------------- CONVERTER FUNCTIONS -------------------------------------
    link = ''
    yt = None
    ys = None
    convert_download_statue = StringProperty("Convert")
    download_statue = StringProperty("Download")

    def convert_download_music(self):
        if self.convert_download_statue == "Convert":
            self.convert_music()

        elif self.convert_download_statue == "Download":
            self.download_music()

    def convert_music(self):
        self.link = self.root.ids.link_input.text
        try:
            self.yt = YouTube(self.link)
            self.convert_download_statue = "Loading please wait..."
            Clock.schedule_once(self.convert_music_callback, 1)
        except:
            self.snackbar_text = 'Video url is unavaialable, try again.'
            self.open_snackbar()

    def convert_music_callback(self, x):
        self.ys = self.yt.streams.filter(only_audio=True).first()
        self.convert_download_statue = "Download"
        self.snackbar_text = 'Video converted successfully!'
        self.open_snackbar()

    def download_music(self):
        self.convert_download_statue = "Downloading..."
        Clock.schedule_once(self.download_music_callback, 8)

    def download_music_callback(self, x):
        try:
            json_file = JsonStore("Albums/youtube.json")
            out_file = self.ys.download("C:\\Users\\idris\\MedMusic\\Youtube")
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            json_file.put(new_file.split("\\")[-1][:-4], path=new_file, type="song")
            self.convert_download_statue = "Convert"
            self.snackbar_text = "Download complete!"
        except FileExistsError:
            self.convert_download_statue = "Convert"
            self.snackbar_text = "File already existing, try again."
            os.remove(out_file)
        except:
            self.snackbar_text = "Error"
        finally:
            self.open_snackbar()

class Playlist(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()
    playlist_image = StringProperty()

class Add_Playlist_Dialog(BoxLayout):
    pass
class Rename_Playlist_Dialog(BoxLayout):
    pass

class Song(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()

class Add_Song_Dialog(BoxLayout):
    pass

class SliverToolbar(MDTopAppBar):
    pass

class MusicPlayer(MDCard):
    pass

class ExpansedMusicPlayer(MDCard):
    pass

class Album(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()
    album_image = StringProperty()

class Title(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()

if __name__== '__main__':
    MedMusic().run()