"""
Painel de Métricas com Design Python - Azul e Verde
Integra visualização profissional de métricas com tema Python
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from metricas_exportacao import MetricasControlador, ExportadorResultados
import os


class PainelMetricas(ctk.CTkFrame):
    """Painel que exibe métricas lado a lado com design Python elegante"""
    
    CORES_PYTHON = {
        "primario": "#1f77b4",      # Azul Python
        "secundario": "#2ca02c",    # Verde Python
        "destaque": "#ff7f0e",      # Laranja
        "fundo": "#f5f5f5",         # Cinza claro
        "borda": "#cccccc",         # Cinza borda
        "texto_principal": "#1a1a1a",  # Preto
        "texto_secundario": "#363535"  # Cinza texto
    }
    
    def __init__(self, parent, cores, metricas_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.cores = cores
        self.metricas_callback = metricas_callback
        self.metricas_sem = {}
        self.metricas_com = {}
        self.figuras_graficos = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        self.criar_paineis_metricas()
        self.criar_paineis_exportacao()
    
    def criar_paineis_metricas(self):
        """Cria os painéis de visualização com design Python melhorado"""
        
        # Painel esquerdo - Sem Controlador
        frame_sem = ctk.CTkFrame(
            self,
            fg_color="#f0f4f8",
            corner_radius=12,
            border_width=2,
            border_color=self.CORES_PYTHON["primario"]
        )
        frame_sem.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        frame_sem.grid_columnconfigure(0, weight=1)
        frame_sem.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho com emoji
        ctk.CTkLabel(
            frame_sem,
            text="🔓 SISTEMA SEM CONTROLADOR (Malha Aberta)",
            font=("Segoe UI", 13, "bold"),
            text_color=self.CORES_PYTHON["primario"]
        ).grid(row=0, column=0, pady=(12, 8), sticky="w", padx=15)
        
        self.texto_metricas_sem = ctk.CTkTextbox(
            frame_sem,
            font=("Courier New", 10),
            fg_color="#ffffff",
            border_color=self.CORES_PYTHON["borda"],
            border_width=1,
            height=300,
            text_color=self.CORES_PYTHON["texto_principal"]
        )
        self.texto_metricas_sem.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.texto_metricas_sem.insert("1.0", "⏳ Aguardando análise...")
        
        # Painel direito - Com Controlador
        frame_com = ctk.CTkFrame(
            self,
            fg_color="#f0f8f4",
            corner_radius=12,
            border_width=2,
            border_color=self.CORES_PYTHON["secundario"]
        )
        frame_com.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        frame_com.grid_columnconfigure(0, weight=1)
        frame_com.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho com emoji
        ctk.CTkLabel(
            frame_com,
            text="🔒 SISTEMA COM CONTROLADOR (Malha Fechada)",
            font=("Segoe UI", 13, "bold"),
            text_color=self.CORES_PYTHON["secundario"]
        ).grid(row=0, column=0, pady=(12, 8), sticky="w", padx=15)
        
        self.texto_metricas_com = ctk.CTkTextbox(
            frame_com,
            font=("Courier New", 10),
            fg_color="#ffffff",
            border_color=self.CORES_PYTHON["borda"],
            border_width=1,
            height=300,
            text_color=self.CORES_PYTHON["texto_principal"]
        )
        self.texto_metricas_com.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.texto_metricas_com.insert("1.0", "⏳ Aguardando análise...")
    
    def criar_paineis_exportacao(self):
        """Cria o painel de opções de exportação com design Python"""
        
        frame_exportacao = ctk.CTkFrame(
            self,
            fg_color="#e8eef7",
            corner_radius=12,
            border_width=2,
            border_color=self.CORES_PYTHON["primario"]
        )
        frame_exportacao.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        frame_exportacao.grid_columnconfigure(0, weight=1)
        
        # Título
        ctk.CTkLabel(
            frame_exportacao,
            text="📊 Exportar Métricas e Gráficos",
            font=("Segoe UI", 12, "bold"),
            text_color=self.CORES_PYTHON["primario"]
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        # Frame de botões
        frame_botoes = ctk.CTkFrame(frame_exportacao, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=15, pady=(0, 10))
        
        # Botão CSV
        botao_csv = ctk.CTkButton(
            frame_botoes,
            text="📄 CSV",
            command=self.exportar_csv,
            height=38,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.CORES_PYTHON["primario"],
            hover_color="#1a5a99"
        )
        botao_csv.pack(side="left", padx=(0, 8), fill="x", expand=True)
        
        # Botão PNG
        botao_png = ctk.CTkButton(
            frame_botoes,
            text="🖼️ PNG",
            command=self.exportar_png,
            height=38,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.CORES_PYTHON["secundario"],
            hover_color="#228B22"
        )
        botao_png.pack(side="left", padx=(0, 8), fill="x", expand=True)
        
        # Botão PDF
        botao_pdf = ctk.CTkButton(
            frame_botoes,
            text="📋 PDF",
            command=self.exportar_pdf,
            height=38,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.CORES_PYTHON["destaque"],
            hover_color="#e07000"
        )
        botao_pdf.pack(side="left", padx=(0, 8), fill="x", expand=True)
        
        # Botão Limpar
        botao_limpar = ctk.CTkButton(
            frame_botoes,
            text="🗑️ Limpar",
            command=self.limpar_dados,
            height=38,
            font=("Segoe UI", 11, "bold"),
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        botao_limpar.pack(side="left", fill="x", expand=True)
        
        # Label de status
        self.label_status = ctk.CTkLabel(
            frame_exportacao,
            text="✅ Pronto para exportar",
            font=("Segoe UI", 9),
            text_color=self.CORES_PYTHON["secundario"]
        )
        self.label_status.pack(anchor="w", padx=15, pady=(0, 12))
    
    def atualizar_metricas(self, metricas_sem, metricas_com, tipo_entrada="Degrau"):
        """Atualiza os painéis com novas métricas"""
        
        self.metricas_sem = metricas_sem
        self.metricas_com = metricas_com
        self.tipo_entrada = tipo_entrada
        
        # Limpar e atualizar painel sem controlador
        self.texto_metricas_sem.delete("1.0", "end")
        self.adicionar_metricas_ao_texto(self.texto_metricas_sem, metricas_sem)
        
        # Limpar e atualizar painel com controlador
        self.texto_metricas_com.delete("1.0", "end")
        self.adicionar_metricas_ao_texto(self.texto_metricas_com, metricas_com)
        
        self.label_status.configure(text="✅ Métricas atualizadas com sucesso", text_color=self.CORES_PYTHON["secundario"])
    
    def adicionar_metricas_ao_texto(self, textbox, metricas):
        """Melhorar formatação com emojis e organização clara das métricas"""
        
        conteudo = []
        
        # Cabeçalho com estilo
        conteudo.append("╔" + "=" * 45 + "╗")
        conteudo.append("║" + " MÉTRICAS DO SISTEMA ".center(45) + "║")
        conteudo.append("╚" + "=" * 45 + "╝")
        conteudo.append("")
        
        # ⏱️ RESPOSTA TEMPORAL
        conteudo.append("⏱️ RESPOSTA TEMPORAL")
        conteudo.append("─" * 48)
        
        tempo_subida = metricas.get('tempo_subida_10_90', 0)
        tempo_pico = metricas.get('tempo_pico', 0)
        tempo_acomodacao_2 = metricas.get('tempo_acomodacao_2pct', 0)
        tempo_acomodacao_5 = metricas.get('tempo_acomodacao_5pct', 0)
        
        conteudo.append(f"  Tempo de Subida (10-90%)    : {tempo_subida:>12.2f}s")
        conteudo.append(f"  Tempo de Pico               : {tempo_pico:>12.2f}s")
        conteudo.append(f"  Tempo Acomodação (±2%)      : {tempo_acomodacao_2:>12.2f}s")
        conteudo.append(f"  Tempo Acomodação (±5%)      : {tempo_acomodacao_5:>12.2f}s")
        conteudo.append("")
        
        # 📈 AMPLITUDE E PICO
        conteudo.append("📈 AMPLITUDE E RESPOSTA DE PICO")
        conteudo.append("─" * 48)
        
        y_pico = metricas.get('y_pico', 0)
        valor_final = metricas.get('valor_final', 0)
        sobressinal = metricas.get('sobressinal_pct', 0)
        
        conteudo.append(f"  Valor de Pico               : {y_pico:>12.2f}")
        conteudo.append(f"  Valor Final (Estado Est.)   : {valor_final:>12.2f}")
        conteudo.append(f"  Sobressinal Mp(%)           : {sobressinal:>12.2f}%")
        conteudo.append("")
        
        # ⚡ ERRO E CARACTERIZAÇÃO
        conteudo.append(" 🚫 ERRO E ESTABILIDADE")
        conteudo.append("─" * 48)
        
        erro_estacionario = metricas.get('erro_estacionario', 0)
        erro_pct = metricas.get('erro_pct', 0)
        
        conteudo.append(f"  Erro Estacionário           : {erro_estacionario:>12.2f}")
        conteudo.append(f"  Erro Estacionário (%)       : {erro_pct:>12.2f}%")
        conteudo.append("")
        
        # 🔧 PARÂMETROS DO SISTEMA
        conteudo.append("🔧 PARÂMETROS DO SISTEMA")
        conteudo.append("─" * 48)
        
        freq_natural = metricas.get('frequencia_natural', 0)
        coef_amortecimento = metricas.get('coeficiente_amortecimento', 0)
        
        conteudo.append(f"  Frequência Natural (ωn)     : {freq_natural:>12.2f}rad/s")
        conteudo.append(f"  Coef. Amortecimento (ζ)     : {coef_amortecimento:>12.2f}")
        conteudo.append("")
        
        # Rodapé
        conteudo.append("╔" + "=" * 45 + "╗")
        conteudo.append("║" + " Dados prontos para exportação ".center(45) + "║")
        conteudo.append("╚" + "=" * 45 + "╝")
        
        textbox.insert("end", "\n".join(conteudo))
    
    def adicionar_figuras(self, figuras_graficos):
        """Armazena as figuras para exportação"""
        self.figuras_graficos = figuras_graficos
    
    def exportar_csv(self):
        """Exporta métricas para CSV"""
        
        if not self.metricas_sem or not self.metricas_com:
            self.mostrar_aviso("Nenhuma métrica para exportar")
            return
        
        try:
            caminho = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"metricas_controle_{self.obter_timestamp()}.csv"
            )
            
            if not caminho:
                return
            
            sucesso, mensagem = ExportadorResultados.exportar_csv(
                self.metricas_sem,
                self.metricas_com,
                caminho
            )
            
            if sucesso:
                self.label_status.configure(text=f"✅ {mensagem}", text_color=self.CORES_PYTHON["secundario"])
            else:
                self.label_status.configure(text=f"❌ {mensagem}", text_color="#d32f2f")
                self.mostrar_erro(mensagem)
            
        except Exception as e:
            self.mostrar_erro(f"Erro ao exportar CSV: {str(e)}")
    
    def exportar_png(self):
        """Exporta gráficos para PNG"""
        
        if not self.figuras_graficos:
            self.mostrar_aviso("Nenhum gráfico para exportar")
            return
        
        try:
            caminho = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=f"graficos_controle_{self.obter_timestamp()}.png"
            )
            
            if not caminho:
                return
            
            if self.figuras_graficos:
                _, figura = self.figuras_graficos[0]
                sucesso, mensagem = ExportadorResultados.exportar_png(figura, caminho)
                
                if sucesso:
                    self.label_status.configure(text=f"✅ {mensagem}", text_color=self.CORES_PYTHON["secundario"])
                else:
                    self.label_status.configure(text=f"❌ {mensagem}", text_color="#d32f2f")
                    self.mostrar_erro(mensagem)
        
        except Exception as e:
            self.mostrar_erro(f"Erro ao exportar PNG: {str(e)}")
    
    def exportar_pdf(self):
        """Exporta relatório completo em PDF"""
        
        if not self.metricas_sem or not self.metricas_com:
            self.mostrar_aviso("Nenhuma métrica para exportar")
            return
        
        try:
            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"relatorio_controle_{self.obter_timestamp()}.pdf"
            )
            
            if not caminho:
                return
            
            sucesso, mensagem = ExportadorResultados.exportar_pdf(
                self.metricas_sem,
                self.metricas_com,
                self.figuras_graficos,
                caminho
            )
            
            if sucesso:
                self.label_status.configure(text=f"✅ {mensagem}", text_color=self.CORES_PYTHON["secundario"])
            else:
                self.label_status.configure(text=f"❌ {mensagem}", text_color="#d32f2f")
                self.mostrar_erro(mensagem)
        
        except Exception as e:
            self.mostrar_erro(f"Erro ao exportar PDF: {str(e)}")
    
    def limpar_dados(self):
        """Limpa os dados das métricas"""
        self.metricas_sem = {}
        self.metricas_com = {}
        self.figuras_graficos = []
        self.texto_metricas_sem.delete("1.0", "end")
        self.texto_metricas_sem.insert("1.0", "⏳ Aguardando análise...")
        self.texto_metricas_com.delete("1.0", "end")
        self.texto_metricas_com.insert("1.0", "⏳ Aguardando análise...")
        self.label_status.configure(text="✅ Pronto para exportar", text_color=self.CORES_PYTHON["secundario"])
    
    @staticmethod
    def obter_timestamp():
        """Gera timestamp para nomes de arquivo"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def mostrar_aviso(self, mensagem):
        """Mostra aviso visual no painel"""
        self.label_status.configure(text=f"⚠️ {mensagem}", text_color="#ff9800")
    
    def mostrar_erro(self, mensagem):
        """Mostra erro visual no painel"""
        try:
            from CTkMessagebox import CTkMessagebox
            CTkMessagebox(title="Erro", message=mensagem, icon="cancel")
        except ImportError:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erro", mensagem)
