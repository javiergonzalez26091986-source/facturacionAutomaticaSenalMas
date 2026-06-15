import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="Facturación en Bloque - Señal Más", layout="wide")

st.title("Generador de Facturación en Bloque SIIGO 🚀")
st.write("Sube la lista de clientes para generar automáticamente el archivo de movimiento contable.")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .stAppDeployButton {display:none;} div[data-testid="stToolbar"] { visibility: hidden !important; }
        .main { background-color: #00233c; } .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        h1, h3 { text-align: center !important; }
        h1 { color: #ffffff; font-size: 2.2rem; margin-top: 0; font-weight: 700; }
        h3 { color: #b0c4de; font-size: 1.1rem; font-weight: 400; margin-bottom: 2.5rem; }
        .stMarkdown p { color: #ffffff; text-align: center; }
        .stTextInput > div > div > input { background-color: #ffffff; color: #00233c; border-radius: 8px; border: 2px solid #00a896; }
        .stForm { border: none; border-radius: 12px; background-color: #ffffff; padding: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .stForm label, .stForm p { color: #00233c !important; font-weight: 600; text-align: left; }
        div[data-testid="stFormSubmitButton"] button {
            background-color: #00a896 !important; color: #ffffff !important; border-radius: 8px !important;
            font-weight: 700 !important; font-size: 1.1rem !important; border: none !important;
            padding: 0.7rem 2rem !important; width: 100% !important; box-shadow: 0 4px 10px rgba(0,168,150,0.3) !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover { background-color: #02c3b1 !important; box-shadow: 0 6px 15px rgba(2,195,177,0.5) !important; }
        .stMarkdown hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #b0c4de, transparent); margin-top: 3rem; }
    </style>
    """, unsafe_allow_html=True)

# Función para calcular los rubros basados en el total
def calcular_rubros(total):
    rubros = [
        {"producto": "41457001", "descripcion": "Servicio de transmisión de datos", "factor": 0.073117647},
        {"producto": "41457002", "descripcion": "Concesión de Equipos", "factor": 0.658058824},
        {"producto": "28150501", "descripcion": "Ingresos Recibidos para Terceros", "factor": 0.176470588},
        {"producto": "24080101", "descripcion": "Iva", "factor": 0.033529412}
    ]
    
    resultados = []
    for r in rubros:
        resultados.append({
            "CÓDIGO PRODUCTO (OBLIGATORIO)": r["producto"],
            "DESCRIPCIÓN DE LA SECUENCIA": r["descripcion"],
            # Nota: Respetamos los 3 espacios de la plantilla de SIIGO
            "VALOR DE LA SECUENCIA   (OBLIGATORIO)": round(total * r["factor"], 2) 
        })
    return resultados

# Columnas exactas de la plantilla movimientocontablebasico de SIIGO
COLUMNAS_SIIGO = [
    "TIPO DE COMPROBANTE (OBLIGATORIO)",
    "CÓDIGO COMPROBANTE  (OBLIGATORIO)",
    "NÚMERO DE DOCUMENTO",
    "VALOR DE LA SECUENCIA   (OBLIGATORIO)",
    "AÑO DEL DOCUMENTO (OBLIGATORIO)",
    "MES DEL DOCUMENTO (OBLIGATORIO)",
    "DÍA DEL DOCUMENTO (OBLIGATORIO)",
    "CÓDIGO DEL VENDEDOR",
    "SECUENCIA (OBLIGATORIO)",
    "CENTRO DE COSTO (OBLIGATORIO)",
    "SUBCENTRO DE COSTO (OBLIGATORIO)",
    "NIT (OBLIGATORIO)",
    "SUCURSAL (OBLIGATORIO)",
    "DESCRIPCIÓN DE LA SECUENCIA",
    "VALOR DEL CARGO 1 DE LA SECUENCIA",
    "VALOR DEL CARGO 2 DE LA SECUENCIA",
    "VALOR DEL DESCUENTO 1 DE LA SECUENCIA",
    "VALOR DEL DESCUENTO 2 DE LA SECUENCIA",
    "PREFIJO DE ORDER REFERENCE",
    "CONSECUTIVO DE ORDER REFERENCE",
    "RUTA DOCUMENTO",
    "PORCENTAJE DEL IVA DE LA SECUENCIA",
    "LÍNEA PRODUCTO (OBLIGATORIO)",
    "GRUPO PRODUCTO (OBLIGATORIO)",
    "CÓDIGO PRODUCTO (OBLIGATORIO)",
    "CANTIDAD (OBLIGATORIO)",
    "CÓDIGO DE LA BODEGA (OBLIGATORIO)",
    "CÓDIGO DE LA UBICACIÓN (OBLIGATORIO)",
    "CANTIDAD DE FACTOR DE CONVERSIÓN",
    "OPERADOR DE FACTOR DE CONVERSIÓN",
    "VALOR DEL FACTOR DE CONVERSIÓN",
    "DESCRIPCIÓN DE COMENTARIOS",
    "DESCRIPCIÓN LARGA"
]

# Subida del archivo de clientes
archivo_clientes = st.file_uploader("Sube el archivo 'Lista de Clientes - SEÑAL MÁS.xlsx' o CSV", type=['xlsx', 'csv'])

if archivo_clientes is not None:
    try:
        # Leer el archivo
        if archivo_clientes.name.endswith('.csv'):
            df_clientes = pd.read_csv(archivo_clientes) 
        else:
            df_clientes = pd.read_excel(archivo_clientes)
        
        # Limpiar columnas vacías y espacios en los nombres
        df_clientes = df_clientes.dropna(axis=1, how='all')
        df_clientes.columns = df_clientes.columns.str.strip()
        
        st.success("Archivo cargado correctamente.")
        
        # Validar que existan las columnas obligatorias
        columnas_requeridas = ['Estado', 'Servicio', 'Valor']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_clientes.columns]
        
        if not columnas_faltantes:
            df_clientes['Estado'] = df_clientes['Estado'].astype(str).str.strip().str.upper()
            
            # Filtrar clientes Activos y Suspendidos
            estados_a_facturar = ['ACTIVO', 'SUSPENDIDO']
            df_a_facturar = df_clientes[df_clientes['Estado'].isin(estados_a_facturar)]
            
            st.info(f"Procesando {len(df_a_facturar)} clientes (Activos y Suspendidos).")
            
            if st.button("Generar Archivo SIIGO"):
                filas_siigo = []
                hoy = datetime.now()
                errores = [] 
                
                barra_progreso = st.progress(0)
                total_clientes = len(df_a_facturar)
                
                for index, (i, row) in enumerate(df_a_facturar.iterrows()):
                    nit_cliente = row['Servicio']
                    estado_cliente = row['Estado']
                    
                    try:
                        if pd.isna(row['Valor']):
                            raise ValueError("Celda vacía")
                            
                        valor_celda = str(row['Valor']).replace('$', '').replace(',', '').strip()
                        precio_plan = float(valor_celda)
                        
                        if precio_plan <= 0:
                            raise ValueError("Valor cero o negativo")
                        
                        desglose = calcular_rubros(precio_plan)
                        
                        secuencia = 1
                        for item in desglose:
                            # 1. Crear un diccionario con todas las 33 columnas vacías por defecto
                            fila = {col: "" for col in COLUMNAS_SIIGO}
                            
                            # 2. Llenar solo los campos que SIIGO exige para la factura
                            fila["TIPO DE COMPROBANTE (OBLIGATORIO)"] = "Factura"
                            fila["CÓDIGO COMPROBANTE  (OBLIGATORIO)"] = "1"
                            fila["VALOR DE LA SECUENCIA   (OBLIGATORIO)"] = item["VALOR DE LA SECUENCIA   (OBLIGATORIO)"]
                            fila["AÑO DEL DOCUMENTO (OBLIGATORIO)"] = hoy.year
                            fila["MES DEL DOCUMENTO (OBLIGATORIO)"] = hoy.month
                            fila["DÍA DEL DOCUMENTO (OBLIGATORIO)"] = hoy.day
                            fila["CÓDIGO DEL VENDEDOR"] = "1"
                            fila["SECUENCIA (OBLIGATORIO)"] = secuencia
                            fila["CENTRO DE COSTO (OBLIGATORIO)"] = "1"
                            fila["SUBCENTRO DE COSTO (OBLIGATORIO)"] = "1"
                            fila["NIT (OBLIGATORIO)"] = nit_cliente
                            fila["SUCURSAL (OBLIGATORIO)"] = "0"
                            fila["DESCRIPCIÓN DE LA SECUENCIA"] = item["DESCRIPCIÓN DE LA SECUENCIA"]
                            fila["CÓDIGO PRODUCTO (OBLIGATORIO)"] = item["CÓDIGO PRODUCTO (OBLIGATORIO)"]
                            fila["CANTIDAD (OBLIGATORIO)"] = "1"
                            fila["CÓDIGO DE LA BODEGA (OBLIGATORIO)"] = "1"
                            
                            filas_siigo.append(fila)
                            secuencia += 1
                            
                    except Exception as e:
                        errores.append(f"NIT {nit_cliente} (Estado: {estado_cliente}) - Valor inválido o vacío: '{row['Valor']}'")
                    
                    barra_progreso.progress((index + 1) / total_clientes)
                
                if errores:
                    st.warning(f"⚠️ Se omitieron {len(errores)} clientes por no tener un 'Valor' válido:")
                    with st.expander("Ver detalle de clientes omitidos"):
                        for err in errores:
                            st.write(err)
                
                if filas_siigo:
                    # Crear DataFrame respetando el orden de COLUMNAS_SIIGO
                    df_siigo = pd.DataFrame(filas_siigo, columns=COLUMNAS_SIIGO)
                    
                    st.success("¡Archivo generado con éxito en el formato exacto de SIIGO!")
                    st.dataframe(df_siigo.head(10))
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_siigo.to_excel(writer, index=False, sheet_name='Movimiento')
                    
                    st.download_button(
                        label="📥 Descargar Archivo 100% Compatible",
                        data=buffer.getvalue(),
                        file_name=f"movimiento_siigo_completo_{hoy.strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.ms-excel",
                        type="primary"
                    )
                else:
                    st.error("No se generó ninguna factura. Verifica los valores en tu archivo Excel.")
                    
        else:
            st.error(f"⚠️ Error de formato: Tu archivo de Excel debe contener obligatoriamente las columnas: **{', '.join(columnas_faltantes)}**.")
            st.info("💡 Asegúrate de nombrar la columna del precio exactamente como 'Valor'.")
            
    except Exception as e:
        st.error(f"Hubo un error general procesando el archivo: {e}")
