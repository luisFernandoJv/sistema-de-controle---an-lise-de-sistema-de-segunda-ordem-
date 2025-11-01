import customtkinter as ctk
from PIL import Image, ImageTk
import os
from criterios_estabilidade import CriteriosEstabilidade, ErroValidacao
from analise_segunda_ordem import AnalisadorSegundaOrdem, ErroValidacao as ErroValidacao2
from controladores import JanelaControladores
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import platform

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Paleta de cores educacional profissional
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

class ResponsiveConfig:
    """Classe para gerenciar configurações responsivas multiplataforma"""
    
    def __init__(self):
        self.platform = platform.system()
        self.is_windows = self.platform == "Windows"
        self.is_linux = self.platform == "Linux"
        
    def get_screen_info(self, root):
        """Obtém informações precisas da tela"""
        try:
            root.update_idletasks()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # Ajuste para diferentes DPIs
            if self.is_windows:
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    user32.SetProcessDPIAware()
                    screen_width = user32.GetSystemMetrics(0)
                    screen_height = user32.GetSystemMetrics(1)
                except:
                    pass
            
            return screen_width, screen_height
        except:
            return 1920, 1080  # Fallback
    
    def calculate_window_size(self, screen_width, screen_height, scale=0.8):
        """Calcula tamanho ideal da janela baseado na resolução"""
        # Tamanhos mínimos e máximos
        min_width, min_height = 1200, 700
        max_width, max_height = 1920, 1080
        
        # Calcular tamanho proporcional
        window_width = int(screen_width * scale)
        window_height = int(screen_height * scale)
        
        # Aplicar limites
        window_width = max(min_width, min(window_width, max_width))
        window_height = max(min_height, min(window_height, max_height))
        
        # Ajustes específicos para notebooks
        if screen_height <= 768:  # Notebooks com tela pequena
            window_height = min(window_height, 650)
            scale = 0.75
        elif screen_height <= 900:  # Notebooks médios
            window_height = min(window_height, 800)
            scale = 0.78
        
        return window_width, window_height
    
    def get_font_scale(self, screen_height):
        """Retorna escala de fonte baseada na altura da tela"""
        if screen_height <= 768:
            return 0.85
        elif screen_height <= 900:
            return 0.9
        elif screen_height <= 1080:
            return 1.0
        else:
            return 1.1
    
    def get_padding_scale(self, screen_width):
        """Retorna escala de padding baseada na largura da tela"""
        if screen_width <= 1366:
            return 0.7
        elif screen_width <= 1600:
            return 0.85
        else:
            return 1.0

