"""Poster Maker task plugin.

Creates downloadable social posters locally with Pillow. No paid image API is required.
"""

from io import BytesIO
import html
import math
import re
import textwrap

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

TASK_NAME = "Poster Maker"
TASK_ICON = "🖼️"

WIDGET_PREFIX = "poster_maker:"


def _font(size, bold=False):
    """Find a broadly available font, with a Pillow fallback."""
    candidates = []
    if bold:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ])
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


THEMES = {
    "Midnight blue": ((10, 22, 58), (29, 91, 160), (255, 255, 255), (100, 230, 255)),
    "Sunset orange": ((77, 24, 47), (231, 94, 49), (255, 250, 235), (255, 207, 95)),
    "Forest green": ((8, 54, 49), (24, 128, 93), (246, 255, 244), (190, 245, 144)),
    "Royal purple": ((39, 22, 79), (113, 57, 153), (255, 249, 255), (255, 195, 239)),
    "Clean white": ((245, 248, 255), (222, 233, 248), (24, 36, 62), (26, 103, 210)),
}


def _blend(start, end, amount):
    return tuple(round(start[i] + (end[i] - start[i]) * amount) for i in range(3))


def _make_gradient(size, top, bottom):
    width, height = size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        color = _blend(top, bottom, y / max(1, height - 1))
        draw.line((0, y, width, y), fill=color)
    return image


def _wrap_by_width(draw, text, font, max_width):
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    lines = []
    current = ""
    for word in words:
        if not word:
            continue
        candidate = word if not current else current + " " + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_title(draw, title, max_width, max_height):
    for size in range(92, 35, -2):
        font = _font(size, bold=True)
        lines = _wrap_by_width(draw, title, font, max_width)
        line_height = size * 1.16
        if len(lines) <= 4 and len(lines) * line_height <= max_height:
            return font, lines, int(line_height)
    font = _font(36, bold=True)
    return font, _wrap_by_width(draw, title, font, max_width)[:4], 43


def _render_poster(content, title, subtitle, theme_name, format_name, footer):
    width, height = (1080, 1350) if format_name == "Portrait (4:5)" else (1080, 1080)
    top, bottom, foreground, accent = THEMES[theme_name]
    image = _make_gradient((width, height), top, bottom)
    draw = ImageDraw.Draw(image, "RGB")

    # Decorative shapes, deliberately behind the text.
    draw.ellipse((width - 340, -150, width + 120, 310), fill=_blend(top, accent, 0.25))
    draw.ellipse((-210, height - 350, 230, height + 90), fill=_blend(bottom, accent, 0.18))
    draw.rounded_rectangle((58, 58, width - 58, height - 58), radius=34, outline=_blend(foreground, accent, 0.5), width=3)
    draw.rounded_rectangle((82, 84, 240, 96), radius=6, fill=accent)

    margin = 92
    max_text_width = width - 2 * margin
    title = (title or "").strip()
    if not title:
        first = re.split(r"[.!?\n]", content.strip(), maxsplit=1)[0].strip()
        title = first or "Your Big Idea"
        if len(title) > 78:
            title = title[:75].rsplit(" ", 1)[0] + "…"

    title_font, title_lines, title_line_height = _fit_title(
        draw, title, max_text_width, int(height * 0.32)
    )
    y = 140
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill=foreground)
        y += title_line_height

    if subtitle.strip():
        sub_font = _font(34, bold=False)
        sub_lines = _wrap_by_width(draw, subtitle.strip(), sub_font, max_text_width)
        for line in sub_lines[:3]:
            draw.text((margin, y + 12), line, font=sub_font, fill=accent)
            y += 43

    y += 26
    draw.rounded_rectangle((margin, y, margin + 116, y + 8), radius=4, fill=accent)
    y += 38

    body_font = _font(29, bold=False)
    body_lines = []
    for paragraph in content.strip().splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            body_lines.append("")
        else:
            body_lines.extend(_wrap_by_width(draw, paragraph, body_font, max_text_width))
    max_body_lines = max(5, int((height - y - 200) / 42))
    if len(body_lines) > max_body_lines:
        body_lines = body_lines[:max_body_lines]
        if body_lines:
            body_lines[-1] = body_lines[-1].rstrip(" .") + "…"
    for line in body_lines:
        if line:
            draw.text((margin, y), line, font=body_font, fill=foreground)
        y += 42

    # Bottom callout/footer area.
    footer_y = height - 164
    draw.rounded_rectangle((margin, footer_y, width - margin, footer_y + 2), radius=1, fill=_blend(foreground, accent, 0.45))
    if footer.strip():
        footer_font = _font(24, bold=True)
        footer_lines = _wrap_by_width(draw, footer.strip(), footer_font, max_text_width)
        for idx, line in enumerate(footer_lines[:2]):
            draw.text((margin, footer_y + 24 + idx * 31), line, font=footer_font, fill=accent)

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()



