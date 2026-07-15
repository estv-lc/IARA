import streamlit as st
import xarray as xr
import pandas as pd
import plotly.express as px
import os
import numpy as np

st.set_page_config(page_title="BioOcean View", layout="wide", page_icon="🌊")
st.title("🌊 IARA: Interface de Análise de Recursos Aquáticos")
st.markdown("Desenvolvido para a Olimpíada do Oceano (O2) - Monitoramento de Florações Algais Nocivas.")

REGIOES = {
    "Garopaba - SC (Sul)": {"slug": "garopaba", "bounds": [-48.75, -48.50, -28.15, -27.95]},
    "Baía de Guanabara - RJ (Sudeste)": {"slug": "guanabara", "bounds": [-43.30, -42.90, -23.00, -22.70]},
    "Abrolhos - BA (Nordeste)": {"slug": "abrolhos", "bounds": [-39.20, -38.60, -18.20, -17.60]},
    "Foz do Amazonas - AP/PA (Norte)": {"slug": "amazonas", "bounds": [-50.50, -49.50, 0.50, 1.50]}
}

CATALOGO = {
    "Clorofila-a (Algas)": {"prefixo": "clorofila", "var": "CHL", "unidade": "mg/m³", "cor": "green"},
    "Temperatura da Superfície": {"prefixo": "temperatura", "var": "analysed_sst", "unidade": "°C", "cor": "red"},
    "Turbidez (Sedimentos)": {"prefixo": "turbidez", "var": "SPM", "unidade": "g/m³", "cor": "brown"}
}

# --- BARRA LATERAL ---
st.sidebar.header("Painel de Controle")
regiao_escolhida = st.sidebar.selectbox("Selecione a Região:", list(REGIOES.keys()))
ano_escolhido = st.sidebar.selectbox("Selecione o Ano de Análise:", ["2025", "2026"])

slug_regiao = REGIOES[regiao_escolhida]["slug"]
bounds = REGIOES[regiao_escolhida]["bounds"]

tab_series, tab_correlacao = st.tabs(["📈 Séries Temporais", "📊 Análise de Correlação"])

# ==========================================
# ABA 1: SÉRIES TEMPORAIS INDIVIDUAIS
# ==========================================
with tab_series:
    variavel_escolhida = st.selectbox("Selecione a Variável para Visualização Diária:", list(CATALOGO.keys()))
    info = CATALOGO[variavel_escolhida]
    arquivo = f"{info['prefixo']}_{slug_regiao}_{ano_escolhido}.nc"
    
    is_temp_2026 = (variavel_escolhida == "Temperatura da Superfície" and ano_escolhido == "2026")
    is_amazonas_turbidez = (variavel_escolhida == "Turbidez (Sedimentos)" and regiao_escolhida == "Foz do Amazonas - AP/PA (Norte)")
    
    col_dados, col_mapa = st.columns([2, 1])
    
    with col_mapa:
        st.markdown("### 📍 Área de Monitoramento")
        lat_center = (bounds[2] + bounds[3]) / 2
        lon_center = (bounds[0] + bounds[1]) / 2
        df_mapa = pd.DataFrame({'latitude': [lat_center], 'longitude': [lon_center]})
        st.map(df_mapa)
        
    with col_dados:
        if os.path.exists(arquivo):
            ds = xr.open_dataset(arquivo)
            dados_brutos = ds[info["var"]]
            
            if "Temperatura" in variavel_escolhida and float(dados_brutos.mean(skipna=True)) > 200:
                dados_brutos = dados_brutos - 273.15
                
            serie_diaria = dados_brutos.mean(dim=['latitude', 'longitude'], skipna=True)
            df = serie_diaria.to_dataframe().reset_index().dropna(subset=[info["var"]])
            
            if not df.empty:
                media = df[info["var"]].mean()
                maximo = df[info["var"]].max()
                minimo = df[info["var"]].min()
                
                st.subheader(f"📊 Diagnóstico: {variavel_escolhida} em {regiao_escolhida} ({ano_escolhido})")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Média do Período", f"{media:.2f} {info['unidade']}")
                col_m2.metric("Pico Máximo", f"{maximo:.2f} {info['unidade']}", delta="Anomalia" if maximo > media*2 else "Normal", delta_color="inverse")
                col_m3.metric("Valor Mínimo", f"{minimo:.2f} {info['unidade']}")
                
                if is_temp_2026 or is_amazonas_turbidez:
                    st.markdown("### 📈 Evolução Temporal Diária <span style='color:red;'>*</span>", unsafe_allow_html=True)
                else:
                    st.markdown("### 📈 Evolução Temporal Diária")
                
                fig = px.line(df, x="time", y=info["var"], 
                              labels={"time": "Data", info["var"]: f"Concentração ({info['unidade']})"},
                              color_discrete_sequence=[info["cor"]], markers=True)
                fig.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                if is_temp_2026:
                    st.info(
                        "**Nota Científica (*):** Para garantir o máximo rigor acadêmico, esta plataforma utiliza dados térmicos "
                        "Reprocessados (REP). Devido ao processo de calibração e validação manual dos satélites com boias oceânicas "
                        "reais pela agência Copernicus, há uma defasagem natural de processamento de alguns meses, limitando a "
                        "série histórica de 2026 até o dia 31 de Março."
                    )
                
                if is_amazonas_turbidez:
                    st.info(
                        "**Nota Técnica (*):** Em águas de estuário hiperturbidas (Águas de Caso 2), como a pluma do Rio Amazonas, "
                        "a reflectância óptica atinge a saturação física. Para mitigar artefatos e distorções instrumentais, o algoritmo "
                        "global de turbidez (SPM) do Copernicus adota um limite máximo de corte (teto metodológico) de 100 g/m³."
                    )
            ds.close()
        else:
            st.error(f"Erro: O arquivo de {variavel_escolhida} para a região de {regiao_escolhida} ({ano_escolhido}) não foi localizado no diretório local.")

