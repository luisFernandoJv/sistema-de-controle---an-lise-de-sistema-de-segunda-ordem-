"""
Módulo para Análise do Lugar Geométrico das Raízes (Root Locus)
Baseado no código MATLAB LGR_.m
"""

import control.matlab as matlab
import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Optional
import warnings

warnings.filterwarnings('ignore')


class ErroValidacaoLGR(Exception):
    """Exceção personalizada para erros de validação no LGR"""
    pass


class AnalisadorLGR:
    """Classe para análise completa do Lugar Geométrico das Raízes"""
    
    def __init__(self, tolerancia: float = 1e-2):
        """
        Inicializa o analisador LGR
        
        Args:
            tolerancia: Tolerância para comparações numéricas
        """
        self.tol = tolerancia
        self.num_raw = []  # Para SymPy
        self.den_raw = []  # Para SymPy
        self.polos = None
        self.zeros = None
        self.n = 0  # número de polos
        self.m = 0  # número de zeros
        
    def configurar_sistema(self, numerador: List[float], denominador: List[float]):
        """
        Configura o sistema a ser analisado
        
        Args:
            numerador: Coeficientes do numerador
            denominador: Coeficientes do denominador
        """
        # Salvar coeficientes brutos para SymPy
        self.num_raw = numerador
        self.den_raw = denominador

        # Usar floats para a biblioteca de controle (numpy)
        num_float = np.array(numerador, dtype=float)
        den_float = np.array(denominador, dtype=float)
        
        # Validações
        if len(den_float) == 0:
            raise ErroValidacaoLGR("Denominador não pode ser vazio!")
        
        if abs(den_float[0]) < self.tol:
            raise ErroValidacaoLGR("Primeiro coeficiente do denominador não pode ser zero!")
        
        # Criar sistema de transferência
        self.sistema = matlab.tf(num_float, den_float)
        
        # Encontrar polos e zeros
        self.polos = matlab.pole(self.sistema)
        self.zeros = matlab.zero(self.sistema)
        
        self.n = len(self.polos)
        self.m = len(self.zeros)
        
    def analisar_segmentos(self) -> Tuple[List[Tuple[float, float]], List[bool]]:
        """
        Parte 1: Análise dos segmentos no eixo real
        
        Returns:
            Tupla contendo lista de segmentos e lista de flags indicando se fazem parte do LGR
        """
        # Filtrar polos e zeros reais
        polos_reais = self.polos[np.abs(np.imag(self.polos)) < self.tol].real
        zeros_reais = self.zeros[np.abs(np.imag(self.zeros)) < self.tol].real if len(self.zeros) > 0 else np.array([])
        
        # Juntar e ordenar em ordem decrescente (igual ao MATLAB)
        raizes_reais = np.sort(np.concatenate([polos_reais, zeros_reais]))[::-1]
        
        # Adicionar extremos
        raizes_reais_ext = np.concatenate([[np.inf], raizes_reais, [-np.inf]])
        
        segmentos = []
        faz_parte = []
        
        # Loop (k=0, 1, 2, ...) é análogo ao (k=1, 2, 3, ...) do MATLAB
        for k in range(len(raizes_reais_ext) - 1):
            seg = (raizes_reais_ext[k], raizes_reais_ext[k + 1])
            segmentos.append(seg)
            
            # MATLAB: "mod(k, 2) == 0" é "Faz parte" (pois k começa em 1)
            # Python: "k % 2 == 1" é "Faz parte" (pois k começa em 0)
            pertence = (k % 2 == 1) and abs(seg[0] - seg[1]) > self.tol
            faz_parte.append(pertence)
        
        return segmentos, faz_parte
    
    def calcular_assintotas(self) -> Dict:
        """
        Parte 2: Cálculo das assíntotas
        
        Returns:
            Dicionário com informações das assíntotas
        """
        num_assint = self.n - self.m
        
        if num_assint <= 0:
            return {
                'numero': 0,
                'sigma': None,
                'angulos': []
            }
        
        # Centro das assíntotas (sigma)
        sigma = (np.sum(self.polos) - np.sum(self.zeros)) / num_assint
        
        # Ângulos das assíntotas
        angulos = [(2 * k - 1) * 180 / num_assint for k in range(1, num_assint + 1)]
        
        return {
            'numero': num_assint,
            'sigma': sigma.real if np.iscomplex(sigma) else sigma,
            'angulos': angulos
        }

    def _criar_polinomio_sympy(self, coef_list: List) -> sp.Expr:
        """Cria um polinômio SymPy usando sp.Rational para precisão."""
        s = sp.Symbol('s')
        polinomio = 0
        grau = len(coef_list) - 1
        for i, c in enumerate(coef_list):
            # Converter para string e depois para Rational garante precisão
            polinomio += sp.Rational(str(c)) * s**(grau - i)
        return polinomio

    def calcular_pontos_entrada_saida(self) -> List[float]:
        """
        Parte 3: Cálculo dos pontos de entrada/saída
        
        Returns:
            Lista de pontos de entrada/saída válidos
        """
        s = sp.Symbol('s')
        
        # Criar polinômios simbólicos usando Rational
        num_poly = self._criar_polinomio_sympy(self.num_raw)
        den_poly = self._criar_polinomio_sympy(self.den_raw)
        
        # K = 1/G(s) -> K = den(s) / num(s)
        if num_poly == 0:
            return [] # Evita divisão por zero
        K_expr = den_poly / num_poly
        
        # Derivada dK/ds
        dK_ds = sp.diff(K_expr, s)
        
        # Resolver dK/ds = 0
        try:
            raizes_dK = sp.solve(dK_ds, s)
            raizes_dK_complex = [complex(r.evalf()) for r in raizes_dK if r.is_finite is not False]
        except Exception as e:
            print(f"Aviso: Erro ao resolver dK/ds simbolicamente: {e}")
            return []
        
        # Filtrar apenas pontos reais
        pontos_IO_filtrados = [r.real for r in raizes_dK_complex if abs(r.imag) < self.tol]
        
        # Obter raízes reais (polos e zeros)
        polos_reais = self.polos[np.abs(np.imag(self.polos)) < self.tol].real
        zeros_reais = self.zeros[np.abs(np.imag(self.zeros)) < self.tol].real if len(self.zeros) > 0 else np.array([])
        
        # Juntar e ordenar em ordem decrescente (para a regra da direita)
        raizes_reais = np.sort(np.concatenate([polos_reais, zeros_reais]))[::-1]
        
        pontos_IO_reais = []
        
        for ponto in pontos_IO_filtrados:
            # Contar raízes reais estritamente à direita do ponto
            num_direita = np.sum(raizes_reais > (ponto + self.tol))
            
            if num_direita % 2 == 1:
                pontos_IO_reais.append(ponto)
        
        return sorted(list(set(pontos_IO_reais)))

    def calcular_angulos_partida_chegada(self) -> Dict:
        """
        Parte 4: Cálculo dos ângulos de partida e chegada
        
        Returns:
            Dicionário com ângulos de partida dos polos e chegada dos zeros
        """
        angulos_partida = {}
        angulos_chegada = {}
        
        # Ângulos de partida dos polos complexos
        for k, pk in enumerate(self.polos):
            if abs(np.imag(pk)) > self.tol:
                angulo = 0
                for z in self.zeros:
                    angulo += np.angle(pk - z)
                for p_idx, p in enumerate(self.polos):
                    if p_idx != k:
                        angulo -= np.angle(pk - p)
                angulo += np.pi
                angulo = np.arctan2(np.sin(angulo), np.cos(angulo))
                angulos_partida[pk] = np.degrees(angulo)
        
        # Ângulos de chegada dos zeros complexos
        for k, zk in enumerate(self.zeros):
            if abs(np.imag(zk)) > self.tol:
                angulo = 0
                for p in self.polos:
                    angulo += np.angle(zk - p)
                for z_idx, z in enumerate(self.zeros):
                    if z_idx != k:
                        angulo -= np.angle(zk - z)
                angulo += np.pi
                angulo = np.arctan2(np.sin(angulo), np.cos(angulo))
                angulos_chegada[zk] = np.degrees(angulo)
        
        return {
            'partida': angulos_partida,
            'chegada': angulos_chegada
        }
    
    def calcular_cruzamento_eixo_imaginario(self) -> Optional[Dict]:
        """
        Parte 5: Cálculo do cruzamento com o eixo imaginário usando Routh-Hurwitz
        
        Returns:
            Dicionário com ganho K e pontos de cruzamento, ou None se não houver
        """
        try:
            s, k = sp.symbols('s k')
            
            # Polinômio característico: num*k + den
            num_poly = self._criar_polinomio_sympy(self.num_raw)
            den_poly = self._criar_polinomio_sympy(self.den_raw)
            
            char_poly = num_poly * k + den_poly
            
            # Obter coeficientes
            coefs = sp.Poly(char_poly, s).all_coeffs()
            
            # Construir tabela de Routh
            routh_table = self._construir_routh(coefs)
            
            if not routh_table or len(routh_table) < 3:
                return None
            
            # Penúltima linha, primeira coluna (s^1)
            ks_expr = routh_table[-2][0]
            
            # Resolver ks = 0
            sol_k = sp.solve(ks_expr, k)
            
            if not sol_k:
                return None
            
            # Filtrar soluções de K reais e positivas
            k_critico_val = None
            k_critico_sym = None
            for sol in sol_k:
                try:
                    k_val = complex(sol.evalf())
                    if abs(k_val.imag) < self.tol and k_val.real > self.tol:
                        k_critico_val = k_val.real
                        k_critico_sym = sol
                        break
                except TypeError:
                    continue # Ignorar soluções não numéricas
            
            if k_critico_val is None:
                return None
            
            # Substituir k na antepenúltima linha (s^2) para encontrar ω
            c1 = routh_table[-3][0].subs(k, k_critico_sym)
            c2 = routh_table[-3][1].subs(k, k_critico_sym) if len(routh_table[-3]) > 1 else 0
            
            # Resolver equação auxiliar (c1*s^2 + c2 = 0)
            aux_poly_coefs = [complex(c1.evalf()), 0, complex(c2.evalf())]
            
            # Garantir que o primeiro coeficiente não seja zero
            if abs(aux_poly_coefs[0]) < self.tol:
                return None
                
            raizes = np.roots(aux_poly_coefs)
            
            # Filtrar raízes imaginárias puras
            cruzamentos = []
            for r in raizes:
                if abs(r.real) < self.tol and abs(r.imag) > self.tol:
                    cruzamentos.append(r)
            
            if cruzamentos:
                return {
                    'k_critico': k_critico_val,
                    'k_critico_sym': k_critico_sym, # Salvar a versão simbólica (ex: 9/4)
                    'cruzamentos': cruzamentos,
                    'tabela_routh': routh_table
                }
            
            return None
            
        except Exception as e:
            print(f"Erro em Routh: {e}")
            return None
    
    def _construir_routh(self, coefs: List) -> List[List]:
        """
        Constrói a tabela de Routh-Hurwitz
        
        Args:
            coefs: Coeficientes do polinômio característico
            
        Returns:
            Tabela de Routh como lista de listas
        """
        try:
            n_coefs = len(coefs)
            n_rows = n_coefs
            n_cols = (n_coefs + 1) // 2
            
            # Inicializar tabela simbólica com zeros
            tabela_sp = sp.zeros(n_rows, n_cols)
            
            # Preencher primeira linha (s^n)
            for i, j in enumerate(range(0, n_coefs, 2)):
                tabela_sp[0, i] = coefs[j]
            
            # Preencher segunda linha (s^(n-1))
            for i, j in enumerate(range(1, n_coefs, 2)):
                tabela_sp[1, i] = coefs[j]
            
            # Construir linhas restantes
            for i in range(2, n_rows):
                # Caso especial: linha anterior inteira de zeros
                if all(sp.simplify(elem) == 0 for elem in tabela_sp[i-1, :]):
                    # Pegar coeficientes da linha s^i (i-2)
                    grau_aux = (n_coefs - 1) - (i-2)
                    aux_poly_coefs = [tabela_sp[i-2, j] * (grau_aux - 2*j) for j in range(n_cols)]
                    for j, coef in enumerate(aux_poly_coefs):
                        if j < n_cols:
                            tabela_sp[i-1, j] = coef
                    
                cabeça = sp.simplify(tabela_sp[i-1, 0])
                
                if cabeça == 0:
                    # Caso especial: zero na primeira coluna
                    return tabela_sp.tolist()[:i] # Parar aqui por simplicidade

                for j in range(n_cols - 1):
                    # Determinante
                    det = (tabela_sp[i-1, 0] * tabela_sp[i-2, j+1] - 
                           tabela_sp[i-2, 0] * tabela_sp[i-1, j+1])
                    
                    if det == 0:
                        tabela_sp[i, j] = 0
                    else:
                        tabela_sp[i, j] = sp.simplify(det / cabeça)
            
            return tabela_sp.tolist()
            
        except Exception as e:
            print(f"Erro ao construir Routh: {e}")
            return []
    
    # ==================================================================
    # ================== FUNÇÃO GERAR_RELATORIO ATUALIZADA =============
    # ==================================================================
    def _formatar_tabela_routh(self, tabela_sym: List[List]) -> List[str]:
        """Formata a tabela de Routh para exibição limpa e organizada."""
        if not tabela_sym:
            return ["    (Tabela não pôde ser gerada)"]

        # Adicionar labels s^n
        grau_max = len(tabela_sym) - 1
        labels_s = [f"s^{grau_max - i}" for i in range(len(tabela_sym))]
        label_s_width = max(len(s) for s in labels_s) + 2  # +2 for padding ' s^n '

        # Converter elementos para string e simplificar
        tabela_str = []
        for linha_sym in tabela_sym:
            linha_str_elem = []
            for elem in linha_sym:
                simpl_elem = sp.simplify(elem)
                # Formatar para melhor legibilidade
                if simpl_elem.is_Float:
                    elem_str = f"{float(simpl_elem):.4g}".rstrip('0').rstrip('.')
                else:
                    elem_str = str(simpl_elem)
                linha_str_elem.append(elem_str)
            tabela_str.append(linha_str_elem)
        
        # Calcular larguras das colunas de dados
        num_cols = max(len(r) for r in tabela_str) if tabela_str else 0
        if num_cols == 0: 
            return ["    (Tabela vazia)"]
        
        # Largura da coluna de dados (pelo menos 12, como na ref)
        data_col_width = 12 
        
        # Calcular larguras das colunas
        col_widths = [0] * num_cols
        # Adicionar cabeçalho para cálculo de largura
        header_cols = [f"s^{grau_max - 2*j}" if (grau_max - 2*j) >= 0 else "" for j in range(num_cols)]
        
        for linha in tabela_str:
            for i, elem in enumerate(linha):
                col_widths[i] = max(col_widths[i], len(elem))
        
        # Checar também o cabeçalho
        for i, elem in enumerate(header_cols):
             col_widths[i] = max(col_widths[i], len(elem))

        # Garantir largura mínima e adicionar padding
        col_widths = [max(data_col_width, w + 2) for w in col_widths]

        linhas_formatadas = []
        
        # --- Linha Superior (Box drawing) ---
        linha_sup = "    ┌" + "─" * label_s_width + "┬"
        linha_sup += "┬".join(["─" * w for w in col_widths]) + "┐"
        linhas_formatadas.append(linha_sup)

        # --- Linha de Cabeçalho das Colunas de Dados (s^n, s^n-2...) ---
        header_line = f"    │{'':^{label_s_width}}│"
        header_elems = []
        for j, elem in enumerate(header_cols):
            header_elems.append(f"{elem:^{col_widths[j]}}")
        header_line += "│".join(header_elems) + "│"
        linhas_formatadas.append(header_line)

        # --- Linha Separadora Abaixo do Cabeçalho ---
        linha_sep_header = "    ├" + "─" * label_s_width + "┼"
        linha_sep_header += "┼".join(["─" * w for w in col_widths]) + "┤"
        linhas_formatadas.append(linha_sep_header)

        # --- Linhas da Tabela ---
        for i, linha_dados_str in enumerate(tabela_str):
            # Label da linha (s^n) - Alinhado à direita como na ref
            linha_atual = f"    │{labels_s[i]:>{label_s_width-1}} │"
            
            # Dados
            elementos = []
            for j, elem_str in enumerate(linha_dados_str):
                # Centrado, como na ref
                elementos.append(f"{elem_str:^{col_widths[j]}}")
            # Preencher colunas restantes
            for j in range(len(linha_dados_str), num_cols):
                elementos.append(f"{'0':^{col_widths[j]}}")
            
            linha_atual += "│".join(elementos) + "│"
            linhas_formatadas.append(linha_atual)

            # Linha Separadora (apenas se não for a última)
            if i < len(tabela_str) - 1:
                linha_sep = "    ├" + "─" * label_s_width + "┼"
                linha_sep += "┼".join(["─" * w for w in col_widths]) + "┤"
                linhas_formatadas.append(linha_sep)

        # --- Linha Inferior ---
        linha_inf = "    └" + "─" * label_s_width + "┴"
        linha_inf += "┴".join(["─" * w for w in col_widths]) + "┘"
        linhas_formatadas.append(linha_inf)

        return linhas_formatadas

    def gerar_relatorio_completo(self) -> str:
        """
        Gera relatório completo da análise LGR, formatado de forma didática
        
        Returns:
            String formatada com todos os resultados
        """
        relatorio = []
        
        # === CABEÇALHO GERAL ===
        relatorio.append("==========================================================")
        relatorio.append("     ANÁLISE DETALHADA DO LUGAR GEOMÉTRICO DAS RAÍZES     ")
        relatorio.append("==========================================================")
        
        # === SISTEMA ANALISADO ===
        relatorio.append("\n📊 SISTEMA ANALISADO:")
        relatorio.append("-" * 40)
        relatorio.append(f"Numerador:    {self.num_raw}")
        relatorio.append(f"Denominador:  {self.den_raw}")
        relatorio.append(f"Função G(s):  {self._formatar_funcao_transferencia()}")
        
        # === PARTE 1: POLOS E ZEROS ===
        relatorio.append("\n\n🔍 1. POLOS E ZEROS DO SISTEMA (MALHA ABERTA):")
        relatorio.append("-" * 40)
        
        relatorio.append(f"Quantidade de Polos (n): {self.n}")
        if self.n > 0:
            relatorio.append("Polos do sistema:")
            for i, p in enumerate(self.polos):
                tipo = "REAL" if abs(p.imag) < self.tol else "COMPLEXO"
                relatorio.append(f"  Polo {i+1}: {p.real:8.4f} {p.imag:+.4f}j  [{tipo}]")
        
        relatorio.append(f"\nQuantidade de Zeros (m): {self.m}")
        if self.m > 0:
            relatorio.append("Zeros do sistema:")
            for i, z in enumerate(self.zeros):
                tipo = "REAL" if abs(z.imag) < self.tol else "COMPLEXO"
                relatorio.append(f"  Zero {i+1}: {z.real:8.4f} {z.imag:+.4f}j  [{tipo}]")
        
        # === PARTE 2: SEGMENTOS DO EIXO REAL ===
        relatorio.append("\n\n📈 2. SEGMENTOS NO EIXO REAL QUE PERTENCEM AO LGR:")
        relatorio.append("-" * 55)
        relatorio.append("[i] Regra: Segmentos com número ÍMPAR de polos/zeros à sua direita.")
        
        segmentos, faz_parte = self.analisar_segmentos()
        encontrou_segmentos = False
        
        for seg, pertence in zip(segmentos, faz_parte):
            inicio = "  +∞ " if np.isinf(seg[0]) else f"{seg[0]:>6.2f}"
            fim = "  -∞ " if np.isinf(seg[1]) else f"{seg[1]:>6.2f}"
            
            status = ""
            if abs(seg[0] - seg[1]) > self.tol: # Ignorar pontos (ex: -1.00 -> -1.00)
                status = "[FAZ PARTE]" if pertence else "[Não faz parte]"
            
            relatorio.append(f"    {inicio} → {fim}: {status}")
            if pertence:
                encontrou_segmentos = True
        
        if not encontrou_segmentos:
            relatorio.append("    ✗ Nenhum segmento do eixo real pertence ao LGR.")
        
        # === PARTE 3: ASSÍNTOTAS ===
        relatorio.append("\n\n📐 3. ASSÍNTOTAS (para K → ∞):")
        relatorio.append("-" * 35)
        relatorio.append("[i] Trajetória dos ramos que vão para o infinito.")
        
        assint = self.calcular_assintotas()
        relatorio.append(f"\n    Número de assíntotas: {assint['numero']} (n - m)")
        
        if assint['numero'] > 0:
            relatorio.append(f"    Centro (Sigma):       {assint['sigma']:.4f}")
            angulos_str = " ".join([f"{ang:.1f}°" for ang in assint['angulos']])
            relatorio.append(f"    Ângulos:              {angulos_str}")
        else:
             relatorio.append("\n    (Não há assíntotas, pois n ≤ m)")
        
        # === PARTE 4: PONTOS DE ENTRADA/SAÍDA ===
        relatorio.append("\n\n⚡ 4. PONTOS DE ENTRADA/SAÍDA NO EIXO REAL:")
        relatorio.append("-" * 45)
        relatorio.append("[i] Onde os ramos saem ou entram no eixo real (dK/ds = 0).")
        
        pontos_io = self.calcular_pontos_entrada_saida()
        if pontos_io:
            relatorio.append("\n    [✓] Pontos VÁLIDOS (que estão no LGR):")
            for i, ponto in enumerate(pontos_io):
                relatorio.append(f"       Ponto {i+1}: s = {ponto:8.4f}")
        else:
            relatorio.append("\n    ✗ Nenhum ponto de entrada/saída encontrado no LGR.")
        
        # === PARTE 5: ÂNGULOS DE PARTIDA/CHEGADA ===
        relatorio.append("\n\n🎯 5. ÂNGULOS DE PARTIDA E CHEGADA:")
        relatorio.append("-" * 40)
        relatorio.append("[i] Direção dos ramos ao sair de polos/chegar em zeros complexos.")
        
        angulos = self.calcular_angulos_partida_chegada()
        
        if angulos['partida']:
            relatorio.append("\n    Ângulos de Partida (dos Polos):")
            for polo, ang in angulos['partida'].items():
                relatorio.append(f"       • Polo ({polo.real:.2f} {polo.imag:+.2f}j): {ang:6.1f}°")
        else:
            relatorio.append("\n    Ângulos de Partida: ✗ Nenhum polo complexo.")
        
        if angulos['chegada']:
            relatorio.append("\n    Ângulos de Chegada (nos Zeros):")
            for zero, ang in angulos['chegada'].items():
                relatorio.append(f"       • Zero ({zero.real:.2f} {zero.imag:+.2f}j): {ang:6.1f}°")
        else:
            relatorio.append("\n    Ângulos de Chegada: ✗ Nenhum zero complexo.")
        
        # === PARTE 6: CRUZAMENTO COM EIXO IMAGINÁRIO ===
        relatorio.append("\n\n📊 6. CRUZAMENTO COM EIXO IMAGINÁRIO (Routh-Hurwitz):")
        relatorio.append("-" * 50)
        relatorio.append("[i] Análise de estabilidade marginal (onde K > 0).")
        
        cruzamento = self.calcular_cruzamento_eixo_imaginario()
        
        if cruzamento:
            relatorio.append("\n    📋 TABELA DE ROUTH-HURWITZ:")
            relatorio.extend(self._formatar_tabela_routh(cruzamento['tabela_routh'])) 

            k_critico_val = cruzamento['k_critico']
            k_critico_sym = cruzamento['k_critico_sym']
            
            # Formatar ganho crítico
            if hasattr(k_critico_sym, 'is_Rational') and k_critico_sym.is_Rational:
                relatorio.append(f"\n    [✓] GANHO CRÍTICO DE ESTABILIDADE:")
                relatorio.append(f"        K_crítico = {k_critico_sym} (aprox. {k_critico_val:.4f})")
            else:
                 relatorio.append(f"\n    [✓] GANHO CRÍTICO DE ESTABILIDADE:")
                 relatorio.append(f"        K_crítico = {k_critico_val:.4f}")
            
            relatorio.append("\n    [✓] PONTOS DE CRUZAMENTO (em ±jω):")
            pontos_unicos = {abs(p.imag) for p in cruzamento['cruzamentos']}
            for p_imag in sorted(pontos_unicos):
                relatorio.append(f"        s = ±j{p_imag:.4f}")
                
            relatorio.append(f"\n    💡 INTERPRETAÇÃO:")
            relatorio.append(f"       • Para 0 < K < {k_critico_val:.4f}: Sistema ESTÁVEL")
            relatorio.append(f"       • Para K = {k_critico_val:.4f}: Estabilidade MARGINAL")
            relatorio.append(f"       • Para K > {k_critico_val:.4f}: Sistema INSTÁVEL")
        else:
            relatorio.append("\n    ✅ O sistema NÃO CRUZA o eixo imaginário para K > 0.")
            relatorio.append("       (Pode ser estável ou instável para todo K,")
            relatorio.append("        verifique a 1ª coluna da tabela de Routh)")
        
        # === RESUMO FINAL ===
        relatorio.append("\n\n" + "=" * 70)
        relatorio.append("                         RESUMO DA ANÁLISE")
        relatorio.append("=" * 70)
        
        polos_estaveis = sum(1 for p in self.polos if p.real < -self.tol)
        polos_instaveis = sum(1 for p in self.polos if p.real > self.tol)
        polos_eixo = self.n - polos_estaveis - polos_instaveis
        
        relatorio.append(f"    • Polos em Malha Aberta:")
        relatorio.append(f"        - Estáveis (Re < 0):   {polos_estaveis}")
        relatorio.append(f"        - No Eixo jω (Re = 0): {polos_eixo}")
        relatorio.append(f"        - Instáveis (Re > 0):  {polos_instaveis}")
        relatorio.append(f"    • Zeros em Malha Aberta: {self.m}")
        relatorio.append(f"    • Ramos para o infinito: {assint['numero']}")
        
        if cruzamento:
            relatorio.append(f"    • Faixa de estabilidade (Malha Fechada): 0 < K < {cruzamento['k_critico']:.4f}")
        else:
            # Checar primeira coluna de Routh (sem 'k')
            estavel_sempre = True
            if cruzamento and cruzamento['tabela_routh']:
                for linha in cruzamento['tabela_routh']:
                    if not linha[0].has(sp.Symbol('k')):
                        if float(sp.simplify(linha[0]).evalf()) < 0:
                            estavel_sempre = False
                            break
            
            if estavel_sempre:
                relatorio.append("    • Faixa de estabilidade (Malha Fechada): 0 < K < ∞")
            else:
                relatorio.append("    • Faixa de estabilidade (Malha Fechada): INSTÁVEL para todo K > 0")
        
        relatorio.append("\n" + "=" * 70)
        
        return "\n".join(relatorio)
    
    def _formatar_funcao_transferencia(self) -> str:
        """Formata a função de transferência de forma legível"""
        if not self.num_raw or not self.den_raw:
            return "Não definida"
        
        num_str = self._coefs_para_polinomio(self.num_raw)
        den_str = self._coefs_para_polinomio(self.den_raw)
        
        # Adicionar parênteses se houver mais de um termo
        if " + " in num_str or " - " in num_str:
             num_str = f"({num_str})"
        if " + " in den_str or " - " in den_str:
            den_str = f"({den_str})"
            
        return f"{num_str} / {den_str}"
    
    def _coefs_para_polinomio(self, coefs: List[float]) -> str:
        """Converte coeficientes para string de polinômio"""
        termos = []
        grau = len(coefs) - 1
        
        for i, coef_val in enumerate(coefs):
            if abs(coef_val) < self.tol:
                continue
            
            coef = sp.Rational(str(coef_val))
            expoente = grau - i
            
            # Formatar coeficiente
            termo_str = ""
            if coef < 0:
                termo_str += " - "
            elif i > 0:
                termo_str += " + "
            
            coef_abs = abs(coef)
            
            if abs(coef_abs - 1) < self.tol and expoente > 0:
                 termo_str += ""
            else:
                termo_str += f"{coef_abs}"
                if expoente > 0:
                    termo_str += "·"

            # Formatar variável e expoente
            if expoente == 0:
                if abs(coef_abs - 1) < self.tol and i > 0:
                    termo_str += "1" # Garante que '1' apareça se for o único termo
                var_str = f"{termo_str}"
            elif expoente == 1:
                var_str = f"{termo_str}s"
            else:
                var_str = f"{termo_str}s^{expoente}"
            
            termos.append(var_str)
        
        if not termos:
            return "0"
        
        return "".join(termos).lstrip(" + ")
    
    # Métodos auxiliares para plotagem (mantidos da versão anterior)
    def obter_linhas_angulos_partida(self, comprimento: float = 1.0) -> Dict:
        """Calcula pontos para desenhar as linhas dos ângulos de partida"""
        linhas = {}
        angulos = self.calcular_angulos_partida_chegada()['partida']
        
        for polo, angulo in angulos.items():
            angulo_rad = np.deg2rad(angulo)
            x_inicio = polo.real
            y_inicio = polo.imag
            x_fim = x_inicio + comprimento * np.cos(angulo_rad)
            y_fim = y_inicio + comprimento * np.sin(angulo_rad)
            
            linhas[polo] = {
                'inicio': (x_inicio, y_inicio),
                'fim': (x_fim, y_fim),
                'angulo': angulo
            }
        
        return linhas
    
    def obter_linhas_angulos_chegada(self, comprimento: float = 1.0) -> Dict:
        """Calcula pontos para desenhar as linhas dos ângulos de chegada"""
        linhas = {}
        angulos = self.calcular_angulos_partida_chegada()['chegada']
        
        for zero, angulo in angulos.items():
            angulo_rad = np.deg2rad(angulo)
            x_inicio = zero.real
            y_inicio = zero.imag
            x_fim = x_inicio - comprimento * np.cos(angulo_rad)
            y_fim = y_inicio - comprimento * np.sin(angulo_rad)
            
            linhas[zero] = {
                'inicio': (x_fim, y_fim),
                'fim': (x_inicio, y_inicio),
                'angulo': angulo
            }
        
        return linhas
    
    def obter_segmentos_eixo_real(self) -> List[Dict]:
        """Retorna os segmentos do eixo real que fazem parte do LGR"""
        segmentos, faz_parte = self.analisar_segmentos()
        
        segmentos_eixo_real = []
        for seg, pertence in zip(segmentos, faz_parte):
            if pertence and not np.isinf(seg[0]) and not np.isinf(seg[1]):
                segmentos_eixo_real.append({
                    'inicio': seg[1],
                    'fim': seg[0],
                    'faz_parte': pertence
                })
        
        return segmentos_eixo_real
    
    def calcular_polos_dominantes(self, zeta_desejado: float, wn_desejado: Optional[float] = None) -> Dict:
        """
        Calcula os polos dominantes desejados baseado no coeficiente de amortecimento
        
        Args:
            zeta_desejado: Coeficiente de amortecimento desejado (0 < zeta < 1)
            wn_desejado: Frequência natural desejada (opcional)
            
        Returns:
            Dicionário com informações dos polos dominantes
        """
        if zeta_desejado <= 0 or zeta_desejado >= 1:
            raise ErroValidacaoLGR("Coeficiente de amortecimento deve estar entre 0 e 1")
        
        # Se wn não foi fornecido, usar um valor baseado nos polos existentes
        if wn_desejado is None:
            # Estimar wn baseado na magnitude média dos polos
            magnitudes = np.abs(self.polos)
            wn_desejado = np.mean(magnitudes) if len(magnitudes) > 0 else 2.0
        
        # Calcular polos dominantes
        sigma = -zeta_desejado * wn_desejado
        wd = wn_desejado * np.sqrt(1 - zeta_desejado**2)
        
        polo_dominante_1 = sigma + 1j * wd
        polo_dominante_2 = sigma - 1j * wd
        
        # Calcular linha de amortecimento constante
        theta = np.arccos(zeta_desejado)
        
        return {
            'polo_1': polo_dominante_1,
            'polo_2': polo_dominante_2,
            'sigma': sigma,
            'wd': wd,
            'wn': wn_desejado,
            'zeta': zeta_desejado,
            'theta': np.degrees(theta)
        }
    
    def obter_linha_amortecimento(self, zeta: float, comprimento: float = 10.0) -> Dict:
        """
        Calcula pontos para desenhar a linha de amortecimento constante
        
        Args:
            zeta: Coeficiente de amortecimento
            comprimento: Comprimento da linha
            
        Returns:
            Dicionário com pontos da linha
        """
        theta = np.arccos(zeta)
        
        # Linhas partindo da origem
        x = np.array([0, -comprimento * np.cos(theta)])
        y_pos = np.array([0, comprimento * np.sin(theta)])
        y_neg = np.array([0, -comprimento * np.sin(theta)])
        
        return {
            'x': x,
            'y_positivo': y_pos,
            'y_negativo': y_neg,
            'theta_graus': np.degrees(theta),
            'zeta': zeta
        }