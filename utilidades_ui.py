"""
Utilidades para UI responsiva e cross-plataforma
Gerencia redimensionamento, DPI e escalamento de fontes
"""

import platform
import tkinter as tk
from typing import Callable, Optional

class GerenciadorResponsividade:
    """Gerencia layout responsivo e escalamento automático"""
    
    def __init__(self, janela_raiz):
        self.janela = janela_raiz
        self.proporcoes_originais = {}
        self.callbacks_redimensionamento = []
        
        # Detectar DPI e escala
        self.escala_dpi = self._detectar_dpi()
        self.escala_fonte_base = 11 * self.escala_dpi
        
        # Ligar evento de redimensionamento
        self.janela.bind("<Configure>", self._on_configure)
    
    def _detectar_dpi(self) -> float:
        """Detecta e retorna fator de escala DPI"""
        sistema = platform.system()
        
        if sistema == "Windows":
            try:
                from ctypes import windll
                # Conseguir DPI da tela primária
                dc = windll.user32.GetDC(0)
                dpi = windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
                windll.user32.ReleaseDC(0, dc)
                return max(1.0, dpi / 96.0)
            except:
                return 1.0
        
        elif sistema == "Darwin":  # macOS
            try:
                # macOS geralmente retorna 1.0 ou 2.0 (Retina)
                import subprocess
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True, text=True
                )
                if "Retina" in result.stdout:
                    return 2.0
            except:
                pass
            return 1.0
        
        else:  # Linux
            try:
                import tkinter as tk_root
                root = tk_root.Tk()
                dpi = root.winfo_fpixels("1i")
                root.destroy()
                return max(1.0, dpi / 96.0)
            except:
                return 1.0
    
    def _on_configure(self, event):
        """Chamado quando janela é redimensionada"""
        for callback in self.callbacks_redimensionamento:
            try:
                callback(event)
            except Exception as e:
                from logger_sistema import logger
                logger.error(f"Erro em callback de redimensionamento: {e}")
    
    def registrar_callback_redimensionamento(self, callback: Callable):
        """Registra callback para redimensionamento"""
        self.callbacks_redimensionamento.append(callback)
    
    def calcular_tamanho_fonte(self, tamanho_base: int) -> int:
        """Calcula tamanho de fonte com escala DPI"""
        return max(8, int(tamanho_base * self.escala_dpi))
    
    def calcular_padding(self, padding_base: int) -> int:
        """Calcula padding com escala DPI"""
        return max(2, int(padding_base * self.escala_dpi))
    
    def centralizar_janela(self, largura: int, altura: int):
        """Centraliza a janela na tela"""
        # Atualizar geometria para calcular posições
        self.janela.update_idletasks()
        
        # Obter dimensões da tela
        tela_largura = self.janela.winfo_screenwidth()
        tela_altura = self.janela.winfo_screenheight()
        
        # Calcular posição central
        x = (tela_largura - largura) // 2
        y = (tela_altura - altura) // 2
        
        # Aplicar geometria
        self.janela.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def maximizar_janela(self):
        """Maximiza a janela"""
        self.janela.state('zoomed' if platform.system() == "Windows" else 'normal')

class UtiliadadesGraficos:
    """Utilidades para renderização de gráficos com DPI awareness"""
    
    @staticmethod
    def obter_dpi_figura(escala_dpi: float = 1.0) -> int:
        """Retorna DPI adequado para figura matplotlib"""
        return int(100 * escala_dpi)
    
    @staticmethod
    def obter_tamanho_figura(escala_dpi: float = 1.0) -> tuple:
        """Retorna tamanho (width, height) com escala DPI"""
        largura = 5.5 * escala_dpi
        altura = 3.8 * escala_dpi
        return (largura, altura)
