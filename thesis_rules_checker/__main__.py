from pprint import pprint
from PyPDF2 import PdfReader

reader = PdfReader("1.PDF")

def visitor_text(text, cm, tm, fontDict, fontSize):
    if text is None or fontDict is None:
        return
    print("Text: "+str(text))
    pprint(cm)
    pprint(tm)
    print("x: {}, y: {}".format(tm[4], tm[5]))
    print("fontDict: "+str(fontDict["/BaseFont"]))
    print("fontSize: "+str(fontSize))
    input()

for page in reader.pages:
    page.extract_text(visitor_text=visitor_text)
