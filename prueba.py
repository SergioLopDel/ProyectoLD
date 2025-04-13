import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class FuzzySystem:
    def __init__(self):
        # Definición de los universos de discurso
        self.servicio_universe = np.linspace(0, 5, 501)
        self.comida_universe = np.linspace(0, 5, 501)
        self.propina_universe = np.linspace(0, 15, 1501)
        
        # Funciones de membresía para servicio y comida
        self.servicio_terms = {
            'mediocre': self.trapmf(self.servicio_universe, [0, 0, 1, 1.5]),
            'mala': self.trimf(self.servicio_universe, [0.5, 1.5, 2.5]),
            'regular': self.trimf(self.servicio_universe, [1.5, 2.5, 3.5]),
            'bueno': self.trimf(self.servicio_universe, [2.5, 3.5, 4.5]),
            'excelente': self.trapmf(self.servicio_universe, [3.5, 4.5, 5, 5])
        }
        
        self.comida_terms = {
            'mediocre': self.trapmf(self.comida_universe, [0, 0, 1, 1.5]),
            'mala': self.trimf(self.comida_universe, [0.5, 1.5, 2.5]),
            'regular': self.trimf(self.comida_universe, [1.5, 2.5, 3.5]),
            'bueno': self.trimf(self.comida_universe, [2.5, 3.5, 4.5]),
            'excelente': self.trapmf(self.comida_universe, [3.5, 4.5, 5, 5])
        }
        
        # Funciones de membresía para propina
        self.propina_terms = {
            'cero': self.singletonmf(self.propina_universe, 0),
            'muybaja': self.trapmf(self.propina_universe, [0, 0, 2, 4]),
            'baja': self.trapmf(self.propina_universe, [2, 4, 6, 8]),
            'media': self.trapmf(self.propina_universe, [6, 8, 10, 12]),
            'alta': self.trapmf(self.propina_universe, [10, 12, 14, 14.99]),
            'muyalta': self.singletonmf(self.propina_universe, 15)
        }
        
        # Reglas del sistema
        self.rules = self.create_rules()
    
    def trimf(self, x, params):
        """Función triangular de membresía"""
        a, b, c = params
        y = np.zeros(len(x))
        y[(a <= x) & (x <= b)] = (x[(a <= x) & (x <= b)] - a) / (b - a)
        y[(b <= x) & (x <= c)] = (c - x[(b <= x) & (x <= c)]) / (c - b)
        return y
    
    def trapmf(self, x, params):
        """Función trapezoidal de membresía"""
        a, b, c, d = params
        y = np.zeros(len(x))
        y[(a <= x) & (x < b)] = (x[(a <= x) & (x < b)] - a) / (b - a)
        y[(b <= x) & (x <= c)] = 1
        y[(c < x) & (x <= d)] = (d - x[(c < x) & (x <= d)]) / (d - c)
        return y
    
    def singletonmf(self, x, value):
        """Función singleton de membresía"""
        y = np.zeros(len(x))
        y[x == value] = 1
        return y
    
    def create_rules(self):
        """Crea las reglas del sistema difuso"""
        rules = []
        
        # Mapeo de categorías a índices para acceder a las funciones de membresía
        categories = ['mediocre', 'mala', 'regular', 'bueno', 'excelente']
        tip_categories = ['muybaja', 'baja', 'media', 'alta', 'muyalta']
        
        # Matriz de reglas (servicio x comida -> propina)
        rule_matrix = [
            # Mediocre  Mala    Regular Bueno   Excelente
            ['muybaja', 'muybaja', 'muybaja', 'muybaja', 'baja'],     # Mediocre
            ['muybaja', 'muybaja', 'muybaja', 'baja', 'media'],      # Mala
            ['muybaja', 'muybaja', 'baja', 'media', 'alta'],        # Regular
            ['muybaja', 'baja', 'media', 'alta', 'muyalta'],        # Bueno
            ['baja', 'media', 'alta', 'muyalta', 'muyalta']         # Excelente
        ]
        
        # Convertir matriz en lista de reglas
        for i, servicio_cat in enumerate(categories):
            for j, comida_cat in enumerate(categories):
                propina_cat = rule_matrix[i][j]
                rules.append({
                    'servicio': servicio_cat,
                    'comida': comida_cat,
                    'propina': propina_cat
                })
        
        # Regla especial para 0,0
        rules.append({
            'servicio': 'mediocre',
            'comida': 'mediocre',
            'propina': 'cero'
        })
        
        return rules
    
    def fuzzify(self, value, terms, universe):
        """Fuzzificación: calcula el grado de membresía para cada término"""
        membership = {}
        for term, mf in terms.items():
            membership[term] = np.interp(value, universe, mf)
        return membership
    
    def infer(self, servicio_val, comida_val):
        """Inferencia difusa: aplica las reglas y calcula la salida agregada"""
        # Paso 1: Fuzzificación de las entradas
        servicio_fuzzy = self.fuzzify(servicio_val, self.servicio_terms, self.servicio_universe)
        comida_fuzzy = self.fuzzify(comida_val, self.comida_terms, self.comida_universe)
        
        # Paso 2: Aplicar reglas y agregar resultados
        aggregated = np.zeros(len(self.propina_universe))
        
        for rule in self.rules:
            # Obtener grados de membresía para los antecedentes
            servicio_degree = servicio_fuzzy[rule['servicio']]
            comida_degree = comida_fuzzy[rule['comida']]
            
            # Aplicar operador AND (usamos mínimo)
            firing_strength = min(servicio_degree, comida_degree)
            
            # Recortar la función de membresía de consecuencia y agregar
            consequence_mf = np.minimum(firing_strength, self.propina_terms[rule['propina']])
            aggregated = np.maximum(aggregated, consequence_mf)
        
        return aggregated
    
    def defuzzify(self, aggregated_output, method='centroid'):
        """Defuzzificación: calcula un valor nítido a partir de la salida difusa"""
        if method == 'centroid':
            # Método del centroide
            if np.sum(aggregated_output) == 0:
                return 0
            return np.sum(self.propina_universe * aggregated_output) / np.sum(aggregated_output)
        elif method == 'lom':
            # Last of Maximum
            max_val = np.max(aggregated_output)
            max_indices = np.where(aggregated_output == max_val)[0]
            return self.propina_universe[max_indices[-1]]
        else:
            raise ValueError("Método de defuzzificación no soportado")

