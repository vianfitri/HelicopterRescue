import os
import re
import xml.etree.ElementTree as ET

def rescale_svg_baked(input_path: str, output_path: str, target_w: float = 100.0, target_h: float = 100.0):
    """
    Mentranslasikan seluruh koordinat internal SVG (elemen <path>, <rect>, <circle>, dll)
    ke ukuran target secara permanen ("baking" koordinat).
    """
    # Register namespace SVG agar hasil XML tetap bersih
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Ambil ukuran asli (default 16 jika tidak ditemukan)
    old_w = float(root.attrib.get('width', 16))
    old_h = float(root.attrib.get('height', 16))

    scale_x = target_w / old_w
    scale_y = target_h / old_h

    # Regex untuk menemukan semua angka desimal/integer dalam string koordinat
    num_pattern = re.compile(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?')

    def scale_path_d(d_string, sx, sy):
        """Mengalikan angka koordinat x dan y di dalam atribut d='...'"""
        tokens = re.split(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', d_string)
        result = []
        is_x = True # Alternasi koordinating X dan Y
        
        for token in tokens:
            if num_pattern.fullmatch(token):
                val = float(token)
                # Kalikan sesuai sumbu X atau Y
                new_val = val * sx if is_x else val * sy
                # Format angka hingga max 4 desimal agar rapi
                result.append(f"{new_val:.4f}".rstrip('0').rstrip('.'))
                is_x = not is_x
            else:
                # Jika huruf perintah SVG (M, L, C, Z, dll), reset giliran koordinat ke X
                if any(c.isalpha() for c in token):
                    is_x = True
                result.append(token)
        return "".join(result)

    # Iterasi seluruh elemen di dalam SVG
    for elem in root.iter():
        # Clean tag name dari namespace
        tag = elem.tag.split('}')[-1]

        # 1. Scaling elemen <path d="...">
        if 'd' in elem.attrib:
            elem.attrib['d'] = scale_path_d(elem.attrib['d'], scale_x, scale_y)

        # 2. Scaling elemen dasar seperti <rect>, <circle>, <line>
        for attr_x in ['x', 'cx', 'x1', 'x2', 'width', 'rx']:
            if attr_x in elem.attrib:
                try:
                    elem.attrib[attr_x] = str(round(float(elem.attrib[attr_x]) * scale_x, 4))
                except ValueError:
                    pass

        for attr_y in ['y', 'cy', 'y1', 'y2', 'height', 'ry']:
            if attr_y in elem.attrib:
                try:
                    elem.attrib[attr_y] = str(round(float(elem.attrib[attr_y]) * scale_y, 4))
                except ValueError:
                    pass

        # 3. Scaling stroke-width jika ada
        if 'stroke-width' in elem.attrib:
            try:
                elem.attrib['stroke-width'] = str(round(float(elem.attrib['stroke-width']) * scale_x, 4))
            except ValueError:
                pass

    # Update atribut <svg> utama
    root.attrib['width'] = str(int(target_w) if target_w.is_integer() else target_w)
    root.attrib['height'] = str(int(target_h) if target_h.is_integer() else target_h)
    root.attrib['viewBox'] = f"0 0 {target_w} {target_h}"

    # Simpan kembali sebagai file SVG valid
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Sukses! SVG berhasil di-baked ke ukuran {target_w}x{target_h}: {output_path}")

# --- Cara Penggunaan ---
if __name__ == "__main__":
    file_input = "debug_connected.svg"
    file_output = "debug_connected_100x100_baked.svg"

    rescale_svg_baked(file_input, file_output, target_w=100.0, target_h=100.0)