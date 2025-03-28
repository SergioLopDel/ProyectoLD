import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Configuración de rangos de alta precisión
servicio = ctrl.Antecedent(np.linspace(0, 5, 501), 'servicio')
comida = ctrl.Antecedent(np.linspace(0, 5, 501), 'comida')
propina = ctrl.Consequent(np.linspace(0, 15, 1501), 'propina')

# Funciones de membresía para servicio
servicio['inexistente'] = fuzz.trimf(servicio.universe, [0, 0, 0.001])
servicio['mediocre'] = fuzz.trapmf(servicio.universe, [0.001, 0.1, 1, 1.5])
servicio['mala'] = fuzz.trimf(servicio.universe, [0.5, 1.5, 2.5])
servicio['regular'] = fuzz.trimf(servicio.universe, [1.5, 2.5, 3.5])
servicio['bueno'] = fuzz.trimf(servicio.universe, [2.5, 3.5, 4.5])
servicio['excelente'] = fuzz.trapmf(servicio.universe, [3.5, 4.5, 5, 5])

# Funciones de membresía para comida
comida['inexistente'] = fuzz.trimf(comida.universe, [0, 0, 0.001])
comida['mediocre'] = fuzz.trapmf(comida.universe, [0.001, 0.1, 1, 1.5])
comida['mala'] = fuzz.trimf(comida.universe, [0.5, 1.5, 2.5])
comida['regular'] = fuzz.trimf(comida.universe, [1.5, 2.5, 3.5])
comida['bueno'] = fuzz.trimf(comida.universe, [2.5, 3.5, 4.5])
comida['excelente'] = fuzz.trapmf(comida.universe, [3.5, 4.5, 5, 5])

# Configuración manual de las membresías de propina
propina['muyalta'] = fuzz.trimf(propina.universe, [15, 15, 15])
propina['alta'] = fuzz.trapmf(propina.universe, [10, 12, 14, 14.99])
propina['media'] = fuzz.trapmf(propina.universe, [6, 8, 10, 12])
propina['baja'] = fuzz.trapmf(propina.universe, [2, 4, 6, 8])
propina['muybaja'] = fuzz.trimf(propina.universe, [0, 0, 0])

# Reglas del sistema (igual que antes)
rules = [
    ctrl.Rule(servicio['inexistente'] & comida['inexistente'], propina['muybaja']),
    ctrl.Rule(servicio['inexistente'] & comida['mediocre'], propina['muybaja']),
    ctrl.Rule(servicio['inexistente'] & comida['mala'], propina['muybaja']),
    ctrl.Rule(servicio['inexistente'] & comida['regular'], propina['muybaja']),
    ctrl.Rule(servicio['inexistente'] & comida['bueno'], propina['muybaja']),
    ctrl.Rule(servicio['inexistente'] & comida['excelente'], propina['muybaja']),
    
    ctrl.Rule(servicio['mediocre'] & comida['inexistente'], propina['muybaja']),
    ctrl.Rule(servicio['mala'] & comida['inexistente'], propina['muybaja']),
    ctrl.Rule(servicio['regular'] & comida['inexistente'], propina['muybaja']),
    ctrl.Rule(servicio['bueno'] & comida['inexistente'], propina['muybaja']),
    ctrl.Rule(servicio['excelente'] & comida['inexistente'], propina['muybaja']),
    
    ctrl.Rule(servicio['mediocre'] & comida['mediocre'], propina['baja']),
    ctrl.Rule(servicio['mediocre'] & comida['mala'], propina['baja']),
    ctrl.Rule(servicio['mediocre'] & comida['regular'], propina['baja']),
    ctrl.Rule(servicio['mediocre'] & comida['bueno'], propina['media']),
    ctrl.Rule(servicio['mediocre'] & comida['excelente'], propina['media']),
    
    ctrl.Rule(servicio['mala'] & comida['mediocre'], propina['baja']),
    ctrl.Rule(servicio['mala'] & comida['mala'], propina['baja']),
    ctrl.Rule(servicio['mala'] & comida['regular'], propina['media']),
    ctrl.Rule(servicio['mala'] & comida['bueno'], propina['media']),
    ctrl.Rule(servicio['mala'] & comida['excelente'], propina['media']),
    
    ctrl.Rule(servicio['regular'] & comida['mediocre'], propina['media']),
    ctrl.Rule(servicio['regular'] & comida['mala'], propina['media']),
    ctrl.Rule(servicio['regular'] & comida['regular'], propina['media']),
    ctrl.Rule(servicio['regular'] & comida['bueno'], propina['alta']),
    ctrl.Rule(servicio['regular'] & comida['excelente'], propina['alta']),
    
    ctrl.Rule(servicio['bueno'] & comida['mediocre'], propina['media']),
    ctrl.Rule(servicio['bueno'] & comida['mala'], propina['media']),
    ctrl.Rule(servicio['bueno'] & comida['regular'], propina['alta']),
    ctrl.Rule(servicio['bueno'] & comida['bueno'], propina['alta']),
    ctrl.Rule(servicio['bueno'] & comida['excelente'], propina['muyalta']),
    
    ctrl.Rule(servicio['excelente'] & comida['mediocre'], propina['alta']),
    ctrl.Rule(servicio['excelente'] & comida['mala'], propina['alta']),
    ctrl.Rule(servicio['excelente'] & comida['regular'], propina['muyalta']),
    ctrl.Rule(servicio['excelente'] & comida['bueno'], propina['muyalta']),
    ctrl.Rule(servicio['excelente'] & comida['excelente'], propina['muyalta']),
]

