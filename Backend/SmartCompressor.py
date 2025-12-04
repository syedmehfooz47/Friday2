# -*- coding: utf-8 -*-
"""
Smart File Compressor - Advanced compression for all file types
Supports: Images (JPG, PNG, WEBP, GIF), PDFs, Office docs (DOCX, XLSX, PPTX), and archives
Features: Smart auto-compression, target size, target percentage, quality preservation
"""

import os
import io
import sys
import zipfile
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv
from .logger import Logger

load_dotenv()

# --- Dependency Checks ---
PILLOW_AVAILABLE = False
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    Logger.log("Pillow not installed. Image compression disabled.", "WARNING")

PYPDF_AVAILABLE = False
try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    Logger.log("pypdf not installed. PDF compression disabled.", "WARNING")

# Check for advanced PDF compression with pikepdf (better compression)
PIKEPDF_AVAILABLE = False
try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
    Logger.log("pikepdf available for advanced PDF compression.", "COMPRESSOR")
except ImportError:
    Logger.log("pikepdf not installed. Using basic PDF compression. Install with: pip install pikepdf", "INFO")

# Check for Office document compression
PYTHON_DOCX_AVAILABLE = False
try:
    from docx import Document
    PYTHON_DOCX_AVAILABLE = True
    Logger.log("python-docx available for DOCX compression.", "COMPRESSOR")
except ImportError:
    Logger.log("python-docx not installed. DOCX compression limited.", "INFO")

OPENPYXL_AVAILABLE = False
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
    Logger.log("openpyxl available for XLSX compression.", "COMPRESSOR")
except ImportError:
    Logger.log("openpyxl not installed. XLSX compression limited.", "INFO")

PPTX_AVAILABLE = False
try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
    Logger.log("python-pptx available for PPTX compression.", "COMPRESSOR")
except ImportError:
    Logger.log("python-pptx not installed. PPTX compression limited.", "INFO")


