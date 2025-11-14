"""
Módulo centralizado para gerenciamento de temas
Evita importações circulares entre tela.py e outros módulos
"""

import os
import sys
import json


def obter_caminho_recurso(nome_arquivo):
    """
    Obtém o caminho correto para recursos tanto em desenvolvimento quanto no executável.
    PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
    """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Se não estiver rodando como executável, usa o diretório atual
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, nome_arquivo)


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
        self.config_file = self._obter_caminho_config()
        self.carregar_configuracao()
    
    def _obter_caminho_config(self):
        """
        Obtém o caminho para o arquivo de configuração no diretório do usuário.
        Isso garante que as configurações persistam entre execuções.
        """
        try:
            # Tenta usar o diretório do usuário
            if os.name == 'nt':  # Windows
                base_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'SistemaControle')
            else:  # Linux/Mac
                base_dir = os.path.join(os.path.expanduser('~'), '.sistemacontrole')
            
            # Cria o diretório se não existir
            os.makedirs(base_dir, exist_ok=True)
            return os.path.join(base_dir, 'config_tema.json')
        except Exception:
            # Fallback para o diretório temporário
            import tempfile
            return os.path.join(tempfile.gettempdir(), 'sistemacontrole_config_tema.json')
    
    def carregar_configuracao(self):
        """Carrega configuração salva"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    tema_carregado = config.get('tema', 'dark')
                    # Valida se o tema existe
                    if tema_carregado in self.TEMAS:
                        self.tema_atual = tema_carregado
                    else:
                        self.tema_atual = "dark"
            else:
                self.tema_atual = "dark"
        except Exception as e:
            print(f"[AVISO] Erro ao carregar configuração de tema: {e}")
            self.tema_atual = "dark"
    
    def salvar_configuracao(self):
        """Salva configuração atual"""
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'tema': self.tema_atual}, f, indent=2)
        except Exception as e:
            print(f"[AVISO] Erro ao salvar configuração de tema: {e}")
    
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
        return self.TEMAS[self.tema_atual].copy()
    
    def obter_nome_tema(self):
        """Retorna nome amigável do tema"""
        nomes = {
            "dark": "Escuro",
            "light": "Claro",
            "high_contrast": "Alto Contraste"
        }
        return nomes.get(self.tema_atual, "Escuro")


# Instância global do gerenciador de temas
gerenciador_temas = GerenciadorTemas()

# Função helper para obter cores facilmente
def obter_cores():
    """Retorna as cores do tema atual"""
    return gerenciador_temas.obter_cores()
