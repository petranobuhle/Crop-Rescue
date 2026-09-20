import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Crop Rescue",
    page_icon="🌱",
    layout="wide"
)

# ---------- CUSTOM STYLING ----------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(20, 40, 20, 0.85), rgba(20, 40, 20, 0.85)),
                    url("https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-attachment: fixed;
    }
    .result-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 12px;
        margin-top: 15px;
    }
    h1, h2, h3 {
        color: #f0fff0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- LOAD MODEL ----------
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('plant_disease_model.h5')

model = load_model()

class_names = ['Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
               'Corn_(maize)___Common_rust_',
               'Corn_(maize)___Northern_Leaf_Blight',
               'Corn_(maize)___healthy',
               'Potato___Early_blight',
               'Potato___Late_blight',
               'Potato___healthy',
               'Tomato___Bacterial_spot',
               'Tomato___Early_blight',
               'Tomato___Late_blight',
               'Tomato___Leaf_Mold',
               'Tomato___Septoria_leaf_spot',
               'Tomato___Spider_mites Two-spotted_spider_mite',
               'Tomato___Target_Spot',
               'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
               'Tomato___Tomato_mosaic_virus',
               'Tomato___healthy']

# ---------- DISEASE INFO (description + treatment tip) ----------
disease_info = {
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': ("A fungal disease causing grayish lesions on leaves, reducing yield.", "Rotate crops, use resistant hybrids, and apply fungicide if severe."),
    'Corn_(maize)___Common_rust_': ("Small reddish-brown pustules appear on leaves.", "Plant resistant varieties; fungicides help in severe outbreaks."),
    'Corn_(maize)___Northern_Leaf_Blight': ("Long grayish-green lesions form on leaves, reducing photosynthesis.", "Use resistant hybrids and rotate crops each season."),
    'Corn_(maize)___healthy': ("No disease detected.", "Continue regular monitoring and good field hygiene."),
    'Potato___Early_blight': ("Dark concentric spots on older leaves, caused by a fungus.", "Remove infected leaves, avoid overhead watering, apply fungicide."),
    'Potato___Late_blight': ("A fast-spreading fungal disease causing dark, water-soaked lesions.", "Destroy infected plants promptly and apply fungicide preventively."),
    'Potato___healthy': ("No disease detected.", "Maintain proper spacing and soil drainage."),
    'Tomato___Bacterial_spot': ("Small, dark, water-soaked spots on leaves and fruit.", "Use disease-free seeds, avoid overhead watering, apply copper-based sprays."),
    'Tomato___Early_blight': ("Dark spots with concentric rings, usually on older leaves.", "Remove affected leaves, rotate crops, apply fungicide."),
    'Tomato___Late_blight': ("Water-soaked lesions that spread quickly in humid weather.", "Remove infected plants immediately, improve airflow, use fungicide."),
    'Tomato___Leaf_Mold': ("Yellow patches on top of leaves, mold underneath.", "Improve ventilation and reduce humidity around plants."),
    'Tomato___Septoria_leaf_spot': ("Small circular spots with dark borders on leaves.", "Remove infected leaves and avoid wetting foliage when watering."),
    'Tomato___Spider_mites Two-spotted_spider_mite': ("Tiny pests causing yellow speckling and leaf damage.", "Use insecticidal soap or introduce natural predators like ladybugs."),
    'Tomato___Target_Spot': ("Brown lesions with concentric rings, similar to early blight.", "Remove affected foliage and apply appropriate fungicide."),
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': ("A viral disease spread by whiteflies, causing curled yellow leaves.", "Control whitefly populations and remove infected plants."),
    'Tomato___Tomato_mosaic_virus': ("Causes mottled, discolored leaves and stunted growth.", "Remove infected plants; disinfect tools between uses."),
    'Tomato___healthy': ("No disease detected.", "Continue good watering and spacing practices.")
}

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("🌱 Crop Rescue")
    st.write(
        "An AI-powered tool that helps identify diseases in **tomato, potato, and maize** "
        "crops from a simple leaf photo."
    )
    st.write("**Model:** MobileNetV2 (transfer learning)")
    st.write("**Classes covered:** 17 disease/healthy categories")
    st.write("**Validation accuracy:** ~81%")
    st.markdown("---")
    st.write("Built by Petra Nobuhle Mahwadu as a student portfolio project.")
    st.write("[View on GitHub](https://github.com/petranouhle/crop-rescue)")

# ---------- MAIN PAGE ----------
st.title("🌱 Crop Rescue")
st.write("Upload a photo of a tomato, potato, or maize leaf to check for disease and get care recommendations.")

uploaded_file = st.file_uploader("Choose a leaf photo", type=["jpg", "jpeg", "png", "jfif"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])

    image = Image.open(uploaded_file).convert('RGB')
    with col1:
        st.image(image, caption="Uploaded photo", use_container_width=True)

    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions)]
    confidence = np.max(predictions) * 100
    description, treatment = disease_info[predicted_class]

    with col2:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader(predicted_class.replace('_', ' ').replace('  ', ' '))
        st.progress(int(confidence))
        st.write(f"**Confidence:** {confidence:.2f}%")
        st.write(f"**About:** {description}")
        st.write(f"**Recommended action:** {treatment}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.caption("⚠️ This is a student prototype. Results should not replace professional agricultural advice.")
    