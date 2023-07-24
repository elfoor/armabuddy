import codecs


class WA1252(codecs.Codec):  # WA character set codec
    translate_characters_in  = 'аеёорстухАВЕЁМНОРСТХĄąĆćĘęŁłŃńŚśŹźŻż'
    translate_characters_out = 'aeëopcтyxABEËMHOPCTXAaCcEeLlNnSsZzZz'
    translation_table = str.maketrans(translate_characters_in, translate_characters_out)

    decoding_table = (  # cp1252 with tweaks (marked with * before name). ref: https://worms2d.info/WA_character_table
        '\0'    # 0x00 -> \u0000 NULL
        '\x01'  # 0x01 -> \u0001 START OF HEADING
        '\x02'  # 0x02 -> \u0002 START OF TEXT
        '\x03'  # 0x03 -> \u0003 END OF TEXT
        '\x04'  # 0x04 -> \u0004 END OF TRANSMISSION
        '\x05'  # 0x05 -> \u0005 ENQUIRY
        '\x06'  # 0x06 -> \u0006 ACKNOWLEDGE
        '\a'    # 0x07 -> \u0007 BELL
        '\b'    # 0x08 -> \u0008 BACKSPACE
        '\t'    # 0x09 -> \u0009 HORIZONTAL TABULATION
        '\n'    # 0x0A -> \u000A LINE FEED
        '\v'    # 0x0B -> \u000B VERTICAL TABULATION
        '\f'    # 0x0C -> \u000C FORM FEED
        '\r'    # 0x0D -> \u000D CARRIAGE RETURN
        '\x0E'  # 0x0E -> \u000E SHIFT OUT
        '\x0F'  # 0x0F -> \u000F SHIFT IN
        # WormNET game names translation. Give characters "&'<>\ for bytes 0x10 to 0x15, see update logs for more info:
        # v3.6.30.0_Beta and v3.7.2.1 in https://worms2d.info/Worms_Armageddon_ReadMe_(English)#Version_History
        '"'     # 0x10 -> \u0022 * QUOTATION MARK
        '&'     # 0x11 -> \u0026 * AMPERSAND
        "'"     # 0x12 -> \u0027 * APOSTROPHE
        '<'     # 0x13 -> \u003C * LESS-THAN SIGN
        '>'     # 0x14 -> \u003E * GREATER-THAN SIGN
        '\\'    # 0x15 -> \u005C * REVERSE SOLIDUS
        '\0'    # 0x16 -> \u0000 * Reserved / Unused
        '\0'    # 0x17 -> \u0000 * Reserved / Unused
        '\0'    # 0x18 -> \u0000 * Reserved / Unused
        '\0'    # 0x19 -> \u0000 * Reserved / Unused
        '\0'    # 0x1A -> \u0000 * Reserved / Unused
        '\0'    # 0x1B -> \u0000 * Reserved / Unused
        '\0'    # 0x1C -> \u0000 * Reserved / Unused
        '\0'    # 0x1D -> \u0000 * Reserved / Unused
        '\0'    # 0x1E -> \u0000 * Reserved / Unused
        '\0'    # 0x1F -> \u0000 * Reserved / Unused
        ' '     # 0x20 -> \u0020 SPACE
        '!'     # 0x21 -> \u0021 EXCLAMATION MARK
        '"'     # 0x22 -> \u0022 QUOTATION MARK
        '#'     # 0x23 -> \u0023 NUMBER SIGN
        '$'     # 0x24 -> \u0024 DOLLAR SIGN
        '%'     # 0x25 -> \u0025 PERCENT SIGN
        '&'     # 0x26 -> \u0026 AMPERSAND
        "'"     # 0x27 -> \u0027 APOSTROPHE
        '('     # 0x28 -> \u0028 LEFT PARENTHESIS
        ')'     # 0x29 -> \u0029 RIGHT PARENTHESIS
        '*'     # 0x2A -> \u002A ASTERISK
        '+'     # 0x2B -> \u002B PLUS SIGN
        ','     # 0x2C -> \u002C COMMA
        '-'     # 0x2D -> \u002D HYPHEN-MINUS
        '.'     # 0x2E -> \u002E FULL STOP
        '/'     # 0x2F -> \u002F SOLIDUS
        '0'     # 0x30 -> \u0030 DIGIT ZERO
        '1'     # 0x31 -> \u0031 DIGIT ONE
        '2'     # 0x32 -> \u0032 DIGIT TWO
        '3'     # 0x33 -> \u0033 DIGIT THREE
        '4'     # 0x34 -> \u0034 DIGIT FOUR
        '5'     # 0x35 -> \u0035 DIGIT FIVE
        '6'     # 0x36 -> \u0036 DIGIT SIX
        '7'     # 0x37 -> \u0037 DIGIT SEVEN
        '8'     # 0x38 -> \u0038 DIGIT EIGHT
        '9'     # 0x39 -> \u0039 DIGIT NINE
        ':'     # 0x3A -> \u003A COLON
        ';'     # 0x3B -> \u003B SEMICOLON
        '<'     # 0x3C -> \u003C LESS-THAN SIGN
        '='     # 0x3D -> \u003D EQUALS SIGN
        '>'     # 0x3E -> \u003E GREATER-THAN SIGN
        '?'     # 0x3F -> \u003F QUESTION MARK
        '@'     # 0x40 -> \u0040 COMMERCIAL AT
        'A'     # 0x41 -> \u0041 LATIN CAPITAL LETTER A
        'B'     # 0x42 -> \u0042 LATIN CAPITAL LETTER B
        'C'     # 0x43 -> \u0043 LATIN CAPITAL LETTER C
        'D'     # 0x44 -> \u0044 LATIN CAPITAL LETTER D
        'E'     # 0x45 -> \u0045 LATIN CAPITAL LETTER E
        'F'     # 0x46 -> \u0046 LATIN CAPITAL LETTER F
        'G'     # 0x47 -> \u0047 LATIN CAPITAL LETTER G
        'H'     # 0x48 -> \u0048 LATIN CAPITAL LETTER H
        'I'     # 0x49 -> \u0049 LATIN CAPITAL LETTER I
        'J'     # 0x4A -> \u004A LATIN CAPITAL LETTER J
        'K'     # 0x4B -> \u004B LATIN CAPITAL LETTER K
        'L'     # 0x4C -> \u004C LATIN CAPITAL LETTER L
        'M'     # 0x4D -> \u004D LATIN CAPITAL LETTER M
        'N'     # 0x4E -> \u004E LATIN CAPITAL LETTER N
        'O'     # 0x4F -> \u004F LATIN CAPITAL LETTER O
        'P'     # 0x50 -> \u0050 LATIN CAPITAL LETTER P
        'Q'     # 0x51 -> \u0051 LATIN CAPITAL LETTER Q
        'R'     # 0x52 -> \u0052 LATIN CAPITAL LETTER R
        'S'     # 0x53 -> \u0053 LATIN CAPITAL LETTER S
        'T'     # 0x54 -> \u0054 LATIN CAPITAL LETTER T
        'U'     # 0x55 -> \u0055 LATIN CAPITAL LETTER U
        'V'     # 0x56 -> \u0056 LATIN CAPITAL LETTER V
        'W'     # 0x57 -> \u0057 LATIN CAPITAL LETTER W
        'X'     # 0x58 -> \u0058 LATIN CAPITAL LETTER X
        'Y'     # 0x59 -> \u0059 LATIN CAPITAL LETTER Y
        'Z'     # 0x5A -> \u005A LATIN CAPITAL LETTER Z
        '['     # 0x5B -> \u005B LEFT SQUARE BRACKET
        '\\'    # 0x5C -> \u005C REVERSE SOLIDUS
        ']'     # 0x5D -> \u005D RIGHT SQUARE BRACKET
        '^'     # 0x5E -> \u005E CIRCUMFLEX ACCENT
        '_'     # 0x5F -> \u005F LOW LINE
        '`'     # 0x60 -> \u0060 GRAVE ACCENT
        'a'     # 0x61 -> \u0061 LATIN SMALL LETTER A
        'b'     # 0x62 -> \u0062 LATIN SMALL LETTER B
        'c'     # 0x63 -> \u0063 LATIN SMALL LETTER C
        'd'     # 0x64 -> \u0064 LATIN SMALL LETTER D
        'e'     # 0x65 -> \u0065 LATIN SMALL LETTER E
        'f'     # 0x66 -> \u0066 LATIN SMALL LETTER F
        'g'     # 0x67 -> \u0067 LATIN SMALL LETTER G
        'h'     # 0x68 -> \u0068 LATIN SMALL LETTER H
        'i'     # 0x69 -> \u0069 LATIN SMALL LETTER I
        'j'     # 0x6A -> \u006A LATIN SMALL LETTER J
        'k'     # 0x6B -> \u006B LATIN SMALL LETTER K
        'l'     # 0x6C -> \u006C LATIN SMALL LETTER L
        'm'     # 0x6D -> \u006D LATIN SMALL LETTER M
        'n'     # 0x6E -> \u006E LATIN SMALL LETTER N
        'o'     # 0x6F -> \u006F LATIN SMALL LETTER O
        'p'     # 0x70 -> \u0070 LATIN SMALL LETTER P
        'q'     # 0x71 -> \u0071 LATIN SMALL LETTER Q
        'r'     # 0x72 -> \u0072 LATIN SMALL LETTER R
        's'     # 0x73 -> \u0073 LATIN SMALL LETTER S
        't'     # 0x74 -> \u0074 LATIN SMALL LETTER T
        'u'     # 0x75 -> \u0075 LATIN SMALL LETTER U
        'v'     # 0x76 -> \u0076 LATIN SMALL LETTER V
        'w'     # 0x77 -> \u0077 LATIN SMALL LETTER W
        'x'     # 0x78 -> \u0078 LATIN SMALL LETTER X
        'y'     # 0x79 -> \u0079 LATIN SMALL LETTER Y
        'z'     # 0x7A -> \u007A LATIN SMALL LETTER Z
        '{'     # 0x7B -> \u007B LEFT CURLY BRACKET
        '|'     # 0x7C -> \u007C VERTICAL LINE
        '}'     # 0x7D -> \u007D RIGHT CURLY BRACKET
        '~'     # 0x7E -> \u007E TILDE
        '\0'    # 0x7F -> \u0000 * Reserved / Unused
        'Б'     # 0x80 -> \u0411 * CYRILLIC CAPITAL LETTER BE
        'Г'     # 0x81 -> \u0413 * CYRILLIC CAPITAL LETTER GHE
        'Д'     # 0x82 -> \u0414 * CYRILLIC CAPITAL LETTER DE
        'Ж'     # 0x83 -> \u0416 * CYRILLIC CAPITAL LETTER ZHE
        'З'     # 0x84 -> \u0417 * CYRILLIC CAPITAL LETTER ZE
        'И'     # 0x85 -> \u0418 * CYRILLIC CAPITAL LETTER I
        'Й'     # 0x86 -> \u0419 * CYRILLIC CAPITAL LETTER SHORT I
        'К'     # 0x87 -> \u041A * CYRILLIC CAPITAL LETTER KA
        'Л'     # 0x88 -> \u041B * CYRILLIC CAPITAL LETTER EL
        'П'     # 0x89 -> \u041F * CYRILLIC CAPITAL LETTER PE
        'У'     # 0x8A -> \u0423 * CYRILLIC CAPITAL LETTER U
        'Ф'     # 0x8B -> \u0424 * CYRILLIC CAPITAL LETTER EF
        'Ц'     # 0x8C -> \u0426 * CYRILLIC CAPITAL LETTER TSE
        'Ч'     # 0x8D -> \u0427 * CYRILLIC CAPITAL LETTER CHE
        'Ш'     # 0x8E -> \u0428 * CYRILLIC CAPITAL LETTER SHA
        'Щ'     # 0x8F -> \u0429 * CYRILLIC CAPITAL LETTER SHCHA
        'Ъ'     # 0x90 -> \u042A * CYRILLIC CAPITAL LETTER HARD SIGN
        'Ы'     # 0x91 -> \u042B * CYRILLIC CAPITAL LETTER YERU
        'Ь'     # 0x92 -> \u042C * CYRILLIC CAPITAL LETTER SOFT SIGN
        'Э'     # 0x93 -> \u042D * CYRILLIC CAPITAL LETTER E
        'Ю'     # 0x94 -> \u042E * CYRILLIC CAPITAL LETTER YU
        '\0'    # 0x95 -> \u0000 * Reserved / Unused
        'Я'     # 0x96 -> \u042F * CYRILLIC CAPITAL LETTER YA
        'б'     # 0x97 -> \u0431 * CYRILLIC SMALL LETTER BE
        'в'     # 0x98 -> \u0432 * CYRILLIC SMALL LETTER VE
        'г'     # 0x99 -> \u0433 * CYRILLIC SMALL LETTER GHE
        'д'     # 0x9A -> \u0434 * CYRILLIC SMALL LETTER DE
        'ж'     # 0x9B -> \u0436 * CYRILLIC SMALL LETTER ZHE
        'з'     # 0x9C -> \u0437 * CYRILLIC SMALL LETTER ZE
        'и'     # 0x9D -> \u0438 * CYRILLIC SMALL LETTER I
        'й'     # 0x9E -> \u0439 * CYRILLIC SMALL LETTER SHORT I
        'Ÿ'     # 0x9F -> \u0178 LATIN CAPITAL LETTER Y WITH DIAERESIS
        '\xA0'  # 0xA0 -> \u00A0 NO-BREAK SPACE
        '¡'     # 0xA1 -> \u00A1 INVERTED EXCLAMATION MARK
        'к'     # 0xA2 -> \u043A * CYRILLIC SMALL LETTER KA
        '£'     # 0xA3 -> \u00A3 POUND SIGN
        '\0'    # 0xA4 -> \u0000 * Reserved / Unused
        'л'     # 0xA5 -> \u043B * CYRILLIC SMALL LETTER EL
        'м'     # 0xA6 -> \u043C * CYRILLIC SMALL LETTER EM
        'н'     # 0xA7 -> \u043D * CYRILLIC SMALL LETTER EN
        'п'     # 0xA8 -> \u043F * CYRILLIC SMALL LETTER PE
        'т'     # 0xA9 -> \u0442 * CYRILLIC SMALL LETTER TE
        'ф'     # 0xAA -> \u0444 * CYRILLIC SMALL LETTER EF
        'ц'     # 0xAB -> \u0446 * CYRILLIC SMALL LETTER TSE
        'ч'     # 0xAC -> \u0447 * CYRILLIC SMALL LETTER CHE
        'ш'     # 0xAD -> \u0448 * CYRILLIC SMALL LETTER SHA
        'щ'     # 0xAE -> \u0449 * CYRILLIC SMALL LETTER SHCHA
        'ъ'     # 0xAF -> \u044A * CYRILLIC SMALL LETTER HARD SIGN
        'ы'     # 0xB0 -> \u044B * CYRILLIC SMALL LETTER YERU
        'ь'     # 0xB1 -> \u044C * CYRILLIC SMALL LETTER SOFT SIGN
        'э'     # 0xB2 -> \u044D * CYRILLIC SMALL LETTER E
        'ю'     # 0xB3 -> \u044E * CYRILLIC SMALL LETTER YU
        'я'     # 0xB4 -> \u044F * CYRILLIC SMALL LETTER YA
        'Ő'     # 0xB5 -> \u0150 * LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
        'ő'     # 0xB6 -> \u0151 * LATIN SMALL LETTER O WITH DOUBLE ACUTE
        'Ű'     # 0xB7 -> \u0170 * LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
        'ű'     # 0xB8 -> \u0171 * LATIN SMALL LETTER U WITH DOUBLE ACUTE
        'Ğ'     # 0xB9 -> \u011E * LATIN CAPITAL LETTER G WITH BREVE
        'ğ'     # 0xBA -> \u011F * LATIN SMALL LETTER G WITH BREVE
        'Ş'     # 0xBB -> \u015E * LATIN CAPITAL LETTER S WITH CEDILLA
        'ş'     # 0xBC -> \u015F * LATIN SMALL LETTER S WITH CEDILLA
        'İ'     # 0xBD -> \u0130 * LATIN CAPITAL LETTER I WITH DOT ABOVE
        'ı'     # 0xBE -> \u0131 * LATIN SMALL LETTER DOTLESS I
        '¿'     # 0xBF -> \u00BF INVERTED QUESTION MARK
        'À'     # 0xC0 -> \u00C0 LATIN CAPITAL LETTER A WITH GRAVE
        'Á'     # 0xC1 -> \u00C1 LATIN CAPITAL LETTER A WITH ACUTE
        'Â'     # 0xC2 -> \u00C2 LATIN CAPITAL LETTER A WITH CIRCUMFLEX
        'Ã'     # 0xC3 -> \u00C3 LATIN CAPITAL LETTER A WITH TILDE
        'Ä'     # 0xC4 -> \u00C4 LATIN CAPITAL LETTER A WITH DIAERESIS
        'Å'     # 0xC5 -> \u00C5 LATIN CAPITAL LETTER A WITH RING ABOVE
        'Æ'     # 0xC6 -> \u00C6 LATIN CAPITAL LETTER AE
        'Ç'     # 0xC7 -> \u00C7 LATIN CAPITAL LETTER C WITH CEDILLA
        'È'     # 0xC8 -> \u00C8 LATIN CAPITAL LETTER E WITH GRAVE
        'É'     # 0xC9 -> \u00C9 LATIN CAPITAL LETTER E WITH ACUTE
        'Ê'     # 0xCA -> \u00CA LATIN CAPITAL LETTER E WITH CIRCUMFLEX
        'Ë'     # 0xCB -> \u00CB LATIN CAPITAL LETTER E WITH DIAERESIS
        'Ì'     # 0xCC -> \u00CC LATIN CAPITAL LETTER I WITH GRAVE
        'Í'     # 0xCD -> \u00CD LATIN CAPITAL LETTER I WITH ACUTE
        'Î'     # 0xCE -> \u00CE LATIN CAPITAL LETTER I WITH CIRCUMFLEX
        'Ï'     # 0xCF -> \u00CF LATIN CAPITAL LETTER I WITH DIAERESIS
        'À'     # 0xD0 -> \u00C0 LATIN CAPITAL LETTER A WITH GRAVE
        'Ñ'     # 0xD1 -> \u00D1 LATIN CAPITAL LETTER N WITH TILDE
        'Ò'     # 0xD2 -> \u00D2 LATIN CAPITAL LETTER O WITH GRAVE
        'Ó'     # 0xD3 -> \u00D3 LATIN CAPITAL LETTER O WITH ACUTE
        'Ô'     # 0xD4 -> \u00D4 LATIN CAPITAL LETTER O WITH CIRCUMFLEX
        'Õ'     # 0xD5 -> \u00D5 LATIN CAPITAL LETTER O WITH TILDE
        'Ö'     # 0xD6 -> \u00D6 LATIN CAPITAL LETTER O WITH DIAERESIS
        '×'     # 0xD7 -> \u00D7 MULTIPLICATION SIGN
        'Ø'     # 0xD8 -> \u00D8 LATIN CAPITAL LETTER O WITH STROKE
        'Ù'     # 0xD9 -> \u00D9 LATIN CAPITAL LETTER U WITH GRAVE
        'Ú'     # 0xDA -> \u00DA LATIN CAPITAL LETTER U WITH ACUTE
        'Û'     # 0xDB -> \u00DB LATIN CAPITAL LETTER U WITH CIRCUMFLEX
        'Ü'     # 0xDC -> \u00DC LATIN CAPITAL LETTER U WITH DIAERESIS
        'Ý'     # 0xDD -> \u00DD LATIN CAPITAL LETTER Y WITH ACUTE
        'Þ'     # 0xDE -> \u00DE LATIN CAPITAL LETTER THORN
        'ß'     # 0xDF -> \u00DF LATIN SMALL LETTER SHARP S
        'à'     # 0xE0 -> \u00E0 LATIN SMALL LETTER A WITH GRAVE
        'á'     # 0xE1 -> \u00E1 LATIN SMALL LETTER A WITH ACUTE
        'â'     # 0xE2 -> \u00E2 LATIN SMALL LETTER A WITH CIRCUMFLEX
        'ã'     # 0xE3 -> \u00E3 LATIN SMALL LETTER A WITH TILDE
        'ä'     # 0xE4 -> \u00E4 LATIN SMALL LETTER A WITH DIAERESIS
        'å'     # 0xE5 -> \u00E5 LATIN SMALL LETTER A WITH RING ABOVE
        'æ'     # 0xE6 -> \u00E6 LATIN SMALL LETTER AE
        'ç'     # 0xE7 -> \u00E7 LATIN SMALL LETTER C WITH CEDILLA
        'è'     # 0xE8 -> \u00E8 LATIN SMALL LETTER E WITH GRAVE
        'é'     # 0xE9 -> \u00E9 LATIN SMALL LETTER E WITH ACUTE
        'ê'     # 0xEA -> \u00EA LATIN SMALL LETTER E WITH CIRCUMFLEX
        'ë'     # 0xEB -> \u00EB LATIN SMALL LETTER E WITH DIAERESIS
        'ì'     # 0xEC -> \u00EC LATIN SMALL LETTER I WITH GRAVE
        'í'     # 0xED -> \u00ED LATIN SMALL LETTER I WITH ACUTE
        'î'     # 0xEE -> \u00EE LATIN SMALL LETTER I WITH CIRCUMFLEX
        'ï'     # 0xEF -> \u00EF LATIN SMALL LETTER I WITH DIAERESIS
        'ð'     # 0xF0 -> \u00F0 LATIN SMALL LETTER ETH
        'ñ'     # 0xF1 -> \u00F1 LATIN SMALL LETTER N WITH TILDE
        'ò'     # 0xF2 -> \u00F2 LATIN SMALL LETTER O WITH GRAVE
        'ó'     # 0xF3 -> \u00F3 LATIN SMALL LETTER O WITH ACUTE
        'ô'     # 0xF4 -> \u00F4 LATIN SMALL LETTER O WITH CIRCUMFLEX
        'õ'     # 0xF5 -> \u00F5 LATIN SMALL LETTER O WITH TILDE
        'ö'     # 0xF6 -> \u00F6 LATIN SMALL LETTER O WITH DIAERESIS
        '÷'     # 0xF7 -> \u00F7 DIVISION SIGN
        'ø'     # 0xF8 -> \u00F8 LATIN SMALL LETTER O WITH STROKE
        'ù'     # 0xF9 -> \u00F9 LATIN SMALL LETTER U WITH GRAVE
        'ú'     # 0xFA -> \u00FA LATIN SMALL LETTER U WITH ACUTE
        'û'     # 0xFB -> \u00FB LATIN SMALL LETTER U WITH CIRCUMFLEX
        'ü'     # 0xFC -> \u00FC LATIN SMALL LETTER U WITH DIAERESIS
        'ý'     # 0xFD -> \u00FD LATIN SMALL LETTER Y WITH ACUTE
        'þ'     # 0xFE -> \u00FE LATIN SMALL LETTER THORN
        'ÿ'     # 0xFF -> \u00FF LATIN SMALL LETTER Y WITH DIAERESIS
    )
    encoding_table = codecs.charmap_build(decoding_table)
    handled_characters = set(''.join(decoding_table) + translate_characters_in)

    @classmethod
    def encode(cls, input_, errors='strict'):
        return codecs.charmap_encode(input_.translate(cls.translation_table), errors, cls.encoding_table)

    @classmethod
    def decode(cls, input_, errors='strict'):
        return codecs.charmap_decode(input_, errors, cls.decoding_table)

    @staticmethod
    def lookup(name):
        if name != 'wa1252':
            return None

        return codecs.CodecInfo(
            name='wa1252',
            encode=WA1252().encode,
            decode=WA1252().decode,
        )