class StarSlider(ttk.Frame):
    def __init__(self, parent, text, variable, from_, to):
        super().__init__(parent)
        self.variable = variable
        self.from_ = from_
        self.to = to
        
        # Frame contenedor para centrar todo
        container = ttk.Frame(self)
        container.pack(expand=True)
        
        # Etiqueta centrada
        ttk.Label(container, text=text, font=('Helvetica', 11)).pack(anchor='center')
        
        # Frame para estrellas centradas
        stars_frame = ttk.Frame(container)
        stars_frame.pack(anchor='center', pady=5)
        
        # Crear estrellas
        self.stars = []
        for i in range(int(from_), int(to)+1):
            star_label = ttk.Label(stars_frame)
            star_label.pack(side=tk.LEFT, padx=2)
            self.stars.append(star_label)
        
        # Slider centrado
        self.slider = ttk.Scale(container, from_=from_, to=to, variable=variable, 
                               command=self.update_stars, length=200)
        self.slider.pack(anchor='center')
        
        # Valor actual centrado
        self.value_label = ttk.Label(container, text=f"{variable.get():.1f}")
        self.value_label.pack(anchor='center')
        
        self.update_stars()
    
    def update_stars(self, *args):
        value = self.variable.get()
        self.value_label.config(text=f"{value:.1f}")
        
        full_star = "★"
        empty_star = "☆"
        
        for i, star_label in enumerate(self.stars, start=self.from_):
            if value >= i:
                star_label.config(text=full_star, font=('Arial', 20), foreground='#FFD700')  # Dorado
            else:
                star_label.config(text=empty_star, font=('Arial', 20), foreground='#CCCCCC')  # Gris claro

class PropinaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.tk.call('tk', 'scaling', 2.0)
        self.title("🌟 Sistema de Propinas Difusas 🌟")
        self.geometry("1000x800")
        self.configure(bg='#f5f5f5')
        
        # Inicializar sistema difuso
        self.fuzzy_system = FuzzySystem()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=8)
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('Result.TLabel', font=('Helvetica', 24, 'bold'))
        
        self.servicio_var = tk.DoubleVar(value=2.5)
        self.comida_var = tk.DoubleVar(value=2.5)
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        ttk.Label(main_frame, text="Sistema de Recomendación de Propinas", 
                 style='Header.TLabel').pack(pady=10)
        
        # Panel de entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=20)
        
        # Slider de servicio con estrellas
        self.servicio_slider = StarSlider(input_frame, "Calificación del Servicio (0-5):", 
                                        self.servicio_var, 0, 5)
        self.servicio_slider.pack(fill=tk.X, pady=10)
        
        # Slider de comida con estrellas
        self.comida_slider = StarSlider(input_frame, "Calificación de la Comida (0-5):", 
                                      self.comida_var, 0, 5)
        self.comida_slider.pack(fill=tk.X, pady=10)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Calcular Propina", 
                  command=self.calculate_tip).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="📋 Ver Reglas de Inferencia", 
                  command=self.show_rules).pack(side=tk.LEFT, padx=10)
        
        # Resultado
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(pady=20)
        
        ttk.Label(result_frame, text="Propina recomendada:", 
                 style='Header.TLabel').pack()
        
        self.propina_display = ttk.Label(result_frame, text="0.00%", 
                                       style='Result.TLabel', foreground='#2e7d32')
        self.propina_display.pack(pady=5)
        
        self.category_display = ttk.Label(result_frame, text="(Esperando cálculo)", 
                                        font=('Helvetica', 14), foreground='#666666')
        self.category_display.pack()
        
        # Gráficos
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(expand=True, fill=tk.BOTH, pady=20)
        
        self.fig = Figure(figsize=(10, 4), dpi=100, facecolor='#f5f5f5')
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        self.plot_membership_functions()
    
    def calculate_tip(self):
        try:
            servicio_val = round(self.servicio_var.get(), 2)
            comida_val = round(self.comida_var.get(), 2)
            
            # Inferencia difusa
            aggregated = self.fuzzy_system.infer(servicio_val, comida_val)
            
            # Defuzzificación
            tip = self.fuzzy_system.defuzzify(aggregated, method='lom')
            category = self.get_tip_category(tip)
            
            # Actualizar displays
            self.propina_display.config(text=f"{tip:.2f}%")
            self.category_display.config(text=f"({category})")
            
            # Nueva paleta de colores mejorada
            colors = {
                "Muy baja": '#E74C3C',  # Rojo vibrante
                "Baja": '#E67E22',      # Naranja
                "Media": '#F1C40F',     # Amarillo
                "Alta": '#2ECC71',      # Verde
                "Muy alta": '#9B59B6'   # Púrpura (reemplaza el azul)
            }
            color = colors.get(category, '#2ECC71')
            
            self.propina_display.config(foreground=color)
            self.category_display.config(foreground=color)
            
        except Exception as e:
            self.propina_display.config(text="Error", foreground='#E74C3C')
            self.category_display.config(text="(Verifique los valores)")
    
    def get_tip_category(self, value):
        # Usamos un enfoque con diccionario para evitar if-elif anidados
        categories = [
            (15, "Muy alta"),
            (14, "Alta"),
            (12, "Media"),
            (8, "Baja"),
            (1, "Muy baja"),
            (0, "Ninguna")
        ]
        
        for threshold, category in categories:
            if value > threshold:
                return category
        return "Ninguna"
    
    def show_rules(self):
        rules_window = tk.Toplevel(self)
        rules_window.title("Reglas de Inferencia Completas")
        rules_window.geometry("750x550")
    
        text_frame = ttk.Frame(rules_window)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                    padx=10, pady=10, font=('Courier', 10))
        text.pack(expand=True, fill=tk.BOTH)
        
        scrollbar.config(command=text.yview)
        
        rules_text = """
        REGLAS COMPLETAS DEL SISTEMA (5x5 = 25 reglas)
        
        [Servicio Excelente]
        1. Excelente + Excelente → Muy Alta (15%)
        2. Excelente + Bueno → Muy Alta (15%)
        3. Excelente + Regular → Alta (10-14%)
        4. Excelente + Mala → Media (6-10%)
        5. Excelente + Mediocre → Baja (2-6%)
        
        [Servicio Bueno]
        6. Bueno + Excelente → Muy Alta (15%)
        7. Bueno + Bueno → Alta (10-14%)
        8. Bueno + Regular → Media (6-10%)
        9. Bueno + Mala → Baja (2-6%)
        10. Bueno + Mediocre → Muy Baja (0-2%)
        
        [Servicio Regular]
        11. Regular + Excelente → Alta (10-14%)
        12. Regular + Bueno → Media (6-10%)
        13. Regular + Regular → Baja (2-6%)
        14. Regular + Mala → Muy Baja (0-2%)
        15. Regular + Mediocre → Muy Baja (0-2%)
        
        [Servicio Mala]
        16. Mala + Excelente → Media (6-10%)
        17. Mala + Bueno → Baja (2-6%)
        18. Mala + Regular → Muy Baja (0-2%)
        19. Mala + Mala → Muy Baja (0-2%)
        20. Mala + Mediocre → Muy Baja (0-2%)
        
        [Servicio Mediocre]
        21. Mediocre + Excelente → Baja (2-6%)
        22. Mediocre + Bueno → Muy Baja (0-2%)
        23. Mediocre + Regular → Muy Baja (0-2%)
        24. Mediocre + Mala → Muy Baja (0-2%)
        25. Mediocre + Mediocre → Muy Baja (0-2%)
        """
        
        text.insert(tk.END, rules_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(rules_window, text="Cerrar", command=rules_window.destroy).pack(pady=10)
    
    def plot_membership_functions(self):
        self.fig.clf()
        
        # Configurar estilo de los gráficos
        plt_style = {
            'axes.facecolor': '#ffffff',
            'axes.edgecolor': '#dddddd',
            'axes.grid': True,
            'grid.color': '#eeeeee',
            'axes.titlepad': 10,
            'axes.titlesize': 10,
            'axes.titleweight': 'bold'
        }
        
        for param, value in plt_style.items():
            matplotlib.rcParams[param] = value
        
        # Gráfico de servicio
        ax1 = self.fig.add_subplot(131)
        colors = ['#ff6b6b', '#ffa502', '#feca57', '#1dd1a1', '#2e86de']
        for i, (name, mf) in enumerate(self.fuzzy_system.servicio_terms.items()):
            ax1.plot(self.fuzzy_system.servicio_universe, mf, label=name, color=colors[i], linewidth=2)
        ax1.set_title('Servicio')
        ax1.legend(framealpha=0.9, facecolor='white')
        ax1.set_ylim(0, 1.1)
        ax1.set_facecolor('#f8f9fa')
        
        # Gráfico de comida
        ax2 = self.fig.add_subplot(132)
        for i, (name, mf) in enumerate(self.fuzzy_system.comida_terms.items()):
            ax2.plot(self.fuzzy_system.comida_universe, mf, label=name, color=colors[i], linewidth=2)
        ax2.set_title('Comida')
        ax2.legend(framealpha=0.9, facecolor='white')
        ax2.set_ylim(0, 1.1)
        ax2.set_facecolor('#f8f9fa')
        
        # Gráfico de propina
        ax3 = self.fig.add_subplot(133)
        propina_colors = ['#ff0000', '#ff6b6b', '#ff9f43', '#feca57', '#2ecc71', '#1a237e']
        for i, (name, mf) in enumerate(self.fuzzy_system.propina_terms.items()):
            ax3.plot(self.fuzzy_system.propina_universe, mf, label=name, color=propina_colors[i], linewidth=2)
        ax3.set_title('Propina')
        ax3.legend(framealpha=0.9, facecolor='white')
        ax3.set_ylim(0, 1.1)
        ax3.set_facecolor('#f8f9fa')
        
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

if __name__ == "__main__":
    app = PropinaApp()
    app.mainloop()