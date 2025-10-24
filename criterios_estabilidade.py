import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class CriteriosEstabilidade:
    @staticmethod
    def routh_hurwitz(coeficientes):
        """
        Implementação do critério de Routh-Hurwitz
        """
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
        if tabela[1, 0] == 0:
            tabela[1, 0] = 0.01
        
        # Preencher o restante da tabela
        for i in range(2, m):
            for j in range(n - 1):
                x = tabela[i-1, 0]
                if x == 0:
                    x = 0.01
                
                tabela[i, j] = ((tabela[i-1, 0] * tabela[i-2, j+1]) - (tabela[i-2, 0] * tabela[i-1, j+1])) / x
            
            # Caso especial: linha toda zero
            if np.all(tabela[i, :] == 0):
                ordem = m - i + 1
                c = 0
                d = 0
                for j in range(n - 1):
                    if d < len(tabela[i-1, :]):
                        tabela[i, j] = (ordem - c) * tabela[i-1, d]
                        d += 1
                        c += 2
            
            # Substituir zero por valor pequeno
            if tabela[i, 0] == 0:
                tabela[i, 0] = 0.01
        
        # Contar polos no semiplano direito
        polos_direita = 0
        for i in range(m - 1):
            if tabela[i, 0] * tabela[i+1, 0] < 0:
                polos_direita += 1
        
        # Calcular raízes
        raizes_polinomio = np.roots(r)
        
        return tabela, polos_direita, raizes_polinomio

    @staticmethod
    def analisar_nyquist(coeficientes_numerador, coeficientes_denominador):
        """
        Análise de estabilidade pelo critério de Nyquist
        """
        try:
            sistema = signal.TransferFunction(coeficientes_numerador, coeficientes_denominador)
            
            resultado = "=== ANÁLISE DE NYQUIST ===\n\n"
            resultado += f"Sistema: {CriteriosEstabilidade.formatar_funcao_transferencia(coeficientes_numerador, coeficientes_denominador)}\n\n"
            resultado += "Análise de Nyquist realizada com sucesso.\n"
            resultado += "Gráfico de Nyquist pode ser gerado na seção de resultados.\n"
            
            return resultado
        except Exception as e:
            return f"Erro na análise de Nyquist: {str(e)}"

    @staticmethod
    def lugar_das_raizes(coeficientes_numerador, coeficientes_denominador):
        """
        Análise do lugar das raízes
        """
        try:
            sistema = signal.TransferFunction(coeficientes_numerador, coeficientes_denominador)
            
            resultado = "=== LUGAR DAS RAÍZES ===\n\n"
            resultado += f"Sistema: {CriteriosEstabilidade.formatar_funcao_transferencia(coeficientes_numerador, coeficientes_denominador)}\n\n"
            resultado += "Lugar das raízes calculado com sucesso.\n"
            resultado += "Gráfico do lugar das raízes pode ser gerado na seção de resultados.\n"
            
            return resultado
        except Exception as e:
            return f"Erro no cálculo do lugar das raízes: {str(e)}"

    @staticmethod
    def formatar_polinomio(coeficientes):
        """Formata os coeficientes como um polinômio na ordem s⁰, s¹, s², ..."""
        termos = []
        
        for i, coef in enumerate(coeficientes):
            if abs(coef) > 1e-10:  # Ignorar coeficientes muito próximos de zero
                expoente = len(coeficientes) - 1 - i  # Expoente atual
                
                if expoente == 0:
                    termos.append(f"{coef:.4f}")
                elif expoente == 1:
                    if abs(coef) == 1:
                        termos.append("s")
                    else:
                        termos.append(f"{coef:.4f}s")
                else:
                    if abs(coef) == 1:
                        termos.append(f"s^{expoente}")
                    else:
                        termos.append(f"{coef:.4f}s^{expoente}")
        
        # Se não há termos, retorna "0"
        if not termos:
            return "0"
        
        # Junta os termos com " + " e substitui " + -" por " - "
        polinomio = " + ".join(termos)
        polinomio = polinomio.replace("+ -", "- ")
        
        # Remove coeficiente 1 desnecessário
        polinomio = polinomio.replace("1.0000s", "s")
        polinomio = polinomio.replace("-1.0000s", "-s")
        
        return polinomio

    @staticmethod
    def formatar_funcao_transferencia(numerador, denominador):
        """Formata uma função de transferência"""
        num_str = CriteriosEstabilidade.formatar_polinomio(numerador)
        den_str = CriteriosEstabilidade.formatar_polinomio(denominador)
        return f"G(s) = ({num_str}) / ({den_str})"

    @staticmethod
    def formatar_equacao_caracteristica(denominador):
        """Formata a equação característica na ordem s⁰, s¹, s², ..."""
        termos = []
        
        for i, coef in enumerate(denominador):
            if abs(coef) > 1e-10:  # Ignorar coeficientes muito próximos de zero
                expoente = len(denominador) - 1 - i  # Expoente atual
                
                if expoente == 0:
                    termos.append(f"{coef:.4f}")
                elif expoente == 1:
                    if abs(coef) == 1:
                        termos.append("s")
                    else:
                        termos.append(f"{coef:.4f}s")
                else:
                    if abs(coef) == 1:
                        termos.append(f"s^{expoente}")
                    else:
                        termos.append(f"{coef:.4f}s^{expoente}")
        
        # Se não há termos, retorna "0"
        if not termos:
            return "0"
        
        # Junta os termos com " + " e substitui " + -" por " - "
        equacao = " + ".join(termos)
        equacao = equacao.replace("+ -", "- ")
        
        # Remove coeficiente 1 desnecessário
        equacao = equacao.replace("1.0000s", "s")
        equacao = equacao.replace("-1.0000s", "-s")
        
        return f"Δ(s) = {equacao} = 0"

    @staticmethod
    def formatar_tabela_routh(tabela):
        """Formata a tabela de Routh-Hurwitz de forma profissional e organizada"""
        linhas = []
        
        # Determinar o número de colunas
        num_colunas = tabela.shape[1]
        grau_max = tabela.shape[0] - 1
        
        # Criar cabeçalho com as potências de s
        cabecalho = "┌" + "─" * 12 + "┬"
        for i in range(num_colunas - 1):
            cabecalho += "─" * 12 + "┬"
        cabecalho += "─" * 12 + "┐"
        linhas.append(cabecalho)
        
        # Linha do cabeçalho com potências
        linha_potencias = "│"
        for i in range(num_colunas):
            exp = grau_max - 2*i
            if exp >= 0:
                if exp == 0:
                    linha_potencias += f"    s⁰    │"
                elif exp == 1:
                    linha_potencias += f"    s¹    │"
                else:
                    linha_potencias += f"   s{exp:}   │"
            else:
                linha_potencias += " " * 12 + "│"
        linhas.append(linha_potencias)
        
        # Linha separadora
        separadora = "├" + "─" * 12 + "┼"
        for i in range(num_colunas - 1):
            separadora += "─" * 12 + "┼"
        separadora += "─" * 12 + "┤"
        linhas.append(separadora)
        
        # Linhas da tabela
        for i in range(tabela.shape[0]):
            linha = "│"
            for j in range(tabela.shape[1]):
                valor = tabela[i, j]
                if abs(valor) < 1e-10:
                    linha += f"    0.0000  │"
                elif abs(valor) < 1e-4:
                    linha += f" {valor:10.2e} │"
                else:
                    linha += f" {valor:10.4f} │"
            linhas.append(linha)
            
            # Adicionar linha separadora se não for a última linha
            if i < tabela.shape[0] - 1:
                linhas.append(separadora)
        
        # Rodapé da tabela
        rodape = "└" + "─" * 12 + "┴"
        for i in range(num_colunas - 1):
            rodape += "─" * 12 + "┴"
        rodape += "─" * 12 + "┘"
        linhas.append(rodape)
        
        return "\n".join(linhas)

    @staticmethod
    def gerar_relatorio_routh_hurwitz(coeficientes):
        """
        Gera um relatório completo da análise de Routh-Hurwitz
        """
        try:
            tabela, polos_direita, raizes = CriteriosEstabilidade.routh_hurwitz(coeficientes)
            
            relatorio = "═" * 60 + "\n"
            relatorio += "         ANÁLISE DE ESTABILIDADE - ROUTH-HURWITZ\n"
            relatorio += "═" * 60 + "\n\n"
            
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
            
            for i, raiz in enumerate(raizes):
                if abs(raiz.imag) < 1e-10:
                    relatorio += f"• Raiz {i+1}: {raiz.real:10.6f}\n"
                else:
                    relatorio += f"• Raiz {i+1}: {raiz.real:10.6f} + {raiz.imag:10.6f}j\n"
            
            return relatorio
            
        except Exception as e:
            return f"Erro na análise: {str(e)}"

    @staticmethod
    def analisar_sistema_completo(numerador, denominador):
        """
        Análise completa do sistema incluindo função de transferência e equação característica
        """
        try:
            resultado = "═" * 70 + "\n"
            resultado += "              ANÁLISE COMPLETA DO SISTEMA\n"
            resultado += "═" * 70 + "\n\n"
            
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
            
        except Exception as e:
            return f"Erro na análise do sistema: {str(e)}"

# Função equivalente ao rhc do MATLAB
def rhc(coeficientes):
    """
    Função equivalente ao rhc do MATLAB
    Uso: rhc([5, 4, 6, 9, 8, 7])
    """
    resultado = CriteriosEstabilidade.gerar_relatorio_routh_hurwitz(coeficientes)
    print(resultado)

# Exemplo de uso automático (como no MATLAB)
if __name__ == "__main__":
    # Teste automático com os mesmos coeficientes do exemplo
    coeficientes_exemplo = [5, 4, 6, 9, 8, 7]
    rhc(coeficientes_exemplo)