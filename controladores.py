import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import control
from control import tf, step_response, feedback
from scipy.signal import lsim as scipy_lsim
from matplotlib.ticker import AutoMinorLocator
from matplotlib.patches import Circle
import tkinter as tk
import platform

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Paleta de cores
CORES = {
    "primaria": "#1a4d8f",
    "primaria_hover": "#144173",
    "secundaria": "#2e7d32",
    "secundaria_hover": "#1b5e20",
    "terciaria": "#c62828",
    "terciaria_hover": "#8e0000",
    "fundo_escuro": "#1a1a2e",
    "fundo_claro": "#16213e",
    "texto_principal": "#e4e4e4",
    "texto_secundario": "#94a3b8",
    "acento": "#0f3460",
    "borda": "#2d3748",
    "sucesso": "#059669",
    "alerta": "#d97706",
    "erro": "#dc2626"
}

class JanelaControladores(ctk.CTkToplevel):
    """Janela de análise de controladores - Otimizada para Windows"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Detectar configurações do Windows
        self.is_windows = platform.system() == "Windows"
        self.dpi_scale = self.detectar_dpi_scale()
        
        # Configuração da janela
        self.title("ANÁLISE DE CONTROLADORES")
        self.configurar_tamanho_janela()
        self.resizable(True, True)
        self.configure(fg_color=CORES["fundo_escuro"])
        
        # Opção para tela cheia (descomente a linha abaixo para ativar)
        # self.state('zoomed')  # Windows
        # self.attributes('-fullscreen', True)  # Linux/Mac
        
        # Configuração específica para Windows
        if self.is_windows:
            try:
                # Habilita DPI awareness no Windows
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
            
            # Ícone (se disponível)
            try:
                self.iconbitmap(default='icon.ico')
            except:
                pass
        
        # Cores para gráficos
        self.graph_colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'tertiary': '#2ca02c',
            'quaternary': '#d62728',
            'background': '#ffffff',
            'grid': '#e0e0e0',
            'reference': '#ff4444',
            'input': '#6666ff',
            'stable': '#28a745',
            'unstable': '#dc3545',
            'zeros': '#6f42c1',
            'tolerance': '#ff6b6b',
            'settling': '#00b894',
            'peak': '#6c5ce7'
        }
        
        # Configurar estilo matplotlib com ajuste de DPI
        self.configurar_matplotlib()
        
        self.centralizar_janela()
        self.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.transient(self.parent)
        self.grab_set()
        self.focus_set()
        
        # Criar interface
        self.criar_cabecalho()
        self.criar_conteudo()
        
        # Ajustar após criar interface
        self.update_idletasks()
        
    def detectar_dpi_scale(self):
        """Detecta o fator de escala DPI do Windows"""
        try:
            if self.is_windows:
                from ctypes import windll
                hdc = windll.user32.GetDC(0)
                dpi = windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                windll.user32.ReleaseDC(0, hdc)
                return dpi / 96.0  # 96 DPI é 100%
        except:
            pass
        return 1.0
    
    def configurar_tamanho_janela(self):
        """Configura tamanho responsivo baseado na resolução da tela"""
        # Obter resolução da tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular tamanho ideal (80% da tela, mas não menor que mínimo)
        ideal_width = int(screen_width * 0.80)
        ideal_height = int(screen_height * 0.85)
        
        # Tamanhos mínimo e máximo
        min_width = 1000
        min_height = 700
        max_width = screen_width  # Máximo = largura da tela
        max_height = screen_height  # Máximo = altura da tela
        
        # Aplicar limites
        self.window_width = max(min_width, min(ideal_width, max_width))
        self.window_height = max(min_height, min(ideal_height, max_height))
        
        # Configurar tamanho mínimo
        self.minsize(min_width, min_height)
        
    def ativar_tela_cheia(self):
        """Ativa o modo tela cheia"""
        if self.is_windows:
            self.state('zoomed')  # Maximizado no Windows
        else:
            self.attributes('-fullscreen', True)  # Tela cheia no Linux/Mac
    
    def desativar_tela_cheia(self):
        """Desativa o modo tela cheia"""
        if self.is_windows:
            self.state('normal')
        else:
            self.attributes('-fullscreen', False)
        
    def configurar_matplotlib(self):
        """Configura matplotlib para renderização otimizada no Windows"""
        # Ajustar DPI baseado na escala do sistema
        base_dpi = 100
        adjusted_dpi = int(base_dpi / self.dpi_scale) if self.dpi_scale > 1 else base_dpi
        
        plt.rcParams['figure.dpi'] = adjusted_dpi
        plt.rcParams['savefig.dpi'] = adjusted_dpi
        
        # Configurações de fonte
        plt.rcParams['font.size'] = 9
        plt.rcParams['axes.titlesize'] = 11
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 8
        plt.rcParams['figure.titlesize'] = 12
        plt.rcParams['font.family'] = 'sans-serif'
        
        # Backend otimizado para Windows
        if self.is_windows:
            plt.rcParams['backend'] = 'TkAgg'
    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        
        # Obter dimensões da tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular posição central
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        
        # Garantir que não fique fora da tela
        x = max(0, x)
        y = max(0, y)
        
        self.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')
    
    def criar_cabecalho(self):
        """Cria o cabeçalho"""
        frame_cabecalho = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=70,
            corner_radius=0
        )
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame_cabecalho.grid_columnconfigure(1, weight=1)
        frame_cabecalho.grid_columnconfigure(2, weight=0)
        
        # Botão fechar
        botao_voltar = ctk.CTkButton(
            frame_cabecalho,
            text="← FECHAR",
            command=self.fechar_janela,
            width=110,
            height=38,
            font=("Segoe UI", 12, "bold"),
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"],
            corner_radius=8
        )
        botao_voltar.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # Botão tela cheia/normal
        self.botao_fullscreen = ctk.CTkButton(
            frame_cabecalho,
            text="⛶ TELA CHEIA",
            command=self.toggle_tela_cheia,
            width=130,
            height=38,
            font=("Segoe UI", 11, "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        )
        self.botao_fullscreen.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        self.fullscreen_ativo = False
        
        # Título
        label_titulo = ctk.CTkLabel(
            frame_cabecalho,
            text="ANÁLISE DE CONTROLADORES PI, PD E PID",
            font=("Segoe UI", 22, "bold"),
            text_color=CORES["texto_principal"]
        )
        label_titulo.grid(row=0, column=1, pady=15)
    
    def criar_conteudo(self):
        """Cria o conteúdo principal"""
        frame_conteudo = ctk.CTkFrame(self, fg_color=CORES["fundo_claro"])
        frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        frame_conteudo.grid_columnconfigure(1, weight=1)
        frame_conteudo.grid_rowconfigure(0, weight=1)
        
        # Painel de controle (esquerda)
        self.criar_painel_controle(frame_conteudo)
        
        # Área de gráficos (direita)
        self.criar_area_graficos(frame_conteudo)
    
    def criar_painel_controle(self, parent):
        """Cria o painel de controle lateral"""
        # Ajustar largura baseado no DPI
        panel_width = int(380 * self.dpi_scale)
        
        frame_scroll = ctk.CTkScrollableFrame(
            parent,
            width=panel_width,
            fg_color="transparent"
        )
        frame_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Frames
        self.criar_frame_sistema(frame_scroll)
        self.criar_frame_entrada(frame_scroll)
        self.criar_frame_controlador(frame_scroll)
        self.criar_botoes_acao(frame_scroll)
    
    def criar_frame_sistema(self, parent):
        """Frame de configuração do sistema"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 15))
        
        # Título
        ctk.CTkLabel(
            frame,
            text="FUNÇÃO DE TRANSFERÊNCIA",
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Numerador
        ctk.CTkLabel(
            frame,
            text="Numerador:",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        self.entrada_numerador = ctk.CTkEntry(
            frame,
            placeholder_text="Ex: 4",
            height=40,
            font=("Segoe UI", 11),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_numerador.insert(0, "4")
        
        ctk.CTkLabel(
            frame,
            text="Coeficientes separados por espaço",
            font=("Segoe UI", 9),
            text_color=CORES["texto_secundario"]
        ).pack(anchor="w", padx=20, pady=(0, 10))
        
        # Denominador
        ctk.CTkLabel(
            frame,
            text="Denominador:",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        self.entrada_denominador = ctk.CTkEntry(
            frame,
            placeholder_text="Ex: 1 0.8 4",
            height=40,
            font=("Segoe UI", 11),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_denominador.insert(0, "1 0.8 4")
        
        ctk.CTkLabel(
            frame,
            text="Coeficientes separados por espaço",
            font=("Segoe UI", 9),
            text_color=CORES["texto_secundario"]
        ).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Informação sobre o sistema padrão
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            info_frame,
            text="📊 Sistema padrão: G(s) = 4/(s² + 0.8s + 4)",
            font=("Segoe UI", 10, "bold"),
            text_color=CORES["sucesso"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text="ωn = 2 rad/s, ζ = 0.2 (Subamortecido)",
            font=("Segoe UI", 9),
            text_color=CORES["texto_secundario"]
        ).pack(anchor="w")
    
    def criar_frame_entrada(self, parent):
        """Frame de seleção do tipo de entrada"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            frame,
            text="⚡ TIPO DE ENTRADA",
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        self.tipo_entrada = ctk.StringVar(value="Degrau Unitário")
        
        ctk.CTkRadioButton(
            frame,
            text="Degrau Unitário",
            variable=self.tipo_entrada,
            value="Degrau Unitário",
            font=("Segoe UI", 11),
            text_color=CORES["texto_principal"],
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkRadioButton(
            frame,
            text="Rampa Unitária",
            variable=self.tipo_entrada,
            value="Rampa Unitária",
            font=("Segoe UI", 11),
            text_color=CORES["texto_principal"],
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(anchor="w", padx=20, pady=(5, 15))
    
    def criar_frame_controlador(self, parent):
        """Frame de configuração do controlador"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            frame,
            text="🎮 CONTROLADOR",
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            frame,
            text="Tipo:",
            font=("Segoe UI", 11, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=20, pady=(5, 5))
        
        self.tipo_controlador = ctk.CTkComboBox(
            frame,
            values=["PI", "PD", "PID"],
            height=38,
            font=("Segoe UI", 11),
            fg_color=CORES["fundo_claro"],
            button_color=CORES["primaria"],
            button_hover_color=CORES["primaria_hover"],
            border_color=CORES["borda"],
            command=self.atualizar_parametros_controlador
        )
        self.tipo_controlador.pack(fill="x", padx=20, pady=(0, 15))
        self.tipo_controlador.set("PI")
        
        self.frame_parametros = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_parametros.pack(fill="x", padx=20, pady=(0, 15))
        
        self.atualizar_parametros_controlador()
    
    def atualizar_parametros_controlador(self, event=None):
        """Atualiza os campos de parâmetros do controlador"""
        for widget in self.frame_parametros.winfo_children():
            widget.destroy()
        
        tipo = self.tipo_controlador.get()
        
        self.criar_campo_parametro(self.frame_parametros, "Kp:", "1.0", "kp")
        
        if tipo in ["PI", "PID"]:
            self.criar_campo_parametro(self.frame_parametros, "Ki:", "0.5", "ki")
        
        if tipo in ["PD", "PID"]:
            self.criar_campo_parametro(self.frame_parametros, "Kd:", "0.1", "kd")
    
    def criar_campo_parametro(self, parent, label, valor_padrao, nome):
        """Cria um campo de parâmetro"""
        frame_campo = ctk.CTkFrame(parent, fg_color="transparent")
        frame_campo.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            frame_campo,
            text=label,
            font=("Segoe UI", 11, "bold"),
            text_color=CORES["texto_principal"],
            width=40
        ).pack(side="left")
        
        entrada = ctk.CTkEntry(
            frame_campo,
            height=35,
            font=("Segoe UI", 11),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        entrada.pack(side="left", fill="x", expand=True, padx=(10, 0))
        entrada.insert(0, valor_padrao)
        
        setattr(self, f"entrada_{nome}", entrada)
    
    def criar_botoes_acao(self, parent):
        """Cria os botões de ação"""
        ctk.CTkButton(
            parent,
            text="▶ GERAR ANÁLISE COMPLETA",
            command=self.gerar_analise,
            height=50,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).pack(fill="x", pady=(10, 10))
        
        ctk.CTkButton(
            parent,
            text="🗑️ Limpar Tudo",
            command=self.limpar_tudo,
            height=45,
            font=("Segoe UI", 12, "bold"),
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"],
            corner_radius=8
        ).pack(fill="x")
    
    def criar_area_graficos(self, parent):
        """Cria a área de gráficos com tamanho responsivo"""
        frame_graficos = ctk.CTkFrame(parent, fg_color=CORES["acento"], corner_radius=10)
        frame_graficos.grid(row=0, column=1, sticky="nsew", pady=0)
        frame_graficos.grid_columnconfigure(0, weight=1)
        frame_graficos.grid_rowconfigure(0, weight=1)
        
        # Calcular largura do notebook baseado no tamanho da janela
        notebook_width = max(600, int((self.window_width - 450) * 0.95))
        
        self.notebook = ctk.CTkTabview(
            frame_graficos, 
            fg_color=CORES["fundo_claro"],
            segmented_button_fg_color=CORES["primaria"],
            segmented_button_selected_color=CORES["primaria_hover"],
            segmented_button_selected_hover_color=CORES["primaria_hover"],
            width=notebook_width
        )
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.notebook.add("📊 Resposta Temporal")
        self.notebook.add("🔍 Lugar das Raízes")
        self.notebook.add("⭕ Polos e Zeros")
        
        self.criar_aba_resposta()
        self.criar_aba_lgr()
        self.criar_aba_polos_zeros()
    
    def criar_aba_resposta(self):
        """Cria a aba de resposta temporal"""
        tab = self.notebook.tab("📊 Resposta Temporal")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=0)
        
        # Calcular DPI ajustado para gráficos
        graph_dpi = max(70, int(90 / self.dpi_scale))
        
        # Gráfico sem controlador
        frame_sem = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_sem.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))
        frame_sem.grid_columnconfigure(0, weight=1)
        frame_sem.grid_rowconfigure(1, weight=1)
        frame_sem.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            frame_sem,
            text="📈 SEM CONTROLADOR",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, pady=(8, 5), sticky="w", padx=10)
        
        self.fig_resp_sem = plt.Figure(figsize=(6, 4), dpi=graph_dpi)
        self.ax_resp_sem = self.fig_resp_sem.add_subplot(111)
        self.setup_plot_style(self.ax_resp_sem)
        
        self.canvas_resp_sem = FigureCanvasTkAgg(self.fig_resp_sem, master=frame_sem)
        self.canvas_resp_sem.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 5))
        
        toolbar_frame_sem = ctk.CTkFrame(frame_sem, fg_color="transparent")
        toolbar_frame_sem.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        toolbar_sem = NavigationToolbar2Tk(self.canvas_resp_sem, toolbar_frame_sem)
        self.configurar_toolbar(toolbar_sem)
        
        # Gráfico com controlador
        frame_com = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_com.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        frame_com.grid_columnconfigure(0, weight=1)
        frame_com.grid_rowconfigure(1, weight=1)
        frame_com.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            frame_com,
            text="📊 COM CONTROLADOR",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, pady=(8, 5), sticky="w", padx=10)
        
        self.fig_resp_com = plt.Figure(figsize=(6, 4), dpi=graph_dpi)
        self.ax_resp_com = self.fig_resp_com.add_subplot(111)
        self.setup_plot_style(self.ax_resp_com)
        
        self.canvas_resp_com = FigureCanvasTkAgg(self.fig_resp_com, master=frame_com)
        self.canvas_resp_com.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 5))
        
        toolbar_frame_com = ctk.CTkFrame(frame_com, fg_color="transparent")
        toolbar_frame_com.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        toolbar_com = NavigationToolbar2Tk(self.canvas_resp_com, toolbar_frame_com)
        self.configurar_toolbar(toolbar_com)

        # Frame de informações
        frame_info = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_info.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        self.label_info_resposta = ctk.CTkLabel(
            frame_info,
            text="🔎 Use os botões ⤭ (Zoom) e ✥ (Pan) para explorar os gráficos.",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        )
        self.label_info_resposta.pack(pady=8)
    
    def criar_aba_lgr(self):
        """Cria a aba de Lugar das Raízes"""
        tab = self.notebook.tab("🔍 Lugar das Raízes")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        graph_dpi = max(70, int(90 / self.dpi_scale))
        
        # LGR sem controlador
        frame_sem = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_sem.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        frame_sem.grid_columnconfigure(0, weight=1)
        frame_sem.grid_rowconfigure(1, weight=1)
        frame_sem.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            frame_sem,
            text="🔍 SEM CONTROLADOR",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, pady=(8, 5), sticky="w", padx=10)
        
        self.fig_lgr_sem = plt.Figure(figsize=(6, 4), dpi=graph_dpi)
        self.ax_lgr_sem = self.fig_lgr_sem.add_subplot(111)
        self.setup_plot_style(self.ax_lgr_sem)
        
        self.canvas_lgr_sem = FigureCanvasTkAgg(self.fig_lgr_sem, master=frame_sem)
        self.canvas_lgr_sem.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 5))
        
        toolbar_frame_lgr_sem = ctk.CTkFrame(frame_sem, fg_color="transparent")
        toolbar_frame_lgr_sem.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        toolbar_lgr_sem = NavigationToolbar2Tk(self.canvas_lgr_sem, toolbar_frame_lgr_sem)
        self.configurar_toolbar(toolbar_lgr_sem)

        # LGR com controlador
        frame_com = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_com.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        frame_com.grid_columnconfigure(0, weight=1)
        frame_com.grid_rowconfigure(1, weight=1)
        frame_com.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            frame_com,
            text="🎯 COM CONTROLADOR",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, pady=(8, 5), sticky="w", padx=10)
        
        self.fig_lgr_com = plt.Figure(figsize=(6, 4), dpi=graph_dpi)
        self.ax_lgr_com = self.fig_lgr_com.add_subplot(111)
        self.setup_plot_style(self.ax_lgr_com)
        
        self.canvas_lgr_com = FigureCanvasTkAgg(self.fig_lgr_com, master=frame_com)
        self.canvas_lgr_com.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 5))
        
        toolbar_frame_lgr_com = ctk.CTkFrame(frame_com, fg_color="transparent")
        toolbar_frame_lgr_com.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        toolbar_lgr_com = NavigationToolbar2Tk(self.canvas_lgr_com, toolbar_frame_lgr_com)
        self.configurar_toolbar(toolbar_lgr_com)
    
    def criar_aba_polos_zeros(self):
        """Cria a aba de Polos e Zeros"""
        tab = self.notebook.tab("⭕ Polos e Zeros")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=2)
        container.grid_rowconfigure(1, weight=0)
        container.grid_rowconfigure(2, weight=1)
        
        graph_dpi = max(70, int(90 / self.dpi_scale))
        
        # Gráfico
        frame_grafico = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_grafico.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        frame_grafico.grid_columnconfigure(0, weight=1)
        frame_grafico.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_grafico,
            text="🎯 DIAGRAMA DE POLOS E ZEROS (COM CONTROLADOR)",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, pady=(8, 5), sticky="w", padx=10)
        
        self.fig_pz = plt.Figure(figsize=(8, 5), dpi=graph_dpi)
        self.ax_pz = self.fig_pz.add_subplot(111)
        self.setup_plot_style(self.ax_pz)
        
        self.canvas_pz = FigureCanvasTkAgg(self.fig_pz, master=frame_grafico)
        self.canvas_pz.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        
        # Toolbar PZ
        toolbar_frame_pz = ctk.CTkFrame(container, fg_color="transparent")
        toolbar_frame_pz.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 8))
        toolbar_pz = NavigationToolbar2Tk(self.canvas_pz, toolbar_frame_pz)
        self.configurar_toolbar(toolbar_pz)

        # Informações
        frame_info = ctk.CTkFrame(container, fg_color=CORES["acento"], corner_radius=8)
        frame_info.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        frame_info.grid_columnconfigure(0, weight=1)
        frame_info.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_info,
            text="📋 INFORMAÇÕES DETALHADAS",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, pady=(8, 5), sticky="w", padx=10)
        
        self.texto_info = ctk.CTkTextbox(
            frame_info,
            font=("Consolas", 9),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1,
            height=120
        )
        self.texto_info.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.texto_info.insert("1.0", "Informações sobre polos e zeros aparecerão aqui...")
    
    def configurar_toolbar(self, toolbar):
        """Configura a toolbar do matplotlib para o tema dark"""
        toolbar.config(background=CORES["acento"])
        toolbar._message_label.config(
            background=CORES["acento"], 
            foreground=CORES["texto_principal"]
        )
        
        for widget in toolbar.winfo_children():
            if isinstance(widget, (tk.Button, tk.Checkbutton)):
                widget.config(
                    background=CORES["fundo_claro"], 
                    relief="flat", 
                    fg=CORES["texto_principal"], 
                    activeforeground=CORES["texto_principal"], 
                    activebackground=CORES["primaria"]
                )
        
        toolbar.update()
    
    def setup_plot_style(self, ax):
        """Configura o estilo dos gráficos para o tema dark"""
        ax.set_facecolor(CORES["fundo_claro"])
        ax.figure.set_facecolor(CORES["acento"])
        
        ax.tick_params(axis='both', which='major', colors=CORES["texto_principal"], labelsize=9)
        ax.title.set_color(CORES["texto_principal"])
        ax.xaxis.label.set_color(CORES["texto_principal"])
        ax.yaxis.label.set_color(CORES["texto_principal"])
        ax.xaxis.label.set_fontweight('bold')
        ax.yaxis.label.set_fontweight('bold')
        ax.title.set_fontweight('bold')
        
        for spine in ax.spines.values():
            spine.set_color(CORES["texto_secundario"])
            spine.set_linewidth(1.2)
        
        ax.grid(True, which='both', linestyle=':', linewidth=0.5, 
                color=CORES["texto_secundario"], alpha=0.3)
        
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(which='both', width=1)
        ax.tick_params(which='major', length=6)
        ax.tick_params(which='minor', length=3)
    
    def parse_coeficientes(self, texto):
        """Converte texto para lista de coeficientes"""
        try:
            if not texto.strip():
                raise ValueError("Campo vazio")
            return [float(x.strip()) for x in texto.split()]
        except ValueError:
            raise ValueError("Formato inválido. Use números separados por espaços.")
    
    def get_controlador_tf(self):
        """Retorna a função de transferência do controlador"""
        try:
            tipo = self.tipo_controlador.get()
            kp = float(self.entrada_kp.get())
            
            if tipo == "PI":
                ki = float(self.entrada_ki.get())
                return tf([kp, ki], [1, 0])
            
            elif tipo == "PD":
                kd = float(self.entrada_kd.get())
                return tf([kd, kp], [1])
            
            elif tipo == "PID":
                ki = float(self.entrada_ki.get())
                kd = float(self.entrada_kd.get())
                return tf([kd, kp, ki], [1, 0])
            
        except ValueError as e:
            raise ValueError(f"Valor inválido nos parâmetros do controlador: {str(e)}")
    
    def calcular_metricas_resposta(self, t, y, sys_cl):
        """Calcula todas as métricas de resposta ao degrau"""
        metricas = {}
        
        try:
            wn_damp, zeta_damp, _ = control.damp(sys_cl, doprint=False)
            
            if len(wn_damp) > 0:
                valid_wn = wn_damp[wn_damp > 1e-5]
                if len(valid_wn) > 0:
                    idx_dominante = np.argmin(valid_wn)
                    metricas['Wn'] = valid_wn[idx_dominante]
                    metricas['Zeta'] = zeta_damp[np.where(wn_damp == valid_wn[idx_dominante])[0][0]]
                else:
                    metricas['Wn'] = 0
                    metricas['Zeta'] = 0
            else:
                metricas['Wn'] = 0
                metricas['Zeta'] = 0

            y_final = y[-1]
            metricas['y_final'] = y_final
            
            y_pico = np.max(y)
            metricas['y_pico'] = y_pico
            metricas['Tp'] = t[np.argmax(y)]
            metricas['Mp'] = (y_pico - y_final) / y_final * 100 if abs(y_final) > 1e-6 else 0
            
            try:
                t_10 = t[np.where(y >= 0.1 * y_final)[0][0]]
                t_90 = t[np.where(y >= 0.9 * y_final)[0][0]]
                metricas['Tr'] = t_90 - t_10
            except IndexError:
                metricas['Tr'] = 0

            try:
                lim_sup = y_final * 1.02
                lim_inf = y_final * 0.98
                indices_fora_banda = np.where((y > lim_sup) | (y < lim_inf))[0]
                idx_ts = indices_fora_banda[-1]
                metricas['Ts'] = t[idx_ts + 1]
                metricas['y_Ts'] = y[idx_ts + 1]
            except IndexError:
                metricas['Ts'] = 0
                metricas['y_Ts'] = y_final

        except Exception as e:
            print(f"Erro ao calcular métricas: {e}")
            return {'y_final': 0, 'y_pico': 0, 'Tp': 0, 'Mp': 0, 'Tr': 0, 'Ts': 0, 'y_Ts': 0, 'Wn': 0, 'Zeta': 0}
            
        return metricas
    
    def plotar_resposta_completa(self, ax, t, y, metricas, titulo, cor, y_lim_top=None):
        """Plota o gráfico de resposta completo"""
        m = metricas
        zeta = m.get('Zeta', 0)
        ganho_k = m.get('y_final', 0)

        cor_plot = 'cyan' if cor == self.graph_colors['primary'] else 'orange'
        label_saida = f"Saída (Mp: {m.get('Mp', 0):.1f}%)"
        ax.plot(t, y, color=cor_plot, linewidth=2.5, label=label_saida, zorder=3)

        ax.plot(t, np.ones_like(t), color='yellow',
                   linewidth=1.5, linestyle='--', label='Referência', alpha=0.7, zorder=2)

        label_vf = f'Valor Final (K={ganho_k:.3f})'
        ax.axhline(y=m['y_final'], color='lime', linestyle=':',
                   linewidth=1.5, label=label_vf, alpha=0.8, zorder=2)

        if zeta >= 0 and m['y_final'] > 1e-6:
            y_sup_2 = m['y_final'] * 1.02
            y_inf_2 = m['y_final'] * 0.98
            ax.axhline(y=y_sup_2, color='orange', linestyle=':',
                      alpha=0.4, linewidth=0.8, label='Faixa ±2%', zorder=1)
            ax.axhline(y=y_inf_2, color='orange', linestyle=':',
                      alpha=0.4, linewidth=0.8, zorder=1)

        if 0 <= zeta < 1 and m.get('Mp', 0) > 0.1:
            tp = m.get('Tp', 0)
            y_pico = m.get('y_pico', m['y_final'])
            ax.plot(tp, y_pico, 'ro', markersize=7, label=f'Pico (Tp={tp:.3f}s)', zorder=4)
            ax.axhline(y=y_pico, color='red', linestyle=':', alpha=0.5, linewidth=1, zorder=1)
            ax.text(tp, y_pico * 1.02, f'Mp={m.get("Mp", 0):.1f}%',
                   color='red', fontsize=9, ha='center', va='bottom', fontweight='bold', zorder=5)

        ts_2 = m.get('Ts', 0)
        if ts_2 > 0 and zeta >= 0:
            y_ts2 = m.get('y_Ts', m['y_final'])
            ax.plot(ts_2, y_ts2, 'o', color='orange', markersize=7, label=f'Ts(2%)={ts_2:.2f}s', zorder=4)
            ax.axvline(x=ts_2, color='orange', linestyle='--',
                       alpha=0.6, linewidth=1.5, zorder=1)

        ax.set_title(titulo, fontsize=11, pad=10)
        ax.set_xlabel('Tempo (s)', fontsize=10, color=CORES["texto_principal"])
        ax.set_ylabel('Amplitude', fontsize=10, color=CORES["texto_principal"])

        legend = ax.legend(loc='best', fontsize=9, facecolor=CORES["fundo_claro"],
                           edgecolor=CORES["texto_secundario"], labelcolor=CORES["texto_principal"])
        if legend: legend.get_frame().set_alpha(0.85)

        y_top_limit = y_lim_top if y_lim_top is not None else max(1.1, m.get('y_pico', 1.0) * 1.15 if m.get('Mp',0) > 0.1 else 1.5)
        y_bottom_limit = min(0, np.min(y) * 1.1 if len(y) > 0 and np.min(y) < -1e-3 else 0)
        ax.set_ylim(bottom=y_bottom_limit, top=y_top_limit)
        ax.set_xlim(left=0, right=t[-1] if len(t) > 0 else 10)

        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
    
    def gerar_analise(self):
        """Gera a análise completa do sistema"""
        try:
            num = self.parse_coeficientes(self.entrada_numerador.get())
            den = self.parse_coeficientes(self.entrada_denominador.get())
            
            if not num or not den:
                raise ValueError("Numerador e denominador não podem estar vazios")
            
            G = tf(num, den)
            Gc = self.get_controlador_tf()
            
            self.gerar_resposta_temporal(G, Gc)
            self.gerar_lgr(G, Gc)
            self.gerar_polos_zeros(G, Gc)
            
        except Exception as e:
            self.mostrar_erro(str(e))
    
    def gerar_resposta_temporal(self, G, Gc):
        """Gera os gráficos de resposta temporal"""
        tipo_entrada = self.tipo_entrada.get()

        try:
            sys_sem_aberta = G
            sys_com_fechada = feedback(G * Gc, 1)
            sys_sem_fechada = feedback(G, 1)

            self.ax_resp_sem.clear()
            self.ax_resp_com.clear()

            self.setup_plot_style(self.ax_resp_sem)
            self.setup_plot_style(self.ax_resp_com)

            if tipo_entrada == "Degrau Unitário":
                t_final = 20
                t = np.linspace(0, t_final, 1000)

                t_sem, y_sem = step_response(sys_sem_aberta, T=t)
                t_com, y_com = step_response(sys_com_fechada, T=t)

                y_max_sem = np.max(y_sem) if len(y_sem) > 0 else 1.0
                y_max_com = np.max(y_com) if len(y_com) > 0 else 1.0
                y_max_global = max(1.1, y_max_sem * 1.1, y_max_com * 1.1)

                metricas_sem = self.calcular_metricas_resposta(t_sem, y_sem, sys_sem_fechada)
                metricas_com = self.calcular_metricas_resposta(t_com, y_com, sys_com_fechada)

                self.plotar_resposta_completa(
                    self.ax_resp_sem, t_sem, y_sem, metricas_sem,
                    'Resposta ao Degrau - Sistema Original (Malha Aberta)',
                    self.graph_colors['primary'],
                    y_lim_top=y_max_global
                )

                self.plotar_resposta_completa(
                    self.ax_resp_com, t_com, y_com, metricas_com,
                    'Resposta ao Degrau - Com Controlador (Malha Fechada)',
                    self.graph_colors['secondary'],
                    y_lim_top=y_max_global
                )

            else:  # Rampa Unitária
                t_final_rampa = 10
                t = np.linspace(0, t_final_rampa, 1000)
                u = t

                num_sem, den_sem = sys_sem_aberta.num[0][0], sys_sem_aberta.den[0][0]
                num_com, den_com = sys_com_fechada.num[0][0], sys_com_fechada.den[0][0]

                t_sem, y_sem, _ = scipy_lsim((num_sem, den_sem), U=u, T=t)
                t_com, y_com, _ = scipy_lsim((num_com, den_com), U=u, T=t)

                y_max_rampa_sem = np.max(y_sem) if len(y_sem) > 0 else t_final_rampa
                y_max_rampa_com = np.max(y_com) if len(y_com) > 0 else t_final_rampa
                y_max_global_rampa = max(t_final_rampa, y_max_rampa_sem, y_max_rampa_com) * 1.1

                self.ax_resp_sem.plot(t_sem, y_sem, linewidth=2.5, color=self.graph_colors['primary'], label='Saída')
                self.ax_resp_sem.plot(t_sem, u, '--', linewidth=1.5, color=CORES["texto_secundario"],
                                    alpha=0.8, label='Entrada (Rampa)')
                self.ax_resp_sem.set_title('Resposta à Rampa - Sistema Original (Malha Aberta)', fontsize=11)
                self.ax_resp_sem.set_xlabel('Tempo (s)', fontsize=10)
                self.ax_resp_sem.set_ylabel('Amplitude', fontsize=10)
                self.ax_resp_sem.set_ylim(bottom=0, top=y_max_global_rampa)
                self.ax_resp_sem.set_xlim(left=0, right=t_final_rampa)

                legend_sem = self.ax_resp_sem.legend(fontsize=9, loc='lower right')
                legend_sem.get_frame().set_facecolor(CORES["fundo_claro"])
                legend_sem.get_frame().set_edgecolor(CORES["texto_secundario"])
                legend_sem.get_frame().set_alpha(0.75)
                for text in legend_sem.get_texts():
                    text.set_color(CORES["texto_principal"])

                self.ax_resp_com.plot(t_com, y_com, linewidth=2.5, color=self.graph_colors['secondary'], label='Saída')
                self.ax_resp_com.plot(t_com, u, '--', linewidth=1.5, color=CORES["texto_secundario"],
                                    alpha=0.8, label='Entrada (Rampa)')
                self.ax_resp_com.set_title('Resposta à Rampa - Com Controlador (Malha Fechada)', fontsize=11)
                self.ax_resp_com.set_xlabel('Tempo (s)', fontsize=10)
                self.ax_resp_com.set_ylabel('Amplitude', fontsize=10)
                self.ax_resp_com.set_ylim(bottom=0, top=y_max_global_rampa)
                self.ax_resp_com.set_xlim(left=0, right=t_final_rampa)

                legend_com = self.ax_resp_com.legend(fontsize=9, loc='lower right')
                legend_com.get_frame().set_facecolor(CORES["fundo_claro"])
                legend_com.get_frame().set_edgecolor(CORES["texto_secundario"])
                legend_com.get_frame().set_alpha(0.75)
                for text in legend_com.get_texts():
                    text.set_color(CORES["texto_principal"])

            self.setup_plot_style(self.ax_resp_sem)
            self.setup_plot_style(self.ax_resp_com)
            
            try:
                 self.fig_resp_sem.tight_layout(pad=1.5)
                 self.fig_resp_com.tight_layout(pad=1.5)
            except:
                 pass

            self.canvas_resp_sem.draw()
            self.canvas_resp_com.draw()

        except Exception as e:
            print(f"Erro ao gerar resposta temporal: {e}")
            for ax in [self.ax_resp_sem, self.ax_resp_com]:
                ax.clear()
                self.setup_plot_style(ax)
                ax.text(0.5, 0.5, f'Erro: {str(e)}',
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=10, color=CORES["erro"])
            self.canvas_resp_sem.draw()
            self.canvas_resp_com.draw()
    
    def gerar_lgr(self, G, Gc):
        """Gera os gráficos de Lugar Geométrico das Raízes"""
        self.ax_lgr_sem.clear()
        self.ax_lgr_com.clear()
        
        try:
            control.rlocus(G, ax=self.ax_lgr_sem, grid=True)
            self.ax_lgr_sem.set_title('Lugar das Raízes - Sistema Original', fontsize=11, fontweight='bold')
            self.ax_lgr_sem.set_xlabel('Parte Real', fontsize=10, fontweight='bold')
            self.ax_lgr_sem.set_ylabel('Parte Imaginária', fontsize=10, fontweight='bold')
            self.ax_lgr_sem.grid(True, alpha=0.3)
            
            control.rlocus(G * Gc, ax=self.ax_lgr_com, grid=True)
            self.ax_lgr_com.set_title('Lugar das Raízes - Com Controlador', fontsize=11, fontweight='bold')
            self.ax_lgr_com.set_xlabel('Parte Real', fontsize=10, fontweight='bold')
            self.ax_lgr_com.set_ylabel('Parte Imaginária', fontsize=10, fontweight='bold')
            self.ax_lgr_com.grid(True, alpha=0.3)
            
        except Exception as e:
            self.ax_lgr_sem.text(0.5, 0.5, 'Erro ao gerar LGR\nTente outros parâmetros', 
                               ha='center', va='center', transform=self.ax_lgr_sem.transAxes)
            self.ax_lgr_com.text(0.5, 0.5, 'Erro ao gerar LGR\nTente outros parâmetros', 
                               ha='center', va='center', transform=self.ax_lgr_com.transAxes)
        
        self.setup_plot_style(self.ax_lgr_sem)
        self.setup_plot_style(self.ax_lgr_com)
        
        try:
            self.fig_lgr_sem.tight_layout(pad=3.0)
            self.fig_lgr_com.tight_layout(pad=3.0)
        except:
            pass
            
        self.canvas_lgr_sem.draw()
        self.canvas_lgr_com.draw()
    
    def gerar_polos_zeros(self, G, Gc):
        """Gera o gráfico de polos e zeros"""
        try:
            sys_com = feedback(G * Gc, 1)
            poles_com = control.poles(sys_com)
            zeros_com = control.zeros(sys_com)
            
            self.ax_pz.clear()
            
            if poles_com.size > 0:
                polos_estaveis = poles_com[poles_com.real < 0]
                polos_instaveis = poles_com[poles_com.real >= 0]
                
                if polos_estaveis.size > 0:
                    self.ax_pz.plot(polos_estaveis.real, polos_estaveis.imag, 'x', 
                                  markersize=12, markeredgewidth=3, 
                                  color=self.graph_colors['stable'], 
                                  label='Polos Estáveis')
                
                if polos_instaveis.size > 0:
                    self.ax_pz.plot(polos_instaveis.real, polos_instaveis.imag, 'x', 
                                  markersize=12, markeredgewidth=3,
                                  color=self.graph_colors['unstable'], 
                                  label='Polos Instáveis')
            
            if zeros_com.size > 0:
                self.ax_pz.plot(zeros_com.real, zeros_com.imag, 'o', markersize=10, 
                              markeredgewidth=2, fillstyle='none', 
                              color=self.graph_colors['zeros'], label='Zeros')
            
            self.ax_pz.axhline(0, color='black', linewidth=1, alpha=0.8)
            self.ax_pz.axvline(0, color='black', linewidth=1, alpha=0.8)
            
            xlim = self.ax_pz.get_xlim()
            ylim = self.ax_pz.get_ylim()
            
            if xlim[1] > 0:
                self.ax_pz.axvspan(0.001, xlim[1], color='#f8d7da', alpha=0.3, label='Região Instável')
            
            margin_x = max(0.5, (xlim[1] - xlim[0]) * 0.1)
            margin_y = max(0.5, (ylim[1] - ylim[0]) * 0.1)
            self.ax_pz.set_xlim(xlim[0] - margin_x, xlim[1] + margin_x)
            self.ax_pz.set_ylim(ylim[0] - margin_y, ylim[1] + margin_y)
            
            self.ax_pz.set_title('Diagrama de Polos e Zeros - Sistema Controlado', 
                               fontsize=11, fontweight='bold')
            self.ax_pz.set_xlabel('Parte Real', fontsize=10, fontweight='bold')
            self.ax_pz.set_ylabel('Parte Imaginária', fontsize=10, fontweight='bold')
            
            if poles_com.size > 0 or zeros_com.size > 0:
                self.ax_pz.legend(fontsize=9, loc='best')
            
            circle = Circle((0, 0), 1, fill=False, color='#6c757d', 
                          linestyle='--', alpha=0.4, linewidth=1)
            self.ax_pz.add_patch(circle)
            
            self.ax_pz.grid(True, alpha=0.3)
            
            self.setup_plot_style(self.ax_pz)
            
            try:
                self.fig_pz.tight_layout(pad=3.0)
            except:
                pass
                
            self.canvas_pz.draw()
            
            self.atualizar_info_pz(poles_com, zeros_com)
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao gerar polos e zeros: {str(e)}")
    
    def atualizar_info_pz(self, poles, zeros):
        """Atualiza as informações textuais de polos e zeros"""
        self.texto_info.delete("1.0", "end")
        
        self.texto_info.insert("end", "=" * 65 + "\n")
        self.texto_info.insert("end", "ANÁLISE DO SISTEMA COM CONTROLADOR\n")
        self.texto_info.insert("end", "=" * 65 + "\n\n")
        
        self.texto_info.insert("end", "🎯 POLOS DO SISTEMA:\n")
        self.texto_info.insert("end", "-" * 65 + "\n")
        
        polos_estaveis = 0
        polos_instaveis = 0
        
        if poles.size > 0:
            for i, p in enumerate(poles):
                parte_real = p.real
                parte_imag = p.imag
                
                if abs(parte_imag) < 1e-10:
                    info = f"Polo {i+1}: {parte_real:+.4f}"
                else:
                    if parte_imag >= 0:
                        info = f"Polo {i+1}: {parte_real:+.4f} + {parte_imag:.4f}j"
                    else:
                        info = f"Polo {i+1}: {parte_real:+.4f} - {abs(parte_imag):.4f}j"
                
                if parte_real < 0:
                    self.texto_info.insert("end", f"  ✓ {info} [ESTÁVEL]\n")
                    polos_estaveis += 1
                else:
                    self.texto_info.insert("end", f"  ✗ {info} [INSTÁVEL]\n")
                    polos_instaveis += 1
        else:
            self.texto_info.insert("end", "  Nenhum polo encontrado.\n")
        
        self.texto_info.insert("end", "\n🎯 ZEROS DO SISTEMA:\n")
        self.texto_info.insert("end", "-" * 65 + "\n")
        
        if zeros.size > 0:
            for i, z in enumerate(zeros):
                parte_real = z.real
                parte_imag = z.imag
                
                if abs(parte_imag) < 1e-10:
                    info = f"Zero {i+1}: {parte_real:+.4f}\n"
                else:
                    if parte_imag >= 0:
                        info = f"Zero {i+1}: {parte_real:+.4f} + {parte_imag:.4f}j\n"
                    else:
                        info = f"Zero {i+1}: {parte_real:+.4f} - {abs(parte_imag):.4f}j\n"
                
                self.texto_info.insert("end", f"  • {info}")
        else:
            self.texto_info.insert("end", "  Nenhum zero encontrado.\n")
        
        self.texto_info.insert("end", "\n📊 ANÁLISE DE ESTABILIDADE:\n")
        self.texto_info.insert("end", "=" * 65 + "\n")
        
        if poles.size > 0:
            if all(p.real < 0 for p in poles):
                self.texto_info.insert("end", "✅ Sistema ESTÁVEL\n")
                self.texto_info.insert("end", "   Todos os polos no semiplano esquerdo.\n")
            elif any(p.real > 0 for p in poles):
                self.texto_info.insert("end", "❌ Sistema INSTÁVEL\n")
                self.texto_info.insert("end", "   Há polos no semiplano direito.\n")
            else:
                self.texto_info.insert("end", "⚠️  Sistema MARGINALMENTE ESTÁVEL\n")
                self.texto_info.insert("end", "   Há polos no eixo imaginário.\n")
        
        self.texto_info.insert("end", "\n📌 RESUMO:\n")
        self.texto_info.insert("end", "-" * 65 + "\n")
        self.texto_info.insert("end", f"   Total de polos: {poles.size}\n")
        self.texto_info.insert("end", f"   Total de zeros: {zeros.size}\n")
        self.texto_info.insert("end", f"   Polos estáveis: {polos_estaveis}\n")
        self.texto_info.insert("end", f"   Polos instáveis: {polos_instaveis}\n")
        
        self.texto_info.insert("end", "\n" + "=" * 65 + "\n")
    
    def toggle_tela_cheia(self):
        """Alterna entre tela cheia e janela normal"""
        if self.fullscreen_ativo:
            self.desativar_tela_cheia()
            self.botao_fullscreen.configure(text="⛶ TELA CHEIA")
            self.fullscreen_ativo = False
        else:
            self.ativar_tela_cheia()
            self.botao_fullscreen.configure(text="⛶ SAIR TELA CHEIA")
            self.fullscreen_ativo = True
    
    def limpar_tudo(self):
        """Limpa todos os gráficos e campos"""
        for ax in [self.ax_resp_sem, self.ax_resp_com, 
                  self.ax_lgr_sem, self.ax_lgr_com, self.ax_pz]:
            ax.clear()
            self.setup_plot_style(ax)
        
        for canvas in [self.canvas_resp_sem, self.canvas_resp_com,
                      self.canvas_lgr_sem, self.canvas_lgr_com, self.canvas_pz]:
            canvas.draw()
        
        self.texto_info.delete("1.0", "end")
        self.texto_info.insert("1.0", "Informações sobre polos e zeros aparecerão aqui...")
        
        self.entrada_numerador.delete(0, "end")
        self.entrada_numerador.insert(0, "4")
        self.entrada_denominador.delete(0, "end")
        self.entrada_denominador.insert(0, "1 0.8 4")
        
        self.tipo_entrada.set("Degrau Unitário")
        self.tipo_controlador.set("PI")
        self.atualizar_parametros_controlador()
        
        self.mostrar_mensagem("Limpo", "Todos os dados foram limpos!")
    
    def mostrar_mensagem(self, titulo, mensagem):
        """Mostra uma mensagem de informação"""
        try:
            from CTkMessagebox import CTkMessagebox
            CTkMessagebox(title=titulo, message=mensagem, icon="check")
        except ImportError:
            from tkinter import messagebox
            messagebox.showinfo(titulo, mensagem)
    
    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        try:
            from CTkMessagebox import CTkMessagebox
            CTkMessagebox(title="Erro", message=mensagem, icon="cancel")
        except ImportError:
            from tkinter import messagebox
            messagebox.showerror("Erro", mensagem)
    
    def fechar_janela(self):
        """Fecha a janela de forma segura"""
        try:
            # Limpar figuras do matplotlib antes de fechar
            plt.close(self.fig_resp_sem)
            plt.close(self.fig_resp_com)
            plt.close(self.fig_lgr_sem)
            plt.close(self.fig_lgr_com)
            plt.close(self.fig_pz)
        except:
            pass
        
        self.destroy()


def abrir_analisador_controladores(parent_window):
    """
    Função para abrir o analisador de controladores
    
    Args:
        parent_window: Janela pai (do tela.py)
    
    Returns:
        Instância do JanelaControladores
    """
    return JanelaControladores(parent_window)


if __name__ == "__main__":
    import customtkinter as ctk
    
    # Configuração para Windows
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    root = ctk.CTk()
    root.withdraw()
    app = JanelaControladores(root)
    root.mainloop()