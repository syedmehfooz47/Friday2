# -*- coding: utf-8 -*-
"""
Unified File Converter - Convert and compress between multiple formats
Supports PDF, DOCX, PPTX, XLSX, JPG, PNG, SVG with compression
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from .logger import Logger

load_dotenv()

# --- Dependency Checks ---
WIN32_AVAILABLE = False
if sys.platform == "win32":
    try:
        import win32com.client
        import comtypes.client # Often needed alongside win32com
        # --- ADDED: pygetwindow check needed for convert_active_document ---
        import pygetwindow as gw
        WIN32_AVAILABLE = True
        Logger.log("win32com, comtypes, and pygetwindow available for Office conversions.", "CONVERTER")
    except ImportError:
        Logger.log("win32com/comtypes/pygetwindow not available. Office document conversions (DOCX, PPTX, XLSX to PDF) and active document conversion disabled on Windows.", "WARNING")

PDF2DOCX_AVAILABLE = False
try:
    from pdf2docx import Converter as PDF2DOCXConverter
    PDF2DOCX_AVAILABLE = True
    Logger.log("pdf2docx available for PDF to DOCX conversion.", "CONVERTER")
except ImportError:
    Logger.log("pdf2docx not installed. PDF to DOCX conversion disabled. Install with: pip install pdf2docx", "WARNING")

IMG2PDF_AVAILABLE = False
try:
    import img2pdf
    IMG2PDF_AVAILABLE = True
    Logger.log("img2pdf available for Image to PDF conversion.", "CONVERTER")
except ImportError:
    Logger.log("img2pdf not installed. Image to PDF conversion disabled. Install with: pip install img2pdf", "WARNING")

PDF2IMAGE_AVAILABLE = False
try:
    # pdf2image requires poppler binaries
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError
    try:
        # Test if poppler is accessible - Create a dummy PDF path to check
        # NOTE: This check might still fail if __init__.py isn't there, but it's better than nothing.
        # A more robust check would involve a tiny known PDF file.
        dummy_check_path = Path(__file__).parent / "__init__.py" # Use init file as placeholder
        if dummy_check_path.exists():
             _ = convert_from_path(dummy_check_path, dpi=10, fmt='jpeg') # Use jpeg format
        PDF2IMAGE_AVAILABLE = True # Assume it works if no specific error
        Logger.log("pdf2image available for PDF to Image conversion.", "CONVERTER")
    except PDFInfoNotInstalledError:
        Logger.log("pdf2image found, but Poppler binaries not found or not in PATH. PDF to Image conversion disabled.", "ERROR")
        Logger.log("Download Poppler for your OS: https://github.com/oschwartz10612/poppler-windows/releases/ or use package manager.", "INFO")
    except Exception as e: # Catch other potential errors during check
        Logger.log(f"pdf2image check failed ({e.__class__.__name__}), assuming available but Poppler might be missing.", "WARNING")
        PDF2IMAGE_AVAILABLE = True # Still assume lib is installed

except ImportError:
    Logger.log("pdf2image not installed. PDF to Image conversion disabled. Install with: pip install pdf2image", "WARNING")


CAIROSVG_AVAILABLE = False
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
    Logger.log("CairoSVG available for SVG conversion.", "CONVERTER")
except ImportError:
    Logger.log("CairoSVG not installed. SVG conversion disabled. Install with: pip install CairoSVG", "WARNING")
except OSError:
    Logger.log("CairoSVG library found, but its C library dependency (Cairo/GTK) is missing or not configured.", "ERROR")
    Logger.log("Install GTK+ runtime for Windows or necessary libraries on Linux/macOS.", "INFO")


PYPDF_AVAILABLE = False
try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
    Logger.log("pypdf available for PDF manipulation/compression.", "CONVERTER")
except ImportError:
    Logger.log("pypdf not installed. PDF compression disabled. Install with: pip install pypdf", "WARNING")


class FileConverter:
    """Unified file converter with compression"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_folder = self.project_root / "Data" / "ConvertedDocuments"
        self.data_folder.mkdir(parents=True, exist_ok=True)
        Logger.log(f"FileConverter initialized. Output folder: {self.data_folder}", "CONVERTER")

    def get_all_converted_files(self):
        """Get all files in the converted documents folder, sorted by modification time."""
        try:
            files = list(self.data_folder.glob("*.*")) # Only get files
            return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
        except Exception as e:
            Logger.log(f"Error getting converted files: {e}", "ERROR")
            return []

    def get_last_converted_file(self):
        """Get the absolute path of the most recently converted file."""
        files = self.get_all_converted_files()
        if files:
            last_file = files[0].resolve() # Get absolute path
            Logger.log(f"Last converted file requested: {last_file}", "CONVERTER")
            return str(last_file)
        else:
            Logger.log("No converted files found when requesting last converted file.", "CONVERTER")
            return None

    def convert_file(self, input_path: str, output_format: str,
                           compress: bool = False, compression_quality: int = 85) -> tuple:
        """
        Convert file to specified format with optional compression.

        Args:
            input_path: Absolute path to input file.
            output_format: Desired output format (e.g., 'pdf', 'docx', 'png').
            compress: Whether to compress the output (if supported).
            compression_quality: Compression quality 10-100 (higher = better).

        Returns:
            Tuple of (response message, output file path or None).
        """
        username = os.getenv("Username", "Boss")
        input_file = Path(input_path).resolve() # Ensure absolute path

        if not input_file.exists() or not input_file.is_file():
            Logger.log(f"Input file not found or is not a file: {input_path}", "ERROR")
            return f"File not found: {input_path}", None

        input_ext = input_file.suffix.lower().replace('.', '')
        output_format = output_format.lower().replace('.', '')

        Logger.log(f"Request to convert '{input_file.name}' ({input_ext}) to {output_format}", "CONVERTER")

        if not 10 <= compression_quality <= 100:
             Logger.log(f"Invalid compression quality ({compression_quality}), defaulting to 85.", "WARNING")
             compression_quality = 85

        output_path = None
        message = ""

        try:
            # --- Conversion Routing ---
            if input_ext == 'pdf' and output_format == 'docx':
                message, output_path = self._pdf_to_docx(str(input_file))
            elif input_ext == 'docx' and output_format == 'pdf':
                message, output_path = self._docx_to_pdf(str(input_file))
            elif input_ext == 'pptx' and output_format == 'pdf':
                message, output_path = self._pptx_to_pdf(str(input_file))
            elif input_ext == 'xlsx' and output_format == 'pdf':
                 message, output_path = self._xlsx_to_pdf(str(input_file))
            elif input_ext in ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'] and output_format == 'pdf':
                message, output_path = self._image_to_pdf(str(input_file))
            elif input_ext == 'pdf' and output_format in ['jpg', 'png', 'jpeg', 'tiff', 'bmp']:
                message, output_path = self._pdf_to_image(str(input_file), output_format)
            elif input_ext in ['jpg', 'jpeg', 'webp', 'bmp', 'tiff'] and output_format == 'png':
                 message, output_path = self._image_to_image(str(input_file), 'png')
            elif input_ext == 'png' and output_format in ['jpg', 'jpeg', 'webp', 'bmp', 'tiff']:
                message, output_path = self._image_to_image(str(input_file), output_format)
            elif input_ext == 'svg' and output_format in ['jpg', 'png', 'pdf', 'jpeg']:
                 message, output_path = self._svg_to_format(str(input_file), output_format)
            elif input_ext in ['jpg', 'png', 'jpeg'] and output_format == 'svg':
                 message = f"Raster image ({input_ext}) to SVG conversion requires vectorization (not supported), Boss."
                 output_path = None
            else:
                 message = f"Conversion from {input_ext} to {output_format} is not supported, Boss."
                 output_path = None

            # --- Compression Step ---
            if output_path and compress:
                # Only compress supported formats after conversion
                if Path(output_path).suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    compress_msg, compressed_path = self._compress_image(output_path, compression_quality)
                    if compressed_path:
                        message += f" {compress_msg}"
                        output_path = compressed_path # Update output path to compressed version
                    else:
                        message += f" Compression failed: {compress_msg}"
                elif Path(output_path).suffix.lower() == '.pdf':
                    compress_msg, compressed_path = self._compress_pdf(output_path, compression_quality) # Use quality as percent approximation
                    if compressed_path:
                         message += f" {compress_msg}"
                         output_path = compressed_path
                    else:
                        message += f" Compression failed: {compress_msg}"
                elif Path(output_path).suffix.lower() == '.svg':
                     compress_msg, compressed_path = self._compress_svg(output_path, compression_quality)
                     if compressed_path:
                           message += f" {compress_msg}"
                           output_path = compressed_path
                     else:
                           message += f" Compression failed: {compress_msg}"

            return message, output_path

        except Exception as e:
            Logger.log(f"Conversion failed for '{input_file.name}': {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR") # Log full traceback
            return f"Conversion error processing '{input_file.name}': {e}", None

    def compress_file(self, input_path: str, compression_percent: int = 50) -> tuple:
        """Compress a supported file (PDF, JPG, PNG, SVG)."""
        username = os.getenv("Username", "Boss")
        input_file = Path(input_path).resolve()

        if not input_file.exists() or not input_file.is_file():
            Logger.log(f"Input file not found for compression: {input_path}", "ERROR")
            return f"File not found: {input_path}", None

        if not 10 <= compression_percent <= 100:
            Logger.log(f"Invalid compression percent ({compression_percent}), using 50.", "WARNING")
            compression_percent = 50

        input_ext = input_file.suffix.lower()
        Logger.log(f"Request to compress '{input_file.name}' to ~{100-compression_percent}% size reduction", "CONVERTER")

        try:
            if input_ext in ['.jpg', '.jpeg', '.png']:
                return self._compress_image(str(input_file), compression_percent)
            elif input_ext == '.pdf':
                return self._compress_pdf(str(input_file), compression_percent)
            elif input_ext == '.svg':
                return self._compress_svg(str(input_file), compression_percent)
            else:
                return f"Compression not supported for {input_ext} files, Boss.", None
        except Exception as e:
            Logger.log(f"Compression error for '{input_file.name}': {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return f"Compression error: {e}", None

    # --- Specific Conversion Methods ---

    def _pdf_to_docx(self, pdf_path: str) -> tuple:
        """Convert PDF to DOCX using pdf2docx"""
        username = os.getenv("Username", "Boss")
        if not PDF2DOCX_AVAILABLE:
            return f"PDF to DOCX conversion requires pdf2docx library, Boss.", None

        output_path = self.data_folder / f"{Path(pdf_path).stem}_converted.docx"
        try:
            cv = PDF2DOCXConverter(pdf_path)
            cv.convert(str(output_path))
            cv.close()
            Logger.log(f"Converted PDF to DOCX: {output_path}", "CONVERTER")
            return f"Converted to DOCX, Boss.", str(output_path)
        except Exception as e:
            Logger.log(f"PDF to DOCX failed: {e}", "ERROR")
            return f"PDF to DOCX conversion failed: {e}", None

    def _office_to_pdf_win32(self, office_path: str, app_name: str, save_format: int) -> tuple:
        """Generic Office to PDF conversion using Windows COM."""
        username = os.getenv("Username", "Boss")
        if not WIN32_AVAILABLE:
            return f"{app_name} to PDF conversion requires Windows with Microsoft Office and pywin32, Boss.", None

        output_path = self.data_folder / f"{Path(office_path).stem}_converted.pdf"
        app = None
        doc = None
        try:
            app = win32com.client.Dispatch(f"{app_name}.Application")
            app.Visible = False
            # Ensure absolute path for COM object
            abs_office_path = str(Path(office_path).resolve())
            doc = app.Workbooks.Open(abs_office_path) if app_name == "Excel" else \
                  app.Presentations.Open(abs_office_path) if app_name == "PowerPoint" else \
                  app.Documents.Open(abs_office_path) # Default to Word

            doc.SaveAs(str(output_path.resolve()), FileFormat=save_format) # Use resolve here too
            Logger.log(f"Converted {app_name} to PDF: {output_path}", "CONVERTER")
            return f"Converted to PDF, Boss.", str(output_path)
        except Exception as e:
            Logger.log(f"{app_name} to PDF failed: {e}", "ERROR")
            return f"{app_name} to PDF conversion failed: {e}", None
        finally:
            if doc:
                try:
                    doc.Close(SaveChanges=False)
                except Exception as close_e:
                     Logger.log(f"Error closing {app_name} document: {close_e}", "WARNING")
            if app:
                try:
                    app.Quit()
                except Exception as quit_e:
                    Logger.log(f"Error quitting {app_name} application: {quit_e}", "WARNING")


    def _docx_to_pdf(self, docx_path: str) -> tuple:
        return self._office_to_pdf_win32(docx_path, "Word", 17) # 17 = wdFormatPDF

    def _pptx_to_pdf(self, pptx_path: str) -> tuple:
        return self._office_to_pdf_win32(pptx_path, "PowerPoint", 32) # 32 = ppSaveAsPDF

    def _xlsx_to_pdf(self, xlsx_path: str) -> tuple:
         # Excel uses ExportAsFixedFormat
        username = os.getenv("Username", "Boss")
        if not WIN32_AVAILABLE:
            return f"Excel to PDF requires Windows with Excel and pywin32, Boss.", None

        output_path = self.data_folder / f"{Path(xlsx_path).stem}_converted.pdf"
        excel = None
        workbook = None
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            workbook = excel.Workbooks.Open(str(Path(xlsx_path).resolve()))
            # Ensure path uses correct separators for COM
            output_path_str = str(output_path.resolve()).replace('/', '\\')
            workbook.ExportAsFixedFormat(0, output_path_str) # 0 = xlTypePDF
            Logger.log(f"Converted Excel to PDF: {output_path}", "CONVERTER")
            return f"Converted to PDF, Boss.", str(output_path)
        except Exception as e:
            Logger.log(f"Excel to PDF failed: {e}", "ERROR")
            return f"Excel to PDF conversion failed: {e}", None
        finally:
            if workbook:
                try:
                    workbook.Close(SaveChanges=False)
                except Exception as close_e:
                    Logger.log(f"Error closing Excel workbook: {close_e}", "WARNING")
            if excel:
                try:
                    excel.Quit()
                except Exception as quit_e:
                    Logger.log(f"Error quitting Excel application: {quit_e}", "WARNING")


    def _image_to_pdf(self, image_path: str) -> tuple:
        """Convert image (JPG, PNG, etc.) to PDF using img2pdf"""
        username = os.getenv("Username", "Boss")
        if not IMG2PDF_AVAILABLE:
            return f"Image to PDF conversion requires img2pdf library, Boss.", None

        output_path = self.data_folder / f"{Path(image_path).stem}_converted.pdf"
        try:
            with open(str(output_path), "wb") as f:
                # img2pdf can take multiple paths or a single one
                f.write(img2pdf.convert(image_path))
            Logger.log(f"Converted image to PDF: {output_path}", "CONVERTER")
            return f"Converted to PDF, Boss.", str(output_path)
        except Exception as e:
            Logger.log(f"Image to PDF failed: {e}", "ERROR")
            return f"Image to PDF conversion failed: {e}", None

    def _pdf_to_image(self, pdf_path: str, output_format: str) -> tuple:
        """Convert PDF (first page) to image (JPG, PNG) using pdf2image"""
        username = os.getenv("Username", "Boss")
        if not PDF2IMAGE_AVAILABLE:
            return f"PDF to image requires pdf2image library and Poppler binaries, Boss.", None

        output_path = self.data_folder / f"{Path(pdf_path).stem}_page1.{output_format}"
        try:
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1, fmt=output_format)
            if images:
                # No need to save again if fmt is provided
                # images[0].save(str(output_path), output_format.upper())
                # The file is already saved by convert_from_path when using fmt and output_folder is implicitly cwd if not given
                # We need to construct the expected path based on pdf2image's naming convention or pass output_folder
                # Let's save explicitly to control the name.
                images[0].save(str(output_path))

                Logger.log(f"Converted PDF page 1 to {output_format}: {output_path}", "CONVERTER")
                return f"Converted first page to {output_format.upper()}, Boss.", str(output_path)
            else:
                return f"Could not extract image from PDF, Boss.", None
        except Exception as e:
            Logger.log(f"PDF to image failed: {e}", "ERROR")
            return f"PDF to image conversion failed: {e}", None

    def _image_to_image(self, image_path: str, output_format: str) -> tuple:
        """Convert between image formats using Pillow"""
        username = os.getenv("Username", "Boss")
        output_format = output_format.lower()
        pil_format = output_format.upper()
        if pil_format == "JPG": pil_format = "JPEG" # Pillow uses JPEG

        output_path = self.data_folder / f"{Path(image_path).stem}_converted.{output_format}"
        try:
            img = Image.open(image_path)
            # Handle transparency for formats that don't support it (like JPEG)
            if img.mode == 'RGBA' and pil_format in ['JPEG', 'BMP', 'TIFF']:
                Logger.log(f"Image has transparency, converting to RGB for {pil_format} format.", "CONVERTER")
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3]) # Use alpha channel as mask
                img = rgb_img
            elif img.mode != 'RGB' and pil_format in ['JPEG']: # Ensure RGB for JPEG
                 img = img.convert('RGB')

            if pil_format == "JPEG":
                img.save(str(output_path), pil_format, quality=95) # Default quality for non-compressed conversion
            else:
                 img.save(str(output_path), pil_format)

            Logger.log(f"Converted {Path(image_path).suffix} to {output_format}: {output_path}", "CONVERTER")
            return f"Converted to {output_format.upper()}, Boss.", str(output_path)
        except Exception as e:
            Logger.log(f"Image to {output_format} failed: {e}", "ERROR")
            return f"Image conversion failed: {e}", None

    def _svg_to_format(self, svg_path: str, output_format: str) -> tuple:
        """Convert SVG to PNG, JPG, or PDF using CairoSVG"""
        username = os.getenv("Username", "Boss")
        if not CAIROSVG_AVAILABLE:
            return f"SVG conversion requires CairoSVG and its C library dependency, Boss.", None

        output_path = self.data_folder / f"{Path(svg_path).stem}_converted.{output_format}"
        try:
            with open(svg_path, 'rb') as svg_file:
                svg_data = svg_file.read()

            if output_format == 'png':
                cairosvg.svg2png(bytestring=svg_data, write_to=str(output_path))
            elif output_format in ['jpg', 'jpeg']:
                # CairoSVG doesn't directly output JPG, convert via PNG
                temp_png_path = output_path.with_suffix('.png')
                cairosvg.svg2png(bytestring=svg_data, write_to=str(temp_png_path))
                message, final_path = self._image_to_image(str(temp_png_path), 'jpeg') # Use jpeg internally
                temp_png_path.unlink() # Delete temporary PNG
                if final_path:
                     output_path = Path(final_path) # Update output path
                else:
                    raise ValueError("Failed intermediate PNG to JPG conversion")
            elif output_format == 'pdf':
                cairosvg.svg2pdf(bytestring=svg_data, write_to=str(output_path))
            else:
                 return f"Unsupported output format for SVG: {output_format}", None

            Logger.log(f"Converted SVG to {output_format}: {output_path}", "CONVERTER")
            return f"Converted to {output_format.upper()}, Boss.", str(output_path)
        except Exception as e:
            Logger.log(f"SVG conversion failed: {e}", "ERROR")
            return f"SVG conversion failed: {e}", None

    # --- Compression Methods ---

    def _compress_image(self, image_path: str, quality_percent: int) -> tuple:
        """Compress JPG or PNG file using Pillow."""
        username = os.getenv("Username", "Boss")
        output_path = self.data_folder / f"{Path(image_path).stem}_compressed{Path(image_path).suffix}"
        img_format = Path(image_path).suffix.lower()

        try:
            img = Image.open(image_path)
            original_size = Path(image_path).stat().st_size

            if img_format == '.png':
                Logger.log("Compressing PNG (lossless optimization)...", "CONVERTER")
                img.save(str(output_path), "PNG", optimize=True, compress_level=9)
            elif img_format in ['.jpg', '.jpeg']:
                Logger.log(f"Compressing JPEG with quality={quality_percent}...", "CONVERTER")
                if img.mode == 'RGBA':
                     rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                     rgb_img.paste(img, mask=img.split()[3])
                     img = rgb_img
                elif img.mode != 'RGB':
                     img = img.convert('RGB')
                img.save(str(output_path), "JPEG", quality=quality_percent, optimize=True)
            else:
                 return f"Compression not supported for {img_format}", None

            compressed_size = output_path.stat().st_size
            if original_size > 0:
                 reduction = ((original_size - compressed_size) / original_size) * 100
                 message = f"Compressed by {reduction:.1f}%, Boss."
                 Logger.log(f"Image compressed by {reduction:.1f}%: {output_path}", "CONVERTER")
            else:
                message = f"Compressed image saved, Boss (original size was 0)."
                Logger.log(f"Image compressed (original 0 bytes): {output_path}", "CONVERTER")

            return message, str(output_path)
        except Exception as e:
            Logger.log(f"Image compression failed: {e}", "ERROR")
            return f"Image compression failed: {e}", None

    def _compress_pdf(self, pdf_path: str, quality_percent: int) -> tuple:
        """Compress PDF file using pypdf."""
        username = os.getenv("Username", "Boss")
        if not PYPDF_AVAILABLE:
            return f"PDF compression requires pypdf library, Boss.", None

        output_path = self.data_folder / f"{Path(pdf_path).stem}_compressed.pdf"
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            original_size = Path(pdf_path).stat().st_size

            for page in reader.pages:
                page.compress_content_streams() # Basic lossless compression
                writer.add_page(page)

            with open(str(output_path), "wb") as f:
                writer.write(f)

            compressed_size = output_path.stat().st_size
            if original_size > 0:
                reduction = ((original_size - compressed_size) / original_size) * 100
                message = f"Compressed PDF by {reduction:.1f}%, Boss."
                Logger.log(f"PDF compressed by {reduction:.1f}%: {output_path}", "CONVERTER")
            else:
                 message = f"Compressed PDF saved, Boss (original size was 0)."
                 Logger.log(f"PDF compressed (original 0 bytes): {output_path}", "CONVERTER")

            return message, str(output_path)
        except Exception as e:
            Logger.log(f"PDF compression failed: {e}", "ERROR")
            return f"PDF compression failed: {e}", None

    def _compress_svg(self, svg_path: str, quality_percent: int) -> tuple:
        """Compress SVG file (basic whitespace/indent removal)."""
        username = os.getenv("Username", "Boss")
        output_path = self.data_folder / f"{Path(svg_path).stem}_compressed.svg"
        try:
            original_size = Path(svg_path).stat().st_size
            tree = ET.parse(svg_path)
            ET.indent(tree, space="")
            tree.write(str(output_path), encoding='utf-8', xml_declaration=True)

            compressed_size = output_path.stat().st_size
            if original_size > 0:
                reduction = ((original_size - compressed_size) / original_size) * 100
                message = f"Compressed SVG by {reduction:.1f}%, Boss."
                Logger.log(f"SVG compressed by {reduction:.1f}%: {output_path}", "CONVERTER")
            else:
                 message = f"Compressed SVG saved, Boss (original size was 0)."
                 Logger.log(f"SVG compressed (original 0 bytes): {output_path}", "CONVERTER")

            return message, str(output_path)
        except Exception as e:
            Logger.log(f"SVG compression failed: {e}", "ERROR")
            return f"SVG compression failed: {e}", None

    # --- MOVED: convert_active_document ---
    def convert_active_document(self, output_format: str) -> tuple[str, str]:
        """
        Convert currently active Word/PowerPoint document (Windows only).

        Args:
            output_format: Desired format (pdf, docx, pptx).

        Returns:
            Tuple of (response message, output path or None).
        """
        username = os.getenv("Username", "Boss")
        if not WIN32_AVAILABLE:
            return f"Active document conversion requires Windows, Office, pywin32, and pygetwindow, Boss.", None

        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return f"Could not identify an active window, Boss.", None

            title = active_window.title.lower()
            file_path = None
            app_name = None

            if "word" in title:
                Logger.log("Active app detected: Word", "CONVERTER")
                app_name = "Word"
                try:
                    word = win32com.client.GetActiveObject("Word.Application")
                    if word.Documents.Count > 0:
                        file_path = word.ActiveDocument.FullName
                    else:
                        return f"No active document found in Word, Boss.", None
                except Exception as e:
                    return f"Could not connect to Word: {e}", None

            elif "powerpoint" in title:
                Logger.log("Active app detected: PowerPoint", "CONVERTER")
                app_name = "PowerPoint"
                try:
                    powerpoint = win32com.client.GetActiveObject("PowerPoint.Application")
                    if powerpoint.Presentations.Count > 0:
                        file_path = powerpoint.ActivePresentation.FullName
                    else:
                        return f"No active presentation found in PowerPoint, Boss.", None
                except Exception as e:
                    return f"Could not connect to PowerPoint: {e}", None
            else:
                return f"Active window is not Word or PowerPoint, Boss.", None

            if file_path:
                Logger.log(f"Found active document: {file_path}", "CONVERTER")
                # Call the appropriate conversion method
                input_ext = Path(file_path).suffix.lower()
                output_format_clean = output_format.lower().replace('.', '')

                if input_ext == '.docx' and output_format_clean == 'pdf':
                    return self._docx_to_pdf(file_path)
                elif input_ext == '.pptx' and output_format_clean == 'pdf':
                    return self._pptx_to_pdf(file_path)
                else:
                    return f"Conversion from active {input_ext} to {output_format_clean} not supported, Boss.", None
            else:
                # This case should ideally be handled above, but as a fallback:
                return f"Could not get the file path of the active document, Boss.", None

        except Exception as e:
            Logger.log(f"Error in convert_active_document: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return f"Error converting active document: {e}", None


# Global instance
file_converter = FileConverter()

# --- REMOVED: Global convert_active_document function ---
# The function is now a method of the FileConverter class.