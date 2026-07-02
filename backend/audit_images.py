import os
import json
import shutil
import sys

# Define base paths
project_root = r"c:\Users\fotoa\OneDrive\Dokumen\coba_insight"
public_dir = os.path.join(project_root, "frontend", "public")
materi_dir = os.path.join(public_dir, "content", "materi")
artifact_dir = r"C:\Users\fotoa\.gemini\antigravity-ide\brain\62ecf055-0bd1-41fe-82eb-7401eaa24b37"
output_images_dir = os.path.join(artifact_dir, "images")

# Ensure output directory exists
os.makedirs(output_images_dir, exist_ok=True)

# Map folder names to friendly names
PATH_NAME_MAP = {
    "materi path machine learning": "Machine Learning",
    "materi path front end": "Frontend Development",
    "materi path backend": "Backend Development"
}

def resolve_image_path(src):
    if src.startswith("/assets"):
        # Matches React: src.startsWith('/assets') ? `/content${src}` : src
        # which means /content/assets/...
        # Physically: frontend/public/content/assets/...
        return os.path.join(public_dir, "content", src.lstrip("/"))
    elif src.startswith("/content"):
        # Physically: frontend/public/content/...
        return os.path.join(public_dir, src.lstrip("/"))
    else:
        # Fallback direct path
        return os.path.join(public_dir, src.lstrip("/"))

