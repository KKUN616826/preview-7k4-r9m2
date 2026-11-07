"""Mind2Act behavioural profile, v5 letters (MBTI-style letters, meanings defined by this benchmark).

Source: "Mind2Act 模型性格分类 v5（类 MBTI）" handoff, 2026-11-07. Letters only say which of two task
groups a model does relatively better on; they are tendencies, not ability. On the site every axis
shows one of its two letters, the side the model leans to; a lean whose bootstrap stability is
below 80% is marked as weak with its stability, instead of the harness's X.

Each of the sixteen codes has its own pixel character (`avatar`): a 16 x 16 sprite with the prop
or headgear of its nickname, in a shade of its family colour (letters 1 + 4).
"""
from html import escape

AXES = [
    # (key, name, compares, (left letter, left label), (right letter, right label))
    ('energy', 'Energy', 'Act tasks vs. Mind tasks', ('E', 'Act-dominant'), ('I', 'Mind-dominant')),
    ('information', 'Information', 'entity vs. spatial memory', ('S', 'entity memory'), ('N', 'spatial memory')),
    ('decisions', 'Decisions', 'precision vs. reactivity', ('T', 'precision'), ('F', 'reactivity')),
    ('lifestyle', 'Lifestyle', 'plan-driven vs. feedback-driven', ('J', 'feedforward'), ('P', 'feedback')),
]
STABLE = 80   # bootstrap stability (%) at or above which a lean counts as clear
TRAITS = {
    'E': 'Extravert · Act-dominant', 'I': 'Introvert · Mind-dominant',
    'S': 'Sensing · entity memory', 'N': 'iNtuition · spatial memory',
    'T': 'Thinking · precision', 'F': 'Feeling · reactivity',
    'J': 'Judging · feedforward', 'P': 'Perceiving · feedback',
}
SHORT = {'E': 'Act', 'I': 'Mind', 'S': 'entity', 'N': 'spatial', 'T': 'precision', 'F': 'reactivity',
         'J': 'plan', 'P': 'feedback'}

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
ORDER = ['IJ', 'IP', 'EJ', 'EP']
FAMILY_COLOUR = {'IJ': '#4f46b0', 'IP': '#2f7360', 'EJ': '#2f6386', 'EP': '#a2451f'}

# code: (nickname, own colour: a shade of the family colour)
TYPES = {
    'ISTJ': ('Bookkeeper', '#4f46b0'), 'ISFJ': ('Dispatcher', '#6a46b8'),
    'INTJ': ('Chess Player', '#3a3f8c'), 'INFJ': ('Navigator', '#9b3f8f'),
    'ISTP': ('Inspector', '#2f7360'), 'ISFP': ('Scout', '#4a8a36'),
    'INTP': ('Surveyor', '#22706f'), 'INFP': ('Pathfinder', '#667f24'),
    'ESTJ': ('Assembler', '#2f6386'), 'ESFJ': ('Line Expert', '#2479a8'),
    'ENTJ': ('Engineer', '#3c5370'), 'ENFJ': ('Conductor', '#1f7f8f'),
    'ESTP': ('Fixer', '#a2451f'), 'ESFP': ('Acrobat', '#c4621a'),
    'ENTP': ('Tuner', '#9a3434'), 'ENFP': ('Goalkeeper', '#a87414'),
}
NICKNAMES = {code: nick for code, (nick, _) in TYPES.items()}

