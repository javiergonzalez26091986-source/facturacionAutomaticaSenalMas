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
    # Nota: Los porcentajes están extraídos de tu archivo CALCULO SEÑAL MAS.
    # Ajusta estos factores si el total de la suma difiere del 100% de la factura.
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
        # Leer el archivo. SIN saltar la primera fila para no perder los encabezados
        if archivo_clientes.name.endswith('.csv'):
            df_clientes = pd.read_csv(archivo_clientes) 
        else:
            df_clientes = pd.read_excel(archivo_clientes)
        
        # Limpiar columnas vacías e identificar las reales
        df_clientes = df_clientes.dropna(axis=1, how='all')
        
        # Buenas prácticas: Eliminar posibles espacios en blanco al inicio o final en los nombres de las columnas
        df_clientes.columns = df_clientes.columns.str.strip()
        
        st.success("Archivo de clientes cargado correctamente.")
        
        # Filtrar solo clientes Activos
        if 'Estado' in df_clientes.columns:
            df_activos = df_clientes[df_clientes['Estado'].str.upper() == 'ACTIVO']
            st.info(f"Se encontraron {len(df_activos)} clientes activos para facturar.")
            
            if st.button("Procesar y Generar Archivo SIIGO"):
                filas_siigo = []
                hoy = datetime.now()
                
                # Iterar sobre cada cliente activo
                for index, row in df_activos.iterrows():
                    # Asegurarse de que el NIT y el Precio existan
                    nit_cliente = row['Servicio'] # En tu archivo, la cédula está en la columna 'Servicio'
                    precio_plan = float(row.iloc[-1]) # Asumiendo que el precio es la última columna
                    
                    # Calcular la división de valores
                    desglose = calcular_rubros(precio_plan)
                    
                    # Generar una fila para SIIGO por cada rubro
                    secuencia = 1
                    for item in desglose:
                        fila = {
                            "TIPO DE COMPROBANTE (OBLIGATORIO)": "Factura", # Ajustar según SIIGO
                            "CÓDIGO COMPROBANTE  (OBLIGATORIO)": "1", # Ajustar según SIIGO
                            "NÚMERO DE DOCUMENTO": "", # SIIGO lo suele autogenerar si va vacío
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
                            "CÓDIGO DE LA BODEGA (OBLIGATORIO)": "1" # Ajustar si manejan bodegas
                        }
                        filas_siigo.append(fila)
                        secuencia += 1
                
                # Crear DataFrame final
                df_siigo = pd.DataFrame(filas_siigo)
                
                # Mostrar vista previa
                st.write("Vista previa de los datos a exportar:")
                st.dataframe(df_siigo.head(10))
                
                # Exportar a Excel en memoria para descarga
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_siigo.to_excel(writer, index=False, sheet_name='Movimiento')
                
                st.download_button(
                    label="📥 Descargar Archivo para SIIGO",
                    data=buffer.getvalue(),
                    file_name=f"movimiento_siigo_{hoy.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.ms-excel"
                )
        else:
            st.error("No se encontró la columna 'Estado' en el archivo cargado. Verifica el formato.")
            
    except Exception as e:
        st.error(f"Hubo un error procesando el archivo: {e}")
