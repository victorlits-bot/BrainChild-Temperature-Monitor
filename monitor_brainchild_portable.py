
import csv
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from serial.tools import list_ports
import matplotlib
matplotlib.use("TkAgg")
import time
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Button

from pymodbus.client import ModbusSerialClient

from openpyxl import Workbook
from openpyxl.chart import ScatterChart, Series, Reference
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

# ============================================
# CONFIGURACION DEL EQUIPO
# ============================================

PUERTO = None
BAUDRATE = 9600
NODO = 1

INTERVALO_LECTURA = 1.0       # segundos
INTERVALO_AUTOGUARDADO = 3600 # una hora
VENTANA_GRAFICO = 60          # minutos

def seleccionar_conexion():
    root = tk.Tk()
    root.title("BrainChild Monitor - Conexion")
    root.resizable(False, False)
    panel = ttk.Frame(root, padding=20)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="BrainChild PR1006", font=("Segoe UI", 17, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
    ttk.Label(panel, text="9600 baudios | Modbus 1 | 8N1").grid(row=1, column=0, columnspan=2, sticky="w", pady=8)
    combo = ttk.Combobox(panel, state="readonly", width=52)
    combo.grid(row=2, column=0, sticky="ew", pady=8)
    ports = []
    def actualizar_puertos():
        ports[:] = sorted(list_ports.comports(), key=lambda x: x.device)
        combo["values"] = [f"{x.device} - {x.description}" for x in ports]
        if ports:
            combo.current(next((i for i,x in enumerate(ports) if "XR21" in x.description.upper()), 0))
        else:
            combo.set("")
    ttk.Button(panel, text="Actualizar", command=actualizar_puertos).grid(row=2, column=1, padx=8)
    base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
    carpeta = tk.StringVar(value=str(base / "Registros"))
    ttk.Label(panel, text="Carpeta de registros").grid(row=3, column=0, sticky="w")
    ttk.Entry(panel, textvariable=carpeta, width=55).grid(row=4, column=0, sticky="ew")
    def elegir():
        ruta = filedialog.askdirectory(parent=root)
        if ruta: carpeta.set(ruta)
    ttk.Button(panel, text="Examinar", command=elegir).grid(row=4, column=1, padx=8)
    resultado = []
    def conectar():
        i = combo.current()
        if i < 0:
            messagebox.showwarning("Puerto", "Conecte el adaptador USB y actualice la lista.", parent=root)
            return
        puerto = ports[i].device
        prueba = ModbusSerialClient(port=puerto, baudrate=BAUDRATE, bytesize=8, parity="N", stopbits=1, timeout=2, retries=0)
        try:
            if not prueba.connect(): raise RuntimeError("No se pudo abrir el puerto")
            r = prueba.read_input_registers(address=1, count=3, device_id=NODO)
            if r.isError() or len(r.registers) != 3: raise RuntimeError("Sin respuesta valida del PR1006")
            if not carpeta.get().strip(): raise RuntimeError("Seleccione una carpeta")
            ruta = Path(carpeta.get()).expanduser().resolve()
            ruta.mkdir(parents=True, exist_ok=True)
            import tempfile
            with tempfile.NamedTemporaryFile(dir=ruta): pass
            resultado.extend([puerto, ruta])
        except Exception as e:
            messagebox.showerror("Conexion", f"{puerto}: {e}\nCierre RealTimeViewer y revise el cable y el puerto.", parent=root)
        finally:
            prueba.close()
        if resultado: root.destroy()
    ttk.Button(panel, text="Conectar e iniciar monitoreo", command=conectar).grid(row=5, column=0, columnspan=2, pady=18)
    actualizar_puertos()
    root.mainloop()
    if not resultado: raise SystemExit(0)
    return resultado

PUERTO, CARPETA = seleccionar_conexion()

# El ejecutable sin consola conserva los mensajes en un archivo.
if getattr(sys, "frozen", False):
    sys.stdout = sys.stderr = open(CARPETA / "monitor.log", "a", encoding="utf-8", buffering=1)

SESION = datetime.now().strftime("%Y%m%d_%H%M%S")

ARCHIVO_CSV = CARPETA / f"temperaturas_{SESION}.csv"

# ============================================
# CONEXION MODBUS
# ============================================

cliente = ModbusSerialClient(
    port=PUERTO,
    baudrate=BAUDRATE,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2
)

def convertir_temperatura(valor):
    # Escala validada con las lecturas del PR1006
    return -200 + (valor * 1050 / 65535)

# ============================================
# VARIABLES DE MONITOREO
# ============================================

inicio = time.monotonic()
proxima_lectura = inicio
proximo_guardado = inicio + INTERVALO_AUTOGUARDADO

tiempos = []
temperaturas = [[], [], []]
registros = []

finalizado = False
exportando = False

# ============================================
# CREAR CSV
# ============================================

with open(
    ARCHIVO_CSV,
    "w",
    newline="",
    encoding="utf-8-sig"
) as archivo:

    escritor = csv.writer(archivo, delimiter=";")
    escritor.writerow([
        "Fecha",
        "Hora",
        "Tiempo (min)",
        "AI1 (C)",
        "AI2 (C)",
        "AI3 (C)"
    ])

# ============================================
# EXPORTAR EXCEL
# ============================================

def crear_excel(ruta, datos):

    libro = Workbook()

    hoja = libro.active
    hoja.title = "Mediciones"

    encabezados = [
        "Fecha",
        "Hora",
        "Tiempo (min)",
        "AI1 (C)",
        "AI2 (C)",
        "AI3 (C)"
    ]

    hoja.append(encabezados)

    for registro in datos:
        hoja.append(registro)

    # Encabezados
    for celda in hoja[1]:
        celda.font = Font(
            bold=True,
            color="FFFFFF"
        )
        celda.fill = PatternFill(
            "solid",
            fgColor="17365D"
        )

    for columna in range(1, 7):
        letra = get_column_letter(columna)
        hoja.column_dimensions[letra].width = 19

    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions

    for fila in hoja.iter_rows(
        min_row=2,
        min_col=3,
        max_col=6
    ):
        for celda in fila:
            celda.number_format = "0.000"

    # ========================================
    # GRAFICO EXCEL
    # ========================================

    if datos:

        grafico = ScatterChart()

        grafico.title = (
            "Monitoreo de temperaturas BrainChild"
        )
        grafico.x_axis.title = (
            "Tiempo transcurrido (minutos)"
        )
        grafico.y_axis.title = "Temperatura (C)"

        grafico.scatterStyle = "line"
        grafico.style = 13
        grafico.width = 26
        grafico.height = 15

        x = Reference(
            hoja,
            min_col=3,
            min_row=2,
            max_row=hoja.max_row
        )

        colores_excel = [
            "0070C0",
            "00A050",
            "FF0000"
        ]

        for indice, columna in enumerate([4, 5, 6]):

            y = Reference(
                hoja,
                min_col=columna,
                min_row=2,
                max_row=hoja.max_row
            )

            serie = Series(
                y,
                x,
                title=f"AI{indice + 1}"
            )

            serie.graphicalProperties.line.solidFill = (
                colores_excel[indice]
            )
            serie.graphicalProperties.line.width = 22000

            grafico.series.append(serie)

        grafico.x_axis.scaling.min = 0
        grafico.x_axis.majorUnit = 5

        hoja.add_chart(grafico, "H3")

    # ========================================
    # RESUMEN ESTADISTICO
    # ========================================

    resumen = libro.create_sheet("Resumen")

    resumen.append([
        "Sensor",
        "Minimo (C)",
        "Maximo (C)",
        "Promedio (C)",
        "Lecturas"
    ])

    for i in range(3):

        valores = [
            registro[i + 3]
            for registro in datos
        ]

        if valores:
            resumen.append([
                f"AI{i + 1}",
                min(valores),
                max(valores),
                sum(valores) / len(valores),
                len(valores)
            ])

    for celda in resumen[1]:
        celda.font = Font(
            bold=True,
            color="FFFFFF"
        )
        celda.fill = PatternFill(
            "solid",
            fgColor="17365D"
        )

    for columna in range(1, 6):
        letra = get_column_letter(columna)
        resumen.column_dimensions[letra].width = 20

    for fila in resumen.iter_rows(
        min_row=2,
        min_col=2,
        max_col=4
    ):
        for celda in fila:
            celda.number_format = "0.00"

    libro.save(ruta)

# ============================================
# CONFIGURAR GRAFICO EN TIEMPO REAL
# ============================================

fig, ax = plt.subplots(figsize=(12, 7))
fig.canvas.manager.set_window_title(f"BrainChild Monitor - {PUERTO}")

fig.subplots_adjust(
    top=0.79,
    bottom=0.22,
    left=0.10,
    right=0.95
)

colores = ["blue", "green", "red"]

lineas = []

for i in range(3):

    linea, = ax.plot(
        [],
        [],
        color=colores[i],
        linewidth=1.7,
        label=f"AI{i + 1}"
    )

    lineas.append(linea)

ax.set_title(
    "BrainChild PR1006 - Monitoreo continuo",
    fontsize=14
)

ax.set_xlabel("Tiempo transcurrido (minutos)")
ax.set_ylabel("Temperatura (C)")

ax.set_xlim(0, VENTANA_GRAFICO)

ax.xaxis.set_major_locator(
    MultipleLocator(5)
)

ax.grid(True, alpha=0.35)
ax.legend(loc="upper right")

# ============================================
# INDICADORES
# ============================================

texto_temperaturas = fig.text(
    0.5,
    0.94,
    "Esperando primera lectura...",
    ha="center",
    fontsize=13,
    fontweight="bold"
)

texto_tiempo = fig.text(
    0.5,
    0.89,
    "Tiempo transcurrido: 00:00:00",
    ha="center",
    fontsize=11
)

texto_estado = fig.text(
    0.5,
    0.84,
    "Iniciando monitoreo...",
    ha="center",
    fontsize=10
)

# ============================================
# BOTON GUARDAR
# ============================================

texto_guardado = fig.text(0.5, 0.025, "Sin exportaciones aun", ha="center", fontsize=9)

ax_boton = fig.add_axes([
    0.36, 0.055, 0.28, 0.065
])

boton_guardar = Button(
    ax_boton,
    "Guardar PNG + Excel"
)

# ============================================
# LEER TEMPERATURAS
# ============================================

def leer_temperaturas():

    if not cliente.connected:

        if not cliente.connect():
            raise ConnectionError(
                f"No se pudo conectar al {PUERTO}"
            )

    respuesta = cliente.read_input_registers(
        address=1,
        count=3,
        device_id=NODO
    )

    if respuesta.isError():
        raise RuntimeError(str(respuesta))

    return [
        convertir_temperatura(valor)
        for valor in respuesta.registers
    ]

# ============================================
# GUARDAR PNG + EXCEL
# ============================================

def guardar_resultados(origen="Manual"):

    global exportando

    if exportando:
        return

    exportando = True

    try:

        marca = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        nombre = f"monitoreo_{SESION}_{marca}"

        ruta_png = CARPETA / f"{nombre}.png"
        ruta_excel = CARPETA / f"{nombre}.xlsx"

        # Copia de las mediciones hasta este momento
        datos = list(registros)

        # Generar Excel editable
        crear_excel(ruta_excel, datos)

        # Guardar imagen del grafico
        fig.savefig(
            ruta_png,
            dpi=180,
            bbox_inches="tight"
        )

        print("\n================================")
        print("GUARDADO:", origen)
        print("Excel:", ruta_excel)
        print("Imagen:", ruta_png)
        print("Registros:", len(datos))
        print("================================\n")

        texto_estado.set_text(
            f"Guardado correcto - {len(datos)} lecturas"
        )
        texto_guardado.set_text(f"Ultimo guardado: {datetime.now():%H:%M:%S} - PNG + Excel")
        fig.canvas.draw_idle()

    except Exception as error:

        print("Error al guardar:", error)

        texto_estado.set_text(
            "Error al guardar - CSV disponible"
        )
        texto_guardado.set_text(f"Error de exportacion: {error}")
        fig.canvas.draw_idle()

    finally:
        exportando = False

def guardar_manual(event):
    print("\nBOTON GUARDAR PRESIONADO")
    guardar_resultados("Manual")

conexion_boton = boton_guardar.on_clicked(guardar_manual)

# ============================================
# ACTUALIZACION DEL MONITOREO
# ============================================

def actualizar(frame):

    global proxima_lectura
    global proximo_guardado

    if finalizado:
        return lineas

    ahora = time.monotonic()
    transcurrido = ahora - inicio

    # Reloj de monitoreo
    horas = int(transcurrido // 3600)
    minutos = int((transcurrido % 3600) // 60)
    segundos = int(transcurrido % 60)

    texto_tiempo.set_text(
        f"Tiempo transcurrido: "
        f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    )

    # ========================================
    # LECTURA CADA SEGUNDO
    # ========================================

    if ahora >= proxima_lectura:

        proxima_lectura = ahora + INTERVALO_LECTURA

        try:

            valores = leer_temperaturas()

            fecha = datetime.now()
            tiempo_min = (
                time.monotonic() - inicio
            ) / 60

            registro = [
                fecha.strftime("%d-%m-%Y"),
                fecha.strftime("%H:%M:%S"),
                round(tiempo_min, 4),
                *[round(v, 3) for v in valores]
            ]

            # Guardar inmediatamente en CSV
            with open(
                ARCHIVO_CSV,
                "a",
                newline="",
                encoding="utf-8-sig"
            ) as archivo:

                escritor = csv.writer(
                    archivo,
                    delimiter=";"
                )

                escritor.writerow([
                    registro[0],
                    registro[1],
                    *[
                        str(v).replace(".", ",")
                        for v in registro[2:]
                    ]
                ])

            registros.append(registro)

            tiempos.append(tiempo_min)

            for i in range(3):
                temperaturas[i].append(valores[i])

            # Mostrar solo los ultimos 60 minutos
            limite_inferior = max(
                0,
                tiempo_min - VENTANA_GRAFICO
            )

            for i in range(3):

                # Solo datos visibles en la ventana
                indices_visibles = [
                    j for j, t in enumerate(tiempos)
                    if t >= limite_inferior
                ]

                x_visible = [
                    tiempos[j]
                    for j in indices_visibles
                ]

                y_visible = [
                    temperaturas[i][j]
                    for j in indices_visibles
                ]

                lineas[i].set_data(
                    x_visible,
                    y_visible
                )

            ax.set_xlim(
                limite_inferior,
                limite_inferior + VENTANA_GRAFICO
            )

            ax.relim()
            ax.autoscale_view(
                scalex=False,
                scaley=True
            )

            texto_temperaturas.set_text(
                f"AI1: {valores[0]:.1f} C    "
                f"AI2: {valores[1]:.1f} C    "
                f"AI3: {valores[2]:.1f} C"
            )

            texto_estado.set_text(
                f"Registrando - "
                f"{len(registros)} mediciones"
            )

            print(
                fecha.strftime("%H:%M:%S"),
                f"AI1={valores[0]:.1f}",
                f"AI2={valores[1]:.1f}",
                f"AI3={valores[2]:.1f}"
            )

        except Exception as error:

            print("Error de comunicacion:", error)

            texto_estado.set_text(
                "Error de comunicacion - Reintentando"
            )

            cliente.close()

    # ========================================
    # GUARDADO AUTOMATICO CADA HORA
    # ========================================

    if time.monotonic() >= proximo_guardado:

        guardar_resultados("Automatico - 1 hora")

        proximo_guardado += INTERVALO_AUTOGUARDADO

    return lineas

# ============================================
# CIERRE DEL PROGRAMA
# ============================================

def cerrar(event):

    global finalizado

    if finalizado:
        return

    finalizado = True

    cliente.close()

    print("\nMONITOREO DETENIDO")
    print("CSV:", ARCHIVO_CSV)

    # Guardar Excel final al cerrar
    try:

        ruta_final = CARPETA / (
            f"monitoreo_{SESION}_FINAL.xlsx"
        )

        crear_excel(
            ruta_final,
            list(registros)
        )

        print("Excel final:", ruta_final)

    except Exception as error:
        print("Error al guardar Excel final:", error)

fig.canvas.mpl_connect(
    "close_event",
    cerrar
)

# ============================================
# INICIAR
# ============================================

print("======================================")
print(" MONITOREO CONTINUO BRAINCHILD PR1006")
print("======================================")
print("Puerto:", PUERTO)
print("Lectura: cada segundo")
print("Grafico: ultimos 60 minutos")
print("Guardado automatico: cada hora")
print("Guardado manual: boton PNG + Excel")
print("CSV:", ARCHIVO_CSV)
print("======================================")

animacion = FuncAnimation(
    fig,
    actualizar,
    interval=200,
    cache_frame_data=False
)

try:
    plt.show()
finally:
    cliente.close()
