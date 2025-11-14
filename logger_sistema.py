"""
Sistema de logging centralizado para o Sistema de Controle
Fornece logs estruturados para debug e análise de problemas
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

class LoggerSistema:
    """Gerenciador centralizado de logs com suporte a arquivo e console"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSistema, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _get_logs_directory(self):
        """
        Obtém o diretório apropriado para logs baseado no ambiente
        """
        if getattr(sys, 'frozen', False):
            # Running as executable
            if sys.platform == "win32":
                # Windows: Use AppData/Local
                appdata = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
                if appdata:
                    base_dir = Path(appdata) / "SistemaControle"
                else:
                    base_dir = Path.home() / "SistemaControle"
            else:
                # Linux/Mac: Use home directory
                base_dir = Path.home() / ".sistemacontrole"
        else:
            # Running as script
            base_dir = Path(".")
        
        logs_dir = base_dir / "logs"
        return logs_dir
    
    def _setup_logger(self):
        """Configura o logger com arquivo e console"""
        try:
            # Criar diretório de logs se não existir
            logs_dir = self._get_logs_directory()
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo com data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = logs_dir / f"sistema_{timestamp}.log"
            
            # Configurar logger
            self._logger = logging.getLogger("SistemaControle")
            self._logger.setLevel(logging.DEBUG)
            
            # Remover handlers anteriores se existirem
            for handler in self._logger.handlers[:]:
                self._logger.removeHandler(handler)
            
            # Formato detalhado
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Handler para arquivo
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
            
            # Handler para console (apenas WARNING e acima)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)
            
            self._logger.info(f"Logger iniciado com sucesso. Logs em: {logs_dir}")
        
        except Exception as e:
            # Fallback: se falhar, usar apenas console
            self._logger = logging.getLogger("SistemaControle")
            self._logger.setLevel(logging.WARNING)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
            self._logger.warning(f"Não foi possível criar arquivo de log: {e}")
    
    def get_logger(self):
        """Retorna o logger configurado"""
        return self._logger
    
    def info(self, mensagem):
        """Log de informação"""
        self._logger.info(mensagem)
    
    def debug(self, mensagem):
        """Log de debug"""
        self._logger.debug(mensagem)
    
    def warning(self, mensagem):
        """Log de aviso"""
        self._logger.warning(mensagem)
    
    def error(self, mensagem):
        """Log de erro"""
        self._logger.error(mensagem)
    
    def critical(self, mensagem):
        """Log crítico"""
        self._logger.critical(mensagem)
    
    def exception(self, mensagem):
        """Log de exceção com stack trace"""
        self._logger.exception(mensagem)

# Instância global
logger = LoggerSistema()
