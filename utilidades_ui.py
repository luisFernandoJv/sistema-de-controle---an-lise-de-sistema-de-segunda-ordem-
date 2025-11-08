"""
🧩 Utilidades para interface gráfica moderna, responsiva e multiplataforma.

Fornece classes utilitárias para:
• Gerenciar responsividade (DPI, fonte e padding adaptativos)
• Configurar gráficos matplotlib com estilo moderno
• Validar entradas de forma visual e acessível
• Aplicar estilos visuais consistentes em botões e campos
"""

import platform
import tkinter as tk
from typing import Callable


# ==========================================================
# 🖥️ GERENCIADOR DE RESPONSIVIDADE
# ==========================================================
class GerenciadorResponsividade:
    """Gerencia layout responsivo e escalamento automático de UI."""

    def __init__(self, janela_raiz: tk.Tk):
        self.janela = janela_raiz
        self.callbacks_redimensionamento = []
        self.escala_dpi = self._detectar_dpi()
        self.escala_fonte_base = 11 * self.escala_dpi
        self.janela.bind("<Configure>", self._on_configure)

    def _detectar_dpi(self) -> float:
        """Detecta e retorna o fator de escala DPI do sistema."""
        sistema = platform.system()
        try:
            if sistema == "Windows":
                from ctypes import windll
                dc = windll.user32.GetDC(0)
                dpi = windll.gdi32.GetDeviceCaps(dc, 88)
                windll.user32.ReleaseDC(0, dc)
                return max(1.0, dpi / 96.0)

            elif sistema == "Darwin":  # macOS
                import subprocess
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True, text=True
                )
                return 2.0 if "Retina" in result.stdout else 1.0

            else:  # Linux
                root = tk.Tk()
                dpi = root.winfo_fpixels("1i")
                root.destroy()
                return max(1.0, dpi / 96.0)
        except Exception:
            return 1.0

    def _on_configure(self, event):
        """Executa callbacks registrados quando a janela é redimensionada."""
        for callback in self.callbacks_redimensionamento:
            try:
                callback(event)
            except Exception as e:
                try:
                    from logger_sistema import logger
                    logger.error(f"Erro em callback de redimensionamento: {e}")
                except ImportError:
                    print(f"[AVISO] Erro em callback: {e}")

    def registrar_callback_redimensionamento(self, callback: Callable):
        """Registra uma função a ser chamada ao redimensionar a janela."""
        if callable(callback):
            self.callbacks_redimensionamento.append(callback)

    def calcular_tamanho_fonte(self, tamanho_base: int) -> int:
        """Ajusta o tamanho da fonte de acordo com o DPI."""
        return max(8, int(tamanho_base * self.escala_dpi))

    def calcular_padding(self, padding_base: int) -> int:
        """Ajusta espaçamentos (padding) conforme DPI."""
        return max(2, int(padding_base * self.escala_dpi))

    def centralizar_janela(self, largura: int, altura: int):
        """Centraliza a janela na tela."""
        self.janela.update_idletasks()
        sw, sh = self.janela.winfo_screenwidth(), self.janela.winfo_screenheight()
        x, y = (sw - largura) // 2, (sh - altura) // 2
        self.janela.geometry(f"{largura}x{altura}+{x}+{y}")

    def maximizar_janela(self):
        """Maximiza a janela (compatível com Windows e Linux)."""
        if platform.system() == "Windows":
            self.janela.state("zoomed")
        else:
            self.janela.attributes("-zoomed", True)


# ==========================================================
# 📈 UTILITÁRIOS PARA GRÁFICOS
# ==========================================================
class UtiliadadesGraficos:
    """Funções auxiliares para renderização de gráficos matplotlib."""

    @staticmethod
    def obter_dpi_figura(escala_dpi: float = 1.0) -> int:
        """Retorna um DPI ideal para gráficos matplotlib."""
        return int(100 * escala_dpi)

    @staticmethod
    def obter_tamanho_figura(escala_dpi: float = 1.0) -> tuple:
        """Retorna o tamanho da figura ajustado ao DPI."""
        return (5.5 * escala_dpi, 3.8 * escala_dpi)


