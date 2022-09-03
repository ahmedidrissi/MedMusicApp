#-------------------------------------------------------------------------------------------
#------------------------------------- LIBRARIES -------------------------------------------
#-------------------------------------------------------------------------------------------

import os
import glob
import webbrowser
from pytube import YouTube  
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import Albums
import Playlists
import Songs
import Titles

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty

from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.filemanager import MDFileManager

#-------------------------------------------------------------------------------------------
#------------------------------------ MAIN CLASS -------------------------------------------
#-------------------------------------------------------------------------------------------

class MedMusic(MDApp):
    toolbar_title = StringProperty() # Toolbar title of the current screen (except HomeScreen)
    first_screen = StringProperty() # Last screen before opening the SongsScreen 
    image = StringProperty() # Image of the playlist\\album in the SongsScreen
    songs_number = StringProperty("0") # Songs number of the playlist\\album in the SongsScreen

    current_data = ListProperty() #Widgets to display in the current screen
    current_playlist = StringProperty() # Current playlist\\album to edit\\play
    running_playlist = StringProperty() # Running playlist\\album
    running_song_title = StringProperty() # Running song title

    expansed_music_player = BooleanProperty(False) # Opened or closed ?
    progress_bar_value = ObjectProperty(0) # Current value of the music player progress bar
    play_pause_icon = StringProperty("play") # Play\\Pause icon of the music player
    repeat_icon = StringProperty("repeat-off") # Repeat icon of the music player : off\\once\\many
    left_time = StringProperty("00:00") # Left time of the music player
    right_time = StringProperty("00:00") # Right time of the music player
#--------------------------------- GENERAL FUNCTIONS ---------------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        mixer.init() # Initialize the pygame mixer
        self.snackbar_text = '' # Message of the snackbar

        self.about_us_dialog = None # Popup screen of about
        self.phone_number_dialog = None # Popup screen of WhatsApp number
        self.add_playlist_dialog = None # Popup screen to add a playlist
        self.rename_playlist_dialog = None # Popup screen to rename a playlist
        self.add_songs_dialog = None # Popup screen to add songs, it shows the available albums
        self.choose_songs_dialog = None # Popup screen to choose songs to add

        self.chosen_album = "" # name of the choosen album to add in AlbumsScreen
        self.album_songs = [] # songs of the choosen album
        self.choosen_image = "" # path of the choosen image to replace a playlist\\album's image
        self.paths = [] # Paths of the songs to add in a playlist

        self.current_songs = [] # Songs of the current playlist\\album to edit\\play
        self.current_song = "" # Song to edit\\play
        self.current_song_title = "" # Current song title 
 
        self.running_songs = [] # Songs of the running playlist\\album 
        self.running_song = "" # Running song

        self.all_songs = [] # Songs from all available albums
        self.titles = [] # All songs titles
    
        self.current_time = 0 # Current time of the running song
        self.song_length = 1 # Running song length
    
        self.pause_pressed = False # Running song is paused ?
        self.repeated = False # Running songs are repated ?

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
    
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Light" 
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.primary_hue = "500" 
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.8
        return Builder.load_file("main.kv")
    
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

    def switch_theme(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
 
    def request_user_permissions(self):
        if platform == "android":
            # Request permissions
            self.open_albums_file_manager()
        else:
            self.open_albums_file_manager()

    def open_settings(self):
        bottom_sheet_menu = MDListBottomSheet()
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
        about_us = open("data/About_Us.txt", "r").read()
        if item == "About us":
            if not self.about_us_dialog:
                self.about_us_dialog = MDDialog(
                    title="About us :",
                    type="simple",
                    text=about_us,
                )
            self.about_us_dialog.open()
        elif item == "WhatsApp":
            if not self.phone_number_dialog:
                self.phone_number_dialog = MDDialog(
                    title="WhatsApp :",
                    type="simple",
                    text="(+212)622406448 \n",
                )
            self.phone_number_dialog.open()
        elif item == "GitHub":
            link = "https://github.com/ahmedidrissi/MedMusicApp"
        elif item == "LinkedIn":
            link = "https://www.linkedin.com/in/ahmed-idrissi-87508a249/"
        elif item == "Facebook":
            link = "https://www.facebook.com/Ahmed.Idrissi.2002/"
        elif item == "Instagram":
            link = "https://www.instagram.com/idrissi_ahmed02/"
        
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

#---------------------------------- ALBUMS FUNCTIONS ---------------------------------------
    def create_albums(self, *args):
        albums = os.listdir(self.current_working_dir + "\\Albums")
        self.current_data = []
        for album_file in albums:
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

#-------------------------------- PLAYLISTS FUNCTIONS --------------------------------------
    def create_playlists(self, *args):
        playlists = os.listdir(self.current_working_dir + "\\Playlists")   
        if playlists != []:
            self.running_playlist = playlists[0][:-5]
            playlist_file = JsonStore(self.current_working_dir + f"\\Playlists\\{self.running_playlist}.json")
            playlist_songs_tuples = playlist_file.find(type="song")
            self.running_songs = [song_tuple[1]["path"] for song_tuple in playlist_songs_tuples]
            self.current_data = []
            for playlist_file in playlists:
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
                content_cls=Playlists.Add_Playlist_Dialog(),
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
                content_cls=Playlists.Rename_Playlist_Dialog(),
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

#---------------------------------- SONGS FUNCTIONS ----------------------------------------
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
                Songs.MusicPlayer()
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
                    Songs.MusicPlayer()
                    )
                self.expansed_music_player = False

    def show_expansed_music_player(self):
        if self.running_songs != []:
            self.root.ids.music_player.clear_widgets()
            self.root.ids.music_player.height = dp(180)
            self.root.ids.music_player.add_widget(
                Songs.ExpansedMusicPlayer()
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
                    Songs.Add_Song_Dialog(
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
                    Songs.Choose_Song_Dialog(
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
            self.pause()
            self.running_playlist = self.current_playlist
            self.running_songs = self.current_songs
            self.running_song = song
            self.running_song_title = self.running_song.split("\\")[-1][:-4]
            Clock.schedule_once(self.play, 1)
        except Exception as e:
            self.snackbar_text = str(e)
            self.open_snackbar()

    def get_length(self):
        try:
            audio = MP3(self.running_song)
            self.song_length = audio.info.length
        except Exception:
            audio = WAVE(self.running_song)
            self.song_length = audio.info.length
        except:
            self.song_length = 0
            self.snackbar_text = "Error"
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
        minutes = int(self.song_length//60)
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
        minutes = int(self.current_time//60)
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
            mixer.music.load(self.running_song)
            self.get_length()
            mixer.music.play()
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
            mixer.music.pause()
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
            mixer.music.unpause()
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

#--------------------------------- TITLES FUNCTIONS ----------------------------------------

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

#-------------------------------- CONVERTER FUNCTIONS --------------------------------------
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

    def download_music_callback(self, *args):
        try:
            json_file = JsonStore(self.current_working_dir + "\\Albums\\youtube.json")
            out_file = self.ys.download(self.primary_ext_storage + "\\Download")
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

if __name__== '__main__':
    MedMusic().run()