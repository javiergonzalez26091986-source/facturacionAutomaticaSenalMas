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
            # Limpiar espacios invisibles y unificar mayúsculas en el Estado
            df_clientes['Estado'] = df_clientes['Estado'].astype(str).str.strip().str.upper()
            
            # Filtrar clientes Activos y Suspendidos
            estados_a_facturar = ['ACTIVO', 'SUSPENDIDO']
            df_a_facturar = df_clientes[df_clientes['Estado'].isin(estados_a_facturar)]
            
            st.info(f"Procesando {len(df_a_facturar)} clientes (Activos y Suspendidos).")
            
            # Proceso automático (sin botones intermedios si lo deseas, o con botón para confirmar)
            if st.button("Generar Archivo SIIGO"):
                filas_siigo = []
                hoy = datetime.now()
                errores = [] 
                
                # Barra de progreso para feedback visual (opcional pero recomendado)
                barra_progreso = st.progress(0)
                total_clientes = len(df_a_facturar)
                
                for index, (i, row) in enumerate(df_a_facturar.iterrows()):
                    nit_cliente = row['Servicio']
                    estado_cliente = row['Estado']
                    
                    try:
                        # Limpiar y convertir el valor de la columna 'Valor'
                        # Maneja casos donde la celda esté vacía (NaN)
                        if pd.isna(row['Valor']):
                            raise ValueError("Celda vacía")
                            
                        valor_celda = str(row['Valor']).replace('$', '').replace(',', '').strip()
                        precio_plan = float(valor_celda)
                        
                        if precio_plan <= 0:
                            raise ValueError("Valor cero o negativo")
                        
                        desglose = calcular_rubros(precio_plan)
                        
                        # Generar filas para SIIGO
                        secuencia = 1
                        for item in desglose:
                            fila = {
                                "TIPO DE COMPROBANTE (OBLIGATORIO)": "Factura", 
                                "CÓDIGO COMPROBANTE  (OBLIGATORIO)": "1", 
                                "NÚMERO DE DOCUMENTO": "", 
                                "VALOR DE LA SECUENCIA   (OBLIGATORIO)": item["VALOR DE LA SECUENCIA   (OBLIGATORIO)"],
                                "AÑO DEL DOCUMENTO (OBLIGATORIO)": hoy.year,
                                "MES DEL DOCUMENTO (OBLIGATORIO)": hoy.month,
                                "DÍA DEL DOCUMENTO (OBLIGATORIO)": hoy.day,
                                "CÓDIGO DEL VENDEDOR": "1", 
                                "SECUENCIA (OBLIGATORIO)": secuencia,
                                "CENTRO DE COSTO (OBLIGATORIO)": "1", 
                                "SUBCENTRO DE COSTO (OBLIGATORIO)": "1", 
                                "NIT (OBLIGATORIO)": nit_cliente,
                                "SUCURSAL (OBLIGATORIO)": "0", 
                                "DESCRIPCIÓN DE LA SECUENCIA": item["DESCRIPCIÓN DE LA SECUENCIA"],
                                "CÓDIGO PRODUCTO (OBLIGATORIO)": item["CÓDIGO PRODUCTO (OBLIGATORIO)"],
                                "CANTIDAD (OBLIGATORIO)": "1",
                                "CÓDIGO DE LA BODEGA (OBLIGATORIO)": "1"
                            }
                            filas_siigo.append(fila)
                            secuencia += 1
                            
                    except Exception as e:
                        # Capturar errores puntuales de clientes con datos corruptos
                        errores.append(f"NIT {nit_cliente} (Estado: {estado_cliente}) - Valor inválido o vacío: '{row['Valor']}'")
                    
                    # Actualizar barra de progreso
                    barra_progreso.progress((index + 1) / total_clientes)
                
                # Mostrar resultados
                if errores:
                    st.warning(f"⚠️ Se omitieron {len(errores)} clientes por no tener un 'Valor' válido. Revisa sus datos en tu Excel:")
                    with st.expander("Ver detalle de clientes omitidos"):
                        for err in errores:
                            st.write(err)
                
                if filas_siigo:
                    df_siigo = pd.DataFrame(filas_siigo)
                    
                    st.success("¡Archivo generado con éxito!")
                    st.dataframe(df_siigo.head(10))
                    
                    # Generar Excel en memoria
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_siigo.to_excel(writer, index=False, sheet_name='Movimiento')
                    
                    st.download_button(
                        label="📥 Descargar Archivo para SIIGO",
                        data=buffer.getvalue(),
                        file_name=f"movimiento_siigo_{hoy.strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.ms-excel",
                        type="primary" # Resalta el botón
                    )
                else:
                    st.error("No se generó ninguna factura. Verifica los valores en tu archivo Excel.")
                    
        else:
            st.error(f"⚠️ Error de formato: Tu archivo de Excel debe contener obligatoriamente las columnas: **{', '.join(columnas_faltantes)}**.")
            st.info("💡 Asegúrate de nombrar la columna del precio exactamente como 'Valor'.")
            
    except Exception as e:
        st.error(f"Hubo un error general procesando el archivo: {e}")