# 16 x 16 sprites. f face, d clothes (both from the type colour), k ink, w white, a gold, g steel,
# b brown, l glass blue. Props: ledger, headset, chess pawn, captain's cap, magnifier, ranger hat and
# binoculars, survey tripod, hood and lantern, hard hat and gear, paper cap and parcel, goggles and
# blueprint, baton and bow tie, cap and hammer, raised arms and stripes, headphones and tuning fork,
# keeper gloves and number one.
SPRITES = {
    'ISTJ': ["................", "................", "................", "....aaaaaaaa....",
             ".....ffffff.....", ".....ffffff.....", ".....kwkkwk.....", ".....ffffff.....",
             ".....ffkkff.....", ".....ffffff.....", "....dddddddd....", "...fddddddddbbb.",
             "...fddddddddbwb.", "....ddddddddbbb.", ".....dd..dd.....", ".....kk..kk....."],
    'ISFJ': ["................", "................", "................", ".....kkkkkk.....",
             "....kffffffk....", "....kffffffk....", "...kkfkffkfkk...", "...kkffffffkk...",
             ".....fkffkfk....", ".....ffkkfa.....", "....dddddddd....", "...fddddddddf...",
             "...fdddadddddf..", "....dddddddd....", ".....dd..dd.....", ".....kk..kk....."],
    'INTJ': ["................", "................", ".............kk.", ".....kkkkkk..kk.",
             ".....kffffk.kkkk", ".....ffffff..kk.", ".....fkkkkf..kk.", ".....ffffff.kkkk",
             ".....ffkkff.kkkk", ".....ffffff.....", "....dwdwdwdw....", "...fwdwdwdwdf...",
             "...fdwdwdwdwf...", "....wdwdwdwd....", ".....dd..dd.....", ".....kk..kk....."],
    'INFJ': ["................", "......wwww......", ".....wwaaww.....", "....kkkkkkkk....",
             ".....ffffff.....", ".....ffffff.....", ".....fkkkkf.....", ".....ffffff.....",
             ".....kffffk.....", ".....fkkkkf.....", "....dddddddd....", "...fddaddaddf...",
             "...fddddddddf...", "....dddddddd....", ".....dd..dd.....", ".....kk..kk....."],
    'ISTP': ["................", "................", "......bbbb......", ".....bbbbbbb....",
             ".....ffffff..kk.", ".....ffffff.kllk", ".....fkffkf.kllk", ".....ffffff..kk.",
             ".....ffkkff.b...", ".....ffffff.b...", "....ddddddddb...", "...fddddddddf...",
             "...fkkkkkkkk....", "....dddddddd....", ".....dd..dd.....", ".....kk..kk....."],
    'ISFP': ["................", "......bbbb......", "......bbbb......", "...bbbbbbbbbb...",
             ".....ffffff.....", ".....ffffff.....", ".....fkffkf.....", ".....ffffff.....",
             ".....kffffk.....", ".....fkkkkf.....", "....dddddddd....", "...fdkkddkkdf...",
             "...fdkkddkkdf...", "....dddddddd....", ".....dd..dd.....", ".....kk..kk....."],
    'INTP': ["................", ".......aa.......", "......dddd......", ".....dddddd.....",
             ".....ffffff.....", ".....ffffff.....", ".....fkkkkf.ggg.", ".....ffffff.gkg.",
             ".....ffkkff.ggg.", ".....ffffff..k..", "....dddddddd.k..", "...fddddddddfk..",
             "...fddddddddk.k.", "....ddddddddk.k.", ".....dd..ddk...k", ".....kk..kkk...k"],
    'INFP': ["................", "................", "......dddd......", ".....dddddd.....",
             "....dffffffd....", "....dffffffd....", "....dfkkkkfd....", "....dffffffd....",
             "....dkffffkd....", "....dfkkkkfd....", "....dddddddd....", "...fddddddddf...",
             "...fddddddddkk..", "....ddddddddaa..", ".....dd..dd.aa..", ".....kk..kk....."],
    'ESTJ': ["................", "................", "......aaaa......", "....aaaaaaaa....",
             "...aaaaaaaaaa...", "....ffffffff....", "....ffkffkff....", "....ffffffff....",
             "....fffkkfff..g.", "....ffffffff.ggg", "...dddddddddd.g.", "..fddddddddddf..",
             "...dddddddddd...", "...dddddddddd...", ".....dd..dd.....", ".....kk..kk....."],
    'ESFJ': ["................", "................", "................", ".....wwwwww.....",
             "....wwwwwwww....", "....ffffffff....", "....ffkffkff....", "....ffffffff....",
             "....fkffffkf....", "....ffkkkkff....", "...dddddddddd...", "...dbbbaabbbd...",
             "..fdbbbaabbbdf..", "...dbbbbbbbbd...", ".....dd..dd.....", ".....kk..kk....."],
    'ENTJ': ["................", "................", "................", "....kkkkkkkk....",
             "....gllggllg....", "....ffffffff....", "....ffkkkkff....", "....ffffffff....",
             "....fffkkfff....", "....ffffffff....", "...dddddddddd.ll", "..fdddddddddlll.",
             "..fddddddddll...", "...dddddddddd...", ".....dd..dd.....", ".....kk..kk....."],
    'ENFJ': ["................", "................", "...............k", "....kkkkkkk...k.",
             "....kkkfffff.k..", "....ffffffff.f..", "....ffkkkkff.d..", "....ffffffff.d..",
             "....fkffffkf.d..", "....ffkkkkff.d..", "...ddddkkddddd..", "..fdddwwwwdddd..",
             "...dddwwwwddd...", "...dddddddddd...", ".....dd..dd.....", ".....kk..kk....."],
    'ESTP': ["................", "................", "................", "....kkkkkkkk....",
             "..kkkkkkkkkk....", "....ffffffff....", "....ffkffkffgggg", "....ffffffffgggg",
             "....fffkkfff.b..", "....ffffffff.b..", "...dddddddddfb..", "..fdddddddddd...",
             "...kkkkaakkkk...", "...dddddddddd...", ".....dd..dd.....", ".....kk..kk....."],
    'ESFP': ["................", ".a............a.", "..f....kk....f..", "..d.kkkkkkkk.d..",
             "..d.ffffffff.d..", "..d.ffffffff.d..", "..d.ffkffkff.d..", "..d.ffffffff.d..",
             "..d.fkffffkf.d..", "..ddffkkkkffdd..", "...wdwdwdwdwd...", "...dwdwdwdwdw...",
             "...wdwdwdwdwd...", "...dwdwdwdwdw...", ".....dd..dd.....", ".....kk..kk....."],
    'ENTP': ["................", "................", ".....kkkkkk.....", "....k......k....",
             "....ffffffff....", "...kffffffffk...", "...kffkkkkffkg.g", "...kffffffffkg.g",
             "....fffkkfff.ggg", "....ffffffff..g.", "...dddddddddd.g.", "..fddddddddddf..",
             "...dddddddddd...", "...dddddddddd...", ".....dd..dd.....", ".....kk..kk....."],
    'ENFP': ["................", "................", "................", "....dddddddd....",
             "....dddddddddd..", "....ffffffff....", "....ffkkkkff....", "....ffffffff....",
             "....fkffffkf....", "aaa.ffkkkkff.aaa", "aaaddddddddddaaa", "...dddddwdddd...",
             "...dddddwdddd...", "...ddddwwwddd...", ".....dd..dd.....", ".....kk..kk....."],
}
for _code, _rows in SPRITES.items():
    assert len(_rows) == 16 and all(len(r) == 16 for r in _rows), _code


