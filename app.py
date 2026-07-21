import streamlit as st
import xarray as xr
import pandas as pd
import plotly.express as px
import os
import numpy as np
import copernicusmarine as cm

st.set_page_config(page_title="IARA: Recursos Aquáticos", layout="wide", page_icon="🌊")
st.title("🌊 IARA: Interface de Análise de Recursos Aquáticos")
st.markdown("Plataforma de Monitoramento Costeiro e Análise Estatística de Parâmetros Oceanográficos.")

# --- BANCO DE DADOS DO COPERNICUS ---
DATASETS = {
    "Clorofila-a (Algas)": {
        "dataset_id": "cmems_obs-oc_glo_bgc-plankton_my_l4-gapfree-multi-4km_P1D",
        "var": "CHL", "unidade": "mg/m³", "cor": "green", "prefixo": "clorofila"
    },
    "Temperatura da Superfície": {
        "dataset_id": "METOFFICE-GLO-SST-L4-REP-OBS-SST",
        "var": "analysed_sst", "unidade": "°C", "cor": "red", "prefixo": "temperatura"
    },
    "Turbidez (Sedimentos)": {
        "dataset_id": "cmems_obs-oc_glo_bgc-transp_my_l3-multi-4km_P1D",
        "var": "SPM", "unidade": "g/m³", "cor": "brown", "prefixo": "turbidez"
    }
}

REGIOES = {
    "Garopaba - SC (Sul)": {"slug": "garopaba", "bounds": [-48.75, -48.50, -28.15, -27.95]},
    "Baía de Guanabara - RJ (Sudeste)": {"slug": "guanabara", "bounds": [-43.30, -42.90, -23.00, -22.70]},
    "Abrolhos - BA (Nordeste)": {"slug": "abrolhos", "bounds": [-39.20, -38.60, -18.20, -17.60]},
    "Foz do Amazonas - AP/PA (Norte)": {"slug": "amazonas", "bounds": [-50.50, -49.50, 0.50, 1.50]}
}

# --- FUNÇÃO PARA DOWNLOAD DINÂMICO DE COORDENADA ---
def baixar_dados_coordenada(dataset_id, var, lat, lon, ano):
    username = st.secrets["COPERNICUS_USERNAME"]
    password = st.secrets["COPERNICUS_PASSWORD"]
    
    nome_arquivo = f"custom_{var}_{lat}_{lon}_{ano}.nc"
    
    if os.path.exists(nome_arquivo):
        return nome_arquivo
        
    try:
        with st.spinner(f"Conectando ao satélite para extrair {var}..."):
            cm.subset(
                dataset_id=dataset_id,
                variables=[var],
                minimum_longitude=lon - 0.15,
                maximum_longitude=lon + 0.15,
                minimum_latitude=lat - 0.15,
                maximum_latitude=lat + 0.15,
                start_datetime=f"{ano}-01-01T00:00:00",
                end_datetime=f"{ano}-12-31T23:59:59",
                output_filename=nome_arquivo,
                username=username,
                password=password,
                force_download=True
            )
        return nome_arquivo
    except Exception as e:
        st.error(f"Erro ao baixar dados do satélite: {e}")
        return None

# --- BARRA LATERAL ---
st.sidebar.header("Painel de Controle")
modo_analise = st.sidebar.radio("Modo de Cobertura:", ["📍 Hotspots Estáticos", "🌐 Qualquer Ponto do Brasil"])
ano_escolhido = st.sidebar.selectbox("Selecione o Ano de Análise:", ["2025", "2026"])

lat_alvo, lon_alvo = 0.0, 0.0
slug_regiao, bounds, regiao_escolhida = "", [], ""

if modo_analise == "📍 Hotspots Estáticos":
    regiao_escolhida = st.sidebar.selectbox("Selecione a Região:", list(REGIOES.keys()))
    slug_regiao = REGIOES[regiao_escolhida]["slug"]
    bounds = REGIOES[regiao_escolhida]["bounds"]
    lat_alvo = (bounds[2] + bounds[3]) / 2
    lon_alvo = (bounds[0] + bounds[1]) / 2
