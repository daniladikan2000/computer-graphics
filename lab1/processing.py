from models import RGB, CMYK, HSV

def rgb_to_cmyk(rgb: RGB) -> CMYK:
    r, g, b = rgb.r / 255.0, rgb.g / 255.0, rgb.b / 255.0
    k = 1.0 - max(r, g, b)
    
    if k == 1.0: 
        return CMYK(0, 0, 0, 100)
    
    c = (1.0 - r - k) / (1.0 - k)
    m = (1.0 - g - k) / (1.0 - k)
    y = (1.0 - b - k) / (1.0 - k)
    return CMYK(round(c * 100), round(m * 100), round(y * 100), round(k * 100))

def cmyk_to_rgb(cmyk: CMYK) -> RGB:
    c, m, y, k = cmyk.c, cmyk.m, cmyk.y, cmyk.k
    
    r = 255 * (1.0 - c / 100.0) * (1.0 - k / 100.0)
    g = 255 * (1.0 - m / 100.0) * (1.0 - k / 100.0)
    b = 255 * (1.0 - y / 100.0) * (1.0 - k / 100.0)
    return RGB(round(r), round(g), round(b))

def rgb_to_hsv(rgb: RGB) -> HSV:
    r, g, b = rgb.r / 255.0, rgb.g / 255.0, rgb.b / 255.0
    
    cmax, cmin = max(r, g, b), min(r, g, b)
    delta = cmax - cmin
    
    if delta == 0: 
        h = 0.0
    elif cmax == r:
        h = 60.0 * (((g - b) / delta) % 6)
    elif cmax == g: 
        h = 60.0 * (((b - r) / delta) + 2)
    else: 
        h = 60.0 * (((r - g) / delta) + 4)
        
    s = 0.0 if cmax == 0 else delta / cmax
    return HSV(round(h) % 360, round(s * 100), round(cmax * 100))

def hsv_to_rgb(hsv: HSV) -> RGB:
    h = 0 if hsv.h == 360 else hsv.h
    s, v = hsv.s / 100.0, hsv.v / 100.0
    
    c = v * s
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = v - c
    
    if 0 <= h < 60: 
        r, g, b = c, x, 0.0
    elif 60 <= h < 120: 
        r, g, b = x, c, 0.0
    elif 120 <= h < 180: 
        r, g, b = 0.0, c, x
    elif 180 <= h < 240: 
        r, g, b = 0.0, x, c
    elif 240 <= h < 300: 
        r, g, b = x, 0.0, c
    else: 
        r, g, b = c, 0.0, x
    return RGB(round((r + m) * 255), round((g + m) * 255), round((b + m) * 255))

def rgb_to_hex(rgb: RGB) -> str:
    return f"#{rgb.r:02X}{rgb.g:02X}{rgb.b:02X}"

def hex_to_rgb(hex_str: str) -> RGB:
    hex_str = hex_str.lstrip('#')
    return RGB(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))