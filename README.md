# IARA: Interface de Análise de Recursos Aquáticos 

A **IARA** é uma plataforma que associa dados de sensoriamento remoto e permite uma análise estatística voltado ao monitoramento de condições oceanográficas e à possível detecção de anomalias na rede hidrográfica brasileira. Desenvolvido para a **Olímpiada do Oceano (02)**, o sistema cruza dados biológicos, geológicos, físicos e químicos para identificar fatores que possivelmente influenciem florações algais nocivas (FANs).

## Acesse a aplicação

A IARA está disponível online e pode ser utilizada diretamente pelo navegador, sem necessidade de instalação:

[![Abrir a IARA no Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://iara-o2.streamlit.app/)

**Link direto:** [iara-o2.streamlit.app](https://iara-o2.streamlit.app/)

## Funcionalidades principais

* **Monitoramento de hotspots nacionais:** Cobertura para quatro regiões estratégicas:
  * Garopaba (SC) - Dinâmica de ressurgência em águas temperadas.
  * Baía de Guanabara (RJ) - Sistema de estuário eutrofizado por pressões antrópicas.
  * Parque Nacional de Abrolhos (BA) - Sensibilidade térmica em ecossistemas de corais.
  * Foz do Amazonas (AP/PA) - Pluma em estuário de alta turbidez.
* **Análise multifatorial:** Processamento de séries temporais de clorofila-a, temperatura da superfície do mar e turbidez.
* **Modelagem estatística:** Cálculo do coeficiente de correlação de pearson e ajuste de regressão linear para avaliar a possível dependência entre variáveis.
* **Filtros de rigor:** Tratamento de limitações instrumentais, como a saturação óptica em águas de caso 2 (Foz do Amazonas) e o tempo de coleta de dados térmicos (REP).

## Tecnologias utilizadas

* **Linguagem:** Python
* **Acesso a dados:** `copernicusmarine` (API do Copernicus Marine Service)
* **Processamento de matrizes multidimensionais:** `xarray` e `netCDF4`
* **Manipulação e estatística:** `pandas`, `numpy` e `scipy`
* **Visualização de dados:** `plotly` (gráficos) e `streamlit` (interface web)

## Como executar o projeto localmente

### 1. Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado.

### 2. Clonar o repositório
```bash
git clone [https://github.com/](https://github.com/)[estv-lc]/IARA.git
cd IARA
```