else:
    st.sidebar.markdown("### Coordenadas do Brasil")
    lat_alvo = st.sidebar.number_input("Latitude (Ex: -23.0 para RJ):", min_value=-35.0, max_value=5.0, value=-23.00, step=0.1)
    lon_alvo = st.sidebar.number_input("Longitude (Ex: -43.1 para RJ):", min_value=-55.0, max_value=-30.0, value=-43.10, step=0.1)
    if st.sidebar.button("📡 Buscar Novos Dados do Satélite"):
        st.sidebar.success("Novas coordenadas registradas! Aguarde o processamento.")

# --- PROCESSAMENTO DOS ARQUIVOS ---
def carregar_e_processar(variavel, ano):
    info = DATASETS[variavel]
    if modo_analise == "📍 Hotspots Estáticos":
        arquivo = f"dados/{info['prefixo']}_{slug_regiao}_{ano}.nc"
        if os.path.exists(arquivo):
            return xr.open_dataset(arquivo), info["var"]
    else:
        arquivo = baixar_dados_coordenada(info["dataset_id"], info["var"], lat_alvo, lon_alvo, ano)
        if arquivo and os.path.exists(arquivo):
            return xr.open_dataset(arquivo), info["var"]
    return None, None

tab_series, tab_correlacao = st.tabs(["📈 Séries Temporais", "📊 Análise de Correlação"])

