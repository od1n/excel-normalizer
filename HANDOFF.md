# HANDOFF — Proyectos de portafolio (freelance)

> Respaldo preparado el 9 de noviembre de 2026. Repositorios pequeños y públicos usados como muestra de trabajo en Upwork, Fiverr y Freelancer. Cada uno tiene su `README.md` en inglés.

| Proyecto | Repositorio | Carpeta local | Qué hace |
|---|---|---|---|
| Portafolio JP | https://github.com/od1n/portafolio-jp (privado) | `C:\Proyectos\portafolio-jp` | Página única bilingüe servida con nginx en Docker (EasyPanel), https://portafolio-jp.vinculo.dev. Contacto por formulario (requisito de Upwork). Para actualizar: editar `index.html`, commit, push y botón "Deploy" del servicio en EasyPanel. |
| RAG Document Q&A | https://github.com/od1n/rag-document-qa | `C:\Users\Toor\source\repos\rag-document-qa` (copia idéntica en `D:\Desarrollo\Claude\Projects\rag-document-qa`) | Preguntas sobre PDF con citas: ChromaDB + embeddings de OpenAI o locales, interfaz Streamlit. `streamlit run app.py`. |
| Invoice Extractor | https://github.com/od1n/invoice-extractor-demo | `D:\Desarrollo\Claude\Projects\invoice-extractor-demo` | FastAPI + Claude Vision: facturas en imagen → datos validados → Excel/CSV. |
| PDF Text Extractor | https://github.com/od1n/pdf-text-extractor | `C:\Users\Toor\Documents\pdf-text-extractor` | PDF a texto con dos motores (pdftotext y pdfplumber), informe de verificación y OCR con Tesseract. |
| Excel Normalizer | https://github.com/od1n/excel-normalizer | `C:\Users\Toor\Documents\excel-normalizer` | Normaliza libros de Excel (z-score o min-max) con informe antes/después. |
| n8n Workflows | https://github.com/od1n/n8n-workflows | `D:\Desarrollo\Claude\Projects\n8n-workflows` (copia idéntica en `C:\Users\Toor\Downloads\n8n-workflows`) | Exportación sin credenciales de los flujos de producción: buscador de ofertas de trabajo y evaluador de mensajes de la bandeja. |

Ejecución típica de los de Python:

```powershell
Set-Location 'C:\Users\Toor\source\repos\rag-document-qa'
python -m pip install -r 'C:\Users\Toor\source\repos\rag-document-qa\requirements.txt'
```

Claves: cada uno trae `.env.example`; las claves reales nunca se suben.

Nota: hay dos copias de `rag-document-qa` y de `n8n-workflows`; ambas apuntan al mismo GitHub y están al día. Conviene borrar una para no confundirse.
