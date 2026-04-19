import framebuf

# RGB565 Palette including new shades for depth
PALETTE = {
    '.': 0x0000, # Transparent (Black)
    'W': 0xFFFF, # White
    'w': 0xBDF7, # Light Grey
    'g': 0x7BEF, # Dark Grey
    'R': 0xF800, # Red
    'r': 0x7800, # Dark Red
    'B': 0x001F, # Blue
    'C': 0x07FF, # Cyan
    'G': 0x07E0, # Green
    'd': 0x03E0, # Dark Green
    'Y': 0xFFE0, # Yellow
    'O': 0xFD20, # Orange
    'M': 0xF81F, # Magenta
    'm': 0x780F, # Dark Magenta
}

def compile_sprite(ascii_art):
    """
    Converts an array of ASCII strings into a FrameBuffer suitable for blitting.
    """
    height = len(ascii_art)
    width = len(ascii_art[0])
    # 2 bytes per pixel for RGB565
    buf = bytearray(width * height * 2)
    
    idx = 0
    for row in ascii_art:
        for char in row:
            color = PALETTE.get(char, 0x0000)
            buf[idx] = color & 0xFF
            buf[idx+1] = color >> 8
            idx += 2
            
    return framebuf.FrameBuffer(buf, width, height, framebuf.RGB565)

# --- DEFINITIONS ---

# Player Ship: Straight Flight (16x16)
_player_straight = [
    ".......WW.......",
    ".......WW.......",
    "......wWWw......",
    "......wWWw......",
    "......gwwg......",
    ".....WwwwwW.....",
    ".....WwwwwW.....",
    "...g.CwwwwC.g...",
    "...WWCCwwCCWW...",
    "..WWwCCCCCCwWW..",
    "..WwwCCCCCCwwW..",
    ".gWwgCwwwwCgwWg.",
    ".gWw.ggwwgg.wWg.",
    ".Ww..g....g..wW.",
    ".W............W.",
    "................"
]

_player_straight_f2 = _player_straight.copy()
_player_straight_f2[13] = ".Ww..g.OO.g..wW."
_player_straight_f2[14] = ".W.....YY.....W."
_player_straight_f2[15] = ".......Y........"

# Player Ship: Bank Left (16x16)
_player_left = [
    "........WW......",
    ".......wWW......",
    ".......wWW......",
    "......gwwW......",
    "......Cwwgg.....",
    ".....CCwW.......",
    "....CCCwW.......",
    "...CCCCww.g.....",
    "..CCWCCwwWw.....",
    "..CWWWCCCwww....",
    ".gCWWWCCCwW.....",
    ".WgWggCwwwW.....",
    ".WW...ggwW......",
    ".g......wW......",
    "........g.......",
    "................"
]

_player_left_f2 = _player_left.copy()
_player_left_f2[13] = ".g......wW.O...."
_player_left_f2[14] = "........g...Y..."

# Player Ship: Bank Right (16x16)
_player_right = [
    "......WW........",
    "......WWw.......",
    "......WWw.......",
    "......Wwwg......",
    ".....ggwwC......",
    ".......WwCC.....",
    ".......WwCCC....",
    ".....g.wwCCCC...",
    ".....wWwwCCWCC..",
    "....wwwCCCWWWC..",
    ".....WwCCCWWWg..",
    ".....WwwwCggWg..",
    "......Wwgg...W..",
    "......Ww......g.",
    ".......g........",
    "................"
]

_player_right_f2 = _player_right.copy()
_player_right_f2[13] = "....O.Ww......g."
_player_right_f2[14] = "...Y...g........"

# Scout Enemy (16x16)
_scout_f1 = [
    ".......rr.......",
    "......rRRr......",
    "......RRRR......",
    ".....RwRRwR.....",
    "....RwwRRwwR....",
    "...RRwRRRRwRR...",
    "...RwRRRRRRwR...",
    "..RRwwwwwwwwRR..",
    "..RwwwRRRRwwwR..",
    "..Rr..rRRr..rR..",
    ".R.R...rr...R.R.",
    ".R.R........R.R.",
    "R..R........R..R",
    "R..r........r..R",
    "r..............r",
    "................"
]

