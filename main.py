from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import xml.etree.ElementTree as ET

app = FastAPI()

# Conexión Supabase
DATABASE_URL = os.getenv("DATABASE_URL")


# Función para conectarse
def get_conn():
    return psycopg2.connect(DATABASE_URL)


# Modelo
class Mascota(BaseModel):
    id: int
    nombre: str
    especie: str
    edad: int
    estado: str


# Inicio
@app.get("/")
def inicio():
    return {"mensaje": "API de mascotas funcionando con Supabase"}


# CREATE
@app.post("/mascotas/")
def crear_mascota(mascota: Mascota):

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM mascotas WHERE id=%s",
        (mascota.id,)
    )

    existe = cursor.fetchone()

    if existe:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="La mascota ya existe"
        )

    cursor.execute("""
        INSERT INTO mascotas
        (id,nombre,especie,edad,estado)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        mascota.id,
        mascota.nombre,
        mascota.especie,
        mascota.edad,
        mascota.estado
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return {"mensaje":"Mascota creada correctamente"}


# READ
@app.get("/mascotas/")
def obtener_mascotas():

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM mascotas"
    )

    datos = cursor.fetchall()

    resultado=[]

    for d in datos:

        resultado.append({
            "id":d[0],
            "nombre":d[1],
            "especie":d[2],
            "edad":d[3],
            "estado":d[4]
        })

    cursor.close()
    conn.close()

    return resultado


# UPDATE
@app.put("/mascotas/{id}")
def actualizar_mascota(id:int, mascota:Mascota):

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE mascotas
    SET nombre=%s,
        especie=%s,
        edad=%s,
        estado=%s
    WHERE id=%s
    """,(
        mascota.nombre,
        mascota.especie,
        mascota.edad,
        mascota.estado,
        id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return {"mensaje":"Mascota actualizada"}


# DELETE
@app.delete("/mascotas/{id}")
def eliminar_mascota(id:int):

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM mascotas WHERE id=%s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {"mensaje":"Mascota eliminada"}


# XML
@app.get("/reporte/xml")
def generar_xml():

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM mascotas"
    )

    datos=cursor.fetchall()

    root=ET.Element("mascotas")

    total=len(datos)
    adoptadas=0

    for d in datos:

        mascota_xml=ET.SubElement(
            root,
            "mascota"
        )

        ET.SubElement(
            mascota_xml,
            "id"
        ).text=str(d[0])

        ET.SubElement(
            mascota_xml,
            "nombre"
        ).text=d[1]

        ET.SubElement(
            mascota_xml,
            "especie"
        ).text=d[2]

        ET.SubElement(
            mascota_xml,
            "edad"
        ).text=str(d[3])

        ET.SubElement(
            mascota_xml,
            "estado"
        ).text=d[4]

        if d[4].lower()=="adoptado":
            adoptadas+=1

    porcentaje=(
        adoptadas/total*100
        if total>0 else 0
    )

    resumen=ET.SubElement(
        root,
        "resumen"
    )

    ET.SubElement(
        resumen,
        "total_mascotas"
    ).text=str(total)

    ET.SubElement(
        resumen,
        "mascotas_adoptadas"
    ).text=str(adoptadas)

    ET.SubElement(
        resumen,
        "porcentaje_adoptadas"
    ).text=f"{porcentaje:.2f}%"

    cursor.close()
    conn.close()

    return ET.tostring(
        root,
        encoding="unicode"
    )