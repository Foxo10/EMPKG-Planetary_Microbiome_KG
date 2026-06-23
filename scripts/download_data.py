"""
download_data.py

Descarga los archivos iniciales de EMP Release 1 para la fase de exploración:

- emp_qiime_mapping_subset_2k.tsv
- emp_deblur_90bp.subset_2k.rare_5000.biom

Uso:
    python scripts/download_data.py
"""

from pathlib import Path

import requests
from tqdm import tqdm

BASE_URL = "https://ftp.microbio.me/emp/release1"
DATA_RAW = Path("data/raw/emp/release1")


FILES = {
    "mapping_files/emp_qiime_mapping_subset_2k.tsv":
        DATA_RAW / "mapping_files" / "emp_qiime_mapping_subset_2k.tsv",

    "otu_tables/deblur/emp_deblur_90bp.subset_2k.rare_5000.biom":
        DATA_RAW / "otu_tables" / "deblur" / "emp_deblur_90bp.subset_2k.rare_5000.biom",
}


def download_file(url: str, output_path: Path) -> None:
    """Descarga un archivo usando HTTP/HTTPS."""
    if output_path.exists() and output_path.stat().st_size > 0:
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"Ya existe: {output_path} ({size_mb:.1f} MB)")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print(f"\nDescargando: {url}")
        print(f"Destino: {output_path}")

        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with output_path.open("wb") as file:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=output_path.name,

            ) as bar:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
                        bar.update(len(chunk))

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar {url}: {e}")
        if output_path.is_file():
            output_path.unlink()


def main() -> None:
    for rel_url, output_path in FILES.items():
        url = f"{BASE_URL}/{rel_url}"
        download_file(url, output_path)


if __name__ == "__main__":
    main()
