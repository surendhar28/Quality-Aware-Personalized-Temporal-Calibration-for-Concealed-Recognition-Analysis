import os
import json
import pymupdf  # fitz
import openpyxl

def extract_pdf_info(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += f"--- Page {page_num + 1} ---\n"
        text += page.get_text() + "\n"
    return text

def inspect_excel_fast(excel_path):
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    sheet_info = {}
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i > 15:
                break
            rows.append(row)
        
        headers = [str(c) if c is not None else f"col_{j}" for j, c in enumerate(rows[0])] if len(rows) > 0 else []
        sample_rows = []
        for r in rows[1:6]:
            sample_rows.append({headers[j]: (str(v) if v is not None else None) for j, v in enumerate(r) if j < len(headers)})
            
        sheet_info[sheet_name] = {
            "columns_count": len(headers),
            "columns": headers,
            "sample_rows": sample_rows
        }
    wb.close()
    return sheet_info

def main():
    processed_dir = r"E:\karthianna\data\processed"
    pdf_path = os.path.join(processed_dir, "Eye Tracking Dataset Structure.pdf")
    rec1_path = os.path.join(processed_dir, "CIT Recording1.xlsx")
    
    report = {}
    
    if os.path.exists(pdf_path):
        report["pdf_structure_text"] = extract_pdf_info(pdf_path)
    else:
        report["pdf_structure_text"] = "PDF not found"
        
    if os.path.exists(rec1_path):
        report["excel_info"] = inspect_excel_fast(rec1_path)
        
    txt_out = r"E:\karthianna\data\audit_zenodo_summary.txt"
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write("=== ZENODO PDF STRUCTURE ===\n")
        f.write(report.get("pdf_structure_text", ""))
        f.write("\n\n=== EXCEL STRUCTURE (CIT Recording1.xlsx) ===\n")
        excel_info = report.get("excel_info", {})
        for sheet, sdata in excel_info.items():
            f.write(f"\nSheet: {sheet}\n")
            f.write(f"Columns count: {sdata['columns_count']}\n")
            f.write("Columns:\n")
            for c in sdata["columns"]:
                f.write(f"  - {c}\n")
            f.write("\nSample Rows:\n")
            for idx, r in enumerate(sdata.get("sample_rows", [])):
                f.write(f"  Row {idx+1}:\n")
                for k, v in list(r.items())[:15]:
                    f.write(f"    {k}: {v}\n")
                    
    print(f"Audit completed successfully! Saved to {txt_out}")

if __name__ == "__main__":
    main()
