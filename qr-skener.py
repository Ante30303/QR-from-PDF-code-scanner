import glob
import os
import pathlib
from datetime import date

import cv2
import fitz
import numpy as np
from PyPDF2 import PdfMerger
from pyzbar import pyzbar

pdf_input_mapa = glob.glob('input pdf/*.pdf')

for pdf_input in pdf_input_mapa:
    pdf = fitz.open(pdf_input) 
    obrasci = []
    for page in pdf:

        for imag in page.get_images():
            xref = imag[0]
            img_bytes =  pdf.extract_image(xref)["image"]
            # Dekodiramo sliku
            decoded = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), -1)
            barcodes = pyzbar.decode(decoded)

            if len(barcodes) != 0:
                barcode = barcodes[0]
                barcodeData = barcode.data.decode("utf-8")
                barcodeData = barcodeData.replace("\n", "_")

                obrasci.append([page.number, barcodeData])

    for i in range(len(obrasci)):
        from_page = obrasci[i][0]
        try:
            to_page = obrasci[i+1][0] -1
        except IndexError:
            to_page = len(pdf)
        
        doc = fitz.open()
        doc.insert_pdf(pdf, from_page, to_page)
        name_by_id = f"{obrasci[i][1]}"
        today = date.today()
        if os.path.exists(f"{today.year}\\{today.month:02d}\\{today.day:02d}\\{name_by_id}.pdf"):
            path_to_file = f"{today.year}\\{today.month:02d}\\{today.day:02d}\\{name_by_id}"
            os.rename(f"{path_to_file}.pdf", f"{path_to_file}1.pdf")
            doc.save(f"{today.year}\\{today.month:02d}\\{today.day:02d}\\{obrasci[i][1]}2.pdf")
            merger = PdfMerger()
            # Mergamo fajllove sa promjenjenim imenima
            merger.append(f"{path_to_file}1.pdf")
            merger.append(f"{today.year}\\{today.month:02d}\\{today.day:02d}\\{obrasci[i][1]}2.pdf")
            # Stvaramo mergani pdf sa originalnim imenom
            merger.write(f"{path_to_file}.pdf")
            merger.close()

            os.remove(f"{path_to_file}1.pdf")
            os.remove(f"{path_to_file}2.pdf")

        else:
            # We are savig new pdf file in folders: year --> month --> day --> pdf file
            pathlib.Path(f'{os.getcwd()}\\{today.year}\\{today.month:02d}\\{today.day:02d}').mkdir(parents=True, exist_ok=True)
            doc.save(f"{today.year}\\{today.month:02d}\\{today.day:02d}\\{obrasci[i][1]}.pdf")
