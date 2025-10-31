import customtkinter as ctk
from PIL import Image, ImageTk
import os
from criterios_estabilidade import CriteriosEstabilidade, ErroValidacao
from analise_segunda_ordem import AnalisadorSegundaOrdem, ErroValidacao as ErroValidacao2
from controladores import JanelaControladores
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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

class SistemaTCC(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela principal
        self.title("FERRAMENTA COMPUTACIONAL PARA ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE")
        self.geometry("1000x700")
        
        # Configurações de tamanho
        self.maxsize(width=1200, height=800)
        self.minsize(width=800, height=600)
        
        # Aplicar cor de fundo
        self.configure(fg_color=CORES["fundo_escuro"])
        
        # Centralizar janela
        self.centralizar_janela()
        
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
        
        # Dicionário para armazenar janelas abertas
        self.janelas_abertas = {}
        
        # Criar tela principal
        self.tela_principal = TelaPrincipal(parent=self.container, controlador=self)
        self.tela_principal.grid(row=0, column=0, sticky="nsew")
    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f'{largura}x{altura}+{x}+{y}')
    
    def carregar_imagens(self):
        """Carrega as imagens utilizadas no sistema"""
        self.foto_fundo = None
        self.logo_image = None

        # Carregar Logo
        try:
            if os.path.exists("logo.png"):
                img_pil = Image.open("logo.png").convert("RGBA")
                max_h_logo = 60
                ratio = min(1.0, max_h_logo / img_pil.height)
                new_size = (int(img_pil.width * ratio), int(img_pil.height * ratio))
                img_pil_resized = img_pil.resize(new_size, Image.Resampling.LANCZOS)
                self.logo_image = ctk.CTkImage(light_image=img_pil_resized, dark_image=img_pil_resized, size=new_size)
        except Exception as e:
            print(f"Erro ao carregar logo.png: {e}")
            self.logo_image = None

    
    def abrir_janela(self, tipo_janela, titulo):
        """Abre uma nova janela do tipo especificado"""
        if tipo_janela in self.janelas_abertas:
            try:
                self.janelas_abertas[tipo_janela].destroy()
            except:
                pass
        
        if tipo_janela == "criterio":
            janela = JanelaCriterio(self, titulo)
        elif tipo_janela == "analise":
            janela = JanelaAnalise(self, titulo)
        elif tipo_janela == "controladores":
            janela = JanelaControladores(self)
        else:
            return
        
        self.janelas_abertas[tipo_janela] = janela
        janela.focus_set()

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
        frame_cabecalho = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=140,
            corner_radius=0
        )
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame_cabecalho.grid_columnconfigure(0, weight=1)
        frame_cabecalho.grid_rowconfigure(0, weight=1)
        
        container_principal = ctk.CTkFrame(frame_cabecalho, fg_color="transparent")
        container_principal.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
        container_principal.grid_columnconfigure(0, weight=3)
        container_principal.grid_columnconfigure(1, weight=1)
        
        # LADO ESQUERDO - TÍTULO E INFORMAÇÕES
        container_titulo = ctk.CTkFrame(container_principal, fg_color="transparent")
        container_titulo.grid(row=0, column=0, sticky="w", padx=0, pady=0)
        
        titulo_principal = ctk.CTkLabel(
            container_titulo,
            text="FERRAMENTA COMPUTACIONAL PARA ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE",
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"],
            wraplength=600,
            justify="left"
        )
        titulo_principal.pack(anchor="w", pady=(0, 5))
        
        linha_divisoria = ctk.CTkFrame(
            container_titulo,
            height=2,
            fg_color=CORES["primaria"],
            corner_radius=1
        )
        linha_divisoria.pack(fill="x", pady=8)
        
        subtitulo = ctk.CTkLabel(
            container_titulo,
            text="Trabalho de Conclusão de Curso - Engenharia de Computação",
            font=("Segoe UI", 13, "bold"),
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
        
        texto_institucional = ctk.CTkLabel(
            container_logo_interno,
            text="UFERSA\nUniversidade Federal Rural do Semi-Árido",
            font=("Segoe UI", 10, "bold"),
            text_color=CORES["texto_secundario"],
            justify="center"
        )
        texto_institucional.pack()
    
    def criar_conteudo_principal(self):
        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_rowconfigure(1, weight=1)
        
        if self.controlador.foto_fundo:
            label_fundo = ctk.CTkLabel(frame_principal, image=self.controlador.foto_fundo, text="")
            label_fundo.place(relwidth=1, relheight=1)
            label_fundo.lower()
        
        frame_botoes = ctk.CTkFrame(
            frame_principal, 
            fg_color=CORES["fundo_claro"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["borda"]
        )
        frame_botoes.grid(row=0, column=0, pady=50, padx=20, sticky="n")
        
        ctk.CTkLabel(
            frame_botoes,
            text="MÓDULOS DO SISTEMA",
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            frame_botoes,
            text="Selecione o módulo desejado para análise",
            font=("Segoe UI", 12),
            text_color=CORES["texto_secundario"]
        ).pack(pady=(0, 20))
        
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
                width=400,
                height=65,
                font=("Segoe UI", 16, "bold"),
                corner_radius=10,
                fg_color=info["cor"],
                hover_color=info["cor_hover"],
                border_width=0,
                anchor="center"
            )
            botao.pack(pady=12, padx=30)
    
    def criar_rodape(self):
        frame_rodape = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=70,
            corner_radius=0
        )
        frame_rodape.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        frame_rodape.grid_columnconfigure(0, weight=1)
        
        container_rodape = ctk.CTkFrame(frame_rodape, fg_color="transparent")
        container_rodape.pack(fill="x", padx=20, pady=15)
        
        informacao_aluno = ctk.CTkLabel(
            container_rodape,
            text="Aluno: Luís Fernando Alexandre dos Santos | Orientador: Prof. Dr. Cecilio Martins de Sousa Neto",
            font=("Segoe UI", 11),
            text_color=CORES["texto_secundario"]
        )
        informacao_aluno.pack(side="left")
        
        ano = ctk.CTkLabel(
            container_rodape,
            text="2025 - Universidade Federal Rural do Semi-Árido",
            font=("Segoe UI", 11, "bold"),
            text_color=CORES["texto_secundario"]
        )
        ano.pack(side="right")

