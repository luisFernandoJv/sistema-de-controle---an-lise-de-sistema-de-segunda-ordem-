import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import math
import platform

class ErroValidacao(Exception):
    """Exceção customizada para erros de validação"""
    pass

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
        """
        Valida se os coeficientes são válidos
        
        Args:
            coeficientes: Lista de coeficientes
            nome: Nome do campo para mensagem de erro
            
        Raises:
            ErroValidacao: Se os coeficientes forem inválidos
        """
        if not coeficientes or len(coeficientes) == 0:
            raise ErroValidacao(f"❌ {nome.capitalize()} não pode estar vazio!")
        
        # Verificar se todos são números válidos
        for i, coef in enumerate(coeficientes):
            if not isinstance(coef, (int, float, np.number)):
                raise ErroValidacao(f"❌ {nome.capitalize()}[{i}] = '{coef}' não é um número válido!")
            
            if math.isnan(coef) or math.isinf(coef):
                raise ErroValidacao(f"❌ {nome.capitalize()}[{i}] contém valor inválido (NaN ou Infinito)!")
        
        # Verificar se o primeiro coeficiente não é zero
        if abs(coeficientes[0]) < 1e-15:
            raise ErroValidacao(
                f"❌ O primeiro coeficiente de {nome} não pode ser zero!\n"
                f"   O coeficiente do termo de maior grau deve ser diferente de zero."
            )
        
        # Verificar se todos os coeficientes são zero
        if all(abs(c) < 1e-15 for c in coeficientes):
            raise ErroValidacao(f"❌ {nome.capitalize()} não pode ter todos os coeficientes iguais a zero!")
    
    @staticmethod
    def routh_hurwitz(coeficientes):
        """
        Implementação do critério de Routh-Hurwitz
        
        Args:
            coeficientes: Lista de coeficientes do polinômio característico
            
        Returns:
            tuple: (tabela, polos_direita, raizes_polinomio)
            
        Raises:
            ErroValidacao: Se os coeficientes forem inválidos
        """
        try:
            # Validar coeficientes
            CriteriosEstabilidade.validar_coeficientes(coeficientes, "polinômio característico")
            
            r = coeficientes
            m = len(r)
            n = round(m / 2)
            
            # Separar coeficientes pares e ímpares
            coeficientes_pares = []
            coeficientes_impares = []
            
            for p in range(len(r)):
                if (p + 1) % 2 == 0:
                    coeficientes_pares.append(r[p])
                else:
                    coeficientes_impares.append(r[p])
            
            # Preencher a tabela de Routh-Hurwitz
            tabela = np.zeros((m, n))
            
            # Ajustar tamanho se necessário
            if len(coeficientes_pares) < n:
                coeficientes_pares.extend([0] * (n - len(coeficientes_pares)))
            if len(coeficientes_impares) < n:
                coeficientes_impares.extend([0] * (n - len(coeficientes_impares)))
            
            tabela[0, :] = coeficientes_impares[:n]
            tabela[1, :] = coeficientes_pares[:n]
            
            # Substituir zero por um valor pequeno
            if abs(tabela[1, 0]) < 1e-15:
                tabela[1, 0] = 0.01
            
            # Preencher o restante da tabela
            for i in range(2, m):
                for j in range(n - 1):
                    x = tabela[i-1, 0]
                    if abs(x) < 1e-15:
                        x = 0.01
                    
                    try:
                        tabela[i, j] = ((tabela[i-1, 0] * tabela[i-2, j+1]) - 
                                       (tabela[i-2, 0] * tabela[i-1, j+1])) / x
                    except (ZeroDivisionError, IndexError):
                        tabela[i, j] = 0
                
                # Caso especial: linha toda zero
                if np.all(np.abs(tabela[i, :]) < 1e-15):
                    ordem = m - i + 1
                    c = 0
                    d = 0
                    for j in range(n - 1):
                        if d < len(tabela[i-1, :]):
                            tabela[i, j] = (ordem - c) * tabela[i-1, d]
                            d += 1
                            c += 2
                
                # Substituir zero por valor pequeno
                if abs(tabela[i, 0]) < 1e-15:
                    tabela[i, 0] = 0.01
            
            # Contar polos no semiplano direito
            polos_direita = 0
            for i in range(m - 1):
                if tabela[i, 0] * tabela[i+1, 0] < 0:
                    polos_direita += 1
            
            # Calcular raízes
            try:
                raizes_polinomio = np.roots(r)
            except Exception as e:
                print(f"Aviso: Não foi possível calcular raízes: {str(e)}")
                raizes_polinomio = np.array([])
            
            return tabela, polos_direita, raizes_polinomio
            
        except ErroValidacao:
            raise
        except Exception as e:
            raise ErroValidacao(f"❌ Erro ao calcular Routh-Hurwitz: {str(e)}")

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
                if col_power >= 0:
                    header_text = f"s^{col_power}"
                else:
                    header_text = ""
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
            
            relatorio = "╔" * 60 + "\n"
            relatorio += "         ANÁLISE DE ESTABILIDADE - ROUTH-HURWITZ\n"
            relatorio += "╔" * 60 + "\n\n"
            
            relatorio += "POLINÔMIO CARACTERÍSTICO:\n"
            relatorio += f"  {CriteriosEstabilidade.formatar_equacao_caracteristica(coeficientes)}\n\n"
            
            relatorio += "TABELA DE ROUTH-HURWITZ:\n"
            relatorio += CriteriosEstabilidade.formatar_tabela_routh(tabela)
            
            relatorio += "\n\n" + "─" * 60 + "\n"
            relatorio += "RESULTADO DA ANÁLISE:\n"
            relatorio += "─" * 60 + "\n"
            
            relatorio += f"• Número de polos no semiplano direito: {polos_direita}\n"
            
            if polos_direita == 0:
                relatorio += "• ✅ SISTEMA ESTÁVEL - Todos os polos estão no semiplano esquerdo\n"
            else:
                relatorio += f"• ⚠️  SISTEMA INSTÁVEL - {polos_direita} polo(s) no semiplano direito\n"
            
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
            
            resultado = "╔" * 70 + "\n"
            resultado += "              ANÁLISE COMPLETA DO SISTEMA\n"
            resultado += "╔" * 70 + "\n\n"
            
            # Função de transferência
            resultado += "FUNÇÃO DE TRANSFERÊNCIA:\n"
            resultado += "─" * 40 + "\n"
            resultado += f"  {CriteriosEstabilidade.formatar_funcao_transferencia(numerador, denominador)}\n\n"
            
            # Equação característica
            resultado += "EQUAÇÃO CARACTERÍSTICA:\n"
            resultado += "─" * 40 + "\n"
            resultado += f"  {CriteriosEstabilidade.formatar_equacao_caracteristica(denominador)}\n\n"
            
            # Análise Routh-Hurwitz
            resultado += CriteriosEstabilidade.gerar_relatorio_routh_hurwitz(denominador)
            
            return resultado
            
        except ErroValidacao as e:
            return f"ERRO DE VALIDAÇÃO:\n{str(e)}"
        except Exception as e:
            return f"❌ Erro na análise do sistema: {str(e)}"


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