# ==========================================================
# ✅ VALIDAÇÃO DE ENTRADAS
# ==========================================================
class ValidadorEntrada:
    """Gerencia validações visuais e feedback de entradas."""

    @staticmethod
    def validar_entrada(entry_widget, condicao_valida, cores, mensagem_erro="Valor inválido!"):
        """Aplica feedback visual ao campo conforme validação."""
        if not condicao_valida:
            entry_widget.configure(border_color=cores["erro"], border_width=2)
            if not entry_widget.get():
                entry_widget.configure(placeholder_text=mensagem_erro)
        else:
            entry_widget.configure(border_color=cores["borda"], border_width=1)

    @staticmethod
    def criar_validacao_numerica(entry_widget, cores):
        """Ativa validação automática de entrada numérica (float ou lista)."""
        def validar(event=None):
            texto = entry_widget.get().strip()
            if not texto:
                ValidadorEntrada.validar_entrada(entry_widget, True, cores)
                return
            try:
                [float(x) for x in texto.split()]
                ValidadorEntrada.validar_entrada(entry_widget, True, cores)
            except ValueError:
                ValidadorEntrada.validar_entrada(
                    entry_widget, False, cores, "Use números separados por espaço"
                )

        entry_widget.bind("<FocusOut>", validar)
        entry_widget.bind("<KeyRelease>", validar)


# ==========================================================
# 🎨 ESTILOS MODERNOS DE UI
# ==========================================================
class EstilosModernos:
    """Define padrões de fontes e estilos visuais modernos."""

    FONTES = {
        "titulo": ("Inter", 22, "bold"),
        "subtitulo": ("Inter", 16, "bold"),
        "texto": ("Inter", 12),
        "botao": ("Inter", 14, "bold"),
        "entrada": ("Inter", 11),
        "pequeno": ("Inter", 10),
    }

    FALLBACK = {
        "titulo": ("Segoe UI", 22, "bold"),
        "subtitulo": ("Segoe UI", 16, "bold"),
        "texto": ("Segoe UI", 12),
        "botao": ("Segoe UI", 14, "bold"),
        "entrada": ("Segoe UI", 11),
        "pequeno": ("Segoe UI", 10),
    }

    @classmethod
    def obter_fonte(cls, tipo: str):
        """Retorna uma fonte moderna com fallback automático."""
        try:
            import tkinter.font as tkfont
            fonte = cls.FONTES.get(tipo, cls.FONTES["texto"])
            test = tkfont.Font(family=fonte[0], size=fonte[1])
            if "Inter" in test.actual().get("family", ""):
                return fonte
        except Exception:
            pass
        return cls.FALLBACK.get(tipo, cls.FALLBACK["texto"])

    @staticmethod
    def estilo_botao(cores, tipo="primario"):
        """Gera estilo padronizado para botões."""
        cores_map = {
            "primario": ("primaria", "primaria_hover"),
            "secundario": ("secundaria", "secundaria_hover"),
            "terciario": ("terciaria", "terciaria_hover"),
        }
        cor, hover = cores_map.get(tipo, ("primaria", "primaria_hover"))
        return {
            "corner_radius": 12,
            "height": 45,
            "font": EstilosModernos.obter_fonte("botao"),
            "fg_color": cores[cor],
            "hover_color": cores[hover],
            "text_color": "white",
            "border_width": 0,
        }

    @staticmethod
    def estilo_entrada(cores):
        """Retorna estilo consistente para entradas (CTkEntry)."""
        return {
            "height": 40,
            "font": EstilosModernos.obter_fonte("entrada"),
            "fg_color": cores["fundo_claro"],
            "border_color": cores["borda"],
            "border_width": 1,
            "corner_radius": 8,
        }


# ==========================================================
# 📊 CONFIGURAÇÃO DE GRÁFICOS MODERNOS
# ==========================================================
class ConfiguracaoGraficosModerna:
    """Aplica estilo visual moderno aos gráficos matplotlib."""

    @staticmethod
    def aplicar_estilo_moderno(cores):
        """Define tema visual coerente com o modo claro/escuro atual."""
        import matplotlib.pyplot as plt
        try:
            plt.style.use("seaborn-v0_8-darkgrid")
        except Exception:
            pass

        plt.rcParams.update({
            "axes.facecolor": cores["fundo_claro"],
            "figure.facecolor": cores["acento"],
            "savefig.facecolor": cores["acento"],
            "axes.edgecolor": cores["borda"],
            "axes.labelcolor": cores["texto_principal"],
            "xtick.color": cores["texto_principal"],
            "ytick.color": cores["texto_principal"],
            "text.color": cores["texto_principal"],
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Segoe UI", "DejaVu Sans"],
            "lines.linewidth": 2.2,
            "grid.alpha": 0.3,
            "legend.framealpha": 0.9,
            "legend.facecolor": cores["fundo_claro"],
            "legend.edgecolor": cores["borda"],
        })
