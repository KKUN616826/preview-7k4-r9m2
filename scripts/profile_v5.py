"""Mind2Act behavioural profile, v5 letters (MBTI-style letters, meanings defined by this benchmark).

Source: "Mind2Act 模型性格分类 v5（类 MBTI）" handoff, 2026-11-07. Letters only say which of two task
groups a model does relatively better on; they are tendencies, not ability. X = no clear lean
(bootstrap stability below 80%), ? = too little evidence. Nicknames only appear when all four
letters are decided; the family (main type) needs letters 1 and 4.

`avatar(code)` draws a 12 x 12 pixel character whose features follow the letters:
family colour (letters 1 + 4), head width (E wide with ears, I narrow), eyes (S two pixel eyes
for "what", N one visor for "where"), mouth (T flat, F open), headgear (J flat cap, P antenna).
An undecided letter is drawn faint.
"""
from html import escape

AXES = [
    # (key, name, compares, (left letter, left label), (right letter, right label))
    ('energy', 'Energy', 'Act tasks vs. Mind tasks', ('E', 'Act-dominant'), ('I', 'Mind-dominant')),
    ('information', 'Information', 'entity vs. spatial memory', ('S', 'entity memory'), ('N', 'spatial memory')),
    ('decisions', 'Decisions', 'precision vs. reactivity', ('T', 'precision'), ('F', 'reactivity')),
    ('lifestyle', 'Lifestyle', 'plan-driven vs. feedback-driven', ('J', 'feedforward'), ('P', 'feedback')),
]
TRAITS = {
    'E': 'Extravert · Act-dominant', 'I': 'Introvert · Mind-dominant',
    'S': 'Sensing · entity memory', 'N': 'iNtuition · spatial memory',
    'T': 'Thinking · precision', 'F': 'Feeling · reactivity',
    'J': 'Judging · feedforward', 'P': 'Perceiving · feedback',
}
PLAIN = {'E': 'acts', 'I': 'thinks', 'S': 'remembers what', 'N': 'remembers where',
         'T': 'precise', 'F': 'fast', 'J': 'plans ahead', 'P': 'follows feedback'}

FAMILIES = {
    'IJ': ('Feedforward Planner', 'Reasons better than it executes; plans first, then carries the plan out.',
           'Multi-step sequences that need looking ahead', 'Rarely corrects when the outcome drifts from the plan'),
    'IP': ('Feedback Adapter', 'Reasons better than it executes; corrects step by step from what it sees.',
           'Changing scenes that reward correction', 'Long sequences and one-shot precise moves'),
    'EJ': ('Procedural Executor', 'Executes better than it reasons; follows a fixed procedure.',
           'Fixed, repetitive procedures', 'Remembering changing facts or inferring new rules'),
    'EP': ('Servo Responder', 'Executes better than it reasons; steady hands that adjust quickly as the scene changes.',
           'Dynamic interception and feedback-based fine tuning', 'Tasks that need multi-step memory and planning'),
}
NICKNAMES = {
    'ISTJ': 'Bookkeeper', 'ISFJ': 'Dispatcher', 'INTJ': 'Chess Player', 'INFJ': 'Navigator',
    'ISTP': 'Inspector', 'ISFP': 'Scout', 'INTP': 'Surveyor', 'INFP': 'Pathfinder',
    'ESTJ': 'Assembler', 'ESFJ': 'Line Expert', 'ENTJ': 'Engineer', 'ENFJ': 'Conductor',
    'ESTP': 'Fixer', 'ESFP': 'Acrobat', 'ENTP': 'Tuner', 'ENFP': 'Goalkeeper',
}
ORDER = ['IJ', 'IP', 'EJ', 'EP']
# Short pole labels for the card's axis rows.
SHORT = {'E': 'Act', 'I': 'Mind', 'S': 'entity', 'N': 'spatial', 'T': 'precision', 'F': 'reactivity',
         'J': 'plan', 'P': 'feedback'}
PALETTE = {  # deep, face, ink, tint
    'IJ': ('#4f46b0', '#cdc9f6', '#272063', '#ecebfc'),
    'IP': ('#2f7360', '#bfe3d4', '#163b31', '#e4f3ec'),
    'EJ': ('#2f6386', '#c4dcea', '#15344a', '#e5f0f6'),
    'EP': ('#a2451f', '#f4c8b4', '#4f1d0b', '#fae8e0'),
    None: ('#5d6a72', '#d8dee1', '#2b3439', '#eef1f2'),
}


def family(code):
    key = code[0] + code[3]
    return key if key in FAMILIES else None


def nickname(code):
    return NICKNAMES.get(code)


def title(code):
    """Nickname and family when decided, e.g. 'Tuner · Servo Responder'; the family alone otherwise."""
    fam = family(code)
    if fam is None:
        return 'No core type'
    name = FAMILIES[fam][0]
    return f'{NICKNAMES[code]} · {name}' if code in NICKNAMES else name


def traits(code):
    return ' · '.join(TRAITS[ch] for ch in code if ch in TRAITS)


def plain(code):
    return ', '.join(PLAIN[ch] for ch in code if ch in PLAIN)


def avatar(code, cls='m2a-avatar'):
    deep, face, ink, _ = PALETTE[family(code)]
    e, s, t, j = code
    x0, x1 = (1, 10) if e == 'E' else (2, 9)     # E: wide head with ears, I: narrower
    w = x1 - x0 + 1
    px = []  # (x, y, w, h, colour, faint)

    def add(x, y, wd, h, colour, faint=False):
        px.append((x, y, wd, h, colour, faint))

    if j == 'J':
        add(x0, 1, w, 2, deep)                                   # flat cap
    elif j == 'P':
        add(5, 0, 2, 1, face), add(5, 1, 2, 2, deep)             # antenna
    else:
        add(x0, 2, w, 1, deep, True)
    add(x0, 3, w, 7, face)                                       # head, rows 3-9
    if e == 'E':
        add(0, 5, 1, 3, deep), add(11, 5, 1, 3, deep)            # ears out
    elif e != 'I':
        add(1, 5, 1, 3, deep, True), add(10, 5, 1, 3, deep, True)
    if s == 'S':
        add(3, 5, 2, 2, ink), add(7, 5, 2, 2, ink)               # two eyes: what
    elif s == 'N':
        add(3, 5, 6, 2, ink), add(7, 5, 1, 1, face)              # visor: where
    else:
        add(3, 5, 2, 2, ink, True), add(7, 5, 2, 2, ink, True)
    if t == 'T':
        add(4, 8, 4, 1, ink)                                     # flat mouth
    elif t == 'F':
        add(3, 7, 1, 1, ink), add(8, 7, 1, 1, ink), add(4, 8, 4, 1, ink)   # open grin
    else:
        add(5, 8, 2, 1, ink, True)
    add(5, 10, 2, 1, deep)                                       # neck
    add(x0 + 1, 11, w - 2, 1, deep)                              # shoulders
    faint = ' opacity=".35"'
    rects = ''.join(f'<rect x="{x}" y="{y}" width="{wd}" height="{h}" fill="{c}"{faint if f else ""}/>'
                    for x, y, wd, h, c, f in px)
    return (f'<svg class="{escape(cls)}" viewBox="0 0 12 12" shape-rendering="crispEdges" '
            f'aria-hidden="true" focusable="false" data-code="{escape(code)}">{rects}</svg>')
