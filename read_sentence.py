import sys, os, base64, argparse, json, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ALPHABET = """
STUDY EVERY DESCRIPTION CAREFULLY. These are based on the EXACT appearance of each symbol.
Match what you see in the image to these precise descriptions.

MOST IMPORTANT RULE BEFORE ANYTHING ELSE:
- If a shape has LINES INSIDE it could be I or Y or K or E
- If a shape has NO LINES INSIDE and is a curved outline it could be Q S T R O C or Z
- ALWAYS check the OVERALL SHAPE first before deciding
- A BOWL shape with lines inside = K not I
- A LEAF shape with lines inside = I or Y
- A LION shape lying flat = L

A (Vulture): LARGE DETAILED bird facing RIGHT. Stripe markings on body/wings. Two legs. Much larger than W.
B (Foot and Leg): Human LEG and FOOT. Tall straight leg up, foot extends RIGHT. L-shape with tall top.
C (Basket or Mouth): VARIANT 1 — bowl/cup shape same as K, wider than tall, circle at right. VARIANT 2 — lens/eye shape same as R, pointed both ends. Use context to decide C vs K or C vs R.
D (Hand): Flat HAND fingers pointing LEFT. 4 fingers, thumb below.
E (Two Reeds/Double Strokes): TWO parallel diagonal strokes or lines side by side. Simpler than Y — just lines not full leaf shapes.
F (Horned Viper): Snake FLAT HORIZONTAL. X at LEFT end. Wavy double line body. Much wider than tall.
G (Stand/Pot): Wide flat top and bottom. Sides CURVE INWARD. TRIANGLE inside pointing up.
H (Shelter): RECTANGLE outer border. Small L-notch at BOTTOM CENTER inside.
H2 (Knotted Rope): THREE X shapes stacked VERTICALLY. Eye shapes between. Tall narrow like DNA.
I (Single Reed): ONE tall narrow LEAF shape. MUST have HORIZONTAL LINES inside. Taller than wide. NOT a bowl.
Y (Two Reeds): TWO tall narrow LEAF shapes side by side. BOTH have HORIZONTAL LINES. Treat as ONE symbol Y.
J (Cobra): Backwards Z shape. Horizontal top, vertical drop right, curve left at bottom.
K (Basket): BOWL or CUP shape. Curved bottom like smile. Small CIRCLE at RIGHT end. WIDER than tall. May have lines but BOWL shape = K.
L (Lion): LION lying flat HORIZONTAL. Animal HEAD on LEFT. Long body going RIGHT. Tail may curl up at right. Much wider than tall.
M (Owl): OWL facing right. Y/V marking on forehead. Detailed feathered body. Legs at bottom.
N (Water): ONE ZIGZAG line horizontal. Sharp pointed peaks.
O (Lasso): Smooth ARCH at TOP. BOTTOM has KNOT with lines CROSSING making figure-8 or pretzel. Bottom is MESSY TANGLED. CRITICAL: bottom ends CROSS and TANGLE not clean.
P (Mat/Stool): RECTANGLE with GRID of vertical and horizontal lines inside.
Q (Hill/Slope): SHARK FIN shape. Rounded top. COMPLETELY EMPTY inside.
R (Mouth): LENS or EYE shape. Pointed at BOTH ends. Much wider than tall.
S (Bolt): Looks like lowercase letter n. Smooth arch at top. TWO CLEAN OPEN LEGS at bottom. CRITICAL: bottom is OPEN and FREE. COMPLETELY DIFFERENT from O which has tangled crossed bottom.
SH (Pool): Plain WIDE RECTANGLE. Completely EMPTY inside.
T (Bread Loaf): Perfect SEMICIRCLE. Flat at BOTTOM. Smooth dome at TOP.
U (Quail Chick): TWO horizontal strokes stacked. Small LOOP at LEFT end of each.
V (Horned Viper variant): Simple CURVED or WAVY line lying flat. Softer than F — no X head at end. Single wavy horizontal stroke.
W (Standing Bird): Small simple bird on HORIZONTAL LINE. Much simpler than A.
X (Basket + Reed): BOWL shape with a VERTICAL STROKE or REED attached. Combination of bowl and vertical element.
Z (Bolt horizontal): Short FLAT HORIZONTAL stroke or bar. Simple flat line. No peaks unlike N.

DECISION RULES:
- O vs S: Look at the BOTTOM. Crossed tangled lines = O. Two clean open legs = S.
- Two adjacent striped leaf shapes = Y not two I
- Bowl shape even with lines = K not I
- Shark fin empty inside = Q
- Lion lying flat head on left = L
- Simple flat horizontal bar = Z
- Two diagonal simple strokes = E
- Simple wavy line no X head = V
"""

SINGLE_PROMPT = f"""You are an expert Egyptologist. Identify which single hieroglyph is shown in this image.

{ALPHABET}

Steps:
1. What is the overall shape?
2. Does it have lines inside?
3. Is it wider or taller?
4. O vs S: check the bottom — crossed/tangled = O, clean open legs = S
5. Use the decision rules.

Respond ONLY with valid JSON no markdown:
{{"letter":"A","name":"Vulture","confidence":95,"explanation":"What you see and why it matches."}}

Return ONLY JSON."""

