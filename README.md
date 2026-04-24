<div align="center">

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Concluído-22c55e?style=for-the-badge"/>
<img src="https://img.shields.io/badge/TCC-UFERSA%202025-orange?style=for-the-badge"/>

<br/><br/>

# ⚙️ SysControl — Ferramenta de Análise de Sistemas de Controle

> **Aplicação desktop completa para análise, projeto e simulação de sistemas de controle dinâmicos.**  
> Desenvolvida como Trabalho de Conclusão de Curso em Engenharia de Computação.

<br/>

_Autor: **Luís Fernando Alexandre dos Santos**_  
_Orientador: **Prof. Dr. Cecilio Martins de Sousa Neto**_  
_Universidade Federal Rural do Semi-Árido — UFERSA · 2025_

</div>

---

## 📌 Visão Geral

O **SysControl** é uma ferramenta educacional desenvolvida em Python com interface gráfica moderna, destinada a estudantes e profissionais de Engenharia de Controle, Computação, Elétrica e Mecatrônica.

A aplicação reúne em um único ambiente:

- ✅ Análise de **estabilidade** via Critério de Routh-Hurwitz
- ✅ Extração de **parâmetros** de sistemas de segunda ordem (ωₙ, ζ, K)
- ✅ Análise completa do **Lugar Geométrico das Raízes (LGR)**
- ✅ Projeto e simulação de **controladores PI, PD e PID** com comparativos gráficos

---

## 🖥️ Interface da Aplicação

| Módulo | Tela |
|--------|------|
| 🏠 Tela Principal | ![Tela Principal](image/tela1.png) |
| 📊 Análise de Estabilidade | ![Análise de Estabilidade](image/tela2.png) |
| ⚙️ Sistema de 2ª Ordem | ![Análise de Sistema 2ª Ordem](image/tela3.png) |
| 📌 Lugar Geométrico das Raízes | ![LGR](image/tela4.png) |
| 🎮 Análise de Controladores | ![Análise de Controladores](image/tela5.png) |

---

## 🧩 Módulos

### 📊 1. Análise de Estabilidade

Determina a estabilidade de um sistema a partir de sua equação característica.

- Implementa o **Critério de Routh-Hurwitz** com geração automática da tabela
- Identifica o número de **polos instáveis** (semiplano direito)
- Exibe as **raízes do polinômio** e uma conclusão clara sobre a estabilidade

**Entrada:** coeficientes do polinômio característico  
**Saída:** tabela de Routh formatada + relatório textual completo

---

### ⚙️ 2. Análise de Sistema de 2ª Ordem

Extrai parâmetros e métricas de desempenho de sistemas de segunda ordem.

| Parâmetro | Descrição |
|-----------|-----------|
| ωₙ | Frequência natural |
| ζ | Coeficiente de amortecimento |
| K | Ganho estático |
| Tr | Tempo de subida (10% → 90%) |
| Tp | Tempo de pico |
| Mp (%) | Máximo sobressinal |
| Ts | Tempo de acomodação (±2%) |

Classifica automaticamente o sistema: **subamortecido**, **criticamente amortecido** ou **superamortecido**.

---

### 📌 3. Lugar Geométrico das Raízes (LGR)

Análise gráfica e textual completa do LGR de um sistema em malha aberta.

**Regras de construção calculadas:**
1. Polos e zeros do sistema
2. Segmentos do eixo real pertencentes ao LGR
3. Assíntotas — centro e ângulos
4. Pontos de entrada/saída (`dK/ds = 0`)
5. Ângulos de partida e chegada (polos/zeros complexos)
6. **Ganho Crítico (K)** e cruzamentos com o eixo jω via Routh-Hurwitz

**Saídas:** gráfico interativo com polos, zeros, ramos e assíntotas + relatório didático detalhado

---

### 🎮 4. Análise de Controladores (PI · PD · PID)

Projeta, simula e compara o desempenho do sistema com e sem controlador.

**Interface multi-abas com comparativos lado a lado:**

| Aba | Conteúdo |
|-----|----------|
| 📈 Resposta Temporal | y(t) — sistema original vs. controlado |
| 📌 Lugar das Raízes | LGR de G(s) vs. Gc(s)·G(s) |
| 🗺️ Polos e Zeros | Mapa do sistema em malha fechada |
| 📋 Métricas | Tabela comparativa (Tr, Ts, Mp, e_ss...) |

> **Funcionalidade extra:** a aba LGR permite definir **polos dominantes desejados** a partir de ζ e ωₙ, exibindo a linha de ζ constante no gráfico para auxiliar no projeto.

---

## 🧠 Base Teórica

```
G(s) = N(s) / D(s)          Função de Transferência

         K · ωₙ²
G(s) = ──────────────────    Forma padrão de 2ª ordem
        s² + 2ζωₙs + ωₙ²
```

| Conceito | Descrição |
|----------|-----------|
| **Função de Transferência** | Representação no domínio de Laplace |
| **Routh-Hurwitz** | Método algébrico para análise de estabilidade |
| **LGR** | Trajetória dos polos de malha fechada em função do ganho K |
| **PID** | Controlador com ação proporcional, integral e derivativa |
| **Erro em Regime (e_ss)** | Diferença entre referência e saída em regime permanente |

---

## 🛠️ Stack Tecnológica

| Biblioteca | Uso |
|------------|-----|
| `CustomTkinter` | Interface gráfica moderna e responsiva |
| `Matplotlib` | Geração e exibição de gráficos embutidos |
| `Control` | Núcleo de análise de sistemas de controle |
| `NumPy` | Cálculos numéricos e manipulação de arrays |
| `SciPy` | Simulação da resposta à rampa (`lsim`) |
| `SymPy` | Cálculos simbólicos do LGR e tabela de Routh |
| `Pillow` | Carregamento de imagens na interface |

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/luisFernandoJv/sistema-de-controle---an-lise-de-sistema-de-segunda-ordem-.git
cd sistema-de-controle---an-lise-de-sistema-de-segunda-ordem-
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
customtkinter
matplotlib
control
numpy
scipy
sympy
Pillow
```

### 4. Execute a aplicação

```bash
python tela.py
```

---

## 📁 Estrutura do Projeto

```
📦 sistema-de-controle/
 ┣ 📂 image/              # Screenshots da interface
 ┣ 📜 tela.py             # Ponto de entrada — tela principal
 ┣ 📜 estabilidade.py     # Módulo 1: Análise de Estabilidade
 ┣ 📜 segunda_ordem.py    # Módulo 2: Sistema de 2ª Ordem
 ┣ 📜 lgr.py              # Módulo 3: Lugar Geométrico das Raízes
 ┣ 📜 controladores.py    # Módulo 4: Análise de Controladores
 ┣ 📜 requirements.txt
 ┗ 📜 README.md
```

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.

---

<div align="center">

Desenvolvido com 💙 para a comunidade de Engenharia de Controle  
**UFERSA · Engenharia de Computação · 2025**

</div>
