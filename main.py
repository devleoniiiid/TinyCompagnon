import tkinter as tk
from tkinter import ttk
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from PIL import Image, ImageTk
from datetime import datetime
import threading
from flask import Flask, render_template, request, jsonify
import io
import os
import sys
import time

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
current_screen = None

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=config['spotify']['client_id'],
        client_secret=config['spotify']['client_secret'],
        redirect_uri="http://localhost:8888/callback",
        scope="user-read-currently-playing",
        cache_path=".spotify_cache"
    ))
except Exception as e:
    logger.error(f"Erreur d'initialisation: {e}")
    sys.exit(1)

class TinyCompagnon:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.attributes('-fullscreen', True)
            self.current_frame = None
            self.default_screen = 'clock'
            
            if not os.path.exists('uploaded_photos'):
                os.makedirs('uploaded_photos')
                logger.info("Dossier uploaded_photos créé")
            
            self.setup_initial_screen()
            self.root.after(5000, self.show_default_screen)
            self.check_screen_changes()
            self.last_weather_update = 0
            self.weather_data = None
        except Exception as e:
            logger.error(f"Erreur dans l'initialisation de TinyCompagnon: {e}")
            sys.exit(1)

    def check_screen_changes(self):
        try:
            global current_screen
            if current_screen:
                logger.debug(f"Changement d'écran détecté: {current_screen}")
                if current_screen == 'spotify':
                    self.show_spotify_screen()
                elif current_screen == 'clock':
                    self.show_clock_screen()
                elif current_screen == 'photo':
                    self.show_photo_frame()
                elif current_screen == 'weather':
                    self.show_weather_screen()
                elif current_screen == 'news':
                    self.show_news_screen()
                current_screen = None
            self.root.after(100, self.check_screen_changes)
        except Exception as e:
            logger.error(f"Erreur dans check_screen_changes: {e}")

    def setup_initial_screen(self):
        try:
            self.initial_frame = tk.Frame(self.root, bg='black')
            self.initial_frame.pack(expand=True, fill='both')
            label = tk.Label(self.initial_frame, text="TinyCompagnon", font=("Arial", 48), bg='black', fg='white')
            label.pack(expand=True)
            self.current_frame = self.initial_frame
        except Exception as e:
            logger.error(f"Erreur dans setup_initial_screen: {e}")

    def show_spotify_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg='black', width=800, height=480)
        self.current_frame.pack(expand=True, fill='both')
        self.current_frame.pack_propagate(False)
        
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(1, weight=1)
        
        left_container = tk.Frame(self.current_frame, bg='black')
        left_container.grid(row=0, column=0, sticky='nsew', padx=(12, 0))
        
        cover_frame = tk.Frame(left_container, bg='black', width=375, height=375)
        cover_frame.pack(expand=True)
        cover_frame.pack_propagate(False)
        
        cover_label = tk.Label(cover_frame, bg='black')
        cover_label.place(relx=0.5, rely=0.5, anchor='center')
        
        right_main = tk.Frame(self.current_frame, bg='black', width=400, height=480)
        right_main.grid(row=0, column=1, sticky='nsew')
        
        no_playback_label = tk.Label(self.current_frame, 
                                   text="Aucune Lecture Active", 
                                   font=("Arial", 48, "bold"),
                                   fg='white',
                                   bg='black')
        
        def adjust_font_size(label, initial_size, text):
            font_size = initial_size
            label.config(text=text)
            while label.winfo_reqwidth() > 350 and font_size > 12:
                font_size -= 2
                label.config(font=("Arial", font_size, "bold" if initial_size > 24 else "normal"))
        
        text_container = tk.Frame(right_main, bg='black')
        text_container.place(relx=0.5, rely=0.5, anchor='center')
        
        song_label = tk.Label(text_container, font=("Arial", 32, "bold"), fg='white', bg='black', wraplength=350)
        song_label.pack(pady=8)
        
        artist_label = tk.Label(text_container, font=("Arial", 22), fg='#1DB954', bg='black', wraplength=350)
        artist_label.pack(pady=4)
        
        album_label = tk.Label(text_container, font=("Arial", 18), fg='#B3B3B3', bg='black', wraplength=350)
        album_label.pack(pady=4)
        
        progress_frame = tk.Frame(text_container, bg='black', width=350)
        progress_frame.pack(pady=15)
        
        style = ttk.Style()
        style.configure("Spotify.Horizontal.TProgressbar", 
                       thickness=8,
                       troughcolor='#404040',
                       background='#1DB954')
        
        progress_bar = ttk.Progressbar(progress_frame, 
                                     style="Spotify.Horizontal.TProgressbar",
                                     length=350,
                                     mode='determinate')
        progress_bar.pack()
        
        time_label = tk.Label(progress_frame, font=("Arial", 12), fg='#B3B3B3', bg='black')
        time_label.pack(pady=4)
        
        def update_spotify():
            try:
                if not self.current_frame.winfo_exists():
                    return
                    
                current_track = sp.current_user_playing_track()
                
                if current_track is None or not current_track['is_playing']:
                    if left_container.winfo_exists():
                        left_container.grid_remove()
                    if right_main.winfo_exists():
                        right_main.grid_remove()
                    if no_playback_label.winfo_exists():
                        no_playback_label.place(relx=0.5, rely=0.5, anchor='center')
                else:
                    if no_playback_label.winfo_exists():
                        no_playback_label.place_forget()
                    if left_container.winfo_exists():
                        left_container.grid()
                    if right_main.winfo_exists():
                        right_main.grid()
                    
                    img_url = current_track['item']['album']['images'][0]['url']
                    response = requests.get(img_url)
                    img_data = Image.open(io.BytesIO(response.content))
                    img_data = img_data.resize((375, 375), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img_data)
                    cover_label.configure(image=img_tk)
                    cover_label.image = img_tk
                    
                    adjust_font_size(song_label, 32, current_track['item']['name'])
                    adjust_font_size(artist_label, 22, current_track['item']['artists'][0]['name'])
                    adjust_font_size(album_label, 18, current_track['item']['album']['name'])
                    
                    progress = current_track['progress_ms'] / current_track['item']['duration_ms'] * 100
                    progress_bar['value'] = progress
                    
                    current_time = datetime.fromtimestamp(current_track['progress_ms']/1000).strftime('%M:%S')
                    total_time = datetime.fromtimestamp(current_track['item']['duration_ms']/1000).strftime('%M:%S')
                    time_label.config(text=f"{current_time} / {total_time}")
                    
            except Exception as e:
                logger.error(f"Erreur Spotify: {e}")
                return
            
            if self.current_frame.winfo_exists():
                self.root.after(1000, update_spotify)
        
        update_spotify()

    def show_clock_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg='black')
        self.current_frame.pack(expand=True, fill='both')
        
        time_label = tk.Label(self.current_frame, font=("Arial", 120, "bold"), fg='white', bg='black')
        time_label.pack(expand=True)
        
        def update_time():
            try:
                if time_label.winfo_exists():
                    current_time = datetime.now().strftime('%H:%M:%S')
                    time_label.config(text=current_time)
                    self.root.after(1000, update_time)
            except Exception as e:
                logger.error(f"Erreur dans update_time: {e}")
        
        update_time()

    def show_photo_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg='black')
        self.current_frame.pack(expand=True, fill='both')
        
        photo_label = tk.Label(self.current_frame, bg='black')
        photo_label.pack(expand=True, fill='both')
        
        def load_photo():
            try:
                photos = [f for f in os.listdir('uploaded_photos') if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                if photos:
                    latest_photo = max([os.path.join('uploaded_photos', f) for f in photos], key=os.path.getctime)
                    img = Image.open(latest_photo)
                    
                    screen_width = self.root.winfo_width()
                    screen_height = self.root.winfo_height()
                    
                    img_ratio = img.size[0] / img.size[1]
                    screen_ratio = screen_width / screen_height
                    
                    if screen_ratio > img_ratio:
                        new_height = screen_height
                        new_width = int(new_height * img_ratio)
                    else:
                        new_width = screen_width
                        new_height = int(new_width / img_ratio)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    photo_tk = ImageTk.PhotoImage(img)
                    photo_label.configure(image=photo_tk)
                    photo_label.image = photo_tk
            except Exception as e:
                logger.error(f"Erreur chargement photo: {e}")
            
            self.root.after(1000, load_photo)
        
        load_photo()

    def update_weather_data(self):
        try:
            meteoblue_config = config['meteoblue']
            api_key = meteoblue_config['METEOBLUE_API_KEY']
            lat = meteoblue_config['LAT']
            lon = meteoblue_config['LON']
            asl = meteoblue_config['ASL']
            
            url = "https://my.meteoblue.com/packages/basic-1h"
            params = {
                'apikey': api_key,
                'lat': lat,
                'lon': lon,
                'asl': asl,
                'format': 'json',
                'tz': 'Europe/Paris'
            }
            
            logger.info("Tentative d'appel API Meteoblue")
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Erreur API: {response.status_code}")
                logger.error(f"Réponse: {response.text}")
                return None
                
            self.weather_data = response.json()
            self.last_weather_update = time.time()
            
            current_temp = self.weather_data['data_1h']['temperature'][0]
            logger.info(f"Nouvelle température: {current_temp}°C")
            
            return self.weather_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour météo: {e}")
            logger.exception(e)
            return None

    def show_weather_screen(self):
        try:
            logger.info("Démarrage de show_weather_screen")
            
            if self.current_frame:
                self.current_frame.destroy()
                logger.info("Ancien frame détruit")
                
            self.current_frame = tk.Frame(self.root, bg='black', width=800, height=480)
            self.current_frame.pack(expand=True, fill='both')
            self.current_frame.pack_propagate(False)
            logger.info("Nouveau frame créé")
            
            self.current_frame.grid_columnconfigure(0, weight=1)
            self.current_frame.grid_columnconfigure(1, weight=1)
            
            left_frame = tk.Frame(self.current_frame, bg='black', width=400, height=480)
            left_frame.grid(row=0, column=0, sticky='nsew', padx=(40, 20))
            left_frame.pack_propagate(False)
            
            right_frame = tk.Frame(self.current_frame, bg='black', width=400, height=480)
            right_frame.grid(row=0, column=1, sticky='nsew', padx=20)
            right_frame.pack_propagate(False)
            logger.info("Frames gauche et droite créés")
            
            weather_icon_label = tk.Label(left_frame, bg='black')
            weather_icon_label.place(relx=0.5, rely=0.5, anchor='center')
            
            info_container = tk.Frame(right_frame, bg='black')
            info_container.place(relx=0.5, rely=0.5, anchor='center')
            
            date_label = tk.Label(info_container, font=("Arial", 36, "bold"), fg='white', bg='black')
            date_label.pack(pady=(0, 20))
            
            current_temp_label = tk.Label(info_container, font=("Arial", 72, "bold"), fg='white', bg='black')
            current_temp_label.pack(pady=10)
            
            minmax_temp_label = tk.Label(info_container, font=("Arial", 24), fg='#B3B3B3', bg='black')
            minmax_temp_label.pack(pady=10)
            
            forecast_label = tk.Label(info_container, font=("Arial", 36), fg='#1DB954', bg='black')
            forecast_label.pack(pady=10)
            logger.info("Labels créés")
            
            def get_weather_icon(code):
                weather_icons = {
                    1: "soleil.png",
                    2: "nuageux.png",
                    3: "nuage.png",
                    4: "nuage.png",
                    5: "brume.png",
                    6: "brume.png",
                    7: "pluvieux.png",
                    8: "pluie.png",
                    9: "pluie.png",
                    10: "neige.png",
                    11: "neige.png",
                    12: "neige.png",
                    13: "neige.png"
                }
                icon_name = weather_icons.get(code, "unknown.png")
                return os.path.join("static", "images", "Weather Icons", icon_name)
            
            def get_weather_description(code):
                weather_codes = {
                    1: "Ensoleillé",
                    2: "Partiellement nuageux",
                    3: "Très nuageux",
                    4: "Couvert",
                    5: "Brouillard",
                    6: "Brouillard givrant",
                    7: "Légère pluie",
                    8: "Pluie",
                    9: "Forte pluie",
                    10: "Pluie verglaçante",
                    11: "Légère neige",
                    12: "Neige",
                    13: "Forte neige"
                }
                return weather_codes.get(code, "Indéterminé")
            
            logger.info("Tentative de récupération des données météo")
            meteoblue_config = config['meteoblue']
            api_key = meteoblue_config['METEOBLUE_API_KEY']
            lat = meteoblue_config['LAT']
            lon = meteoblue_config['LON']
            asl = meteoblue_config['ASL']
            
            url = "https://my.meteoblue.com/packages/basic-1h"
            params = {
                'apikey': api_key,
                'lat': lat,
                'lon': lon,
                'asl': asl,
                'format': 'json',
                'tz': 'Europe/Paris'
            }
            
            logger.info("Envoi de la requête API")
            response = requests.get(url, params=params)
            logger.info(f"Réponse reçue: status {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Erreur API: {response.status_code}")
                logger.error(f"Réponse: {response.text}")
                raise Exception(f"Erreur API: {response.status_code}")
            
            weather_data = response.json()
            logger.info("Données météo reçues et parsées")
            
            current_temp = weather_data['data_1h']['temperature'][0]
            temp_min = min(weather_data['data_1h']['temperature'][:24])
            temp_max = max(weather_data['data_1h']['temperature'][:24])
            weather_code = weather_data['data_1h']['pictocode'][0]
            logger.info(f"Température actuelle: {current_temp}°C")
            
            current_temp_label.config(text=f"{current_temp:.1f}°C")
            minmax_temp_label.config(text=f"Min: {temp_min:.1f}°C  Max: {temp_max:.1f}°C")
            forecast_label.config(text=get_weather_description(weather_code))
            date_label.config(text=datetime.now().strftime('%H:%M'))
            logger.info("Labels mis à jour")
            
            icon_path = get_weather_icon(weather_code)
            if os.path.exists(icon_path):
                weather_icon = Image.open(icon_path)
                weather_icon = weather_icon.resize((300, 300), Image.Resampling.LANCZOS)
                weather_icon_tk = ImageTk.PhotoImage(weather_icon)
                weather_icon_label.configure(image=weather_icon_tk)
                weather_icon_label.image = weather_icon_tk
                logger.info("Icône météo chargée")
            else:
                logger.error(f"Icône non trouvée: {icon_path}")
            
        except Exception as e:
            logger.error(f"Erreur dans show_weather_screen: {e}")
            logger.exception(e)

    def show_news_screen(self):
        try:
            logger.info("Démarrage de show_news_screen")
            
            if self.current_frame:
                self.current_frame.destroy()
                
            self.current_frame = tk.Frame(self.root, bg='black', width=800, height=480)
            self.current_frame.pack(expand=True, fill='both')
            self.current_frame.pack_propagate(False)
            
            main_container = tk.Frame(self.current_frame, bg='black')
            main_container.pack(expand=True, fill='both', padx=20, pady=20)
            
            title_label = tk.Label(main_container, 
                                 text="Actualités", 
                                 font=("Arial", 36, "bold"), 
                                 fg='white', 
                                 bg='black')
            title_label.pack(pady=(0, 20))
            
            article_frame = tk.Frame(main_container, bg='black')
            article_frame.pack(expand=True, fill='both')
            
            title_label = tk.Label(article_frame, 
                                 text="",
                                 font=("Arial", 24, "bold"),
                                 fg='white',
                                 bg='black',
                                 wraplength=700,
                                 justify='left')
            title_label.pack(pady=(0, 20))
            
            desc_label = tk.Label(article_frame,
                                text="",
                                font=("Arial", 18),
                                fg='#B3B3B3',
                                bg='black',
                                wraplength=700,
                                justify='left')
            desc_label.pack(pady=10)
            
            def fetch_news():
                try:
                    url = "https://newsapi.org/v2/everything"
                    params = {
                        'apiKey': config['newsapi']['API_KEY'],
                        'q': 'actualités',
                        'language': 'fr',
                        'sortBy': 'publishedAt',
                        'pageSize': 10
                    }
                    
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        news_data = response.json()
                        return news_data.get('articles', [])
                    else:
                        logger.error(f"Erreur API: {response.status_code}")
                        return []
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des actualités: {e}")
                    return []
            
            def update_articles():
                nonlocal articles, current_article_index
                logger.info("Réactualisation des articles")
                new_articles = fetch_news()
                if new_articles:
                    articles = new_articles
                    current_article_index = 0
                    update_article()
                
                if self.current_frame.winfo_exists():
                    self.root.after(600000, update_articles)
            
            articles = fetch_news()
            current_article_index = 0
            
            if articles:
                def update_article():
                    nonlocal current_article_index
                    
                    if not self.current_frame.winfo_exists():
                        return
                        
                    if current_article_index < len(articles):
                        article = articles[current_article_index]
                        
                        title_label.configure(text=article.get('title', 'Pas de titre'))
                        desc_label.configure(text=article.get('description', 'Pas de description'))
                        
                        current_article_index = (current_article_index + 1) % len(articles)
                        
                        if self.current_frame.winfo_exists():
                            self.root.after(10000, update_article)
                
                update_article()
                self.root.after(600000, update_articles)
                
            else:
                error_label = tk.Label(article_frame,
                                     text="Erreur lors de la récupération des actualités",
                                     font=("Arial", 14),
                                     fg='red',
                                     bg='black')
                error_label.pack(pady=20)
            
        except Exception as e:
            logger.error(f"Erreur dans show_news_screen: {e}")
            logger.exception(e)

    def show_default_screen(self):
        global current_screen
        current_screen = self.default_screen

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Erreur route /: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/change_screen/<screen>')
def change_screen(screen):
    try:
        global current_screen
        current_screen = screen
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Erreur route /change_screen: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({'status': 'error', 'message': 'No photo uploaded'})
        
        photo = request.files['photo']
        if photo.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})
        
        if photo:
            filename = os.path.join('uploaded_photos', photo.filename)
            photo.save(filename)
            logger.info(f"Photo sauvegardée: {filename}")
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Erreur upload_photo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_default_screen')
def get_default_screen():
    try:
        return jsonify({'screen': app.default_screen, 'status': 'success'})
    except Exception as e:
        logger.error(f"Erreur route /get_default_screen: {e}")
        return jsonify({'error': str(e)}), 500

def run_flask():
    try:
        app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Erreur démarrage Flask: {e}")

if __name__ == "__main__":
    try:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        logger.info("Serveur Flask démarré")
        
        app = TinyCompagnon()
        app.root.mainloop()
    except Exception as e:
        logger.error(f"Erreur principale: {e}")
        sys.exit(1)
