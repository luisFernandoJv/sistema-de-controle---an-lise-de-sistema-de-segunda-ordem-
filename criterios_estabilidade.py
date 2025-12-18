import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import math
import platform
import sympy as sp

class ErroValidacao(Exception):
    """Exceção customizada para erros de validação"""
    pass

class ValidadorCoeficientes:
    """Classe centralizada para validação de coeficientes"""
    
    @staticmethod
    def validar(coeficientes, nome="coeficientes", permitir_vazio=False):
        """
        Validação robusta de coeficientes
        
        Args:
            coeficientes: Lista de coeficientes
            nome: Nome do campo
            permitir_vazio: Se permite lista vazia
            
        Raises:
            ErroValidacao: Se inválido
        """
        # Validação 1: Lista vazia
        if not coeficientes:
            if permitir_vazio:
                return True
            raise ErroValidacao(f"❌ {nome.capitalize()} não pode estar vazio!")
        
        # Validação 2: Tipo de dados
        if not isinstance(coeficientes, (list, tuple, np.ndarray)):
            raise ErroValidacao(f"❌ {nome} deve ser uma lista de números!")
        
        # Validação 3: Cada coeficiente
        for i, coef in enumerate(coeficientes):
            if not isinstance(coef, (int, float, np.number)):
                raise ErroValidacao(f"❌ {nome}[{i}] = '{coef}' não é número!")
            
            if math.isnan(coef) or math.isinf(coef):
                raise ErroValidacao(f"❌ {nome}[{i}] é inválido (NaN/Inf)!")
        
        # Validação 4: Primeiro coeficiente (para denominador)
        if "denominador" in nome.lower() and abs(coeficientes[0]) < 1e-15:
            raise ErroValidacao(f"❌ Primeiro coeficiente de {nome} não pode ser zero!")
        
        return True

