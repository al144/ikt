"""
Időjárás Előrejelző Asztali Alkalmazás
Modern, professzionális megjelenésű desktop alkalmazás WeatherAPI használatával
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import io

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Időjárás Központ")
        self.root.geometry("1200x900")
        self.root.configure(bg='#0f172a')
        
        # API konfiguráció
        self.API_KEY = 'fc0c362b1feb4ed78b6173130251712'
        self.BASE_URL = 'https://api.weatherapi.com/v1'
        
        # Színséma
        self.colors = {
            'bg_dark': '#0f172a',
            'bg_card': '#1e293b',
            'bg_card_hover': '#334155',
            'text_primary': '#ffffff',
            'text_secondary': '#94a3b8',
            'accent_blue': '#3b82f6',
            'accent_cyan': '#06b6d4',
            'accent_red': '#ef4444',
            'accent_orange': '#f97316',
            'accent_green': '#10b981',
            'border': '#475569'
        }
        
        self.setup_styles()
        self.create_widgets()
        
        # Alapértelmezett város betöltése
        self.load_weather('Budapest')
    
    def setup_styles(self):
        """Stílusok beállítása"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Entry stílus
        style.configure('Search.TEntry',
                       fieldbackground=self.colors['bg_card'],
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       relief='flat')
        
        # Button stílus
        style.configure('Search.TButton',
                       background=self.colors['accent_blue'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat',
                       padding=10)
        
        style.map('Search.TButton',
                 background=[('active', self.colors['accent_cyan'])])
    
    def create_widgets(self):
        """UI elemek létrehozása"""
        # Fő keretrendszer
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Címsor
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="IDŐJÁRÁS KÖZPONT",
            font=('Arial Black', 32, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_dark']
        )
        title_label.pack()
        
        # Keresés
        search_frame = tk.Frame(main_frame, bg=self.colors['bg_card'], relief='flat', bd=2)
        search_frame.pack(fill='x', pady=(0, 20))
        
        self.search_entry = tk.Entry(
            search_frame,
            font=('Arial', 14),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=10
        )
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.insert(0, 'Keress települést...')
        self.search_entry.bind('<FocusIn>', self.on_entry_click)
        self.search_entry.bind('<FocusOut>', self.on_focusout)
        self.search_entry.bind('<Return>', lambda e: self.search_weather())
        
        search_btn = tk.Button(
            search_frame,
            text="KERESÉS",
            font=('Arial Black', 12, 'bold'),
            bg=self.colors['accent_blue'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent_cyan'],
            activeforeground=self.colors['text_primary'],
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.search_weather
        )
        search_btn.pack(side='right', padx=5, pady=5)
        
        # Scrollable frame a tartalomnak
        canvas = tk.Canvas(main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Egér görgő támogatás
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
    
    def on_entry_click(self, event):
        """Entry placeholder kezelés"""
        if self.search_entry.get() == 'Keress települést...':
            self.search_entry.delete(0, 'end')
            self.search_entry.config(fg=self.colors['text_primary'])
    
    def on_focusout(self, event):
        """Entry placeholder visszaállítás"""
        if self.search_entry.get() == '':
            self.search_entry.insert(0, 'Keress települést...')
            self.search_entry.config(fg=self.colors['text_secondary'])
    
    def search_weather(self):
        """Keresés végrehajtása"""
        city = self.search_entry.get()
        if city and city != 'Keress települést...':
            self.load_weather(city)
    
    def create_card(self, parent, title, value, icon='📊', color=None):
        """Információs kártya létrehozása"""
        if color is None:
            color = self.colors['bg_card']
        
        card = tk.Frame(parent, bg=color, relief='flat', bd=0)
        card.pack(fill='x', pady=5)
        
        # Belső padding
        inner = tk.Frame(card, bg=color)
        inner.pack(fill='x', padx=15, pady=15)
        
        # Icon és címke
        header = tk.Frame(inner, bg=color)
        header.pack(fill='x')
        
        icon_label = tk.Label(
            header,
            text=icon,
            font=('Arial', 20),
            bg=color,
            fg=self.colors['text_primary']
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        title_label = tk.Label(
            header,
            text=title,
            font=('Arial', 12),
            bg=color,
            fg=self.colors['text_secondary']
        )
        title_label.pack(side='left')
        
        # Érték
        value_label = tk.Label(
            inner,
            text=value,
            font=('Arial Black', 24, 'bold'),
            bg=color,
            fg=self.colors['text_primary']
        )
        value_label.pack(anchor='w', pady=(5, 0))
        
        return card
    
    def format_value(self, value, unit=''):
        """Érték formázás N/A kezeléssel"""
        if value is None or value == '':
            return 'N/A'
        return f"{value}{unit}"
    
    def load_weather(self, city):
        """Időjárás adatok betöltése"""
        try:
            # Aktuális időjárás
            current_url = f"{self.BASE_URL}/current.json?key={self.API_KEY}&q={city}&lang=hu&aqi=yes"
            forecast_url = f"{self.BASE_URL}/forecast.json?key={self.API_KEY}&q={city}&days=8&lang=hu&aqi=yes"
            
            current_response = requests.get(current_url)
            forecast_response = requests.get(forecast_url)
            
            if current_response.status_code != 200 or forecast_response.status_code != 200:
                messagebox.showerror("Hiba", "Település nem található!")
                return
            
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            
            self.display_weather(current_data, forecast_data)
            
        except Exception as e:
            messagebox.showerror("Hiba", f"Hiba történt az adatok betöltése során:\n{str(e)}")
    
    def display_weather(self, current_data, forecast_data):
        """Időjárás megjelenítése"""
        # Tartalom törlése
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Adatok kinyerése
        current = current_data.get('current', {})
        location = current_data.get('location', {})
        today = forecast_data.get('forecast', {}).get('forecastday', [{}])[0]
        forecast_days = forecast_data.get('forecast', {}).get('forecastday', [])[1:8]
        
        # Fő időjárás kártya
        main_card = tk.Frame(self.scrollable_frame, bg=self.colors['bg_card'], relief='flat')
        main_card.pack(fill='x', pady=(0, 20))
        
        main_inner = tk.Frame(main_card, bg=self.colors['bg_card'])
        main_inner.pack(fill='x', padx=20, pady=20)
        
        # Város és idő
        city_label = tk.Label(
            main_inner,
            text=location.get('name', 'N/A'),
            font=('Arial Black', 28, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        city_label.pack(anchor='w')
        
        location_label = tk.Label(
            main_inner,
            text=f"{location.get('country', 'N/A')} • {location.get('localtime', 'N/A').split(' ')[1] if location.get('localtime') else 'N/A'}",
            font=('Arial', 14),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        location_label.pack(anchor='w', pady=(5, 20))
        
        # Hőmérséklet és állapot
        temp_frame = tk.Frame(main_inner, bg=self.colors['bg_card'])
        temp_frame.pack(anchor='w', pady=(0, 15))
        
        icon_label = tk.Label(
            temp_frame,
            text=self.get_weather_emoji(current.get('condition', {}).get('text', '')),
            font=('Arial', 60),
            bg=self.colors['bg_card']
        )
        icon_label.pack(side='left', padx=(0, 20))
        
        temp_info = tk.Frame(temp_frame, bg=self.colors['bg_card'])
        temp_info.pack(side='left')
        
        temp_label = tk.Label(
            temp_info,
            text=self.format_value(current.get('temp_c'), '°'),
            font=('Arial Black', 72, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        temp_label.pack(anchor='w')
        
        condition_label = tk.Label(
            temp_info,
            text=current.get('condition', {}).get('text', 'N/A'),
            font=('Arial', 16),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        condition_label.pack(anchor='w')
        
        # Min/Max
        minmax_frame = tk.Frame(main_inner, bg=self.colors['bg_card'])
        minmax_frame.pack(anchor='w')
        
        tk.Label(
            minmax_frame,
            text=f"Max: {self.format_value(today.get('day', {}).get('maxtemp_c'), '°C')}",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_card'],
            fg='#fca5a5'
        ).pack(side='left', padx=(0, 20))
        
        tk.Label(
            minmax_frame,
            text=f"Min: {self.format_value(today.get('day', {}).get('mintemp_c'), '°C')}",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_card'],
            fg='#93c5fd'
        ).pack(side='left')
        
        # Statisztikák
        stats_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_dark'])
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # 2x2 grid
        stats_grid = tk.Frame(stats_frame, bg=self.colors['bg_dark'])
        stats_grid.pack()
        
        # 1. sor
        row1 = tk.Frame(stats_grid, bg=self.colors['bg_dark'])
        row1.pack(fill='x', pady=(0, 10))
        
        stat1 = tk.Frame(row1, bg=self.colors['bg_card'])
        stat1.pack(side='left', padx=(0, 10), expand=True, fill='both')
        self.create_card(stat1, 'Páratartalom', 
                        self.format_value(current.get('humidity'), '%'), '💧')
        
        stat2 = tk.Frame(row1, bg=self.colors['bg_card'])
        stat2.pack(side='left', expand=True, fill='both')
        self.create_card(stat2, 'Szél', 
                        self.format_value(current.get('wind_kph'), ' km/h'), '💨')
        
        # 2. sor
        row2 = tk.Frame(stats_grid, bg=self.colors['bg_dark'])
        row2.pack(fill='x')
        
        stat3 = tk.Frame(row2, bg=self.colors['bg_card'])
        stat3.pack(side='left', padx=(0, 10), expand=True, fill='both')
        self.create_card(stat3, 'Látótávolság', 
                        self.format_value(current.get('vis_km'), ' km'), '👁️')
        
        stat4 = tk.Frame(row2, bg=self.colors['bg_card'])
        stat4.pack(side='left', expand=True, fill='both')
        self.create_card(stat4, 'Légnyomás', 
                        self.format_value(current.get('pressure_mb'), ' mb'), '🌡️')
        
        # Napkelte/Naplemente
        sun_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_dark'])
        sun_frame.pack(fill='x', pady=(0, 20))
        
        sunrise_card = tk.Frame(sun_frame, bg=self.colors['bg_card'])
        sunrise_card.pack(side='left', expand=True, fill='both', padx=(0, 10))
        self.create_card(sunrise_card, 'Napkelte', 
                        today.get('astro', {}).get('sunrise', 'N/A'), '🌅')
        
        sunset_card = tk.Frame(sun_frame, bg=self.colors['bg_card'])
        sunset_card.pack(side='left', expand=True, fill='both')
        self.create_card(sunset_card, 'Naplemente', 
                        today.get('astro', {}).get('sunset', 'N/A'), '🌇')
        
        # Figyelmeztetések
        avg_temp = today.get('day', {}).get('avgtemp_c')
        uv_index = current.get('uv')
        
        if (avg_temp is not None and avg_temp < 7) or (uv_index is not None and uv_index >= 6):
            alerts_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_dark'])
            alerts_frame.pack(fill='x', pady=(0, 20))
            
            if avg_temp is not None and avg_temp < 7:
                alert1 = tk.Frame(alerts_frame, bg='#1e40af', relief='flat')
                alert1.pack(fill='x', pady=(0, 10))
                
                alert_inner = tk.Frame(alert1, bg='#1e40af')
                alert_inner.pack(fill='x', padx=15, pady=15)
                
                tk.Label(
                    alert_inner,
                    text="⚠️ TÉLI GUMI AJÁNLOTT",
                    font=('Arial Black', 14, 'bold'),
                    bg='#1e40af',
                    fg='#dbeafe'
                ).pack(anchor='w', pady=(0, 5))
                
                tk.Label(
                    alert_inner,
                    text=f"Az átlaghőmérséklet {self.format_value(avg_temp, '°C')}, ami 7°C alatt van.\nAjánlott téli gumit használni!",
                    font=('Arial', 11),
                    bg='#1e40af',
                    fg='#bfdbfe',
                    justify='left'
                ).pack(anchor='w')
            
            if uv_index is not None and uv_index >= 6:
                alert2 = tk.Frame(alerts_frame, bg='#c2410c', relief='flat')
                alert2.pack(fill='x')
                
                alert_inner = tk.Frame(alert2, bg='#c2410c')
                alert_inner.pack(fill='x', padx=15, pady=15)
                
                tk.Label(
                    alert_inner,
                    text="⚠️ MAGAS UV SUGÁRZÁS",
                    font=('Arial Black', 14, 'bold'),
                    bg='#c2410c',
                    fg='#fed7aa'
                ).pack(anchor='w', pady=(0, 5))
                
                tk.Label(
                    alert_inner,
                    text=f"Az UV index {self.format_value(uv_index)}!\nHasználj napvédő krémet és kerüld a közvetlen napfényt!",
                    font=('Arial', 11),
                    bg='#c2410c',
                    fg='#fdba74',
                    justify='left'
                ).pack(anchor='w')
        
        # 7 napos előrejelzés
        forecast_title = tk.Label(
            self.scrollable_frame,
            text="7 NAPOS ELŐREJELZÉS",
            font=('Arial Black', 20, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary']
        )
        forecast_title.pack(anchor='w', pady=(0, 15))
        
        forecast_container = tk.Frame(self.scrollable_frame, bg=self.colors['bg_card'])
        forecast_container.pack(fill='x')
        
        for i, day in enumerate(forecast_days):
            date_obj = datetime.strptime(day.get('date', ''), '%Y-%m-%d')
            day_name = date_obj.strftime('%a')
            date_str = date_obj.strftime('%b %d')
            
            day_frame = tk.Frame(forecast_container, bg=self.colors['bg_card_hover'] if i % 2 == 0 else self.colors['bg_card'])
            day_frame.pack(fill='x', pady=1)
            
            day_inner = tk.Frame(day_frame, bg=day_frame['bg'])
            day_inner.pack(fill='x', padx=15, pady=10)
            
            # Nap neve
            tk.Label(
                day_inner,
                text=day_name.upper(),
                font=('Arial Black', 11, 'bold'),
                bg=day_frame['bg'],
                fg=self.colors['accent_cyan'],
                width=6
            ).pack(side='left', padx=(0, 10))
            
            # Dátum
            tk.Label(
                day_inner,
                text=date_str,
                font=('Arial', 10),
                bg=day_frame['bg'],
                fg=self.colors['text_secondary'],
                width=8
            ).pack(side='left', padx=(0, 15))
            
            # Ikon
            tk.Label(
                day_inner,
                text=self.get_weather_emoji(day.get('day', {}).get('condition', {}).get('text', '')),
                font=('Arial', 24),
                bg=day_frame['bg']
            ).pack(side='left', padx=(0, 15))
            
            # Hőmérséklet
            temp_frame = tk.Frame(day_inner, bg=day_frame['bg'])
            temp_frame.pack(side='left', padx=(0, 15))
            
            tk.Label(
                temp_frame,
                text=self.format_value(day.get('day', {}).get('avgtemp_c'), '°'),
                font=('Arial Black', 18, 'bold'),
                bg=day_frame['bg'],
                fg=self.colors['text_primary']
            ).pack()
            
            # Trend
            if i > 0:
                prev_temp = forecast_days[i-1].get('day', {}).get('avgtemp_c')
                curr_temp = day.get('day', {}).get('avgtemp_c')
                trend = self.get_trend_icon(prev_temp, curr_temp)
                
                tk.Label(
                    temp_frame,
                    text=trend,
                    font=('Arial', 12),
                    bg=day_frame['bg']
                ).pack()
            
            # Min/Max
            minmax_frame = tk.Frame(day_inner, bg=day_frame['bg'])
            minmax_frame.pack(side='left', padx=(0, 15))
            
            tk.Label(
                minmax_frame,
                text=f"↑ {self.format_value(day.get('day', {}).get('maxtemp_c'), '°')}",
                font=('Arial', 10),
                bg=day_frame['bg'],
                fg='#fca5a5'
            ).pack()
            
            tk.Label(
                minmax_frame,
                text=f"↓ {self.format_value(day.get('day', {}).get('mintemp_c'), '°')}",
                font=('Arial', 10),
                bg=day_frame['bg'],
                fg='#93c5fd'
            ).pack()
            
            # Feltétel
            tk.Label(
                day_inner,
                text=day.get('day', {}).get('condition', {}).get('text', 'N/A'),
                font=('Arial', 10),
                bg=day_frame['bg'],
                fg=self.colors['text_secondary']
            ).pack(side='left', fill='x', expand=True)
        
        # Lábléc
        footer = tk.Label(
            self.scrollable_frame,
            text=f"Adatforrás: WeatherAPI.com • Frissítve: {location.get('localtime', 'N/A')}",
            font=('Arial', 9),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_secondary']
        )
        footer.pack(pady=20)
    
    def get_weather_emoji(self, condition):
        """Időjárás emoji visszaadása"""
        condition_lower = condition.lower() if condition else ''
        
        if 'hó' in condition_lower or 'snow' in condition_lower:
            return '❄️'
        elif 'eső' in condition_lower or 'rain' in condition_lower or 'zápor' in condition_lower:
            return '🌧️'
        elif 'felhő' in condition_lower or 'cloud' in condition_lower or 'borult' in condition_lower:
            return '☁️'
        elif 'nap' in condition_lower or 'sun' in condition_lower or 'clear' in condition_lower or 'tiszta' in condition_lower:
            return '☀️'
        elif 'vihar' in condition_lower or 'storm' in condition_lower or 'thunder' in condition_lower:
            return '⛈️'
        elif 'köd' in condition_lower or 'fog' in condition_lower or 'mist' in condition_lower:
            return '🌫️'
        else:
            return '🌤️'
    
    def get_trend_icon(self, prev_temp, curr_temp):
        """Trend ikon visszaadása"""
        if prev_temp is None or curr_temp is None:
            return '—'
        
        diff = curr_temp - prev_temp
        if diff > 1:
            return '📈'
        elif diff < -1:
            return '📉'
        else:
            return '—'

def main():
    """Alkalmazás indítása"""
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
