# ⚡ DOCLING CYBER-CONVERTER // NEON EDITION

![License](https://img.shields.io/badge/license-MIT-blueviolet)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Docling](https://img.shields.io/badge/engine-Docling-ff69b4)
![Gemini](https://img.shields.io/badge/AI-Gemini_Flash-00f3ff)

**DOCLING APP** es una herramienta de digitalización técnica de alto rendimiento diseñada para transformar documentos complejos (PDF, DOCX) en archivos Markdown limpios, estructurados y listos para LLMs. Con una interfaz estética **Cyberpunk**, este software no solo es funcional, sino que ofrece una experiencia visual premium.

---

## 🚀 Características Principales

- **Conversión de Alta Fidelidad**: Utiliza el motor `Docling` para procesar documentos manteniendo la jerarquía y estructura.
- **Análisis Visual con IA (Opcional)**: Integración con **Google Gemini** para analizar gráficas, diagramas y tablas complejas dentro de los PDFs.
- **Experto en LaTeX**: Detección y conversión automática de ecuaciones matemáticas a formato LaTeX íntegro.
- **Reconocimiento de Estructuras**: Detección avanzada de tablas y metadatos del documento.
- **Interfaz Neon UI**: Desarrollada con `CustomTkinter` para un entorno de trabajo futurista y eficiente.
- **Multiprocesamiento**: Soporte nativo para aceleración por GPU (CUDA) o ejecución optimizada en CPU.

---

## 🛠️ Instalación y Configuración

El proyecto incluye scripts automatizados para facilitar la configuración dependiendo de tu hardware.

### Requisitos Previos
- **Python 3.10 o superior** instalado.
- (Opcional) Una GPU NVIDIA para aceleración de OCR y modelos de visión locales.

### Opción A: Instalación Estándar (CPU)
Ideal para laptops sin GPU dedicada o si prefieres una instalación ligera.
1. Ejecuta `setup.bat`. Esto creará un entorno virtual (`venv`) e instalará los paquetes necesarios con la versión de PyTorch para CPU.
2. Para iniciar la aplicación, ejecuta `run.bat`.

### Opción B: Instalación con Aceleración GPU (NVIDIA)
Recomendado para procesos masivos de documentos u OCR pesado.
1. Ejecuta `setup_gpu.bat`. Este script configurará un entorno virtual dedicado (`venv_gpu`) e instalará PyTorch con soporte para **CUDA 12.4** (optimizado para arquitecturas modernas como la serie RTX 30/40).
2. Para iniciar la aplicación con potencia total, ejecuta `run_gpu.bat`.

---

## 🧠 Integración con Gemini (Análisis Visual)

Para llevar la conversión al siguiente nivel, puedes activar el **Análisis Visual**. Esto permite que la aplicación "vea" las imágenes del PDF y las traduzca a contenido técnico o ecuaciones LaTeX.

1. Consigue tu API Key en [Google AI Studio](https://aistudio.google.com/).
2. Abre la aplicación e ingresa tu clave en el panel superior **"GEMINI API KEY"**.
3. Haz clic en **"GUARDAR"** (la clave se almacenará de forma segura en un archivo `.env`).
4. Marca la casilla **"ACTIVAR ANÁLISIS VISUAL"** antes de iniciar la conversión.

---

## 📖 Cómo utilizarlo

1. **Cargar Archivos**: Selecciona uno o varios archivos PDF o DOCX.
2. **Configurar**: Decide si quieres usar el análisis de Gemini.
3. **Ejecutar**: El sistema procesará cada documento y generará los resultados en la carpeta `MD_results`.
4. **Logs en Tiempo Real**: Sigue el progreso y posibles errores a través de la consola integrada con estética de hacker.

---

## 📂 Estructura del Proyecto

- `app.py`: El núcleo de la aplicación y la interfaz gráfica.
- `MD_results/`: Carpeta de destino de tus archivos Markdown convertidos.
- `.env`: Almacena tu configuración privada (como la API Key).
- `setup_*.bat`: Scripts de instalación automatizada.
- `run_*.bat`: Scripts de lanzamiento rápido.

---

## ⚠️ Notas Técnicas

- **Filtro de Ruido**: El sistema ignora automáticamente imágenes decorativas (logos, líneas) para no ensuciar el Markdown resultante.
- **Protocolo de Anclaje**: La IA de Gemini intenta insertar las descripciones e imágenes exactamente donde aparecen en el texto original mediante un sistema de "anclaje de doble línea".

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Siéntete libre de clonarlo, modificarlo y mejorarlo. 

---
*Developed with ❤️ for the Cyberpunk future of document processing.*
