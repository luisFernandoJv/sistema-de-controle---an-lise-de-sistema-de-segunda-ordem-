"""
Módulo de Análise de Sistemas de Segunda Ordem
Análise completa de sistemas de controle de 2ª ordem em malha aberta e fechada
"""

import numpy as np
import math

class AnalisadorSegundaOrdem:
    """
    Classe para análise completa de sistemas de segunda ordem
    """
    
    def __init__(self):
        self.wn = None  # Frequência natural
        self.zeta = None  # Coeficiente de amortecimento
        self.ganho = None  # Ganho do sistema
        self.tipo_malha = None  # 'aberta' ou 'fechada'
        self.numerador = None  # Coeficientes do numerador
        self.denominador = None  # Coeficientes do denominador
    
    def extrair_parametros_de_funcao(self, numerador, denominador, tipo_malha='fechada'):
        """
        Extrai os parâmetros ωn, ζ e K a partir dos coeficientes da função de transferência
        
        Args:
            numerador: Lista com coeficientes do numerador [a, b, c, ...]
            denominador: Lista com coeficientes do denominador [a, b, c]
            tipo_malha: 'aberta' ou 'fechada'
        
        Returns:
            Tupla (wn, zeta, ganho) ou None se não for segunda ordem
        """
        # Verificar se é realmente segunda ordem
        if len(denominador) != 3:
            raise ValueError(f"Sistema não é de segunda ordem! Denominador tem grau {len(denominador)-1}")
        
        # Normalizar denominador (dividir por a0)
        a0 = denominador[0]  # Coeficiente de s²
        a1 = denominador[1]  # Coeficiente de s
        a2 = denominador[2]  # Termo constante
        
        if a0 == 0:
            raise ValueError("Coeficiente de s² não pode ser zero!")
        
        # Normalizar
        a1_norm = a1 / a0
        a2_norm = a2 / a0
        
        # Forma padrão: s² + 2ζωn·s + ωn²
        # Portanto: ωn² = a2_norm e 2ζωn = a1_norm
        
        if a2_norm <= 0:
            raise ValueError("Sistema instável ou não-físico! ωn² deve ser positivo.")
        
        wn = math.sqrt(a2_norm)
        
        if wn == 0:
            raise ValueError("Frequência natural não pode ser zero!")
        
        zeta = a1_norm / (2 * wn)
        
        # Calcular ganho a partir do numerador
        # K = b_n / a_n (termo constante do numerador / termo constante do denominador)
        if len(numerador) > 0:
            # Pegar o último elemento (termo constante)
            ganho_num = numerador[-1]
            ganho_den = a2
            ganho = ganho_num / ganho_den if ganho_den != 0 else 1.0
        else:
            ganho = 1.0
        
        return wn, zeta, ganho
    
    def analisar_de_funcao_transferencia(self, numerador, denominador, tipo_malha='fechada'):
        """
        Analisa sistema de segunda ordem a partir da função de transferência
        
        Args:
            numerador: Lista com coeficientes [a, b, c, ...] (maior → menor grau)
            denominador: Lista com coeficientes [a, b, c] (maior → menor grau)
            tipo_malha: 'aberta' ou 'fechada'
        
        Returns:
            String formatada com todos os resultados
        """
        try:
            # Extrair parâmetros
            wn, zeta, ganho = self.extrair_parametros_de_funcao(numerador, denominador, tipo_malha)
            
            # Armazenar
            self.numerador = numerador
            self.denominador = denominador
            
            # Realizar análise completa
            return self.analisar_sistema_completo(wn, zeta, ganho, tipo_malha)
            
        except Exception as e:
            return f"ERRO na análise: {str(e)}"
    
    def analisar_sistema_completo(self, wn, zeta, ganho=1.0, tipo_malha='fechada'):
        """
        Realiza análise completa do sistema de segunda ordem
        
        Args:
            wn: Frequência natural (rad/s)
            zeta: Coeficiente de amortecimento
            ganho: Ganho do sistema
            tipo_malha: 'aberta' ou 'fechada'
        
        Returns:
            String formatada com todos os resultados
        """
        self.wn = wn
        self.zeta = zeta
        self.ganho = ganho
        self.tipo_malha = tipo_malha
        
        resultado = []
        resultado.append("=" * 80)
        resultado.append("ANÁLISE COMPLETA DE SISTEMA DE SEGUNDA ORDEM".center(80))
        resultado.append("=" * 80)
        resultado.append("")
        
        # Informações do sistema
        resultado.append("📋 PARÂMETROS DO SISTEMA:")
        resultado.append("-" * 80)
        resultado.append(f"   Tipo de Malha: {tipo_malha.upper()}")
        
        # Mostrar função de transferência original se disponível
        if self.numerador and self.denominador:
            resultado.append(f"   Numerador (coeficientes): {self.numerador}")
            resultado.append(f"   Denominador (coeficientes): {self.denominador}")
            resultado.append("")
        
        resultado.append(f"   Frequência Natural (ωn): {wn:.4f} rad/s")
        resultado.append(f"   Coeficiente de Amortecimento (ζ): {zeta:.4f}")
        resultado.append(f"   Ganho (K): {ganho:.4f}")
        resultado.append("")
        
        # Função de transferência
        resultado.append("🔍 FUNÇÃO DE TRANSFERÊNCIA:")
        resultado.append("-" * 80)
        if tipo_malha == 'fechada':
            resultado.append(f"   G(s) = {ganho * wn**2:.4f} / (s² + {2*zeta*wn:.4f}s + {wn**2:.4f})")
            resultado.append(f"   Forma padrão: G(s) = {ganho}·ωn² / (s² + 2ζωn·s + ωn²)")
        else:
            resultado.append(f"   G(s) = {ganho * wn**2:.4f} / (s² + {2*zeta*wn:.4f}s + {wn**2:.4f})")
            resultado.append(f"   Forma padrão (Malha Aberta): G(s) = K·ωn² / (s² + 2ζωn·s + ωn²)")
        resultado.append("")
        
        # Classificação do sistema
        resultado.append("🔎 CLASSIFICAÇÃO DO SISTEMA:")
        resultado.append("-" * 80)
        classificacao = self.classificar_sistema()
        resultado.append(f"   {classificacao}")
        resultado.append("")
        
        # Polos do sistema
        resultado.append("📍 POLOS DO SISTEMA:")
        resultado.append("-" * 80)
        polos = self.calcular_polos()
        resultado.extend(polos)
        resultado.append("")
        
        # Características temporais
        resultado.append("⏱️  CARACTERÍSTICAS TEMPORAIS:")
        resultado.append("-" * 80)
        caracteristicas = self.calcular_caracteristicas_temporais()
        resultado.extend(caracteristicas)
        resultado.append("")
        
        # Características de resposta
        resultado.append("📊 CARACTERÍSTICAS DA RESPOSTA AO DEGRAU:")
        resultado.append("-" * 80)
        resposta = self.calcular_resposta_degrau()
        resultado.extend(resposta)
        resultado.append("")
        
        # Análise de estabilidade
        resultado.append("✅ ANÁLISE DE ESTABILIDADE:")
        resultado.append("-" * 80)
        estabilidade = self.analisar_estabilidade()
        resultado.extend(estabilidade)
        resultado.append("")
        
        # Recomendações
        resultado.append("💡 RECOMENDAÇÕES E OBSERVAÇÕES:")
        resultado.append("-" * 80)
        recomendacoes = self.gerar_recomendacoes()
        resultado.extend(recomendacoes)
        resultado.append("")
        
        # Resumo dos parâmetros principais
        resultado.append("=" * 80)
        resultado.append("RESUMO DOS PARÂMETROS PRINCIPAIS".center(80))
        resultado.append("=" * 80)
        resumo = self.gerar_resumo()
        resultado.extend(resumo)
        resultado.append("")
        
        resultado.append("=" * 80)
        resultado.append("FIM DA ANÁLISE".center(80))
        resultado.append("=" * 80)
        
        return "\n".join(resultado)
    
    def gerar_resumo(self):
        """Gera resumo com os parâmetros principais"""
        resultado = []
        
        resultado.append(f"   ωn (Frequência Natural):          {self.wn:.4f} rad/s")
        resultado.append(f"   ζ (Coef. Amortecimento):          {self.zeta:.4f}")
        resultado.append(f"   K (Ganho):                        {self.ganho:.4f}")
        resultado.append("")
        
        if 0 < self.zeta < 1:
            # Tempo de pico
            wd = self.wn * math.sqrt(1 - self.zeta**2)
            tp = math.pi / wd
            resultado.append(f"   Tp (Tempo de Pico):               {tp:.4f} s")
            
            # Overshoot
            mp_percent = 100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2))
            resultado.append(f"   Mp (Máximo Sobressinal):          {mp_percent:.2f}%")
            
        elif self.zeta == 0:
            resultado.append(f"   Tp (Tempo de Pico):               Oscilação contínua")
            resultado.append(f"   Mp (Máximo Sobressinal):          Infinito")
        else:
            resultado.append(f"   Tp (Tempo de Pico):               Não aplicável (sem overshoot)")
            resultado.append(f"   Mp (Máximo Sobressinal):          0%")
        
        # Tempo de acomodação
        if self.zeta > 0:
            ts_2 = 4 / (self.zeta * self.wn)
            ts_5 = 3 / (self.zeta * self.wn)
            resultado.append(f"   Ts (Tempo Acomodação 2%):         {ts_2:.4f} s")
            resultado.append(f"   Ts (Tempo Acomodação 5%):         {ts_5:.4f} s")
        
        # Tempo de subida
        if 0 < self.zeta < 1:
            wd = self.wn * math.sqrt(1 - self.zeta**2)
            beta = math.atan(math.sqrt(1 - self.zeta**2) / self.zeta)
            tr = (math.pi - beta) / wd
            resultado.append(f"   Tr (Tempo de Subida):             {tr:.4f} s")
        elif self.zeta == 1:
            tr = 2.2 / self.wn
            resultado.append(f"   Tr (Tempo de Subida):             {tr:.4f} s")
        elif self.zeta > 1:
            tr = 2.2 / (self.zeta * self.wn)
            resultado.append(f"   Tr (Tempo de Subida):             {tr:.4f} s (aprox.)")
        
        # Valor final e erro
        if self.tipo_malha == 'fechada':
            valor_final = self.ganho
            erro = 1 - valor_final
            resultado.append(f"   Valor Final (y_ss):               {valor_final:.4f}")
            resultado.append(f"   Erro Regime Permanente:           {abs(erro)*100:.2f}%")
        
        return resultado
    
    def classificar_sistema(self):
        """Classifica o sistema quanto ao amortecimento"""
        if self.zeta < 0:
            return "⚠️  SISTEMA INSTÁVEL (ζ < 0)"
        elif self.zeta == 0:
            return "🔄 SISTEMA NÃO AMORTECIDO (ζ = 0) - Oscilação contínua"
        elif 0 < self.zeta < 1:
            return f"📉 SISTEMA SUBAMORTECIDO (0 < ζ < 1) - Resposta oscilatória com sobressinal"
        elif self.zeta == 1:
            return "⚡ SISTEMA CRITICAMENTE AMORTECIDO (ζ = 1) - Resposta mais rápida sem oscilação"
        else:  # zeta > 1
            return f"📈 SISTEMA SUPERAMORTECIDO (ζ > 1) - Resposta lenta sem oscilação"
    
    def calcular_polos(self):
        """Calcula e formata os polos do sistema"""
        resultado = []
        
        if self.zeta < 1:
            # Polos complexos conjugados
            parte_real = -self.zeta * self.wn
            parte_imaginaria = self.wn * math.sqrt(1 - self.zeta**2)
            
            resultado.append(f"   Polos Complexos Conjugados:")
            resultado.append(f"   s₁ = {parte_real:.4f} + j{parte_imaginaria:.4f}")
            resultado.append(f"   s₂ = {parte_real:.4f} - j{parte_imaginaria:.4f}")
            resultado.append("")
            resultado.append(f"   Parte Real: {parte_real:.4f}")
            resultado.append(f"   Parte Imaginária: ±{parte_imaginaria:.4f}")
            
            # Frequência natural amortecida
            wd = parte_imaginaria
            resultado.append(f"   Frequência Natural Amortecida (ωd): {wd:.4f} rad/s")
            
        elif self.zeta == 1:
            # Polos reais repetidos
            polo = -self.wn
            resultado.append(f"   Polos Reais Repetidos:")
            resultado.append(f"   s₁ = s₂ = {polo:.4f}")
            
        else:  # zeta > 1
            # Polos reais distintos
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
            resultado.append("   ⚠️  Sistema instável - características temporais não aplicáveis")
            return resultado
        
        if self.zeta == 0:
            resultado.append("   ⚠️  Sistema não amortecido - oscilação contínua")
            resultado.append(f"   Período de Oscilação (T): {2*math.pi/self.wn:.4f} s")
            resultado.append(f"   Frequência de Oscilação (f): {self.wn/(2*math.pi):.4f} Hz")
            return resultado
        
        # Tempo de subida (Rise Time) - aproximação para sistemas subamortecidos
        if 0 < self.zeta < 1:
            wd = self.wn * math.sqrt(1 - self.zeta**2)
            beta = math.atan(math.sqrt(1 - self.zeta**2) / self.zeta)
            tr = (math.pi - beta) / wd
            resultado.append(f"   Tempo de Subida (Tr): {tr:.4f} s")
            resultado.append(f"      (Tempo para ir de 10% a 90% do valor final)")
        elif self.zeta == 1:
            tr = 2.2 / self.wn
            resultado.append(f"   Tempo de Subida (Tr): {tr:.4f} s")
        else:
            # Para sistemas superamortecidos, aproximação
            tr = 2.2 / (self.zeta * self.wn)
            resultado.append(f"   Tempo de Subida (Tr): {tr:.4f} s (aproximado)")
        
        # Tempo de pico (Peak Time) - apenas para sistemas subamortecidos
        if 0 < self.zeta < 1:
            wd = self.wn * math.sqrt(1 - self.zeta**2)
            tp = math.pi / wd
            resultado.append(f"   Tempo de Pico (Tp): {tp:.4f} s")
            resultado.append(f"      (Tempo para atingir o primeiro pico)")
        else:
            resultado.append(f"   Tempo de Pico (Tp): Não aplicável (sistema sem overshoot)")
        
        # Tempo de acomodação (Settling Time) - critério de 2%
        ts_2 = 4 / (self.zeta * self.wn)
        resultado.append(f"   Tempo de Acomodação 2% (Ts): {ts_2:.4f} s")
        resultado.append(f"      (Tempo para permanecer dentro de ±2% do valor final)")
        
        # Tempo de acomodação - critério de 5%
        ts_5 = 3 / (self.zeta * self.wn)
        resultado.append(f"   Tempo de Acomodação 5% (Ts): {ts_5:.4f} s")
        resultado.append(f"      (Tempo para permanecer dentro de ±5% do valor final)")
        
        # Constante de tempo
        if self.zeta >= 1:
            tau = 1 / (self.zeta * self.wn)
            resultado.append(f"   Constante de Tempo (τ): {tau:.4f} s")
        
        return resultado
    
    def calcular_resposta_degrau(self):
        """Calcula características da resposta ao degrau unitário"""
        resultado = []
        
        if self.zeta < 0:
            resultado.append("   ⚠️  Sistema instável - resposta divergente")
            return resultado
        
        # Valor em regime permanente
        if self.tipo_malha == 'fechada':
            valor_final = self.ganho
        else:
            resultado.append("   ⚠️  Malha aberta - valor final depende da entrada")
            valor_final = self.ganho
        
        resultado.append(f"   Valor Final (Regime Permanente): {valor_final:.4f}")
        resultado.append("")
        
        # Sobressinal (Overshoot) - apenas para sistemas subamortecidos
        if 0 < self.zeta < 1:
            mp_percent = 100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2))
            mp_valor = valor_final * (1 + mp_percent/100)
            
            resultado.append(f"   Máximo Sobressinal (Mp): {mp_percent:.2f}%")
            resultado.append(f"   Valor do Pico: {mp_valor:.4f}")
            resultado.append(f"      (Máximo ultrapassado acima do valor final)")
        elif self.zeta == 0:
            resultado.append(f"   Máximo Sobressinal (Mp): Infinito (oscilação contínua)")
        else:
            resultado.append(f"   Máximo Sobressinal (Mp): 0% (sem overshoot)")
        
        resultado.append("")
        
        # Erro em regime permanente
        if self.tipo_malha == 'fechada':
            erro_regime = 1 - valor_final
            resultado.append(f"   Erro em Regime Permanente: {erro_regime:.4f}")
            resultado.append(f"   Erro Percentual: {abs(erro_regime)*100:.2f}%")
        else:
            resultado.append(f"   Erro em Regime Permanente (Malha Aberta): Não aplicável")
        
        return resultado
    
    def analisar_estabilidade(self):
        """Analisa a estabilidade do sistema"""
        resultado = []
        
        if self.zeta < 0:
            resultado.append("   ❌ SISTEMA INSTÁVEL")
            resultado.append("   Razão: Coeficiente de amortecimento negativo (ζ < 0)")
            resultado.append("   Consequência: Resposta divergente no tempo")
        elif self.zeta == 0:
            resultado.append("   ⚠️  SISTEMA MARGINALMENTE ESTÁVEL")
            resultado.append("   Razão: Amortecimento nulo (ζ = 0)")
            resultado.append("   Consequência: Oscilação permanente sem convergência")
        else:
            resultado.append("   ✅ SISTEMA ESTÁVEL")
            resultado.append(f"   Razão: ζ = {self.zeta:.4f} > 0")
            resultado.append("   Consequência: Resposta converge para valor final")
            
            # Análise dos polos
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
        
        resultado.append("")
        
        # Margem de estabilidade
        if self.zeta > 0:
            resultado.append("   🔍 MARGEM DE ESTABILIDADE:")
            if self.zeta < 1:
                margem = self.zeta * self.wn
                resultado.append(f"   Margem de Fase: Relacionada a ζ = {self.zeta:.4f}")
                resultado.append(f"   Taxa de Decaimento: {margem:.4f} (|parte real dos polos|)")
            else:
                resultado.append(f"   Sistema bem amortecido com ζ = {self.zeta:.4f}")
        
        return resultado
    
    def gerar_recomendacoes(self):
        """Gera recomendações baseadas na análise"""
        resultado = []
        
        if self.zeta < 0:
            resultado.append("   ⚠️  ATENÇÃO: Sistema instável!")
            resultado.append("   • Revisar o projeto do sistema")
            resultado.append("   • Verificar sinais de realimentação")
            resultado.append("   • Considerar adicionar compensação")
        
        elif self.zeta == 0:
            resultado.append("   ⚠️  Sistema oscilatório:")
            resultado.append("   • Adicionar amortecimento ao sistema")
            resultado.append("   • Considerar usar um controlador PD ou PID")
            resultado.append("   • Revisar parâmetros do sistema")
        
        elif 0 < self.zeta < 0.4:
            resultado.append("   📊 Sistema subamortecido com alto overshoot:")
            resultado.append(f"   • Overshoot atual: {100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2)):.2f}%")
            resultado.append("   • Considerar aumentar o amortecimento (ζ) para reduzir oscilações")
            resultado.append("   • Ideal para sistemas que precisam de resposta rápida")
            resultado.append("   • Cuidado com aplicações sensíveis a overshoot")
        
        elif 0.4 <= self.zeta < 0.7:
            resultado.append("   ✅ Amortecimento adequado para muitas aplicações:")
            resultado.append(f"   • Overshoot moderado: {100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2)):.2f}%")
            resultado.append("   • Boa velocidade de resposta")
            resultado.append("   • Compromisso entre rapidez e estabilidade")
            resultado.append("   • Recomendado para sistemas de controle gerais")
        
        elif 0.7 <= self.zeta < 1:
            resultado.append("   ✅ Sistema bem amortecido:")
            resultado.append(f"   • Baixo overshoot: {100 * math.exp(-math.pi * self.zeta / math.sqrt(1 - self.zeta**2)):.2f}%")
            resultado.append("   • Resposta suave e controlada")
            resultado.append("   • Ideal para aplicações que não toleram oscilações")
        
        elif self.zeta == 1:
            resultado.append("   ⚡ Sistema criticamente amortecido (ÓTIMO):")
            resultado.append("   • Resposta mais rápida possível sem overshoot")
            resultado.append("   • Sem oscilações")
            resultado.append("   • Ideal para a maioria das aplicações de controle")
        
        else:  # zeta > 1
            resultado.append("   📈 Sistema superamortecido:")
            resultado.append("   • Sem overshoot (resposta monotônica)")
            resultado.append("   • Resposta lenta comparada ao criticamente amortecido")
            resultado.append("   • Considerar reduzir ζ para melhorar velocidade de resposta")
            resultado.append("   • Adequado quando estabilidade é mais importante que velocidade")
        
        resultado.append("")
        
        # Recomendações sobre frequência natural
        resultado.append("   🎯 Sobre a Frequência Natural (ωn):")
        if self.wn < 1:
            resultado.append(f"   • ωn = {self.wn:.4f} rad/s é relativamente baixa")
            resultado.append("   • Sistema terá resposta lenta")
            resultado.append("   • Considerar aumentar ωn se velocidade for importante")
        elif 1 <= self.wn <= 10:
            resultado.append(f"   • ωn = {self.wn:.4f} rad/s está em faixa adequada")
            resultado.append("   • Boa velocidade de resposta")
        else:
            resultado.append(f"   • ωn = {self.wn:.4f} rad/s é alta")
            resultado.append("   • Sistema muito rápido")
            resultado.append("   • Atenção a ruídos e limitações físicas")
        
        resultado.append("")
        
        # Recomendações específicas do tipo de malha
        if self.tipo_malha == 'fechada':
            resultado.append("   🔄 Sistema em Malha Fechada:")
            resultado.append("   • Apresenta erro de regime permanente baseado no ganho")
            resultado.append("   • Realimentação melhora estabilidade")
            resultado.append("   • Considerar controlador para melhorar desempenho")
        else:
            resultado.append("   📂 Sistema em Malha Aberta:")
            resultado.append("   • Não há correção automática de erros")
            resultado.append("   • Sensível a perturbações e variações de parâmetros")
            resultado.append("   • Considerar implementar malha fechada para melhor controle")
        
        resultado.append("")
        
        # Fórmulas úteis
        resultado.append("   📐 FÓRMULAS PRINCIPAIS UTILIZADAS:")
        resultado.append("   • Função de Transferência: G(s) = K·ωn² / (s² + 2ζωn·s + ωn²)")
        resultado.append("   • Polos (ζ<1): s = -ζωn ± jωn√(1-ζ²)")
        resultado.append("   • Overshoot: Mp(%) = 100·e^(-πζ/√(1-ζ²))")
        resultado.append("   • Tempo de Pico: Tp = π / (ωn√(1-ζ²))")
        resultado.append("   • Tempo de Acomodação (2%): Ts = 4 / (ζωn)")
        resultado.append("   • Tempo de Acomodação (5%): Ts = 3 / (ζωn)")
        
        return resultado
    
    def calcular_resposta_temporal(self, tempo_final=10, num_pontos=1000):
        """
        Calcula a resposta temporal do sistema (para plotagem futura)
        
        Args:
            tempo_final: Tempo final da simulação
            num_pontos: Número de pontos na simulação
        
        Returns:
            Tupla (tempo, resposta)
        """
        if self.zeta < 0:
            return None, None
        
        t = np.linspace(0, tempo_final, num_pontos)
        
        if self.zeta == 0:
            # Sistema não amortecido
            y = self.ganho * (1 - np.cos(self.wn * t))
        
        elif 0 < self.zeta < 1:
            # Sistema subamortecido
            wd = self.wn * math.sqrt(1 - self.zeta**2)
            sigma = self.zeta * self.wn
            phi = math.atan(math.sqrt(1 - self.zeta**2) / self.zeta)
            
            y = self.ganho * (1 - (np.exp(-sigma * t) / math.sqrt(1 - self.zeta**2)) * 
                             np.sin(wd * t + phi))
        
        elif self.zeta == 1:
            # Sistema criticamente amortecido
            y = self.ganho * (1 - np.exp(-self.wn * t) * (1 + self.wn * t))
        
        else:  # zeta > 1
            # Sistema superamortecido
            s1 = -self.zeta * self.wn + self.wn * math.sqrt(self.zeta**2 - 1)
            s2 = -self.zeta * self.wn - self.wn * math.sqrt(self.zeta**2 - 1)
            
            A = s1 / (s1 - s2)
            B = -s2 / (s1 - s2)
            
            y = self.ganho * (1 - A * np.exp(s2 * t) - B * np.exp(s1 * t))
        
        return t, y


# Função auxiliar para testes
def exemplo_uso():
    """Exemplo de uso do analisador"""
    analisador = AnalisadorSegundaOrdem()
    
    # Exemplo 1: Sistema subamortecido
    print("EXEMPLO 1: Sistema Subamortecido")
    resultado1 = analisador.analisar_sistema_completo(wn=10, zeta=0.5, ganho=1.0, tipo_malha='fechada')
    print(resultado1)
    print("\n" + "="*80 + "\n")
    
    # Exemplo 2: Sistema criticamente amortecido
    print("EXEMPLO 2: Sistema Criticamente Amortecido")
    resultado2 = analisador.analisar_sistema_completo(wn=8, zeta=1.0, ganho=1.0, tipo_malha='fechada')
    print(resultado2)
    print("\n" + "="*80 + "\n")
    
    # Exemplo 3: Sistema superamortecido
    print("EXEMPLO 3: Sistema Superamortecido")
    resultado3 = analisador.analisar_sistema_completo(wn=5, zeta=1.5, ganho=1.0, tipo_malha='aberta')
    print(resultado3)


if __name__ == "__main__":
    exemplo_uso()