_scout_f2 = [
    ".......rr.......",
    "......rRRr......",
    "......RRRR......",
    ".....RwRRwR.....",
    "....RwwRRwwR....",
    "...RRwRRRRwRR...",
    "...RwRRRRRRwR...",
    "..RRwwwwwwwwRR..",
    "..RwwwRRRRwwwR..",
    "..Rr.MrRRrM.rR..",
    ".R.R..MMMM..R.R.",
    ".R.R........R.R.",
    "R..R........R..R",
    "................",
    "R..r........r..R",
    "r..............r"
]

# Tank Enemy (16x16)
_tank_f1 = [
    "gWwW........WwWg",
    "gwWw..rrrr..wWwg",
    "gwWw.rMMMMr.wWwg",
    "gwwWw.rMMr.wWwwg",
    "ggwwwW.rr.Wwwwgg",
    ".gwwwwWwwWwwwwg.",
    ".ggwwwRwwRwwwgg.",
    "..gwwwRwwRwwwg..",
    "..ggwwRwwRwwgg..",
    "...gwwRRRRwwg...",
    "...ggwRRRRwgg...",
    "....gwRRRRwg....",
    "....gRwwwwwg....",
    "....gRRRRRRg....",
    "....gR.RR.Rg....",
    "....gg.gg.gg...."
]

_tank_f2 = [
    "gWwW........WwWg",
    "gwWw........wWwg",
    "gwWw..rrrr..wWwg",
    "gwwWw.rMMr.wWwwg",
    "ggwwwW.rr.Wwwwgg",
    ".gwwwwWwwWwwwwg.",
    ".ggwwwRwwRwwwgg.",
    "..gwwwRrRrwwwg..",
    "..ggwwrRrRwwgg..",
    "...gwwRRRRwwg...",
    "...ggwRRwRwgg...",
    "....gwRwRwwg....",
    "....gwwwRwwg....",
    "....gRRRRRRg....",
    "....gg.gg.gg....",
    "....O......O...."
]

# Boss Ship (64x30)
_boss_f1 = [
    "................................gM..............................",
    "...............................gMMg.............................",
    "..............................gMMMMg............................",
    ".......wWWWWWWWw.............gMMMMMMg.............wWWWWWWWw.....",
    "......wWwwwwwwwWw...........gMwwMMwwMg...........wWwwwwwwwWw....",
    ".....gWw.......wWg.........gMwWWMMWWwMg.........gWw.......wWg...",
    "....gwWg.......gWwg.......gMwMwwMMwwMwMg.......gwWg.......gWwg..",
    "...ggwwg.......gwwgg.....gMwMM..MM..MMwMg.....ggwwg.......gwwgg.",
    "..ggwwg.........gwwgg...gMwMM...MM...MMwMg...ggwwg.........gwwgg",
    ".gWwwwg.........gwwwWg.gwMwMM...MM...MMwMwg.gWwwwg.........gwwwW",
    ".WwwwwWw.......wWwwwwWgwwMwMM..gMMg..MMwMwwgWwwwwWw.......wWwwww",
    ".wWwwwwwWwwwwwWwwwwwWwwwwwMwwggwMMwggwwMwwwwWwwwwwWwwwwwWwwwwwWw",
    ".gwWwwwwwwwwwwwwwwwWwwwwwMwWWwggMMggwWWwMwwwwwWwwwwwwwwwwwwwwwWg",
    "..gwWwwwwwwwwwwwwwWwwwwwwMwWWww.MM.wwWWwMwwwwwwWwwwwwwwwwwwwwWg.",
    "...gWwwwwWWWWwwwwwWg....gwMwww..MM..wwwMwg....gWwwwwwWWWWwwwwWg.",
    "...gRwwwWWRRWWwwwRg......gwMMM..MM..MMMwg......gRwwwWWRRWWwwwRg.",
    "....RwwWWReeRWWwwR........gwMMM.MM.MMMwg........RwwWWReeRWWwwR..",
    "....RwwWWreeRWWwwR.........gMwMMMMMMwMg.........RwwWWreeRWWwwR..",
    "....ggwWWeeeRWWwgg..........gMwwMMwwMg..........ggwWWeeeRWWwgg..",
    ".....ggWWreeeWWgg............gwMwwMwg............ggWWreeeWWgg...",
    "......ggWReeRWgg..............gWwwWg..............ggWReeRWgg....",
    ".......ggWRRWgg................gWWg................ggWRRWgg.....",
    "........ggWWgg.................gWWg.................ggWWgg......",
    ".........gggg...................gg...................gggg.......",
    "................................................................",
    ".................................R..............................",
    "........R........................r.......................R......",
    "........O........................O.......................O......",
    "........Y................................................Y......",
    "................................................................"
]

