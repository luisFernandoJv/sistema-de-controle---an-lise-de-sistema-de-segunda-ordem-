import customtkinter as ctk
from PIL import Image, ImageTk
import os
import warnings
from criterios_estabilidade import CriteriosEstabilidade, ErroValidacao
from analise_segunda_ordem import AnalisadorSegundaOrdem, ErroValidacao as ErroValidacao2
from controladores import JanelaControladores
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import control.matlab as matlab
import numpy as np
import platform
import sys
import json
import threading
import queue
from logger_sistema import logger  # import logger
from gerenciador_excecoes import gerenciador_excecoes, TipoErro, GerenciadorExcecoes  # import exception handler
from utilidades_ui import GerenciadorResponsividade, UtiliadadesGraficos  # import UI utilities
from lugar_geometrico_raizes import AnalisadorLGR, ErroValidacaoLGR
from tema_config import GerenciadorTemas, gerenciador_temas

CORES = gerenciador_temas.obter_cores()

# Configuração do tema inicial
ctk.set_appearance_mode(CORES["mode"])
ctk.set_default_color_theme("blue")


class GerenciadorTemas:
    """Gerencia temas claro e escuro com persistência"""
    
    TEMAS = {
        "dark": {
            "mode": "dark",
            "primaria": "#1a4d8f",
            "primaria_hover": "#144173",
            "secundaria": "#2e7d32",
            "secundaria_hover": "#1e5021",
            "terciaria": "#c62828",
            "terciaria_hover": "#8e0000",
            "quarto": "#9333ea",
            "quarto_hover": "#7e22ce",
            "fundo_escuro": "#1a1a2e",
            "fundo_claro": "#16213e",
            "texto_principal": "#fcfcfc",
            "texto_secundario": "#f9f9f9",
            "acento": "#0f3460",
            "borda": "#2d3748",
            "sucesso": "#059669",
            "alerta": "#d97706",
            "erro": "#dc2626"
        },
        "light": {
            "mode": "light",
            "primaria": "#2563eb",
            "primaria_hover": "#1d4ed8",
            "secundaria": "#1e5021",
            "secundaria_hover": "#15803d",
            "terciaria": "#dc2626",
            "terciaria_hover": "#b91c1c",
            "quarto": "#9333ea",
            "quarto_hover": "#7e22ce",
            "fundo_escuro": "#f8fafc",
            "fundo_claro": "#ffffff",
            "texto_principal": "#000000",
            "texto_secundario": "#313335",
            "acento": "#e2e8f0",
            "borda": "#cbd5e1",
            "sucesso": "#10b981",
            "alerta": "#f59e0b",
            "erro": "#ef4444"
        },
        "high_contrast": {
            "mode": "dark",
            "primaria": "#0066ff",
            "primaria_hover": "#0052cc",
            "secundaria": "#00ff00",
            "secundaria_hover": "#00cc00",
            "terciaria": "#ff0000",
            "terciaria_hover": "#cc0000",
            "quarto": "#9333ea",
            "quarto_hover": "#7e22ce",
            "fundo_escuro": "#000000",
            "fundo_claro": "#1a1a1a",
            "texto_principal": "#ffffff",
            "texto_secundario": "#ffff00",
            "acento": "#333333",
            "borda": "#ffffff",
            "sucesso": "#00ff00",
            "alerta": "#ffff00",
            "erro": "#ff0000"
        }
    }
    
    def __init__(self):
        self.tema_atual = "dark"
        self.config_file = "config_tema.json"
        self.carregar_configuracao()
    
    def carregar_configuracao(self):
        """Carrega configuração salva"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.tema_atual = config.get('tema', 'dark')
        except:
            self.tema_atual = "dark"
    
    def salvar_configuracao(self):
        """Salva configuração atual"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'tema': self.tema_atual}, f)
        except:
            pass
    
    def alternar_tema(self):
        """Alterna entre temas"""
        temas_disponiveis = list(self.TEMAS.keys())
        idx_atual = temas_disponiveis.index(self.tema_atual)
        idx_proximo = (idx_atual + 1) % len(temas_disponiveis)
        self.tema_atual = temas_disponiveis[idx_proximo]
        self.salvar_configuracao()
        return self.tema_atual
    
    def definir_tema(self, nome_tema):
        """Define um tema específico"""
        if nome_tema in self.TEMAS:
            self.tema_atual = nome_tema
            self.salvar_configuracao()
            return True
        return False
    
    def obter_cores(self):
        """Retorna as cores do tema atual"""
        return self.TEMAS[self.tema_atual]
    
    def obter_nome_tema(self):
        """Retorna nome amigável do tema"""
        nomes = {
            "dark": "Escuro",
            "light": "Claro",
            "high_contrast": "Alto Contraste"
        }
        return nomes.get(self.tema_atual, "Escuro")

gerenciador_temas = GerenciadorTemas()
CORES = gerenciador_temas.obter_cores()

# Configuração do tema inicial
ctk.set_appearance_mode(CORES["mode"])
ctk.set_default_color_theme("blue")


class GerenciadorExcecoes:
    """Novo sistema centralizado de tratamento de exceções"""
    
    def __init__(self):
        self.historico_erros = []
        self.max_historico = 100
    
    def registrar_erro(self, tipo, mensagem, contexto=None):
        """Registra erro para debug e análise"""
        import datetime
        registro = {
            "timestamp": datetime.datetime.now().isoformat(),
            "tipo": tipo,
            "mensagem": mensagem,
            "contexto": contexto
        }
        self.historico_erros.append(registro)
        if len(self.historico_erros) > self.max_historico:
            self.historico_erros.pop(0)
    
    def obter_ultimo_erro(self):
        """Retorna o último erro registrado"""
        if self.historico_erros:
            return self.historico_erros[-1]
        return None
    
    def limpar_historico(self):
        """Limpa histórico de erros"""
        self.historico_erros = []

gerenciador_excecoes = GerenciadorExcecoes()

class TransicaoSuave:
    """Sistema de transições suaves entre telas com efeitos visuais"""
    
    def __init__(self, duracao_ms=300):
        self.duracao = duracao_ms
        self.em_transicao = False
    
    def animar_entrada(self, widget, callback=None):
        """Anima entrada de widget"""
        if self.em_transicao:
            return
        
        self.em_transicao = True
        widget.configure(fg_color="transparent")
        
        passos = 10
        delay = self.duracao // passos
        
        def animar(passo):
            if passo < passos:
                widget.update()
                widget.after(delay, lambda: animar(passo + 1))
            else:
                self.em_transicao = False
                if callback:
                    callback()
        
        animar(0)

transicao = TransicaoSuave()

class ResponsiveConfig:
    """Classe para gerenciar configurações responsivas multiplataforma"""
    
    def __init__(self):
        self.platform = platform.system()
        self.is_windows = self.platform == "Windows"
        self.is_linux = self.platform == "Linux"
        self.is_mac = self.platform == "Darwin"
        
        self.dpi_scale = self.get_dpi_scale()
        self.scaling_factor = self.get_scaling_factor()
        
        self.config_acessibilidade = {
            "tamanho_fonte_aumentado": False,
            "alto_contraste": False,
            "animacoes_reduzidas": False,
            "leitor_tela": False
        }
    
    def get_dpi_scale(self):
        """Detecta o fator de escala DPI do sistema"""
        try:
            if self.is_windows:
                from ctypes import windll
                try:
                    windll.shcore.SetProcessDPIAware()
                    hdc = windll.user32.GetDC(0)
                    dpi = windll.gdi32.GetDeviceCaps(hdc, 88)
                    windll.user32.ReleaseDC(0, hdc)
                    return dpi / 96.0
                except:
                    return 1.0
            elif self.is_mac:
                # macOS geralmente usa Retina (2x)
                return 2.0 if 'retina' in str(sys.platform).lower() else 1.0
            else:
                # Linux - tentar detectar via Xrandr
                try:
                    import subprocess
                    output = subprocess.check_output(['xrandr']).decode()
                    if 'current' in output:
                        return 1.0
                except:
                    pass
        except:
            pass
        return 1.0
    
    def get_scaling_factor(self):
        """Retorna fator de escala baseado no sistema"""
        if self.is_mac:
            return 1.2  # macOS precisa de ajuste
        elif self.is_linux:
            return 1.0
        else:  # Windows
            return 1.0 / self.dpi_scale if self.dpi_scale > 1 else 1.0
    
    def get_screen_info(self, root):
        """Obtém informações precisas da tela"""
        try:
            root.update_idletasks()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            if self.is_windows:
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    user32.SetProcessDPIAware()
                    screen_width = user32.GetSystemMetrics(0)
                    screen_height = user32.GetSystemMetrics(1)
                except:
                    pass
            elif self.is_mac:
                # macOS Retina adjustment
                screen_width = int(screen_width / self.dpi_scale)
                screen_height = int(screen_height / self.dpi_scale)
            elif self.is_linux:
                # Linux - usar valores diretos do Tk
                pass
            
            return screen_width, screen_height
        except:
            return 1920, 1080  # Fallback
    
    def calculate_window_size(self, screen_width, screen_height, scale=0.8):
        """Calcula tamanho ideal da janela baseado na resolução"""
        if self.is_mac:
            min_width, min_height = 1100, 650
            max_width, max_height = 2560, 1440
        elif self.is_linux:
            min_width, min_height = 1000, 600
            max_width, max_height = 1920, 1080
        else:  # Windows
            min_width, min_height = 1200, 700
            max_width, max_height = 1920, 1080
        
        # Calcular tamanho proporcional
        window_width = int(screen_width * scale)
        window_height = int(screen_height * scale)
        
        # Aplicar limites
        window_width = max(min_width, min(window_width, max_width))
        window_height = max(min_height, min(window_height, max_height))
        
        if screen_height <= 768:  # Notebooks com tela pequena
            window_height = min(window_height, 650)
            scale = 0.75
        elif screen_height <= 900:  # Notebooks médios
            window_height = min(window_height, 800)
            scale = 0.78
        elif screen_height <= 1080:  # Full HD
            window_height = min(window_height, 950)
            scale = 0.85
        elif screen_height <= 1440:  # 2K
            window_height = min(window_height, 1300)
            scale = 0.88
        else:  # 4K e superior
            window_height = min(window_height, 1600)
            scale = 0.90
        
        return window_width, window_height
    
    def get_font_scale(self, screen_height):
        """Retorna escala de fonte baseada na altura da tela e plataforma"""
        base_scale = 1.0
        
        if self.is_mac:
            base_scale = 0.95  # macOS tem fontes maiores
        elif self.is_linux:
            base_scale = 1.0
        else:  # Windows
            base_scale = 1.0
        
        # Ajuste por resolução
        if screen_height <= 768:
            return 0.80 * base_scale
        elif screen_height <= 900:
            return 0.85 * base_scale
        elif screen_height <= 1080:
            return 0.95 * base_scale
        elif screen_height <= 1440:
            return 1.05 * base_scale
        else:
            return 1.15 * base_scale
    
    def get_padding_scale(self, screen_width):
        """Retorna escala de padding baseada na largura da tela"""
        if screen_width <= 1366:
            return 0.7
        elif screen_width <= 1600:
            return 0.85
        elif screen_width <= 1920:
            return 1.0
        else:
            return 1.1
            
    def aumentar_fonte(self, tamanho_base):
        """Aumenta tamanho da fonte para acessibilidade"""
        if self.config_acessibilidade["tamanho_fonte_aumentado"]:
            return int(tamanho_base * 1.3)
        return tamanho_base
    
    def alternar_tamanho_fonte(self):
        """Alterna entre tamanho normal e aumentado"""
        self.config_acessibilidade["tamanho_fonte_aumentado"] = not self.config_acessibilidade["tamanho_fonte_aumentado"]
        return self.config_acessibilidade["tamanho_fonte_aumentado"]

