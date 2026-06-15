import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="Facturación en Bloque - Señal Más", layout="wide")

st.title("Generador de Facturación en Bloque SIIGO 🚀")
st.write("Sube la lista de clientes para generar automáticamente el archivo de movimiento contable.")

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
            "VALOR DE LA SECUENCIA   (OBLIGATORIO)": round(total * r["factor"], 2)
        })
    return resultados

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
                        
                        # ESTRUCTURA EXACTA DE LA PLANTILLA SIIGO (34 COLUMNAS)
                        secuencia = 1
                        for item in desglose:
                            fila = {
                                "TIPO DE COMPROBANTE (OBLIGATORIO)": "Factura", # Revisa si SIIGO acepta "Factura" aquí o requiere un código contable
                                "CÓDIGO COMPROBANTE  (OBLIGATORIO)": "1",
                                "NÚMERO DE DOCUMENTO": "",
                                "AÑO DEL DOCUMENTO (OBLIGATORIO)": hoy.year,
                                "MES DEL DOCUMENTO (OBLIGATORIO)": hoy.month,
                                "DÍA DEL DOCUMENTO (OBLIGATORIO)": hoy.day,
                                "NIT (OBLIGATORIO)": nit_cliente,
                                "SUCURSAL (OBLIGATORIO)": "0",
                                "CÓDIGO DEL VENDEDOR": "1",
                                "SECUENCIA (OBLIGATORIO)": secuencia,
                                "CUENTA CONTABLE (OBLIGATORIO)": "", # Vacío porque usarás Producto
                                "CENTRO DE COSTO (OBLIGATORIO)": "1",
                                "SUBCENTRO DE COSTO (OBLIGATORIO)": "1",
                                "DESCRIPCIÓN DE LA SECUENCIA": item["DESCRIPCIÓN DE LA SECUENCIA"],
                                "TIPO / CRUZAR CON:": "",
                                "NRO DEL COMPROBANTE / CRUZAR CON:": "",
                                "VENCIMIENTO AÑO / CRUZAR CON:": "",
                                "VENCIMIENTO MES / CRUZAR CON:": "",
                                "VENCIMIENTO DÍA / CRUZAR CON:": "",
                                "AÑO DE VENCIMIENTO": "",
                                "MES DE VENCIMIENTO": "",
                                "DÍA DE VENCIMIENTO": "",
                                "CÓDIGO DE LA BODEGA (OBLIGATORIO)": "1",
                                "CÓDIGO PRODUCTO (OBLIGATORIO)": item["CÓDIGO PRODUCTO (OBLIGATORIO)"],
                                "CANTIDAD (OBLIGATORIO)": "1",
                                "PRECIO UNITARIO": "",
                                "NIT CRUZAR CON": "",
                                "DESCUENTO/RECARGO 1": "",
                                "PORCENTAJE": "",
                                "DESCUENTO/RECARGO 2": "",
                                "PORCENTAJE DESCUENTO/RECARGO 2": "",
                                "DESCUENTO/RECARGO 3": "",
                                "PORCENTAJE DESCUENTO/RECARGO 3": "",
                                "VALOR DE LA SECUENCIA   (OBLIGATORIO)": item["VALOR DE LA SECUENCIA   (OBLIGATORIO)"]
                            }
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
                    df_siigo = pd.DataFrame(filas_siigo)
                    
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
