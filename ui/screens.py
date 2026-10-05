from datetime import datetime
from typing import Any

import streamlit as st

from config import MAX_UPLOAD_SIZE_MB, SUPPORTED_CROPS
from data.catalog import DiseaseInfo, catalog_entries, crop_for_class
from data.feedback import FEEDBACK_RATINGS
from data.history import ScanRecord
from services.diagnosis import PredictionResult
from services.image_quality import inspect_image
from ui.layout import hero_background, local_image


CROP_PRESENTATION = {
    "Maize": ("🌽", "maize.jpg", "A staple crop grown across the region."),
    "Potato": ("🥔", "potato.jpg", "Check leaves for signs of stress."),
    "Tomato": ("🍅", "tomato.jpg", "Review visible leaf symptoms."),
    "Cassava": ("🌿", "cassava.jpg", "Check leaf patterns and new growth."),
    "Beans": ("🫘", "beans.jpg", "Disease support is being prepared."),
}


def render_home() -> bool:
    hero_class, background_style = hero_background()
    inline_style = f' style="{background_style}"' if background_style else ""

    st.markdown(
        f'<section class="hero {hero_class}"{inline_style}>'
        '<p class="eyebrow">FIELD NOTES, MADE PRACTICAL</p>'
        '<h1>Better decisions<br>start with a closer look.</h1>'
        '<p class="hero-copy">Check a crop leaf, understand what the model sees, '
        'and find a grounded next step for your field.</p>'
        '<div class="hero-meta"><span class="status-dot"></span> '
        'Local AI model · No cloud diagnosis</div></section>',
        unsafe_allow_html=True,
    )
    started = st.button(
        "Start diagnosis",
        type="primary",
        use_container_width=True,
        key="home_start_diagnosis",
    )

    st.markdown(
        '<div class="section-heading"><div><p class="eyebrow">A FIELD TOOL, '
        'NOT A FINAL VERDICT</p><h2>From leaf photo to useful next step</h2></div>'
        '<p>Designed to help you observe and decide what to check next.</p></div>'
        '<div class="feature-grid">'
        '<article class="feature-item"><span class="feature-index">01</span>'
        '<h3>Check the photo</h3><p>Get a simple warning if the image is dark, '
        'blurry, or too small.</p></article>'
        '<article class="feature-item"><span class="feature-index">02</span>'
        '<h3>See the model result</h3><p>Review a prediction and its confidence '
        'without treating it as certainty.</p></article>'
        '<article class="feature-item"><span class="feature-index">03</span>'
        '<h3>Choose a next step</h3><p>Use crop information as general guidance '
        'and confirm serious concerns locally.</p></article></div>',
        unsafe_allow_html=True,
    )
    return started


