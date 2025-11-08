"""
Módulo de Análise de Sistemas de Segunda Ordem
Análise completa de sistemas de controle de 2ª ordem em malha aberta e fechada
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

try:
    from tela import gerenciador_temas, CORES
except ImportError:
    class GerenciadorTemasFallback:
        def __init__(self):
            self.tema_atual = "dark"
        
        def obter_cores(self):
            return {
                "primaria": "#1a4d8f",
                "fundo_escuro": "#1a1a2e",
                "fundo_claro": "#16213e",
                "texto_principal": "#e4e4e4",
                "texto_secundario": "#94a3b8",
                "sucesso": "#059669",
                "erro": "#dc2626",
                "mode": "dark",
                "tema_atual": "dark"
            }
    gerenciador_temas = GerenciadorTemasFallback()
    CORES = gerenciador_temas.obter_cores()

class ErroValidacao(Exception):
    """Exceção customizada para erros de validação"""
    pass

class AnalisadorSegundaOrdem:
    """
    Classe para análise completa de sistemas de segunda ordem
    Centraliza TODA a lógica de análise, cálculos e plotagem
    """
    
    def __init__(self):
        self.wn = None
        self.zeta = None
        self.ganho = None
        self.tipo_malha = None
        self.tipo_entrada = None
        self.numerador = None
        self.denominador = None
        self.cache_respostas = {}
    
    @staticmethod
    def validar_coeficientes(coeficientes, nome="coeficientes"):
        """Validação consolidada"""
        if not coeficientes or len(coeficientes) == 0:
            raise ErroValidacao(f"❌ {nome.capitalize()} não pode estar vazio!")
        
        for i, coef in enumerate(coeficientes):
            if not isinstance(coef, (int, float, np.number)):
                raise ErroValidacao(f"❌ {nome}[{i}] não é número: {coef}")
            if math.isnan(coef) or math.isinf(coef):
                raise ErroValidacao(f"❌ {nome}[{i}] = NaN ou Inf")
    
    def extrair_parametros_de_funcao(self, numerador, denominador, tipo_malha='fechada'):
        """Extração com melhor tratamento de erros"""
        # Validações
        self.validar_coeficientes(numerador, "numerador")
        self.validar_coeficientes(denominador, "denominador")
        
        if len(denominador) != 3:
            raise ErroValidacao(
                f"❌ Sistema deve ser 2ª ordem!\n"
                f"   Denominador: {len(denominador)} coeficientes (esperado: 3)"
            )
        
        a0, a1, a2 = float(denominador[0]), float(denominador[1]), float(denominador[2])
        
        if abs(a0) < 1e-15:
            raise ErroValidacao("❌ Coeficiente a₀ (s²) não pode ser zero!")
        
        if abs(a2) < 1e-15:
            raise ErroValidacao("❌ Termo constante (a₂) não pode ser zero!")
        
        # Cálculos normalizados
        a1_norm = a1 / a0
        a2_norm = a2 / a0
        
        if a2_norm < 0:
            raise ErroValidacao("❌ Sistema não-físico: ωn² negativo!")
        
        try:
            wn = math.sqrt(a2_norm)
            zeta = a1_norm / (2 * wn) if wn > 0 else 0
            ganho = numerador[-1] / a2 if a2 != 0 else 1.0
            
            return wn, zeta, ganho
            
        except (ValueError, ZeroDivisionError) as e:
            raise ErroValidacao(f"❌ Erro cálculo: {str(e)}")
    
    def calcular_resposta_temporal(self, tempo_final=None, num_pontos=1000):
        """Cálculo com verificação de cache"""
        # Criar chave de cache
        cache_key = (self.wn, self.zeta, self.ganho, self.tipo_entrada, tempo_final, num_pontos)
        
        if cache_key in self.cache_respostas:
            return self.cache_respostas[cache_key]
        
        # Cálculo original
        try:
            if self.zeta < 0:
                return None, None
            
            if self.wn <= 0:
                return None, None
            
            # Determinar tempo final
            if tempo_final is None:
                if self.zeta > 0:
                    ts = 4 / (self.zeta * self.wn)
                    tempo_final = max(ts * 1.5, 5)
                else:
                    tempo_final = 10
            
            t = np.linspace(0, tempo_final, num_pontos)
            
            if self.tipo_entrada == 'degrau':
                if self.zeta == 0:
                    y = self.ganho * (1 - np.cos(self.wn * t))
                elif 0 < self.zeta < 1:
                    wd = self.wn * np.sqrt(np.maximum(1 - self.zeta**2, 0))
                    if wd > 0:
                        sigma = self.zeta * self.wn
                        phi = np.arctan(wd / (self.zeta * self.wn + 1e-10))
                        y = self.ganho * (1 - (np.exp(-sigma * t) / (np.sqrt(1 - self.zeta**2) + 1e-10)) * 
                                         np.sin(wd * t + phi))
                    else:
                        y = self.ganho * np.ones_like(t)
                elif self.zeta == 1:
                    y = self.ganho * (1 - np.exp(-self.wn * t) * (1 + self.wn * t))
                else:
                    discriminante = self.zeta**2 - 1
                    if discriminante > 0:
                        sqrt_disc = np.sqrt(discriminante)
                        s1 = -self.zeta * self.wn + self.wn * sqrt_disc
                        s2 = -self.zeta * self.wn - self.wn * sqrt_disc
                        A = s1 / (s1 - s2 + 1e-10)
                        B = -s2 / (s1 - s2 + 1e-10)
                        y = self.ganho * (1 - A * np.exp(np.maximum(s2 * t, -100)) - B * np.exp(np.maximum(s1 * t, -100)))
                    else:
                        y = self.ganho * np.ones_like(t)
            else:  # rampa
                if self.tipo_malha == 'fechada' and self.zeta > 0:
                    kv = self.ganho * self.wn * self.wn
                    erro_ss = 1 / (kv + 1e-10)
                    
                    if 0 < self.zeta < 1:
                        wd = self.wn * np.sqrt(np.maximum(1 - self.zeta**2, 0))
                        sigma = self.zeta * self.wn
                        y = t - erro_ss - (2 * self.zeta / (self.wn * np.sqrt(np.maximum(1 - self.zeta**2, 1e-10)))) * np.exp(-sigma * t) * np.sin(wd * t)
                    else:
                        y = t - erro_ss * (1 - np.exp(-self.wn * t))
                else:
                    y = t * 0.5
            
            # Salvar em cache
            resultado = (t, y)
            self.cache_respostas[cache_key] = resultado
            
            return resultado
            
        except Exception as e:
            print(f"Erro cálculo temporal: {str(e)}")
            return None, None
    
    def analisar_de_funcao_transferencia(self, numerador, denominador, tipo_malha='fechada', tipo_entrada='degrau'):
        """
        Analisa sistema de segunda ordem a partir da função de transferência
        
        Args:
            numerador: Lista de coeficientes do numerador
            denominador: Lista de coeficientes do denominador
            tipo_malha: 'fechada' ou 'aberta'
            tipo_entrada: 'degrau' ou 'rampa'
            
        Returns:
            str: Relatório completo da análise
        """
        try:
            wn, zeta, ganho = self.extrair_parametros_de_funcao(numerador, denominador, tipo_malha)
            
            self.numerador = numerador
            self.denominador = denominador
            self.tipo_entrada = tipo_entrada
            self.tipo_malha = tipo_malha
            self.wn = wn
            self.zeta = zeta
            self.ganho = ganho
            
            return self.analisar_sistema_completo(wn, zeta, ganho, tipo_malha, tipo_entrada)
            
        except ErroValidacao as e:
            return f"ERRO DE VALIDAÇÃO:\n{str(e)}"
        except Exception as e:
            return f"❌ ERRO na análise: {str(e)}\n\nVerifique se os valores inseridos estão corretos."
    
    def analisar_sistema_completo(self, wn, zeta, ganho=1.0, tipo_malha='fechada', tipo_entrada='degrau'):
        """
        Realiza análise completa do sistema de segunda ordem
        """
        # Validações adicionais
        if wn <= 0:
            return "❌ ERRO: Frequência natural deve ser positiva!"
        
        if math.isnan(wn) or math.isinf(wn):
            return "❌ ERRO: Frequência natural inválida!"
        
        if math.isnan(zeta) or math.isinf(zeta):
            return "❌ ERRO: Coeficiente de amortecimento inválido!"
        
        self.wn = wn
        self.zeta = zeta
        self.ganho = ganho
        self.tipo_malha = tipo_malha
        self.tipo_entrada = tipo_entrada
        
        resultado = []
        resultado.append("-" * 57)
        resultado.append("ANÁLISE COMPLETA DE SISTEMA DE SEGUNDA ORDEM".center(50))
        resultado.append("-" * 57)
        resultado.append("")
        
        resultado.append("📋 PARÂMETROS DO SISTEMA:")
        resultado.append("-" * 57)
        resultado.append(f"   Tipo de Malha: {tipo_malha.upper()}")
        resultado.append(f"   Tipo de Entrada: {tipo_entrada.upper()}")
        
        if self.numerador and self.denominador:
            resultado.append(f"   Numerador (coeficientes): {self.numerador}")
            resultado.append(f"   Denominador (coeficientes): {self.denominador}")
            resultado.append("")
        
        resultado.append(f"   Frequência Natural (ωn): {wn:.4f} rad/s")
        resultado.append(f"   Coeficiente de Amortecimento (ζ): {zeta:.4f}")
        resultado.append(f"   Ganho (K): {ganho:.4f}")
        resultado.append("")
        
        resultado.append("📐 FUNÇÃO DE TRANSFERÊNCIA:")
        resultado.append("-" * 57)
        if tipo_malha == 'fechada':
            resultado.append(f"   G(s) = {ganho * wn**2:.4f} / (s² + {2*zeta*wn:.4f}s + {wn**2:.4f})")
            resultado.append(f"   Forma padrão: G(s) = {ganho}·ωn² / (s² + 2ζωn·s + ωn²)")
        else:
            resultado.append(f"   G(s) = {ganho * wn**2:.4f} / (s² + {2*zeta*wn:.4f}s + {wn**2:.4f})")
            resultado.append(f"   Forma padrão (Malha Aberta): G(s) = K·ωn² / (s² + 2ζωn·s + ωn²)")
        resultado.append("")
        
        resultado.append("🔎 CLASSIFICAÇÃO DO SISTEMA:")
        resultado.append("-" * 57)
        classificacao = self.classificar_sistema()
        resultado.append(f"   {classificacao}")
        resultado.append("")
        
        resultado.append("📍 POLOS DO SISTEMA:")
        resultado.append("-" * 57)
        try:
            polos = self.calcular_polos()
            resultado.extend(polos)
        except Exception as e:
            resultado.append(f"   ⚠️ Erro ao calcular polos: {str(e)}")
        resultado.append("")
        
        resultado.append("-" * 57)
        resultado.append("🎯 CARACTERIZAÇÃO DA RESPOSTA".center(50))
        resultado.append("-" * 57)
        resultado.append("")
        
        try:
            if tipo_malha == 'aberta':
                resultado.append("📊 MALHA ABERTA - PARÂMETROS PRINCIPAIS:")
                resultado.append("-" * 57)
                resultado.append(f"   ζ (Coeficiente de Amortecimento): {zeta:.4f}")
                resultado.append(f"   ωn (Frequência Natural): {wn:.4f} rad/s")
                resultado.append("")
                
                if 0 < zeta < 1:
                    wd = wn * math.sqrt(1 - zeta**2)
                    resultado.append(f"   ωd (Frequência Natural Amortecida): {wd:.4f} rad/s")
                    resultado.append("")
                
            else:  # Malha fechada
                resultado.append("📊 MALHA FECHADA - CARACTERÍSTICAS TEMPORAIS:")
                resultado.append("-" * 57)
                
                if 0 < zeta < 1:
                    wd = wn * math.sqrt(1 - zeta**2)
                    tp = math.pi / wd
                    resultado.append(f"   Tp (Tempo de Pico): {tp:.4f} s")
                    resultado.append(f"      └─ Tempo para atingir o primeiro pico máximo")
                else:
                    resultado.append(f"   Tp (Tempo de Pico): Não aplicável (sistema sem overshoot)")
                resultado.append("")
                
                if zeta > 0:
                    ts_2 = 4 / (zeta * wn)
                    ts_5 = 3 / (zeta * wn)
                    resultado.append(f"   Ts (Tempo de Acomodação - 2%): {ts_2:.4f} s")
                    resultado.append(f"      └─ Tempo para permanecer dentro de ±2% do valor final")
                    resultado.append("")
                    resultado.append(f"   Ts (Tempo de Acomodação - 5%): {ts_5:.4f} s")
                    resultado.append(f"      └─ Tempo para permanecer dentro de ±5% do valor final")
                else:
                    resultado.append(f"   Ts: Sistema não estável ou não amortecido")
                resultado.append("")
                
                if 0 < zeta < 1:
                    mp_percent = 100 * math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))
                    resultado.append(f"   Mp (Máximo Sobressinal): {mp_percent:.2f}%")
                    resultado.append(f"      └─ Percentual de ultrapassagem do valor final")
                elif zeta == 0:
                    resultado.append(f"   Mp (Máximo Sobressinal): ∞ (oscilação contínua)")
                else:
                    resultado.append(f"   Mp (Máximo Sobressinal): 0.00%")
                    resultado.append(f"      └─ Sistema sem overshoot")
                resultado.append("")
                
                resultado.append(f"   Erro em Regime Permanente:")
                if tipo_entrada == 'degrau':
                    if ganho != 0:
                        if tipo_malha == 'fechada':
                            erro_percentual = abs(1 - ganho) * 100
                            resultado.append(f"      └─ e_ss (Entrada Degrau): {abs(1-ganho):.4f} ({erro_percentual:.2f}%)")
                            resultado.append(f"      └─ Valor Final: {ganho:.4f}")
                        else:
                            resultado.append(f"      └─ e_ss (Entrada Degrau): Infinito (malha aberta)")
                    else:
                        resultado.append(f"      └─ e_ss: Sistema sem ganho válido")
                else:  # rampa
                    if tipo_malha == 'fechada':
                        if ganho != 0 and zeta > 0 and wn > 0:
                            kv = ganho * wn * wn
                            erro_rampa = 1 / kv if kv != 0 else float('inf')
                            resultado.append(f"      └─ e_ss (Entrada Rampa): {erro_rampa:.4f}")
                            resultado.append(f"      └─ Kv (Constante de Velocidade): {kv:.4f}")
                        else:
                            resultado.append(f"      └─ e_ss (Entrada Rampa): Infinito")
                    else:
                        resultado.append(f"      └─ e_ss (Entrada Rampa): Infinito (malha aberta)")
                resultado.append("")
        except Exception as e:
            resultado.append(f"⚠️ Erro ao calcular características: {str(e)}")
            resultado.append("")
        
        resultado.append("⏱️ CARACTERÍSTICAS TEMPORAIS ADICIONAIS:")
        resultado.append("-" * 57)
        try:
            caracteristicas = self.calcular_caracteristicas_temporais()
            resultado.extend(caracteristicas)
        except Exception as e:
            resultado.append(f"   ⚠️ Erro: {str(e)}")
        resultado.append("")
        
        resultado.append("✅ ANÁLISE DE ESTABILIDADE:")
        resultado.append("-" * 57)
        try:
            estabilidade = self.analisar_estabilidade()
            resultado.extend(estabilidade)
        except Exception as e:
            resultado.append(f"   ⚠️ Erro: {str(e)}")
        resultado.append("")
        
        resultado.append("💡 RECOMENDAÇÕES E OBSERVAÇÕES:")
        resultado.append("-" * 57)
        try:
            recomendacoes = self.gerar_recomendacoes()
            resultado.extend(recomendacoes)
        except Exception as e:
            resultado.append(f"   ⚠️ Erro: {str(e)}")
        resultado.append("")
        
        resultado.append("=" * 57)
        resultado.append("RESUMO EXECUTIVO".center(50))
        resultado.append("=" * 57)
        try:
            resumo = self.gerar_resumo()
            resultado.extend(resumo)
        except Exception as e:
            resultado.append(f"⚠️ Erro ao gerar resumo: {str(e)}")
        resultado.append("")
        
        resultado.append("=" * 57)
        resultado.append("FIM DA ANÁLISE".center(50))
        resultado.append("=" * 57)
        
        return "\n".join(resultado)
    
    def gerar_resumo(self):
        """Gera resumo executivo com os parâmetros principais"""
        resultado = []
        
        resultado.append(f"   Sistema: {self.tipo_malha.upper()} | Entrada: {self.tipo_entrada.upper()}")
        resultado.append("")
        resultado.append(f"   ωn (Frequência Natural):          {self.wn:.4f} rad/s")
        resultado.append(f"   ζ (Coef. Amortecimento):          {self.zeta:.4f}")
        resultado.append(f"   K (Ganho):                        {self.ganho:.4f}")
        resultado.append("")
        
        if self.tipo_malha == 'fechada':
            if 0 < self.zeta < 1:
                wd = self.wn * math.sqrt(1 - self.zeta**2)
                tp = math.pi / wd
                resultado.append(f"   Tp (Tempo de Pico):               {tp:.4f} s")
                
                mp_percent = 100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2))
                resultado.append(f"   Mp (Máximo Sobressinal):          {mp_percent:.2f}%")
                
            elif self.zeta == 0:
                resultado.append(f"   Tp (Tempo de Pico):               Oscilação contínua")
                resultado.append(f"   Mp (Máximo Sobressinal):          Infinito")
            else:
                resultado.append(f"   Tp (Tempo de Pico):               Não aplicável")
                resultado.append(f"   Mp (Máximo Sobressinal):          0.00%")
            
            if self.zeta > 0:
                ts_2 = 4 / (self.zeta * self.wn)
                ts_5 = 3 / (self.zeta * self.wn)
                resultado.append(f"   Ts (Tempo Acomodação 2%):         {ts_2:.4f} s")
                resultado.append(f"   Ts (Tempo Acomodação 5%):         {ts_5:.4f} s")
            
            if self.tipo_entrada == 'degrau':
                erro = abs(1 - self.ganho)
                resultado.append(f"   Erro Regime (Degrau):             {erro:.4f} ({erro*100:.2f}%)")
            else:
                if self.ganho != 0 and self.zeta > 0 and self.wn > 0:
                    kv = self.ganho * self.wn * self.wn
                    erro_rampa = 1 / kv if kv != 0 else float('inf')
                    resultado.append(f"   Erro Regime (Rampa):              {erro_rampa:.4f}")
        
        return resultado
    
    def classificar_sistema(self):
        """Classifica o sistema quanto ao amortecimento"""
        if self.zeta < 0:
            return "⚠️ SISTEMA INSTÁVEL (ζ < 0)"
        elif self.zeta == 0:
            return "🔄 SISTEMA NÃO AMORTECIDO (ζ = 0) - Oscilação contínua"
        elif 0 < self.zeta < 1:
            return f"📉 SISTEMA SUBAMORTECIDO (0 < ζ < 1) - Resposta oscilatória com sobressinal"
        elif self.zeta == 1:
            return "⚡ SISTEMA CRITICAMENTE AMORTECIDO (ζ = 1) - Resposta mais rápida sem oscilação"
        else:
            return f"📈 SISTEMA SUPERAMORTECIDO (ζ > 1) - Resposta lenta sem oscilação"
    
    def calcular_polos(self):
        """Calcula e formata os polos do sistema"""
        resultado = []
        
        if self.zeta < 1:
            parte_real = -self.zeta * self.wn
            parte_imaginaria = self.wn * math.sqrt(abs(1 - self.zeta**2))
            
            resultado.append(f"   Polos Complexos Conjugados:")
            resultado.append(f"   s₁ = {parte_real:.4f} + j{parte_imaginaria:.4f}")
            resultado.append(f"   s₂ = {parte_real:.4f} - j{parte_imaginaria:.4f}")
            resultado.append("")
            resultado.append(f"   Parte Real: {parte_real:.4f}")
            resultado.append(f"   Parte Imaginária: ±{parte_imaginaria:.4f}")
            
            if self.zeta > 0:
                wd = parte_imaginaria
                resultado.append(f"   Frequência Natural Amortecida (ωd): {wd:.4f} rad/s")
            
        elif self.zeta == 1:
            polo = -self.wn
            resultado.append(f"   Polos Reais Repetidos:")
            resultado.append(f"   s₁ = s₂ = {polo:.4f}")
            
        else:
            s1 = -self.zeta * self.wn + self.wn * math.sqrt(self.zeta**2 - 1)
            s2 = -self.zeta * self.wn - self.wn * math.sqrt(self.zeta**2 - 1)
            
            resultado.append(f"   Polos Reais Distintos:")
            resultado.append(f"   s₁ = {s1:.4f}")
            resultado.append(f"   s₂ = {s2:.4f}")
        
        return resultado
    
    def calcular_caracteristicas_temporais(self):
        """Calcula as características temporais do sistema"""
        resultado = []
        
        if self.zeta < 0:
            resultado.append("   ⚠️ Sistema instável - características temporais não aplicáveis")
            return resultado
        
        if self.zeta == 0:
            resultado.append("   ⚠️ Sistema não amortecido - oscilação contínua")
            resultado.append(f"   Período de Oscilação (T): {2*math.pi/self.wn:.4f} s")
            resultado.append(f"   Frequência de Oscilação (f): {self.wn/(2*math.pi):.4f} Hz")
            return resultado
        
        if 0 < self.zeta < 1:
            wd = self.wn * math.sqrt(1 - self.zeta**2)
            beta = math.atan(math.sqrt(1 - self.zeta**2) / self.zeta)
            tr = (math.pi - beta) / wd
            resultado.append(f"   Tempo de Subida (Tr): {tr:.4f} s")
            resultado.append(f"      └─ Tempo para ir de 10% a 90% do valor final")
        elif self.zeta == 1:
            tr = 2.2 / self.wn
            resultado.append(f"   Tempo de Subida (Tr): {tr:.4f} s")
        else:
            tr = 2.2 / (self.zeta * self.wn)
            resultado.append(f"   Tempo de Subida (Tr): {tr:.4f} s (aproximado)")
        
        if self.zeta >= 1:
            tau = 1 / (self.zeta * self.wn)
            resultado.append(f"   Constante de Tempo (τ): {tau:.4f} s")
        
        return resultado
    
    def analisar_estabilidade(self):
        """Analisa a estabilidade do sistema"""
        resultado = []
        
        if self.zeta < 0:
            resultado.append("   ❌ SISTEMA INSTÁVEL")
            resultado.append("   Razão: Coeficiente de amortecimento negativo (ζ < 0)")
            resultado.append("   Consequência: Resposta divergente no tempo")
        elif self.zeta == 0:
            resultado.append("   ⚠️ SISTEMA MARGINALMENTE ESTÁVEL")
            resultado.append("   Razão: Amortecimento nulo (ζ = 0)")
            resultado.append("   Consequência: Oscilação permanente sem convergência")
        else:
            resultado.append("   ✅ SISTEMA ESTÁVEL")
            resultado.append(f"   Razão: ζ = {self.zeta:.4f} > 0")
            resultado.append("   Consequência: Resposta converge para valor final")
            
            if self.zeta < 1:
                parte_real = -self.zeta * self.wn
                resultado.append(f"   Polos com parte real negativa: {parte_real:.4f}")
            elif self.zeta == 1:
                polo = -self.wn
                resultado.append(f"   Polos reais negativos: {polo:.4f}")
            else:
                s1 = -self.zeta * self.wn + self.wn * math.sqrt(self.zeta**2 - 1)
                s2 = -self.zeta * self.wn - self.wn * math.sqrt(self.zeta**2 - 1)
                resultado.append(f"   Polos reais negativos: {s1:.4f} e {s2:.4f}")
        
        return resultado
    
    def gerar_recomendacoes(self):
        """Gera recomendações baseadas na análise"""
        resultado = []
        
        if self.tipo_entrada == 'rampa':
            resultado.append("   📌 OBSERVAÇÃO SOBRE ENTRADA RAMPA:")
            resultado.append("   • Entrada rampa gera erro de regime permanente maior que degrau")
            resultado.append("   • Erro depende da constante de velocidade Kv = K·ωn²")
            resultado.append("")
        
        if self.zeta < 0:
            resultado.append("   ⚠️ ATENÇÃO: Sistema instável!")
            resultado.append("   • Revisar o projeto do sistema")
        elif self.zeta == 0:
            resultado.append("   ⚠️ Sistema oscilatório:")
            resultado.append("   • Adicionar amortecimento ao sistema")
        elif 0 < self.zeta < 0.4:
            mp = 100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2))
            resultado.append("   📊 Sistema subamortecido com alto overshoot:")
            resultado.append(f"   • Overshoot atual: {mp:.2f}%")
            resultado.append("   • Considere aumentar ζ para reduzir oscilações")
        elif 0.4 <= self.zeta < 0.7:
            mp = 100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2))
            resultado.append("   ✅ Amortecimento adequado:")
            resultado.append(f"   • Overshoot moderado: {mp:.2f}%")
            resultado.append("   • Bom compromisso entre velocidade e estabilidade")
        elif 0.7 <= self.zeta < 1:
            mp = 100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2))
            resultado.append("   ✅ Sistema bem amortecido:")
            resultado.append(f"   • Baixo overshoot: {mp:.2f}%")
            resultado.append("   • Resposta suave com mínima oscilação")
        elif self.zeta == 1:
            resultado.append("   ⚡ Sistema criticamente amortecido (ÓTIMO):")
            resultado.append("   • Resposta mais rápida sem overshoot")
            resultado.append("   • Configuração ideal para muitas aplicações")
        else:
            resultado.append("   📈 Sistema superamortecido:")
            resultado.append("   • Sem overshoot mas resposta lenta")
            resultado.append("   • Considere reduzir ζ para melhorar velocidade")
        
        return resultado
    
    def plotar_resposta(self, frame_grafico=None):
        """
        Plota a resposta temporal do sistema com estilo profissional e tema dinâmico
        
        Args:
            frame_grafico: Frame opcional para embedding (não usado nesta versão)
            
        Returns:
            Figure: Objeto Figure do matplotlib
        """
        try:
            t, y = self.calcular_resposta_temporal()
            
            if t is None or y is None:
                return None
            
            cores_tema = gerenciador_temas.obter_cores()
            modo_tema = cores_tema.get("mode", "dark")
            tema_atual = getattr(gerenciador_temas, 'tema_atual', 'dark')
            
            bg_color = '#ffffff'
            fg_color = '#f8f9fa'
            text_color = '#000000'
            grid_color = '#898989'
            line_color = '#1f77b4'
            ref_color = '#ff7f0e'
            stable_color = '#2ca02c'
            peak_color = '#d62728'
            settling_color = '#9467bd'
            tolerance_color = '#ff9896'
            
            # Configurar o gráfico com fundo branco
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            # Plotar resposta
            ax.plot(t, y, line_color, linewidth=2.5, label='Resposta do Sistema', zorder=3)
            
            # Plotar entrada
            if self.tipo_entrada == 'degrau':
                ax.plot(t, np.ones_like(t) * self.ganho, ref_color, 
                       linewidth=1.5, linestyle='--', label='Entrada (Degrau)', alpha=0.7, zorder=2)
                
                # Marcar características para malha fechada
                if self.tipo_malha == 'fechada' and self.zeta > 0:
                    # Tempo de pico e Mp
                    if 0 < self.zeta < 1:
                        wd = self.wn * math.sqrt(1 - self.zeta**2)
                        tp = math.pi / wd
                        mp_valor = self.ganho * (1 + math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2)))
                        
                        ax.plot(tp, mp_valor, 'o', color=peak_color, markersize=8, 
                               label=f'Pico (Tp={tp:.3f}s)', zorder=4)
                        ax.axhline(y=mp_valor, color=peak_color, linestyle=':', alpha=0.5, linewidth=1)
                        ax.text(tp, mp_valor + 0.05 * self.ganho, f'Mp={((mp_valor/self.ganho - 1)*100):.1f}%', 
                               color=peak_color, fontsize=9, ha='center', fontweight='bold')
                    
                    # Banda de ±2% e ±5%
                    ax.axhline(y=self.ganho * 1.02, color=tolerance_color, linestyle=':', 
                              alpha=0.5, linewidth=1, label='±2%', zorder=1)
                    ax.axhline(y=self.ganho * 0.98, color=tolerance_color, linestyle=':', 
                              alpha=0.5, linewidth=1, zorder=1)
                    ax.axhline(y=self.ganho * 1.05, color=stable_color, linestyle=':', 
                              alpha=0.4, linewidth=1, label='±5%', zorder=1)
                    ax.axhline(y=self.ganho * 0.95, color=stable_color, linestyle=':', 
                              alpha=0.4, linewidth=1, zorder=1)
                    
                    # Marcar tempo de acomodação (2%)
                    if self.zeta > 0:
                        ts = 4 / (self.zeta * self.wn)
                        if ts < t[-1]:
                            ax.axvline(x=ts, color=settling_color, linestyle='--', 
                                      alpha=0.6, linewidth=1.5, label=f'Ts(2%)={ts:.2f}s', zorder=1)
            else:  # rampa
                ax.plot(t, t, ref_color, linewidth=1.5, linestyle='--', 
                       label='Entrada (Rampa)', alpha=0.7, zorder=2)
                
                # Mostrar erro de regime se aplicável
                if self.tipo_malha == 'fechada' and self.zeta > 0:
                    kv = self.ganho * self.wn * self.wn
                    erro_ss = 1 / kv if kv != 0 else 0
                    if erro_ss > 0 and erro_ss < 10:
                        ax.plot(t, t - erro_ss, stable_color, linewidth=1.5, 
                               linestyle=':', alpha=0.6, label=f'Entrada - e_ss ({erro_ss:.3f})', zorder=1)
            
            # Configurações do gráfico
            ax.set_xlabel('Tempo (s)', color=text_color, fontsize=10, fontweight='bold')
            ax.set_ylabel('Amplitude', color=text_color, fontsize=10, fontweight='bold')
            
            titulo = f'Resposta do Sistema - {self.tipo_malha.upper()} - Entrada: {self.tipo_entrada.upper()}'
            ax.set_title(titulo, color=text_color, fontsize=12, fontweight='bold', pad=20)
            
            # Grade
            ax.grid(True, alpha=0.3, color=grid_color, linestyle='--', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # Legenda
            legend = ax.legend(loc='best', facecolor='white', edgecolor=text_color, 
                              fontsize=8, framealpha=0.9)
            for text in legend.get_texts():
                text.set_color(text_color)
            
            # Colorir labels dos eixos
            ax.tick_params(axis='x', colors=text_color, labelsize=10)
            ax.tick_params(axis='y', colors=text_color, labelsize=10)
            
            # Colorir bordas
            for spine in ax.spines.values():
                spine.set_edgecolor(text_color)
                spine.set_linewidth(1.5)
            
            # Ajustar limites do eixo Y para melhor visualização
            y_min = min(0, np.min(y) * 1.1)
            y_max = np.max(y) * 1.15
            
            # Se houver pico, garantir que ele apareça
            if self.tipo_entrada == 'degrau' and 0 < self.zeta < 1:
                mp_valor = self.ganho * (1 + math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2)))
                y_max = max(y_max, mp_valor * 1.1)
            
            ax.set_ylim(y_min, y_max)
            ax.set_xlim(0, t[-1])
            
            # Adicionar informações do sistema no gráfico
            info_text = f'ωn = {self.wn:.3f} rad/s | ζ = {self.zeta:.3f} | K = {self.ganho:.3f}'
            info_bg = 'white'
            info_edge = stable_color
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   fontsize=7, verticalalignment='bottom', color=stable_color,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor=info_bg, alpha=0.9, edgecolor=info_edge),
                   fontweight='bold')
            
            # Adicionar classificação do sistema
            classificacao = self.classificar_sistema().split(' - ')[0]
            classificacao_limpa = classificacao.replace('📉', '').replace('⚡', '').replace('📈', '').replace('🔄', '').replace('⚠️', '').strip()
            class_color = ref_color
            ax.text(0.98, 0.98, classificacao_limpa, transform=ax.transAxes, 
                   fontsize=7, verticalalignment='bottom', horizontalalignment='right',
                   color=class_color, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor=info_bg, alpha=0.9, edgecolor=class_color))
            
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            print(f"Erro ao plotar gráfico: {str(e)}")
            return None

# Funções auxiliares para uso direto
def analisar_sistema(numerador, denominador, tipo_malha='fechada', tipo_entrada='degrau'):
    """
    Função auxiliar para análise rápida de um sistema
    
    Args:
        numerador: Lista de coeficientes do numerador
        denominador: Lista de coeficientes do denominador
        tipo_malha: 'fechada' ou 'aberta'
        tipo_entrada: 'degrau' ou 'rampa'
        
    Returns:
        str: Relatório completo da análise
    
    Exemplo:
        >>> resultado = analisar_sistema([100], [1, 10, 100], 'fechada', 'degrau')
        >>> print(resultado)
    """
    analisador = AnalisadorSegundaOrdem()
    return analisador.analisar_de_funcao_transferencia(numerador, denominador, tipo_malha, tipo_entrada)


def plotar_sistema(numerador, denominador, tipo_malha='fechada', tipo_entrada='degrau'):
    """
    Função auxiliar para plotagem rápida de um sistema
    
    Args:
        numerador: Lista de coeficientes do numerador
        denominador: Lista de coeficientes do denominador
        tipo_malha: 'fechada' ou 'aberta'
        tipo_entrada: 'degrau' ou 'rampa'
        
    Returns:
        Figure: Objeto Figure do matplotlib
    
    Exemplo:
        >>> fig = plotar_sistema([100], [1, 10, 100], 'fechada', 'degrau')
        >>> plt.show()
    """
    analisador = AnalisadorSegundaOrdem()
    analisador.analisar_de_funcao_transferencia(numerador, denominador, tipo_malha, tipo_entrada)
    return analisador.plotar_resposta()


# Exemplo de uso standalone
if __name__ == "__main__":
    print("=" * 80)
    print("TESTE DO MÓDULO DE ANÁLISE DE SISTEMAS DE 2ª ORDEM".center(80))
    print("=" * 80)
    print()
    
    # Exemplo 1: Sistema subamortecido
    print("EXEMPLO 1: Sistema Subamortecido")
    print("-" * 80)
    numerador = [100]
    denominador = [1, 10, 100]
    
    resultado = analisar_sistema(numerador, denominador, 'fechada', 'degrau')
    print(resultado)
    print()
    
    print()
    print("=" * 80)
    print("EXEMPLO 2: Sistema Criticamente Amortecido")
    print("=" * 80)
    print()
    
    # Exemplo 2: Sistema criticamente amortecido
    numerador2 = [25]
    denominador2 = [1, 10, 25]
    
    resultado2 = analisar_sistema(numerador2, denominador2, 'fechada', 'degrau')
    print(resultado2)
    
    print()
    print("=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)