# ==========================================
# ABA 1: SÉRIES TEMPORAIS INDIVIDUAIS
# ==========================================
with tab_series:
    variavel_escolhida = st.selectbox("Selecione a Variável para Visualização Diária:", list(DATASETS.keys()))
    
    # Condições para ativação dos avisos técnicos e científicos
    is_temp_2026 = (variavel_escolhida == "Temperatura da Superfície" and ano_escolhido == "2026")
    is_amazonas_turbidez = (
        variavel_escolhida == "Turbidez (Sedimentos)" and 
        modo_analise == "📍 Hotspots Estáticos" and 
        regiao_escolhida == "Foz do Amazonas - AP/PA (Norte)"
    )
    
    col_dados, col_mapa = st.columns([2, 1])
    
    with col_mapa:
        st.markdown("### 📍 Área de Monitoramento")
        df_mapa = pd.DataFrame({'latitude': [lat_alvo], 'longitude': [lon_alvo]})
        st.map(df_mapa)
        
    with col_dados:
        ds, var_nome = carregar_e_processar(variavel_escolhida, ano_escolhido)
        if ds is not None:
            dados_brutos = ds[var_nome]
            
            if "Temperatura" in variavel_escolhida and float(dados_brutos.mean(skipna=True)) > 200:
                dados_brutos = dados_brutos - 273.15
                
            serie_diaria = dados_brutos.mean(dim=['latitude', 'longitude'], skipna=True)
            df = serie_diaria.to_dataframe().reset_index().dropna()
            
            if not df.empty:
                media = df[var_nome].mean()
                maximo = df[var_nome].max()
                minimo = df[var_nome].min()
                
                titulo_diag = f"📊 Diagnóstico: {variavel_escolhida}"
                if modo_analise == "📍 Hotspots Estáticos":
                    titulo_diag += f" em {regiao_escolhida} ({ano_escolhido})"
                else:
                    titulo_diag += f" ({ano_escolhido})"
                st.subheader(titulo_diag)
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Média do Período", f"{media:.2f} {DATASETS[variavel_escolhida]['unidade']}")
                col_m2.metric("Pico Máximo", f"{maximo:.2f} {DATASETS[variavel_escolhida]['unidade']}")
                col_m3.metric("Valor Mínimo", f"{minimo:.2f} {DATASETS[variavel_escolhida]['unidade']}")
                
                fig = px.line(df, x="time", y=var_nome, 
                              labels={"time": "Data", var_nome: f"Concentração ({DATASETS[variavel_escolhida]['unidade']})"},
                              color_discrete_sequence=[DATASETS[variavel_escolhida]["cor"]], markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Exibição condicional dos avisos metodológicos
                if is_temp_2026:
                    st.info(
                        "**Nota (*):** Para garantir o máximo rigor acadêmico, esta plataforma utiliza dados térmicos "
                        "Reprocessados (REP). Devido ao processo de calibração e validação manual dos satélites com boias oceânicas "
                        "reais pela agência Copernicus, há uma defasagem natural de processamento de alguns meses, limitando a "
                        "série histórica de 2026 até o dia 31 de Março."
                    )
                
                if is_amazonas_turbidez:
                    st.info(
                        "**Nota (*):** Em águas de estuário hiperturbidas (Águas de Caso 2), como a pluma do Rio Amazonas, "
                        "a reflectância óptica atinge a saturação física. Para mitigar distorções instrumentais, o algoritmo "
                        "global de turbidez (SPM) do Copernicus adota um limite máximo de corte (teto metodológico) de 100 g/m³."
                    )
            ds.close()
        else:
            st.warning("Dados não disponíveis localmente ou aguardando requisição ao satélite.")

# ==========================================
# ABA 2: ANÁLISE DE CORRELAÇÃO DE VARIÁVEIS
# ==========================================
with tab_correlacao:
    st.subheader("📊 Cruzamento Estatístico de Dados Oceânicos")
    col_sel_x, col_sel_y = st.columns(2)
    with col_sel_x:
        var_x = st.selectbox("Variável Independente (Eixo X):", list(DATASETS.keys()), index=1)
    with col_sel_y:
        var_y = st.selectbox("Variável Dependente (Eixo Y):", list(DATASETS.keys()), index=0)
        
    if var_x == var_y:
        st.warning("Aviso: Selecione duas variáveis distintas.")
    else:
        ds_x, var_nome_x = carregar_e_processar(var_x, ano_escolhido)
        ds_y, var_nome_y = carregar_e_processar(var_y, ano_escolhido)
        
        if ds_x is not None and ds_y is not None:
            dados_x = ds_x[var_nome_x]
            if "Temperatura" in var_x and float(dados_x.mean(skipna=True)) > 200:
                dados_x = dados_x - 273.15
            df_x = dados_x.mean(dim=['latitude', 'longitude'], skipna=True).to_dataframe().reset_index()
            df_x = df_x[["time", var_nome_x]].dropna().rename(columns={var_nome_x: "valor_x"})
            
            dados_y = ds_y[var_nome_y]
            if "Temperatura" in var_y and float(dados_y.mean(skipna=True)) > 200:
                dados_y = dados_y - 273.15
            df_y = dados_y.mean(dim=['latitude', 'longitude'], skipna=True).to_dataframe().reset_index()
            df_y = df_y[["time", var_nome_y]].dropna().rename(columns={var_nome_y: "valor_y"})
            
            df_merged = pd.merge(df_x, df_y, on="time").dropna()
            
            if not df_merged.empty:
                r_val = df_merged["valor_x"].corr(df_merged["valor_y"])
                
                col_r, col_desc = st.columns([1, 2])
                with col_r:
                    st.metric("Coeficiente de Pearson (R)", f"{r_val:.3f}")
                with col_desc:
                    st.markdown(f"**Grau de Associação:** Coeficiente calculando o acoplamento ecológico entre as variáveis.")
                
                fig_scatter = px.scatter(df_merged, x="valor_x", y="valor_y", hover_data={"time": True},
                                         labels={"valor_x": f"{var_x}", "valor_y": f"{var_y}"})
                
                slope, intercept = np.polyfit(df_merged["valor_x"].values, df_merged["valor_y"].values, 1)
                x_trend = np.linspace(df_merged["valor_x"].min(), df_merged["valor_x"].max(), 100)
                y_trend = slope * x_trend + intercept
                
                df_trend = pd.DataFrame({"valor_x": x_trend, "valor_y": y_trend})
                fig_trend = px.line(df_trend, x="valor_x", y="valor_y", color_discrete_sequence=["#FF8C00"])
                fig_scatter.add_trace(fig_trend.data[0])
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("Cruzamento indisponível.")
            ds_x.close()
            ds_y.close()
