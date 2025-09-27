import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Control de Emisión de Componentes (OF)", layout="wide")
st.title("Control de Emisión de Componentes (OF)")
st.caption("Demo con datos simulados estilo SAP (jul–sep 2025)")

ROOT = Path(__file__).parent
CSV_FILES = sorted([p.name for p in ROOT.glob("*.csv")])

if not CSV_FILES:
    st.warning("No se encontraron CSV en la raíz del repositorio.")
    st.stop()

fname = st.selectbox("Selecciona un CSV", CSV_FILES, index=0)
df = pd.read_csv(ROOT / fname, dtype=str)

st.write(f"**{fname}** — {len(df):,} filas")

# Conversión de cantidad (si existe)
if "cantidad" in df.columns:
    df["cantidad_num"] = pd.to_numeric(
        df["cantidad"].str.replace(",", ".", regex=False), errors="coerce"
    )

# Filtros
c1, c2, c3, c4 = st.columns(4)
with c1:
    mov_ops = sorted(df.get("movimiento", pd.Series()).dropna().unique().tolist())
    f_mov = st.multiselect("Movimiento", mov_ops, default=mov_ops)
with c2:
    f_of = st.text_input("OF contiene")
with c3:
    f_comp = st.text_input("Componente contiene")
with c4:
    f_fecha = st.text_input("Fecha contiene (YYYY-MM)")

fdf = df.copy()
if f_mov:
    fdf = fdf[fdf["movimiento"].isin(f_mov)]
if f_of:
    s = f_of.strip().lower()
    fdf = fdf[fdf["of"].astype(str).str.lower().str.contains(s, na=False)]
if f_comp:
    s = f_comp.strip().lower()
    fdf = fdf[fdf["componente_codigo"].astype(str).str.lower().str.contains(s, na=False)]
if f_fecha and "fecha" in fdf.columns:
    s = f_fecha.strip()
    fdf = fdf[fdf["fecha"].astype(str).str.contains(s, na=False)]

# KPIs
if "cantidad_num" in fdf.columns:
    total_em = fdf.loc[fdf["movimiento"]=="Emision","cantidad_num"].sum()
    total_dev = fdf.loc[fdf["movimiento"]=="Devolucion","cantidad_num"].sum()
    neto = (total_em or 0) - (total_dev or 0)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Emitido", f"{total_em:,.3f}")
    k2.metric("Total Devuelto", f"{total_dev:,.3f}")
    k3.metric("Neto (E-D)", f"{neto:,.3f}")
    k4.metric("Movimientos", f"{len(fdf):,}")

st.dataframe(fdf, use_container_width=True)
