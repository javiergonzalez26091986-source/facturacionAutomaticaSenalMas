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
        # Leer el archivo sin saltar la primera fila
        if archivo_clientes.name.endswith('.csv'):
            df_clientes = pd.read_csv(archivo_clientes) 
        else:
            df_clientes = pd.read_excel(archivo_clientes)
        
        # Limpiar columnas vacías e identificar las reales
        df_clientes = df_clientes.dropna(axis=1, how='all')
        
        # Buenas prácticas: Eliminar posibles espacios en blanco en los nombres de las columnas
        df_clientes.columns = df_clientes.columns.str.strip()
        
        st.success("Archivo de clientes cargado correctamente.")
        
        # Verificar que exista la columna 'Estado'
        if 'Estado' in df_clientes.columns:
            
            # Limpiar espacios invisibles y convertir a mayúsculas para evitar errores tipográficos
            df_clientes['Estado'] = df_clientes['Estado'].astype(str).str.strip().str.upper()
            
            # Filtrar clientes Activos Y Suspendidos
            estados_a_facturar = ['ACTIVO', 'SUSPENDIDO']
            df_a_facturar = df_clientes[df_clientes['Estado'].isin(estados_a_facturar)]
            
            st.info(f"Se encontraron {len(df_a_facturar)} clientes (Activos y Suspendidos) para facturar.")
            
            st.write("---")
            st.write("⚙️ **Configuración de Datos**")
            
            # Selector de columnas para evitar que el programa se confunda con celdas lejanas
            col_nit = st.selectbox("Selecciona la columna del Cédula/NIT:", df_clientes.columns, index=list(df_clientes.columns).index('Servicio') if 'Servicio' in df_clientes.columns else 0)
            col_precio = st.selectbox("Selecciona la columna del Valor a Facturar (Precio):", df_clientes.columns, index=len(df_clientes.columns)-1)
            
            if st.button("Procesar y Generar Archivo SIIGO"):
                filas_siigo = []
                hoy = datetime.now()
                errores = [] # Lista para guardar los clientes problemáticos
                
                # Iterar sobre cada cliente a facturar
                for index, row in df_a_facturar.iterrows():
                    nit_cliente = row[col_nit]
                    estado_cliente = row['Estado']
                    
                    try:
                        # Extraer y asegurar que el precio sea numérico
                        valor_celda = str(row[col_precio]).replace('$', '').replace(',', '').strip()
                        precio_plan = float(valor_celda)
                        
                        desglose = calcular_rubros(precio_plan)
                        
                        # Generar una fila para SIIGO por cada rubro
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
                        # Si falla un cliente, guardamos el error pero el programa continúa
                        errores.append(f"Cédula/NIT {nit_cliente} (Estado: {estado_cliente}): revisa la celda de precio (Valor actual: {row[col_precio]})")
                
                # Mostrar alertas si hubo clientes omitidos por error de formato en el precio
                if errores:
                    st.warning(f"⚠️ Se omitieron {len(errores)} clientes por formato inválido en su precio. Revisa sus datos:")
                    with st.expander("Ver clientes omitidos"):
                        for err in errores:
                            st.write(err)
                
                # Crear DataFrame final si hay filas procesadas
                if filas_siigo:
                    df_siigo = pd.DataFrame(filas_siigo)
                    
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
                    st.error("No se generó ninguna fila válida. Verifica los datos de origen.")
                    
        else:
            st.error("No se encontró la columna 'Estado' en el archivo cargado. Verifica el formato.")
            
    except Exception as e:
        st.error(f"Hubo un error general procesando el archivo: {e}")
