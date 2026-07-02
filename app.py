import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

# Configuración de la página (Aquí se carga el favicon de la pestaña)
st.set_page_config(
    page_title="Facturación en Bloque - Señal Más", 
    page_icon="logoSenalMas.ico", # Ícono de la pestaña
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS BLINDADOS CONTRA EL MODO OSCURO ---
st.markdown("""
    <style>
        /* ATAQUE A LAS VARIABLES GLOBALES DE STREAMLIT */
        :root {
            --text-color: #00233c !important;
            --background-color: #ffffff !important;
            --secondary-background-color: #f4f6f9 !important;
        }

        /* 1. Ocultar Header superior, menú de hamburguesa, botón Deploy y Footer */
        [data-testid="stHeader"] {visibility: hidden !important; display: none !important;}
        [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
        [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
        footer {visibility: hidden !important; display: none !important;}
        #MainMenu {visibility: hidden !important; display: none !important;}

        /* 2. Forzar fondo completamente blanco para toda la web app */
        .stApp, .main { background-color: #ffffff !important; } 
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        /* 3. Textos principales en el azul corporativo original para legibilidad */
        h1, h1 *, div[data-testid="stMarkdownContainer"] h1 { 
            color: #00233c !important; 
            text-align: center !important;
            font-size: 2.2rem !important; 
            margin-top: 0 !important; 
            font-weight: 700 !important; 
        }
        
        h3, h3 *, div[data-testid="stMarkdownContainer"] h3 { 
            color: #00a896 !important; 
            text-align: center !important;
            font-size: 1.1rem !important; 
            font-weight: 600 !important; 
            margin-bottom: 2.5rem !important; 
        }
        
        /* Etiquetas y descripciones generales */
        label, label p, div[data-testid="stWidgetLabel"] p, p, .stMarkdown p { 
            color: #00233c !important; 
            font-weight: 600 !important;
        }

        /* 4. Subidor de archivos (área donde se arrastra) blindado */
        [data-testid="stFileUploaderDropzone"] {
            background-color: #f4f6f9 !important;
            border: 2px dashed #00a896 !important;
            border-radius: 8px !important;
        }
        [data-testid="stFileUploaderDropzone"] * {
            color: #00233c !important;
            -webkit-text-fill-color: #00233c !important;
        }
        [data-testid="stFileUploader"] button {
            background-color: #ffffff !important;
            color: #00233c !important;
            border: 1px solid #00a896 !important;
        }
        [data-testid="stFileUploader"] button svg {
            fill: #00233c !important;
        }
        
        /* RECUADRO DEL ARCHIVO CARGADO: Blindaje total */
        [data-testid="stUploadedFile"] {
            background-color: #f4f6f9 !important;
            border: 1px solid #00a896 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        [data-testid="stUploadedFile"] * {
            color: #00233c !important;
            -webkit-text-fill-color: #00233c !important;
            background-color: transparent !important; /* Quita fondos negros ocultos */
        }
        [data-testid="stUploadedFile"] svg {
            fill: #00233c !important;
        }

        /* 5. Botones generales (Generar, Descargar) */
        div[data-testid="stFormSubmitButton"] button, 
        .stButton button, 
        .stDownloadButton button,
        div[data-testid="stDownloadButton"] button {
            background-color: #00a896 !important; color: #ffffff !important; border-radius: 8px !important;
            font-weight: 700 !important; font-size: 1.1rem !important; border: none !important;
            padding: 0.7rem 2rem !important; width: 100% !important; box-shadow: 0 4px 10px rgba(0,168,150,0.3) !important;
        }
        .stButton button:hover, .stDownloadButton button:hover, div[data-testid="stDownloadButton"] button:hover { 
            background-color: #02c3b1 !important; box-shadow: 0 6px 15px rgba(2,195,177,0.5) !important; 
        }
        .stButton button *, .stDownloadButton button * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        
        /* 6. Evitar fondo oscuro en la tabla de datos previsualizada */
        .stDataFrame { background-color: transparent !important; }
        
        /* 7. Expansores (Expanders) */
        [data-testid="stExpander"] {
            background-color: #f4f6f9 !important;
            border: 1px solid #00a896 !important;
            border-radius: 8px !important;
        }
        [data-testid="stExpander"] * {
            color: #00233c !important;
        }
        
        .stMarkdown hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #00a896, transparent); margin-top: 3rem; }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO Y TÍTULO ALINEADOS ---
try:
    # Convertimos la imagen a código base64 para insertarla en HTML
    with open("logoSenalMas.jpeg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    # Inyectamos el HTML alineando la imagen y el título en la misma línea
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
            <img src="data:image/jpeg;base64,{encoded_string}" width="90" style="border-radius: 10px;">
            <h1 style="margin: 0 !important; padding: 0 !important;">Generador de Facturación en Bloque SIIGO 🚀</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
except Exception:
    # Respaldo en caso de que la imagen no cargue
    st.title("Generador de Facturación en Bloque SIIGO 🚀")
    st.warning("No se encontró la imagen 'logoSenalMas.jpeg'. Verifica el nombre en Github.")

st.markdown("<p style='text-align: center;'>Sube la lista de clientes para generar automáticamente el archivo de movimiento contable.</p>", unsafe_allow_html=True)

# Función para calcular los rubros basados en el total
def calcular_rubros(total):
    rubros = [
        {"producto": "41457001", "descripcion": "INTERNET HOGAR", "factor": 0.073117647, "cc": "1", "scc": "1001"},
        {"producto": "41457002", "descripcion": "CONCESION DE EQUIPOS", "factor": 0.658058824, "cc": "2", "scc": "2001"},
        {"producto": "41459501", "descripcion": "TELEVISION SUBCONTRATADAs", "factor": 0.176470588, "cc": "4", "scc": "4001"},
        {"producto": "24080101", "descripcion": "IVA GENERADO EN VENTAS DEL 19%", "factor": 0.033529412, "cc": "", "scc": ""},
        {"producto": "13050501", "descripcion": "CLIENTES", "factor": 1.0, "cc": "", "scc": ""}
    ]
    
    resultados = []
    for r in rubros:
        resultados.append({
            "CÓDIGO PRODUCTO (OBLIGATORIO)": r["producto"],
            "DESCRIPCIÓN DE LA SECUENCIA": r["descripcion"],
            "VALOR DE LA SECUENCIA   (OBLIGATORIO)": round(total * r["factor"], 2),
            "cc": r["cc"],
            "scc": r["scc"]
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
                            fila = {col: "" for col in COLUMNAS_SIIGO}
                            
                            fila["TIPO DE COMPROBANTE (OBLIGATORIO)"] = "Factura"
                            fila["CÓDIGO COMPROBANTE  (OBLIGATORIO)"] = "1"
                            fila["VALOR DE LA SECUENCIA   (OBLIGATORIO)"] = item["VALOR DE LA SECUENCIA   (OBLIGATORIO)"]
                            fila["AÑO DEL DOCUMENTO (OBLIGATORIO)"] = hoy.year
                            fila["MES DEL DOCUMENTO (OBLIGATORIO)"] = hoy.month
                            fila["DÍA DEL DOCUMENTO (OBLIGATORIO)"] = hoy.day
                            fila["CÓDIGO DEL VENDEDOR"] = "1"
                            fila["SECUENCIA (OBLIGATORIO)"] = secuencia
                            fila["CENTRO DE COSTO (OBLIGATORIO)"] = item["cc"]
                            fila["SUBCENTRO DE COSTO (OBLIGATORIO)"] = item["scc"]
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
                    df_siigo = pd.DataFrame(filas_siigo, columns=COLUMNAS_SIIGO)
                    
                    st.success("¡Archivo generado con éxito en el formato exacto de SIIGO!")
                    st.dataframe(df_siigo.head(10))
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        # 1. Desplazamos los datos de Pandas para que empiecen en la fila 5 (índice 4 de Excel)
                        df_siigo.to_excel(writer, index=False, sheet_name='Movimiento', startrow=4)
                        
                        # 2. Accedemos de forma directa a la hoja de cálculo de xlsxwriter
                        workbook = writer.book
                        worksheet = writer.sheets['Movimiento']
                        
                        # 3. Inyectamos los textos requeridos por la plantilla en las filas indicadas
                        # Fila 1 de Excel (Índice 0): Nombre de la empresa
                        worksheet.write(0, 0, "EMPRESA DE INTERNET Y TELEVISION SEÑAL MAS S.A.S.")
                        
                        # Fila 2 de Excel (Índice 1): Nombre del modelo
                        worksheet.write(1, 0, "MODELO PARA LA IMPORTACION DE MOVIMIENTO CONTABLE - MODELO BÁSICO")
                        
                        # Nota: Las filas 3 y 4 (índices 2 y 3) no se tocan, por lo que permanecen vacías automáticamente.
                    
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