class SistemaTCC(ctk.CTk):
    """Janela principal do sistema"""
    
    def __init__(self):
        super().__init__()
        
        logger.info("Iniciando aplicação SistemaTCC")
        
        self.config = ResponsiveConfig()
        self.gerenciador_temas = gerenciador_temas
        
        self.contexto_sistema = {
            "num": [4.0],
            "den": [1.0, 0.8, 4.0],
            "tipo_malha": "fechada",
            "tipo_entrada": "degrau"
        }
        
        self.font_titulo = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        self.font_subtitulo = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.font_corpo = ctk.CTkFont(family="Segoe UI", size=14)
        self.font_label = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.font_pequeno = ctk.CTkFont(family="Segoe UI", size=10)
        
        if self.config.is_windows:
            try:
                from ctypes import windll
                windll.shcore.SetProcessDPIAwareness(1)
            except:
                pass
        
        # Configuração da janela principal
        self.title("ANÁLISE DE CONTROLADORES - Sistema de Controle")
        # self.title("FERRAMENTA COMPUTACIONAL PARA ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE")
        
        self.set_window_icon()
        
        # Obter informações da tela
        self.screen_width, self.screen_height = self.config.get_screen_info(self)
        
        # Calcular tamanho da janela
        window_width, window_height = self.config.calculate_window_size(
            self.screen_width, self.screen_height
        )
        
        # Definir geometria
        self.geometry(f"{window_width}x{window_height}")
        
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
        
        self.frame_atual = None
        
        # Dicionário para rastrear janelas abertas
        self.janelas_abertas = {}
        
        # Criar tela principal
        self.tela_principal = TelaPrincipal(parent=self.container, controlador=self)
        self.tela_principal.grid(row=0, column=0, sticky="nsew")
        self.frame_atual = self.tela_principal
        
        self.configurar_atalhos()
        
        self.criar_menu_acessibilidade()
        
        # Garantir visibilidade
        self.lift()
        self.focus_force()
        
        # Bind para redimensionamento
        self.bind("<Configure>", self.on_window_resize)
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.fila_operacoes = queue.Queue()
        self.processando_fila = False
        
        self.thread_background = threading.Thread(target=self._processar_fila, daemon=True)
        self.thread_background.start()
    
    def _processar_fila(self):
        """Processa operações da fila de forma assíncrona"""
        while True:
            try:
                operacao = self.fila_operacoes.get(timeout=1)
                if operacao:
                    funcao, args, kwargs = operacao
                    try:
                        funcao(*args, **kwargs)
                    except Exception as e:
                        gerenciador_excecoes.registrar_erro("background", str(e), "fila")
            except queue.Empty:
                continue
            except Exception as e:
                gerenciador_excecoes.registrar_erro("thread", str(e), "processamento")
    
    def agendar_operacao(self, funcao, *args, **kwargs):
        """Agenda operação para execução em background"""
        self.fila_operacoes.put((funcao, args, kwargs))
    
    def set_window_icon(self):
        """Define o ícone da janela de forma multiplataforma"""
        try:
            if self.config.is_windows:
                if os.path.exists("image/icons/papel.ico"):
                    self.iconbitmap("image/icons/papel.ico")
            elif self.config.is_linux:
                if os.path.exists("image/icons/papel.ico"):
                    icon = Image.open("image/icons/papel.ico")
                    photo = ImageTk.PhotoImage(icon)
                    self.iconphoto(True, photo)
            elif self.config.is_mac:
                # macOS usa o ícone do app bundle
                pass
        except Exception as e:
            print(f"Aviso: Não foi possível carregar ícone: {e}")
            self.logo_image = None
    
    def configurar_atalhos(self):
        """Configura atalhos de teclado multiplataforma"""
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.exit_fullscreen())
        
        # Atalhos específicos por plataforma
        if self.config.is_mac:
            self.bind("<Command-q>", lambda e: self._on_closing())
            self.bind("<Command-w>", lambda e: self._on_closing())
        else:
            self.bind("<Control-q>", lambda e: self._on_closing())
            self.bind("<Alt-F4>", lambda e: self._on_closing())
            
        # Atalhos de teclado para acessibilidade
        self.bind("<Control-plus>", lambda e: self.aumentar_fonte_global())
        self.bind("<Control-minus>", lambda e: self.diminuir_fonte_global())
        self.bind("<Control-t>", lambda e: self.alternar_tema())
        self.bind("<Control-h>", lambda e: self.mostrar_ajuda())
        self.bind("<Control-c>", lambda e: self.toggle_alto_contraste())
        self.bind("<F1>", lambda e: self.mostrar_ajuda())
    
    def toggle_fullscreen(self):
        """Alterna tela cheia de forma multiplataforma"""
        if not hasattr(self, '_fullscreen'):
            self._fullscreen = False
        
        self._fullscreen = not self._fullscreen
        
        if self.config.is_windows:
            if self._fullscreen:
                self.state('zoomed')
            else:
                self.state('normal')
        elif self.config.is_mac:
            self.attributes('-fullscreen', self._fullscreen)
        else:  # Linux
            self.attributes('-zoomed', self._fullscreen)
    
    def exit_fullscreen(self):
        """Sai do modo tela cheia"""
        if hasattr(self, '_fullscreen') and self._fullscreen:
            self._fullscreen = False
            if self.config.is_windows:
                self.state('normal')
            elif self.config.is_mac:
                self.attributes('-fullscreen', False)
            else:
                self.attributes('-zoomed', False)
    
    def _on_closing(self): # rename on_closing to _on_closing
        """Fecha a aplicação de forma segura"""
        logger.info("Fechando aplicação SistemaTCC")
        try:
            # Fechar todas as janelas abertas
            for janela in list(self.janelas_abertas.values()):
                try:
                    janela.destroy()
                except:
                    pass
            
            # Limpar matplotlib
            plt.close('all')
            
            # Destruir janela principal
            self.destroy()
            logger.info("Aplicação SistemaTCC encerrada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao fechar aplicação: {e}", exc_info=True)
            self.destroy()
    
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

        try:
            if os.path.exists("logo.png"):
                img_pil = Image.open("logo.png").convert("RGBA")
                
                if self.screen_height <= 768:
                    max_h_logo = 40
                elif self.screen_height <= 900:
                    max_h_logo = 45
                elif self.screen_height <= 1080:
                    max_h_logo = 55
                elif self.screen_height <= 1440:
                    max_h_logo = 65
                else:
                    max_h_logo = 75
                
                if self.config.is_mac:
                    max_h_logo = int(max_h_logo * 0.9)
                
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
    
    def abrir_criterios_estabilidade(self):
        """Abre o módulo de critérios de estabilidade"""
        logger.info("Abrindo módulo de critérios de estabilidade")
        self.trocar_para_frame(FrameCriterio, titulo="CRITÉRIOS DE ESTABILIDADE")
    
    def abrir_analise_segunda_ordem(self):
        """Abre o módulo de análise de segunda ordem"""
        logger.info("Abrindo módulo de análise de segunda ordem")
        self.trocar_para_frame(FrameAnalise, titulo="ANÁLISE DE SISTEMAS DE 2ª ORDEM")
    
    # ================== MÉTODO ATUALIZADO ==================
    def abrir_lgr(self):
        """Abre o módulo de Lugar Geométrico das Raízes"""
        logger.info("Abrindo módulo LGR")
        self.trocar_para_frame(JanelaLGR, titulo="📌 LUGAR GEOMÉTRICO DAS RAÍZES")
    # =======================================================

    def abrir_controladores(self):
        """Abre o módulo de controladores"""
        logger.info("Abrindo módulo de controladores")
        try:
            from controladores import JanelaControladores
            janela = JanelaControladores(self)
            self.janelas_abertas['controladores'] = janela
        except Exception as e:
            logger.error(f"Erro ao abrir controladores: {e}")
            self.mostrar_erro(f"Erro ao abrir módulo de controladores: {str(e)}")
    
    # ================== MÉTODO ATUALIZADO ==================
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
            janela = FrameCriterio(self, titulo)
        elif tipo_janela == "analise":
            janela = FrameAnalise(self, titulo)
        # --- Bloco LGR removido מכאן ---
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
    # =======================================================
    
    def criar_menu_acessibilidade(self):
        """Cria menu de acessibilidade e configurações"""
        # Frame flutuante para configurações
        self.frame_config = None
        self.config_visivel = False
        
        # Atalhos de teclado para acessibilidade já configurados em configurar_atalhos
    
    def toggle_configuracoes(self):
        """Mostra/oculta painel de configurações"""
        if self.config_visivel:
            if self.frame_config:
                self.frame_config.destroy()
                self.frame_config = None
            self.config_visivel = False
        else:
            self.mostrar_painel_configuracoes()
            self.config_visivel = True
    
    def mostrar_painel_configuracoes(self):
        """Mostra painel de configurações flutuante"""
        if self.frame_config:
            self.frame_config.destroy()
        
        # Frame flutuante
        self.frame_config = ctk.CTkFrame(
            self,
            fg_color=CORES["fundo_claro"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["primaria"]
        )
        self.frame_config.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        ctk.CTkLabel(
            self.frame_config,
            text="⚙️ CONFIGURAÇÕES E ACESSIBILIDADE",
            font=("Segoe UI", self.scale_font(18), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(pady=20, padx=30)
        
        # Seção de Temas
        frame_temas = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        frame_temas.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            frame_temas,
            text="🎨 Tema:",
            font=("Segoe UI", self.scale_font(14), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=5)
        
        frame_botoes_tema = ctk.CTkFrame(frame_temas, fg_color="transparent")
        frame_botoes_tema.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            frame_botoes_tema,
            text="🌙 Escuro",
            command=lambda: self.aplicar_tema("dark"),
            width=120,
            height=40,
            font=("Segoe UI", self.scale_font(12), "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes_tema,
            text="☀️ Claro",
            command=lambda: self.aplicar_tema("light"),
            width=120,
            height=40,
            font=("Segoe UI", self.scale_font(12), "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes_tema,
            text="🔆 Alto Contraste",
            command=lambda: self.aplicar_tema("high_contrast"),
            width=150,
            height=40,
            font=("Segoe UI", self.scale_font(12), "bold"),
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"]
        ).pack(side="left", padx=5)
        
        # Seção de Acessibilidade
        frame_acess = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        frame_acess.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            frame_acess,
            text="♿ Acessibilidade:",
            font=("Segoe UI", self.scale_font(14), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=5)
        
        ctk.CTkButton(
            frame_acess,
            text="🔤 Aumentar Fonte (Ctrl++)",
            command=self.aumentar_fonte_global,
            width=250,
            height=40,
            font=("Segoe UI", self.scale_font(14), "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(pady=5)
        
        ctk.CTkButton(
            frame_acess,
            text="🔡 Diminuir Fonte (Ctrl+-)",
            command=self.diminuir_fonte_global,
            width=250,
            height=40,
            font=("Segoe UI", self.scale_font(14), "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(pady=5)
        
        # Atalhos
        frame_atalhos = ctk.CTkFrame(self.frame_config, fg_color=CORES["acento"], corner_radius=10)
        frame_atalhos.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(
            frame_atalhos,
            text="⌨️ Atalhos de Teclado:",
            font=("Segoe UI", self.scale_font(15), "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        atalhos_texto = """
        F1 - Ajuda
        F11 - Tela Cheia
        Ctrl+T - Alternar Tema
        Ctrl++ - Aumentar Fonte
        Ctrl+- - Diminuir Fonte
        Ctrl+H - Ajuda
        ESC - Sair Tela Cheia
        """
        
        ctk.CTkLabel(
            frame_atalhos,
            text=atalhos_texto,
            font=("Consolas", self.scale_font(14)),
            text_color=CORES["texto_secundario"],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Botão fechar
        ctk.CTkButton(
            self.frame_config,
            text="✖ Fechar",
            command=self.toggle_configuracoes,
            width=200,
            height=45,
            font=("Segoe UI", self.scale_font(13), "bold"),
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"]
        ).pack(pady=20)
    
    def aplicar_tema(self, nome_tema):
        """Aplica um tema específico"""
        global CORES
        self.gerenciador_temas.definir_tema(nome_tema)
        CORES = self.gerenciador_temas.obter_cores()
        ctk.set_appearance_mode(CORES["mode"])
        
        # Recriar interface
        self.recriar_interface()
    
    def alternar_tema(self):
        """Alterna entre temas disponíveis"""
        global CORES
        novo_tema = self.gerenciador_temas.alternar_tema()
        CORES = self.gerenciador_temas.obter_cores()
        ctk.set_appearance_mode(CORES["mode"])
        
        # Recriar interface
        self.recriar_interface()
    
    def toggle_alto_contraste(self):
        """Ativa/desativa modo alto contraste"""
        if self.gerenciador_temas.tema_atual == "high_contrast":
            self.aplicar_tema("dark")
        else:
            self.aplicar_tema("high_contrast")
    
    def aumentar_fonte_global(self):
        """Aumenta o tamanho das fontes do sistema em todos os frames ativos"""
        # Ajusta o tamanho base das fontes
        if self.font_corpo.cget("size") < 20: # Limite para evitar fontes gigantes
            self.font_titulo.configure(size=self.font_titulo.cget("size") + 2)
            self.font_subtitulo.configure(size=self.font_subtitulo.cget("size") + 2)
            self.font_corpo.configure(size=self.font_corpo.cget("size") + 1)
            self.font_label.configure(size=self.font_label.cget("size") + 1)
            self.font_pequeno.configure(size=self.font_pequeno.cget("size") + 1)
            
            # Atualiza fontes em módulos abertos
            for widget in self.winfo_children():
                if isinstance(widget, FrameBase):
                    widget.atualizar_fontes()
            
            logger.info("Fontes aumentadas globalmente")
    
    def diminuir_fonte_global(self):
        """Diminui o tamanho das fontes do sistema em todos os frames ativos"""
        if self.font_corpo.cget("size") > 10: # Limite para evitar fontes muito pequenas
            self.font_titulo.configure(size=self.font_titulo.cget("size") - 2)
            self.font_subtitulo.configure(size=self.font_subtitulo.cget("size") - 2)
            self.font_corpo.configure(size=self.font_corpo.cget("size") - 1)
            self.font_label.configure(size=self.font_label.cget("size") - 1)
            self.font_pequeno.configure(size=self.font_pequeno.cget("size") - 1)

            # Atualiza fontes em módulos abertos
            for widget in self.winfo_children():
                if isinstance(widget, FrameBase):
                    widget.atualizar_fontes()

            logger.info("Fontes diminuídas globalmente")
    
    def resetar_fonte(self):
        """Reseta as fontes para o tamanho padrão"""
        self.font_titulo.configure(size=20)
        self.font_subtitulo.configure(size=16)
        self.font_corpo.configure(size=14)
        self.font_label.configure(size=12)
        self.font_pequeno.configure(size=10)
        logger.info("Fontes resetadas")
    
    def mostrar_ajuda(self):
        """Mostra janela de ajuda"""
        janela_ajuda = ctk.CTkToplevel(self)
        janela_ajuda.title("Ajuda - Sistema de Controle")
        janela_ajuda.geometry("700x600")
        janela_ajuda.configure(fg_color=CORES["fundo_escuro"])
        
        # Centralizar
        janela_ajuda.update_idletasks()
        x = (self.winfo_screenwidth() - 700) // 2
        y = (self.winfo_screenheight() - 600) // 2
        janela_ajuda.geometry(f"700x600+{x}+{y}")
        
        # Conteúdo
        frame_scroll = ctk.CTkScrollableFrame(
            janela_ajuda,
            fg_color=CORES["fundo_claro"]
        )
        frame_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame_scroll,
            text="📚 GUIA DE USO DO SISTEMA",
            font=("Segoe UI", 20, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(pady=15)
        
        ajuda_texto = """
        MÓDULOS DISPONÍVEIS:
        
        1. ANÁLISE DE ESTABILIDADE
           • Critério de Routh-Hurwitz
           • Análise de polos e zeros
           • Determinação de estabilidade
        
        2. ANÁLISE DE SISTEMA 2ª ORDEM
           • Resposta ao degrau e rampa
           • Cálculo de parâmetros (ωn, ζ, K)
           • Características temporais
           • Gráficos de resposta
        
        3. ANÁLISE DE CONTROLADORES
           • Controladores PI, PD e PID
           • Lugar das raízes
           • Resposta temporal comparativa
           • Diagrama de polos e zeros
        
        ACESSIBILIDADE:
        
        • Temas: Escuro, Claro e Alto Contraste
        • Ajuste de tamanho de fonte
        • Atalhos de teclado
        • Interface responsiva
        
        ATALHOS DE TECLADO:
        
        F1 - Ajuda
        F11 - Tela Cheia
        Ctrl+T - Alternar Tema
        Ctrl++ - Aumentar Fonte
        Ctrl+- - Diminuir Fonte
        Ctrl+H - Ajuda
        ESC - Sair Tela Cheia
        
        COMO USAR:
        
        1. Selecione o módulo desejado
        2. Insira os coeficientes da função de transferência
        3. Configure os parâmetros necessários
        4. Clique em "Analisar" ou "Plotar"
        5. Visualize os resultados e gráficos
        
        FORMATO DE ENTRADA:
        
        • Coeficientes separados por espaço
        • Do maior para o menor grau
        • Use ponto (.) para decimais
        • Exemplo: 1 2 4 (para s² + 2s + 4)
        
        SUPORTE:
        
        Para mais informações, consulte a documentação
        ou entre em contato com o desenvolvedor.
        """
        
        ctk.CTkLabel(
            frame_scroll,
            text=ajuda_texto,
            font=("Segoe UI", 12),
            text_color=CORES["texto_secundario"],
            justify="left"
        ).pack(pady=10, padx=20)
        
        ctk.CTkButton(
            janela_ajuda,
            text="Fechar",
            command=janela_ajuda.destroy,
            width=150,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(pady=15)

    def mostrar_erro(self, mensagem):
        """Mostra uma janela de erro simples"""
        janela_erro = ctk.CTkToplevel(self)
        janela_erro.title("❌ Erro Inesperado")
        janela_erro.geometry("450x250")
        janela_erro.configure(fg_color=CORES["fundo_escuro"])

        # Centralizar
        janela_erro.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 250) // 2
        janela_erro.geometry(f"450x250+{x}+{y}")

        janela_erro.grid_columnconfigure(0, weight=1)
        janela_erro.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            janela_erro,
            text="❌ Ocorreu um Erro:",
            font=self.font_subtitulo,
            text_color=CORES["erro"]
        ).pack(pady=(20, 10))

        erro_textbox = ctk.CTkTextbox(
            janela_erro,
            font=self.font_corpo,
            text_color=CORES["texto_principal"],
            fg_color=CORES["fundo_claro"],
            width=400,
            height=100,
            wrap="word",
            activate_scrollbars=True
        )
        erro_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        erro_textbox.insert("1.0", mensagem)
        erro_textbox.configure(state="disabled")

        ctk.CTkButton(
            janela_erro,
            text="Fechar",
            command=janela_erro.destroy,
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(pady=20)

        janela_erro.transient(self)
        janela_erro.grab_set()
        janela_erro.focus_force()
    
    def recriar_interface(self):
        """Recria a interface com novo tema"""
        # Destruir container atual
        if hasattr(self, 'container'):
            self.container.destroy()
        
        # Reconfigurar cor de fundo
        self.configure(fg_color=CORES["fundo_escuro"])
        
        # Recriar container
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color=CORES["fundo_escuro"])
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Recriar tela principal
        self.tela_principal = TelaPrincipal(parent=self.container, controlador=self)
        self.tela_principal.grid(row=0, column=0, sticky="nsew")
        self.frame_atual = self.tela_principal
        
        # Fechar painel de configurações se estiver aberto
        if self.config_visivel:
            self.toggle_configuracoes()

        # Atualizar fontes dos frames de módulos abertos
        for widget in self.winfo_children():
            if isinstance(widget, FrameBase):
                widget.atualizar_fontes()
    
    def trocar_para_frame(self, frame_class, *args, **kwargs):
        """
        Troca para um novo frame com transição fade
        
        Args:
            frame_class: Classe do frame a ser criado
            *args, **kwargs: Argumentos para o construtor do frame
        """
        # Fade out
        self.attributes("-alpha", 0.0)
        self.update_idletasks()
        
        # Destruir frame antigo
        if self.frame_atual:
            self.frame_atual.destroy()
        
        # Criar e mostrar novo frame
        self.frame_atual = frame_class(parent=self.container, controlador=self, *args, **kwargs)
        self.frame_atual.grid(row=0, column=0, sticky="nsew")
        
        # Fade in
        self.after(50, lambda: self.attributes("-alpha", 1.0)) # Usar lambda para garantir execução assíncrona
    
    def voltar_para_menu(self):
        """Volta para o menu principal com transição"""
        self.trocar_para_frame(TelaPrincipal)
    
    # Métodos de fonte globais já definidos em aumentar_fonte_global e diminuir_fonte_global
    
    # Este método abrir_janela foi atualizado acima, removendo a lógica "lgr"
    # def abrir_janela(self, tipo_janela, titulo): ...

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
        # Adicionar coluna para o botão de configurações
        container_principal.grid_columnconfigure(2, weight=0)
        
        # LADO ESQUERDO
        container_titulo = ctk.CTkFrame(container_principal, fg_color="transparent")
        container_titulo.grid(row=0, column=0, sticky="w", padx=0, pady=0)
        
        # Título responsivo
        titulo_size = self.controlador.scale_font(20)
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
        
        subtitulo_size = self.controlador.scale_font(15)
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
        
        inst_size = self.controlador.scale_font(12)
        texto_institucional = ctk.CTkLabel(
            container_logo_interno,
            text="UFERSA",
            font=("Segoe UI", inst_size, "bold"),
            text_color=CORES["texto_secundario"],
            justify="center"
        )
        texto_institucional.pack()
        
        # Botão de configurações (lado direito)
        botao_config = ctk.CTkButton(
            container_principal,
            text="⚙️",
            command=self.controlador.toggle_configuracoes,
            width=50,
            height=50,
            font=("Segoe UI", 25),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=25
        )
        botao_config.grid(row=0, column=2, sticky="e", padx=(10, 0))
    
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
        
        titulo_size = self.controlador.scale_font(18)
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
        button_height = 50 if self.controlador.screen_height <= 768 else 65
        button_font = self.controlador.scale_font(18)
        button_padding = self.controlador.scale_padding(12)
        
        informacoes_botoes = [
            {
                "texto": "📊 ANÁLISE DE ESTABILIDADE",
                "comando": lambda: self.controlador.abrir_criterios_estabilidade(),
                "cor": CORES["primaria"],
                "cor_hover": CORES["primaria_hover"],
            },
            {
                "texto": "📈 ANÁLISE DE SISTEMA 2ª ORDEM", 
                "comando": lambda: self.controlador.abrir_analise_segunda_ordem(),
                "cor": CORES["secundaria"],
                "cor_hover": CORES["secundaria_hover"],
            },
            {
                "texto": "⚲ LUGAR GEOMÉTRICO DAS RAÍZES",
                "comando": lambda: self.controlador.abrir_lgr(),
                "cor": CORES["quarto"],
                "cor_hover": CORES["quarto_hover"],
            },
            {
                "texto": "🎮 ANÁLISE DE CONTROLADORES",
                "comando": lambda: self.controlador.abrir_controladores(),
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
        
        font_size = self.controlador.scale_font(15)
        
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

class FrameBase(ctk.CTkFrame):
    """Classe base para frames de módulos (substitui JanelaBase)"""
    def __init__(self, parent, controlador, titulo):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.titulo = titulo
        
        # Configuração responsiva
        config = ResponsiveConfig()
        screen_width, screen_height = config.get_screen_info(controlador)
        
        # Escalas
        self.font_scale = config.get_font_scale(screen_height)
        self.padding_scale = config.get_padding_scale(screen_width)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Linha 1 para o conteúdo
        
        self.criar_cabecalho()
        self.criar_conteudo()
    
    def scale_font(self, base_size):
        return int(base_size * self.font_scale)
    
    def scale_padding(self, base_padding):
        return int(base_padding * self.padding_scale)
    
    def criar_cabecalho(self):
        header_height = 65 if self.controlador.winfo_screenheight() <= 768 else 70
        
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
            text="← VOLTAR",
            command=self.voltar_menu,
            width=110,
            height=38,
            font=self.controlador.font_label,
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"],
            corner_radius=8
        )
        botao_voltar.grid(row=0, column=0, sticky="w", padx=padding, pady=15)
        
        label_titulo = ctk.CTkLabel(
            frame_cabecalho,
            text=self.titulo,
            font=self.controlador.font_titulo,
            text_color=CORES["texto_principal"]
        )
        label_titulo.grid(row=0, column=1, pady=15)
    
    def criar_conteudo(self):
        """Sobrescrever em subclasses"""
        pass
    
    def voltar_menu(self):
        """Volta para o menu principal"""
        self.controlador.voltar_para_menu()

    def atualizar_fontes(self):
        """Atualiza fontes dos widgets deste frame (se necessário)"""
        # Exemplo: Se houver labels, botões, etc. com fontes específicas
        pass # Deve ser implementado nas subclasses se necessário

class FrameCriterio(FrameBase):
    def __init__(self, parent, controlador, titulo):
        self.numerador = []
        self.denominador = []
        super().__init__(parent, controlador, titulo)
        
        if self.controlador.contexto_sistema.get("num"):
            num_str = " ".join(map(str, self.controlador.contexto_sistema["num"]))
            self.entrada_numerador.insert(0, num_str)
        if self.controlador.contexto_sistema.get("den"):
            den_str = " ".join(map(str, self.controlador.contexto_sistema["den"]))
            self.entrada_denominador.insert(0, den_str)
    
    def criar_conteudo(self):
        padding = self.scale_padding(20)
        
        # Container principal com 2 colunas
        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=padding, pady=padding)
        frame_conteudo.grid_columnconfigure(0, weight=0)  # Coluna esquerda - largura fixa
        frame_conteudo.grid_columnconfigure(1, weight=1)  # Coluna direita - expansível
        frame_conteudo.grid_rowconfigure(0, weight=1)
        
        # Calcular largura responsiva do painel esquerdo
        screen_width = self.controlador.winfo_screenwidth()
        if screen_width <= 1366:
            panel_esquerdo_width = 280
        elif screen_width <= 1600:
            panel_esquerdo_width = 320
        else:
            panel_esquerdo_width = 360
        
        # ==================== PAINEL ESQUERDO - ENTRADAS ====================
        frame_esquerdo = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["primaria"]
        )
        frame_esquerdo.grid(row=0, column=0, sticky="ns", padx=(0, 15))
        frame_esquerdo.grid_propagate(False)
        frame_esquerdo.configure(width=panel_esquerdo_width)
        frame_esquerdo.grid_columnconfigure(0, weight=1)
        frame_esquerdo.grid_rowconfigure(2, weight=1)
        
        # Título do painel esquerdo
        titulo_esq = ctk.CTkLabel(
            frame_esquerdo,
            text="⚙️ CONFIGURAÇÃO",
            font=("Segoe UI", self.scale_font(15), "bold"),
            text_color=CORES["texto_principal"]
        )
        titulo_esq.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        
        # Linha divisória
        linha_esq = ctk.CTkFrame(
            frame_esquerdo,
            height=2,
            fg_color=CORES["primaria"],
            corner_radius=1
        )
        linha_esq.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Container scrollável para entradas
        scroll_esquerdo = ctk.CTkScrollableFrame(
            frame_esquerdo,
            fg_color="transparent",
            corner_radius=0
        )
        scroll_esquerdo.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        scroll_esquerdo.grid_columnconfigure(0, weight=1)
        
        # ===== ENTRADA NUMERADOR =====
        label_num = ctk.CTkLabel(
            scroll_esquerdo,
            text="Numerador:",
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"]
        )
        label_num.grid(row=0, column=0, sticky="w", pady=(0, 6))
        
        self.entrada_numerador = ctk.CTkEntry(
            scroll_esquerdo,
            placeholder_text="Ex: 1 3",
            font=self.controlador.font_label,
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1,
            height=35
        )
        self.entrada_numerador.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        
        hint_num = ctk.CTkLabel(
            scroll_esquerdo,
            text="maior → menor grau",
            font=("Segoe UI", self.scale_font(10)),
            text_color=CORES["texto_secundario"]
        )
        hint_num.grid(row=2, column=0, sticky="w", pady=(0, 18))
        
        # ===== ENTRADA DENOMINADOR =====
        label_den = ctk.CTkLabel(
            scroll_esquerdo,
            text="Denominador:",
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"]
        )
        label_den.grid(row=3, column=0, sticky="w", pady=(0, 6))
        
        self.entrada_denominador = ctk.CTkEntry(
            scroll_esquerdo,
            placeholder_text="Ex: 1 5 6",
            font=self.controlador.font_label,
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1,
            height=35
        )
        self.entrada_denominador.grid(row=4, column=0, sticky="ew", pady=(0, 4))
        
        hint_den = ctk.CTkLabel(
            scroll_esquerdo,
            text="maior → menor grau",
            font=("Segoe UI", self.scale_font(12)),
            text_color=CORES["texto_secundario"]
        )
        hint_den.grid(row=5, column=0, sticky="w", pady=(0, 25))
        
        # ===== BOTÕES =====
        btn_completo = ctk.CTkButton(
            scroll_esquerdo,
            text="📊 Análise Completa",
            command=self.analisar_sistema_completo,
            font=self.controlador.font_label,
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            height=38,
            corner_radius=8
        )
        btn_completo.grid(row=6, column=0, sticky="ew", pady=(0, 9))
        
        btn_routh = ctk.CTkButton(
            scroll_esquerdo,
            text="📈 Routh-Hurwitz",
            command=self.analisar_routh_hurwitz,
            font=self.controlador.font_label,
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            height=38,
            corner_radius=8
        )
        btn_routh.grid(row=7, column=0, sticky="ew", pady=(0, 9))
        
        btn_limpar = ctk.CTkButton(
            scroll_esquerdo,
            text="🗑️ Limpar",
            command=self.limpar_entrada,
            font=self.controlador.font_label,
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"],
            height=38,
            corner_radius=8
        )
        btn_limpar.grid(row=8, column=0, sticky="ew")
        
        # ==================== PAINEL DIREITO - RESULTADOS ====================
        frame_direito = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["primaria"]
        )
        frame_direito.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        frame_direito.grid_columnconfigure(0, weight=1)
        frame_direito.grid_rowconfigure(2, weight=1)
        
        # Título do painel direito
        titulo_dir = ctk.CTkLabel(
            frame_direito,
            text="📋 RESULTADOS DA ANÁLISE",
            font=("Segoe UI", self.scale_font(13), "bold"),
            text_color=CORES["texto_principal"]
        )
        titulo_dir.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        # Linha divisória
        linha_dir = ctk.CTkFrame(
            frame_direito,
            height=2,
            fg_color=CORES["primaria"],
            corner_radius=1
        )
        linha_dir.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Textbox de resultados
        self.texto_resultados = ctk.CTkTextbox(
            frame_direito,
            font=("Courier New", self.scale_font(14)),
            fg_color=CORES["fundo_claro"],
            text_color=CORES["texto_principal"],
            border_color=CORES["borda"],
            border_width=1,
            corner_radius=8,
            wrap="word"
        )
        self.texto_resultados.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Conteúdo inicial de ajuda
        self._adicionar_conteudo_inicial()
    
    def _adicionar_conteudo_inicial(self):
        """Adiciona conteúdo inicial de ajuda"""
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", "📌 INSTRUÇÕES DE USO\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n\n")
        self.texto_resultados.insert("end", "1:  PREENCHA OS CAMPOS:\n")
        self.texto_resultados.insert("end", "   • Numerador: Coeficientes do numerador (Ex: 1 3)\n")
        self.texto_resultados.insert("end", "   • Denominador: Coeficientes do denominador (Ex: 1 5 6)\n\n")
        self.texto_resultados.insert("end", "2:  CLIQUE EM UMA ANÁLISE:\n")
        self.texto_resultados.insert("end", "   • 📊 Análise Completa: Análise geral do sistema\n")
        self.texto_resultados.insert("end", "   • 📈 Routh-Hurwitz: Teste de estabilidade\n\n")
        self.texto_resultados.insert("end", "3:  FORMATO CORRETO:\n")
        self.texto_resultados.insert("end", "   • Separe números com ESPAÇO\n")
        self.texto_resultados.insert("end", "   • Use ponto (.) para decimais (Ex: 1.5 2.3)\n")
        self.texto_resultados.insert("end", "   • Do MAIOR para o MENOR grau\n\n")
        self.texto_resultados.insert("end", "✅ EXEMPLO DE USO:\n")
        self.texto_resultados.insert("end", "   Numerador:   1 3\n")
        self.texto_resultados.insert("end", "   Denominador: 1 5 6\n")
        self.texto_resultados.insert("end", "   Sistema: G(s) = (s + 3) / (s² + 5s + 6)\n")
    
    def limpar_entrada(self):
        """Limpa os campos de entrada e foca no numerador"""
        self.entrada_numerador.delete(0, "end")
        self.entrada_denominador.delete(0, "end")
        self.entrada_numerador.focus()
        self._adicionar_conteudo_inicial()
    
    def obter_coeficientes(self):
        """Obtém e valida os coeficientes do usuário"""
        try:
            texto_num = self.entrada_numerador.get().strip()
            texto_den = self.entrada_denominador.get().strip()
            
            if not texto_num or not texto_den:
                raise ValueError("❌ CAMPOS VAZIOS!\n\nPor favor, preencha ambos os campos:\n   • Numerador\n   • Denominador")
            
            try:
                numerador = [float(x) for x in texto_num.split()]
            except ValueError:
                raise ValueError(
                    f"❌ ERRO NO NUMERADOR!\n\n"
                    f"Valor inserido: '{texto_num}'\n\n"
                    f"Use apenas números separados por espaço.\n\n"
                    f"Exemplos corretos:\n"
                    f"   • 1 3\n"
                    f"   • 2.5 4.2"
                )
            
            try:
                denominador = [float(x) for x in texto_den.split()]
            except ValueError:
                raise ValueError(
                    f"❌ ERRO NO DENOMINADOR!\n\n"
                    f"Valor inserido: '{texto_den}'\n\n"
                    f"Use apenas números separados por espaço.\n\n"
                    f"Exemplos corretos:\n"
                    f"   • 1 5 6\n"
                    f"   • 2.5 4.2 8.1"
                )
            
            if len(numerador) == 0:
                raise ValueError("❌ NUMERADOR VAZIO!\n\nO numerador não pode estar vazio!")
            
            if len(denominador) == 0:
                raise ValueError("❌ DENOMINADOR VAZIO!\n\nO denominador não pode estar vazio!")
            
            if abs(denominador[0]) < 1e-15:
                raise ValueError(
                    "❌ PRIMEIRO COEFICIENTE DO DENOMINADOR É ZERO!\n\n"
                    f"Valor inserido: {denominador}\n\n"
                    f"O coeficiente do termo de maior grau não pode ser zero.\n\n"
                    f"Exemplo correto: 1 5 6\n"
                    f"Exemplo errado: 0 5 6"
                )
            
            if all(abs(c) < 1e-15 for c in denominador):
                raise ValueError(
                    "❌ DENOMINADOR INVÁLIDO!\n\n"
                    f"O denominador não pode ter todos os coeficientes iguais a ZERO!\n"
                    f"Valor inserido: {denominador}"
                )
            
            self.controlador.contexto_sistema["num"] = numerador
            self.controlador.contexto_sistema["den"] = denominador
            
            return numerador, denominador
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"❌ ERRO INESPERADO!\n\n{str(e)}")
    
    def analisar_sistema_completo(self):
        """Realiza análise completa do sistema"""
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
        """Realiza análise Routh-Hurwitz"""
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
        """Exibe mensagem de erro formatada"""
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", f"{mensagem}\n\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n\n")
        self.texto_resultados.insert("end", "💡 DICAS PARA CORRIGIR:\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n")
        self.texto_resultados.insert("end", "✓ Use apenas números (inteiros ou decimais)\n")
        self.texto_resultados.insert("end", "✓ Separe os coeficientes por ESPAÇO\n")
        self.texto_resultados.insert("end", "✓ Use ponto (.) para decimais, não vírgula\n")
        self.texto_resultados.insert("end", "✓ O primeiro coeficiente não pode ser ZERO\n")
        self.texto_resultados.insert("end", "✓ Digite os coeficientes do MAIOR para o MENOR grau\n\n")
        self.texto_resultados.insert("end", "📝 EXEMPLOS CORRETOS:\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n")
        self.texto_resultados.insert("end", "Numerador:   1 3\n")
        self.texto_resultados.insert("end", "Denominador: 1 5 6\n")
        self.texto_resultados.insert("end", "Sistema: G(s) = (s + 3) / (s² + 5s + 6)\n\n")
        self.texto_resultados.insert("end", "Numerador:   2.5 1.5\n")
        self.texto_resultados.insert("end", "Denominador: 1 3.5 2.8\n")
        self.texto_resultados.insert("end", "Sistema: G(s) = (2.5s + 1.5) / (s² + 3.5s + 2.8)\n")

class FrameAnalise(FrameBase):
    def __init__(self, parent, controlador, titulo):
        self.analisador = AnalisadorSegundaOrdem()
        self.canvas_grafico = None
        super().__init__(parent, controlador, titulo)
        
        if self.controlador.contexto_sistema.get("num"):
            num_str = " ".join(map(str, self.controlador.contexto_sistema["num"]))
            self.entrada_numerador.delete(0, "end")
            self.entrada_numerador.insert(0, num_str)
        if self.controlador.contexto_sistema.get("den"):
            den_str = " ".join(map(str, self.controlador.contexto_sistema["den"]))
            self.entrada_denominador.delete(0, "end")
            self.entrada_denominador.insert(0, den_str)
        if self.controlador.contexto_sistema.get("tipo_malha"):
            self.tipo_malha.set(self.controlador.contexto_sistema["tipo_malha"])
        if self.controlador.contexto_sistema.get("tipo_entrada"):
            self.tipo_entrada.set(self.controlador.contexto_sistema["tipo_entrada"])
    
    def criar_conteudo(self):
        padding = self.scale_padding(20)
        
        container_principal = ctk.CTkFrame(self, fg_color="transparent")
        container_principal.grid(row=1, column=0, sticky="nsew", padx=padding, pady=padding)
        container_principal.grid_columnconfigure(0, weight=0)
        container_principal.grid_columnconfigure(1, weight=1)
        container_principal.grid_rowconfigure(0, weight=1)
        
        # Largura responsiva do painel esquerdo
        screen_width = self.controlador.winfo_screenwidth()
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
            font=self.controlador.font_subtitulo,
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
        frame_configuracoes.grid(row=0, column=0, sticky="ew", pady=15)
        frame_configuracoes.grid_columnconfigure(0, weight=1)
        frame_configuracoes.grid_columnconfigure(1, weight=1)
        
        # Tipo de Malha
        frame_malha = ctk.CTkFrame(frame_configuracoes, fg_color="transparent")
        frame_malha.grid(row=0, column=0, sticky="ew", pady=15, padx=15)
        
        ctk.CTkLabel(
            frame_malha,
            text="⇄ Tipo de Sistema:",
            font=self.controlador.font_corpo,
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 8))
        
        self.tipo_malha = ctk.StringVar(value="fechada")
        
        ctk.CTkRadioButton(
            frame_malha,
            text="Malha Fechada",
            variable=self.tipo_malha,
            value="fechada",
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(anchor="w", pady=4)
        
        ctk.CTkRadioButton(
            frame_malha,
            text="Malha Aberta",
            variable=self.tipo_malha,
            value="aberta",
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(anchor="w", pady=4)
        
        # Tipo de Entrada
        frame_entrada_tipo = ctk.CTkFrame(frame_configuracoes, fg_color="transparent")
        frame_entrada_tipo.grid(row=0, column=1, sticky="ew", pady=15, padx=15)
        
        ctk.CTkLabel(
            frame_entrada_tipo,
            text="📥 Tipo de Entrada:",
            font=self.controlador.font_corpo,
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 8))
        
        self.tipo_entrada = ctk.StringVar(value="degrau")
        
        ctk.CTkRadioButton(
            frame_entrada_tipo,
            text="Degrau Unitário",
            variable=self.tipo_entrada,
            value="degrau",
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"],
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(anchor="w", pady=4)
        
        ctk.CTkRadioButton(
            frame_entrada_tipo,
            text="Rampa Unitária",
            variable=self.tipo_entrada,
            value="rampa",
            font=self.controlador.font_label,
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
            text="⚙ Função de Transferência de 2ª Ordem:",
            font=self.controlador.font_corpo,
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=12, padx=15)
        
        # Numerador
        ctk.CTkLabel(
            frame_entrada, 
            text="Numerador:", 
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"]
        ).grid(row=1, column=0, sticky="w", pady=5, padx=15)
        
        entry_height = 34 if self.controlador.winfo_screenheight() <= 768 else 36
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 4",
            height=entry_height,
            font=self.controlador.font_corpo,
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        # Denominador
        ctk.CTkLabel(
            frame_entrada, 
            text="Denominador:", 
            font=self.controlador.font_label,
            text_color=CORES["texto_principal"]
        ).grid(row=3, column=0, sticky="w", pady=5, padx=15)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 2 4",
            height=entry_height,
            font=self.controlador.font_corpo,
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Botões de ação
        frame_botoes = ctk.CTkFrame(frame_entrada, fg_color="transparent")
        frame_botoes.grid(row=5, column=0, pady=(5, 15), padx=15)
        
        button_height = 43 if self.controlador.winfo_screenheight() <= 768 else 45
        
        ctk.CTkButton(
            frame_botoes,
            text="╰┈➤ Analisar Sistema",
            command=self.analisar_sistema,
            width=160,
            height=button_height,
            font=self.controlador.font_corpo,
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
            font=self.controlador.font_corpo,
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
            font=self.controlador.font_corpo,
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=10, padx=15)
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados,
            font=("Consolas", self.scale_font(12)),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1,
            wrap="word",
            height=300
        )
        self.texto_resultados.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
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
            font=self.controlador.font_subtitulo,
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
            font=self.controlador.font_corpo,
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
            
            self.controlador.contexto_sistema["num"] = numerador
            self.controlador.contexto_sistema["den"] = denominador
            self.controlador.contexto_sistema["tipo_malha"] = self.tipo_malha.get()
            self.controlador.contexto_sistema["tipo_entrada"] = self.tipo_entrada.get()
            
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
                canvas_widget.grid(row=0, column=0, sticky="nsew")
                canvas_widget.grid_propagate(True)
                
                toolbar_frame = ctk.CTkFrame(self.grafico_container, fg_color="transparent")
                toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
                toolbar = NavigationToolbar2Tk(self.canvas_grafico, toolbar_frame)
                toolbar.update()
                
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

class JanelaLGR(FrameBase):
    """Frame para análise do Lugar Geométrico das Raízes (agora herda de FrameBase)"""
    
    def __init__(self, parent, controlador, titulo):
        # 1. Chamar construtor da classe base (FrameBase)
        super().__init__(parent, controlador, titulo)
        
        # 2. Configurações específicas deste frame
        self.analisador = AnalisadorLGR()
        self.canvas_grafico = None
        
        # 3. Carregar dados do contexto se existirem
        if hasattr(self.controlador, 'contexto_sistema'):
            if self.controlador.contexto_sistema.get("num"):
                num_str = " ".join(map(str, self.controlador.contexto_sistema["num"]))
                self.entrada_numerador.insert(0, num_str)
            if self.controlador.contexto_sistema.get("den"):
                den_str = " ".join(map(str, self.controlador.contexto_sistema["den"]))
                self.entrada_denominador.insert(0, den_str)
        
        logger.info("Frame LGR aberto")
        
    # 4. Remover criar_cabecalho() - FrameBase já cuida disso

    def criar_conteudo(self):
        """Cria o conteúdo principal da janela (chamado por FrameBase)"""
        
        # Container principal que ficará em row=1 (abaixo do cabeçalho)
        container_principal = ctk.CTkFrame(self, fg_color="transparent")
        container_principal.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        container_principal.grid_columnconfigure(0, weight=0)  # Painel esquerdo fixo
        container_principal.grid_columnconfigure(1, weight=1)  # Painel direito expansível
        container_principal.grid_rowconfigure(0, weight=1)
        
        # PAINEL ESQUERDO - Entradas e Controles
        self.criar_painel_esquerdo(container_principal)
        
        # PAINEL DIREITO - Gráfico e Resultados
        self.criar_painel_direito(container_principal)
    
    def criar_painel_esquerdo(self, parent):
        """Cria o painel esquerdo com entradas"""
        frame_esquerdo = ctk.CTkFrame(
            parent,
            fg_color=CORES["acento"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["primaria"],
            width=420
        )
        frame_esquerdo.grid(row=0, column=0, sticky="ns", padx=(0, 15))
        frame_esquerdo.grid_propagate(False)
        frame_esquerdo.grid_columnconfigure(0, weight=1)
        frame_esquerdo.grid_rowconfigure(2, weight=1)
        
        # Título
        titulo = ctk.CTkLabel(
            frame_esquerdo,
            text="⚙️ CONFIGURAÇÃO DO SISTEMA",
            font=self.controlador.font_subtitulo, # Usar fonte do controlador
            text_color=CORES["texto_principal"]
        )
        titulo.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        
        # Linha divisória
        linha = ctk.CTkFrame(
            frame_esquerdo,
            height=2,
            fg_color=CORES["primaria"],
            corner_radius=1
        )
        linha.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Container scrollável
        scroll_container = ctk.CTkScrollableFrame(
            frame_esquerdo,
            fg_color="transparent"
        )
        scroll_container.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        scroll_container.grid_columnconfigure(0, weight=1)
        
        # === ENTRADAS ===
        frame_entradas = ctk.CTkFrame(
            scroll_container,
            fg_color=CORES["fundo_claro"],
            corner_radius=10
        )
        frame_entradas.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        frame_entradas.grid_columnconfigure(0, weight=1)
        
        # Instruções
        instrucoes = ctk.CTkLabel(
            frame_entradas,
            text="📝 Digite os coeficientes da Função de Transferência",
            font=self.controlador.font_corpo, # Usar fonte do controlador
            text_color=CORES["texto_principal"]
        )
        instrucoes.grid(row=0, column=0, sticky="w", pady=12, padx=15)
        
        # Numerador
        ctk.CTkLabel(
            frame_entradas,
            text="Numerador:",
            font=self.controlador.font_label, # Usar fonte do controlador
            text_color=CORES["texto_principal"]
        ).grid(row=1, column=0, sticky="w", pady=(5, 5), padx=15)
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entradas,
            placeholder_text="Ex: 1",
            height=36,
            font=self.controlador.font_corpo, # Usar fonte do controlador
            fg_color=CORES["fundo_escuro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        hint_num = ctk.CTkLabel(
            frame_entradas,
            text="💡 Maior → menor grau (Ex: 1 2 3)",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        )
        hint_num.grid(row=3, column=0, sticky="w", pady=(0, 15), padx=15)
        
        # Denominador
        ctk.CTkLabel(
            frame_entradas,
            text="Denominador:",
            font=self.controlador.font_label, # Usar fonte do controlador
            text_color=CORES["texto_principal"]
        ).grid(row=4, column=0, sticky="w", pady=(5, 5), padx=15)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entradas,
            placeholder_text="Ex: 1 4 5 2 0",
            height=36,
            font=self.controlador.font_corpo, # Usar fonte do controlador
            fg_color=CORES["fundo_escuro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        hint_den = ctk.CTkLabel(
            frame_entradas,
            text="💡 Maior → menor grau (Ex: 1 5 6)",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        )
        hint_den.grid(row=6, column=0, sticky="w", pady=(0, 15), padx=15)
        
        # === BOTÕES ===
        frame_botoes = ctk.CTkFrame(
            scroll_container,
            fg_color="transparent"
        )
        frame_botoes.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        frame_botoes.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(
            frame_botoes,
            text="📊 Análise Completa",
            command=self.analisar_completo,
            height=45,
            font=self.controlador.font_corpo, # Usar fonte do controlador
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).grid(row=0, column=0, sticky="ew", padx=0, pady=5)
        
        ctk.CTkButton(
            frame_botoes,
            text="📈 Plotar Root Locus",
            command=self.plotar_lgr,
            height=45,
            font=self.controlador.font_corpo, # Usar fonte do controlador
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).grid(row=1, column=0, sticky="ew", padx=0, pady=5)
        
        ctk.CTkButton(
            frame_botoes,
            text="🗑️ Limpar",
            command=self.limpar_tudo,
            height=45,
            font=self.controlador.font_corpo, # Usar fonte do controlador
            fg_color=CORES["terciaria"],
            hover_color=CORES["terciaria_hover"],
            corner_radius=8
        ).grid(row=2, column=0, sticky="ew", padx=0, pady=5)
        
        # === ÁREA DE RESULTADOS ===
        frame_resultados = ctk.CTkFrame(
            scroll_container,
            fg_color=CORES["fundo_claro"],
            corner_radius=10
        )
        frame_resultados.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        frame_resultados.grid_columnconfigure(0, weight=1)
        frame_resultados.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_resultados,
            text="📋 Resultados da Análise",
            font=self.controlador.font_corpo, # Usar fonte do controlador
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=10, padx=15)
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados,
            font=self.controlador.font_pequeno, # Usar fonte do controlador
            fg_color=CORES["fundo_escuro"],
            border_color=CORES["borda"],
            border_width=1,
            wrap="word",
            height=350
        )
        self.texto_resultados.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        
        self._adicionar_instrucoes_iniciais()
    
    def criar_painel_direito(self, parent):
        """Cria o painel direito com gráfico"""
        frame_direito = ctk.CTkFrame(
            parent,
            fg_color=CORES["acento"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["primaria"]
        )
        frame_direito.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        frame_direito.grid_columnconfigure(0, weight=1)
        frame_direito.grid_rowconfigure(1, weight=1)
        
        # Título
        ctk.CTkLabel(
            frame_direito,
            text="📈 GRÁFICO DO LUGAR GEOMÉTRICO DAS RAÍZES",
            font=self.controlador.font_subtitulo, # Usar fonte do controlador
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=15, padx=20)
        
        # Frame do gráfico
        self.frame_grafico = ctk.CTkFrame(
            frame_direito,
            fg_color=CORES["fundo_claro"],
            corner_radius=10
        )
        self.frame_grafico.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.frame_grafico.grid_columnconfigure(0, weight=1)
        self.frame_grafico.grid_rowconfigure(0, weight=1)
        
        # Container do gráfico
        self.grafico_container = ctk.CTkFrame(
            self.frame_grafico,
            fg_color=CORES["fundo_claro"]
        )
        self.grafico_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.grafico_container.grid_columnconfigure(0, weight=1)
        self.grafico_container.grid_rowconfigure(0, weight=1)
        
        # Label inicial
        self.label_sem_grafico = ctk.CTkLabel(
            self.grafico_container,
            text="📊\n\nClique em 'Plotar Root Locus'\npara visualizar o lugar geométrico das raízes",
            font=self.controlador.font_corpo, # Usar fonte do controlador
            text_color=CORES["texto_secundario"],
            justify="center"
        )
        self.label_sem_grafico.grid(row=0, column=0)
    
    def _adicionar_instrucoes_iniciais(self):
        """Adiciona instruções iniciais no textbox"""
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", "📌 INSTRUÇÕES DE USO\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n\n")
        self.texto_resultados.insert("end", "1. PREENCHA OS CAMPOS:\n")
        self.texto_resultados.insert("end", "   • Numerador: Coeficientes do numerador\n")
        self.texto_resultados.insert("end", "   • Denominador: Coeficientes do denominador\n\n")
        self.texto_resultados.insert("end", "2. CLIQUE EM UMA ANÁLISE:\n")
        self.texto_resultados.insert("end", "   • 📊 Análise Completa: Relatório detalhado\n")
        self.texto_resultados.insert("end", "   • 📈 Plotar Root Locus: Visualização gráfica\n\n")
        self.texto_resultados.insert("end", "3. FORMATO:\n")
        self.texto_resultados.insert("end", "   • Separe números com ESPAÇO\n")
        self.texto_resultados.insert("end", "   • Use ponto (.) para decimais\n")
        self.texto_resultados.insert("end", "   • Do MAIOR para o MENOR grau\n\n")
        self.texto_resultados.insert("end", "✅ EXEMPLO:\n")
        self.texto_resultados.insert("end", "   Numerador:   1\n")
        self.texto_resultados.insert("end", "   Denominador: 1 4 5 2 0\n")
        self.texto_resultados.insert("end", "   G(s) = 1/(s⁴+4s³+5s²+2s)\n")
    
    def obter_coeficientes(self):
        """Obtém e valida os coeficientes"""
        try:
            texto_num = self.entrada_numerador.get().strip()
            texto_den = self.entrada_denominador.get().strip()
            
            if not texto_num or not texto_den:
                raise ValueError("❌ Por favor, preencha ambos os campos!")
            
            try:
                numerador = [float(x) for x in texto_num.split()]
            except ValueError:
                raise ValueError(f"❌ Erro no NUMERADOR!\nValor: '{texto_num}'\nUse apenas números.")
            
            try:
                denominador = [float(x) for x in texto_den.split()]
            except ValueError:
                raise ValueError(f"❌ Erro no DENOMINADOR!\nValor: '{texto_den}'\nUse apenas números.")
            
            if len(numerador) == 0:
                raise ValueError("❌ Numerador não pode estar vazio!")
            
            if len(denominador) == 0:
                raise ValueError("❌ Denominador não pode estar vazio!")
            
            if abs(denominador[0]) < 1e-15:
                raise ValueError("❌ Primeiro coeficiente do denominador não pode ser zero!")
            
            # Salvar no contexto
            if hasattr(self.controlador, 'contexto_sistema'):
                self.controlador.contexto_sistema["num"] = numerador
                self.controlador.contexto_sistema["den"] = denominador
            
            return numerador, denominador
            
        except ValueError as e:
            raise e
    
    def analisar_completo(self):
        """Realiza análise completa do LGR"""
        try:
            numerador, denominador = self.obter_coeficientes()
            
            # Configurar e analisar
            self.analisador.configurar_sistema(numerador, denominador)
            relatorio = self.analisador.gerar_relatorio_completo()
            
            # Exibir resultados
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", relatorio)
            
            logger.info("Análise LGR completa realizada")
            
        except (ValueError, ErroValidacaoLGR) as e:
            self.mostrar_erro(str(e))
        except Exception as e:
            self.mostrar_erro(f"Erro inesperado: {str(e)}")
            logger.error(f"Erro na análise LGR: {e}", exc_info=True)
    
    # ================== FUNÇÃO PLOTAR ATUALIZADA ==================
    def plotar_lgr(self):
        """Plota o gráfico do Lugar Geométrico das Raízes com análise completa tipo MATLAB"""
        try:
            numerador, denominador = self.obter_coeficientes()
            
            # Configurar sistema
            self.analisador.configurar_sistema(numerador, denominador)
            
            # Limpar gráfico anterior
            if self.canvas_grafico:
                self.canvas_grafico.get_tk_widget().destroy()
                self.canvas_grafico = None
            
            if self.label_sem_grafico:
                self.label_sem_grafico.destroy()
                self.label_sem_grafico = None
            
            # Criar sistema de transferência
            sistema = matlab.tf(numerador, denominador)
            
            # Criar figura com fundo branco para melhor visualização
            fig = plt.figure(figsize=(10, 8), facecolor='white')
            ax = fig.add_subplot(111, facecolor='white')
            
            matlab.rlocus(sistema, plot=True, ax=ax, grid=False)
            
            assint = self.analisador.calcular_assintotas()
            if assint['numero'] > 0:
                ax_limits = ax.axis()
                L = max(abs(lim) for lim in ax_limits) * 3
                sigma = assint['sigma']
                
                for angulo in assint['angulos']:
                    ang_rad = np.deg2rad(angulo)
                    x = [sigma, sigma + L * np.cos(ang_rad)]
                    y = [0, L * np.sin(ang_rad)]
                    ax.plot(x, y, '--', color='gray', linewidth=1.5, alpha=0.4, label='Assíntotas' if angulo == assint['angulos'][0] else '')
            
            segmentos_real = self.analisador.obter_segmentos_eixo_real()
            for idx, seg in enumerate(segmentos_real):
                ax.plot([seg['inicio'], seg['fim']], [0, 0], 
                       'b-', linewidth=6, alpha=0.3, 
                       label='Segmentos no Eixo Real' if idx == 0 else '')
            
            linhas_partida = self.analisador.obter_linhas_angulos_partida(comprimento=1.2)
            for idx, (polo, linha) in enumerate(linhas_partida.items()):
                ax.plot([linha['inicio'][0], linha['fim'][0]], 
                       [linha['inicio'][1], linha['fim'][1]], 
                       'g--', linewidth=2.5, alpha=0.7, 
                       label='Ângulo de Partida' if idx == 0 else '')
                # Adicionar texto com o ângulo
                ax.annotate(f"{linha['angulo']:.1f}°", 
                           xy=(linha['fim'][0], linha['fim'][1]),
                           xytext=(8, 8), textcoords='offset points',
                           fontsize=9, color='green', fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='green'))
            
            linhas_chegada = self.analisador.obter_linhas_angulos_chegada(comprimento=1.2)
            for idx, (zero, linha) in enumerate(linhas_chegada.items()):
                ax.plot([linha['inicio'][0], linha['fim'][0]], 
                       [linha['inicio'][1], linha['fim'][1]], 
                       'orange', linestyle='--', linewidth=2.5, alpha=0.7, 
                       label='Ângulo de Chegada' if idx == 0 else '')
                # Adicionar texto com o ângulo
                ax.annotate(f"{linha['angulo']:.1f}°", 
                           xy=(linha['inicio'][0], linha['inicio'][1]),
                           xytext=(8, 8), textcoords='offset points',
                           fontsize=9, color='orange', fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='orange'))
            
            cruzamento = self.analisador.calcular_cruzamento_eixo_imaginario()
            if cruzamento:
                for idx, ponto in enumerate(cruzamento['cruzamentos']):
                    ax.plot(ponto.real, ponto.imag, 'r*', markersize=18, markeredgewidth=2,
                           label=f'Cruzamento (K={cruzamento["k_critico"]:.2f})' if idx == 0 else '')
                    # Desenhar linha horizontal no cruzamento
                    xlim = ax.get_xlim()
                    ax.plot(xlim, [ponto.imag, ponto.imag], 'r--', linewidth=1.5, alpha=0.5)
                    # Adicionar anotação
                    ax.annotate(f'K={cruzamento["k_critico"]:.2f}', 
                               xy=(ponto.real, ponto.imag),
                               xytext=(15, 0), textcoords='offset points',
                               fontsize=9, color='red', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red'))
            
            # Configurações finais do gráfico
            ax.axhline(y=0, color='k', linewidth=0.8, alpha=0.5)
            ax.axvline(x=0, color='k', linewidth=0.8, alpha=0.5)
            ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
            ax.set_xlabel('Eixo Real', fontsize=12, fontweight='bold', color='black')
            ax.set_ylabel('Eixo Imaginário', fontsize=12, fontweight='bold', color='black')
            ax.set_title('Lugar Geométrico das Raízes (Root Locus)', fontsize=14, fontweight='bold', color='black', pad=15)
            
            # Configurar cores dos eixos e texto
            ax.tick_params(axis='both', colors='black', labelsize=10)
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(1.2)
            
            # Legenda com fundo branco
            legend = ax.legend(loc='best', fontsize=9, framealpha=0.9, facecolor='white', edgecolor='black')
            for text in legend.get_texts():
                text.set_color('black')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Incorporar na interface
            self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.grafico_container)
            self.canvas_grafico.draw()
            
            canvas_widget = self.canvas_grafico.get_tk_widget()
            canvas_widget.grid(row=0, column=0, sticky="nsew")
            
            # Adicionar toolbar
            toolbar_frame = ctk.CTkFrame(self.grafico_container, fg_color="transparent")
            toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
            toolbar = NavigationToolbar2Tk(self.canvas_grafico, toolbar_frame)
            toolbar.update()
            
            plt.close(fig)
            
            logger.info("Gráfico LGR plotado com sucesso")
            
        except (ValueError, ErroValidacaoLGR) as e:
            self.mostrar_erro(str(e))
        except Exception as e:
            self.mostrar_erro(f"Erro ao plotar: {str(e)}")
            logger.error(f"Erro ao plotar LGR: {e}", exc_info=True)
    # =======================================================
    
    def limpar_tudo(self):
        """Limpa todas as entradas e resultados"""
        self.entrada_numerador.delete(0, "end")
        self.entrada_denominador.delete(0, "end")
        self.entrada_numerador.focus()
        
        # Limpar gráfico
        if self.canvas_grafico:
            self.canvas_grafico.get_tk_widget().destroy()
            self.canvas_grafico = None
        
        # Recriar label
        if not self.label_sem_grafico:
            self.label_sem_grafico = ctk.CTkLabel(
                self.grafico_container,
                text="📊\n\nClique em 'Plotar Root Locus'\npara visualizar o lugar geométrico das raízes",
                font=self.controlador.font_corpo, # Usar fonte do controlador
                text_color=CORES["texto_secundario"],
                justify="center"
            )
            self.label_sem_grafico.grid(row=0, column=0)
        
        self._adicionar_instrucoes_iniciais()
        
        logger.info("Interface LGR limpa")
    
    def mostrar_erro(self, mensagem):
        """Exibe mensagem de erro"""
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", f"{mensagem}\n\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n")
        self.texto_resultados.insert("end", "💡 DICAS:\n")
        self.texto_resultados.insert("end", "=" * 70 + "\n")
        self.texto_resultados.insert("end", "✓ Use apenas números (inteiros ou decimais)\n")
        self.texto_resultados.insert("end", "✓ Separe por ESPAÇO\n")
        self.texto_resultados.insert("end", "✓ Use ponto (.) para decimais\n")
        self.texto_resultados.insert("end", "✓ Primeiro coeficiente ≠ 0\n")
        self.texto_resultados.insert("end", "✓ Maior → menor grau\n\n")
        self.texto_resultados.insert("end", "📝 EXEMPLO:\n")
        self.texto_resultados.insert("end", "   Numerador:   1\n")
        self.texto_resultados.insert("end", "   Denominador: 1 4 5 2 0\n")


if __name__ == "__main__":
    try:
        # Configurar DPI awareness antes de criar a janela
        if platform.system() == "Windows":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDPIAwareness(1)
            except:
                pass
        
        app = SistemaTCC()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
