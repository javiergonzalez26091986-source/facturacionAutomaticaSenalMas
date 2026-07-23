import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

# Configuración de la página
st.set_page_config(
    page_title="Facturación en Bloque - Señal Más", 
    page_icon="logoSenalMas.ico",
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
    with open("logoSenalMas.jpeg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
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
    st.title("Generador de Facturación en Bloque SIIGO 🚀")
    st.warning("No se encontró la imagen 'logoSenalMas.jpeg'. Verifica el nombre en Github.")

st.markdown("<p style='text-align: center;'>Sube la lista de clientes para generar automáticamente el archivo de movimiento contable (Modelo General - 8 Secuencias).</p>", unsafe_allow_html=True)

# --- 1. FUNCIÓN DE RUBROS (8 SECUENCIAS DEL MODELO GENERAL) ---
def calcular_rubros(total, nombre_cliente):
    # Cálculos matemáticos precisos
    val_internet = round(total * 0.073117647, 2)
    val_equipos = round(total * 0.658058824, 2)
    val_tv = round(total * 0.176470588, 2)
    val_iva = round(total * 0.033529412, 2)
    
    # El valor de clientes debe ser la suma exacta para evitar descuadres de centavos
    val_clientes = round(val_internet + val_equipos + val_tv + val_iva, 2) 
    
    # 8 Filas requeridas por la plantilla (Ingresos, CxC, Impuestos e Inventarios)
    rubros = [
        # 1. Ingreso Internet
        {"cuenta": "4145700100", "dc": "C", "linea": "1", "grupo": "1", "producto": "1001", "descripcion": "INTERNET HOGAR", "valor": val_internet, "cc": 0, "scc": 0, "zona": 1, "iva": 0, "gravada": "N", "base_cheque": 0, "cant": 1, "bodega": 1, "forma_pago": 0},
        
        # 2. Ingreso Equipos
        {"cuenta": "4145700200", "dc": "C", "linea": "1", "grupo": "2", "producto": "2001", "descripcion": "CONCESION DE EQUIPOS", "valor": val_equipos, "cc": 0, "scc": 0, "zona": 1, "iva": 0, "gravada": "N", "base_cheque": 0, "cant": 1, "bodega": 1, "forma_pago": 0},
        
        # 3. Ingreso TV (OJO: Centro de costo 1, IVA 19, Gravada S)
        {"cuenta": "4145950100", "dc": "C", "linea": "1", "grupo": "4", "producto": "4001", "descripcion": "TELEVISION SUBCONTRATADA", "valor": val_tv, "cc": 1, "scc": 0, "zona": 1, "iva": 19, "gravada": "S", "base_cheque": 0, "cant": 1, "bodega": 1, "forma_pago": 0},
        
        # 4. Clientes (OJO: Forma de pago 1)
        {"cuenta": "1305050100", "dc": "D", "linea": "", "grupo": "", "producto": "", "descripcion": nombre_cliente, "valor": val_clientes, "cc": 0, "scc": 0, "zona": 0, "iva": 0, "gravada": "", "base_cheque": 0, "cant": 0, "bodega": 0, "forma_pago": 1},
        
        # 5. IVA (OJO: El cheque lleva la base del servicio TV)
        {"cuenta": "2408050100", "dc": "C", "linea": "", "grupo": "", "producto": "", "descripcion": nombre_cliente, "valor": val_iva, "cc": 0, "scc": 0, "zona": 0, "iva": 0, "gravada": "", "base_cheque": val_tv, "cant": 0, "bodega": 0, "forma_pago": 0},
        
        # 6. Costo/Inventario Internet (OJO: Valor 0, Cheque lleva el valor base de Internet)
        {"cuenta": "1435010100", "dc": "C", "linea": "1", "grupo": "1", "producto": "1001", "descripcion": "INTERNET HOGAR", "valor": 0, "cc": 0, "scc": 0, "zona": 1, "iva": 0, "gravada": "N", "base_cheque": val_internet, "cant": 1, "bodega": 1, "forma_pago": 0},
        
        # 7. Costo/Inventario Equipos (OJO: Valor 0, Cheque lleva el valor base de Equipos)
        {"cuenta": "1435010100", "dc": "C", "linea": "1", "grupo": "2", "producto": "2001", "descripcion": "CONCESION DE EQUIPOS", "valor": 0, "cc": 0, "scc": 0, "zona": 1, "iva": 0, "gravada": "N", "base_cheque": val_equipos, "cant": 1, "bodega": 1, "forma_pago": 0},
        
        # 8. Costo/Inventario TV (OJO: Valor 0, Cheque lleva el valor base de TV, Gravada N en esta cuenta)
        {"cuenta": "1435010100", "dc": "C", "linea": "1", "grupo": "4", "producto": "4001", "descripcion": "TELEVISION SUBCONTRATADA", "valor": 0, "cc": 0, "scc": 0, "zona": 1, "iva": 0, "gravada": "N", "base_cheque": val_tv, "cant": 1, "bodega": 1, "forma_pago": 0}
    ]
    
    resultados = []
    for r in rubros:
        resultados.append({
            "CUENTA CONTABLE   (OBLIGATORIO)": r["cuenta"],
            "DÉBITO O CRÉDITO (OBLIGATORIO)": r["dc"],
            "LÍNEA PRODUCTO": r["linea"],
            "GRUPO PRODUCTO": r["grupo"],
            "CÓDIGO PRODUCTO": r["producto"],
            "DESCRIPCIÓN DE LA SECUENCIA": r["descripcion"],
            "VALOR DE LA SECUENCIA   (OBLIGATORIO)": r["valor"],
            "CENTRO DE COSTO": r["cc"],
            "SUBCENTRO DE COSTO": r["scc"],
            "CÓDIGO DE LA ZONA": r["zona"],
            "SECUENCIA GRAVADA O EXCENTA": r["gravada"],
            "FORMA DE PAGO": r["forma_pago"],
            "PORCENTAJE DEL IVA DE LA SECUENCIA": r["iva"],
            "NÚMERO DE CHEQUE": r["base_cheque"],
            "CANTIDAD": r["cant"],
            "CÓDIGO DE LA BODEGA": r["bodega"]
        })
    return resultados

# --- 2. COLUMNAS EXACTAS (91 Campos del Modelo General) ---
COLUMNAS_SIIGO = [
    "TIPO DE COMPROBANTE (OBLIGATORIO)", "CÓDIGO COMPROBANTE  (OBLIGATORIO)", "NÚMERO DE DOCUMENTO",
    "CUENTA CONTABLE   (OBLIGATORIO)", "DÉBITO O CRÉDITO (OBLIGATORIO)", "VALOR DE LA SECUENCIA   (OBLIGATORIO)",
    "AÑO DEL DOCUMENTO", "MES DEL DOCUMENTO", "DÍA DEL DOCUMENTO", "CÓDIGO DEL VENDEDOR",
    "CÓDIGO DE LA CIUDAD", "CÓDIGO DE LA ZONA", "SECUENCIA", "CENTRO DE COSTO", "SUBCENTRO DE COSTO",
    "NIT", "SUCURSAL", "DESCRIPCIÓN DE LA SECUENCIA", "NÚMERO DE CHEQUE", "COMPROBANTE ANULADO",
    "CÓDIGO DEL MOTIVO DE DEVOLUCIÓN", "FORMA DE PAGO", "VALOR DEL CARGO 1 DE LA SECUENCIA",
    "VALOR DEL CARGO 2 DE LA SECUENCIA", "VALOR DEL DESCUENTO 1 DE LA SECUENCIA",
    "VALOR DEL DESCUENTO 2 DE LA SECUENCIA", "VALOR DEL DESCUENTO 3 DE LA SECUENCIA",
    "FACTURA ELECTRÓNICA A DEBITAR/ACREDITAR", "NÚMERO DE FACTURA ELECTRÓNICA A DEBITAR/ACREDITAR",
    "PREFIJO DE ORDER REFERENCE", "CONSECUTIVO DE ORDER REFERENCE", "PREFIJO ORDEN DE ENTREGA",
    "NÚMERO ORDEN DE ENTREGA", "AÑO FECHA DE ORDEN DE ENTREGA", "MES FECHA DE ORDEN DE ENTREGA",
    "DÍA FECHA DE ORDEN DE ENTREGA", "INGRESOS PARA TERCEROS", "FECHA ACTUALIZACIÓN DEL DOCUMENTO",
    "HORA DE ACTUALIZACIÓN DEL DOCUMENTO", "PREFIJO ORDEN DE ENTREGA2", "NÚMERO ORDEN DE ENTREGA2",
    "AÑO FECHA DE ORDEN DE ENTREGA2", "MES FECHA DE ORDEN DE ENTREGA2", "DÍA FECHA DE ORDEN DE ENTREGA2",
    "PREFIJO ORDEN DE ENTREGA3", "NÚMERO ORDEN DE ENTREGA3", "AÑO FECHA DE ORDEN DE ENTREGA3",
    "MES FECHA DE ORDEN DE ENTREGA3", "DÍA FECHA DE ORDEN DE ENTREGA3", "PREFIJO ORDEN DE ENTREGA4",
    "NÚMERO ORDEN DE ENTREGA4", "AÑO FECHA DE ORDEN DE ENTREGA4", "MES FECHA DE ORDEN DE ENTREGA4",
    "DÍA FECHA DE ORDEN DE ENTREGA4", "PREFIJO ORDEN DE ENTREGA5", "NÚMERO ORDEN DE ENTREGA5",
    "AÑO FECHA DE ORDEN DE ENTREGA5", "MES FECHA DE ORDEN DE ENTREGA5", "DÍA FECHA DE ORDEN DE ENTREGA5",
    "PORCENTAJE ALIMENTOS ULTRAPROCESADOS", "VALOR ALIMENTOS ULTRAPROCESADOS", "VALOR BEBIDAS AZUCARADAS",
    "AÑO EXPEDICIÓN FACTURA", "MES EXPEDICIÓN FACTURA", "DÍA EXPEDICIÓN FACTURA", "RUTA DOCUMENTO",
    "PORCENTAJE DEL IVA DE LA SECUENCIA", "VALOR DE IVA DE LA SECUENCIA", "BASE DE RETENCIÓN",
    "BASE PARA CUENTAS MARCADAS COMO RETEIVA", "SECUENCIA GRAVADA O EXCENTA", "PORCENTAJE AIU",
    "BASE IVA AIU", "VALOR TOTAL IMPOCONSUMO DE LA SECUENCIA", "IVA COMO MAYOR VALOR DE LA COMPRA",
    "LÍNEA PRODUCTO", "GRUPO PRODUCTO", "CÓDIGO PRODUCTO", "CANTIDAD", "CANTIDAD DOS",
    "CÓDIGO DE LA BODEGA", "CÓDIGO DE LA UBICACIÓN", "CANTIDAD DE FACTOR DE CONVERSIÓN",
    "OPERADOR DE FACTOR DE CONVERSIÓN", "VALOR DEL FACTOR DE CONVERSIÓN", "TIPO Y COMPROBANTE CRUCE",
    "NÚMERO DE DOCUMENTO CRUCE", "NÚMERO DE VENCIMIENTO", "AÑO VENCIMIENTO DE DOCUMENTO CRUCE",
    "MES VENCIMIENTO DE DOCUMENTO CRUCE", "DÍA VENCIMIENTO DE DOCUMENTO CRUCE"
]

archivo_clientes = st.file_uploader("Sube el archivo 'Lista de Clientes - SEÑAL MÁS.xlsx' o CSV", type=['xlsx', 'csv'])

if archivo_clientes is not None:
    try:
        if archivo_clientes.name.endswith('.csv'):
            df_clientes = pd.read_csv(archivo_clientes) 
        else:
            df_clientes = pd.read_excel(archivo_clientes)
        
        df_clientes = df_clientes.dropna(axis=1, how='all')
        df_clientes.columns = df_clientes.columns.str.strip()
        
        st.success("Archivo cargado correctamente.")
        
        columnas_requeridas = ['Estado', 'Servicio', 'Valor']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_clientes.columns]
        
        if not columnas_faltantes:
            df_clientes['Estado'] = df_clientes['Estado'].astype(str).str.strip().str.upper()
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
                        
                        # Por ahora mandaremos el texto 'CLIENTES'. Si tu Excel tiene una columna con el nombre
                        # del cliente, deberías cambiar "CLIENTES" por row['Nombre_Columna_Nombre']
                        desglose = calcular_rubros(precio_plan, "CLIENTES")
                        
                        secuencia = 1
                        for item in desglose:
                            # 1. Llenamos con vacíos primero
                            fila = {col: "" for col in COLUMNAS_SIIGO}
                            
                            # 2. Inyectamos los 0 exigidos por el Modelo General (EXCEPTO los campos de Cruce)
                            for col in [
                                "SUCURSAL", "CÓDIGO DEL MOTIVO DE DEVOLUCIÓN", 
                                "VALOR DEL CARGO 1 DE LA SECUENCIA", "VALOR DEL CARGO 2 DE LA SECUENCIA",
                                "VALOR DEL DESCUENTO 1 DE LA SECUENCIA", "VALOR DEL DESCUENTO 2 DE LA SECUENCIA",
                                "VALOR DEL DESCUENTO 3 DE LA SECUENCIA", 
                                "NÚMERO DE FACTURA ELECTRÓNICA A DEBITAR/ACREDITAR",
                                "AÑO FECHA DE ORDEN DE ENTREGA", "MES FECHA DE ORDEN DE ENTREGA", "DÍA FECHA DE ORDEN DE ENTREGA",
                                "AÑO FECHA DE ORDEN DE ENTREGA2", "MES FECHA DE ORDEN DE ENTREGA2", "DÍA FECHA DE ORDEN DE ENTREGA2",
                                "AÑO FECHA DE ORDEN DE ENTREGA3", "MES FECHA DE ORDEN DE ENTREGA3", "DÍA FECHA DE ORDEN DE ENTREGA3",
                                "AÑO FECHA DE ORDEN DE ENTREGA4", "MES FECHA DE ORDEN DE ENTREGA4", "DÍA FECHA DE ORDEN DE ENTREGA4",
                                "AÑO FECHA DE ORDEN DE ENTREGA5", "MES FECHA DE ORDEN DE ENTREGA5", "DÍA FECHA DE ORDEN DE ENTREGA5",
                                "PORCENTAJE ALIMENTOS ULTRAPROCESADOS", "VALOR ALIMENTOS ULTRAPROCESADOS", "VALOR BEBIDAS AZUCARADAS",
                                "VALOR DE IVA DE LA SECUENCIA", "BASE PARA CUENTAS MARCADAS COMO RETEIVA", 
                                "VALOR TOTAL IMPOCONSUMO DE LA SECUENCIA",
                                "CÓDIGO DE LA UBICACIÓN", "CANTIDAD DOS",
                                "CANTIDAD DE FACTOR DE CONVERSIÓN", "OPERADOR DE FACTOR DE CONVERSIÓN", "VALOR DEL FACTOR DE CONVERSIÓN"
                            ]:
                                fila[col] = 0
                                
                            # 3. Asignaciones estrictas
                            fila["TIPO DE COMPROBANTE (OBLIGATORIO)"] = "F"
                            fila["CÓDIGO COMPROBANTE  (OBLIGATORIO)"] = "11" 
                            fila["NÚMERO DE DOCUMENTO"] = "" 
                            
                            fila["CUENTA CONTABLE   (OBLIGATORIO)"] = item["CUENTA CONTABLE   (OBLIGATORIO)"]
                            fila["DÉBITO O CRÉDITO (OBLIGATORIO)"] = item["DÉBITO O CRÉDITO (OBLIGATORIO)"]
                            fila["VALOR DE LA SECUENCIA   (OBLIGATORIO)"] = item["VALOR DE LA SECUENCIA   (OBLIGATORIO)"]
                            
                            fila["AÑO DEL DOCUMENTO"] = hoy.year
                            fila["MES DEL DOCUMENTO"] = hoy.month
                            fila["DÍA DEL DOCUMENTO"] = hoy.day
                            fila["CÓDIGO DEL VENDEDOR"] = 1
                            fila["CÓDIGO DE LA CIUDAD"] = 349 
                            
                            fila["SECUENCIA"] = secuencia
                            fila["CENTRO DE COSTO"] = item["CENTRO DE COSTO"]
                            fila["SUBCENTRO DE COSTO"] = item["SUBCENTRO DE COSTO"]
                            fila["CÓDIGO DE LA ZONA"] = item["CÓDIGO DE LA ZONA"]
                            fila["NIT"] = nit_cliente
                            
                            fila["COMPROBANTE ANULADO"] = "N"
                            fila["DESCRIPCIÓN DE LA SECUENCIA"] = item["DESCRIPCIÓN DE LA SECUENCIA"]
                            fila["NÚMERO DE CHEQUE"] = item["NÚMERO DE CHEQUE"]
                            fila["FORMA DE PAGO"] = item["FORMA DE PAGO"]
                            
                            fila["FECHA ACTUALIZACIÓN DEL DOCUMENTO"] = hoy.strftime("%Y%m%d")
                            fila["HORA DE ACTUALIZACIÓN DEL DOCUMENTO"] = hoy.strftime("%H%M%S")
                            
                            fila["PORCENTAJE DEL IVA DE LA SECUENCIA"] = item["PORCENTAJE DEL IVA DE LA SECUENCIA"]
                            fila["SECUENCIA GRAVADA O EXCENTA"] = item["SECUENCIA GRAVADA O EXCENTA"]
                            
                            fila["LÍNEA PRODUCTO"] = item["LÍNEA PRODUCTO"]
                            fila["GRUPO PRODUCTO"] = item["GRUPO PRODUCTO"]
                            fila["CÓDIGO PRODUCTO"] = item["CÓDIGO PRODUCTO"]
                            
                            fila["CANTIDAD"] = item["CANTIDAD"]
                            fila["CÓDIGO DE LA BODEGA"] = item["CÓDIGO DE LA BODEGA"]
                            
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
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_siigo.to_excel(writer, index=False, sheet_name='Movimiento', startrow=4)
                        
                        workbook = writer.book
                        worksheet = writer.sheets['Movimiento']
                        
                        worksheet.write(0, 0, "EMPRESA DE INTERNET Y TELEVISION SEÑAL MAS S.A.S.")
                        worksheet.write(1, 0, "MODELO PARA LA IMPORTACION DE MOVIMIENTO CONTABLE - MODELO GENERAL")
                        worksheet.write(2, 0, f"De :  ENE  1/{hoy.year}   A :  DIC 31/{hoy.year}")
                    
                    st.download_button(
                        label="📥 Descargar Archivo SIIGO (Modelo General)",
                        data=buffer.getvalue(),
                        file_name=f"Plantilla_General_SIIGO_{hoy.strftime('%Y%m%d')}.xlsx",
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
