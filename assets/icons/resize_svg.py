import os
from svgelements import SVG, Path, Matrix

def generate_sample_svg(filepath: str):
    """Membuat file SVG sampel 16x16 untuk pengujian."""
    sample_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <rect x="2" y="2" width="12" height="12" rx="2" fill="none" stroke="black" stroke-width="1"/>
  <path d="M 4 8 L 7 11 L 12 5" stroke="red" stroke-width="1" fill="none"/>
</svg>'''
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(sample_content)
    print(f"File sampel berhasil dibuat: {filepath}")

def rescale_svg_coordinates(input_path: str, output_path: str, target_w: float = 100.0, target_h: float = 100.0):
    """Mengalikan seluruh nilai koordinat internal SVG ke ukuran target."""
    svg = SVG.parse(input_path)

    # Ambil dimensi asli (default ke 16.0 jika atribut tidak ditemukan)
    old_w = float(svg.width) if svg.width is not None else 16.0
    old_h = float(svg.height) if svg.height is not None else 16.0

    # Hitung rasio perkalian koordinat
    scale_x = target_w / old_w
    scale_y = target_h / old_h

    transform_matrix = Matrix.scale(scale_x, scale_y)

    # Mentranslasikan koordinat titik pada setiap elemen SVG secara matematis
    for element in svg:
        if isinstance(element, Path):
            element *= transform_matrix
            element.transform.reset()
        elif hasattr(element, "apply_transform"):
            element *= transform_matrix
            if hasattr(element, "transform"):
                element.transform.reset()

    # Perbarui ukuran dokumen utama
    svg.width = target_w
    svg.height = target_h
    svg.viewbox = f"0 0 {target_w} {target_h}"

    # Simpan hasil ke file baru
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg.string())

    print(f"Proses translasi selesai: {output_path}")
    print(f"Ukuran baru: {target_w}×{target_h} (faktor skala: {scale_x}×)")

if __name__ == "__main__":
    file_input = "icon_16x16.svg"
    file_output = "icon_100x100_baked.svg"

    # Buat file icon_16x16.svg jika file belum ada di folder kerja
    if not os.path.exists(file_input):
        generate_sample_svg(file_input)

    # Eksekusi perubahan koordinat dari 16x16 ke 100x100
    rescale_svg_coordinates(file_input, file_output, target_w=100.0, target_h=100.0)