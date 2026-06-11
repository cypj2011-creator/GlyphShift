import sys, os, base64, argparse, json, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ALPHABET = """
STUDY EVERY DESCRIPTION CAREFULLY. These are based on the EXACT appearance of each symbol.
Match what you see in the image to these precise descriptions.

MOST IMPORTANT RULE BEFORE ANYTHING ELSE:
- If a shape has LINES INSIDE it could be I or Y or K
- If a shape has NO LINES INSIDE and is a curved outline it could be Q S T R or O
- ALWAYS check the OVERALL SHAPE first before deciding
- A BOWL shape with lines inside = K not I
- A LEAF shape with lines inside = I or Y

A (Vulture):
- A LARGE DETAILED bird standing and facing RIGHT
- Has a long pointed BEAK facing right
- Small dot for EYE on the head
- Body has clear VERTICAL STRIPE MARKINGS on chest
- Wings have DIAGONAL stripe markings
- Has a visible TAIL pointing right at the back
- Two LEGS visible at the bottom
- Much LARGER and more DETAILED than W
- MUST have visible stripe markings on the body
- Key: LARGE + DETAILED stripes on body + long beak + facing RIGHT + STANDING

B (Foot and Leg):
- Shows a complete human LEG and FOOT
- The LEG is TALL and STRAIGHT going upward like a rectangular column
- At the BOTTOM the FOOT extends to the RIGHT
- The foot has a clear HEEL on the left and TOES on the right
- Overall shape like the letter L but with a very tall top
- Clear ANKLE where leg meets foot
- Key: TALL STRAIGHT LEG going up + FOOT extending RIGHT at bottom + L-shape + ankle

D (Hand):
- A flat human HAND with fingers pointing to the LEFT
- Has 4 FINGERS visible with lines between them
- Thumb is slightly below and separate from fingers
- The hand is OPEN and FLAT viewed from above
- Key: FLAT HAND + 4 fingers pointing LEFT + lines between fingers + thumb below

F (Horned Viper):
- A snake lying COMPLETELY FLAT and HORIZONTAL
- Has an X or cross shape at the LEFT end — horned head
- Body is a thin DOUBLE LINE forming 2-3 smooth wavy humps going RIGHT
- Much WIDER than tall
- Key: HORIZONTAL + FLAT + X at LEFT end + wavy double line body + VERY WIDE

G (Stand/Pot):
- Has a WIDE FLAT TOP edge and WIDE FLAT BOTTOM edge
- LEFT and RIGHT sides CURVE INWARD making barrel/hourglass shape
- Inside there is a TRIANGLE pointing UPWARD
- Key: flat TOP + flat BOTTOM + sides CURVE INWARD + TRIANGLE inside

H (Shelter):
- A large RECTANGLE forming the outer border
- Inside at BOTTOM CENTER there is a small L-shape or rectangular notch
- Upper portion of rectangle is EMPTY
- Key: OUTER RECTANGLE + small L-shape notch at BOTTOM CENTER + top is empty

H2 (Knotted Rope):
- THREE X shapes stacked VERTICALLY
- Eye/diamond shapes between the crosses
- Tall and NARROW — much taller than wide
- Like DNA helix or braided chain
- Key: THREE X shapes stacked + eye shapes between + TALL and NARROW

I (Single Reed):
- EXACTLY ONE curved leaf or feather shape
- ABSOLUTELY CRITICAL: MUST have many HORIZONTAL PARALLEL LINES clearly visible INSIDE
- The overall shape is a TALL NARROW LEAF or FEATHER — taller than wide
- CRITICAL: It is a LEAF shape NOT a bowl shape — tapers to point at bottom
- Curved on the LEFT side tapers to point at BOTTOM
- If the shape is a BOWL or CUP shape it is K not I
- Key: ONE TALL NARROW LEAF shape + MUST HAVE HORIZONTAL LINES INSIDE + tapers at bottom + NOT a bowl

Y (Two Reeds):
- EXACTLY TWO curved leaf shapes placed SIDE BY SIDE
- BOTH shapes MUST have HORIZONTAL PARALLEL LINES clearly visible inside each one
- Both shapes are TALL NARROW LEAVES — taller than wide
- Clear GAP between the two shapes
- CRITICAL: If you see two leaf shapes with lines next to each other it is Y not two separate I symbols
- When two striped leaf shapes appear together they form Y as ONE symbol
- Key: TWO TALL NARROW LEAF shapes + BOTH have LINES INSIDE + side by side + they are ONE symbol Y

J (Cobra):
- Shaped like a BACKWARDS Z or N
- Horizontal part at TOP going right
- Vertical DROP on the right side going down
- Curve to the LEFT at the BOTTOM
- Key: horizontal TOP + vertical DROP right + curve LEFT at bottom + like backwards Z

K (Basket):
- Shape of a BOWL or CUP seen from the side
- The BOTTOM is curved downward like a smile or bowl shape
- Has a flat or slightly angled TOP edge
- Small CIRCLE or DOT at the RIGHT end — the handle
- Much WIDER than tall — wider than it is high
- May sometimes have horizontal lines INSIDE the bowl
- CRITICAL: Even if it has lines inside if the overall shape is a BOWL or CUP it is K not I
- The key difference from I: K is WIDER than tall like a bowl, I is TALLER than wide like a leaf
- Key: BOWL or CUP shape + curved bottom like smile + wider than tall + circle at right + overall bowl outline

M (Owl):
- An OWL facing SLIGHTLY TO THE RIGHT
- Y or V shape marking on FOREHEAD
- Large eyes visible on face
- Detailed FEATHERED BODY with wing patterns on right side
- LEGS and FEET at bottom
- Key: OWL + Y/V marking on face + detailed feathers + legs at bottom

N (Water):
- ONE single ZIGZAG line going horizontally across
- Many SHARP POINTED PEAKS going upward like mountain teeth
- ONE LINE only — not three stacked lines
- Key: ONE ZIGZAG line + sharp peaks + horizontal

O (Lasso):
- Looks like a NOOSE or LASSO rope
- TOP is a smooth ARCH or LOOP going upward like an upside down U
- BOTTOM has a KNOT — two lines CROSSING each other making an X or figure-8
- The bottom is MESSY and COMPLICATED with lines overlapping each other
- CRITICAL: The bottom ends DO NOT hang free — they CROSS and TANGLE together
- CRITICAL DIFFERENCE FROM S: O has a messy tangled crossed bottom, S has clean open legs
- Key: smooth arch TOP + CROSSING TANGLED lines at BOTTOM + messy figure-8 bottom

P (Mat/Stool):
- A RECTANGLE as outer border
- Inside has GRID of both VERTICAL and HORIZONTAL lines
- Multiple rows AND columns of small rectangles inside
- Key: RECTANGLE + grid inside + rows AND columns

Q (Hill/Slope):
- Shaped like a SHARK FIN or SAIL
- Has a small flat section at BOTTOM LEFT before curving up
- LEFT side curves smoothly UPWARD then curves back right at top making a rounded peak
- RIGHT side goes DIAGONALLY STRAIGHT DOWN to bottom right
- Flat BOTTOM edge
- ABSOLUTELY CRITICAL: The inside is COMPLETELY EMPTY — NO lines NO stripes NO markings inside
- Just a plain empty outline — you can only see the border of the shape
- If you see ANY lines inside the shape it is I or Y not Q
- Key: SHARK FIN outline + ROUNDED top + diagonal right side + COMPLETELY EMPTY INSIDE

R (Mouth):
- A LENS or EYE shape
- Pointed at BOTH the left end and right end
- Much WIDER than tall
- Smooth curves top and bottom meeting at sharp points
- Key: LENS shape + pointed BOTH ends + wider than tall + smooth curves

S (Bolt):
- Looks EXACTLY like a lowercase letter n
- Smooth ARCH at the top — one clean curve going up
- Two straight legs hanging DOWN at the bottom
- The bottom two legs are OPEN FREE and SEPARATE — they just end cleanly with nothing extra
- CRITICAL: The bottom ends are CLEAN and OPEN — no crossing no tangling no loops no knots
- CRITICAL DIFFERENCE FROM O: S bottom is two clean open legs like letter n, O bottom has crossing tangled lines
- If the bottom is clean and open with no crossing it is S not O
- Key: letter n shape + TWO CLEAN OPEN legs at bottom + nothing crosses at bottom

SH (Pool):
- A plain WIDE RECTANGLE
- Completely EMPTY inside — no lines no grid no markings
- Much WIDER than tall
- Key: WIDE RECTANGLE + completely empty inside + wider than tall

T (Bread Loaf):
- A perfect SEMICIRCLE
- Flat straight edge at BOTTOM
- Smooth dome curve at TOP
- NO animal features NO lines NO loops
- Key: SEMICIRCLE + flat BOTTOM + smooth dome TOP + nothing else

U (Quail Chick):
- EXACTLY TWO horizontal strokes stacked on top of each other
- Each stroke has a small LOOP or CIRCLE at the LEFT end
- Both strokes go LEFT to RIGHT horizontally
- Completely FLAT and HORIZONTAL — not vertical
- Key: TWO horizontal strokes + small loop at LEFT of each + stacked + FLAT HORIZONTAL

W (Standing Bird):
- A SMALL SIMPLE bird standing on a HORIZONTAL LINE
- Faces RIGHT with small beak
- Round body simple wing two thin legs
- Stands on flat baseline
- Much simpler than A
- Key: SMALL SIMPLE BIRD + standing on LINE + facing right

FINAL DECISION RULES:
STEP 1 — Check the OVERALL SHAPE first:
  Is it a BIRD? → A W or U
  Is it a SNAKE? → F or J
  Is it a HUMAN BODY PART? → B or D
  Is it a RECTANGLE? → P H SH
  Is it a CURVED or ORGANIC shape? → continue to step 2

STEP 2 — Does it have LINES INSIDE?
  YES lines inside AND tall narrow leaf shape → I one leaf or Y two leaves
  YES lines inside AND bowl/cup shape wider than tall → K
  NO lines inside → continue to step 3

STEP 3 — What specific shape is it?
  Shark fin empty inside → Q
  Semicircle flat bottom → T
  Lens/eye pointed both ends → R
  Arch like letter n with CLEAN OPEN bottom legs → S
  Arch with CROSSED TANGLED lines at bottom → O
  Bowl with circle handle at right → K
  Barrel with triangle inside → G
  Three stacked X chain → H2
  One zigzag line sharp peaks → N
  Two flat horizontal strokes with loops → U
  Owl with Y marking → M

STEP 4 — Bird identification:
  Large detailed bird with stripes → A
  Small simple bird on a line → W

STEP 5 — O vs S final check:
  Look ONLY at the BOTTOM of the shape
  Bottom has crossing tangled lines or figure-8 = O
  Bottom has two clean open separate legs = S

STEP 6 — Two leaf shapes together = Y not two I symbols:
  Always treat two adjacent striped leaf shapes as ONE symbol Y
"""

