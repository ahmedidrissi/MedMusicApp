#--------------------------------------------------------------------------------
# Bug in kivymd.uix.dialog.dialog.MDDialog class
#--------------------------------------------------------------------------------
import os
import glob
from mutagen.mp3 import MP3
import webbrowser

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty

from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import  Screen
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineAvatarListItem, OneLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.filemanager import MDFileManager

from pytube import YouTube    
from kivy.core.window import Window

from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader
from kivymd.uix.recycleview import MDRecycleView

about_us = '''Hey ! I'm IDRISSI Ahmed a student engineer at ENSIAS Rabat.\n
I made this app using Python and KivyMD. It allows you to add albums from your phone storage, \
create your own playlists, play music and convert YouTube music to mp3 format. \n
You can find the code source in my GitHub account. Enjoy it! \n'''

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

class TitlesScreen(MDScreen):
    recycle_view = ObjectProperty(None)
    items_box = ObjectProperty(None)

    def on_enter(self):
        pass

    def on_leave(self):
        self.recycle_view.data = []
        
class Title(MDCard, RoundedRectangularElevationBehavior):
    title = StringProperty()
    path = StringProperty()

class MusicPlayer(MDCard):
    pass

class ExpansedMusicPlayer(MDCard):
    pass

class MedMusic(MDApp):