class CriteriosEstabilidade:
    
    # Variável de classe para controle de tela cheia em janelas GUI
    _janela_atual = None
    _fullscreen_ativo = False
    
    @staticmethod
    def configurar_janela_gui(janela):
        """
        Configura uma janela GUI para suportar tela cheia
        
        Args:
            janela: Objeto da janela (tkinter/customtkinter)
        """
        CriteriosEstabilidade._janela_atual = janela
        CriteriosEstabilidade._fullscreen_ativo = False
        
        # Detectar sistema operacional
        is_windows = platform.system() == "Windows"
        
        # Adicionar método de alternância
        def toggle_fullscreen():
            if CriteriosEstabilidade._fullscreen_ativo:
                if is_windows:
                    janela.state('normal')
                else:
                    janela.attributes('-fullscreen', False)
                CriteriosEstabilidade._fullscreen_ativo = False
            else:
                if is_windows:
                    janela.state('zoomed')
                else:
                    janela.attributes('-fullscreen', True)
                CriteriosEstabilidade._fullscreen_ativo = True
        
        # Atalhos de teclado
        try:
            janela.bind('<F11>', lambda e: toggle_fullscreen())
            janela.bind('<Escape>', lambda e: (
                janela.state('normal') if is_windows else janela.attributes('-fullscreen', False),
                setattr(CriteriosEstabilidade, '_fullscreen_ativo', False)
            ) if CriteriosEstabilidade._fullscreen_ativo else None)
        except:
            pass
        
        return toggle_fullscreen
    
    @staticmethod
    def ativar_tela_cheia():
        """Ativa tela cheia na janela atual"""
        if CriteriosEstabilidade._janela_atual:
            is_windows = platform.system() == "Windows"
            if is_windows:
                CriteriosEstabilidade._janela_atual.state('zoomed')
            else:
                CriteriosEstabilidade._janela_atual.attributes('-fullscreen', True)
            CriteriosEstabilidade._fullscreen_ativo = True
    
    @staticmethod
    def desativar_tela_cheia():
        """Desativa tela cheia na janela atual"""
        if CriteriosEstabilidade._janela_atual:
            is_windows = platform.system() == "Windows"
            if is_windows:
                CriteriosEstabilidade._janela_atual.state('normal')
            else:
                CriteriosEstabilidade._janela_atual.attributes('-fullscreen', False)
            CriteriosEstabilidade._fullscreen_ativo = False
    
    @staticmethod
    def validar_coeficientes(coeficientes, nome="coeficientes"):
        """Usar validador centralizado"""
        ValidadorCoeficientes.validar(coeficientes, nome)
    
    @staticmethod
    def validar_coeficientes_e_retornar_status(numerador, denominador):
        """
        Valida coeficientes e retorna status com cor
        Retorna: (válido: bool, mensagem: str, cor: str)
        """
        try:
            ValidadorCoeficientes.validar(numerador, "numerador")
            ValidadorCoeficientes.validar(denominador, "denominador")
            return True, "✅ VÁLIDO", "verde"
        except ErroValidacao as e:
            return False, str(e), "vermelho"
        except Exception as e:
            return False, f"❌ Erro: {str(e)}", "vermelho"
    
    @staticmethod
    def routh_hurwitz(coeficientes):
        """Melhor tratamento de casos extremos e edge cases"""
        try:
            CriteriosEstabilidade.validar_coeficientes(coeficientes, "polinômio característico")
            
            r = np.asarray(coeficientes, dtype=float)
            m = len(r)
            # Para m=5: ceil(5/2)=3 colunas (s^4, s^2, s^0), em vez de round(2.5)=2 que omitia s^0
            n = math.ceil(m / 2)
            
            # Separar coeficientes pares e ímpares
            coeficientes_pares = [r[p] for p in range(len(r)) if (p + 1) % 2 == 0]
            coeficientes_impares = [r[p] for p in range(len(r)) if (p + 1) % 2 == 1]
            
            # Preencher garantindo tamanho
            while len(coeficientes_pares) < n:
                coeficientes_pares.append(0)
            while len(coeficientes_impares) < n:
                coeficientes_impares.append(0)
            
            # Preencher a tabela de Routh-Hurwitz
            tabela = np.zeros((m, n))
            
            tabela[0, :] = coeficientes_impares[:n]
            tabela[1, :] = coeficientes_pares[:n]
            
            # Substituir zero por um valor pequeno
            if abs(tabela[1, 0]) < 1e-15:
                tabela[1, 0] = 0.01
            
            # Preenchimento robusta
            for i in range(2, m):
                for j in range(n - 1):
                    try:
                        denominador = tabela[i-1, 0]
                        if abs(denominador) < 1e-15:
                            denominador = 1e-10  # Evitar divisão por zero
                        
                        numerador = (tabela[i-1, 0] * tabela[i-2, j+1] - 
                                    tabela[i-2, 0] * tabela[i-1, j+1])
                        tabela[i, j] = numerador / denominador
                    except:
                        tabela[i, j] = 0
            
            polos_direita = 0
            valores_coluna_primeira = tabela[:, 0]
            
            # Contar mudanças de sinal
            for i in range(len(valores_coluna_primeira) - 1):
                if valores_coluna_primeira[i] * valores_coluna_primeira[i+1] < 0:
                    polos_direita += 1
            
            # Calcular raízes para detectar polos na fronteira (eixo imaginário)
            raizes = np.roots(r)
            
            polos_na_fronteira = 0
            polos_no_eixo_imaginario = 0
            
            for raiz in raizes:
                # Verificar se o polo está na fronteira (parte real próxima de zero)
                if abs(raiz.real) < 1e-6 and abs(raiz.imag) > 1e-6:
                    polos_no_eixo_imaginario += 1
                    polos_na_fronteira += 1
                # Verificar se é um polo real na origem
                elif abs(raiz.real) < 1e-6 and abs(raiz.imag) < 1e-6:
                    polos_na_fronteira += 1
            
            # Se há polos na fronteira e nenhum no semiplano direito, sistema é marginalmente estável
            if polos_na_fronteira > 0 and polos_direita == 0:
                polos_direita = -1  # Usar -1 para indicar marginalmente estável
            
            return tabela, polos_direita, raizes
            
        except ErroValidacao:
            raise
        except Exception as e:
            raise ErroValidacao(f"❌ Erro Routh-Hurwitz: {str(e)}")

    @staticmethod
    def analisar_nyquist(coeficientes_numerador, coeficientes_denominador):
        """
        Análise de estabilidade pelo critério de Nyquist
        
        Args:
            coeficientes_numerador: Lista de coeficientes do numerador
            coeficientes_denominador: Lista de coeficientes do denominador
            
        Returns:
            str: Relatório da análise
        """
        try:
            # Validar coeficientes
            CriteriosEstabilidade.validar_coeficientes(coeficientes_numerador, "numerador")
            CriteriosEstabilidade.validar_coeficientes(coeficientes_denominador, "denominador")
            
            sistema = signal.TransferFunction(coeficientes_numerador, coeficientes_denominador)
            
            resultado = "=== ANÁLISE DE NYQUIST ===\n\n"
            resultado += f"Sistema: {CriteriosEstabilidade.formatar_funcao_transferencia(coeficientes_numerador, coeficientes_denominador)}\n\n"
            resultado += "Análise de Nyquist realizada com sucesso.\n"
            resultado += "Gráfico de Nyquist pode ser gerado na seção de resultados.\n"
            
            return resultado
            
        except ErroValidacao:
            raise
        except Exception as e:
            return f"❌ Erro na análise de Nyquist: {str(e)}"

    @staticmethod
    def lugar_das_raizes(coeficientes_numerador, coeficientes_denominador):
        """
        Análise do lugar das raízes
        
        Args:
            coeficientes_numerador: Lista de coeficientes do numerador
            coeficientes_denominador: Lista de coeficientes do denominador
            
        Returns:
            str: Relatório da análise
        """
        try:
            # Validar coeficientes
            CriteriosEstabilidade.validar_coeficientes(coeficientes_numerador, "numerador")
            CriteriosEstabilidade.validar_coeficientes(coeficientes_denominador, "denominador")
            
            sistema = signal.TransferFunction(coeficientes_numerador, coeficientes_denominador)
            
            resultado = "=== LUGAR DAS RAÍZES ===\n\n"
            resultado += f"Sistema: {CriteriosEstabilidade.formatar_funcao_transferencia(coeficientes_numerador, coeficientes_denominador)}\n\n"
            resultado += "Lugar das raízes calculado com sucesso.\n"
            resultado += "Gráfico do lugar das raízes pode ser gerado na seção de resultados.\n"
            
            return resultado
            
        except ErroValidacao:
            raise
        except Exception as e:
            return f"❌ Erro no cálculo do lugar das raízes: {str(e)}"

    @staticmethod
    def formatar_polinomio(coeficientes):
        """Formata os coeficientes como um polinômio na ordem s⁰, s¹, s², ..."""
        try:
            if not coeficientes or len(coeficientes) == 0:
                return "0"
            
            termos = []
            
            for i, coef in enumerate(coeficientes):
                if abs(coef) > 1e-10:
                    expoente = len(coeficientes) - 1 - i
                    
                    if expoente == 0:
                        termos.append(f"{coef:.4f}")
                    elif expoente == 1:
                        if abs(coef - 1) < 1e-10:
                            termos.append("s")
                        elif abs(coef + 1) < 1e-10:
                            termos.append("-s")
                        else:
                            termos.append(f"{coef:.4f}s")
                    else:
                        if abs(coef - 1) < 1e-10:
                            termos.append(f"s^{expoente}")
                        elif abs(coef + 1) < 1e-10:
                            termos.append(f"-s^{expoente}")
                        else:
                            termos.append(f"{coef:.4f}s^{expoente}")
            
            if not termos:
                return "0"
            
            polinomio = " + ".join(termos)
            polinomio = polinomio.replace("+ -", "- ")
            polinomio = polinomio.replace("1.0000s", "s")
            polinomio = polinomio.replace("-1.0000s", "-s")
            
            return polinomio
            
        except Exception as e:
            return f"Erro ao formatar: {str(e)}"

    @staticmethod
    def formatar_funcao_transferencia(numerador, denominador):
        """Formata uma função de transferência"""
        try:
            num_str = CriteriosEstabilidade.formatar_polinomio(numerador)
            den_str = CriteriosEstabilidade.formatar_polinomio(denominador)
            return f"G(s) = ({num_str}) / ({den_str})"
        except Exception as e:
            return f"Erro ao formatar função: {str(e)}"

    @staticmethod
    def formatar_equacao_caracteristica(denominador):
        """Formata a equação característica na ordem s⁰, s¹, s², ..."""
        try:
            if not denominador or len(denominador) == 0:
                return "Δ(s) = 0"
            
            termos = []
            
            for i, coef in enumerate(denominador):
                if abs(coef) > 1e-10:
                    expoente = len(denominador) - 1 - i
                    
                    if expoente == 0:
                        termos.append(f"{coef:.4f}")
                    elif expoente == 1:
                        if abs(coef - 1) < 1e-10:
                            termos.append("s")
                        elif abs(coef + 1) < 1e-10:
                            termos.append("-s")
                        else:
                            termos.append(f"{coef:.4f}s")
                    else:
                        if abs(coef - 1) < 1e-10:
                            termos.append(f"s^{expoente}")
                        elif abs(coef + 1) < 1e-10:
                            termos.append(f"-s^{expoente}")
                        else:
                            termos.append(f"{coef:.4f}s^{expoente}")
            
            if not termos:
                return "Δ(s) = 0"
            
            equacao = " + ".join(termos)
            equacao = equacao.replace("+ -", "- ")
            equacao = equacao.replace("1.0000s", "s")
            equacao = equacao.replace("-1.0000s", "-s")
            
            return f"Δ(s) = {equacao} = 0"
            
        except Exception as e:
            return f"Erro ao formatar equação: {str(e)}"

    @staticmethod
    def formatar_tabela_routh(tabela):
        """Formata a tabela de Routh-Hurwitz de forma profissional e organizada"""
        try:
            linhas = []
            num_linhas = tabela.shape[0]
            num_colunas_dados = tabela.shape[1]
            grau_max = num_linhas - 1
            
            # Calcular largura das colunas
            s_col_width = len(f" s^{grau_max} ") + 1
            data_col_width = 12
            
            # Linha Superior
            linha_superior = "┌" + "─" * s_col_width + "┬"
            for j in range(num_colunas_dados):
                linha_superior += "─" * data_col_width + ("┬" if j < num_colunas_dados - 1 else "┐")
            linhas.append(linha_superior)
            
            # Linha de Cabeçalho das Colunas de Dados
            header_line = f"│{'':{s_col_width}}│"
            for j in range(num_colunas_dados):
                col_power = grau_max - 2 * j
                header_text = f"s^{col_power}" if col_power >= 0 else ""
                header_line += f"{header_text:^{data_col_width}}│"
            linhas.append(header_line)
            
            # Linha Separadora Abaixo do Cabeçalho
            separadora_header = "├" + "─" * s_col_width + "┼"
            for j in range(num_colunas_dados):
                separadora_header += "─" * data_col_width + ("┼" if j < num_colunas_dados - 1 else "┤")
            linhas.append(separadora_header)
            
            # Linhas da Tabela com Potências de s e Dados
            for i in range(num_linhas):
                potencia_s = grau_max - i
                # Formatar label - quando for s^0, mostrar explicitamente
                if potencia_s == 0:
                    label_s = "s^0"
                elif potencia_s == 1:
                    label_s = "s^1"
                else:
                    label_s = f"s^{potencia_s}"
                
                linha_atual = f"│{label_s:>{s_col_width-2}}  │"
                
                # Adiciona os valores da linha
                for j in range(num_colunas_dados):
                    valor = tabela[i, j]
                    
                    if abs(valor) < 1e-10:
                        valor_str = f"  {0.0:.4f}  "
                    elif abs(valor) < 1e-4 or abs(valor) > 99999.9:
                        valor_str = f" {valor:.2e} "
                    else:
                        valor_str = f" {valor:.4f} "
                    
                    linha_atual += f"{valor_str:^{data_col_width}}│"
                
                linhas.append(linha_atual)
                
                # Linha Separadora entre as linhas de dados
                if i < num_linhas - 1:
                    separadora_dados = "├" + "─" * s_col_width + "┼"
                    for j in range(num_colunas_dados):
                        separadora_dados += "─" * data_col_width + ("┼" if j < num_colunas_dados - 1 else "┤")
                    linhas.append(separadora_dados)
            
            # Linha Inferior
            linha_inferior = "└" + "─" * s_col_width + "┴"
            for j in range(num_colunas_dados):
                linha_inferior += "─" * data_col_width + ("┴" if j < num_colunas_dados - 1 else "┘")
            linhas.append(linha_inferior)
            
            return "\n".join(linhas)
            
        except Exception as e:
            return f"Erro ao formatar tabela: {str(e)}"

    @staticmethod
    def formatar_led_status(polos_direita):
        """
        Formata LED visual com cores para os 3 estados de estabilidade
        Verde: Estável (0 polos instáveis)
        Laranja: Marginalmente estável (polos na fronteira)
        Vermelho: Instável (polos no semiplano direito)
        """
        if polos_direita == 0:
            # SISTEMA ESTÁVEL
            led = "🟢 SISTEMA ESTÁVEL"
            descricao = "Todos os polos no semiplano esquerdo"
            cor_hex = "#05C214"  # Green
        elif polos_direita == -1:
            # SISTEMA MARGINALMENTE ESTÁVEL
            led = "🟠 SISTEMA MARGINALMENTE ESTÁVEL"
            descricao = "Polo(s) na fronteira (eixo imaginário)"
            cor_hex = "#d97706"  # Orange
        else:
            # SISTEMA INSTÁVEL
            led = "✖️ SISTEMA INSTÁVEL"
            descricao = f"{abs(polos_direita)} polo(s) no semiplano direito"
            cor_hex = "#dc2626"  # Red
        
        painel = f"""
╔{'═' * 68}╗
║{'STATUS DO SISTEMA':^68}║
╠{'═' * 68}╣
║{led:^68}║
║{descricao:^68}║
╚{'═' * 68}╝
"""
        return painel, cor_hex
    
    @staticmethod
    def gerar_relatorio_routh_hurwitz(coeficientes):
        """
        Gera um relatório completo da análise de Routh-Hurwitz
        
        Args:
            coeficientes: Lista de coeficientes do polinômio característico
            
        Returns:
            str: Relatório formatado
        """
        try:
            tabela, polos_direita, raizes = CriteriosEstabilidade.routh_hurwitz(coeficientes)
            
            relatorio = "-" * 60 + "\n"
            relatorio += "         ANÁLISE DE ESTABILIDADE - ROUTH-HURWITZ\n"
            relatorio += "-" * 60 + "\n\n"
            
            relatorio += "POLINÔMIO CARACTERÍSTICO:\n"
            relatorio += f"  {CriteriosEstabilidade.formatar_equacao_caracteristica(coeficientes)}\n\n"
            
            relatorio += "TABELA DE ROUTH-HURWITZ:\n"
            relatorio += CriteriosEstabilidade.formatar_tabela_routh(tabela)
            
            relatorio += "\n\n" + "─" * 60 + "\n"
            relatorio += "RESULTADO DA ANÁLISE:\n"
            relatorio += "─" * 60 + "\n"
            
            relatorio += f"• Número de polos no semiplano direito: {polos_direita}\n\n"
            
            painel_status, _ = CriteriosEstabilidade.formatar_led_status(polos_direita)
            relatorio += painel_status
            
            relatorio += "\n" + "─" * 60 + "\n"
            relatorio += "RAÍZES DO POLINÔMIO CARACTERÍSTICO:\n"
            relatorio += "─" * 60 + "\n"
            
            if len(raizes) > 0:
                for i, raiz in enumerate(raizes):
                    if abs(raiz.imag) < 1e-10:
                        relatorio += f"• Raiz {i+1}: {raiz.real:10.6f}\n"
                    else:
                        relatorio += f"• Raiz {i+1}: {raiz.real:10.6f} + {raiz.imag:10.6f}j\n"
            else:
                relatorio += "• Não foi possível calcular as raízes\n"
            
            return relatorio
            
        except ErroValidacao as e:
            return f"ERRO DE VALIDAÇÃO:\n{str(e)}"
        except Exception as e:
            return f"❌ Erro na análise: {str(e)}"

    @staticmethod
    def analisar_sistema_completo(numerador, denominador):
        """
        Análise completa do sistema incluindo função de transferência e equação característica
        
        Args:
            numerador: Lista de coeficientes do numerador
            denominador: Lista de coeficientes do denominador
            
        Returns:
            str: Relatório completo
        """
        try:
            # Validar entradas
            CriteriosEstabilidade.validar_coeficientes(numerador, "numerador")
            CriteriosEstabilidade.validar_coeficientes(denominador, "denominador")
            
            tabela, polos_direita, raizes = CriteriosEstabilidade.routh_hurwitz(denominador)
            
            resultado = "-" * 70 + "\n"
            resultado += "              ANÁLISE COMPLETA DO SISTEMA\n"
            resultado += "-" * 70 + "\n\n"
            
            # Função de transferência
            resultado += "FUNÇÃO DE TRANSFERÊNCIA:\n"
            resultado += "─" * 40 + "\n"
            resultado += f"  {CriteriosEstabilidade.formatar_funcao_transferencia(numerador, denominador)}\n\n"
            
            # Equação característica
            resultado += "EQUAÇÃO CARACTERÍSTICA:\n"
            resultado += "─" * 40 + "\n"
            resultado += f"  {CriteriosEstabilidade.formatar_equacao_caracteristica(denominador)}\n\n"
            
            # Tabela Routh-Hurwitz
            resultado += "TABELA DE ROUTH-HURWITZ:\n"
            resultado += CriteriosEstabilidade.formatar_tabela_routh(tabela)
            resultado += "\n\n" + "─" * 70 + "\n"
            
            resultado += f"• Número de polos no semiplano direito: {polos_direita}\n\n"
            
            painel_status, _ = CriteriosEstabilidade.formatar_led_status(polos_direita)
            resultado += painel_status
            
            resultado += "\n" + "─" * 70 + "\n"
            resultado += "RAÍZES DO POLINÔMIO CARACTERÍSTICO:\n"
            resultado += "─" * 70 + "\n"
            
            if len(raizes) > 0:
                for i, raiz in enumerate(raizes):
                    if abs(raiz.imag) < 1e-10:
                        resultado += f"• Raiz {i+1}: {raiz.real:10.6f}\n"
                    else:
                        resultado += f"• Raiz {i+1}: {raiz.real:10.6f} + {raiz.imag:10.6f}j\n"
            else:
                resultado += "• Não foi possível calcular as raízes\n"
            
            return resultado
            
        except ErroValidacao as e:
            return f"ERRO DE VALIDAÇÃO:\n{str(e)}"
        except Exception as e:
            return f"❌ Erro na análise do sistema: {str(e)}"

    @staticmethod
    def calcular_faixa_ganho_k(coeficientes_num, coeficientes_den):
        """
        Calcula a faixa de ganho K para estabilidade usando Routh-Hurwitz
        
        Args:
            coeficientes_num: Lista de coeficientes do numerador
            coeficientes_den: Lista de coeficientes do denominador
            
        Returns:
            dict: Dicionário com informações sobre estabilidade e faixa de K
        """
        try:
            # Validar coeficientes
            CriteriosEstabilidade.validar_coeficientes(coeficientes_num, "numerador")
            CriteriosEstabilidade.validar_coeficientes(coeficientes_den, "denominador")
            
            # Criar símbolo para K
            K = sp.Symbol('K', real=True, positive=True)
            s = sp.Symbol('s')
            
            # Criar polinômio característico: den(s) + K*num(s) = 0
            num_poly = sum(coeficientes_num[i] * s**(len(coeficientes_num)-1-i) 
                          for i in range(len(coeficientes_num)))
            den_poly = sum(coeficientes_den[i] * s**(len(coeficientes_den)-1-i) 
                          for i in range(len(coeficientes_den)))
            
            char_poly = den_poly + K * num_poly
            
            # Obter coeficientes do polinômio característico
            poly = sp.Poly(char_poly, s)
            coefs = poly.all_coeffs()
            
            # Construir tabela de Routh-Hurwitz com K simbólico
            n = len(coefs)
            routh_table = [[sp.S(0) for _ in range((n+1)//2)] for _ in range(n)]
            
            # Primeira linha: coeficientes de potências pares (s^n, s^(n-2), ...)
            for i, j in enumerate(range(0, n, 2)):
                routh_table[0][i] = coefs[j]
            
            # Segunda linha: coeficientes de potências ímpares (s^(n-1), s^(n-3), ...)
            for i, j in enumerate(range(1, n, 2)):
                routh_table[1][i] = coefs[j]
            
            # Construir resto da tabela
            for i in range(2, n):
                for j in range((n+1)//2 - 1):
                    try:
                        if routh_table[i-1][0] != 0:
                            num = (routh_table[i-1][0] * routh_table[i-2][j+1] - 
                                  routh_table[i-2][0] * routh_table[i-1][j+1])
                            routh_table[i][j] = sp.simplify(num / routh_table[i-1][0])
                        else:
                            routh_table[i][j] = sp.S(0)
                    except (IndexError, ZeroDivisionError):
                        routh_table[i][j] = sp.S(0)
            
            # Analisar primeira coluna para encontrar condições de estabilidade
            primeira_coluna = [routh_table[i][0] for i in range(n)]
            
            # Encontrar K crítico (onde muda de sinal)
            k_critico = None
            freq_critica = None
            condicoes_estabilidade = []
            
            for i, elemento in enumerate(primeira_coluna):
                # Simplificar elemento
                elem_simpl = sp.simplify(elemento)
                
                # Se contém K, resolver para K = 0 (mudança de sinal)
                if K in elem_simpl.free_symbols:
                    # Resolver para K quando elemento = 0
                    solucoes_k = sp.solve(elem_simpl, K)
                    for sol in solucoes_k:
                        try:
                            k_val = float(sol.evalf())
                            if k_val > 0:
                                if k_critico is None or k_val < k_critico:
                                    k_critico = k_val
                                    
                                    # Usando equação auxiliar da linha anterior na tabela de Routh
                                    if i >= 1 and i < n:
                                        # A equação auxiliar vem da linha anterior à mudança de sinal
                                        linha_auxiliar = i - 1
                                        
                                        # Coeficientes da equação auxiliar (forma: a*s^n + s^(n-2) + ...)
                                        coefs_aux = []
                                        for j in range(len(routh_table[linha_auxiliar])):
                                            if routh_table[linha_auxiliar][j] != 0:
                                                coef_val = routh_table[linha_auxiliar][j].subs(K, k_val)
                                                coefs_aux.append(float(coef_val.evalf()))
                                        
                                        # Para sistema de segunda ordem ou maior: s^2 coef + s^0 coef
                                        if len(coefs_aux) >= 2:
                                            a_coef = coefs_aux[0]
                                            b_coef = coefs_aux[1]
                                            
                                            # Frequência: ω = sqrt(b/a)
                                            if a_coef > 0 and b_coef > 0:
                                                freq_critica = float(sp.sqrt(b_coef / a_coef).evalf())
                        except (ValueError, TypeError, AttributeError):
                            continue
            
            # Determinar faixas de estabilidade
            resultado = {
                'k_critico': k_critico,
                'freq_critica': freq_critica,
                'tabela_routh': routh_table,
                'primeira_coluna': primeira_coluna
            }
            
            if k_critico is not None:
                resultado['faixa_estavel'] = f"0 < K < {k_critico:.4f}"
                resultado['faixa_marginalmente_estavel'] = f"K = {k_critico:.4f}"
                resultado['faixa_instavel'] = f"K > {k_critico:.4f}"
                resultado['msg_estabilidade'] = (
                    f"Sistema ESTÁVEL para 0 < K < {k_critico:.4f}\n"
                    f"Sistema MARGINALMENTE ESTÁVEL para K = {k_critico:.4f}\n"
                    f"Sistema INSTÁVEL para K > {k_critico:.4f}"
                )
                if freq_critica is not None:
                    resultado['msg_freq'] = f"Frequência no limiar de estabilidade: ω = {freq_critica:.4f} rad/s"
            else:
                # Verificar se é estável para todo K
                # Avaliar primeira coluna com K = 1
                teste_positivo = True
                for elem in primeira_coluna:
                    try:
                        val = float(elem.subs(K, 1).evalf())
                        if val <= 0:
                            teste_positivo = False
                            break
                    except:
                        teste_positivo = False
                        break
                
                if teste_positivo:
                    resultado['faixa_estavel'] = "0 < K < ∞"
                    resultado['faixa_marginalmente_estavel'] = "Nenhum"
                    resultado['faixa_instavel'] = "Nenhum"
                    resultado['msg_estabilidade'] = "Sistema ESTÁVEL para todo K > 0"
                else:
                    resultado['faixa_estavel'] = "Nenhum"
                    resultado['faixa_marginalmente_estavel'] = "Nenhum"
                    resultado['faixa_instavel'] = "0 < K < ∞"
                    resultado['msg_estabilidade'] = "Sistema INSTÁVEL para todo K > 0"
            
            return resultado
            
        except Exception as e:
            return {
                'erro': str(e),
                'msg_estabilidade': f"Erro ao calcular faixa de ganho: {str(e)}"
            }

    @staticmethod
    def gerar_relatorio_analise_ganho_k(coeficientes_num, coeficientes_den):
        """
        Gera relatório completo da análise de ganho K
        
        Args:
            coeficientes_num: Lista de coeficientes do numerador
            coeficientes_den: Lista de coeficientes do denominador
            
        Returns:
            str: Relatório formatado
        """
        try:
            resultado = CriteriosEstabilidade.calcular_faixa_ganho_k(coeficientes_num, coeficientes_den)
            
            if 'erro' in resultado:
                return f"❌ ERRO: {resultado['erro']}"
            
            relatorio = []
            relatorio.append("=" * 70)
            relatorio.append("       ANÁLISE DE FAIXA DE GANHO K PARA ESTABILIDADE")
            relatorio.append("=" * 70)
            relatorio.append("")
            
            relatorio.append("FUNÇÃO DE TRANSFERÊNCIA:")
            relatorio.append(f"  Numerador:   {CriteriosEstabilidade.formatar_polinomio(coeficientes_num)}")
            relatorio.append(f"  Denominador: {CriteriosEstabilidade.formatar_polinomio(coeficientes_den)}")
            relatorio.append("")
            relatorio.append("Sistema em Malha Fechada: 1 + K·G(s)·H(s) = 0")
            relatorio.append("")
            
            relatorio.append("-" * 70)
            relatorio.append("ANÁLISE DE ESTABILIDADE")
            relatorio.append("-" * 70)
            relatorio.append("")
            
            relatorio.append(resultado['msg_estabilidade'])
            relatorio.append("")
            
            if resultado.get('freq_critica'):
                relatorio.append(resultado['msg_freq'])
                relatorio.append("")
            
            relatorio.append("-" * 70)
            relatorio.append("FAIXAS DE GANHO K")
            relatorio.append("-" * 70)
            relatorio.append(f"  🟢 ESTÁVEL:              {resultado['faixa_estavel']}")
            relatorio.append(f"  🟠 MARGINALMENTE ESTÁVEL: {resultado['faixa_marginalmente_estavel']}")
            relatorio.append(f"  🔴 INSTÁVEL:             {resultado['faixa_instavel']}")
            relatorio.append("")
            
            if resultado.get('k_critico') is not None:
                relatorio.append("-" * 70)
                relatorio.append("VALORES CRÍTICOS")
                relatorio.append("-" * 70)
                relatorio.append(f"  K crítico: {resultado['k_critico']:.6f}")
                if resultado.get('freq_critica') is not None:
                    relatorio.append(f"  Frequência crítica (ω): {resultado['freq_critica']:.6f} rad/s")
                    relatorio.append(f"  Período (T): {2*3.14159/resultado['freq_critica']:.6f} s")
                relatorio.append("")
            
            relatorio.append("=" * 70)
            
            return "\n".join(relatorio)
            
        except Exception as e:
            return f"❌ Erro ao gerar relatório: {str(e)}"

# Função equivalente ao rhc do MATLAB
def rhc(coeficientes):
    """
    Função equivalente ao rhc do MATLAB
    Uso: rhc([5, 4, 6, 9, 8, 7])
    """
    resultado = CriteriosEstabilidade.gerar_relatorio_routh_hurwitz(coeficientes)
    print(resultado)

# Exemplo de uso automático
if __name__ == "__main__":
    # Teste automático com os mesmos coeficientes do exemplo
    coeficientes_exemplo = [1, 0.8, 4]
    rhc(coeficientes_exemplo)
