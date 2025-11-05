#!/usr/bin/env python3
"""
Script de inicialização multiplataforma para o Sistema de Controle
Versão melhorada com logging, tratamento de erros e DPI awareness
"""

import sys
import platform
import subprocess
import os
from pathlib import Path

from logger_sistema import logger
from gerenciador_excecoes import gerenciador_excecoes

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    if sys.version_info < (3, 8):
        msg = "Python 3.8 ou superior é necessário"
        print(f"❌ Erro: {msg}")
        print(f"   Versão atual: {sys.version}")
        logger.error(msg)
        sys.exit(1)
    versao = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✅ Python {versao}")
    logger.info(f"Python {versao} detectado")

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required = [
        'customtkinter',
        'PIL',
        'numpy',
        'scipy',
        'matplotlib',
        'control'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
            logger.info(f"Dependência encontrada: {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} não encontrado")
            logger.warning(f"Dependência ausente: {package}")
    
    if missing:
        print("\n⚠️  Dependências faltando. Instalando...")
        logger.warning(f"Instalando dependências ausentes: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependências instaladas com sucesso!")
            logger.info("Dependências instaladas com sucesso")
        except subprocess.CalledProcessError:
            msg = "Erro ao instalar dependências"
            print(f"❌ {msg}")
            print("   Execute manualmente: pip install -r requirements.txt")
            logger.error(msg)
            sys.exit(1)

def configure_dpi():
    """Configura DPI awareness cross-plataforma"""
    sistema = platform.system()
    print(f"\n🖥️  Sistema Operacional: {sistema} {platform.release()}")
    logger.info(f"SO detectado: {sistema} {platform.release()}")
    
    if sistema == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDPIAwareness(1)
            print("✅ DPI awareness configurado (Windows)")
            logger.info("DPI awareness configurado para Windows")
        except Exception as e:
            print("⚠️  Não foi possível configurar DPI awareness (Windows)")
            logger.warning(f"DPI awareness não configurado: {e}")
    
    elif sistema == "Darwin":  # macOS
        print("✅ DPI awareness nativo (macOS)")
        logger.info("Usando DPI awareness nativo do macOS")
    
    else:  # Linux
        print("✅ DPI awareness nativo (Linux)")
        logger.info("Usando DPI awareness nativo do Linux")

def main():
    """Função principal com tratamento de erros global"""
    print("=" * 70)
    print("     SISTEMA DE ANÁLISE E CARACTERIZAÇÃO DE SISTEMAS DE CONTROLE")
    print("=" * 70)
    
    logger.info("=" * 70)
    logger.info("INICIALIZAÇÃO DO SISTEMA")
    logger.info("=" * 70)
    
    print(f"\n🐍 Verificando ambiente Python...\n")
    
    try:
        check_python_version()
        check_dependencies()
        configure_dpi()
        
        print("\n" + "=" * 70)
        print("🚀 Iniciando aplicação...")
        print("=" * 70 + "\n")
        logger.info("Iniciando interface gráfica...")
        
        try:
            from tela import SistemaTCC
            app = SistemaTCC()
            logger.info("Aplicação iniciada com sucesso")
            app.mainloop()
            logger.info("Aplicação encerrada normalmente")
        except ImportError as e:
            msg = f"Erro ao importar módulo: {e}"
            print(f"❌ {msg}")
            logger.critical(msg)
            sys.exit(1)
        except Exception as e:
            msg = f"Erro ao iniciar aplicação: {e}"
            print(f"❌ {msg}")
            logger.critical(f"Erro crítico na aplicação: {e}", exc_info=True)
            raise
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Aplicação encerrada pelo usuário")
        logger.info("Aplicação encerrada pelo usuário (Ctrl+C)")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        logger.critical(f"Erro fatal não tratado: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
