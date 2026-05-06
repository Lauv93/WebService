from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import xml.etree.ElementTree as ET

app = FastAPI()

# "Base de datos" en memoria
mascotas = []

# Modelo de datos
class Mascota(BaseModel):
    id: int
    nombre: str
    especie: str
    edad: int
    estado: str  # Disponible / Adoptado


# 🔹 CREATE
@app.post("/mascotas/")
def crear_mascota(mascota: Mascota):
    mascotas.append(mascota)
    return {"mensaje": "Mascota creada"}


# 🔹 READ
@app.get("/mascotas/", response_model=List[Mascota])
def obtener_mascotas():
    return mascotas


# 🔹 UPDATE
@app.put("/mascotas/{id}")
def actualizar_mascota(id: int, mascota_actualizada: Mascota):
    for i, m in enumerate(mascotas):
        if m.id == id:
            mascotas[i] = mascota_actualizada
            return {"mensaje": "Mascota actualizada"}
    raise HTTPException(status_code=404, detail="Mascota no encontrada")


# 🔹 DELETE
@app.delete("/mascotas/{id}")
def eliminar_mascota(id: int):
    for i, m in enumerate(mascotas):
        if m.id == id:
            mascotas.pop(i)
            return {"mensaje": "Mascota eliminada"}
    raise HTTPException(status_code=404, detail="Mascota no encontrada")


# 🔹 REPORTE XML
@app.get("/reporte/xml")
def generar_xml():
    root = ET.Element("mascotas")

    total = len(mascotas)
    adoptadas = 0

    for m in mascotas:
        mascota_xml = ET.SubElement(root, "mascota")

        ET.SubElement(mascota_xml, "id").text = str(m.id)
        ET.SubElement(mascota_xml, "nombre").text = m.nombre
        ET.SubElement(mascota_xml, "especie").text = m.especie
        ET.SubElement(mascota_xml, "edad").text = str(m.edad)
        ET.SubElement(mascota_xml, "estado").text = m.estado

        if m.estado.lower() == "adoptado":
            adoptadas += 1

    porcentaje = (adoptadas / total * 100) if total > 0 else 0

    resumen = ET.SubElement(root, "resumen")
    ET.SubElement(resumen, "total").text = str(total)
    ET.SubElement(resumen, "adoptadas").text = str(adoptadas)
    ET.SubElement(resumen, "porcentaje").text = f"{porcentaje:.2f}%"

    return ET.tostring(root, encoding="unicode")