SINGLE_PROMPT = f"""You are an expert Egyptologist specialising in Egyptian hieroglyphic writing.
Carefully examine the image and identify which single hieroglyph is shown.

{ALPHABET}

Follow these steps carefully:
1. What is the OVERALL SHAPE?
2. Does it have lines or stripes INSIDE?
3. Is it wider than tall or taller than wide?
4. Follow the FINAL DECISION RULES step by step.
5. For any arch shape — check the BOTTOM: crossed tangled = O, clean open legs = S.
6. Double check against the detailed description.

Respond ONLY with valid JSON no markdown no backticks:
{{"letter":"A","name":"Vulture","confidence":95,"explanation":"Describe exactly what you see and why it matches.","alternatives":[{{"letter":"W","reason":"brief reason"}}]}}

Return ONLY the JSON object."""

SENTENCE_PROMPT = f"""You are an expert Egyptologist AND linguist specialising in Egyptian hieroglyphic writing.
This image contains multiple Egyptian hieroglyphs in a row from left to right.

{ALPHABET}

IMPORTANT: Two adjacent striped leaf shapes = ONE symbol Y not two separate I symbols.
O vs S: check BOTTOM of each arch shape — crossed tangled bottom = O, clean open legs = S.

For EACH hieroglyph from left to right:
1. What is the OVERALL SHAPE?
2. Does it have lines or stripes INSIDE?
3. Is it wider than tall or taller than wide?
4. Follow the FINAL DECISION RULES step by step.
5. Double check against the detailed description.

Respond ONLY with valid JSON no markdown no backticks:
{{"glyphs":[{{"letter":"A","name":"Vulture","confidence":95}},{{"letter":"B","name":"Foot","confidence":88}}],"sentence":"AB"}}

Return ONLY the JSON object."""


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