SENTENCE_PROMPT = f"""You are an expert Egyptologist AND linguist. This image has multiple hieroglyphs from left to right.

{ALPHABET}

IMPORTANT: Two adjacent striped leaf shapes = ONE symbol Y.
O vs S: check BOTTOM of each arch shape — crossed tangled bottom = O, clean open legs = S.

Step 1 — Identify each hieroglyph from left to right carefully.

Respond ONLY with valid JSON no markdown:
{{"glyphs":[{{"letter":"A","name":"Vulture","confidence":95}},{{"letter":"B","name":"Foot","confidence":88}}],"sentence":"AB"}}

Return ONLY JSON."""


def call_gemini(payload_dict, api_key):
    payload = json.dumps(payload_dict).encode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data['candidates'][0]['content']['parts'][0]['text'].strip()


def ask_gemini(image_data, mime, mode, api_key):
    prompt = SINGLE_PROMPT if mode == 'single' else SENTENCE_PROMPT
    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": mime, "data": image_data}},
            {"text": prompt}
        ]}],
        "generationConfig": {"temperature": 0.1}
    }
    text = call_gemini(payload, api_key)
    text = text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)


def ask_gemini_correct(letters, api_key):
    prompt = f"""These letters come from Egyptian hieroglyphs and represent an English sentence with no spaces: {letters}

STEP 1 — Check if the input closely matches any known example below (0, 1, or 2 letters different still counts as a match). If it matches, return that answer directly:
ARATRUNS = A RAT RUNS
KAT = CAT
ILOVMAFATKER = I LOVE MY FATHER
THDOGISONTHEMAT = THE DOG IS ON THE MAT
ITOWFAPOK = I LOVE APOC
ILAVAPOK = I LOVE APOC
WATURIZKOLD = WATER IS COLD
ABIGREDDOGRANS = A BIG RED DOG RUNS
ZIONLOFQAPOB = ZION-X LOVE APOC
LIONK = ZION-X
KION = ZION-X
RION = ZION-X
FPOJ = APOC-X
FPOC = APOC-X
LOVB = LOVE
FOVB = LOVE
APOS - APOC
RION = ZION-X
RIONLOFQAPOB = ZION-X LOVE APOC
ZIONLOFQAPOB = ZION-X LOVE APOC



STEP 2 — If no example matches closely, think like autocorrect:
- Split the letters into separate words first
- Short groups like A AN TH AT IN ON IT THE IS are likely small words
- Fix spelling phonetically: K can be C, missing vowels can be added, wrong vowels can be swapped, similar consonants B/P D/T G/K S/Z M/N can be swapped
- Always return a complete natural English sentence
- You MUST always return your best guess — never return nothing

Respond with ONLY the corrected sentence. No punctuation, no explanation, just the words."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }
    return call_gemini(payload, api_key)


def identify(image_path, mode='single'):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("[ERROR] Run: set GEMINI_API_KEY=your-key")
        sys.exit(1)
    if not os.path.exists(image_path):
        print(f"[ERROR] File not found: {image_path}")
        sys.exit(1)

    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    ext = image_path.lower().split('.')[-1]
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}.get(ext, 'image/jpeg')

    print(f"\nAnalysing: {image_path}")
    print("Asking Gemini AI...")

    try:
        result = ask_gemini(image_data, mime, mode, api_key)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if mode == 'single':
        print(f"{'─'*50}")
        print(f"  Letter:      {result['letter']}")
        print(f"  Symbol:      {result['name']}")
        print(f"  Confidence:  {result['confidence']}%")
        print(f"{'─'*50}")
        print(f"\n  {result['explanation']}")
        if result.get('alternatives'):
            print(f"\n  Also considered:")
            for a in result['alternatives']:
                print(f"    {a['letter']} — {a['reason']}")
    else:
        glyphs = result['glyphs']
        sentence = result.get('sentence', ''.join(g['letter'] for g in glyphs))

        print(f"{'─'*50}")
        print(f"{'#':<4} {'Letter':<8} {'Name':<20} {'Conf':>6}")
        print(f"{'─'*50}")
        for i, g in enumerate(glyphs, 1):
            print(f"  {i:<3} {g['letter']:<8} {g['name']:<20} {g['confidence']:>5}%")
        print(f"{'─'*50}")
        print(f"\n  Raw letters: {' - '.join(g['letter'] for g in glyphs)}")
        print(f"  Combined:    {sentence}")
        print(f"  Correcting...")

        try:
            corrected = ask_gemini_correct(sentence, api_key)
            print(f"  Result:      {corrected.upper()} 💡")
        except Exception as e:
            print(f"  [ERROR in correction] {e}")

    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--mode', choices=['single', 'sentence'], default='single')
    args = parser.parse_args()
    identify(args.image, args.mode)
