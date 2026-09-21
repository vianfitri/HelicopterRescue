from svgelements import SVG, Path, Matrix

def rescale_svg_coordinates(input_file, output_file, target_w=100, target_h=100):
    # Load SVG
    svg = SVG.parse(input_file)
    
    old_w = svg.width if svg.width is not None else 16
    old_h = svg.height if svg.height is not None else 16
    
    scale_x = target_w / old_w
    scale_y = target_h / old_h

    # Terapkan matriks transformasi skala ke seluruh elemen gambar
    transformation = Matrix.scale(scale_x, scale_y)
    
    for element in svg:
        if isinstance(element, Path):
            # Mengalikan koordinat titik-titik path secara matematis
            element *= transformation
            # Hapus atribut transform yang tersisa agar koordinatnya murni "baked"
            element.transform.reset()

    # Update ukuran dasar SVG
    svg.width = target_w
    svg.height = target_h
    svg.viewbox = f"0 0 {target_w} {target_h}"

    # Simpan ke file baru
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg.string())
        
    print(f"Koordinat angka pada SVG berhasil dikalikan dengan faktor {scale_x}x!")

# Contoh Penggunaan:
# rescale_svg_coordinates('icon_16x16.svg', 'icon_100x100_baked.svg', 100, 100)