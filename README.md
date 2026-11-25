# OpenThermo Monitor

![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Version](https://img.shields.io/badge/Version-0.9.0--Beta-orange)
![Protocol](https://img.shields.io/badge/Protocol-Modbus%20RTU-blue)
![Price](https://img.shields.io/badge/Price-Free-brightgreen)

## English

### Overview

OpenThermo Monitor is a free and open-source temperature monitoring application for Windows, developed for BrainChild PR1006 data recorders using Modbus RTU communication over RS-485.

The project aims to provide an accessible alternative for industrial temperature monitoring, data acquisition and visualization.

### Features

- Real-time temperature monitoring.
- Automatic COM port detection and selection.
- Three temperature channels (AI1, AI2 and AI3).
- Continuous data acquisition.
- Approximately one-second sampling interval.
- Rolling 60-minute temperature chart.
- Automatic CSV data logging.
- Hourly Excel and PNG exports.
- Manual data export.
- Excel reports with charts and statistical summaries.
- Portable Windows application.
- No subscription or hardware license key required.
- Offline operation.

### Download

Visit the [Releases](../../releases) section to download the Windows executable when available.

### Installation and usage

1. Download BrainChild_Monitor.exe from Releases.
2. Connect the BrainChild recorder using a USB-to-RS485 converter.
3. Install the USB converter driver if required.
4. Run the application.
5. Select the appropriate COM port.
6. Select the output folder.
7. Connect and start monitoring.

Python is not required when using the compiled executable.

### Communication settings

| Parameter | Value |
|---|---|
| Protocol | Modbus RTU |
| Interface | RS-485 |
| Baud rate | 9600 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Device address | 1 |
| Channels | AI1, AI2, AI3 |

### Compatibility

Originally developed and tested with the BrainChild PR1006-0A0310S1 using Pt100 sensors.

Compatibility with other models, sensor configurations and register formats has not yet been validated.

### Development roadmap

- Configurable Modbus communication parameters.
- Support for additional temperature channels.
- Custom temperature scaling.
- Support for additional BrainChild models.
- Generic Modbus device compatibility.
- Modbus TCP support.
- Multilingual user interface.

---

## Español

### Descripción

OpenThermo Monitor es una aplicación gratuita y de código abierto para Windows, desarrollada para monitorear temperaturas mediante registradores BrainChild PR1006 utilizando comunicación Modbus RTU sobre RS-485.

El objetivo del proyecto es ofrecer una alternativa accesible para la adquisición, visualización y registro de temperaturas industriales.

### Características

- Monitoreo de temperaturas en tiempo real.
- Detección y selección de puertos COM.
- Tres canales de temperatura (AI1, AI2 y AI3).
- Adquisición continua de datos.
- Registro aproximadamente cada segundo.
- Gráfico dinámico de los últimos 60 minutos.
- Respaldo automático en CSV.
- Exportación automática a Excel y PNG cada hora.
- Guardado manual de mediciones.
- Informes Excel con gráficos y estadísticas.
- Aplicación portable para Windows.
- Sin suscripciones ni llaves de licencia.
- Funcionamiento sin conexión a internet.

### Descarga

Visita la sección [Releases](../../releases) para descargar el ejecutable de Windows cuando esté disponible.

### Instalación y uso

1. Descargar BrainChild_Monitor.exe desde Releases.
2. Conectar el registrador BrainChild mediante un convertidor USB a RS-485.
3. Instalar el controlador del convertidor si es necesario.
4. Ejecutar el programa.
5. Seleccionar el puerto COM correspondiente.
6. Seleccionar la carpeta de almacenamiento.
7. Conectar e iniciar el monitoreo.

No requiere instalar Python si se utiliza el archivo ejecutable.

### Compatibilidad

Desarrollado y probado originalmente con el BrainChild PR1006-0A0310S1 y sensores Pt100.

La compatibilidad con otros modelos, configuraciones de sensores y formatos de registros todavía no ha sido validada.

### Futuras mejoras

- Parámetros de comunicación Modbus configurables.
- Mayor cantidad de canales de temperatura.
- Configuración personalizada de escalas.
- Compatibilidad con otros modelos BrainChild.
- Compatibilidad con dispositivos Modbus genéricos.
- Comunicación Modbus TCP.
- Interfaz multilingüe.

---

## Technologies / Tecnologías

- Python
- PyModbus
- PySerial
- Matplotlib
- OpenPyXL
- Tkinter
- PyInstaller

## Contributions / Contribuciones

Contributions, suggestions, bug reports and compatibility testing are welcome.

Se aceptan contribuciones, sugerencias, reportes de errores y pruebas de compatibilidad.

## License / Licencia

This project is distributed under the MIT License. See the LICENSE file for details.

Este proyecto se distribuye bajo la licencia MIT.

## Disclaimer / Aviso legal

OpenThermo Monitor is an independent project and is not affiliated with, endorsed by or sponsored by BrainChild.

This software is provided as-is, without warranty. It is not certified for safety-critical applications or regulatory compliance. Users must independently verify measurement accuracy before industrial use.

OpenThermo Monitor es un proyecto independiente, sin afiliación con BrainChild. El software se entrega sin garantías y no cuenta con certificación para aplicaciones críticas de seguridad o cumplimiento normativo. El usuario debe verificar la exactitud de las mediciones antes de utilizarlo en procesos industriales.

---

**Free software. Open technology. Accessible monitoring.**