def _render_svg_poster(content, title, subtitle, theme_name, format_name, footer):
    """Create a real, scalable SVG poster that can be downloaded and edited."""
    width, height = (1080, 1350) if format_name == "Portrait (4:5)" else (1080, 1080)
    top, bottom, foreground, accent = THEMES[theme_name]
    rgb = lambda value: "#{:02x}{:02x}{:02x}".format(*value)
    top_hex, bottom_hex = rgb(top), rgb(bottom)
    fg_hex, accent_hex = rgb(foreground), rgb(accent)

    title = (title or "").strip()
    if not title:
        title = re.split(r"[.!?\n]", content.strip(), maxsplit=1)[0].strip() or "Your Big Idea"
        if len(title) > 78:
            title = title[:75].rsplit(" ", 1)[0] + "…"

    def wrap_words(value, limit):
        result, current = [], ""
        for word in re.sub(r"\s+", " ", value).strip().split():
            candidate = word if not current else current + " " + word
            if len(candidate) <= limit:
                current = candidate
            else:
                if current:
                    result.append(current)
                current = word
        if current:
            result.append(current)
        return result

    title_lines = wrap_words(title, 23)[:4]
    subtitle_lines = wrap_words(subtitle, 42)[:3] if subtitle.strip() else []
    body_lines = []
    for paragraph in content.strip().splitlines():
        if paragraph.strip():
            body_lines.extend(wrap_words(paragraph, 48))
        else:
            body_lines.append("")
    max_body = max(4, int((height - 570) / 42))
    if len(body_lines) > max_body:
        body_lines = body_lines[:max_body]
        body_lines[-1] = body_lines[-1].rstrip(" .") + "…"

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<title>Personal AI Agent poster</title>',
        '<defs><linearGradient id="background" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="' + top_hex + '"/><stop offset="100%" stop-color="' + bottom_hex + '"/></linearGradient>',
        '<radialGradient id="glow"><stop offset="0%" stop-color="' + accent_hex + '" stop-opacity=".65"/><stop offset="100%" stop-color="' + accent_hex + '" stop-opacity="0"/></radialGradient></defs>',
        '<rect width="100%" height="100%" fill="url(#background)"/>',
        f'<circle cx="{width-80}" cy="60" r="330" fill="url(#glow)"/>',
        f'<circle cx="35" cy="{height-50}" r="260" fill="url(#glow)" opacity=".55"/>',
        f'<rect x="58" y="58" width="{width-116}" height="{height-116}" rx="34" fill="none" stroke="{fg_hex}" stroke-opacity=".55" stroke-width="3"/>',
        f'<rect x="82" y="84" width="158" height="12" rx="6" fill="{accent_hex}"/>',
    ]
    y = 175
    for line in title_lines:
        elements.append(f'<text x="92" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="66" font-weight="800" fill="{fg_hex}">{html.escape(line)}</text>')
        y += 76
    for line in subtitle_lines:
        y += 5
        elements.append(f'<text x="92" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="32" fill="{accent_hex}">{html.escape(line)}</text>')
        y += 43
    y += 25
    elements.append(f'<rect x="92" y="{y}" width="116" height="8" rx="4" fill="{accent_hex}"/>')
    y += 55
    body_end = height - 200
    for line in body_lines:
        if y > body_end:
            break
        if line:
            elements.append(f'<text x="92" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="{fg_hex}">{html.escape(line)}</text>')
        y += 42
    footer_y = height - 164
    elements.append(f'<path d="M92 {footer_y} H{width-92}" stroke="{fg_hex}" stroke-opacity=".55" stroke-width="2"/>')
    if footer.strip():
        for idx, line in enumerate(wrap_words(footer.strip(), 55)[:2]):
            elements.append(f'<text x="92" y="{footer_y+42+idx*32}" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700" fill="{accent_hex}">{html.escape(line)}</text>')
    elements.append('</svg>')
    return "\n".join(elements).encode("utf-8")


