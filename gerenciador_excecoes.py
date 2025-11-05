"""
Gerenciador centralizado de exceções
Trata erros de forma consistente com logging e UI feedback
"""

import sys
import traceback
import tkinter.messagebox as messagebox
from logger_sistema import logger
from enum import Enum

class TipoErro(Enum):
    """Tipos de erro suportados"""
    VALIDACAO = "Erro de Validação"
    CALCULO = "Erro de Cálculo"
    ARQUIVO = "Erro de Arquivo"
    SISTEMA = "Erro do Sistema"
    DESCONHECIDO = "Erro Desconhecido"

class GerenciadorExcecoes:
    """Gerencia exceções globalmente com logging e UI feedback"""
    
    def __init__(self):
        self.callbacks_erro = []
        self.setup_exception_hook()
    
    def setup_exception_hook(self):
        """Configura o hook global de exceções"""
        sys.excepthook = self._handle_exception
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Trata exceções não capturadas"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log da exceção completa
        erro_traceback = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        logger.error(f"Exceção não tratada:\n{erro_traceback}")
        
        # Mensagem para usuário
        messagebox.showerror(
            "Erro Crítico",
            f"Ocorreu um erro inesperado:\n{exc_value}\n\n"
            f"Verifique o arquivo de log em 'logs/' para mais detalhes."
        )
    
    def registrar_callback_erro(self, callback):
        """Registra callback para ser chamado quando erro ocorrer"""
        self.callbacks_erro.append(callback)
    
    def disparar_callbacks_erro(self, erro_info):
        """Dispara todos os callbacks de erro"""
        for callback in self.callbacks_erro:
            try:
                callback(erro_info)
            except Exception as e:
                logger.error(f"Erro ao chamar callback: {e}")
    
    @staticmethod
    def tratar_erro(tipo=TipoErro.DESCONHECIDO, mensagem="", mostrar_dialog=True):
        """
        Trata um erro de forma centralizada
        
        Args:
            tipo: TipoErro enum indicando tipo de erro
            mensagem: Mensagem de erro específica
            mostrar_dialog: Se deve mostrar diálogo ao usuário
        """
        log_msg = f"{tipo.value}: {mensagem}"
        logger.error(log_msg)
        
        if mostrar_dialog:
            messagebox.showerror(
                tipo.value,
                mensagem or "Verifique o arquivo de log para detalhes."
            )

# Instância global
gerenciador_excecoes = GerenciadorExcecoes()
