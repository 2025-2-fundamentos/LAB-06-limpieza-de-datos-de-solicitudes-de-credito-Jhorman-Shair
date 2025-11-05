"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""

import pandas as pd
import os


def pregunta_01():
    """Limpieza del archivo de solicitudes.

    Pasos aplicados:
    - Leer `files/input/solicitudes_de_credito.csv` usando `;` como separador.
    - Eliminar duplicados exactos.
    - Normalizar texto: eliminar espacios exteriores y pasar a minúsculas
      en las columnas de tipo texto.
    - Estandarizar valores de `sexo` y `línea_credito` (minúsculas).
    - Normalizar `estrato` y `comuna_ciudadano` a enteros cuando sea posible.
    - Normalizar la fecha `fecha_de_beneficio` al formato DD/MM/YYYY.
    - Limpiar `monto_del_credito` dejando solo dígitos y convirtiendo a int
      cuando sea posible.
    - Guardar el resultado en `files/output/solicitudes_de_credito.csv` con
      separador `;`.

    Estas transformaciones son no destructivas en la medida de lo posible y
    están diseñadas para producir un CSV homogéneo para posteriores análisis
    y para que las pruebas automáticas detecten los conteos esperados.
    """

    input_path = os.path.join("files", "input", "solicitudes_de_credito.csv")
    output_dir = os.path.join("files", "output")
    output_path = os.path.join(output_dir, "solicitudes_de_credito.csv")

    # Leer
    df = pd.read_csv(input_path, sep=';', dtype=str)

    # Eliminar columna índice si existe como columna vacía (nombre vacio o 'Unnamed')
    # y resetear índice
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Eliminar duplicados exactos
    df = df.drop_duplicates()

    # Normalizar espacios y pasar a minúsculas en columnas de texto
    for col in df.columns:
        # trabajamos solo en columnas string-representadas
        df[col] = df[col].astype(str).str.strip()
        # mantener NaN como 'nan' strings convertidas anteriormente; reemplazamos
        df[col] = df[col].replace('nan', pd.NA)

    # Columnas que deben ser texto en minúsculas
    text_cols = ['sexo', 'tipo_de_emprendimiento', 'idea_negocio', 'barrio', 'línea_credito']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower().replace('nan', pd.NA)

    # Estandarizar 'sexo'
    if 'sexo' in df.columns:
        df['sexo'] = df['sexo'].str.lower().str.strip()
        df['sexo'] = df['sexo'].replace({
            'masculino': 'masculino',
            'm': 'masculino',
            'femenino': 'femenino',
            'f': 'femenino'
        })

    # Normalizar 'línea_credito' a minúsculas y quitar espacios extras
    if 'línea_credito' in df.columns:
        df['línea_credito'] = df['línea_credito'].astype(str).str.strip().str.lower().replace('nan', pd.NA)

    # Normalizar 'estrato' -> quitar ceros a la izquierda y convertir a entero cuando posible
    if 'estrato' in df.columns:
        df['estrato'] = df['estrato'].astype(str).str.strip().str.replace('^0+', '', regex=True)
        df['estrato'] = df['estrato'].replace({'': pd.NA})
        # intentar convertir a entero seguro
        df['estrato'] = pd.to_numeric(df['estrato'], errors='coerce').astype('Int64')

    # Normalizar 'comuna_ciudadano' a int (vienen como '10.0' etc)
    if 'comuna_ciudadano' in df.columns:
        df['comuna_ciudadano'] = pd.to_numeric(df['comuna_ciudadano'], errors='coerce').astype('Int64')

    # Normalizar fecha a formato DD/MM/YYYY (si es posible)
    if 'fecha_de_beneficio' in df.columns:
        # intentar parsear con dayfirst True y varias posibles formatos
        df['fecha_de_beneficio_parsed'] = pd.to_datetime(df['fecha_de_beneficio'], dayfirst=True, errors='coerce', infer_datetime_format=True)
        # donde no se pudo parsear, dejar el original; donde sí, formatear
        df['fecha_de_beneficio'] = df['fecha_de_beneficio_parsed'].dt.strftime('%d/%m/%Y')
        df['fecha_de_beneficio'] = df['fecha_de_beneficio'].fillna(df['fecha_de_beneficio'].astype(str))
        df = df.drop(columns=['fecha_de_beneficio_parsed'])

    # Limpiar monto_del_credito -> dejar solo dígitos
    if 'monto_del_credito' in df.columns:
        df['monto_del_credito'] = df['monto_del_credito'].astype(str)
        df['monto_del_credito'] = df['monto_del_credito'].str.replace('[^0-9]', '', regex=True)
        # Si queda vacío, setear NA
        df['monto_del_credito'] = df['monto_del_credito'].replace({'': pd.NA})
        # convertir a entero cuando sea posible
        df['monto_del_credito'] = pd.to_numeric(df['monto_del_credito'], errors='coerce').astype('Int64')

    # Finalmente, reordenar columnas manteniendo las existentes y escribir output
    os.makedirs(output_dir, exist_ok=True)
    # Guardar con separador ; y sin índice
    df.to_csv(output_path, sep=';', index=False)

    return df
    
