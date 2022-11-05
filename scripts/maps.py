
# w wall, r river, g grass, s spawn, b - rune (bonus)

WALL = 'w'
RIVER = 'r'
GRASS = 'g'
SPAWN = 's'
RUNE = 'b'


LEVEL_SAMPLE =\
		['                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ',\
		 '                ']

LEVEL_1 =\
		['s ww w         w',\
		 '       rrr     w',\
		 ' w rr r        w',\
		 '          b     ',\
		 '     ggg      g ',\
		 '  w  w       gg ',\
		 '           gggg ',\
		 ' b  w wr gg     ',\
		 '       gggg  rrr',\
		 'w   gggrg    s  ',\
		 'w  gg          g',\
		 'w g    b   b   w',\
		 'w               ',\
		 '      rrrr  s w ',\
		 ' s            w ',]


LEVEL_2 =\
		['s          ws  g',\
		 ' ww        r   g',\
		 ' w rr r  rg    g',\
		 ' g g    ggg w   ',\
		 'wg  ggggrrr   g ',\
		 's w grr g g  gg ',\
		 ' b  ggggggggggg ',\
		 'w r rrrrbgg     ',\
		 ' gg w ggggg brgw',\
		 'gw  gggrg  rrs  ',\
		 'gr gg  gw b w  g',\
		 'gwg   bws g    w',\
		 'g   r r g  gwg  ',\
		 '  r  rrggrw s w ',\
		 ' s     s  ggggg ',]

LEVEL_3 =\
		['gg         ws   ',\
		 'gsw  rrrw      r',\
		 '   g        w rg',\
		 ' w   bw r  b  gg',\
		 '   r gggg g g gw',\
		 'w wg  sw r bg gg',\
		 '  b rrww rrrg  g',\
		 's w gggggggg wg ',\
		 '  g rgrw rrr   w',\
		 '     g r r   w s',\
		 ' w  bg r r  b gw',\
		 'gggggg  ggg   g ',\
		 'w r    g  rgggw ',\
		 '    r bg    w sg',\
		 's wgggggggg   gg']

LEVEL_4 =\
		['g            w s',\
		 'w r  rw  bwgg   ',\
		 ' g w  s    gw  g',\
		 's   g  b w g  gw',\
		 'wg  b w   b gr  ',\
		 '   w  ggg  w   s',\
		 ' wg gggwggbg  w ',\
		 '  g gwgggr gg b ',\
		 ' swbgggrgg  g  w',\
		 'w    w w  gggw s',\
		 'g bgrg g  grg b ',\
		 'gw w   sw ggg ww',\
		 'gg  r bww   g   ',\
		 'w  ggggg   b w s',\
		 's   w     w     ']

LEVEL_5 =\
		['s w          w s',\
		 '  g rggg r b    ',\
		 'w ggg r    r  ww',\
		 '  ggggggggggggg ',\
		 'gbgggw     wggg ',\
		 'wwwg   www   www',\
		 ' bgw wb   bw  g ',\
		 's g  w  r  w  ws',\
		 'g gw wb   bw  g ',\
		 'g gg   www   www',\
		 'rwgggw     wggg ',\
		 'w ggggggggggggg ',\
		 ' b r gg  bw  ggg',\
		 'wggg rg r  g w w',\
		 '  gw  ggw r b   ',\
		 's g  w gggg w  s']

LEVEL_6 =\
		['s  w        w  s',\
		 ' wgg          w ',\
		 '    gg  wb ggg  ',\
		 'w  wg w s w g  w',\
		 'g b  g  w  gg   ',\
		 'g wsw gggggg   w',\
		 'g  b gw rggw b  ',\
		 ' w w gb gb g  w ',\
		 ' s wggrgggrgw s ',\
		 ' w  gg  g  gg w ',\
		 '  bwg w rb wgggg',\
		 'g      b     g  ',\
		 'wgwswg  w  bgg w',\
		 '     gwbs w g   ',\
		 ' w w g  w  g  w ',\
		 's  w  ggggg w  s']


LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6]