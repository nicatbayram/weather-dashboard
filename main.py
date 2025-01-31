import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
from dotenv import load_dotenv
import os

class ModernWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg='#1B4965')
        self.root.minsize(700, 500)
        
        # Configure API
        load_dotenv()
        self.api_key = "598cc438e30bc23a740a2b44a1be4e47" #Get your api http://openweathermap.org/
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Setup styles and GUI
        self.setup_styles()
        self.setup_gui()
        self.setup_icons()
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Custom theme configuration
        style.theme_create('weather_theme', parent='alt', settings={ 
            'TFrame': {'configure': {'background': '#1B4965'}},
            'TButton': {'configure': {'anchor': 'center', 'relief': 'flat'}}, 
            'TLabel': {'configure': {'background': '#1B4965', 'foreground': 'white'}} 
        })
        style.theme_use('weather_theme')
        
        # Custom component styles
        style.configure('Card.TFrame', background='#FFFFFF', borderwidth=2, relief='solid', bordercolor='#E0E0E0')
        style.configure('Shadow.TFrame', background='#1B4965')
        
        # Title styles
        style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'), foreground='#E8F1F5')
        style.configure('Subtitle.TLabel', font=('Helvetica', 12), foreground='#B0D7FF')
        
        # Card styles with border-radius effect
        card_titles = {
            'TempTitle.TLabel': '#E74C3C',
            'FeelsTitle.TLabel': '#2980B9',
            'HumidityTitle.TLabel': '#16A085',
            'WeatherTitle.TLabel': '#8E44AD',
            'WindTitle.TLabel': '#F39C12',
            'PressureTitle.TLabel': '#34495E'
        }
        
        for style_name, color in card_titles.items():
            style.configure(style_name, 
                          font=('Helvetica', 10, 'bold'),
                          background='white',
                          foreground=color)
            
        style.configure('Value.TLabel', 
                      font=('Helvetica', 18),
                      background='white',
                      foreground='#2C3E50')
        
        style.configure('TempValue.TLabel', 
                      font=('Helvetica', 24, 'bold'),
                      background='white',
                      foreground='#E74C3C')
        
        # Button styles
        style.map('Search.TButton',
                background=[('active', '#4A90E2'), ('pressed', '#357ABD')], 
                foreground=[('active', 'white')])
        style.configure('Search.TButton',
                      font=('Helvetica', 11, 'bold'),
                      background='#5FA8D3',
                      foreground='white',
                      borderwidth=0,
                      width=15,
                      padding=10,
                      focuscolor='none',
                      focusthickness=23)
        
        
        # Entry styles
        style.configure('Search.TEntry',
                      font=('Helvetica', 12),
                      fieldbackground='white',
                      borderwidth=2,
                      relief='solid',
                      width=15,
                      padding=10,
                      focuscolor='none',
                      focusthickness=23)
        
        # Error label
        style.configure('Error.TLabel',
                      background='#1B4965',
                      foreground='#ffffff',
                      font=('Helvetica', 10, 'bold'))
        
    def setup_icons(self):
        self.weather_icons = {
            'Thunderstorm': '⛈️',
            'Drizzle': '🌧️',
            'Rain': '🌧️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Smoke': '🌫️',
            'Haze': '🌫️',
            'Dust': '🌫️',
            'Fog': '🌫️',
            'Sand': '🌫️',
            'Ash': '🌫️',
            'Squall': '🌫️',
            'Tornado': '🌪️',
            'Clear': '☀️',
            'Clouds': '☁️'
        }
        
    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Label(header_frame, 
                 text="Weather Dashboard",
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # Search section
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.city_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame,
                               textvariable=self.city_var,
                               style='Search.TEntry',
                               width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.fetch_weather())
        
        self.search_button = ttk.Button(search_frame,
                                      text="Get Weather",
                                      command=self.fetch_weather,
                                      style='Search.TButton')
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.loading_label = ttk.Label(search_frame, text="", style='Subtitle.TLabel')
        
        self.error_label = ttk.Label(search_frame, text="", style='Error.TLabel')
        
        # Weather cards grid
        self.weather_container = ttk.Frame(main_frame)
        self.weather_container.pack(fill=tk.BOTH, expand=True)
        
        # Create weather cards with shadows and border-radius
        self.cards = {
        'temp': self.create_card("TEMPERATURE", "-- °C", 'TempTitle.TLabel', 'TempValue.TLabel'),
        'feels': self.create_card("FEELS LIKE", "-- °C", 'FeelsTitle.TLabel'),
        'humidity': self.create_card("HUMIDITY", "--%", 'HumidityTitle.TLabel'),
        'weather': self.create_card("WEATHER", "--", 'WeatherTitle.TLabel'),
        'wind': self.create_card("WIND SPEED", "-- m/s", 'WindTitle.TLabel'),
        'pressure': self.create_card("PRESSURE", "-- hPa", 'PressureTitle.TLabel')
        }
        
        # Grid layout
        rows = [
        ['temp', 'feels', 'humidity'],
        ['weather', 'wind', 'pressure']
        ]
        for i, row_keys in enumerate(rows):
            for j, key in enumerate(row_keys):
                self.cards[key].grid(row=i, column=j, padx=10, pady=10, sticky='nsew')
                self.weather_container.grid_columnconfigure(j, weight=1)
            self.weather_container.grid_rowconfigure(i, weight=1)
        
    def create_card(self, title, value, title_style=None, value_style='Value.TLabel'):
        # Shadow effect
        shadow = ttk.Frame(self.weather_container, style='Shadow.TFrame')
        card_frame = ttk.Frame(shadow, style='Card.TFrame')
        card_frame.pack(padx=3, pady=3, fill=tk.BOTH, expand=True)
        
        # Card content
        title_label = ttk.Label(card_frame, text=title, style=title_style)
        title_label.pack(pady=(15, 40))
        
        value_label = ttk.Label(card_frame, text=value, style=value_style)
        value_label.pack(pady=(0, 25))
        
        # Special case for weather card
        if title == "WEATHER":
            self.weather_icon = ttk.Label(card_frame, text="", font=('Helvetica', 24))
            self.weather_icon.pack(pady=(10, 0))
            card_frame.weather_icon = self.weather_icon

        card_frame.value_label = value_label
        return shadow
        
    def fetch_weather(self):
        city = self.city_var.get().strip()
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.search_button.config(state=tk.DISABLED)
        self.loading_label.config(text="Fetching...")
        self.loading_label.pack(side=tk.LEFT, padx=(10, 0))
        
        threading.Thread(target=self.fetch_data, args=(city,), daemon=True).start()
        
    def fetch_data(self, city):
        try:
            params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            self.root.after(0, self.update_ui, data)
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))
        finally:
            self.root.after(0, self.reset_ui)
            
    def update_ui(self, data):
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        
        # Update cards
        self.cards['temp'].children['!frame'].value_label.config(text=f"{main['temp']}°C")
        self.cards['feels'].children['!frame'].value_label.config(text=f"{main['feels_like']}°C")
        self.cards['humidity'].children['!frame'].value_label.config(text=f"{main['humidity']}%")
        self.cards['wind'].children['!frame'].value_label.config(text=f"{wind['speed']} m/s")
        self.cards['pressure'].children['!frame'].value_label.config(text=f"{main['pressure']} hPa")
        
        # Update weather description and icon
        weather_desc = weather['description'].capitalize()
        self.cards['weather'].children['!frame'].value_label.config(text=weather_desc)
        icon = self.weather_icons.get(weather['main'], '🌤️')
        self.cards['weather'].children['!frame'].weather_icon.config(text=icon)
        
    def handle_error(self, error):
        self.show_error(f"Error: {error.split(':')[0]}")

    def reset_ui(self):
        self.search_button.config(state=tk.NORMAL)
        self.loading_label.pack_forget()

    def show_error(self, message):
        self.error_label.config(text=message)
        self.error_label.pack(side=tk.LEFT, padx=(10, 0))
        self.root.after(3000, self.error_label.pack_forget)

def main():
    root = tk.Tk()
    app = ModernWeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
