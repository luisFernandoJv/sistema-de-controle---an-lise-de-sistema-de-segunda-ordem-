import customtkinter as ctk
from PIL import Image, ImageTk
import os
from criterios_estabilidade import CriteriosEstabilidade
from analise_segunda_ordem import AnalisadorSegundaOrdem
from controladores import JanelaControladores  # Importação do módulo de controladores

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
        try:
            # Tentar carregar logo se existir
            if os.path.exists("logo.png"):
                imagem_pil = Image.open("logo.png")
                largura, altura = imagem_pil.size
                self.foto_fundo = ctk.CTkImage(
                    light_image=imagem_pil,
                    dark_image=imagem_pil,
                    size=(largura, altura)
                )
            else:
                self.foto_fundo = None
        except Exception as e:
            self.foto_fundo = None
            print(f"Imagem de fundo não encontrada: {e}. Continuando sem imagem.")
    
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
            # Usar a classe JanelaControladores importada
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
            height=100,
            corner_radius=0
        )
        frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame_cabecalho.grid_columnconfigure(0, weight=1)
        
        # Título principal
        titulo = ctk.CTkLabel(
            frame_cabecalho,
            text="FERRAMENTA COMPUTACIONAL PARA ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE",
            font=("Segoe UI", 20, "bold"),
            text_color=CORES["texto_principal"],
            wraplength=900
        )
        titulo.grid(row=0, column=0, pady=(15, 5), padx=20)
        
        # Subtítulo
        subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Trabalho de Conclusão de Curso - Engenharia de Computação",
            font=("Segoe UI", 13),
            text_color=CORES["texto_secundario"]
        )
        subtitulo.grid(row=1, column=0, pady=(0, 15))
    
    def criar_conteudo_principal(self):
        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_rowconfigure(1, weight=1)
        
        # Imagem de fundo (se existir)
        if self.controlador.foto_fundo:
            label_fundo = ctk.CTkLabel(frame_principal, image=self.controlador.foto_fundo, text="")
            label_fundo.place(relwidth=1, relheight=1)
            label_fundo.lower()
        
        # Frame dos botões
        frame_botoes = ctk.CTkFrame(
            frame_principal, 
            fg_color=CORES["fundo_claro"],
            corner_radius=15,
            border_width=2,
            border_color=CORES["borda"]
        )
        frame_botoes.grid(row=0, column=0, pady=50, padx=20, sticky="n")
        
        # Título da seção
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
        
        # Informações dos botões - CORRIGIDO: controladores agora chama diretamente a classe
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
        
        # Criar botões
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
        
        # Container interno para melhor organização
        container_rodape = ctk.CTkFrame(frame_rodape, fg_color="transparent")
        container_rodape.pack(fill="x", padx=20, pady=15)
        
        # Informações do aluno
        informacao_aluno = ctk.CTkLabel(
            container_rodape,
            text="Aluno: Luís Fernando Alexandre dos Santos | Orientador: Prof. Dr. Cecilio Martins de Sousa Neto",
            font=("Segoe UI", 11),
            text_color=CORES["texto_secundario"]
        )
        informacao_aluno.pack(side="left")
        
        # Ano e instituição
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
        self.geometry("1000x800")
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
        
        largura = 1000
        altura = 800
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
        
        # Título
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
        
        # Área de entrada
        frame_entrada = ctk.CTkFrame(
            frame_conteudo,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_entrada.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        frame_entrada.grid_columnconfigure(1, weight=1)
        
        # Entrada do Numerador
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
        
        # Entrada do Denominador
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
        
        # Botões de ação
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
            text="Apenas Routh-Hurwitz", 
            command=self.analisar_routh_hurwitz, 
            width=200,
            height=48,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes, 
            text="Analisar Nyquist", 
            command=self.analisar_nyquist, 
            width=170,
            height=48,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes, 
            text="Lugar das Raízes", 
            command=self.analisar_lugar_raizes, 
            width=170,
            height=48,
            font=("Segoe UI", 13, "bold"),
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        # Área de resultados
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
            
            if not texto_num or not texto_den:
                raise ValueError("Por favor, preencha ambos os campos: numerador e denominador.")
            
            numerador = [float(x) for x in texto_num.split()]
            denominador = [float(x) for x in texto_den.split()]
            
            return numerador, denominador
            
        except ValueError as e:
            raise ValueError("Erro na entrada de dados. Use números separados por espaço.")
    
    def analisar_sistema_completo(self):
        """Análise completa do sistema"""
        try:
            numerador, denominador = self.obter_coeficientes()
            resultado = CriteriosEstabilidade.analisar_sistema_completo(numerador, denominador)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except Exception as e:
            self.mostrar_erro(str(e))
    
    def analisar_routh_hurwitz(self):
        """Apenas análise Routh-Hurwitz"""
        try:
            numerador, denominador = self.obter_coeficientes()
            resultado = CriteriosEstabilidade.gerar_relatorio_routh_hurwitz(denominador)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except Exception as e:
            self.mostrar_erro(str(e))
    
    def analisar_nyquist(self):
        """Análise de Nyquist"""
        try:
            numerador, denominador = self.obter_coeficientes()
            resultado = CriteriosEstabilidade.analisar_nyquist(numerador, denominador)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except Exception as e:
            self.mostrar_erro(str(e))
    
    def analisar_lugar_raizes(self):
        """Análise do Lugar das Raízes"""
        try:
            numerador, denominador = self.obter_coeficientes()
            resultado = CriteriosEstabilidade.lugar_das_raizes(numerador, denominador)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except Exception as e:
            self.mostrar_erro(str(e))
    
    def mostrar_erro(self, mensagem):
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", f"❌ ERRO: {mensagem}")

class JanelaAnalise(JanelaBase):
    def __init__(self, parent, titulo):
        super().__init__(parent, titulo)
        self.analisador = AnalisadorSegundaOrdem()
    
    def criar_conteudo(self):
        # Criar scrollable frame para todo o conteúdo
        frame_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color=CORES["fundo_claro"],
            corner_radius=10
        )
        frame_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        frame_scroll.grid_columnconfigure(0, weight=1)
        
        # Seleção do tipo de malha
        frame_tipo_malha = ctk.CTkFrame(
            frame_scroll,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_tipo_malha.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        frame_tipo_malha.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_tipo_malha,
            text="🔄 Tipo de Sistema:",
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=15, padx=20)
        
        frame_radio = ctk.CTkFrame(frame_tipo_malha, fg_color="transparent")
        frame_radio.grid(row=1, column=0, sticky="w", pady=(0, 15), padx=20)
        
        self.tipo_malha = ctk.StringVar(value="fechada")
        
        ctk.CTkRadioButton(
            frame_radio,
            text="Malha Fechada",
            variable=self.tipo_malha,
            value="fechada",
            font=("Segoe UI", 13, "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            frame_radio,
            text="Malha Aberta",
            variable=self.tipo_malha,
            value="aberta",
            font=("Segoe UI", 13, "bold"),
            text_color=CORES["texto_principal"],
            fg_color=CORES["secundaria"],
            hover_color=CORES["secundaria_hover"]
        ).pack(side="left", padx=10)
        
        # Área de entrada da função de transferência
        frame_entrada = ctk.CTkFrame(
            frame_scroll,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_entrada.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 20))
        frame_entrada.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_entrada,
            text="📐 Função de Transferência de 2ª Ordem:",
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=15, padx=20)
        
        # Entrada do Numerador
        ctk.CTkLabel(
            frame_entrada, 
            text="Numerador:", 
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=1, column=0, sticky="w", pady=8, padx=20)
        
        self.entrada_numerador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 100 (para K·ωn²)",
            width=350,
            height=42,
            font=("Segoe UI", 12),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_numerador.grid(row=1, column=1, sticky="w", padx=20, pady=8)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Coeficientes separados por espaço (do maior para o menor grau)",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        ).grid(row=2, column=1, sticky="w", padx=20, pady=(0, 8))
        
        # Entrada do Denominador
        ctk.CTkLabel(
            frame_entrada, 
            text="Denominador:", 
            font=("Segoe UI", 14, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=3, column=0, sticky="w", pady=8, padx=20)
        
        self.entrada_denominador = ctk.CTkEntry(
            frame_entrada, 
            placeholder_text="Ex: 1 10 100 (para s² + 10s + 100)",
            width=350,
            height=42,
            font=("Segoe UI", 12),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"]
        )
        self.entrada_denominador.grid(row=3, column=1, sticky="w", padx=20, pady=8)
        
        ctk.CTkLabel(
            frame_entrada, 
            text="Coeficientes separados por espaço (do maior para o menor grau)",
            font=("Segoe UI", 10),
            text_color=CORES["texto_secundario"]
        ).grid(row=4, column=1, sticky="w", padx=20, pady=(0, 15))
        
        # Botão de análise
        ctk.CTkButton(
            frame_entrada,
            text="▶ Analisar Sistema Completo",
            command=self.analisar_sistema,
            width=250,
            height=50,
            font=("Segoe UI", 14, "bold"),
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            corner_radius=8
        ).grid(row=5, column=0, columnspan=2, pady=(10, 20))
        
        # Área de resultados com melhor visualização
        frame_resultados = ctk.CTkFrame(
            frame_scroll,
            fg_color=CORES["acento"],
            corner_radius=10
        )
        frame_resultados.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 20))
        frame_resultados.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_resultados,
            text="📊 Resultados da Análise:",
            font=("Segoe UI", 16, "bold"),
            text_color=CORES["texto_principal"]
        ).grid(row=0, column=0, sticky="w", pady=12, padx=20)
        
        # Textbox para resultados com altura fixa
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados,
            font=("Consolas", 11),
            fg_color=CORES["fundo_claro"],
            border_color=CORES["borda"],
            border_width=1,
            wrap="word",
            height=400
        )
        self.texto_resultados.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=15)
        self.texto_resultados.insert("1.0", "Os resultados da análise aparecerão aqui...\n\n")
        self.texto_resultados.insert("end", "📐 ENTRADA DA FUNÇÃO DE TRANSFERÊNCIA:\n")
        self.texto_resultados.insert("end", "Digite os coeficientes do numerador e denominador\n\n")
        self.texto_resultados.insert("end", "Exemplos:\n")
        self.texto_resultados.insert("end", "• Numerador: 100 (para K·ωn² = 100)\n")
        self.texto_resultados.insert("end", "• Denominador: 1 10 100 (para s² + 10s + 100)\n\n")
        self.texto_resultados.insert("end", "O sistema irá extrair automaticamente:\n")
        self.texto_resultados.insert("end", "• Frequência Natural (ωn)\n")
        self.texto_resultados.insert("end", "• Coeficiente de Amortecimento (ζ)\n")
        self.texto_resultados.insert("end", "• Ganho (K)\n\n")
        self.texto_resultados.insert("end", "Selecione o tipo de malha e clique em 'Analisar Sistema Completo'")
    
    def obter_coeficientes(self):
        """Obtém e valida os coeficientes do usuário"""
        try:
            texto_num = self.entrada_numerador.get().strip()
            texto_den = self.entrada_denominador.get().strip()
            
            if not texto_num or not texto_den:
                raise ValueError("Por favor, preencha ambos os campos: numerador e denominador.")
            
            numerador = [float(x) for x in texto_num.split()]
            denominador = [float(x) for x in texto_den.split()]
            
            # Verificar se o denominador é de segunda ordem
            if len(denominador) != 3:
                raise ValueError(f"O denominador deve ter 3 coeficientes (sistema de 2ª ordem).\nVocê forneceu {len(denominador)} coeficiente(s).")
            
            return numerador, denominador
            
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError("Erro na entrada de dados. Use números separados por espaço.")
            raise e
    
    def analisar_sistema(self):
        """Realiza a análise completa do sistema"""
        try:
            numerador, denominador = self.obter_coeficientes()
            tipo_malha = self.tipo_malha.get()
            
            # Usar o método que extrai os parâmetros da função de transferência
            resultado = self.analisador.analisar_de_funcao_transferencia(numerador, denominador, tipo_malha)
            
            self.texto_resultados.delete("1.0", "end")
            self.texto_resultados.insert("1.0", resultado)
            
        except Exception as e:
            self.mostrar_erro(str(e))
    
    def mostrar_erro(self, mensagem):
        self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("1.0", f"❌ ERRO: {mensagem}")

# Executar a aplicação
if __name__ == "__main__":
    app = SistemaTCC()
    app.mainloop()