def _mix(hex_colour, other, share):
    a = [int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * share):02x}' for x, y in zip(a, b))


def colours(code):
    """deep, face, ink, tint for a code, from its own shade."""
    deep = TYPES[code][1]
    return deep, _mix(deep, '#ffffff', .7), _mix(deep, '#000000', .5), _mix(deep, '#ffffff', .9)


def family(code):
    return code[0] + code[3]


def nickname(code):
    return NICKNAMES[code]


def title(code):
    return f'{NICKNAMES[code]} · {FAMILIES[family(code)][0]}'


def traits(code):
    return ' · '.join(TRAITS[ch] for ch in code)


def style(code):
    deep, face, ink, tint = colours(code)
    return f'--fam:{deep};--fam-ink:{ink};--fam-tint:{tint}'


def avatar(code, cls='m2a-avatar', backdrop=False):
    deep, face, ink, tint = colours(code)
    fill = {'f': face, 'd': deep, 'k': ink, 'w': '#ffffff', 'a': '#e3b23c', 'g': '#8f9aa1', 'b': '#8a5a2b', 'l': '#cfe9f3'}
    rects = [f'<rect width="16" height="16" fill="{tint}"/>'] if backdrop else []
    for y, row in enumerate(SPRITES[code]):
        x = 0
        while x < 16:   # merge runs of one colour into a single rect
            ch = row[x]
            run = 1
            while x + run < 16 and row[x + run] == ch:
                run += 1
            if ch != '.':
                rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{fill[ch]}"/>')
            x += run
    return (f'<svg class="{escape(cls)}" viewBox="0 0 16 16" shape-rendering="crispEdges" '
            f'aria-hidden="true" focusable="false" data-code="{escape(code)}">{"".join(rects)}</svg>')
