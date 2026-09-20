#  Crop Rescue

## Crop Disease Detection

Crop Rescue is a tool I'm building to help identify plant diseases from a simple photo of a leaf. Right now it covers three crops — tomato, potato, and maize — and uses a machine learning model I trained to recognize 17 different disease and healthy leaf categories.

The idea came from wanting to work on something that actually matters in an African context. A lot of smallholder farmers don't have easy access to agricultural extension officers, and by the time a disease is visibly spreading, it's often too late to do much about it. Crop Rescue is my attempt at putting a basic diagnostic tool in anyone's hands, using just a smartphone photo.

This is a student project and a work in progress, not a finished product. I built it as part of my Computer Science studies and as a portfolio piece, but I'm continuing to improve it.

---

## The Problem

Crop diseases can spread quickly and cause real damage to yield and income if they aren't caught early. For a lot of farmers, getting a proper diagnosis in time isn't easy — expert help isn't always nearby, and a leaf with early symptoms can look confusingly similar across different diseases.

I wanted to explore whether a trained AI model could offer a first-line diagnosis that's fast, free, and accessible from a phone.

---

## What It Does Right Now

The current version is a working prototype built with Streamlit. A user can:

- Upload a photo of a tomato, potato, or maize leaf
- Have that photo run through my trained TensorFlow model
- See the predicted disease (or "healthy") result
- See the model's confidence score
- Get a short description of the disease and a basic treatment suggestion

## How It Works
Leaf photo uploaded
↓
Image gets resized and processed
↓
Trained TensorFlow model analyzes it
↓
Model predicts the disease class
↓
Result + confidence score + treatment tip displayed


## How I Built It

I used the PlantVillage dataset, filtered down to just the classes for tomato, potato, and maize (17 categories total, about 24,000 images). Rather than training a model from scratch, I used transfer learning with MobileNetV2 — a model already pretrained on millions of general images — and just trained new layers on top to recognize these specific plant diseases. I did the actual training on Kaggle Notebooks since it gives free GPU access, which made a real difference given my own laptop's limited specs.

Once the model was trained, I saved it and built a Streamlit app around it so anyone could upload a photo and get a result without needing to touch any code.

**Tech stack:**
- Python
- TensorFlow / Keras (MobileNetV2, transfer learning)
- NumPy
- Pillow (PIL) for image handling
- Streamlit for the web interface
- Kaggle Notebooks for training
- Git & GitHub for version control

## Results

My current model reaches about **81% validation accuracy** across the 17 classes. I think that's a solid first result for a project built in a few weeks, though there's definitely room to improve — especially for diseases that look visually similar to each other.

## Running It Yourself

1. Clone this repo:
git clone https://github.com/petranobuhle/crop-rescue.git
2. Move into the project folder:
cd crop-rescue
3. Install what you need:
pip install tensorflow streamlit numpy pillow
4. Run the app:
python -m streamlit run app.py
5. It should open automatically in your browser at `localhost:8501`.

## Limitations (being upfront about this)

This is a student prototype, not a certified agricultural diagnostic tool. The prediction can be thrown off by things like poor lighting, cluttered backgrounds, unusual leaf angles, or diseases that look visually similar to each other. It also only knows what it was trained on — a disease outside my 17 categories won't be recognized correctly. I don't want anyone making serious farming decisions based on this alone; it's meant to explore what's possible, not replace real agricultural expertise.

## Where I Want to Take This

Right now this is just a working prototype. Things I'm hoping to add as I keep developing it:

- More detailed disease info — symptoms, causes, prevention, not just a one-line tip
- Support for more crops beyond the current three
- A severity/recovery outlook per disease, not just a static tip
- Better evaluation of the model itself (confusion matrix, precision/recall per class, not just overall accuracy)
- Possibly moving beyond Streamlit into a more complete app if the project grows

## About Me

I'm Petra Nobuhle Mahwadu, a Year 2 Computer Science student at the University of Rwanda. I'm interested in AI, machine learning, and how technology can address real problems in African agriculture and health. Crop Rescue is part of both my portfolio and my own learning process — through building it I've gotten hands-on practice with TensorFlow, image classification, model training and deployment, and building a real (if small) end-to-end application.

## Disclaimer

Crop Rescue is an independent student project built for learning, experimentation, and portfolio purposes. It does not replace professional agricultural advice or laboratory-confirmed diagnosis.