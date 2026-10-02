# Crop Rescue

Crop Rescue is a local-first plant disease screening application for farmers. It combines a trained MobileNetV2 classifier with crop information and local scan history. A model result is a screening aid, not a confirmed agricultural diagnosis.

## Supported Crops

- Maize
- Potato
- Tomato
- Cassava
- Beans are shown as **Coming Soon** and are not sent to the model.

The supplied `plant_disease_model.h5` has 22 output classes. `class_names.json` is the authoritative output ordering; the application validates the model input and output against that file at diagnosis time. Do not reorder or recreate the class list.

## Farmer Flow

1. Choose a supported crop.
2. Take a photo or select one from the device.
3. Review photo-quality warnings and continue when ready.
4. View the model prediction, confidence status, explanation, and general action guidance.
5. Save scan details locally and optionally leave feedback.

The app does not store uploaded images in scan history, automatically retrain, or synchronize data to a server. Feedback remains in a local pending queue.

## Project Structure

```text
app.py                      Streamlit entry point and navigation
config.py                   Project paths and model configuration
services/model.py           Lazy cached model loading and shape checks
services/diagnosis.py       MobileNetV2 preprocessing and inference
services/image_quality.py   Lightweight Pillow/NumPy image checks
data/catalog.py             Crop and disease information
data/database.py            SQLite connection and schema
data/history.py             Local scan history
data/feedback.py            Local pending feedback
ui/layout.py                Cached local assets and shared navigation
ui/screens.py               Product screens and farmer-facing components
assets/styles.css           Responsive product styling
assets/images/              Optional local hero and crop photographs
data/crop_rescue.db         Created locally at runtime; not committed
```

## Local Images

Place optimized JPG files in `assets/images/` named `hero.jpg`, `maize.jpg`, `potato.jpg`, `tomato.jpg`, `cassava.jpg`, and `beans.jpg`. The interface uses designed placeholders for missing images and does not fetch external images at runtime. Image variants are resized and cached in memory. Uploads are limited to 12 MB and decoded images to 16 megapixels to keep memory use bounded.

## Setup

Use Python 3.13 and install the minimal dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. On native Windows, TensorFlow runs on CPU; no GPU is required. The model is loaded only after the user continues to diagnosis and is cached for later scans. No training data is loaded and no model is trained locally; training remains in Kaggle.

## Checks

Run the lightweight tests with:

```powershell
python -m unittest discover -s tests -v
```

The tests cover class ordering, model shape checks, preprocessing layout, prediction mapping, image checks, catalog coverage, and local history/feedback behavior. The model smoke test uses one synthetic image and does not assess model accuracy.

## Limitations

The model only knows its 22 trained classes. Poor lighting, blur, clutter, unseen diseases, or symptoms that resemble one another can affect a prediction. Photo-quality checks are simple heuristics, not scientific measurements. Confidence thresholds are interface rules, not validated accuracy boundaries. Confirm serious or rapidly spreading crop symptoms with local agricultural expertise.

No current validation metric is claimed here for the supplied 22-class model. Model evaluation and any future retraining should be performed in Kaggle, not on the 4 GB development computer.

## About

Crop Rescue began as a student project by Petra Nobuhle Mahwadu, a Year 2 Computer Science student at the University of Rwanda, exploring practical uses of AI in African agriculture.

## Disclaimer

Crop Rescue is an independent student project built for learning, experimentation, and portfolio purposes. It does not replace professional agricultural advice or laboratory-confirmed diagnosis.