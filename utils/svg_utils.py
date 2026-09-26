import wx
import wx.svg
import tempfile
import os
import xml.etree.ElementTree as ET

def load_svg_as_bitmap(
        svg_path_or_string,
        color_hex="#A0A5AF",
        size=(20, 20),
        is_file=True
):
    temp_file_path = None

    try:
        # 1. Parsing SVG sebagai struktur XML
        if is_file:
            tree = ET.parse(svg_path_or_string)
            root = tree.getroot()
        else:
            root = ET.fromstring(svg_path_or_string)

        # Hapus namespace SVG agar manipulasi atribut lebih mudah
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # 2. Cek jenis ikon (Line-art vs Solid Fill)
        # Ambil atribut fill/stroke dari root <svg>
        root_fill = root.attrib.get('fill', '').lower()
        root_stroke = root.attrib.get('stroke', '').lower()

        is_line_art = root_stroke != '' and root_stroke != 'none'

        if is_line_art:
            # Jika ini ikon garis/line-art (seperti Lucide/Feather 24x24):
            root.attrib['stroke'] = color_hex
            # Pastikan fill tetap 'none' agar bagian tengah ikon tidak memblok warna
            root.attrib['fill'] = 'none'
        else:
            # Jika ini ikon blok/solid fill:
            root.attrib['fill'] = color_hex

        # 3. Timpa atribut pada seluruh elemen anak jika ada warna yang mengunci (hardcoded)
        for elem in root.iter():
            if 'stroke' in elem.attrib and elem.attrib['stroke'] != 'none':
                elem.attrib['stroke'] = color_hex
            if 'fill' in elem.attrib and elem.attrib['fill'] != 'none':
                elem.attrib['fill'] = color_hex

        # 4. Simpan XML yang telah diperbaiki ke temp file
        svg_xml_str = ET.tostring(root, encoding='utf-8')

        with tempfile.NamedTemporaryFile('wb', delete=False, suffix='.svg') as tf:
            tf.write(svg_xml_str)
            temp_file_path = tf.name

        # 5. Load dan Render menggunakan wx.svg
        svg_obj = wx.svg.SVGimage.CreateFromFile(temp_file_path)

        # Konversi ke wx.Bitmap dengan ukuran target
        if hasattr(svg_obj, 'ConvertToScaledBitmap'):
            bitmap = svg_obj.ConvertToScaledBitmap(wx.Size(size[0], size[1]))
        else:
            bmp_orig = svg_obj.ConvertToBitmap()
            img = bmp_orig.ConvertToImage()
            img = img.Scale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
            bitmap = img.ConvertToBitmap()

        return bitmap

    except Exception as e:
        print(f"[SVG Utils Error] {e}")
        return wx.Bitmap(size[0], size[1])

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except PermissionError:
                pass
        


    
