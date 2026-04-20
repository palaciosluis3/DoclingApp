import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import gc
import glob
import shutil
import pdfplumber
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv, set_key
import google.generativeai as genai
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc.document import PictureItem, FormulaItem


# Cargar variables de entorno
load_dotenv()

# Configuración Estética Cyberpunk Premium (v2.2 Stable)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#080808"
ACCENT_GREEN = "#39ff14"
ACCENT_CYAN = "#00f3ff"
ACCENT_RED = "#ff003c"
CORNER_RADIUS = 15

EXPERT_PROMPT = (
    "Actúa como un experto en digitalización científica y técnica. SIN INTRODUCCIONES NI SALUDOS. "
    "\n- GRÁFICAS/TABLAS/DIAGRAMAS: Extrae datos técnicos precisos."
    "\n- ECUACIONES: Tradúcelas íntegramente a LaTeX. DEBES envolver la ecuación con doble signo de dólar y asegurar que haya saltos de línea antes y después, exactamente con este formato: \n\n$$\n[ecuación]\n$$\n\n"
    "\nIMPORTANTE: Si la imagen es ruido informativo (logos, líneas, decorativos), responde ÚNICAMENTE con el carácter '.' y nada más."
)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DOCLING GPU // NEON CONVERTER")
        self.geometry("900x750")
        self.configure(fg_color=BG_COLOR)

        self.protocol("WM_DELETE_WINDOW", self.safe_exit)

        self.cancel_flag = False
        self.selected_files = []
        self.output_dir = "MD_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.temp_img_dir = "temp_images"
        os.makedirs(self.temp_img_dir, exist_ok=True)

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Estado de opciones
        self.use_visual_analysis = ctk.BooleanVar(value=True)
        
        self._build_ui()

    def _build_ui(self):
        # Header modernizado
        self.header = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0, height=60)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.lbl_title = ctk.CTkLabel(self.header, text="◆ DOCLING CYBER-CONVERTER", 
                                     font=("Consolas", 18, "bold"), text_color=ACCENT_CYAN)
        self.lbl_title.pack(side="left", padx=30)

        self.btn_hard_exit = ctk.CTkButton(self.header, text="✕", width=40, height=40,
                                          font=("Arial", 18, "bold"),
                                          corner_radius=8,
                                          fg_color="transparent", 
                                          hover_color=ACCENT_RED,
                                          text_color="#ffffff", 
                                          command=self.safe_exit)
        self.btn_hard_exit.pack(side="right", padx=10)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Panel de API Key
        self.api_frame = ctk.CTkFrame(self.main_container, fg_color="#121212", 
                                     corner_radius=CORNER_RADIUS, border_width=1, border_color="#222222")
        self.api_frame.pack(fill="x", pady=(0, 20), ipady=5)

        self.lbl_api = ctk.CTkLabel(self.api_frame, text="GEMINI API KEY:", font=("Consolas", 11), text_color=ACCENT_CYAN)
        self.lbl_api.pack(side="left", padx=20)

        self.ent_api = ctk.CTkEntry(self.api_frame, fg_color="#0f0f0f", border_color="#333333", 
                                   text_color="#ffffff", font=("Consolas", 11), show="*")
        self.ent_api.pack(side="left", padx=10, fill="x", expand=True)
        self.ent_api.insert(0, self.gemini_api_key)

        self.btn_save_api = ctk.CTkButton(self.api_frame, text="GUARDAR", width=80,
                                         fg_color="#1a1a1a", border_color=ACCENT_CYAN, border_width=1,
                                         text_color=ACCENT_CYAN, hover_color="#002233", command=self.save_api_key)
        self.btn_save_api.pack(side="right", padx=20)

        self.ctrl_frame = ctk.CTkFrame(self.main_container, fg_color="#121212", 
                                      corner_radius=CORNER_RADIUS, border_width=1, border_color="#222222")
        self.ctrl_frame.pack(fill="x", pady=(0, 20), ipady=15)

        self.btn_select = ctk.CTkButton(self.ctrl_frame, text="CARGAR ARCHIVOS", corner_radius=10,
                                        fg_color="#1a1a1a", border_color=ACCENT_CYAN, border_width=1,
                                        text_color=ACCENT_CYAN, hover_color="#002233", command=self.select_files)
        self.btn_select.pack(side="left", padx=20, expand=True, fill="x")

        self.btn_start = ctk.CTkButton(self.ctrl_frame, text="EJECUTAR CONVERSION", corner_radius=10,
                                       fg_color="#1a1a1a", border_color=ACCENT_GREEN, border_width=1,
                                       text_color=ACCENT_GREEN, hover_color="#002211", command=self.start_conversion)
        self.btn_start.pack(side="left", padx=20, expand=True, fill="x")

        self.btn_cancel = ctk.CTkButton(self.ctrl_frame, text="ABORTAR", corner_radius=10,
                                        fg_color="#1a1a1a", border_color=ACCENT_RED, border_width=1,
                                        text_color=ACCENT_RED, hover_color="#330000", command=self.cancel_conversion)
        self.btn_cancel.pack(side="left", padx=20, expand=True, fill="x")
        self.btn_cancel.configure(state="disabled")

        # Checkbox para análisis visual
        self.opt_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.opt_frame.pack(fill="x", pady=(0, 10))
        
        self.chk_visual = ctk.CTkCheckBox(self.opt_frame, text="ACTIVAR ANÁLISIS VISUAL (GEMINI + PDFPLUMBER)", 
                                         variable=self.use_visual_analysis,
                                         font=("Consolas", 11),
                                         fg_color=ACCENT_CYAN, hover_color="#002233",
                                         text_color="#ffffff", border_color="#444444")
        self.chk_visual.pack(side="left", padx=10)

        self.lbl_files = ctk.CTkLabel(self.main_container, text="〉ARCHIVOS EN COLA", font=("Consolas", 12, "bold"), text_color="#666666")
        self.lbl_files.pack(anchor="w")
        
        self.txt_files = ctk.CTkTextbox(self.main_container, height=180, corner_radius=CORNER_RADIUS,
                                       fg_color="#0f0f0f", text_color="#aaaaaa", border_color="#222222", border_width=1, 
                                       font=("Consolas", 11))
        self.txt_files.pack(fill="x", pady=(0, 20))
        self.txt_files.configure(state="disabled")

        self.progressbar = ctk.CTkProgressBar(self.main_container, height=12, progress_color=ACCENT_GREEN, 
                                             fg_color="#111111", border_width=0, corner_radius=6)
        self.progressbar.pack(fill="x", pady=(0, 20))
        self.progressbar.set(0)

        self.lbl_log = ctk.CTkLabel(self.main_container, text="〉SYSTEM LOG", font=("Consolas", 12, "bold"), text_color=ACCENT_GREEN)
        self.lbl_log.pack(anchor="w")

        self.txt_log = ctk.CTkTextbox(self.main_container, corner_radius=CORNER_RADIUS,
                                     fg_color="#0f0f0f", text_color=ACCENT_GREEN, border_color="#113311", border_width=1,
                                     font=("Consolas", 11))
        self.txt_log.pack(fill="both", expand=True, pady=(0, 10))
        self.txt_log.configure(state="disabled")

        self.log_message("[OK] Sistema armado. Interfaz v2.2 (Estable)")

    def log_message(self, msg):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"> {msg}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def save_api_key(self):
        key = self.ent_api.get().strip()
        if key:
            self.gemini_api_key = key
            env_path = Path(".env")
            if not env_path.exists():
                env_path.touch()
            set_key(".env", "GEMINI_API_KEY", key)
            self.log_message("[OK] API Key guardada en .env")
        else:
            self.log_message("[WARN] API Key vacía")

    def select_files(self):
        files = filedialog.askopenfilenames(title="Seleccionar Archivos", 
                                           filetypes=[("Archivos soportados", "*.pdf *.docx"), ("PDF", "*.pdf"), ("Word", "*.docx")])
        if files:
            self.selected_files = list(files)
            self.update_file_list()
            self.log_message(f"Cargados {len(self.selected_files)} archivos.")

    def update_file_list(self):
        self.txt_files.configure(state="normal")
        self.txt_files.delete("1.0", "end")
        for f in self.selected_files:
            self.txt_files.insert("end", f + "\n")
        self.txt_files.configure(state="disabled")

    def cancel_conversion(self):
        self.cancel_flag = True
        self.log_message("ABORTANDO...")

    def start_conversion(self):
        if not self.selected_files:
            self.log_message("ERROR: No hay archivos.")
            return
        self.cancel_flag = False
        self.btn_select.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        threading.Thread(target=self._process_files, daemon=True).start()

    def _process_files(self):
        try:
            enable_visual = self.use_visual_analysis.get()
            api_key = self.ent_api.get().strip()

            model = None
            if enable_visual:
                if not api_key:
                    self.after(0, self.log_message, "ERROR: Falta API Key de Gemini para Análisis Visual.")
                    return
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
                except Exception as e:
                    self.after(0, self.log_message, f"ERROR configurando Gemini: {str(e)}")
                    enable_visual = False
            else:
                self.after(0, self.log_message, "[INFO] Análisis Visual (Gemini) desactivado.")

            self.after(0, self.log_message, "Configurando Motores de Conversión...")
            
            # Configurar Pipeline de Docling
            pipeline_options = PdfPipelineOptions()
            if hasattr(pipeline_options, 'formula_options'):
                pipeline_options.formula_options.do_formula_detection = True
            
            pipeline_options.do_table_structure = True
            pipeline_options.do_ocr = True 
            
            converter = DocumentConverter(
                format_options={
                    "pdf": PdfFormatOption(pipeline_options=pipeline_options)
                }
            )

            total = len(self.selected_files)
            
            for idx, file_path in enumerate(self.selected_files):
                if self.cancel_flag: break
                filename = os.path.basename(file_path)
                is_pdf = filename.lower().endswith(".pdf")
                
                self.after(0, self.log_message, f"[{filename}] Procesando...")
                try:
                    # 1. Ejecutar Docling (Soporta PDF, DOCX y más)
                    result = converter.convert(file_path)
                    doc = result.document
                    descriptions = []

                    # 2. Análisis Visual (Solo para PDF y si está habilitado)
                    if is_pdf and enable_visual:
                        os.makedirs(self.temp_img_dir, exist_ok=True)
                        self.after(0, self.log_message, f"  〉Escaneando visuales (Protocolo pdfplumber)...")
                        extracted_data = self.extract_pdfplumber_protocol(file_path)
                        
                        if extracted_data:
                            self.after(0, self.log_message, f"  〉Analizando {len(extracted_data)} imágenes con Gemini...")
                            for i, entry in enumerate(extracted_data):
                                if self.cancel_flag: break
                                try:
                                    self.after(0, self.log_message, f"    - Img {i+1} (Pág {entry['page_num']})...")
                                    desc = self.analyze_image_with_gemini(model, entry['path'])
                                    if desc and desc != ".":
                                        entry['description'] = desc
                                        descriptions.append(entry)
                                except Exception as e:
                                    self.after(0, self.log_message, f"    [!] Error Gemini: {str(e)}")
                        else:
                            self.after(0, self.log_message, f"  〉No se encontraron imágenes filtradas.")

                    # 3. Exportación y Anclaje
                    md_text = doc.export_to_markdown()
                    if descriptions:
                        self.after(0, self.log_message, f"  〉Insertando análisis semántico...")
                        final_md = self.apply_anchored_insertion(md_text, descriptions)
                    else:
                        final_md = md_text

                    output_path = os.path.join(self.output_dir, Path(filename).with_suffix(".md").name)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(final_md)
                    
                    if is_pdf:
                        self.cleanup_temp_images(filename)
                    self.after(0, self.log_message, f"SUCCESS: {filename}")

                except Exception as e:
                    self.after(0, self.log_message, f"ERROR en {filename}: {str(e)}")
                
                self.after(0, self.progressbar.set, (idx + 1) / total)
                gc.collect()
            
            if os.path.exists(self.temp_img_dir):
                shutil.rmtree(self.temp_img_dir)
                self.after(0, self.log_message, "[OK] Carpeta temporal eliminada.")
        except Exception as e:
            self.after(0, self.log_message, f"CRITICAL ERROR: {str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            self.after(0, self._on_process_complete)


    def analyze_image_with_gemini(self, model, image_path):
        img = Image.open(image_path)
        response = model.generate_content([EXPERT_PROMPT, img])
        return response.text.strip()

    def apply_anchored_insertion(self, md_text, descriptions):
        """Inserta las descripciones de Gemini en el Markdown usando el sistema de anclaje."""
        if not descriptions:
            return md_text

        current_md = md_text
        unanchored_items = []
        current_search_pos = 0  # Cursor lineal para evitar retrocesos (TOC, etc.)

        # Ordenar por página para mantener un flujo lógico
        descriptions.sort(key=lambda x: x.get('page_num', 0))

        for i, item in enumerate(descriptions):
            anchor_text = item.get('anchor', "")
            caption = item['description']
            
            # Formateo del bloque de inserción
            if "$$" in caption:
                insertion = f"\n\n**[ECUACIÓN (Análisis Visual)]**\n\n{caption}\n\n"
            else:
                insertion = f"\n\n> **FIGURA {i+1} (Análisis Visual):** {caption}\n\n"

            found_pos = -1
            if anchor_text:
                # El protocolo de búsqueda: primero intenta con la última línea del ancla para flexibilidad
                search_term = anchor_text.split("\n")[-1] if "\n" in anchor_text else anchor_text
                found_pos = current_md.find(search_term, current_search_pos)

            if found_pos != -1:
                # Insertar justo después del término encontrado
                insert_at = found_pos + len(search_term)
                current_md = current_md[:insert_at] + insertion + current_md[insert_at:]
                current_search_pos = insert_at + len(insertion)
            else:
                # Fallback: guardar para anexo final
                unanchored_items.append(item)

        # Si hay elementos que no se pudieron anclar, se ponen al final
        if unanchored_items:
            current_md += "\n\n---\n# COMPLEMENTO DE ELEMENTOS NO ANCLADOS\n"
            for item in unanchored_items:
                desc = item['description']
                if "$$" in desc:
                    current_md += f"\n\n**[ECUACIÓN - Pág. {item['page_num']}]**\n{desc}\n"
                else:
                    current_md += f"\n\n> **[ANÁLISIS - Pág. {item['page_num']}]**\n> {desc.replace(chr(10), chr(10)+'> ')}\n"

        return current_md

    def extract_pdfplumber_protocol(self, filepath):
        """Extrae imágenes basándose estrictamente en el protocolo de app_markitdown.py."""
        img_data = [] 
        filename_base = Path(filepath).stem
        
        try:
            with pdfplumber.open(filepath) as pdf:
                img_count = 0
                for page in pdf.pages:
                    if not page.images:
                        continue
                        
                    for img in page.images:
                        w, h = float(img["width"]), float(img["height"])
                        
                        # FILTROS DE RUIDO (Protocolo):
                        if w < 45 or h < 45: continue
                        
                        # Ratio > 10 ignore
                        ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
                        if ratio > 10: continue

                        img_count += 1
                        try:
                            img_filename = f"{filename_base}_visual_{img_count}.png"
                            img_path = os.path.join(self.temp_img_dir, img_filename)
                            
                            # Renderizado del objeto visual
                            bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                            page.crop(bbox).to_image(resolution=200).save(img_path)
                            
                            # CAPTURA DE ANCLA (Sistema de Doble Línea):
                            top_area = page.crop((0, 0, page.width, max(0, img["top"])))
                            text_above = top_area.extract_text() or ""
                            # Filtramos líneas cortas o vacías para obtener anclas significativas
                            lines = [l.strip() for l in text_above.splitlines() if len(l.strip()) > 10]
                            
                            if len(lines) >= 2:
                                anchor = f"{lines[-2]}\n{lines[-1]}" # Combinación de doble línea
                            elif lines:
                                anchor = lines[-1]
                            else:
                                # Fallback al texto de abajo si arriba está vacío
                                bottom_area = page.crop((0, img["bottom"], page.width, page.height))
                                text_below = bottom_area.extract_text() or ""
                                lines_below = [l.strip() for l in text_below.splitlines() if len(l.strip()) > 10]
                                anchor = lines_below[0] if lines_below else ""

                            img_data.append({
                                "path": img_path,
                                "anchor": anchor[:200], # Limitamos longitud del ancla
                                "page_num": page.page_number
                            })
                        except Exception as e:
                            print(f"[WARN] Error procesando imagen {img_count}: {e}")
                            continue
        except Exception as e:
            self.after(0, self.log_message, f"[WARN] Error en extracción pdfplumber: {str(e)}")
            
        return img_data



    def cleanup_temp_images(self, pdf_filename):
        prefix = Path(pdf_filename).stem
        # Limpiar los patrones generados por el nuevo protocolo visual
        pattern = os.path.join(self.temp_img_dir, f"{prefix}_visual_*.png")
        for f in glob.glob(pattern):
            try: os.remove(f)
            except: pass

    def _on_process_complete(self):
        self.btn_select.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.log_message("Ciclo terminado.")

    def safe_exit(self):
        os._exit(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()