def render():
    st.write("Turn text you give your agent—or a recent Chat message—into a downloadable poster.")
    st.caption("The poster is designed locally with typography, colour, and shapes. No paid image API is needed.")

    history = st.session_state.get("chat_history", [])
    candidates = []
    for index, item in enumerate(history):
        text_value = str(item.get("content", "")).strip()
        if text_value:
            role = "You" if item.get("role") == "user" else "Agent"
            candidates.append((f"{role}: {text_value[:90].replace(chr(10), ' ')}", text_value, index))
    source = st.radio(
        "Content source",
        ["Write or paste content", "Use a recent Chat message"],
        horizontal=True,
        key=WIDGET_PREFIX + "source",
    )

    default_content = ""
    if source == "Use a recent Chat message":
        if candidates:
            labels = [item[0] for item in reversed(candidates)]
            selected_label = st.selectbox(
                "Choose a Chat message",
                labels,
                key=WIDGET_PREFIX + "chat_choice",
            )
            selected = next(item for item in reversed(candidates) if item[0] == selected_label)
            default_content = selected[1]
        else:
            st.info("No chat messages are available yet. Send a message in Chat first, or switch to paste content.")
    content = st.text_area(
        "Poster content",
        value=default_content,
        height=180,
        max_chars=4000,
        placeholder="Paste your announcement, quote, song, product details, event, or other content here.",
        key=WIDGET_PREFIX + "content",
    )
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input(
            "Headline (optional)",
            placeholder="Leave blank to use the first line",
            max_chars=120,
            key=WIDGET_PREFIX + "title",
        )
        subtitle = st.text_input(
            "Subtitle (optional)",
            placeholder="A short supporting line",
            max_chars=180,
            key=WIDGET_PREFIX + "subtitle",
        )
    with col2:
        theme = st.selectbox(
            "Colour theme",
            list(THEMES.keys()),
            key=WIDGET_PREFIX + "theme",
        )
        format_name = st.selectbox(
            "Poster format",
            ["Portrait (4:5)", "Square (1:1)"],
            key=WIDGET_PREFIX + "format",
        )
    footer = st.text_input(
        "Footer / call to action (optional)",
        placeholder="Example: Register today · Contact us",
        max_chars=180,
        key=WIDGET_PREFIX + "footer",
    )

    if st.button("🖼️ Create poster", type="primary", use_container_width=True, key=WIDGET_PREFIX + "create"):
        if not content.strip():
            st.error("Add or select some content first.")
        else:
            try:
                with st.spinner("Designing your poster..."):
                    poster_bytes = _render_poster(
                        content.strip(), title, subtitle, theme, format_name, footer
                    )
                svg_bytes = _render_svg_poster(
                    content.strip(), title, subtitle, theme, format_name, footer
                )
                st.session_state[WIDGET_PREFIX + "image"] = poster_bytes
                st.session_state[WIDGET_PREFIX + "svg"] = svg_bytes
                st.session_state[WIDGET_PREFIX + "filename"] = "personal_agent_poster.png"
                st.success("Poster created. Download it as PNG or scalable SVG below.")
            except Exception as exc:
                st.error(f"Could not create the poster: {exc}")

    poster_bytes = st.session_state.get(WIDGET_PREFIX + "image")
    if poster_bytes:
        st.image(poster_bytes, caption="Your poster", use_container_width=True)
        st.download_button(
            "⬇️ Download poster (PNG)",
            data=poster_bytes,
            file_name=st.session_state.get(WIDGET_PREFIX + "filename", "personal_agent_poster.png"),
            mime="image/png",
            use_container_width=True,
            key=WIDGET_PREFIX + "download",
        )
        svg_bytes = st.session_state.get(WIDGET_PREFIX + "svg")
        if svg_bytes:
            st.download_button(
                "⬇️ Download editable vector poster (SVG)",
                data=svg_bytes,
                file_name="personal_agent_poster.svg",
                mime="image/svg+xml",
                use_container_width=True,
                key=WIDGET_PREFIX + "download_svg",
            )
            # Streamlit's code block includes a built-in Copy button.
            with st.expander("📋 Copy poster SVG code"):
                st.caption("Use the Copy icon on the code block to copy the complete vector poster source.")
                st.code(svg_bytes.decode("utf-8"), language="xml")
            with st.expander("📋 Copy poster text"):
                st.caption("Use the Copy icon on the code block to copy the text used for this poster.")
                st.code(content.strip(), language="text")