class SistemaTCC(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicializar configuração responsiva
        self.config = ResponsiveConfig()
        
        # Configuração da janela principal
        self.title("FERRAMENTA COMPUTACIONAL PARA ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE")
        
        # Obter informações da tela
        self.screen_width, self.screen_height = self.config.get_screen_info(self)
        
        # Calcular tamanho da janela
        window_width, window_height = self.config.calculate_window_size(
            self.screen_width, self.screen_height
        )
        
        # Definir geometria
        self.geometry(f"{window_width}x{window_height}")
        
        # Configurações de tamanho
        self.maxsize(width=self.screen_width, height=self.screen_height)
        self.minsize(width=1000, height=600)
        
        # Aplicar cor de fundo
        self.configure(fg_color=CORES["fundo_escuro"])
        
        # Centralizar janela
        self.centralizar_janela()
        
        # Obter escalas responsivas
        self.font_scale = self.config.get_font_scale(self.screen_height)
        self.padding_scale = self.config.get_padding_scale(self.screen_width)
        
        # Carregar imagens
        self.carregar_imagens()
        
        # Configurar layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Criar container principal
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color=CORES["fundo_escuro"])
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Dicionário para rastrear janelas abertas
        self.janelas_abertas = {}
        
        # Criar tela principal
        self.tela_principal = TelaPrincipal(parent=self.container, controlador=self)
        self.tela_principal.grid(row=0, column=0, sticky="nsew")
        
        # Garantir visibilidade
        self.lift()
        self.focus_force()
        
        # Bind para redimensionamento
        self.bind("<Configure>", self.on_window_resize)
    
    def centralizar_janela(self):
        """Centraliza a janela na tela de forma robusta"""
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        
        # Garantir valores válidos
        if largura < 100:
            largura = 1200
        if altura < 100:
            altura = 700
        
        x = max(0, (self.screen_width - largura) // 2)
        y = max(0, (self.screen_height - altura) // 2)
        
        self.geometry(f'{largura}x{altura}+{x}+{y}')
    
    def on_window_resize(self, event):
        """Callback para redimensionamento da janela"""
        # Atualizar escalas quando a janela for redimensionada
        if event.widget == self:
            pass  # Pode adicionar lógica adicional se necessário
    
    def carregar_imagens(self):
        """Carrega as imagens utilizadas no sistema"""
        self.foto_fundo = None
        self.logo_image = None

        # Carregar Logo com tamanho responsivo
        try:
            if os.path.exists("logo.png"):
                img_pil = Image.open("logo.png").convert("RGBA")
                
                # Tamanho responsivo baseado na altura da tela
                if self.screen_height <= 768:
                    max_h_logo = 45
                elif self.screen_height <= 900:
                    max_h_logo = 50
                else:
                    max_h_logo = 60
                
                ratio = min(1.0, max_h_logo / img_pil.height)
                new_size = (int(img_pil.width * ratio), int(img_pil.height * ratio))
                img_pil_resized = img_pil.resize(new_size, Image.Resampling.LANCZOS)
                self.logo_image = ctk.CTkImage(light_image=img_pil_resized, 
                                              dark_image=img_pil_resized, 
                                              size=new_size)
        except Exception as e:
            print(f"Erro ao carregar logo.png: {e}")
            self.logo_image = None
    
    def scale_font(self, base_size):
        """Retorna tamanho de fonte escalado"""
        return int(base_size * self.font_scale)
    
    def scale_padding(self, base_padding):
        """Retorna padding escalado"""
        return int(base_padding * self.padding_scale)
    
    def abrir_janela(self, tipo_janela, titulo):
        """Abre uma nova janela com gerenciamento adequado"""
        # Fechar janela anterior do mesmo tipo se existir
        if tipo_janela in self.janelas_abertas:
            try:
                self.janelas_abertas[tipo_janela].destroy()
            except:
                pass
            finally:
                self.janelas_abertas.pop(tipo_janela, None)
        
        # Criar nova janela
        if tipo_janela == "criterio":
            janela = JanelaCriterio(self, titulo)
        elif tipo_janela == "analise":
            janela = JanelaAnalise(self, titulo)
        elif tipo_janela == "controladores":
            janela = JanelaControladores(self)
        else:
            return
        
        # Configurações para garantir visibilidade
        janela.transient(self)
        janela.grab_set()
        janela.lift()
        janela.focus_force()
        
        # Armazenar referência
        self.janelas_abertas[tipo_janela] = janela
        
        # Callback para limpar ao fechar
        def ao_fechar():
            self.janelas_abertas.pop(tipo_janela, None)
            janela.destroy()
            self.lift()
            self.focus_force()
        
        janela.protocol("WM_DELETE_WINDOW", ao_fechar)

class TelaPrincipal(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.criar_cabecalho()
        self.criar_conteudo_principal()
        self.criar_rodape()
    
    def criar_cabecalho(self):
        # Altura responsiva do cabeçalho
        header_height = 120 if self.controlador.screen_height <= 768 else 140
        
        frame_cabecalho = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=header_height,
            corner_radius=0
        )
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame_cabecalho.grid_columnconfigure(0, weight=1)
        frame_cabecalho.grid_rowconfigure(0, weight=1)
        
        padding_h = self.controlador.scale_padding(20)
        padding_v = self.controlador.scale_padding(15)
        
        container_principal = ctk.CTkFrame(frame_cabecalho, fg_color="transparent")
        container_principal.grid(row=0, column=0, sticky="nsew", padx=padding_h, pady=padding_v)
        container_principal.grid_columnconfigure(0, weight=3)
        container_principal.grid_columnconfigure(1, weight=1)
        
        # LADO ESQUERDO
        container_titulo = ctk.CTkFrame(container_principal, fg_color="transparent")
        container_titulo.grid(row=0, column=0, sticky="w", padx=0, pady=0)
        
        # Título responsivo
        titulo_size = self.controlador.scale_font(16)
        titulo_width = min(600, int(self.controlador.screen_width * 0.5))
        
        titulo_principal = ctk.CTkLabel(
            container_titulo,
            text="FERRAMENTA COMPUTACIONAL PARA ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE",
            font=("Segoe UI", titulo_size, "bold"),
            text_color=CORES["texto_principal"],
            wraplength=titulo_width,
            justify="left"
        )
        titulo_principal.pack(anchor="w", pady=(0, 5))
        
        linha_divisoria = ctk.CTkFrame(
            container_titulo,
            height=2,
            fg_color=CORES["primaria"],
            corner_radius=1
        )
        linha_divisoria.pack(fill="x", pady=6)
        
        subtitulo_size = self.controlador.scale_font(13)
        subtitulo = ctk.CTkLabel(
            container_titulo,
            text="Trabalho de Conclusão de Curso - Engenharia de Computação",
            font=("Segoe UI", subtitulo_size, "bold"),
            text_color=CORES["texto_secundario"]
        )
        subtitulo.pack(anchor="w", pady=(0, 5))
        
        # LADO DIREITO - LOGO
        container_logo = ctk.CTkFrame(container_principal, fg_color="transparent")
        container_logo.grid(row=0, column=1, sticky="e", padx=0, pady=0)
        
        container_logo_interno = ctk.CTkFrame(container_logo, fg_color="transparent")
        container_logo_interno.pack(expand=True, fill="y")
        
        if self.controlador.logo_image:
            logo_label = ctk.CTkLabel(
                container_logo_interno,
                image=self.controlador.logo_image,
                text=""
            )
            logo_label.pack(pady=(0, 5))
        
        inst_size = self.controlador.scale_font(10)
        texto_institucional = ctk.CTkLabel(
            container_logo_interno,
            text="UFERSA\nUniversidade Federal Rural do Semi-Árido",
            font=("Segoe UI", inst_size, "bold"),
            text_color=CORES["texto_secundario"],
            justify="center"
        )
        texto_institucional.pack()
    
    def criar_conteudo_principal(self):
        padding_h = self.controlador.scale_padding(40)
        padding_v = self.controlador.scale_padding(30)
        
        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.grid(row=1, column=0, sticky="nsew", padx=padding_h, pady=padding_v)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_rowconfigure(1, weight=1)
        
        frame_botoes = ctk.CTkFrame(
            frame_principal, 
            fg_color=CORES["fundo_claro"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["borda"]
        )
        frame_botoes.grid(row=0, column=0, pady=self.controlador.scale_padding(50), 
                         padx=self.controlador.scale_padding(20), sticky="n")
        
        titulo_size = self.controlador.scale_font(16)
        ctk.CTkLabel(
            frame_botoes,
            text="MÓDULOS DO SISTEMA",
            font=("Segoe UI", titulo_size, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(pady=(self.controlador.scale_padding(20), 10))
        
        subtitulo_size = self.controlador.scale_font(12)
        ctk.CTkLabel(
            frame_botoes,
            text="Selecione o módulo desejado para análise",
            font=("Segoe UI", subtitulo_size),
            text_color=CORES["texto_secundario"]
        ).pack(pady=(0, self.controlador.scale_padding(20)))
        
        # Botões responsivos
        button_width = min(400, int(self.controlador.screen_width * 0.3))
        button_height = 60 if self.controlador.screen_height <= 768 else 65
        button_font = self.controlador.scale_font(16)
        button_padding = self.controlador.scale_padding(12)
        
        informacoes_botoes = [
            {
                "texto": "📊 ANÁLISE DE ESTABILIDADE",
                "comando": lambda: self.controlador.abrir_janela("criterio", "ANÁLISE DE ESTABILIDADE"),
                "cor": CORES["primaria"],
                "cor_hover": CORES["primaria_hover"],
            },
            {
                "texto": "⚙️ ANÁLISE DE SISTEMA 2ª ORDEM", 
                "comando": lambda: self.controlador.abrir_janela("analise", "ANÁLISE DE SISTEMA 2ª ORDEM"),
                "cor": CORES["secundaria"],
                "cor_hover": CORES["secundaria_hover"],
            },
            {
                "texto": "📈 ANÁLISE DE CONTROLADORES",
                "comando": lambda: self.controlador.abrir_janela("controladores", "ANÁLISE DE CONTROLADORES"),
                "cor": CORES["terciaria"],
                "cor_hover": CORES["terciaria_hover"],
            }
        ]
        
        for info in informacoes_botoes:
            botao = ctk.CTkButton(
                frame_botoes,
                text=info["texto"],
                command=info["comando"],
                width=button_width,
                height=button_height,
                font=("Segoe UI", button_font, "bold"),
                corner_radius=10,
                fg_color=info["cor"],
                hover_color=info["cor_hover"],
                border_width=0,
                anchor="center"
            )
            botao.pack(pady=button_padding, padx=self.controlador.scale_padding(30))
    
    def criar_rodape(self):
        footer_height = 60 if self.controlador.screen_height <= 768 else 70
        
        frame_rodape = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=footer_height,
            corner_radius=0
        )
        frame_rodape.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        frame_rodape.grid_columnconfigure(0, weight=1)
        
        padding = self.controlador.scale_padding(15)
        container_rodape = ctk.CTkFrame(frame_rodape, fg_color="transparent")
        container_rodape.pack(fill="x", padx=self.controlador.scale_padding(20), pady=padding)
        
        font_size = self.controlador.scale_font(11)
        
        informacao_aluno = ctk.CTkLabel(
            container_rodape,
            text="Aluno: Luís Fernando Alexandre dos Santos | Orientador: Prof. Dr. Cecilio Martins de Sousa Neto",
            font=("Segoe UI", font_size),
            text_color=CORES["texto_secundario"]
        )
        informacao_aluno.pack(side="left")
        
        ano = ctk.CTkLabel(
            container_rodape,
            text="2025 - Universidade Federal Rural do Semi-Árido",
            font=("Segoe UI", font_size, "bold"),
            text_color=CORES["texto_secundario"]
        )
        ano.pack(side="right")

class JanelaBase(ctk.CTkToplevel):
    """Classe base otimizada para janelas secundárias"""
    def __init__(self, parent, titulo):
        super().__init__(parent)
        self.parent = parent
        self.titulo = titulo
        
        self.title(titulo)
        
        # Configuração responsiva
        config = ResponsiveConfig()
        screen_width, screen_height = config.get_screen_info(self)
        
        # Tamanho da janela secundária (um pouco maior que a principal)
        window_width, window_height = config.calculate_window_size(
            screen_width, screen_height, scale=0.88
        )
        
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(True, True)
        self.configure(fg_color=CORES["fundo_escuro"])
        
        # Escalas
        self.font_scale = config.get_font_scale(screen_height)
        self.padding_scale = config.get_padding_scale(screen_width)
        
        # Centralizar
        self.centralizar_janela()
        
        # Configurações de janela
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.grab_set()
        
        self.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.criar_cabecalho()
        self.criar_conteudo()
    
    def scale_font(self, base_size):
        return int(base_size * self.font_scale)
    
    def scale_padding(self, base_padding):
        return int(base_padding * self.padding_scale)
    
    def centralizar_janela(self):
        """Centraliza a janela secundária"""
        self.update_idletasks()
        
        x_pai = self.parent.winfo_x()
        y_pai = self.parent.winfo_y()
        largura_pai = self.parent.winfo_width()
        altura_pai = self.parent.winfo_height()
        
        largura = self.winfo_width()
        altura = self.winfo_height()
        
        if largura < 100:
            largura = 1200
        if altura < 100:
            altura = 800
        
        x = x_pai + (largura_pai - largura) // 2
        y = y_pai + (altura_pai - altura) // 2
        
        x = max(0, min(x, self.winfo_screenwidth() - largura))
        y = max(0, min(y, self.winfo_screenheight() - altura))
        
        self.geometry(f'{largura}x{altura}+{x}+{y}')
    
    def criar_cabecalho(self):
        header_height = 65 if self.winfo_screenheight() <= 768 else 70
        
        frame_cabecalho = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=header_height,
            corner_radius=0
        )
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame_cabecalho.grid_columnconfigure(1, weight=1)
        
        padding = self.scale_padding(20)
        
        botao_voltar = ctk.CTkButton(
            frame_cabecalho,
            text="← FECHAR",
            command=self.fechar_janela,
            width=110,
            height=38,
            font=("Segoe UI", self.scale_font(12), "bold"),
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"],
            corner_radius=8
        )
        botao_voltar.grid(row=0, column=0, sticky="w", padx=padding, pady=15)
        
        label_titulo = ctk.CTkLabel(
            frame_cabecalho,
            text=self.titulo,
            font=("Segoe UI", self.scale_font(22), "bold"),
            text_color=CORES["texto_principal"]
        )
        label_titulo.grid(row=0, column=1, pady=15)
    
    def criar_conteudo(self):
        pass
    
    def fechar_janela(self):
        """Fecha a janela com limpeza adequada"""
        try:
            self.grab_release()
        except:
            pass
        self.destroy()
        
        try:
            self.parent.lift()
            self.parent.focus_force()
        except:
            pass

class JanelaCriterio(JanelaBase):
    def __init__(self, parent, titulo):
        super().__init__(parent, titulo)
        self.numerador = []
        self.denominador = []
    
    def criar_conteudo(self):
        padding = self.scale_padding(20)
        
        frame_conteudo = ctk.CTkFrame(self, fg_color=CORES["fundo_claro"])
        frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=padding, pady=padding)
        frame_conteudo.grid_columnconfigure(0, weight=1)
        frame_conteudo.grid_rowconfigure(2, weight=1)
        
        # Frame de entrada
        frame_entrada = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_entrada.grid(row=0, column=0, sticky="ew", padx=padding, pady=padding)
        frame_entrada.grid_columnconfigure(1, weight=1)
        
        label_size = self.scale_font(14)
        entry_height = 40 if self.winfo_screenheight() <= 768 else 42
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Numerador:", 
            font=("Segoe UI", label_size, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=8, padx=15)
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 3 (para s + 3)",
            width=350,
            height=entry_height,
            font=("Segoe UI", self.scale_font(12)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=0, column=1, sticky="ew", padx=15, pady=8)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Coeficientes separados por espaço (do maior para o menor grau)",
            font=("Segoe UI", self.scale_font(10)),
            text_color=CORES["texto_secundario"]
        ).grid(row=1, column=1, sticky="w", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Denominador:", 
            font=("Segoe UI", label_size, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=2, column=0, sticky="w", pady=8, padx=15)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 5 6 (para s² + 5s + 6)",
            width=350,
            height=entry_height,
            font=("Segoe UI", self.scale_font(12)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=2, column=1, sticky="ew", padx=15, pady=8)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Coeficientes separados por espaço (do maior para o menor grau)",
            font=("Segoe UI", self.scale_font(10)),
            text_color=CORES["texto_secundario"]
        ).grid(row=3, column=1, sticky="w", padx=15, pady=(0, 15))
        
        # Botões
        frame_botoes = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_botoes.grid(row=1, column=0, sticky="w", padx=padding, pady=15)
        
        button_height = 46 if self.winfo_screenheight() <= 768 else 48
        
        ctk.CTkButton(
            frame_botoes, 
            text="Analisar Sistema Completo", 
            command=self.analisar_sistema_completo, 
            width=220,
            height=button_height,
            font=("Segoe UI", self.scale_font(13), "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes, 
            text="Critério Routh-Hurwitz", 
            command=self.analisar_routh_hurwitz, 
            width=200,
            height=button_height,
            font=("Segoe UI", self.scale_font(13), "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        # Frame de resultados
        frame_resultados = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_resultados.grid(row=2, column=0, sticky="nsew", padx=padding, pady=(0, padding))
        frame_resultados.grid_columnconfigure(0, weight=1)
        frame_resultados.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_resultados, 
            text="📋 Resultados da Análise:", 
            font=("Segoe UI", self.scale_font(16), "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=12, padx=15)
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados, 
            font=("Consolas", self.scale_font(11)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1
        )
        self.texto_resultados.grid(row=1, column=0, sticky="nsew", pady=(0, 15), padx=15)
        self.texto_resultados.insert("1.0", "Os resultados da análise aparecerão aqui...\n\n")
        self.texto_resultados.insert("end", "Exemplo de uso:\n")
        self.texto_resultados.insert("end", "• Numerador: 1 3\n")
        self.texto_resultados.insert("end", "• Denominador: 1 5 6\n")
        self.texto_resultados.insert("end", "→ Sistema: G(s) = (s + 3) / (s² + 5s + 6)")
    
    def obter_coeficientes(self):
        """Obtém e valida os coeficientes do usuário"""
        try:
            texto_num = self.entrada_numerador.get().strip()
            texto_den = self.entrada_denominador.get().strip()
            
            if not texto_num or not texto_den:
                raise ValueError("❌ Por favor, preencha ambos os campos:\n   • Numerador\n   • Denominador")
            
            try:
                numerador = [float(x) for x in texto_num.split()]
            except ValueError as e:
                raise ValueError(
                    f"❌ Erro no NUMERADOR!\n"
                    f"   Valor inserido: '{texto_num}'\n"
                    f"   Use apenas números separados por espaço.\n"
                    f"   Exemplo correto: 1 3 ou 2.5 4.2"
                )
            
            try:
                denominador = [float(x) for x in texto_den.split()]
            except ValueError as e:
                raise ValueError(
                    f"❌ Erro no DENOMINADOR!\n"
                    f"   Valor inserido: '{texto_den}'\n"
                    f"   Use apenas números separados por espaço.\n"
                    f"   Exemplo correto: 1 5 6 ou 2.5 4.2 8.1"
                )
            
            if len(numerador) == 0:
                raise ValueError("❌ Numerador não pode estar vazio!")
            
            if len(denominador) == 0:
                raise ValueError("❌ Denominador não pode estar vazio!")
            
            if abs(denominador[0]) < 1e-15:
                raise ValueError(
                    "❌ O primeiro coeficiente do DENOMINADOR não pode ser ZERO!\n"
                    f"   Valor inserido: {denominador}\n"
                    f"   O coeficiente do termo de maior grau deve ser diferente de zero.\n"
                    f"   Exemplo correto: 1 5 6 (não 0 5 6)"
                )
            
            if all(abs(c) < 1e-15 for c in denominador):
                raise ValueError(
                    "❌ O DENOMINADOR não pode ter todos os coeficientes iguais a ZERO!\n"
                    f"   Valor inserido: {denominador}"
                )
            
            return numerador, denominador
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"❌ Erro inesperado ao processar entrada: {str(e)}")
    
    def analisar_sistema_completo(self):
        try:
            numerador, denominador = self.obter_coeficientes()
            resultado = CriteriosEstabilidade.analisar_sistema_completo(numerador, denominador)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except (ValueError, ErroValidacao) as e:
            self.mostrar_erro(str(e))
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado: {str(e)}")
    
    def analisar_routh_hurwitz(self):
        try:
            numerador, denominador = self.obter_coeficientes()
            resultado = CriteriosEstabilidade.gerar_relatorio_routh_hurwitz(denominador)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except (ValueError, ErroValidacao) as e:
            self.mostrar_erro(str(e))
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado: {str(e)}")
    
    def mostrar_erro(self, mensagem):
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", f"{mensagem}\n\n")
        self.texto_resultados.insert("end", "=" * 60 + "\n")
        self.texto_resultados.insert("end", "DICAS PARA CORRIGIR:\n")
        self.texto_resultados.insert("end", "=" * 60 + "\n")
        self.texto_resultados.insert("end", "✓ Use apenas números (inteiros ou decimais)\n")
        self.texto_resultados.insert("end", "✓ Separe os coeficientes por ESPAÇO\n")
        self.texto_resultados.insert("end", "✓ Use ponto (.) para decimais, não vírgula\n")
        self.texto_resultados.insert("end", "✓ O primeiro coeficiente não pode ser ZERO\n")
        self.texto_resultados.insert("end", "✓ Digite os coeficientes do MAIOR para o MENOR grau\n\n")
        self.texto_resultados.insert("end", "Exemplos corretos:\n")
        self.texto_resultados.insert("end", "• Numerador: 1 3\n")
        self.texto_resultados.insert("end", "• Denominador: 1 5 6\n")

class JanelaAnalise(JanelaBase):
    def __init__(self, parent, titulo):
        super().__init__(parent, titulo)
        self.analisador = AnalisadorSegundaOrdem()
        self.canvas_grafico = None
    
    def criar_conteudo(self):
        padding = self.scale_padding(20)
        
        container_principal = ctk.CTkFrame(self, fg_color="transparent")
        container_principal.grid(row=1, column=0, sticky="nsew", padx=padding, pady=padding)
        container_principal.grid_columnconfigure(0, weight=0)
        container_principal.grid_columnconfigure(1, weight=1)
        container_principal.grid_rowconfigure(0, weight=1)
        
        # Largura responsiva do painel esquerdo
        screen_width = self.winfo_screenwidth()
        if screen_width <= 1366:
            panel_width = 380
        elif screen_width <= 1600:
            panel_width = 420
        else:
            panel_width = 450
        
        # PAINEL ESQUERDO
        frame_esquerdo = ctk.CTkFrame(
            container_principal, 
            fg_color=CORES["fundo_claro"],
            corner_radius=10,
            width=panel_width
        )
        frame_esquerdo.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        frame_esquerdo.grid_propagate(False)
        frame_esquerdo.grid_columnconfigure(0, weight=1)
        frame_esquerdo.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho esquerdo
        frame_cabecalho_esq = ctk.CTkFrame(frame_esquerdo, fg_color="transparent")
        frame_cabecalho_esq.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        ctk.CTkLabel(
            frame_cabecalho_esq,
            text="CONFIGURAÇÃO DO SISTEMA",
            font=("Segoe UI", self.scale_font(16), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w")
        
        # Container scrollável
        scroll_container = ctk.CTkScrollableFrame(
            frame_esquerdo,
            fg_color="transparent",
            height=600
        )
        scroll_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        scroll_container.grid_columnconfigure(0, weight=1)
        
        # Frame de configurações
        frame_configuracoes = ctk.CTkFrame(
            scroll_container,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_configuracoes.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        frame_configuracoes.grid_columnconfigure(0, weight=1)
        frame_configuracoes.grid_columnconfigure(1, weight=1)
        
        # Tipo de Malha
        frame_malha = ctk.CTkFrame(frame_configuracoes, fg_color="transparent")
        frame_malha.grid(row=0, column=0, sticky="ew", pady=15, padx=15)
        
        ctk.CTkLabel(
            frame_malha,
            text="🔄 Tipo de Sistema:",
            font=("Segoe UI", self.scale_font(14), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 8))
        
        self.tipo_malha = ctk.StringVar(value="fechada")
        
        ctk.CTkRadioButton(
            frame_malha,
            text="Malha Fechada",
            variable=self.tipo_malha,
            value="fechada",
            font=("Segoe UI", self.scale_font(12), "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(anchor="w", pady=4)
        
        ctk.CTkRadioButton(
            frame_malha,
            text="Malha Aberta",
            variable=self.tipo_malha,
            value="aberta",
            font=("Segoe UI", self.scale_font(12), "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(anchor="w", pady=4)
        
        # Tipo de Entrada
        frame_entrada_tipo = ctk.CTkFrame(frame_configuracoes, fg_color="transparent")
        frame_entrada_tipo.grid(row=0, column=1, sticky="ew", pady=15, padx=15)
        
        ctk.CTkLabel(
            frame_entrada_tipo,
            text="🔥 Tipo de Entrada:",
            font=("Segoe UI", self.scale_font(14), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 8))
        
        self.tipo_entrada = ctk.StringVar(value="degrau")
        
        ctk.CTkRadioButton(
            frame_entrada_tipo,
            text="Degrau Unitário",
            variable=self.tipo_entrada,
            value="degrau",
            font=("Segoe UI", self.scale_font(12), "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(anchor="w", pady=4)
        
        ctk.CTkRadioButton(
            frame_entrada_tipo,
            text="Rampa Unitária",
            variable=self.tipo_entrada,
            value="rampa",
            font=("Segoe UI", self.scale_font(12), "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(anchor="w", pady=4)
        
        # Área de entrada da função de transferência
        frame_entrada = ctk.CTkFrame(
            scroll_container,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_entrada.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        frame_entrada.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_entrada,
            text="📐 Função de Transferência de 2ª Ordem:",
            font=("Segoe UI", self.scale_font(14), "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=12, padx=15)
        
        # Numerador
        ctk.CTkLabel(
            frame_entrada, 
            text="Numerador:", 
            font=("Segoe UI", self.scale_font(12), "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=1, column=0, sticky="w", pady=5, padx=15)
        
        entry_height = 34 if self.winfo_screenheight() <= 768 else 36
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 4",
            height=entry_height,
            font=("Segoe UI", self.scale_font(11)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        # Denominador
        ctk.CTkLabel(
            frame_entrada, 
            text="Denominador:", 
            font=("Segoe UI", self.scale_font(12), "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=3, column=0, sticky="w", pady=5, padx=15)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 2 4",
            height=entry_height,
            font=("Segoe UI", self.scale_font(11)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Botões de ação
        frame_botoes = ctk.CTkFrame(frame_entrada, fg_color="transparent")
        frame_botoes.grid(row=5, column=0, pady=(5, 15), padx=15)
        
        button_height = 43 if self.winfo_screenheight() <= 768 else 45
        
        ctk.CTkButton(
            frame_botoes,
            text="▶ Analisar Sistema",
            command=self.analisar_sistema,
            width=180,
            height=button_height,
            font=("Segoe UI", self.scale_font(13), "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes,
            text="📊 Plotar Gráfico",
            command=self.plotar_grafico,
            width=160,
            height=button_height,
            font=("Segoe UI", self.scale_font(13), "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        # Área de resultados
        frame_resultados = ctk.CTkFrame(
            scroll_container,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_resultados.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        frame_resultados.grid_columnconfigure(0, weight=1)
        frame_resultados.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_resultados,
            text="📊 Resultados da Análise:",
            font=("Segoe UI", self.scale_font(14), "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=10, padx=15)
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados,
            font=("Consolas", self.scale_font(10)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1,
            wrap="word",
            height=300
        )
        self.texto_resultados.grid(row=1, column=0, sticky="nsew", pady=(0, 12), padx=12)
        self.texto_resultados.insert("1.0", "📝 INSTRUÇÕES:\n\n")
        self.texto_resultados.insert("end", "1. Configure o tipo de malha e entrada\n")
        self.texto_resultados.insert("end", "2. Digite os coeficientes:\n")
        self.texto_resultados.insert("end", "   • Numerador: Ex: 4\n")
        self.texto_resultados.insert("end", "   • Denominador: Ex: 1 2 4\n\n")
        self.texto_resultados.insert("end", "3. Clique em 'Analisar Sistema'\n")
        self.texto_resultados.insert("end", "4. Clique em 'Plotar Gráfico' para visualizar\n")
        
        # PAINEL DIREITO - Gráfico
        frame_direito = ctk.CTkFrame(
            container_principal,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_direito.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        frame_direito.grid_columnconfigure(0, weight=1)
        frame_direito.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_direito,
            text="📈 Gráfico da Resposta Temporal",
            font=("Segoe UI", self.scale_font(16), "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=15, padx=20)
        
        self.frame_grafico = ctk.CTkFrame(
            frame_direito,
            fg_color=CORES["fundo_claro"],
            corner_radius=10
        )
        self.frame_grafico.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.frame_grafico.grid_columnconfigure(0, weight=1)
        self.frame_grafico.grid_rowconfigure(0, weight=1)
        
        self.grafico_container = ctk.CTkFrame(
            self.frame_grafico, 
            fg_color=CORES["fundo_claro"]
        )
        self.grafico_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.grafico_container.grid_columnconfigure(0, weight=1)
        self.grafico_container.grid_rowconfigure(0, weight=1)
        
        self.label_sem_grafico = ctk.CTkLabel(
            self.grafico_container,
            text="📊\n\nClique em 'Plotar Gráfico'\npara visualizar a resposta temporal",
            font=("Segoe UI", self.scale_font(14)),
            text_color=CORES["texto_secundario"],
            justify="center"
        )
        self.label_sem_grafico.grid(row=0, column=0, sticky="")
    
    def obter_coeficientes(self):
        """Obtém e valida os coeficientes do usuário"""
        try:
            texto_num = self.entrada_numerador.get().strip()
            texto_den = self.entrada_denominador.get().strip()
            
            if not texto_num or not texto_den:
                raise ValueError("❌ Por favor, preencha ambos os campos:\n   • Numerador\n   • Denominador")
            
            try:
                numerador = [float(x) for x in texto_num.split()]
            except ValueError:
                raise ValueError(
                    f"❌ Erro no NUMERADOR!\n"
                    f"   Valor inserido: '{texto_num}'\n"
                    f"   Use apenas números separados por espaço.\n"
                    f"   Exemplo correto: 4 ou 2.5"
                )
            
            try:
                denominador = [float(x) for x in texto_den.split()]
            except ValueError:
                raise ValueError(
                    f"❌ Erro no DENOMINADOR!\n"
                    f"   Valor inserido: '{texto_den}'\n"
                    f"   Use apenas números separados por espaço.\n"
                    f"   Exemplo correto: 1 2 4 ou 1.5 3.2 5.8"
                )
            
            if len(denominador) != 3:
                raise ValueError(
                    f"❌ Sistema deve ser de 2ª ORDEM!\n"
                    f"   O denominador deve ter EXATAMENTE 3 coeficientes.\n"
                    f"   Você forneceu {len(denominador)} coeficiente(s): {denominador}\n"
                    f"   Formato correto: a₀s² + a₁s + a₂\n"
                    f"   Exemplo: 1 2 4 (representa s² + 2s + 4)"
                )
            
            if abs(denominador[0]) < 1e-15:
                raise ValueError(
                    "❌ O primeiro coeficiente do DENOMINADOR não pode ser ZERO!\n"
                    f"   Valor inserido: {denominador}\n"
                    f"   O coeficiente de s² deve ser diferente de zero.\n"
                    f"   Exemplo correto: 1 2 4 (não 0 2 4)"
                )
            
            if all(abs(c) < 1e-15 for c in denominador):
                raise ValueError(
                    "❌ O DENOMINADOR não pode ter todos os coeficientes iguais a ZERO!\n"
                    f"   Valor inserido: {denominador}"
                )
            
            if len(numerador) == 0:
                raise ValueError("❌ Numerador não pode estar vazio!")
            
            return numerador, denominador
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"❌ Erro inesperado ao processar entrada: {str(e)}")
    
    def analisar_sistema(self):
        """Realiza a análise completa do sistema"""
        try:
            numerador, denominador = self.obter_coeficientes()
            tipo_malha = self.tipo_malha.get()
            tipo_entrada = self.tipo_entrada.get()
            
            resultado = self.analisador.analisar_de_funcao_transferencia(
                numerador, 
                denominador, 
                tipo_malha, 
                tipo_entrada
            )
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except (ValueError, ErroValidacao2) as e:
            self.mostrar_erro(str(e))
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado: {str(e)}")
    
    def plotar_grafico(self):
        """Plota o gráfico da resposta temporal"""
        try:
            numerador, denominador = self.obter_coeficientes()
            tipo_malha = self.tipo_malha.get()
            tipo_entrada = self.tipo_entrada.get()
            
            wn, zeta, ganho = self.analisador.extrair_parametros_de_funcao(
                numerador, denominador, tipo_malha
            )
            
            self.analisador.wn = wn
            self.analisador.zeta = zeta
            self.analisador.ganho = ganho
            self.analisador.tipo_malha = tipo_malha
            self.analisador.tipo_entrada = tipo_entrada
            self.analisador.numerador = numerador
            self.analisador.denominador = denominador
            
            if self.canvas_grafico:
                self.canvas_grafico.get_tk_widget().destroy()
                self.canvas_grafico = None
            
            if self.label_sem_grafico:
                self.label_sem_grafico.destroy()
                self.label_sem_grafico = None
            
            fig = self.analisador.plotar_resposta()
            
            if fig:
                self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.grafico_container)
                self.canvas_grafico.draw()
                
                canvas_widget = self.canvas_grafico.get_tk_widget()
                canvas_widget.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
                canvas_widget.grid_propagate(True)
                
                plt.close(fig)
            
        except (ValueError, ErroValidacao2) as e:
            self.mostrar_erro(str(e))
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado ao plotar: {str(e)}")
    
    def mostrar_erro(self, mensagem):
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", f"{mensagem}\n\n")
        self.texto_resultados.insert("end", "=" * 60 + "\n")
        self.texto_resultados.insert("end", "DICAS PARA CORRIGIR:\n")
        self.texto_resultados.insert("end", "=" * 60 + "\n")
        self.texto_resultados.insert("end", "✓ Use apenas números (inteiros ou decimais)\n")
        self.texto_resultados.insert("end", "✓ Separe os coeficientes por ESPAÇO\n")
        self.texto_resultados.insert("end", "✓ Use ponto (.) para decimais, não vírgula\n")
        self.texto_resultados.insert("end", "✓ O primeiro coeficiente não pode ser ZERO\n")
        self.texto_resultados.insert("end", "✓ Denominador deve ter EXATAMENTE 3 coeficientes\n")
        self.texto_resultados.insert("end", "✓ Digite os coeficientes do MAIOR para o MENOR grau\n\n")
        self.texto_resultados.insert("end", "Exemplos corretos para sistema de 2ª ordem:\n")
        self.texto_resultados.insert("end", "• Numerador: 4\n")
        self.texto_resultados.insert("end", "• Denominador: 1 2 4\n")
        self.texto_resultados.insert("end", "  (representa: G(s) = 4 / (s² + 2s + 4))\n")

# Executar a aplicação
if __name__ == "__main__":
    app = SistemaTCC()
    app.mainloop()