sistema_propina = ctrl.ControlSystem(rules)
calculador_propina = ctrl.ControlSystemSimulation(sistema_propina)
calculador_propina.defuzz_method = 'lom'

class StarRating(tk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
        self.value = tk.DoubleVar(value=0)
        self.stars = []
        
        # Crear título
        ttk.Label(self, text=title, font=('Helvetica', 12)).pack()
        
        # Frame para estrellas
        star_frame = tk.Frame(self)
        star_frame.pack(pady=5)
        
        # Crear 5 estrellas
        for i in range(5):
            star = tk.Label(star_frame, text="☆", font=('Helvetica', 24), fg='gold')
            star.bind("<Button-1>", lambda e, idx=i+1: self.set_value(idx))
            star.bind("<Enter>", lambda e, idx=i+1: self.hover(idx))
            star.bind("<Leave>", lambda e: self.hover(0))
            star.pack(side=tk.LEFT, padx=2)
            self.stars.append(star)
        
        # Botón para cero estrellas
        zero_btn = ttk.Button(self, text="0 estrellas", command=lambda: self.set_value(0))
        zero_btn.pack(pady=5)
    
    def set_value(self, value):
        self.value.set(value)
        self.update_stars()
    
    def hover(self, value):
        if value == 0:
            self.update_stars()
        else:
            for i in range(5):
                self.stars[i].config(text="★" if i < value else "☆")
    
    def update_stars(self):
        current_value = round(self.value.get())
        for i in range(5):
            self.stars[i].config(text="★" if i < current_value else "☆")

class PropinaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌟 Sistema de Propinas Difuso 🌟")
        self.geometry("800x600")
        self.configure(bg='#f0f0f0')
        
        # Frame principal con estilo
        main_frame = ttk.Frame(self, padding="20", style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('Card.TFrame', background='white', borderwidth=2, relief='groove')
        self.style.configure('TButton', font=('Helvetica', 10), padding=6)
        self.style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), background='white')
        
        # Título con emoji
        title_label = ttk.Label(main_frame, text="🌟 Sistema de Propinas 🌟", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame para calificaciones
        rating_frame = ttk.Frame(main_frame)
        rating_frame.pack(fill=tk.X, pady=10)
        
        # Calificación de servicio
        self.servicio_rating = StarRating(rating_frame, "Calificación del Servicio:")
        self.servicio_rating.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Calificación de comida
        self.comida_rating = StarRating(rating_frame, "Calificación de la Comida:")
        self.comida_rating.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Botón para calcular
        calc_btn = ttk.Button(main_frame, text="💸 Calcular Propina 💸", command=self.calculate_tip)
        calc_btn.pack(pady=20)
        
        # Resultado con estilo
        result_frame = ttk.Frame(main_frame, style='Card.TFrame')
        result_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(result_frame, text="Propina recomendada:", font=('Helvetica', 12)).pack(pady=(10, 0))
        
        self.propina_display = ttk.Label(
            result_frame, 
            text="0.00%", 
            font=('Helvetica', 28, 'bold'),
            foreground='#2ECC71'
        )
        self.propina_display.pack()
        
        self.category_display = ttk.Label(
            result_frame, 
            text="(Muy baja)", 
            font=('Helvetica', 14),
            foreground='#E74C3C'
        )
        self.category_display.pack(pady=(0, 10))
        
        # Gráficos (opcional)
        self.setup_graphs(main_frame)
    
    def setup_graphs(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña para servicio
        tab1 = ttk.Frame(notebook)
        fig1 = Figure(figsize=(5, 3), dpi=100)
        ax1 = fig1.add_subplot(111)
        for key in servicio.terms:
            ax1.plot(servicio.universe, servicio[key].mf, label=key)
        ax1.legend()
        ax1.set_title("Membresía de Servicio")
        
        canvas1 = FigureCanvasTkAgg(fig1, tab1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña para comida
        tab2 = ttk.Frame(notebook)
        fig2 = Figure(figsize=(5, 3), dpi=100)
        ax2 = fig2.add_subplot(111)
        for key in comida.terms:
            ax2.plot(comida.universe, comida[key].mf, label=key)
        ax2.legend()
        ax2.set_title("Membresía de Comida")
        
        canvas2 = FigureCanvasTkAgg(fig2, tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña para propina
        tab3 = ttk.Frame(notebook)
        fig3 = Figure(figsize=(5, 3), dpi=100)
        ax3 = fig3.add_subplot(111)
        for key in propina.terms:
            ax3.plot(propina.universe, propina[key].mf, label=key)
        ax3.legend()
        ax3.set_title("Membresía de Propina")
        
        canvas3 = FigureCanvasTkAgg(fig3, tab3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        notebook.add(tab1, text="Servicio")
        notebook.add(tab2, text="Comida")
        notebook.add(tab3, text="Propina")
    
    def get_tip_category(self, tip_value):
        if tip_value <= 1:
            return "Muy baja"
        elif tip_value <= 6:
            return "Baja"
        elif tip_value <= 10:
            return "Media"
        elif tip_value <= 13:
            return "Alta"
        else:
            return "Muy alta"
    
    def calculate_tip(self):
        try:
            servicio_val = self.servicio_rating.value.get()
            comida_val = self.comida_rating.value.get()
            
            # Caso especial [0,0]
            if servicio_val == 0 and comida_val == 0:
                self.propina_display.config(text="0.00%", foreground='#E74C3C')
                self.category_display.config(text="(Muy baja)")
                return
                
            # Resto de casos
            calculador_propina.input['servicio'] = servicio_val
            calculador_propina.input['comida'] = comida_val
            calculador_propina.compute()
            
            tip = calculador_propina.output['propina']
            category = self.get_tip_category(tip)
            
            # Actualizar displays
            self.propina_display.config(text=f"{max(0, min(tip, 15)):.2f}%")
            self.category_display.config(text=f"({category})")
            
            # Configurar color según categoría
            colors = {
                "Muy baja": '#E74C3C',
                "Baja": '#E67E22',
                "Media": '#F1C40F',
                "Alta": '#2ECC71',
                "Muy alta": '#9B59B6'
            }
            color = colors.get(category, '#2ECC71')
            self.propina_display.config(foreground=color)
            self.category_display.config(foreground=color)
            
        except Exception as e:
            self.propina_display.config(text="Error", foreground='#E74C3C')
            self.category_display.config(text="(Verifique los valores)")

if __name__ == "__main__":
    app = PropinaApp()
    app.mainloop()