_boss_f2 = _boss_f1.copy()
_boss_f2[25] = "................................M..............................."
_boss_f2[26] = "........r........................R.......................r......"
_boss_f2[27] = "........O........................O.......................O......"
_boss_f2[28] = ".................................Y.............................."

# Powerup: Triple Shot (12x12)
_pu_triple = [
    "....oooo....",
    "..ooOOOOoo..",
    ".oOOOOOOOOo.",
    ".oOOwwwwOOo.",
    "oOOOwWWwOOOo",
    "oOOOwWWwOOOo",
    "oOOOwwwwOOOo",
    "oOOOwWWwOOOo",
    ".oOOwwwwOOo.",
    ".oOOOOOOOOo.",
    "..ooOOOOoo..",
    "....oooo...."
]

_pu_triple_f2 = [
    ".....oo.....",
    "...oooooo...",
    "..ooOOOOoo..",
    ".ooOOwwOOoo.",
    ".oOOwWWwOOo.",
    "ooOOwwwwOOoo",
    "ooOOwwwwOOoo",
    ".oOOwWWwOOo.",
    ".ooOOwwOOoo.",
    "..ooOOOOoo..",
    "...oooooo...",
    ".....oo....."
]

# Powerup: Speed (12x12)
_pu_speed = [
    "....GGGG....",
    "..GGGGGGGG..",
    ".GGGwwwwGGG.",
    ".GGGwwwwGGG.",
    "GGGGwGGGGGGG",
    "GGGGwGGGGGgG",
    "GGGGwwwwGgGg",
    "GGGGwwwwGGgG",
    ".GGGwGGGGgG.",
    ".GGGwwwwGgG.",
    "..GGGGGGGg..",
    "....GGGG...."
]
# We'll use triple_f2 structure but colored for speed to make it spin
_pu_speed_f2 = [
    ".....GG.....",
    "...GGGGGG...",
    "..GGGGGGGG..",
    ".GGGGwwGGGG.",
    ".GGGwwwwGGG.",
    "GGGGwGGwGGGG",
    "GGGGwGGwGGGG",
    ".GGGwwwwGGG.",
    ".GGGGwwGGGG.",
    "..GGGGGGGG..",
    "...GGGGGG...",
    ".....GG....."
]

# Dictionary to hold the compiled framebuffers
COMPILED = {}

def compile_all():
    global COMPILED
    COMPILED['player_straight_f1'] = compile_sprite(_player_straight)
    COMPILED['player_straight_f2'] = compile_sprite(_player_straight_f2)
    COMPILED['player_left_f1'] = compile_sprite(_player_left)
    COMPILED['player_left_f2'] = compile_sprite(_player_left_f2)
    COMPILED['player_right_f1'] = compile_sprite(_player_right)
    COMPILED['player_right_f2'] = compile_sprite(_player_right_f2)
    
    COMPILED['scout_f1'] = compile_sprite(_scout_f1)
    COMPILED['scout_f2'] = compile_sprite(_scout_f2)
    COMPILED['tank_f1'] = compile_sprite(_tank_f1)
    COMPILED['tank_f2'] = compile_sprite(_tank_f2)
    
    COMPILED['boss_f1'] = compile_sprite(_boss_f1)
    COMPILED['boss_f2'] = compile_sprite(_boss_f2)
    
    COMPILED['pu_triple_f1'] = compile_sprite(_pu_triple)
    COMPILED['pu_triple_f2'] = compile_sprite(_pu_triple_f2)
    
    COMPILED['pu_speed_f1'] = compile_sprite(_pu_speed)
    COMPILED['pu_speed_f2'] = compile_sprite(_pu_speed_f2)
