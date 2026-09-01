import wx
import wx.svg
import re
import tempfile
import os

def load_svg_as_bitmap(
                svg_path_or_string,
                color_hex="#A0A5AF",
                size=(20, 20),
                is_file=True                                
):
    temp_file_path = None

    try:
        if is_file:
            with open(svg_path_or_string, 'r', encoding='utf-8') as f:
                svg_content = f.read()
        else:
            svg_content = svg_path_or_string

        # change fill attribute
        if 'fill=' in svg_content:
            svg_content = re.sub(r'fill="[^"]+"', f'fill="{color_hex}"', svg_content)
        else:
            svg_content = re.sub(r'<svg', f'<svg fill="{color_hex}"', svg_content, count=1)

        # change stroke attribut if svg line-art
        if 'stroke=' in svg_content:
            svg_content = re.sub(r'stroke="[^"]+"', f'stroke="{color_hex}"', svg_content)

        # write svg string to temp file
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.svg', encoding='utf-8') as tf:
            tf.write(svg_content)
            temp_file_path = tf.name

        # load svg with SVGImage.CreateFromFile
        svg_obj = wx.svg.SVGimage.CreateFromFile(temp_file_path)

        # render to wx.Bitmap
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
            os.remove(temp_file_path)
        


    