class SmartCompressor:
    """
    Advanced file compressor with intelligent compression algorithms.
    
    Supports:
    - Images: JPG, PNG, WEBP, GIF, BMP, TIFF
    - Documents: PDF, DOCX, XLSX, PPTX
    - Archives: ZIP (recompress with better settings)
    
    Modes:
    - auto: Smart compression that balances quality and size (recommended)
    - percentage: Reduce file size by a target percentage
    - target_size: Reduce to a specific file size in KB/MB
    - quality: Set specific quality level (1-100)
    """
    
    # Quality presets for different compression levels
    QUALITY_PRESETS = {
        'maximum': {'jpg': 95, 'png': 9, 'webp': 95, 'pdf': 95, 'description': 'Highest quality, minimal compression'},
        'high': {'jpg': 85, 'png': 7, 'webp': 85, 'pdf': 85, 'description': 'High quality, good compression'},
        'balanced': {'jpg': 75, 'png': 6, 'webp': 75, 'pdf': 75, 'description': 'Balanced quality and size'},
        'medium': {'jpg': 60, 'png': 5, 'webp': 60, 'pdf': 60, 'description': 'Medium quality, good size reduction'},
        'aggressive': {'jpg': 45, 'png': 4, 'webp': 45, 'pdf': 45, 'description': 'Lower quality, maximum compression'},
    }
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.output_folder = self.project_root / "Data" / "CompressedFiles"
        self.output_folder.mkdir(parents=True, exist_ok=True)
        Logger.log(f"SmartCompressor initialized. Output: {self.output_folder}", "COMPRESSOR")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def _parse_target_size(self, target: str) -> Optional[int]:
        """Parse target size string like '500KB', '2MB' to bytes"""
        target = target.upper().strip()
        try:
            if 'GB' in target:
                return int(float(target.replace('GB', '').strip()) * 1024 * 1024 * 1024)
            elif 'MB' in target:
                return int(float(target.replace('MB', '').strip()) * 1024 * 1024)
            elif 'KB' in target:
                return int(float(target.replace('KB', '').strip()) * 1024)
            elif 'B' in target:
                return int(float(target.replace('B', '').strip()))
            else:
                # Assume KB if no unit
                return int(float(target) * 1024)
        except ValueError:
            return None
    
    def _get_smart_quality(self, file_type: str, original_size: int) -> Dict[str, Any]:
        """
        Intelligently determine compression settings based on file type and size.
        Aims for 40-60% size reduction while maintaining acceptable quality.
        """
        # Size thresholds in bytes
        SMALL = 100 * 1024  # 100 KB
        MEDIUM = 1 * 1024 * 1024  # 1 MB
        LARGE = 5 * 1024 * 1024  # 5 MB
        VERY_LARGE = 20 * 1024 * 1024  # 20 MB
        
        if file_type in ['jpg', 'jpeg']:
            if original_size < SMALL:
                return {'quality': 88, 'preset': 'high', 'expected_reduction': '10-20%'}
            elif original_size < MEDIUM:
                return {'quality': 82, 'preset': 'high', 'expected_reduction': '25-40%'}
            elif original_size < LARGE:
                return {'quality': 75, 'preset': 'balanced', 'expected_reduction': '40-55%'}
            else:
                return {'quality': 70, 'preset': 'balanced', 'expected_reduction': '50-65%'}
        
        elif file_type == 'png':
            # PNG uses compression level (0-9), not quality
            if original_size < SMALL:
                return {'compress_level': 6, 'preset': 'high', 'expected_reduction': '5-15%'}
            elif original_size < MEDIUM:
                return {'compress_level': 8, 'preset': 'balanced', 'expected_reduction': '15-30%'}
            else:
                return {'compress_level': 9, 'preset': 'balanced', 'expected_reduction': '20-40%'}
        
        elif file_type == 'webp':
            if original_size < MEDIUM:
                return {'quality': 85, 'preset': 'high', 'expected_reduction': '20-35%'}
            else:
                return {'quality': 78, 'preset': 'balanced', 'expected_reduction': '35-50%'}
        
        elif file_type == 'pdf':
            if original_size < MEDIUM:
                return {'quality': 85, 'preset': 'high', 'expected_reduction': '10-25%'}
            elif original_size < LARGE:
                return {'quality': 75, 'preset': 'balanced', 'expected_reduction': '25-45%'}
            else:
                return {'quality': 65, 'preset': 'medium', 'expected_reduction': '40-60%'}
        
        elif file_type in ['docx', 'xlsx', 'pptx']:
            if original_size < MEDIUM:
                return {'quality': 85, 'preset': 'high', 'expected_reduction': '15-30%'}
            else:
                return {'quality': 70, 'preset': 'balanced', 'expected_reduction': '30-50%'}
        
        else:
            return {'quality': 75, 'preset': 'balanced', 'expected_reduction': '20-40%'}
    
    def compress(
        self,
        input_path: str,
        mode: str = 'auto',
        target_percentage: int = None,
        target_size: str = None,
        quality: int = None,
        preset: str = None
    ) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """
        Compress a file with intelligent settings.
        
        Args:
            input_path: Path to file to compress
            mode: 'auto', 'percentage', 'target_size', 'quality', or 'preset'
            target_percentage: Target size reduction percentage (e.g., 50 = reduce by 50%)
            target_size: Target file size (e.g., '500KB', '2MB')
            quality: Direct quality setting (1-100)
            preset: Quality preset ('maximum', 'high', 'balanced', 'medium', 'aggressive')
        
        Returns:
            Tuple of (message, output_path, stats_dict)
        """
        username = os.getenv("Username", "Boss")
        input_file = Path(input_path).resolve()
        
        if not input_file.exists():
            return f"File not found: {input_path}", None, {}
        
        original_size = input_file.stat().st_size
        file_ext = input_file.suffix.lower().replace('.', '')
        
        Logger.log(f"Compressing '{input_file.name}' ({self._format_size(original_size)}) mode={mode}", "COMPRESSOR")
        
        # Determine compression settings based on mode
        settings = {}
        if mode == 'auto':
            settings = self._get_smart_quality(file_ext, original_size)
            Logger.log(f"Auto mode: Using preset '{settings.get('preset')}', expected {settings.get('expected_reduction')}", "COMPRESSOR")
        elif mode == 'preset' and preset:
            if preset in self.QUALITY_PRESETS:
                preset_settings = self.QUALITY_PRESETS[preset]
                settings['quality'] = preset_settings.get(file_ext if file_ext in preset_settings else 'jpg', 75)
                settings['preset'] = preset
            else:
                settings = self._get_smart_quality(file_ext, original_size)
        elif mode == 'quality' and quality:
            settings['quality'] = max(1, min(100, quality))
        elif mode == 'percentage' and target_percentage:
            # Calculate quality needed for target percentage reduction
            # This is approximate - we'll iterate if needed
            settings['target_percentage'] = target_percentage
            settings['quality'] = max(20, 100 - target_percentage)
        elif mode == 'target_size' and target_size:
            target_bytes = self._parse_target_size(target_size)
            if target_bytes and target_bytes < original_size:
                settings['target_bytes'] = target_bytes
                # Estimate initial quality
                ratio = target_bytes / original_size
                settings['quality'] = max(20, int(ratio * 100))
            else:
                return f"Invalid target size or target is larger than original, Boss.", None, {}
        else:
            # Default to auto
            settings = self._get_smart_quality(file_ext, original_size)
        
        # Route to appropriate compressor
        try:
            if file_ext in ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff']:
                result = self._compress_image(input_file, settings)
            elif file_ext == 'pdf':
                result = self._compress_pdf(input_file, settings)
            elif file_ext == 'docx':
                result = self._compress_docx(input_file, settings)
            elif file_ext == 'xlsx':
                result = self._compress_xlsx(input_file, settings)
            elif file_ext == 'pptx':
                result = self._compress_pptx(input_file, settings)
            elif file_ext == 'zip':
                result = self._recompress_zip(input_file, settings)
            else:
                # Generic compression - wrap in zip
                result = self._compress_generic(input_file, settings)
            
            if result[1]:  # If successful
                compressed_size = Path(result[1]).stat().st_size
                reduction = ((original_size - compressed_size) / original_size) * 100
                stats = {
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction_percent': round(reduction, 1),
                    'original_formatted': self._format_size(original_size),
                    'compressed_formatted': self._format_size(compressed_size),
                    'settings': settings
                }
                
                message = f"Compressed '{input_file.name}' from {stats['original_formatted']} to {stats['compressed_formatted']} ({reduction:.1f}% reduction), Boss."
                Logger.log(message, "COMPRESSOR")
                return message, result[1], stats
            else:
                return result[0], None, {}
                
        except Exception as e:
            Logger.log(f"Compression error: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return f"Compression failed: {e}", None, {}
    
    def _compress_image(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Compress image with smart quality settings"""
        if not PILLOW_AVAILABLE:
            return "Image compression requires Pillow library, Boss.", None
        
        file_ext = input_file.suffix.lower().replace('.', '')
        output_path = self.output_folder / f"{input_file.stem}_compressed{input_file.suffix}"
        
        try:
            img = Image.open(str(input_file))
            original_mode = img.mode
            
            # Get quality setting
            quality = settings.get('quality', 75)
            compress_level = settings.get('compress_level', 6)
            
            # Handle target size with iterative compression
            target_bytes = settings.get('target_bytes')
            target_percentage = settings.get('target_percentage')
            
            if file_ext in ['jpg', 'jpeg']:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                if target_bytes:
                    # Iterative compression to reach target size
                    quality = self._find_optimal_quality_jpeg(img, target_bytes, output_path)
                elif target_percentage:
                    original_size = input_file.stat().st_size
                    target = int(original_size * (1 - target_percentage / 100))
                    quality = self._find_optimal_quality_jpeg(img, target, output_path)
                
                img.save(str(output_path), 'JPEG', quality=quality, optimize=True, progressive=True)
            
            elif file_ext == 'png':
                # PNG uses lossless compression
                img.save(str(output_path), 'PNG', optimize=True, compress_level=compress_level)
                
                # If target size specified and PNG is too large, convert to optimized PNG
                if target_bytes and output_path.stat().st_size > target_bytes:
                    # Try quantizing colors for smaller size
                    if img.mode == 'RGBA':
                        img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                    img.save(str(output_path), 'PNG', optimize=True, compress_level=9)
            
            elif file_ext == 'webp':
                img.save(str(output_path), 'WEBP', quality=quality, optimize=True, method=6)
            
            elif file_ext == 'gif':
                img.save(str(output_path), 'GIF', optimize=True)
            
            elif file_ext in ['bmp', 'tiff']:
                # Convert to more efficient format for compression
                if file_ext == 'bmp':
                    output_path = output_path.with_suffix('.png')
                    img.save(str(output_path), 'PNG', optimize=True, compress_level=9)
                else:
                    img.save(str(output_path), 'TIFF', compression='tiff_lzw')
            
            return f"Image compressed successfully", str(output_path)
            
        except Exception as e:
            Logger.log(f"Image compression error: {e}", "ERROR")
            return f"Image compression failed: {e}", None
    
    def _find_optimal_quality_jpeg(self, img: Image.Image, target_bytes: int, output_path: Path) -> int:
        """Binary search to find optimal JPEG quality for target size"""
        low, high = 10, 95
        best_quality = 75
        
        for _ in range(8):  # Max 8 iterations
            mid = (low + high) // 2
            
            buffer = io.BytesIO()
            img.save(buffer, 'JPEG', quality=mid, optimize=True)
            size = buffer.tell()
            
            if size <= target_bytes:
                best_quality = mid
                low = mid + 1
            else:
                high = mid - 1
            
            if abs(size - target_bytes) < target_bytes * 0.05:  # Within 5%
                break
        
        return best_quality
    
    def _compress_pdf(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Compress PDF with advanced settings"""
        output_path = self.output_folder / f"{input_file.stem}_compressed.pdf"
        quality = settings.get('quality', 75)
        
        # Try pikepdf first (better compression)
        if PIKEPDF_AVAILABLE:
            try:
                with pikepdf.open(str(input_file)) as pdf:
                    # Remove unnecessary metadata
                    if '/Metadata' in pdf.Root:
                        del pdf.Root['/Metadata']
                    
                    # Compress streams
                    pdf.save(
                        str(output_path),
                        compress_streams=True,
                        stream_decode_level=pikepdf.StreamDecodeLevel.specialized,
                        object_stream_mode=pikepdf.ObjectStreamMode.generate,
                        recompress_flate=True,
                        linearize=True
                    )
                return "PDF compressed with pikepdf", str(output_path)
            except Exception as e:
                Logger.log(f"pikepdf compression failed, trying pypdf: {e}", "WARNING")
        
        # Fallback to pypdf
        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(str(input_file))
                writer = PdfWriter()
                
                for page in reader.pages:
                    page.compress_content_streams()
                    writer.add_page(page)
                
                # Remove metadata for smaller size
                writer.add_metadata({})
                
                with open(str(output_path), 'wb') as f:
                    writer.write(f)
                
                return "PDF compressed with pypdf", str(output_path)
            except Exception as e:
                Logger.log(f"pypdf compression failed: {e}", "ERROR")
                return f"PDF compression failed: {e}", None
        
        return "PDF compression requires pypdf or pikepdf library, Boss.", None
    
    def _compress_docx(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Compress DOCX by recompressing embedded images and optimizing XML"""
        output_path = self.output_folder / f"{input_file.stem}_compressed.docx"
        quality = settings.get('quality', 75)
        
        try:
            # DOCX is a ZIP file - we can recompress it
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract DOCX
                with zipfile.ZipFile(str(input_file), 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Compress images in the media folder
                media_folder = temp_path / 'word' / 'media'
                if media_folder.exists() and PILLOW_AVAILABLE:
                    for img_file in media_folder.iterdir():
                        if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                            self._compress_embedded_image(img_file, quality)
                
                # Repack with maximum compression
                with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_out:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zip_out.write(file_path, arcname)
            
            return "DOCX compressed successfully", str(output_path)
            
        except Exception as e:
            Logger.log(f"DOCX compression error: {e}", "ERROR")
            return f"DOCX compression failed: {e}", None
    
    def _compress_xlsx(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Compress XLSX by optimizing and recompressing"""
        output_path = self.output_folder / f"{input_file.stem}_compressed.xlsx"
        quality = settings.get('quality', 75)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract XLSX
                with zipfile.ZipFile(str(input_file), 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Compress images if present
                media_folder = temp_path / 'xl' / 'media'
                if media_folder.exists() and PILLOW_AVAILABLE:
                    for img_file in media_folder.iterdir():
                        if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                            self._compress_embedded_image(img_file, quality)
                
                # Repack with maximum compression
                with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_out:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zip_out.write(file_path, arcname)
            
            return "XLSX compressed successfully", str(output_path)
            
        except Exception as e:
            Logger.log(f"XLSX compression error: {e}", "ERROR")
            return f"XLSX compression failed: {e}", None
    
    def _compress_pptx(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Compress PPTX by compressing embedded images"""
        output_path = self.output_folder / f"{input_file.stem}_compressed.pptx"
        quality = settings.get('quality', 75)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract PPTX
                with zipfile.ZipFile(str(input_file), 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Compress images in media folder (PPTX often has large images)
                media_folder = temp_path / 'ppt' / 'media'
                if media_folder.exists() and PILLOW_AVAILABLE:
                    for img_file in media_folder.iterdir():
                        if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.tiff']:
                            self._compress_embedded_image(img_file, quality)
                
                # Repack with maximum compression
                with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_out:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zip_out.write(file_path, arcname)
            
            return "PPTX compressed successfully", str(output_path)
            
        except Exception as e:
            Logger.log(f"PPTX compression error: {e}", "ERROR")
            return f"PPTX compression failed: {e}", None
    
    def _compress_embedded_image(self, img_path: Path, quality: int):
        """Compress an embedded image in-place"""
        try:
            img = Image.open(str(img_path))
            
            if img_path.suffix.lower() in ['.jpg', '.jpeg']:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(str(img_path), 'JPEG', quality=quality, optimize=True)
            elif img_path.suffix.lower() == '.png':
                img.save(str(img_path), 'PNG', optimize=True, compress_level=9)
            elif img_path.suffix.lower() == '.gif':
                img.save(str(img_path), 'GIF', optimize=True)
                
        except Exception as e:
            Logger.log(f"Failed to compress embedded image {img_path.name}: {e}", "WARNING")
    
    def _recompress_zip(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Recompress ZIP archive with maximum compression"""
        output_path = self.output_folder / f"{input_file.stem}_compressed.zip"
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract
                with zipfile.ZipFile(str(input_file), 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Repack with maximum compression
                with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_out:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zip_out.write(file_path, arcname)
            
            return "ZIP recompressed successfully", str(output_path)
            
        except Exception as e:
            Logger.log(f"ZIP recompression error: {e}", "ERROR")
            return f"ZIP recompression failed: {e}", None
    
    def _compress_generic(self, input_file: Path, settings: Dict) -> Tuple[str, Optional[str]]:
        """Compress any file by wrapping in optimized ZIP"""
        output_path = self.output_folder / f"{input_file.stem}_compressed.zip"
        
        try:
            with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_out:
                zip_out.write(str(input_file), input_file.name)
            
            return "File compressed to ZIP", str(output_path)
            
        except Exception as e:
            Logger.log(f"Generic compression error: {e}", "ERROR")
            return f"Compression failed: {e}", None
    
    def get_compression_info(self, file_path: str) -> Dict[str, Any]:
        """Get compression recommendations for a file"""
        input_file = Path(file_path).resolve()
        
        if not input_file.exists():
            return {'error': 'File not found'}
        
        file_ext = input_file.suffix.lower().replace('.', '')
        original_size = input_file.stat().st_size
        
        settings = self._get_smart_quality(file_ext, original_size)
        
        return {
            'file_name': input_file.name,
            'file_type': file_ext,
            'original_size': original_size,
            'original_size_formatted': self._format_size(original_size),
            'recommended_preset': settings.get('preset', 'balanced'),
            'expected_reduction': settings.get('expected_reduction', '20-40%'),
            'supported': file_ext in ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'pdf', 'docx', 'xlsx', 'pptx', 'zip'],
            'presets_available': list(self.QUALITY_PRESETS.keys())
        }


# Global instance
smart_compressor = SmartCompressor()
