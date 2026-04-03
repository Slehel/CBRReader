"""
Generate icon.ico for CBR Reader — Open Comic Book design.
Produces sizes: 16, 32, 48, 64, 128, 256 bundled into one .ico file.
Run: python make_icon.py
"""

from PIL import Image, ImageDraw
import math


def draw_star(draw, cx, cy, r_outer, r_inner, points, fill):
    """Draw a star polygon centered at (cx, cy)."""
    coords = []
    for i in range(points * 2):
        angle = math.radians(i * 180 / points - 90)
        r = r_outer if i % 2 == 0 else r_inner
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(coords, fill=fill)


def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 96  # scale factor relative to 96px design grid

    # --- Background: rounded rect ---
    bg_color = (26, 26, 46, 255)        # #1a1a2e
    radius = int(20 * s)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=bg_color)

    # --- Left page (orange) ---
    lx0, ly0, lx1, ly1 = int(10*s), int(18*s), int(44*s), int(78*s)
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=max(2, int(3*s)), fill=(249, 115, 22))

    # Panel lines on left page (only draw at larger sizes)
    if size >= 32:
        line_color = (26, 26, 46)
        lw = max(1, int(2 * s))
        lpad = int(4 * s)
        # horizontal lines
        for y_ref in [28, 36, 43]:
            y = int(y_ref * s)
            d.line([(lx0 + lpad, y), (lx1 - lpad, y)], fill=line_color, width=lw)
        # panel divider + two sub-panels (only at 48+)
        if size >= 48:
            div_y = int(52 * s)
            d.line([(lx0 + lpad, div_y), (lx1 - lpad, div_y)], fill=line_color, width=lw)
            p1x0, p1y0 = lx0 + lpad, int(55 * s)
            p1x1, p1y1 = lx0 + lpad + int(11 * s), int(73 * s)
            p2x0, p2y0 = lx0 + lpad + int(13 * s), int(55 * s)
            p2x1, p2y1 = lx1 - lpad, int(73 * s)
            d.rounded_rectangle([p1x0, p1y0, p1x1, p1y1], radius=max(1, int(2*s)), fill=(251, 146, 60))
            d.rounded_rectangle([p2x0, p2y0, p2x1, p2y1], radius=max(1, int(2*s)), fill=(253, 186, 116))

    # --- Spine ---
    sx0, sx1 = int(44 * s), int(52 * s)
    d.rounded_rectangle([sx0, int(18*s), sx1, int(78*s)], radius=max(1, int(2*s)), fill=(41, 41, 82))

    # --- Right page (blue) ---
    rx0, ry0, rx1, ry1 = int(52*s), int(18*s), int(86*s), int(78*s)
    d.rounded_rectangle([rx0, ry0, rx1, ry1], radius=max(1, int(3*s)), fill=(59, 130, 246))

    if size >= 32:
        rpad = int(4 * s)
        # image panel on right page
        panel_y1 = int(42 * s)
        d.rounded_rectangle(
            [rx0 + rpad, ry0 + rpad, rx1 - rpad, panel_y1],
            radius=max(1, int(2*s)),
            fill=(96, 165, 250)
        )
        if size >= 48:
            line_color2 = (30, 58, 138)
            lw = max(1, int(2 * s))
            for y_ref in [48, 55, 62]:
                y = int(y_ref * s)
                d.line([(rx0 + rpad, y), (rx1 - rpad, y)], fill=line_color2, width=lw)

    # --- Star accent (top-right) ---
    if size >= 24:
        star_cx = int(82 * s)
        star_cy = int(14 * s)
        r_out = max(3, int(7 * s))
        r_in = max(1, int(3 * s))
        draw_star(d, star_cx, star_cy, r_out, r_in, 5, (251, 191, 36))

    return img


def main():
    sizes = [16, 32, 48, 64, 128, 256]
    frames = [make_icon(sz) for sz in sizes]

    # Save PNG preview (256px)
    frames[-1].save("icon.png")
    print("Saved icon.png")

    # Save multi-size .ico
    frames[-1].save(
        "icon.ico",
        format="ICO",
        sizes=[(sz, sz) for sz in sizes],
        append_images=frames[:-1],
    )
    print("Saved icon.ico")


if __name__ == "__main__":
    main()
