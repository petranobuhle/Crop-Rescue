from dataclasses import dataclass

from config import CROP_CLASS_PREFIXES


@dataclass(frozen=True)
class DiseaseInfo:
    crop: str
    disease: str
    symptoms: str
    explanation: str
    next_steps: tuple[str, ...]
    prevention: str
    note: str = ""


def _entry(
    crop: str,
    disease: str,
    symptoms: str,
    explanation: str,
    next_steps: tuple[str, ...],
    prevention: str,
    note: str = "",
) -> DiseaseInfo:
    return DiseaseInfo(crop, disease, symptoms, explanation, next_steps, prevention, note)


DISEASE_CATALOG: dict[str, DiseaseInfo] = {
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": _entry(
        "Maize", "Gray leaf spot",
        "Long gray or tan lesions may develop between leaf veins.",
        "Gray leaf spot is a fungal leaf disease that can reduce the green leaf area.",
        ("Inspect nearby leaves for similar lesions.", "Monitor whether lesions are spreading and seek local crop advice if they are."),
        "Use locally recommended resistant varieties and crop rotation where practical.",
    ),
    "Corn_(maize)___Common_rust_": _entry(
        "Maize", "Common rust",
        "Small raised reddish-brown pustules can appear on leaf surfaces.",
        "Common rust is a fungal disease; its impact varies with crop stage and conditions.",
        ("Check several plants for rust pustules.", "Ask a local extension worker about management if symptoms are widespread."),
        "Plant adapted varieties and monitor fields regularly.",
    ),
    "Corn_(maize)___Northern_Leaf_Blight": _entry(
        "Maize", "Northern leaf blight",
        "Elongated gray-green or tan lesions may run along the leaf.",
        "Northern leaf blight is a fungal disease affecting maize foliage.",
        ("Inspect upper and lower leaves on nearby plants.", "Monitor spread and use local agricultural guidance for severe symptoms."),
        "Use locally recommended resistant varieties and rotate crops where possible.",
    ),
    "Corn_(maize)___healthy": _entry(
        "Maize", "Healthy leaf pattern",
        "The model did not detect one of its trained disease patterns in this image.",
        "This is a model prediction, not proof that the plant is disease-free.",
        ("Continue routine field scouting.", "Check new growth and nearby plants for changes."),
        "Use healthy seed and follow locally recommended field hygiene.",
    ),
    "Potato___Early_blight": _entry(
        "Potato", "Early blight",
        "Dark leaf spots may develop concentric rings, often on older leaves.",
        "Early blight is commonly associated with a fungal leaf disease and can progress in favorable conditions.",
        ("Inspect older and nearby leaves for similar spots.", "Remove badly affected material where appropriate and ask local advisers about management."),
        "Rotate crops where practical and avoid leaving infected plant debris in the field.",
    ),
    "Potato___Late_blight": _entry(
        "Potato", "Late blight",
        "Dark, water-soaked-looking areas may spread quickly; pale growth can appear in humid conditions.",
        "Late blight can spread rapidly and warrants prompt local assessment.",
        ("Check nearby plants and stems for spreading symptoms.", "Contact a local agricultural adviser promptly if late blight is suspected."),
        "Use healthy planting material and follow local disease alerts and crop guidance.",
        "This model result is not a confirmed diagnosis; confirm urgent concerns locally.",
    ),
    "Potato___healthy": _entry(
        "Potato", "Healthy leaf pattern",
        "The model did not detect one of its trained disease patterns in this image.",
        "This is a model prediction, not proof that the plant is disease-free.",
        ("Continue routine crop checks.", "Watch new leaves and neighboring plants for changes."),
        "Use healthy seed tubers and follow locally recommended crop rotation.",
    ),
    "Tomato___Bacterial_spot": _entry(
        "Tomato", "Bacterial spot",
        "Small dark spots may appear on leaves, stems, or fruit; leaf spots can have pale centers.",
        "Bacterial spot is a plant disease that can affect tomato foliage and fruit.",
        ("Inspect leaves and fruit on nearby plants.", "Avoid handling wet plants and seek local guidance if symptoms spread."),
        "Use clean planting material and reduce unnecessary leaf wetness.",
    ),
    "Tomato___Early_blight": _entry(
        "Tomato", "Early blight",
        "Dark spots with concentric rings may form, often on older leaves.",
        "Early blight is commonly associated with a fungal leaf disease.",
        ("Check older leaves and nearby plants.", "Remove severely affected leaves when practical and monitor for spread."),
        "Maintain airflow and avoid carrying infected plant debris between crops.",
    ),
    "Tomato___Late_blight": _entry(
        "Tomato", "Late blight",
        "Irregular water-soaked-looking patches may darken and spread in humid conditions.",
        "Late blight can spread rapidly and should be assessed promptly when suspected.",
        ("Inspect neighboring plants and stems for similar symptoms.", "Seek local agricultural advice promptly if symptoms are spreading."),
        "Use healthy planting material and follow local disease alerts and crop guidance.",
        "Confirm this result locally before taking urgent crop-management decisions.",
    ),
    "Tomato___Leaf_Mold": _entry(
        "Tomato", "Leaf mold",
        "Pale yellow areas may appear on upper leaf surfaces, with olive growth underneath in humid conditions.",
        "Leaf mold is associated with fungal growth favored by humid, poorly ventilated conditions.",
        ("Check the underside of affected leaves.", "Improve airflow where possible and monitor new growth."),
        "Reduce prolonged humidity around foliage and avoid dense, poorly ventilated planting.",
    ),
    "Tomato___Septoria_leaf_spot": _entry(
        "Tomato", "Septoria leaf spot",
        "Small round spots may have dark margins and pale centers.",
        "Septoria leaf spot is a fungal disease that mainly affects tomato leaves.",
        ("Inspect lower leaves and nearby plants.", "Remove badly affected leaves where practical and monitor spread."),
        "Avoid unnecessary leaf wetting and clear infected debris where appropriate.",
    ),
    "Tomato___Spider_mites Two-spotted_spider_mite": _entry(
        "Tomato", "Two-spotted spider mite",
        "Fine yellow speckling, bronzing, or delicate webbing can occur on leaves.",
        "Spider mites are small pests; similar leaf damage can have other causes.",
        ("Inspect leaf undersides closely for mites or webbing.", "Seek local integrated pest-management guidance before choosing a control method."),
        "Monitor plants regularly and conserve beneficial insects where possible.",
    ),
    "Tomato___Target_Spot": _entry(
        "Tomato", "Target spot",
        "Brown leaf lesions may show concentric rings and can resemble other diseases.",
        "Target spot is a fungal disease; visual symptoms can overlap with other leaf problems.",
        ("Compare symptoms across several leaves.", "Remove badly affected foliage where practical and ask for local confirmation if it spreads."),
        "Maintain airflow and avoid prolonged leaf wetness where possible.",
    ),
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": _entry(
        "Tomato", "Tomato yellow leaf curl virus",
        "Leaves may curl upward and yellow; plants can appear stunted.",
        "This viral disease is associated with whitefly transmission and can affect plant growth.",
        ("Check new growth and nearby plants for similar curling.", "Seek local advice about whitefly management and affected plants."),
        "Use healthy seedlings and follow local guidance for managing whitefly vectors.",
    ),
    "Tomato___Tomato_mosaic_virus": _entry(
        "Tomato", "Tomato mosaic virus",
        "Leaves may show mottled light and dark green areas or distortion.",
        "Mosaic symptoms can be associated with a virus but may resemble other stresses.",
        ("Check multiple leaves and nearby plants.", "Clean tools between plants and seek local confirmation if symptoms persist."),
        "Use clean planting material and practice tool hygiene.",
    ),
    "Tomato___healthy": _entry(
        "Tomato", "Healthy leaf pattern",
        "The model did not detect one of its trained disease patterns in this image.",
        "This is a model prediction, not proof that the plant is disease-free.",
        ("Continue routine plant checks.", "Look at both leaf surfaces and new growth over time."),
        "Use healthy seedlings and maintain appropriate spacing and field hygiene.",
    ),
    "Cassava___Bacterial_Blight": _entry(
        "Cassava", "Bacterial blight",
        "Angular leaf lesions, wilting, or shoot dieback may occur.",
        "Cassava bacterial blight can affect leaves and shoots and may spread through planting material or rain splash.",
        ("Check nearby plants and new shoots.", "Use healthy cuttings and ask local agricultural staff for guidance if symptoms spread."),
        "Use healthy planting material and follow local field sanitation guidance.",
    ),
    "Cassava___Brown_Streak_Disease": _entry(
        "Cassava", "Brown streak disease",
        "Leaf symptoms may include yellowing along veins; root damage may not be visible in a leaf photo.",
        "Cassava brown streak disease can affect foliage and storage roots; a leaf image cannot assess root condition.",
        ("Check several plants and consult local cassava advisers.", "Use locally recommended clean planting material."),
        "Choose planting material and varieties recommended by local agricultural services.",
        "A leaf-photo prediction cannot confirm root symptoms.",
    ),
    "Cassava___Green_Mottle": _entry(
        "Cassava", "Green mottle",
        "Leaves may show mottling, distortion, or uneven green patterns.",
        "Green mottle is a modeled cassava disease category; other stresses can look similar.",
        ("Compare symptoms on several leaves.", "Seek local advice if mottling is spreading across plants."),
        "Use healthy planting material and monitor crop health regularly.",
    ),
    "Cassava___Healthy": _entry(
        "Cassava", "Healthy leaf pattern",
        "The model did not detect one of its trained disease patterns in this image.",
        "This is a model prediction, not proof that the plant or its roots are disease-free.",
        ("Continue routine crop checks.", "Monitor new growth and nearby plants for changes."),
        "Use healthy cuttings and locally recommended field practices.",
    ),
    "Cassava___Mosaic_Disease": _entry(
        "Cassava", "Mosaic disease",
        "Leaves may show yellow and green mosaic patterns, distortion, or reduced leaf size.",
        "Cassava mosaic disease is associated with viral infection and can affect plant growth.",
        ("Check new leaves and nearby plants.", "Use locally recommended healthy planting material and seek extension advice if symptoms spread."),
        "Use resistant or tolerant varieties and healthy cuttings where locally available.",
    ),
}


def crop_for_class(class_name: str) -> str | None:
    for crop, prefix in CROP_CLASS_PREFIXES.items():
        if class_name.startswith(prefix):
            return crop
    return None


def disease_info_for(class_name: str) -> DiseaseInfo | None:
    return DISEASE_CATALOG.get(class_name)


def catalog_entries(
    class_names: tuple[str, ...],
    crop: str | None = None,
) -> tuple[tuple[str, DiseaseInfo | None], ...]:
    return tuple(
        (class_name, disease_info_for(class_name))
        for class_name in class_names
        if crop is None or crop_for_class(class_name) == crop
    )