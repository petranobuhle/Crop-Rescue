import logging
import sqlite3

import streamlit as st

from config import ConfigurationError, SUPPORTED_CROPS, load_class_names
from data.catalog import disease_info_for
from data.database import initialize_database
from data.feedback import save_feedback
from data.history import recent_scans, save_scan
from services.diagnosis import predict_image
from services.model import ModelLoadError, load_model
from ui.layout import apply_styles, render_navigation
from ui.screens import (
    render_capture,
    render_crop_selection,
    render_feedback_form,
    render_history,
    render_home,
    render_library,
    render_result,
)


logger = logging.getLogger(__name__)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Crop Rescue",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# PRODUCT STYLING
# ============================================================

apply_styles()


# ============================================================
# LOAD CLASS NAMES
# ============================================================

try:
    class_names = load_class_names()
except ConfigurationError as exc:
    st.error(f"Crop Rescue configuration issue: {exc}")
    st.stop()

try:
    initialize_database()
    storage_error = None
except (OSError, sqlite3.Error):
    logger.exception("Crop Rescue local database initialization failed")
    storage_error = "Local history and feedback are unavailable right now."


# ============================================================
# SESSION STATE AND NAVIGATION
# ============================================================

for key, initial in (
    ("view", "home"),
    ("selected_crop", None),
    ("photo_revision", 0),
    ("diagnosis_result", None),
    ("diagnosis_crop", None),
    ("scan_id", None),
    ("feedback_saved", False),
    ("scan_storage_warning", None),
):
    st.session_state.setdefault(key, initial)

navigation = render_navigation(st.session_state.view)
if navigation:
    st.session_state.view = navigation

if st.session_state.view == "home":
    if render_home():
        st.session_state.view = "crops"
        st.rerun()

elif st.session_state.view == "crops":
    selected_crop = render_crop_selection()
    if selected_crop == "__home__":
        st.session_state.view = "home"
        st.rerun()
    elif selected_crop:
        st.session_state.selected_crop = selected_crop
        st.session_state.diagnosis_result = None
        st.session_state.view = "diagnose"
        st.rerun()

elif st.session_state.view == "diagnose":
    selected_crop = st.session_state.selected_crop
    if selected_crop not in SUPPORTED_CROPS:
        st.session_state.view = "crops"
        st.rerun()

    if st.session_state.diagnosis_result is not None:
        scan_again = render_result(
            st.session_state.diagnosis_result,
            st.session_state.diagnosis_crop,
            disease_info_for(st.session_state.diagnosis_result.class_name),
        )
        if storage_error or st.session_state.scan_storage_warning:
            st.warning(storage_error or st.session_state.scan_storage_warning)
        elif st.session_state.scan_id:
            feedback = render_feedback_form(
                st.session_state.scan_id,
                st.session_state.feedback_saved,
            )
            if feedback:
                try:
                    save_feedback(
                        st.session_state.scan_id,
                        feedback[0],
                        feedback[1],
                    )
                    st.session_state.feedback_saved = True
                    st.rerun()
                except (OSError, sqlite3.Error, ValueError):
                    logger.exception("Crop Rescue feedback could not be saved")
                    st.error("Feedback could not be saved locally. Please try again.")
        if scan_again:
            st.session_state.diagnosis_result = None
            st.session_state.scan_id = None
            st.session_state.feedback_saved = False
            st.session_state.scan_storage_warning = None
            st.session_state.photo_revision += 1
            st.rerun()
    else:
        action, image = render_capture(
            selected_crop,
            st.session_state.photo_revision,
        )
        if action == "crops":
            st.session_state.view = "crops"
            st.rerun()
        elif action == "change_photo":
            st.session_state.photo_revision += 1
            st.rerun()
        elif action == "diagnose" and image is not None:
            try:
                with st.spinner("Analyzing your leaf..."):
                    model = load_model()
                    result = predict_image(model, image, class_names)
                st.session_state.diagnosis_result = result
                st.session_state.diagnosis_crop = selected_crop
                st.session_state.scan_id = None
                st.session_state.feedback_saved = False
                st.session_state.scan_storage_warning = None
                if not storage_error:
                    try:
                        scan = save_scan(
                            selected_crop,
                            result.class_name,
                            result.confidence,
                            result.confidence_status,
                        )
                        st.session_state.scan_id = scan.scan_id
                    except (OSError, sqlite3.Error):
                        logger.exception("Crop Rescue scan history could not be saved")
                        st.session_state.scan_storage_warning = (
                            "This diagnosis is ready, but its history entry could "
                            "not be saved on this device."
                        )
                st.rerun()
            except (ModelLoadError, ConfigurationError) as exc:
                st.error(f"Diagnosis is unavailable: {exc}")
            except Exception:
                logger.exception("Crop Rescue diagnosis failed")
                st.error(
                    "The photo could not be analyzed. Please try another image "
                    "or contact support if the problem continues."
                )

elif st.session_state.view == "history":
    if storage_error:
        st.error(storage_error)
    else:
        try:
            render_history(recent_scans())
        except (OSError, sqlite3.Error):
            logger.exception("Crop Rescue history could not be loaded")
            st.error("Scan history could not be opened. Your diagnosis service is still available.")

elif st.session_state.view == "library":
    render_library(class_names)