class JanelaBase(ctk.CTkToplevel):
    def __init__(self, parent, titulo):
        super().__init__(parent)
        self.parent = parent
        self.titulo = titulo
        
        self.title(titulo)
        self.geometry("1400x900")
        self.resizable(True, True)
        self.configure(fg_color=CORES["fundo_escuro"])
        
        self.centralizar_janela()
        self.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.criar_cabecalho()
        self.criar_conteudo()
    
    def centralizar_janela(self):
        self.update_idletasks()
        x_pai = self.parent.winfo_x()
        y_pai = self.parent.winfo_y()
        largura_pai = self.parent.winfo_width()
        altura_pai = self.parent.winfo_height()
        
        largura = 1400
        altura = 900
        x = x_pai + (largura_pai - largura) // 2
        y = y_pai + (altura_pai - altura) // 2
        
        self.geometry(f'{largura}x{altura}+{x}+{y}')
    
    def criar_cabecalho(self):
        frame_cabecalho = ctk.CTkFrame(
            self, 
            fg_color=CORES["acento"],
            height=70,
            corner_radius=0
        )
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame_cabecalho.grid_columnconfigure(1, weight=1)
        
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
        
        label_titulo = ctk.CTkLabel(
            frame_cabecalho,
            text=self.titulo,
            font=("Segoe UI", 22, "bold"),
            text_color=CORES["texto_principal"]
        )
        label_titulo.grid(row=0, column=1, pady=15)
    
    def criar_conteudo(self):
        pass
    
    def fechar_janela(self):
        self.destroy()

