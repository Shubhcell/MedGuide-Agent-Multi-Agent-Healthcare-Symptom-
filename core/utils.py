RED_FLAGS = [
    ("chest pain","possible heart attack / immediate ER"),
    ("shortness of breath","respiratory distress / immediate ER"),
    ("severe bleeding","immediate ER"),
    ("loss of consciousness","immediate ER"),
    ("sudden severe headache","possible stroke / immediate ER")
]

def detect_red_flags(parsed: dict):
    found=[]
    txt = parsed.get('raw_text','').lower()
    syms = parsed.get('symptoms',[])
    for term, note in RED_FLAGS:
        if term in txt or term in syms:
            found.append((term,note))
    return found