def render_crop_selection() -> str | None:
    st.markdown('<p class="eyebrow">NEW SCAN</p><h1 class="page-title">Which crop are you checking?</h1>', unsafe_allow_html=True)
    st.write("Choose the crop shown in your photo. Beans diagnosis is not available yet.")

    selection = None
    crop_names = (*SUPPORTED_CROPS, "Beans")
    for row_start in range(0, len(crop_names), 2):
        columns = st.columns(2)
        for column, crop in zip(columns, crop_names[row_start:row_start + 2]):
            icon, image_name, description = CROP_PRESENTATION[crop]
            with column:
                with st.container(border=True):
                    image = local_image(image_name)
                    if image:
                        st.image(image, use_container_width=True)
                    else:
                        st.markdown(
                            f'<div class="crop-placeholder"><span>{icon}</span>'
                            '<small>Crop image</small></div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown(f'<h3 class="crop-title">{crop}</h3>', unsafe_allow_html=True)
                    st.caption(description)
                    if crop == "Beans":
                        st.button(
                            "Coming Soon",
                            disabled=True,
                            use_container_width=True,
                            key="crop_beans_coming_soon",
                        )
                    elif st.button(
                        f"Choose {crop}",
                        type="primary",
                        use_container_width=True,
                        key=f"crop_{crop.lower()}",
                    ):
                        selection = crop

    if st.button("Back to home", key="crop_back_home"):
        return "__home__"
    return selection


def render_capture(crop: str, revision: int) -> tuple[str | None, Any | None]:
    icon = CROP_PRESENTATION[crop][0]
    st.markdown(
        f'<p class="eyebrow">{icon} {crop.upper()} SCAN</p>'
        '<h1 class="page-title">Add a clear leaf photo</h1>',
        unsafe_allow_html=True,
    )
    source = st.radio(
        "Photo source",
        ("Take a photo", "Choose from gallery"),
        horizontal=True,
        label_visibility="collapsed",
        key=f"photo_source_{revision}",
    )

    if source == "Take a photo":
        uploaded_file = st.camera_input(
            "Frame the affected leaf",
            key=f"camera_capture_{revision}",
        )
        if uploaded_file is None:
            st.caption("Allow camera access when prompted, or choose a photo from your device.")
    else:
        uploaded_file = st.file_uploader(
            "Choose a leaf photo",
            type=("jpg", "jpeg", "png", "jfif"),
            key=f"gallery_upload_{revision}",
            max_upload_size=MAX_UPLOAD_SIZE_MB,
        )

    if uploaded_file is None:
        if st.button("Choose a different crop", key=f"back_to_crops_{revision}"):
            return "crops", None
        return None, None

    image_check = inspect_image(uploaded_file.getvalue())
    if not image_check.is_valid:
        for message in image_check.errors:
            st.error(message)
        return None, None

    st.markdown('<div class="photo-preview-heading">Photo preview</div>', unsafe_allow_html=True)
    st.image(image_check.image, caption=f"Selected crop: {crop}", use_container_width=True)
    for message in image_check.warnings:
        st.warning(message)

    action_col, change_col = st.columns([2, 1])
    with action_col:
        continue_scan = st.button(
            "Continue to diagnosis",
            type="primary",
            use_container_width=True,
            key=f"continue_diagnosis_{revision}",
        )
    with change_col:
        change_photo = st.button(
            "Change photo",
            use_container_width=True,
            key=f"change_photo_{revision}",
        )

    if change_photo:
        return "change_photo", None
    if continue_scan:
        return "diagnose", image_check.image
    return None, None


def crop_for_prediction(class_name: str) -> str | None:
    return crop_for_class(class_name)


def _result_title(status: str, disease_label: str) -> str:
    if status == "high":
        return f"Likely {disease_label}"
    if status == "moderate":
        return f"Possible {disease_label}"
    return "Unable to confidently identify the problem"


def _result_message(status: str, disease_label: str) -> str:
    if status == "high":
        return (
            f"This model suggests a likely {disease_label.lower()} pattern. "
            "It is a field-use alert, not a confirmed diagnosis."
        )
    if status == "moderate":
        return (
            f"Possible {disease_label.lower()}. Similar symptoms can occur with other crop "
            "conditions, so a second clear photo or local field check is valuable."
        )
    return (
        "The model is not confident enough to identify a specific problem. "
        "Retake the photo, improve the lighting, and inspect several leaves before acting."
    )


def _field_context_message(
    weather: str,
    soil: str,
    timing: str,
    spread: str,
    result: PredictionResult,
) -> str:
    if weather == "Very rainy" or soil == "Very wet":
        if result.confidence_status == "low":
            return (
                "Recent wet conditions may be increasing crop stress. The current image model "
                "cannot confirm water stress from a photo alone; check soil moisture and inspect nearby plants."
            )
        return (
            "Possible disease detected. Recent heavy or wet conditions may increase the risk of some crop problems. "
            "Inspect nearby plants and monitor whether symptoms are spreading."
        )
    if weather == "Very dry" or soil == "Very dry":
        if result.confidence_status == "low":
            return (
                "Your crop may be experiencing stress. The current AI model cannot confirm water stress from a photo alone. "
                "Check soil moisture and inspect several plants."
            )
        return (
            "Dry conditions may be contributing to stress symptoms. Keep an eye on the plant and compare with nearby healthy plants."
        )
    if spread in {"Several leaves", "Most of the plant", "Several plants"}:
        return (
            "Symptoms appear to be spreading beyond a single leaf. Inspect nearby plants and monitor whether the pattern is expanding."
        )
    if timing == "More than a week ago":
        return (
            "This has been present for more than a week, so comparison with nearby plants and local field checks is important."
        )
    return ""


def render_result(
    result: PredictionResult,
    selected_crop: str,
    disease_info: DiseaseInfo | None,
    crop_mismatch: bool = False,
) -> bool:
    predicted_crop = crop_for_prediction(result.class_name)
    disease_label = (
        disease_info.disease
        if disease_info
        else result.class_name.split("___", 1)[-1].replace("_", " ")
    )
    title = _result_title(result.confidence_status, disease_label)
    summary = _result_message(result.confidence_status, disease_label)

    st.markdown('<p class="eyebrow">FIELD ASSESSMENT</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="page-title">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-crop">Selected crop: {selected_crop}</p>', unsafe_allow_html=True)

    if result.confidence_status == "high":
        badge_label = "Likely"
    elif result.confidence_status == "moderate":
        badge_label = "Possible"
    else:
        badge_label = "Uncertain"
    st.markdown(
        f'<div class="confidence-badge confidence-{result.confidence_status}">'
        f'{badge_label}</div>',
        unsafe_allow_html=True,
    )
    st.progress(min(max(result.confidence, 0.0), 1.0), text=f"Model confidence · {result.confidence:.1%}")
    st.write(summary)

    if crop_mismatch:
        st.error(
            f"The image does not match the selected crop. You chose {selected_crop}, but the model's top class is for "
            f"{predicted_crop or 'another crop'}. Please check the crop selection or retake the photo."
        )
    elif predicted_crop and predicted_crop != selected_crop:
        st.warning(
            f"You selected {selected_crop}, but the model's top class is for {predicted_crop}. "
            "Check that the crop selection and photo are correct."
        )

    st.markdown(
        '<div class="result-section"><p class="eyebrow">AGRICULTURAL INFORMATION</p>'
        '<h2>What this may mean</h2></div>',
        unsafe_allow_html=True,
    )
    if disease_info:
        st.markdown("**What to look for**")
        st.write(disease_info.symptoms)
        st.markdown("**Explanation**")
        st.write(disease_info.explanation)
        if disease_info.note:
            st.info(disease_info.note)
    else:
        st.write(
            "No catalog entry is available for this model class. Confirm the result with a local agricultural professional."
        )

    with st.expander("Field context check", expanded=True):
        weather = st.selectbox("What has the weather been like recently?", ("Very rainy", "Normal", "Very dry"), key="weather_context")
        soil = st.selectbox("How is the soil around the plant?", ("Very wet", "Normal", "Very dry", "Not sure"), key="soil_context")
        timing = st.selectbox("When did you first notice the problem?", ("Today", "A few days ago", "More than a week ago"), key="timing_context")
        spread = st.selectbox("How widespread is the problem?", ("One/few leaves", "Several leaves", "Most of the plant", "Several plants"), key="spread_context")
        context_message = _field_context_message(weather, soil, timing, spread, result)
        if context_message:
            st.info(context_message)
        else:
            st.caption("Context is noted for review. Use this as guidance, not as a trained prediction.")

    st.markdown('<h3 class="subsection-title">What to do now</h3>', unsafe_allow_html=True)
    if disease_info:
        for step_number, step in enumerate(disease_info.next_steps, start=1):
            st.write(f"{step_number}. {step}")
        st.markdown('<h3 class="subsection-title">Prevention</h3>', unsafe_allow_html=True)
        st.write(disease_info.prevention)
    else:
        st.write("Monitor nearby plants and seek local agricultural guidance.")
    st.caption(
        "The AI prediction is not a confirmed diagnosis. Agricultural information is general guidance, not a treatment prescription."
    )

    if result.top_predictions and len(result.top_predictions) > 1:
        st.markdown('<h3 class="subsection-title">Model comparison</h3>', unsafe_allow_html=True)
        for item in result.top_predictions[1:]:
            name = item.class_name.split("___", 1)[-1].replace("_", " ")
            st.write(f"{name} · {item.confidence:.1%}")

    return st.button("Scan another leaf", type="primary", use_container_width=True, key="scan_another_leaf")


def render_history(records: tuple[ScanRecord, ...]) -> None:
    st.markdown('<p class="eyebrow">ON THIS DEVICE</p><h1 class="page-title">Scan history</h1>', unsafe_allow_html=True)
    st.caption("Only scan details are saved. Uploaded photos are not stored in history.")
    if not records:
        st.markdown(
            '<div class="empty-state"><span class="empty-mark">CR</span>'
            '<h2>No scans saved yet</h2><p>Your completed diagnoses will appear here.</p></div>',
            unsafe_allow_html=True,
        )
        return

    for record in records:
        try:
            scanned_at = datetime.fromisoformat(record.scanned_at).astimezone().strftime(
                "%d %b %Y · %H:%M"
            )
        except ValueError:
            scanned_at = record.scanned_at
        disease = record.class_name.split("___", 1)[-1].replace("_", " ")
        with st.container(border=True):
            crop_column, result_column, confidence_column = st.columns([1, 2, 1])
            crop_column.markdown(f"**{record.crop}**")
            result_column.markdown(f"**{disease}**")
            result_column.caption(scanned_at)
            confidence_column.metric("Confidence", f"{record.confidence:.1%}")
            st.caption(f"{record.confidence_status.title()} confidence · Local prediction")


def render_library(class_names: tuple[str, ...]) -> None:
    st.markdown('<p class="eyebrow">CROP KNOWLEDGE</p><h1 class="page-title">Disease library</h1>', unsafe_allow_html=True)
    st.write("Browse information for the classes currently supported by the local model.")
    crop = st.selectbox("Choose a crop", (*SUPPORTED_CROPS, "Beans"), key="library_crop")
    if crop == "Beans":
        st.info("Beans diagnosis and disease information are coming soon. No bean predictions are produced by this model.")
        return

    entries = catalog_entries(class_names, crop)
    if not entries:
        st.info("No model classes are available for this crop.")
        return

    for class_name, info in entries:
        if info is None:
            st.warning("A class in the model mapping has no disease-library information yet.")
            continue
        with st.expander(info.disease):
            st.markdown("**What to look for**")
            st.write(info.symptoms)
            st.markdown("**What it may mean**")
            st.write(info.explanation)
            st.markdown("**What to do now**")
            for step_number, step in enumerate(info.next_steps, start=1):
                st.write(f"{step_number}. {step}")
            st.markdown("**Prevention**")
            st.write(info.prevention)
            if info.note:
                st.caption(info.note)


def render_feedback_form(
    scan_id: str,
    already_submitted: bool,
) -> tuple[str, str] | None:
    st.markdown('<div class="result-section"><p class="eyebrow">YOUR EXPERIENCE</p><h2>Was this diagnosis helpful?</h2></div>', unsafe_allow_html=True)
    if already_submitted:
        st.success("Feedback saved on this device · Pending")
        return None

    rating = st.radio(
        "Was this diagnosis helpful?",
        FEEDBACK_RATINGS,
        horizontal=True,
        key=f"feedback_rating_{scan_id}",
    )
    note = ""
    if rating == "Not helpful":
        note = st.text_area(
            "What seemed wrong? (optional)",
            max_chars=1000,
            key=f"feedback_note_{scan_id}",
        )
    submitted = st.button(
        "Send feedback",
        use_container_width=True,
        key=f"send_feedback_{scan_id}",
    )

    if submitted:
        return rating, note
    return None