class JanelaCriterio(JanelaBase):
    def __init__(self, parent, titulo):
        super().__init__(parent, titulo)
        self.numerador = []
        self.denominador = []
    
    def criar_conteudo(self):
        frame_conteudo = ctk.CTkFrame(self, fg_color=CORES["fundo_claro"])
        frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        frame_conteudo.grid_columnconfigure(0, weight=1)
        frame_conteudo.grid_rowconfigure(2, weight=1)
        
        frame_entrada = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_entrada.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        frame_entrada.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Numerador:", 
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=8, padx=15)
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 3 (para s + 3)",
            width=350,
            height=42,
            font=("Segoe UI", 12),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=0, column=1, sticky="w", padx=15, pady=8)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Coeficientes separados por espaço (do maior para o menor grau)",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        ).grid(row=1, column=1, sticky="w", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Denominador:", 
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=2, column=0, sticky="w", pady=8, padx=15)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 5 6 (para s² + 5s + 6)",
            width=350,
            height=42,
            font=("Segoe UI", 12),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=2, column=1, sticky="w", padx=15, pady=8)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Coeficientes separados por espaço (do maior para o menor grau)",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        ).grid(row=3, column=1, sticky="w", padx=15, pady=(0, 15))
        
        frame_botoes = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_botoes.grid(row=1, column=0, sticky="w", padx=20, pady=15)
        
        ctk.CTkButton(
            frame_botoes, 
            text="Analisar Sistema Completo", 
            command=self.analisar_sistema_completo, 
            width=220,
            height=48,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes, 
            text="Critério Routh-Hurwitz", 
            command=self.analisar_routh_hurwitz, 
            width=200,
            height=48,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        frame_resultados = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_resultados.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        frame_resultados.grid_columnconfigure(0, weight=1)
        frame_resultados.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_resultados, 
            text="📋 Resultados da Análise:", 
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=12, padx=15)
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados, 
            font=("Consolas", 11),
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
            
            # Validação básica de preenchimento
            if not texto_num or not texto_den:
                raise ValueError("❌ Por favor, preencha ambos os campos:\n   • Numerador\n   • Denominador")
            
            # Tentar converter para números
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
            
            # Validações específicas
            if len(numerador) == 0:
                raise ValueError("❌ Numerador não pode estar vazio!")
            
            if len(denominador) == 0:
                raise ValueError("❌ Denominador não pode estar vazio!")
            
            # Verificar se o primeiro coeficiente do denominador não é zero
            if abs(denominador[0]) < 1e-15:
                raise ValueError(
                    "❌ O primeiro coeficiente do DENOMINADOR não pode ser ZERO!\n"
                    f"   Valor inserido: {denominador}\n"
                    f"   O coeficiente do termo de maior grau deve ser diferente de zero.\n"
                    f"   Exemplo correto: 1 5 6 (não 0 5 6)"
                )
            
            # Verificar se todos os coeficientes do denominador são zero
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
        container_principal = ctk.CTkFrame(self, fg_color="transparent")
        container_principal.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        container_principal.grid_columnconfigure(0, weight=0)
        container_principal.grid_columnconfigure(1, weight=1)
        container_principal.grid_rowconfigure(0, weight=1)
        
        # LADO ESQUERDO
        frame_esquerdo = ctk.CTkFrame(
            container_principal, 
            fg_color=CORES["fundo_claro"],
            corner_radius=10,
            width=450
        )
        frame_esquerdo.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        frame_esquerdo.grid_propagate(False)
        frame_esquerdo.grid_columnconfigure(0, weight=1)
        frame_esquerdo.grid_rowconfigure(1, weight=1)
        
        frame_cabecalho_esq = ctk.CTkFrame(frame_esquerdo, fg_color="transparent")
        frame_cabecalho_esq.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        ctk.CTkLabel(
            frame_cabecalho_esq,
            text="CONFIGURAÇÃO DO SISTEMA",
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w")
        
        scroll_container = ctk.CTkScrollableFrame(
            frame_esquerdo,
            fg_color="transparent",
            height=600
        )
        scroll_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        scroll_container.grid_columnconfigure(0, weight=1)
        
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
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 8))
        
        self.tipo_malha = ctk.StringVar(value="fechada")
        
        ctk.CTkRadioButton(
            frame_malha,
            text="Malha Fechada",
            variable=self.tipo_malha,
            value="fechada",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(anchor="w", pady=4)
        
        ctk.CTkRadioButton(
            frame_malha,
            text="Malha Aberta",
            variable=self.tipo_malha,
            value="aberta",
            font=("Segoe UI", 12, "bold"),
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
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 8))
        
        self.tipo_entrada = ctk.StringVar(value="degrau")
        
        ctk.CTkRadioButton(
            frame_entrada_tipo,
            text="Degrau Unitário",
            variable=self.tipo_entrada,
            value="degrau",
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"]
        ).pack(anchor="w", pady=4)
        
        ctk.CTkRadioButton(
            frame_entrada_tipo,
            text="Rampa Unitária",
            variable=self.tipo_entrada,
            value="rampa",
            font=("Segoe UI", 12, "bold"),
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
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=12, padx=15)
        
        # Numerador
        ctk.CTkLabel(
            frame_entrada, 
            text="Numerador:", 
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=1, column=0, sticky="w", pady=5, padx=15)
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 4",
            height=36,
            font=("Segoe UI", 11),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        # Denominador
        ctk.CTkLabel(
            frame_entrada, 
            text="Denominador:", 
            font=("Segoe UI", 12, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=3, column=0, sticky="w", pady=5, padx=15)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 2 4",
            height=36,
            font=("Segoe UI", 11),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Botões de ação
        frame_botoes = ctk.CTkFrame(frame_entrada, fg_color="transparent")
        frame_botoes.grid(row=5, column=0, pady=(5, 15), padx=15)
        
        ctk.CTkButton(
            frame_botoes,
            text="▶ Analisar Sistema",
            command=self.analisar_sistema,
            width=180,
            height=45,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes,
            text="📊 Plotar Gráfico",
            command=self.plotar_grafico,
            width=160,
            height=45,
            font=("Segoe UI", 13, "bold"),
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
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=10, padx=15)
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados,
            font=("Consolas", 10),
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
        
        # LADO DIREITO - Gráfico
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
            font=("Segoe UI", 16, "bold"),
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
            font=("Segoe UI", 14),
            text_color=CORES["texto_secundario"],
            justify="center"
        )
        self.label_sem_grafico.grid(row=0, column=0, sticky="")
    
    def obter_coeficientes(self):
        """Obtém e valida os coeficientes do usuário"""
        try:
            texto_num = self.entrada_numerador.get().strip()
            texto_den = self.entrada_denominador.get().strip()
            
            # Validação básica de preenchimento
            if not texto_num or not texto_den:
                raise ValueError("❌ Por favor, preencha ambos os campos:\n   • Numerador\n   • Denominador")
            
            # Tentar converter para números
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
            
            # Validações específicas para sistema de 2ª ordem
            if len(denominador) != 3:
                raise ValueError(
                    f"❌ Sistema deve ser de 2ª ORDEM!\n"
                    f"   O denominador deve ter EXATAMENTE 3 coeficientes.\n"
                    f"   Você forneceu {len(denominador)} coeficiente(s): {denominador}\n"
                    f"   Formato correto: a₀s² + a₁s + a₂\n"
                    f"   Exemplo: 1 2 4 (representa s² + 2s + 4)"
                )
            
            # Verificar se o primeiro coeficiente do denominador não é zero
            if abs(denominador[0]) < 1e-15:
                raise ValueError(
                    "❌ O primeiro coeficiente do DENOMINADOR não pode ser ZERO!\n"
                    f"   Valor inserido: {denominador}\n"
                    f"   O coeficiente de s² deve ser diferente de zero.\n"
                    f"   Exemplo correto: 1 2 4 (não 0 2 4)"
                )
            
            # Verificar se todos os coeficientes do denominador são zero
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