#--------------------------------- GENERAL FUNCTIONS ----------------------------------
    toolbar_title = StringProperty() 
    image = StringProperty() 
    snackbar_text = ''
    about_us_dialog = None
    phone_number_dialog = None
    first_screen = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mplayer = MusicPlayerWindows()

        if platform == "win":
            self.primary_ext_storage = "C:\\Users\\idris\\Desktop"
            self.current_working_dir = os.getcwd()
        elif platform == "android":
            from android.storage import primary_external_storage_path
            self.primary_ext_storage = primary_external_storage_path()
            self.current_working_dir = self.primary_ext_storage + "/Android/data"
        else:
            self.primary_ext_storage = "\\"
            self.current_working_dir = os.getcwd()

        Window.bind(on_keyboard=self.events)

        self.albums_manager_open = False
        self.albums_file_manager = MDFileManager(
            exit_manager=self.exit_albums_manager,
            select_path=self.add_album,
            preview=True,
        )

        self.images_manager_open = False
        self.images_file_manager = MDFileManager(
            exit_manager=self.exit_images_manager,
            select_path=self.choose_image,
            preview=True,
        )

    def request_user_permissions(self):
        if platform == "android":
            self.open_albums_file_manager()
        else:
            self.open_albums_file_manager()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.albums_manager_open:
                self.albums_file_manager.back()
            elif self.images_manager_open:
                self.images_file_manager.back()
        if keyboard == 27:
            if self.root.ids.screen_manager.current == "HomeScreen":
                MDApp.get_running_app().stop()
                Window.close()
            else:
                if not self.images_manager_open and not self.albums_manager_open:
                    self.back(self.root.ids.screen_manager.current)
        return True

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Light" 
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.primary_hue = "500" 
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8
        return Builder.load_file("main.kv")

    def switch_theme(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def open_settings(self):
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
            "About us": "badge-account-horizontal-outline",
            "GitHub": "github",
            "LinkedIn": "linkedin",
            "Facebook": "facebook",
            "Instagram": "instagram",
            "WhatsApp": "whatsapp",
            
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
            if not self.about_us_dialog:
                self.about_us_dialog = MDDialog(
                    title="About us :",
                    type="simple",
                    text=about_us,
                )
            self.about_us_dialog.open()
        elif item == "GitHub":
            link = "https://github.com/ahmedidrissi/MedMusicApp"
        elif item == "LinkedIn":
            link = "https://www.linkedin.com/in/ahmed-idrissi-87508a249/"
        elif item == "Facebook":
            link = "https://www.facebook.com/Ahmed.Idrissi.2002/"
        elif item == "Instagram":
            link = "https://www.instagram.com/idrissi_ahmed02/"
        elif item == "WhatsApp":
            if not self.phone_number_dialog:
                self.phone_number_dialog = MDDialog(
                    title="WhatsApp :",
                    type="simple",
                    text="(+212)622406448 \n",
                )
            self.phone_number_dialog.open()
        try:
            webbrowser.open(link)
        except Exception as e:
            pass

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
        if self.root.ids.screen_manager.current == "PlaylistsScreen" or self.first_screen == "PlaylistsScreen":
            json_file = JsonStore(self.current_working_dir + f"\\Playlists\\{self.current_playlist}.json")
            json_file.put("<image_key>", path=self.choosen_image, type="image")
            self.create_playlists(1)
        elif self.root.ids.screen_manager.current == "AlbumsScreen" or self.first_screen == "AlbumsScreen":
            json_file = JsonStore(self.current_working_dir + f"\\Albums\\{self.current_playlist}.json")
            json_file.put("<image_key>", path=self.choosen_image, type="image")
            self.root.ids.albums_box.clear_widgets()
            self.create_albums(1)
        if self.root.ids.screen_manager.current == "SongsScreen":
            self.image = self.choosen_image
        
    def exit_images_manager(self, *args):
        self.images_manager_open = False
        self.images_file_manager.close()

    def on_start(self):
        folders = os.listdir(self.current_working_dir)
        if "com.medmusic" not in folders:
            os.mkdir(self.current_working_dir + "\\com.medmusic")

        self.current_working_dir += "\\com.medmusic"
        folders = os.listdir(self.current_working_dir)
        if "Albums" not in folders:
            os.mkdir(self.current_working_dir + "\\Albums")
        if "Playlists" not in folders:
            os.mkdir(self.current_working_dir + "\\Playlists")
        if "Titles" not in folders:
            os.mkdir(self.current_working_dir + "\\Titles")
        if "Youtube" not in folders:
            os.mkdir(self.current_working_dir + "\\Youtube")
            
        self.collect_titles()
     
    def on_pause(self):
        return True

    def back(self, screen):
        self.current_data = []
        if screen == "PlaylistsScreen":
            self.root.ids.music_player.clear_widgets()
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"
            self.pause()

        elif screen == "SongsScreen":
            if self.first_screen == "PlaylistsScreen":
                self.toolbar_title = "Playlists"
                self.songs_number = "0"
                Clock.schedule_once(self.create_playlists, 1)
                self.root.ids.screen_manager.current = "PlaylistsScreen"
                self.root.ids.screen_manager.transition.direction = "right"
            else:
                self.toolbar_title = "Albums"
                self.songs_number = "0"
                Clock.schedule_once(self.create_albums, 1)
                self.root.ids.screen_manager.current = "AlbumsScreen"
                self.root.ids.screen_manager.transition.direction = "right"

        elif screen == "AlbumsScreen":
            self.root.ids.music_player.clear_widgets()
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"
            self.pause()

        elif screen == "TitlesScreen":
            self.root.ids.music_player.clear_widgets()
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"
            self.pause()

        elif screen == "ConverterScreen":
            self.root.ids.screen_manager.current = "HomeScreen"
            self.root.ids.screen_manager.transition.direction = "right"

#--------------------------------- ALBUMS FUNCTIONS ----------------------------------
    albums = []
    chosen_album = StringProperty("")
    album_songs = []

    def create_albums(self, *args):
        self.albums = os.listdir(self.current_working_dir + "\\Albums")
        self.current_data = []
        for album_file in self.albums:
            json_file = JsonStore(self.current_working_dir + f"\\Albums\\{album_file}")
            self.current_data.append({
                'title': album_file[:-5],
                'album_image': json_file.get("<image_key>")["path"],
                'songs_number': json_file.get("<infos>")["songs_number"]
                })

    def show_album_bottom_sheet(self, album):
        self.current_playlist = album
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
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
        if item == "Change the image":
            self.open_images_file_manager()
        elif item == "Remove the album":
            self.remove_album()

    def open_album(self, title):
        self.toolbar_title = ""
        self.current_data = []
        self.current_playlist = title
        album_file = JsonStore(self.current_working_dir + f"\\Albums\\{title}.json")
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
            self.album_songs = glob.glob(f"{self.chosen_album}\\*.mp3") # + glob.glob(f"{self.chosen_album}\\*.wav")
            if self.album_songs!=[]:
                try:
                    album_title = self.chosen_album.split("\\")[-1]
                    album_file = JsonStore(self.current_working_dir + f"\\Albums\\{album_title}.json")
                    image = "data\\Images\\default_image.jpg" 
                    album_file.put("<image_key>", path=image, type="image", songs_number=len(self.album_songs))
                    album_file.put("<infos>", songs_number=str(len(self.album_songs)))
                    for song in self.album_songs:
                        album_file.put(song.split("\\")[-1][:-4], path=song, type="song")
                    text = "Album added successfully"
                except Exception as e:
                    text = str(e)
                    print(self.chosen_album)
                    print(text)
                finally:
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
            os.remove(self.current_working_dir + f"\\Albums\\{self.current_playlist}.json")
            text = "Album removed successfully"
        except:
            text = "Error"
        finally:
            if self.running_playlist == self.current_playlist:
                self.running_playlist = ""
                self.running_songs = []
                self.stop()
                self.root.ids.music_player.clear_widgets()
                self.show_music_player()
            self.back("SongsScreen")
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
        self.playlists = os.listdir(self.current_working_dir + "\\Playlists")   
        if self.playlists != []:
            self.running_playlist = self.playlists[0][:-5]
            playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{self.running_playlist}.json")
            playlist_songs_tuples = playlist_file.find(type="song")
            self.running_songs = [song_tuple[1]["path"] for song_tuple in playlist_songs_tuples]
            self.current_data = []
            for playlist_file in self.playlists:
                json_file = JsonStore(self.current_working_dir + f"\\Playlists\\{playlist_file}")
                self.current_data.append({
                    'title': playlist_file[:-5],
                    'playlist_image': json_file.get("<image_key>")["path"],
                    'songs_number': json_file.get("<infos>")["songs_number"]
                    })
        
    def show_playlist_bottom_sheet(self, playlist):
        self.current_playlist = playlist
        bottom_sheet_menu = MDListBottomSheet() #radius=10, radius_from="top_right"
        data = {
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
        if item == "Add to the playlist":
            self.add_song()
        elif item == "Rename the playlist":
            self.rename_playlist()
        elif item == "Change the image":
            self.open_images_file_manager()
        elif item == "Remove the playlist":
            self.remove_playlist()

    def open_playlist(self, title):
        self.toolbar_title = ""
        self.current_data = []
        self.current_playlist = title
        playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{title}.json")
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
                playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{title}.json")
                image = "data\\Images\\default_image.jpg" 
                playlist_file.put("<image_key>", path=image, type="image")
                playlist_file.put("<infos>", songs_number="0")
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
                self.create_playlists(1)
                self.snackbar_text = text
                self.open_snackbar()
        else:    
            self.snackbar_text = "The name is too long"
            self.open_snackbar()

    def remove_playlist(self):
        try:
            os.remove(self.current_working_dir + f"\\Playlists\\{self.current_playlist}.json")
            text = "Playlist removed successfully"
        except:
            text = "Error"
        finally:
            if self.running_playlist == self.current_playlist:
                self.running_playlist = ""
                self.running_songs = []
                self.stop()
                self.root.ids.music_player.clear_widgets()
                self.show_music_player()
            self.back("SongsScreen")
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
                    self.current_working_dir + f"\\Playlists\\{self.current_playlist}.json",
                    self.current_working_dir + f"\\Playlists\\{new_title}.json"
                    )
                self.current_playlist = new_title
                text = "Playlist renamed successfully"
            except:
                text = "Error"
            finally:
                self.rename_playlist_dialog.dismiss(force=True)
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
    
    current_data = ListProperty()

    def create_list_songs(self, *args):
        self.current_data = []
        for song in self.current_songs:
            if os.path.isfile(song):
                self.current_data.append({
                    'title': song.split("\\")[-1][:-4],
                    'path' : song
                    })

    def show_music_player(self):
        if self.running_songs !=[]:
            if self.running_song == '':
                self.running_song = self.running_songs[0]
                self.running_song_title = self.running_song.split("\\")[-1][:-4]  
            self.root.ids.music_player.clear_widgets()
            self.root.ids.music_player.height = dp(67)
            self.root.ids.music_player.add_widget(
                MusicPlayer()
                )
            self.expansed_music_player = False
        else:
            albums = os.listdir(self.current_working_dir + "\\Albums")
            if albums == []:
                self.root.ids.music_player.clear_widgets()
                self.root.ids.music_player.add_widget(
                    MDLabel(text="No music found", bold=True, halign="center",
                        pos_hint= {"center_y": .5})
                    )
            else:
                album_file = JsonStore(self.current_working_dir + f"\\Albums\\{albums[0]}")
                self.running_playlist = albums[0][:-5]
                songs = album_file.find(type="song")
                self.running_songs = [song_tuple[1]["path"] for song_tuple in songs]
                self.running_song = self.running_songs[0]
                self.running_song_title = self.running_song.split("\\")[-1][:-4]
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
            self.albums = os.listdir(self.current_working_dir + "\\Albums")
            self.add_songs_dialog = MDDialog(
                title="Add song :",
                type="simple",
                items=[
                    Add_Song_Dialog(
                        text = album_file[:-5],
                        source = list(x[1] for x in JsonStore(self.current_working_dir + f"\\Albums\\{album_file}").find(type="image"))[0]["path"],
                    ) for album_file in self.albums
                ],
            )
        self.add_songs_dialog.open()

    def choose_songs(self, album):
        self.add_songs_dialog.dismiss(force=True)
        self.add_songs_dialog = None
        if not self.choose_songs_dialog:
            album_file = JsonStore(self.current_working_dir + f"\\Albums\\{album}.json")
            playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{self.current_playlist}.json")
            album_songs_generator = album_file.find(type="song")
            playlist_songs_generator = playlist_file.find(type="song")
            self.album_songs = [song_tuple[1]["path"] for song_tuple in album_songs_generator]
            self.current_songs = [song_tuple[1]["path"] for song_tuple in playlist_songs_generator]
            self.choose_songs_dialog = MDDialog(
                title="Choose songs :",
                type="confirmation",
                items=[
                    Choose_Song_Dialog(
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
        playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{self.current_playlist}.json")
        for song in self.paths:
            playlist_file.put(song.split("\\")[-1][:-4], path=song, type="song")
        self.songs_number = str(len(self.current_songs))
        playlist_file.put("<infos>", songs_number=self.songs_number)
        self.create_list_songs(1)
        self.choose_songs_dialog.dismiss(force=True)
        self.choose_songs_dialog = None
        self.paths = []

    def remove_song(self, x):
        self.current_songs.remove(self.current_song)
        playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{self.current_playlist}.json")
        playlist_file.delete(self.current_song.split("\\")[-1][:-4])
        self.songs_number = str(len(self.current_songs))
        playlist_file.put("<infos>", songs_number=self.songs_number)
        self.create_list_songs(1)

    def set_song(self, song):
        try:
            self.mplayer.stop()
            self.mplayer.unload()
            self.running_playlist = self.current_playlist
            self.running_songs = self.current_songs
            self.running_song = song
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            Clock.schedule_once(self.play, 1)
        except Exception as e:
            self.snackbar_text = str(e)
            self.open_snackbar()

    def update_progress_bar(self, *args):
        if self.progress_bar_value < 100:
            try:
                self.progress_bar_value += 100/self.song_length
            except Exception as e:
                self.snackbar_text = str(e)
                self.open_snackbar()
                Clock.unschedule(self.update_progress_bar)
                Clock.unschedule(self.update_left_time)
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

    def update_left_time(self, *args):
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
    
    def play(self, *args):
        try:
            self.play_pause_icon = "pause"
            Clock.unschedule(self.update_progress_bar)
            Clock.unschedule(self.update_left_time)
            self.progress_bar_value = 0
            self.current_time = 0
            self.mplayer.load(self.running_song)
            self.song_length = self.mplayer.play()
            self.update_right_time()
            Clock.schedule_interval(self.update_progress_bar, 1)
            Clock.schedule_interval(self.update_left_time, 1)
        except Exception as e:
            self.snackbar_text = str(e)
            file = open(self.current_working_dir + "\\errors.txt", "a")
            file.write(str(e)+"\n")
            self.open_snackbar()
    
    def pause(self):
        try:
            self.play_pause_icon = "play"
            self.pause_pressed = True
            self.mplayer.stop()
        except Exception as e:
            self.snackbar_text = str(e)
            self.open_snackbar()
        finally:
            Clock.unschedule(self.update_progress_bar)
            Clock.unschedule(self.update_left_time)

    def unpause(self):
        try:
            self.pause_pressed = False
            self.play_pause_icon = "pause"
            self.mplayer.play()
            self.mplayer.seek(self.current_time)
            Clock.schedule_interval(self.update_progress_bar, 1)
            Clock.schedule_interval(self.update_left_time, 1)
        except Exception as e:
            self.snackbar_text = str(e)
            self.open_snackbar()

    def play_pause(self):
        if self.play_pause_icon == "play":
            if self.pause_pressed:
                self.unpause()
            else:
                Clock.schedule_once(self.play, 1)      
        else:
            self.pause()
        
    def stop(self):
        pass

    def next(self):
        self.pause()
        self.play_pause_icon = "pause"
        if self.running_songs.index(self.running_song) < len(self.running_songs)-1:
            self.running_song = self.running_songs[self.running_songs.index(self.running_song)+1]
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            Clock.schedule_once(self.play, 1)  
        else:
            if self.repeat_icon == "repeat":
                self.running_song = self.running_songs[0]
                self.running_song_title = self.running_song.split("\\")[-1][:-4]
                Clock.schedule_once(self.play, 1)  

            elif self.repeat_icon == "repeat-once":
                if not self.repeated:
                    self.repeated = True
                    self.running_song = self.running_songs[0]
                    self.running_song_title = self.running_song.split("\\")[-1][:-4]
                    Clock.schedule_once(self.play, 1)  
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
        self.pause()
        self.play_pause_icon = "pause"
        self.running_song = self.running_songs[max(self.running_songs.index(self.running_song)-1, 0)]
        self.running_song_title = self.running_song.split("\\")[-1][:-4]
        Clock.schedule_once(self.play, 1)  

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
        self.titles = os.listdir(self.current_working_dir + "\\Titles")
        self.albums = os.listdir(self.current_working_dir + "\\Albums")
        titles_file = JsonStore(self.current_working_dir + "\\Titles\\Titles.json")
        self.all_songs = []
        for album_file in self.albums:
            json_file = JsonStore(self.current_working_dir + f"\\Albums\\{album_file}")
            self.all_songs += [song_tuple[1]["path"] for song_tuple in json_file.find(type="song")]
        for song in self.all_songs:
            titles_file.put(song.split("\\")[-1][:-4], path=song, type="song")

    def create_list_titles(self):
        self.current_data = []
        self.snackbar_text = "Opening Titles ..."
        self.open_snackbar()
        Clock.schedule_once(self.create_list_titles_callback, 1)

    def create_list_titles_callback(self, *args):
        self.current_playlist = "Titles"
        self.current_songs = self.all_songs
        for song in self.current_songs:
            if os.path.isfile(song):
                self.current_data.append({
                    'title': song.split("\\")[-1][:-4],
                    'path' : song
                    })
#--------------------------------- CONVERTER FUNCTIONS -------------------------------------
    link = ''
    yt = None
    ys = None
    convert_download_statue = StringProperty("Convert")
    download_statue = StringProperty("Download")

    def convert_download_music(self):
        if self.convert_download_statue == "Convert":
            self.link = self.root.ids.link_input.text
            self.convert_download_statue = "Loading please wait..."
            self.convert_music()

        elif self.convert_download_statue == "Download":
            self.download_music()

    def convert_music(self):
        try:
            self.yt = YouTube(self.link)
            Clock.schedule_once(self.convert_music_callback, 2)
        except Exception as e:
            self.snackbar_text = str(e)
            self.open_snackbar()

    def convert_music_callback(self, *args):
        try:
            self.ys = self.yt.streams.filter(only_audio=True).first()
            self.convert_download_statue = "Download"
            self.snackbar_text = 'Video converted successfully!'
        except Exception as e:
            self.snackbar_text = str(e)
        finally:
            self.open_snackbar()

    def download_music(self):
        self.convert_download_statue = "Downloading..."
        Clock.schedule_once(self.download_music_callback, 8)

    def download_music_callback(self, x):
        try:
            json_file = JsonStore(self.current_working_dir + "\\Albums\\youtube.json")
            out_file = self.ys.download(self.primary_ext_storage)
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            songs = json_file.find(type="song")
            self.current_songs = [song_tuple[1]["path"] for song_tuple in songs]
            json_file.put(new_file.split("\\")[-1][:-4], path=new_file, type="song")
            json_file.put("<image_key>", path='data\\Images\\default_image.jpg', type="image")
            json_file.put("<infos>", songs_number=f"{len(self.current_songs) + 1}")
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
            self.collect_titles()

class MusicPlayerWindows(object):
    def __init__(self):
        self.secs = 0
        self.actualsong = ''
        self.length = 0
        self.sound_pos = 0
        self.isplaying = False
        self.sound = None

    def __del__(self):
        if self.sound:
            self.sound.unload()

    def load(self, filename):
        self.__init__()
        self.sound = SoundLoader.load(filename)    
        if self.sound:
            if self.sound.length != -1 :
                self.length = self.sound.length
                self.actualsong = filename
                return True
        return False

    def unload(self):
        if self.sound != None:
            self.sound.unload()
            self.__init__ # reset vars

    def play(self):
        if self.sound:
            self.sound.play()
            self.isplaying = True
            return self.length

    def stop(self):
        self.isplaying = False
        self.secs=0
        if self.sound:
            self.sound.stop()

    def seek(self, timepos_secs):
        self.sound.seek(timepos_secs)

if __name__== '__main__':
    MedMusic().run()