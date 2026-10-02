import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from config import PROJECT_ROOT


ASSET_DIRECTORY = PROJECT_ROOT / "assets" / "images"
STYLE_PATH = PROJECT_ROOT / "assets" / "styles.css"


@st.cache_data(show_spinner=False)
def _read_styles(path: str, modified_ns: int) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


@st.cache_data(show_spinner=False)
def _optimized_image(path: str, max_width: int, max_height: int) -> bytes | None:
    try:
        with Image.open(path) as opened_image:
            image = opened_image.convert("RGB")
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            output = BytesIO()
            image.save(output, format="JPEG", quality=82, optimize=True)
            return output.getvalue()
    except (OSError, ValueError):
        return None


def apply_styles() -> None:
    try:
        modified_ns = STYLE_PATH.stat().st_mtime_ns
    except OSError:
        modified_ns = 0
    styles = _read_styles(str(STYLE_PATH), modified_ns)
    if styles:
        st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)


def local_image(filename: str, size: tuple[int, int] = (900, 560)) -> bytes | None:
    image_path = ASSET_DIRECTORY / filename
    if not image_path.is_file():
        return None
    return _optimized_image(str(image_path), size[0], size[1])


def hero_background() -> tuple[str, str]:
    image = local_image("hero.jpg", (1440, 720))
    if image is None:
        return "hero--placeholder", ""
    encoded = base64.b64encode(image).decode("ascii")
    background = (
        "background-image: linear-gradient(90deg, rgba(12, 35, 25, .9), "
        f"rgba(12, 35, 25, .18)), url(data:image/jpeg;base64,{encoded})"
    )
    return "hero--image", background


def render_navigation(current: str) -> str | None:
    with st.container(key="primary_navigation"):
        st.markdown(
            '<div class="brand-lockup"><span class="brand-mark">CR</span>'
            '<span>Crop Rescue</span></div>',
            unsafe_allow_html=True,
        )
        home, diagnose, history, library = st.columns(4)
        selected = None
        with home:
            if st.button(
                "Home",
                type="primary" if current == "home" else "secondary",
                use_container_width=True,
                key="nav_home",
            ):
                selected = "home"
        with diagnose:
            if st.button(
                "Diagnose",
                type="primary" if current in ("crops", "diagnose") else "secondary",
                use_container_width=True,
                key="nav_diagnose",
            ):
                selected = "crops" if not st.session_state.get("selected_crop") else "diagnose"
        with history:
            if st.button(
                "History",
                type="primary" if current == "history" else "secondary",
                use_container_width=True,
                key="nav_history",
            ):
                selected = "history"
        with library:
            if st.button(
                "Library",
                type="primary" if current == "library" else "secondary",
                use_container_width=True,
                key="nav_library",
            ):
                selected = "library"

    st.markdown('<div class="nav-rule"></div>', unsafe_allow_html=True)
    return selected