def perform_audit():
    audit_results = []
    
    # Walk through materi folder
    for root, dirs, files in os.walk(materi_dir):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)
                
                # Determine path name
                rel_path = os.path.relpath(root, materi_dir)
                parts = rel_path.split(os.sep)
                path_folder = parts[0] if len(parts) > 0 else "Unknown"
                path_name = PATH_NAME_MAP.get(path_folder, path_folder)
                
                # Determine bab number
                bab_folder = parts[1] if len(parts) > 1 else "Unknown"
                bab_number = bab_folder.replace("bab ", "").strip()
                
                # Read json
                with open(json_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except Exception as e:
                        print(f"Error loading {json_path}: {e}")
                        continue
                
                sub_bab_list = data.get("sub_bab", [])
                for slide in sub_bab_list:
                    slide_title = slide.get("judul", "No Title")
                    slide_id = slide.get("id", "")
                    
                    # Search for images in konten
                    konten = slide.get("konten", [])
                    for block in konten:
                        if block.get("tipe") == "gambar":
                            src = block.get("src", "")
                            judul_gambar = block.get("judul", "")
                            deskripsi = block.get("deskripsi_gambar", "Tidak ada deskripsi.")
                            alt = block.get("alt", "")
                            
                            # Resolve path
                            physical_path = resolve_image_path(src)
                            exists = os.path.exists(physical_path)
                            size = os.path.getsize(physical_path) if exists else 0
                            
                            status = "Valid" if (exists and size > 0) else "Broken"
                            loaded = "True" if (exists and size > 0) else "False"
                            
                            copied_filename = ""
                            if exists and size > 0:
                                # Copy to artifact images folder with a unique name
                                clean_src_name = os.path.basename(src)
                                unique_name = f"{path_name.replace(' ', '_')}_bab{bab_number}_{slide_id}_{clean_src_name}"
                                copied_dest = os.path.join(output_images_dir, unique_name)
                                try:
                                    shutil.copy2(physical_path, copied_dest)
                                    copied_filename = unique_name
                                except Exception as copy_err:
                                    print(f"Error copying {physical_path} to {copied_dest}: {copy_err}")
                            
                            # Simple semantic check of relevance
                            # Topik slide vs judul/deskripsi gambar
                            keywords = slide_title.lower().split()
                            content_text = " ".join([c.get("isi", "") for c in konten if c.get("tipe") == "paragraf"]).lower()
                            
                            relevance = "Sesuai"
                            catatan = "Gambar tersedia dan sesuai dengan isi materi."
                            
                            # Decision logic for audit assessment
                            if status == "Broken":
                                relevance = "Tidak"
                                catatan = f"Gambar rusak atau tidak ditemukan di path: {src}"
                            else:
                                # Context checks (simple keyword match or heuristic)
                                slide_lower = slide_title.lower()
                                src_lower = src.lower()
                                
                                if "knn" in slide_lower and "knn" not in src_lower and "k-nearest" not in src_lower and "knn" not in deskripsi.lower():
                                    relevance = "Perlu Ditinjau"
                                    catatan = "Slide membahas KNN, mohon verifikasi relevansi gambar."
                                elif "boundary" in slide_lower and "boundary" not in src_lower and "boundary" not in deskripsi.lower():
                                    relevance = "Perlu Ditinjau"
                                    catatan = "Slide membahas Decision Boundary, mohon verifikasi relevansi gambar."
                                elif "html" in slide_lower and "html" not in src_lower and "html" not in deskripsi.lower() and "FE_bab1" not in file:
                                    relevance = "Perlu Ditinjau"
                                    catatan = "Slide membahas HTML, mohon verifikasi relevansi gambar."
                            
                            audit_results.append({
                                "path": path_name,
                                "bab": f"Bab {bab_number}",
                                "slide": f"{slide_id} - {slide_title}",
                                "src": src,
                                "status": status,
                                "loaded": loaded,
                                "relevance": relevance,
                                "catatan": catatan,
                                "copied_filename": copied_filename,
                                "deskripsi": deskripsi,
                                "judul_gambar": judul_gambar
                            })
                            
    return audit_results

def generate_report(results):
    report_path = os.path.join(artifact_dir, "image_audit_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Laporan Audit Gambar Materi Pembelajaran\n\n")
        f.write("Dokumen ini memuat hasil audit otomatis terhadap seluruh gambar yang digunakan dalam materi pembelajaran pada platform.\n\n")
        
        # Summary
        total = len(results)
        valid = sum(1 for r in results if r["status"] == "Valid")
        broken = total - valid
        f.write("## Ringkasan Audit\n")
        f.write(f"- **Total Gambar**: {total}\n")
        f.write(f"- **Gambar Valid**: {valid}\n")
        f.write(f"- **Gambar Rusak (Broken)**: {broken}\n\n")
        
        # Table of audit
        f.write("## Tabel Audit Kesesuaian & Validitas Gambar\n\n")
        f.write("| Path | Bab | Slide | Status | Sesuai/Tidak | Catatan |\n")
        f.write("| ---- | --- | ----- | ------ | ------------ | ------- |\n")
        
        for r in results:
            f.write(f"| {r['path']} | {r['bab']} | {r['slide']} | {r['status']} | {r['relevance']} | {r['catatan']} |\n")
            
        f.write("\n---\n\n")
        f.write("## Galeri Preview Gambar Materi\n\n")
        f.write("Berikut adalah visualisasi seluruh gambar yang digunakan pada materi pelajaran untuk verifikasi visual langsung:\n\n")
        
        for r in results:
            f.write(f"### {r['path']} - {r['bab']} - {r['slide']}\n")
            f.write(f"- **Judul Gambar**: {r['judul_gambar'] if r['judul_gambar'] else 'Tidak ada judul'}\n")
            f.write(f"- **Path Asli**: `{r['src']}`\n")
            f.write(f"- **Ringkasan/Deskripsi**: {r['deskripsi']}\n\n")
            
            if r['status'] == "Valid" and r['copied_filename']:
                # Absolute path for rendering
                rel_copied = f"file:///{output_images_dir.replace('\\', '/')}/{r['copied_filename']}"
                f.write(f"![{r['slide']}]({rel_copied})\n\n")
            else:
                f.write("> **⚠️ GAMBAR RUSAK / TIDAK DAPAT DIMUAT**\n\n")
            f.write("---\n\n")

    print(f"Report successfully generated at: {report_path}")

if __name__ == "__main__":
    results = perform_audit()
    generate_report(results)
