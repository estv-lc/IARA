# IARA: Interface de Análise de Recursos Aquáticos 

A **IARA** é uma plataforma de sensoriamento remoto e análise estatística voltada ao monitoramento de parâmetros oceanográficos e à detecção de anomalias ambientais no litoral brasileiro. Desenvolvido para a **Olimpíada do Oceano (O2)** e como projeto de validação acadêmica, o sistema cruza dados biogeoquímicos e físicos para identificar fatores que influenciam a ocorrência de Florações Algais Nocivas (FANs).

## Funcionalidades Principais

* **Monitoramento de Hotspots Nacionais:** Cobertura parametrizada para quatro regiões estratégicas:
  * Garopaba (SC) - Dinâmica de ressurgência e águas temperadas.
  * Baía de Guanabara (RJ) - Sistema estuarino eutrofizado por pressões antrópicas.
  * Parque Nacional de Abrolhos (BA) - Sensibilidade térmica em ecossistemas de corais.
  * Foz do Amazonas (AP/PA) - Pluma estuarina de alta turbidez.
* **Análise Multifatorial:** Processamento de séries temporais diárias de Clorofila-a ($CHL$), Temperatura da Superfície do Mar ($SST$) e Turbidez ($SPM$).
* **Modelagem Estatística Dinâmica:** Cálculo em tempo real do Coeficiente de Correlação de Pearson ($R$) e ajuste de regressão linear para avaliar a dependência biofísica entre variáveis.
* **Filtros de Rigor Científico:** Tratamento ativo de limitações instrumentais, como a saturação óptica em Águas de Caso 2 (Foz do Amazonas) e transição de conjuntos de dados térmicos (REP vs NRT).

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Acesso a Dados:** `copernicusmarine` (API oficial do Copernicus Marine Service)
* **Processamento de Matrizes Multidimensionais:** `xarray` e `netCDF4`
* **Manipulação e Estatística:** `pandas`, `numpy` e `scipy`
* **Visualização de Dados:** `plotly` (gráficos dinâmicos) e `streamlit` (interface web)

## Como Executar o Projeto Localmente

### 1. Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado em sua máquina.

### 2. Clonar o Repositório
```bash
git clone [https://github.com/](https://github.com/)[seu-usuario]/IARA.git
cd IARA