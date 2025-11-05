"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""

import pandas as pd
import os


import os
import unicodedata
import pandas as pd


def pregunta_01():
    # Rutas de entrada y salida
    input_path = "files/input/solicitudes_de_credito.csv"
    output_dir = "files/output"
    output_path = os.path.join(output_dir, "solicitudes_de_credito.csv")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Lectura del archivo original
    # ------------------------------------------------------------------
    df = pd.read_csv(input_path, sep=";")

    # Eliminar columna índice innecesaria si existe (tipo 'Unnamed: 0')
    cols_lower = {c.lower(): c for c in df.columns}
    if "unnamed: 0" in cols_lower:
        df = df.drop(columns=[cols_lower["unnamed: 0"]])

    # ------------------------------------------------------------------
    # 2. Limpieza de monto_del_credito (antes de convertir a numérico)
    # ------------------------------------------------------------------
    if "monto_del_credito" in df.columns:
        monto = df["monto_del_credito"].astype(str).str.strip()

        # Quitar símbolo de moneda y espacios
        monto = monto.str.replace("$", "", regex=False)
        monto = monto.str.replace(" ", "", regex=False)

        # Quitar separadores de miles
        monto = monto.str.replace(",", "", regex=False)

        # Quitar parte decimal ".00" en los casos que vienen así
        monto = monto.str.replace(".00", "", regex=False)

        # Convertir a numérico
        df["monto_del_credito"] = pd.to_numeric(monto, errors="coerce")

    # ------------------------------------------------------------------
    # 3. Normalización de texto en columnas categóricas
    # ------------------------------------------------------------------
    text_cols = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]

    for col in text_cols:
        if col in df.columns:
            s = df[col].astype(str).str.strip().str.lower()

            # Quitar acentos / tildes
            s = s.apply(
                lambda x: "".join(
                    c
                    for c in unicodedata.normalize("NFKD", x)
                    if not unicodedata.combining(c)
                )
            )

            # Reemplazar ., _, - por espacio
            s = s.str.replace(r"[._\-]+", " ", regex=True)

            # Colapsar espacios múltiples
            s = s.str.replace(r"\s+", " ", regex=True).str.strip()

            df[col] = s

    # Quitar prefijo "barrio " en nombres de barrios
    if "barrio" in df.columns:
        df["barrio"] = (
            df["barrio"]
            .str.replace(r"^barrio\s+", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # Homogeneizar sexo (m / f -> masculino / femenino)
    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].replace(
            {
                "m": "masculino",
                "f": "femenino",
            }
        )

    # Algunas normalizaciones específicas para línea de crédito
    if "línea_credito" in df.columns:
        df["línea_credito"] = df["línea_credito"].replace(
            {
                "micro credito": "microcredito",
                "micro creditos": "microcredito",
                "micro empresar ial": "microempresarial",
                "micro empresaria l": "microempresarial",
                "microempresa rial": "microempresarial",
            }
        ).str.replace(r"\s+", " ", regex=True).str.strip()

    # ------------------------------------------------------------------
    # 4. Conversión de tipos (fechas y numéricos)
    # ------------------------------------------------------------------
    # Fecha
    if "fecha_de_beneficio" in df.columns:
        df["fecha_de_beneficio"] = pd.to_datetime(
            df["fecha_de_beneficio"], dayfirst=True, errors="coerce"
        )

    # Numéricos
    for num_col in ["estrato", "comuna_ciudadano"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    # ------------------------------------------------------------------
    # 5. Eliminación de registros con datos faltantes en columnas clave
    # ------------------------------------------------------------------
    subset_na = []
    for col in ["tipo_de_emprendimiento", "barrio", "monto_del_credito", "fecha_de_beneficio"]:
        if col in df.columns:
            subset_na.append(col)

    if subset_na:
        df = df.dropna(subset=subset_na)

    # ------------------------------------------------------------------
    # 6. Eliminación de duplicados después de toda la estandarización
    # ------------------------------------------------------------------
    df = df.drop_duplicates()

    # ------------------------------------------------------------------
    # 7. Formateo final y escritura del archivo limpio
    # ------------------------------------------------------------------
    if "fecha_de_beneficio" in df.columns:
        df["fecha_de_beneficio"] = df["fecha_de_beneficio"].dt.strftime("%Y-%m-%d")

    # Ordenar filas para dejar salida estable (no afecta los asserts)
    sort_cols = [c for c in ["fecha_de_beneficio", "barrio", "idea_negocio"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols, kind="stable")

    # Guardar CSV limpio con separador ';'
    df.to_csv(output_path, index=False, sep=";")

    # La función puede devolver el DataFrame por comodidad (no es obligatorio para los tests)
    return df
