import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pathlib import Path
import io
from typing import Dict, List, Tuple, Optional, Any
import csv
import control

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class MetricasControlador:
    """
    Calcula e gerencia métricas de resposta do controlador
    
    Attributes:
        metricas_sem (Dict): Métricas do sistema sem controlador
        metricas_com (Dict): Métricas do sistema com controlador
        historico (List): Histórico de análises realizadas
    """
    
    # Constantes para validação
    EPSILON = 1e-6
    LIMIAR_SUBIDA_10 = 0.1
    LIMIAR_SUBIDA_90 = 0.9
    LIMIAR_ACOMODACAO_2PCT = 0.02
    LIMIAR_ACOMODACAO_5PCT = 0.05
    
    def __init__(self):
        self.metricas_sem: Dict[str, float] = {}
        self.metricas_com: Dict[str, float] = {}
        self.historico: List[Dict] = []
    
    @staticmethod
    def calcular_metricas(
        t: np.ndarray,
        y: np.ndarray,
        y_referencia: float = 1.0,
        sys: Optional[control.TransferFunction] = None
    ) -> Dict[str, float]:
        """
        Calcula métricas completas da resposta temporal
        
        Args:
            t: Array de tempo
            y: Array de amplitude da resposta
            y_referencia: Valor de referência (padrão 1.0 para degrau)
            sys: Sistema de controle para extrair Wn e Zeta
        
        Returns:
            Dicionário com todas as métricas calculadas
        """
        metricas = {}
        
        # Validação de entrada
        if not MetricasControlador._validar_entrada(t, y):
            return metricas
        
        try:
            # Métricas básicas
            metricas.update(MetricasControlador._calcular_metricas_basicas(t, y))
            
            # Métricas de tempo
            metricas.update(MetricasControlador._calcular_metricas_tempo(t, y, metricas))
            
            # Erro estacionário
            metricas.update(
                MetricasControlador._calcular_erro_estacionario(
                    y_referencia, 
                    metricas['valor_final']
                )
            )
            
            # Parâmetros do sistema (Wn e Zeta)
            if sys is not None:
                metricas.update(MetricasControlador._extrair_parametros_sistema(sys))
            else:
                metricas.update({
                    'frequencia_natural': 0.0,
                    'coeficiente_amortecimento': 0.0
                })
            
        except Exception as e:
            print(f"[MetricasControlador] Erro ao calcular métricas: {e}")
        
        return metricas
    
    @staticmethod
    def _validar_entrada(t: np.ndarray, y: np.ndarray) -> bool:
        """Valida arrays de entrada"""
        if len(t) == 0 or len(y) == 0:
            return False
        if len(t) != len(y):
            print("[MetricasControlador] Aviso: t e y têm tamanhos diferentes")
            return False
        return True
    
    @staticmethod
    def _calcular_metricas_basicas(t: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Calcula métricas básicas (valor final, pico)"""
        y_pico = np.max(y)
        valor_final = float(y[-1])
        
        # Sobressinal calculado de forma segura
        if abs(valor_final) > MetricasControlador.EPSILON:
            sobressinal_pct = (y_pico - valor_final) / abs(valor_final) * 100
        else:
            sobressinal_pct = 0.0
        
        return {
            'valor_final': float(valor_final),
            'y_pico': float(y_pico),
            'tempo_pico': float(t[np.argmax(y)]),
            'sobressinal_pct': float(sobressinal_pct)
        }
    
    @staticmethod
    def _calcular_metricas_tempo(
        t: np.ndarray, 
        y: np.ndarray, 
        metricas_basicas: Dict[str, float]
    ) -> Dict[str, float]:
        """Calcula métricas de tempo (subida e acomodação)"""
        y_final = metricas_basicas['valor_final']
        metricas_tempo = {}
        
        # Tempo de subida (10% a 90%)
        if abs(y_final) > MetricasControlador.EPSILON:
            metricas_tempo['tempo_subida_10_90'] = (
                MetricasControlador._calcular_tempo_subida(t, y, y_final)
            )
            
            # Tempo de acomodação (±2% e ±5%)
            metricas_tempo['tempo_acomodacao_2pct'] = (
                MetricasControlador._calcular_tempo_acomodacao(
                    t, y, y_final, MetricasControlador.LIMIAR_ACOMODACAO_2PCT
                )
            )
            
            metricas_tempo['tempo_acomodacao_5pct'] = (
                MetricasControlador._calcular_tempo_acomodacao(
                    t, y, y_final, MetricasControlador.LIMIAR_ACOMODACAO_5PCT
                )
            )
        else:
            metricas_tempo.update({
                'tempo_subida_10_90': 0.0,
                'tempo_acomodacao_2pct': 0.0,
                'tempo_acomodacao_5pct': 0.0
            })
        
        return metricas_tempo
    
    @staticmethod
    def _calcular_tempo_subida(t: np.ndarray, y: np.ndarray, y_final: float) -> float:
        """Calcula tempo de subida (10% a 90%)"""
        lim_10 = MetricasControlador.LIMIAR_SUBIDA_10 * y_final
        lim_90 = MetricasControlador.LIMIAR_SUBIDA_90 * y_final
        
        idx_10 = np.where(y >= lim_10)[0]
        idx_90 = np.where(y >= lim_90)[0]
        
        if len(idx_10) > 0 and len(idx_90) > 0:
            return float(t[idx_90[0]] - t[idx_10[0]])
        return 0.0
    
    @staticmethod
    def _calcular_tempo_acomodacao(
        t: np.ndarray, 
        y: np.ndarray, 
        y_final: float, 
        percentual: float
    ) -> float:
        """Calcula tempo de acomodação para um dado percentual"""
        lim_sup = y_final * (1 + percentual)
        lim_inf = y_final * (1 - percentual)
        
        indices_fora = np.where((y > lim_sup) | (y < lim_inf))[0]
        
        if len(indices_fora) > 0:
            return float(t[indices_fora[-1]])
        return 0.0
    
    @staticmethod
    def _calcular_erro_estacionario(y_referencia: float, valor_final: float) -> Dict[str, float]:
        """Calcula erro estacionário absoluto e percentual"""
        erro_abs = abs(y_referencia - valor_final)
        
        if abs(y_referencia) > MetricasControlador.EPSILON:
            erro_pct = (erro_abs / abs(y_referencia)) * 100
        else:
            erro_pct = 0.0
        
        return {
            'erro_estacionario': float(erro_abs),
            'erro_pct': float(erro_pct)
        }
    
    @staticmethod
    def _extrair_parametros_sistema(sys: control.TransferFunction) -> Dict[str, float]:
        """Extrai frequência natural e coeficiente de amortecimento"""
        try:
            wn_array, zeta_array, _ = control.damp(sys, doprint=False)
            
            if len(wn_array) == 0 or len(zeta_array) == 0:
                return {
                    'frequencia_natural': 0.0,
                    'coeficiente_amortecimento': 0.0
                }
            
            # Filtrar polos válidos (frequência natural > limiar)
            valid_indices = wn_array > MetricasControlador.EPSILON
            
            if not np.any(valid_indices):
                return {
                    'frequencia_natural': 0.0,
                    'coeficiente_amortecimento': 0.0
                }
            
            # Selecionar polos dominantes (menor frequência natural)
            valid_wn = wn_array[valid_indices]
            valid_zeta = zeta_array[valid_indices]
            idx_dominante = np.argmin(valid_wn)
            
            return {
                'frequencia_natural': float(valid_wn[idx_dominante]),
                'coeficiente_amortecimento': float(valid_zeta[idx_dominante])
            }
            
        except Exception as e:
            print(f"[MetricasControlador] Erro ao extrair Wn e Zeta: {e}")
            return {
                'frequencia_natural': 0.0,
                'coeficiente_amortecimento': 0.0
            }
    
    @staticmethod
    def comparar_sistemas(
        metricas_sem: Dict[str, float],
        metricas_com: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Compara métricas do sistema com e sem controlador
        
        Returns:
            Dicionário com diferenças e melhorias percentuais
        """
        comparacao = {}
        
        chaves_comparacao = [
            'tempo_acomodacao_2pct',
            'tempo_acomodacao_5pct',
            'sobressinal_pct',
            'tempo_subida_10_90',
            'erro_pct',
            'erro_estacionario',
            'valor_final',
            'frequencia_natural',
            'coeficiente_amortecimento'
        ]
        
        for chave in chaves_comparacao:
            if chave in metricas_sem and chave in metricas_com:
                valor_sem = metricas_sem[chave]
                valor_com = metricas_com[chave]
                
                # Diferença absoluta
                comparacao[f'{chave}_diferenca'] = valor_com - valor_sem
                
                # Melhoria percentual (com tratamento de divisão por zero)
                if abs(valor_sem) > MetricasControlador.EPSILON:
                    melhoria_pct = ((valor_sem - valor_com) / abs(valor_sem)) * 100
                else:
                    melhoria_pct = 0.0
                
                comparacao[f'{chave}_melhoria_pct'] = melhoria_pct
        
        return comparacao
    
    def gerar_relatorio_texto(
        self,
        metricas_sem: Dict[str, float],
        metricas_com: Dict[str, float],
        tipo_entrada: str = "Degrau"
    ) -> str:
        """
        Gera relatório em texto formatado com todas as métricas
        
        Args:
            metricas_sem: Métricas sem controlador
            metricas_com: Métricas com controlador
            tipo_entrada: Tipo de sinal de entrada
        
        Returns:
            String com relatório formatado
        """
        linhas = []
        separador_principal = "=" * 80
        separador_secao = "-" * 80
        
        # Cabeçalho
        linhas.extend([
            separador_principal,
            "RELATÓRIO DE MÉTRICAS DO SISTEMA DE CONTROLE".center(80),
            separador_principal,
            "",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            f"Tipo de Entrada: {tipo_entrada}",
            ""
        ])
        
        # Seção: Sistema sem controlador
        linhas.extend([
            separador_secao,
            "MÉTRICAS DO SISTEMA SEM CONTROLADOR (MALHA ABERTA)".ljust(80),
            separador_secao
        ])
        linhas.extend(self._formatar_metricas_para_relatorio(metricas_sem))
        
        # Seção: Sistema com controlador
        linhas.extend([
            "",
            separador_secao,
            "MÉTRICAS DO SISTEMA COM CONTROLADOR (MALHA FECHADA)".ljust(80),
            separador_secao
        ])
        linhas.extend(self._formatar_metricas_para_relatorio(metricas_com))
        
        # Seção: Comparação
        linhas.extend([
            "",
            separador_secao,
            "COMPARAÇÃO E MELHORIAS".ljust(80),
            separador_secao
        ])
        
        comparacao = self.comparar_sistemas(metricas_sem, metricas_com)
        linhas.extend(self._formatar_comparacao_para_relatorio(comparacao))
        
        linhas.extend(["", separador_principal])
        
        return "\n".join(linhas)
    
    @staticmethod
    def _formatar_metricas_para_relatorio(metricas: Dict[str, float]) -> List[str]:
        """Formata métricas para exibição em relatório"""
        linhas = []
        
        for chave, valor in sorted(metricas.items()):
            nome_formatado = chave.replace('_', ' ').title()
            
            if isinstance(valor, (int, float)):
                linhas.append(f"  {nome_formatado:<45}: {valor:>12.6f}")
            else:
                linhas.append(f"  {nome_formatado:<45}: {str(valor):>12}")
        
        return linhas
    
    @staticmethod
    def _formatar_comparacao_para_relatorio(comparacao: Dict[str, float]) -> List[str]:
        """Formata comparação para exibição em relatório"""
        linhas = []
        
        # Filtrar apenas melhorias percentuais
        melhorias = {k: v for k, v in comparacao.items() if 'melhoria_pct' in k}
        
        for chave, valor in sorted(melhorias.items()):
            nome = chave.replace('_melhoria_pct', '').replace('_', ' ').title()
            emoji = "✓" if valor > 0 else "✗"
            linhas.append(f"  {emoji} {nome:<40}: {valor:>+8.2f}%")
        
        return linhas


class ExportadorResultados:
    """
    Responsável pela exportação de métricas em múltiplos formatos
    Suporta: CSV, PNG, PDF
    """
    
    # Configurações de exportação
    CONFIG_PNG = {
        'dpi': 300,
        'bbox_inches': 'tight',
        'facecolor': 'white'
    }
    
    CONFIG_PDF = {
        'pagesize': landscape(A4),
        'titulo_cor': '#1a4d8f',
        'subtitulo_cor': '#2e7d32'
    }
    
    @staticmethod
    def exportar_csv(
        metricas_sem: Dict[str, float],
        metricas_com: Dict[str, float],
        caminho_arquivo: str
    ) -> Tuple[bool, str]:
        """
        Exporta métricas para arquivo CSV
        
        Args:
            metricas_sem: Métricas sem controlador
            metricas_com: Métricas com controlador
            caminho_arquivo: Caminho do arquivo de destino
        
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"')
                
                # Cabeçalho
                writer.writerow([
                    'Métrica',
                    'Sem Controlador',
                    'Com Controlador',
                    'Diferença',
                    'Melhoria (%)'
                ])
                
                # Dados
                todas_chaves = sorted(
                    set(metricas_sem.keys()) | set(metricas_com.keys())
                )
                
                for chave in todas_chaves:
                    valor_sem = metricas_sem.get(chave, 0.0)
                    valor_com = metricas_com.get(chave, 0.0)
                    diferenca = valor_com - valor_sem
                    
                    # Melhoria percentual
                    if abs(valor_sem) > MetricasControlador.EPSILON:
                        melhoria = ((valor_sem - valor_com) / abs(valor_sem)) * 100
                    else:
                        melhoria = 0.0
                    
                    nome_metrica = chave.replace('_', ' ').title()
                    
                    writer.writerow([
                        nome_metrica,
                        f"{valor_sem:.6f}" if isinstance(valor_sem, (int, float)) else valor_sem,
                        f"{valor_com:.6f}" if isinstance(valor_com, (int, float)) else valor_com,
                        f"{diferenca:.6f}" if isinstance(diferenca, (int, float)) else diferenca,
                        f"{melhoria:.2f}"
                    ])
            
            return True, f"CSV salvo com sucesso em {caminho_arquivo}"
            
        except PermissionError:
            return False, "Erro: Arquivo está aberto em outro programa"
        except Exception as e:
            return False, f"Erro ao salvar CSV: {str(e)}"
    
    @staticmethod
    def exportar_png(
        figura: plt.Figure,
        caminho_arquivo: str
    ) -> Tuple[bool, str]:
        """
        Exporta gráfico matplotlib para arquivo PNG
        
        Args:
            figura: Figura matplotlib
            caminho_arquivo: Caminho do arquivo de destino
        
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            figura.savefig(caminho_arquivo, **ExportadorResultados.CONFIG_PNG)
            return True, f"PNG salvo com sucesso em {caminho_arquivo}"
            
        except PermissionError:
            return False, "Erro: Arquivo está aberto em outro programa"
        except Exception as e:
            return False, f"Erro ao salvar PNG: {str(e)}"
    
    @staticmethod
    def exportar_pdf(
        metricas_sem: Dict[str, float],
        metricas_com: Dict[str, float],
        figuras_graficos: List[Tuple[str, plt.Figure]],
        caminho_arquivo: str
    ) -> Tuple[bool, str]:
        """
        Exporta relatório completo em PDF com métricas e gráficos
        
        Args:
            metricas_sem: Métricas sem controlador
            metricas_com: Métricas com controlador
            figuras_graficos: Lista de tuplas (titulo, figura_matplotlib)
            caminho_arquivo: Caminho do arquivo de destino
        
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            doc = SimpleDocTemplate(
                caminho_arquivo,
                pagesize=ExportadorResultados.CONFIG_PDF['pagesize']
            )
            story = []
            
            # Adicionar cabeçalho
            story.extend(ExportadorResultados._criar_cabecalho_pdf())
            
            # Adicionar tabela de métricas
            story.extend(
                ExportadorResultados._criar_tabela_metricas_pdf(
                    metricas_sem,
                    metricas_com
                )
            )
            
            # Adicionar gráficos
            if figuras_graficos:
                story.extend(
                    ExportadorResultados._criar_secao_graficos_pdf(figuras_graficos)
                )
            
            # Gerar documento
            doc.build(story)
            return True, f"PDF salvo com sucesso em {caminho_arquivo}"
            
        except PermissionError:
            return False, "Erro: Arquivo está aberto em outro programa"
        except Exception as e:
            return False, f"Erro ao salvar PDF: {str(e)}"
    
    @staticmethod
    def _criar_cabecalho_pdf() -> List[Any]:
        """Cria elementos do cabeçalho do PDF"""
        styles = getSampleStyleSheet()
        
        titulo_style = ParagraphStyle(
            'TituloCustom',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor(ExportadorResultados.CONFIG_PDF['titulo_cor']),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        elementos = [
            Paragraph("RELATÓRIO DE MÉTRICAS - SISTEMA DE CONTROLE", titulo_style),
            Paragraph(
                f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                styles['Normal']
            ),
            Spacer(1, 0.3 * inch)
        ]
        
        return elementos
    
    @staticmethod
    def _criar_tabela_metricas_pdf(
        metricas_sem: Dict[str, float],
        metricas_com: Dict[str, float]
    ) -> List[Any]:
        """Cria tabela de métricas para o PDF"""
        styles = getSampleStyleSheet()
        
        subtitulo_style = ParagraphStyle(
            'SubtituloCustom',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor(ExportadorResultados.CONFIG_PDF['subtitulo_cor']),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        elementos = [Paragraph("Comparação de Métricas", subtitulo_style)]
        
        # Dados da tabela
        dados_tabela = [[
            'Métrica',
            'Sem Controlador',
            'Com Controlador',
            'Melhoria (%)'
        ]]
        
        todas_chaves = sorted(
            set(metricas_sem.keys()) | set(metricas_com.keys())
        )
        
        for chave in todas_chaves:
            valor_sem = metricas_sem.get(chave, 0.0)
            valor_com = metricas_com.get(chave, 0.0)
            
            # Calcular melhoria
            if abs(valor_sem) > MetricasControlador.EPSILON:
                melhoria = ((valor_sem - valor_com) / abs(valor_sem)) * 100
            else:
                melhoria = 0.0
            
            nome = chave.replace('_', ' ').title()
            
            dados_tabela.append([
                nome,
                f"{valor_sem:.4f}" if isinstance(valor_sem, (int, float)) else str(valor_sem),
                f"{valor_com:.4f}" if isinstance(valor_com, (int, float)) else str(valor_com),
                f"{melhoria:+.2f}%" if isinstance(melhoria, (int, float)) else "-"
            ])
        
        # Criar e estilizar tabela
        tabela = Table(
            dados_tabela,
            colWidths=[2.5 * inch, 2 * inch, 2 * inch, 1.5 * inch]
        )
        
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4d8f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.3 * inch))
        
        return elementos
    
    @staticmethod
    def _criar_secao_graficos_pdf(
        figuras_graficos: List[Tuple[str, plt.Figure]]
    ) -> List[Any]:
        """Cria seção de gráficos para o PDF"""
        styles = getSampleStyleSheet()
        
        subtitulo_style = ParagraphStyle(
            'SubtituloCustom',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor(ExportadorResultados.CONFIG_PDF['subtitulo_cor']),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        elementos = [
            PageBreak(),
            Paragraph("Gráficos da Análise", subtitulo_style)
        ]
        
        for titulo_grafico, figura in figuras_graficos:
            try:
                # Salvar figura em buffer de memória
                img_buffer = io.BytesIO()
                figura.savefig(
                    img_buffer,
                    format='png',
                    dpi=100,
                    bbox_inches='tight'
                )
                img_buffer.seek(0)
                
                # Adicionar imagem ao PDF
                img = Image(img_buffer, width=8 * inch, height=4 * inch)
                elementos.append(img)
                elementos.append(Spacer(1, 0.2 * inch))
                
            except Exception as e:
                elementos.append(
                    Paragraph(
                        f"Erro ao adicionar gráfico '{titulo_grafico}': {str(e)}",
                        styles['Normal']
                    )
                )
        
        return elementos