# ==========================================
# ABA 2: ANÁLISE DE CORRELAÇÃO DE VARIÁVEIS
# ==========================================
with tab_correlacao:
    st.subheader("📊 Cruzamento Estatístico de Dados Oceânicos")
    st.markdown("Selecione duas variáveis distintas para analisar a dinâmica de interação e dependência estatística entre elas.")
    
    col_sel_x, col_sel_y = st.columns(2)
    with col_sel_x:
        var_x = st.selectbox("Variável Independente (Eixo X):", list(CATALOGO.keys()), index=1)
    with col_sel_y:
        var_y = st.selectbox("Variável Dependente (Eixo Y):", list(CATALOGO.keys()), index=0)
        
    if var_x == var_y:
        st.warning("Aviso: Selecione duas variáveis distintas para calcular a correlação.")
    else:
        info_x = CATALOGO[var_x]
        info_y = CATALOGO[var_y]
        
        arq_x = f"{info_x['prefixo']}_{slug_regiao}_{ano_escolhido}.nc"
        arq_y = f"{info_y['prefixo']}_{slug_regiao}_{ano_escolhido}.nc"
        
        if os.path.exists(arq_x) and os.path.exists(arq_y):
            # Processamento Eixo X com renomeação padronizada
            ds_x = xr.open_dataset(arq_x)
            dados_x = ds_x[info_x["var"]]
            if "Temperatura" in var_x and float(dados_x.mean(skipna=True)) > 200:
                dados_x = dados_x - 273.15
            df_x = dados_x.mean(dim=['latitude', 'longitude'], skipna=True).to_dataframe().reset_index()
            df_x = df_x[["time", info_x["var"]]].dropna()
            df_x.rename(columns={info_x["var"]: "valor_x"}, inplace=True)
            
            # Processamento Eixo Y com renomeação padronizada
            ds_y = xr.open_dataset(arq_y)
            dados_y = ds_y[info_y["var"]]
            if "Temperatura" in var_y and float(dados_y.mean(skipna=True)) > 200:
                dados_y = dados_y - 273.15
            df_y = dados_y.mean(dim=['latitude', 'longitude'], skipna=True).to_dataframe().reset_index()
            df_y = df_y[["time", info_y["var"]]].dropna()
            df_y.rename(columns={info_y["var"]: "valor_y"}, inplace=True)
            
            # Fusão baseada na dimensão temporal
            df_merged = pd.merge(df_x, df_y, on="time").dropna()
            
            if not df_merged.empty:
                # Cálculo estatístico
                r_val = df_merged["valor_x"].corr(df_merged["valor_y"])
                
                abs_r = abs(r_val)
                if abs_r < 0.3:
                    desc_corr = "Desprezível ou Muito Fraca"
                elif abs_r < 0.5:
                    desc_corr = "Fraca"
                elif abs_r < 0.7:
                    desc_corr = "Moderada"
                else:
                    desc_corr = "Forte a Muito Forte"
                    
                sinal_corr = "Diretamente Proporcional (Positiva)" if r_val > 0 else "Inversamente Proporcional (Negativa)"
                
                col_r, col_desc = st.columns([1, 2])
                with col_r:
                    st.metric("Coeficiente de Pearson (R)", f"{r_val:.3f}")
                with col_desc:
                    st.markdown(f"**Grau de Associação:** Correlação {desc_corr}")
                    st.markdown(f"**Comportamento:** Relação {sinal_corr}")
                
                # Plotagem do gráfico
                x_vals = df_merged["valor_x"].values
                y_vals = df_merged["valor_y"].values
                
                fig_scatter = px.scatter(
                    df_merged, x="valor_x", y="valor_y",
                    hover_data={"time": True},
                    labels={"valor_x": f"{var_x} ({info_x['unidade']})", "valor_y": f"{var_y} ({info_y['unidade']})"},
                    title=f"Dispersão: {var_x} vs. {var_y} ({regiao_escolhida})"
                )
                
                slope, intercept = np.polyfit(x_vals, y_vals, 1)
                x_trend = np.linspace(x_vals.min(), x_vals.max(), 100)
                y_trend = slope * x_trend + intercept
                
                df_trend = pd.DataFrame({"valor_x": x_trend, "valor_y": y_trend})
                
                fig_trend = px.line(df_trend, x="valor_x", y="valor_y", color_discrete_sequence=["#FF8C00"])
                fig_trend.data[0].name = "Tendência Linear"
                fig_trend.data[0].showlegend = True
                
                fig_scatter.add_trace(fig_trend.data[0])
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            else:
                st.warning("Não há dados sobrepostos suficientes para realizar o cruzamento estatístico para este período.")
                
            ds_x.close()
            ds_y.close()
        else:
            st.error("Erro: Ambas as variáveis selecionadas precisam estar previamente baixadas no diretório para esta região e ano.")
