"""Government Schemes API router providing catalog, search, and eligibility matching."""
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter()

# ------------------------------------------------------------------
# Curated Indian Government Agricultural Schemes Catalog
# ------------------------------------------------------------------
SCHEMES_CATALOG: list[dict[str, Any]] = [
    {
        "id": "pm-kisan",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "short_name": "PM-KISAN",
        "category": "Direct Income Support",
        "short_description": "Central sector scheme providing assured income support of ₹6,000 per year directly to bank accounts of landholding farmer families.",
        "benefits": "₹6,000 per annum transferred directly via DBT in three equal 4-monthly installments of ₹2,000 each.",
        "basic_eligibility": "All landholding farmer families with cultivable land parcels in their names, irrespective of land size (excluding institutional landholders and high tax payers).",
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Record (Khatauni / 7/12 / Pattadar Passbook)",
            "Aadhaar-seeded Active Bank Account",
            "Mobile Number linked with Aadhaar",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["All Crops"],
        "min_land_acres": 0.01,
        "max_land_acres": None,
        "priority_categories": ["Small / Marginal", "All Categories"],
        "official_url": "https://pmkisan.gov.in",
        "icon": "🏛️",
        "badge_color": "green",
    },
    {
        "id": "pmfby",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "short_name": "PMFBY",
        "category": "Crop Insurance",
        "short_description": "Comprehensive yield-loss crop insurance covering non-preventable natural risks, localized calamities, post-harvest losses, and unseasonal rainfall.",
        "benefits": "Maximum uniform farmer premium: 2% for Kharif crops, 1.5% for Rabi food/oilseed crops, and 5% for commercial/horticultural crops. Balance premium subsidized by Central & State Govts.",
        "basic_eligibility": "All farmers growing notified crops in notified areas, including sharecroppers, tenant farmers, and loanee/non-loanee farmers.",
        "required_documents": [
            "Aadhaar Card",
            "Land Record (RoR) / Sowing Certificate / Tenancy Agreement",
            "Bank Passbook copy with IFSC",
            "Crop Sowing Declaration / Khasra Girdawari",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["Wheat", "Rice", "Maize", "Cotton", "Soybean", "Pulses", "Millets", "Sugarcane", "Oilseeds", "Vegetables", "Fruits", "All Crops"],
        "min_land_acres": 0.0,
        "max_land_acres": None,
        "priority_categories": ["All Categories", "Small / Marginal", "Tenant Farmers"],
        "official_url": "https://pmfby.gov.in",
        "icon": "🛡️",
        "badge_color": "blue",
    },
    {
        "id": "pmksy",
        "name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY - Per Drop More Crop)",
        "short_name": "PMKSY",
        "category": "Irrigation & Solar",
        "short_description": "Enhances on-farm water use efficiency by promoting precision micro-irrigation technologies (drip and sprinkler systems) with substantial capital subsidies.",
        "benefits": "Up to 55% financial assistance for Small & Marginal farmers and up to 45% for other farmers for installing Drip & Sprinkler micro-irrigation systems.",
        "basic_eligibility": "Farmers of all categories who own cultivable agricultural land with an assured water source (borewell, open well, canal, or farm pond).",
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Document (Khatauni / 7/12 / Jamabandi)",
            "Water Source Proof / Power Connection Receipt",
            "Soil & Water Testing Report",
            "Bank Account Passbook",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["Horticulture", "Vegetables", "Cotton", "Sugarcane", "Wheat", "Maize", "Pulses", "All Crops"],
        "min_land_acres": 0.5,
        "max_land_acres": 12.5,
        "priority_categories": ["Small / Marginal", "Women Farmer", "SC/ST"],
        "official_url": "https://pmksy.gov.in",
        "icon": "💧",
        "badge_color": "cyan",
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card (KCC) Scheme",
        "short_name": "KCC",
        "category": "Credit & Finance",
        "short_description": "Provides farmers with timely and flexible short-term institutional credit for crop cultivation, post-harvest expenses, farm maintenance, and allied activities.",
        "benefits": "Effective interest rate of only 4% p.a. (after 2% Interest Subvention + 3% Prompt Repayment Incentive). Collateral-free credit limit up to ₹1.60 Lakh (up to ₹3 Lakh with simplified hypothecation).",
        "basic_eligibility": "Owner cultivators, tenant farmers, oral lessees, sharecroppers, Self Help Groups (SHGs), and Joint Liability Groups (JLGs) engaged in agriculture or allied sectors.",
        "required_documents": [
            "Aadhaar Card / Voter ID / PAN Card",
            "Land Ownership Record / Registered Tenancy Contract",
            "Crop Sowing Proof / Cropping Pattern Declaration",
            "2 Passport-sized Photographs",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["All Agricultural & Horticultural Crops"],
        "min_land_acres": 0.1,
        "max_land_acres": None,
        "priority_categories": ["All Categories", "Small / Marginal", "Tenant Farmers"],
        "official_url": "https://myscheme.gov.in/schemes/kcc",
        "icon": "💳",
        "badge_color": "emerald",
    },
    {
        "id": "smam",
        "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "short_name": "SMAM",
        "category": "Farm Machinery",
        "short_description": "Promotes modern farm mechanization by providing direct subsidies on agricultural machinery and supporting Custom Hiring Centers (CHCs) in rural areas.",
        "benefits": "40% to 50% subsidy on procurement of tractors, rotavators, seed drills, power tillers, laser land levelers, and sprayers. Up to 80% subsidy for establishing Custom Hiring Centers.",
        "basic_eligibility": "Individual farmers, Farmer Producer Organizations (FPOs), Cooperative Societies. Preferential allotment and higher subsidy for Small/Marginal, SC/ST, and Women farmers.",
        "required_documents": [
            "Aadhaar Card",
            "Land Title Deed / Record of Rights (Parcha / 7/12)",
            "Bank Passbook Copy",
            "Caste Certificate (if claiming SC/ST quota)",
            "Dealer Quotation from Authorized Agricultural Equipment Vendor",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["All Crops"],
        "min_land_acres": 1.0,
        "max_land_acres": None,
        "priority_categories": ["Small / Marginal", "Women Farmer", "SC/ST"],
        "official_url": "https://agrimachinery.nic.in",
        "icon": "🚜",
        "badge_color": "amber",
    },
    {
        "id": "pm-kusum",
        "name": "PM-KUSUM (Solar Agriculture Pump Scheme)",
        "short_name": "PM-KUSUM",
        "category": "Irrigation & Solar",
        "short_description": "Enables farmers to install off-grid standalone solar water pumps or solarize existing grid-connected agricultural pumps with guaranteed buyback of surplus solar power.",
        "benefits": "Up to 60% combined capital subsidy (30% Central Govt + 30% State Govt) on standalone solar pumps (up to 7.5 HP). Farmer contributes only 10% cash, with balance 30% available via bank loan.",
        "basic_eligibility": "Individual farmers, water user associations, and farmer producer groups with cultivable agricultural land requiring irrigation pumping systems.",
        "required_documents": [
            "Aadhaar Card",
            "Land Revenue Document / Khasra Copy",
            "Bank Account Passbook Copy",
            "Electricity Bill / Existing Pump Details (for Component C solarization)",
            "Passport Size Photograph",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["All Crops"],
        "min_land_acres": 0.5,
        "max_land_acres": None,
        "priority_categories": ["Small / Marginal", "Medium / Large", "All Categories"],
        "official_url": "https://pmkusum.mnre.gov.in",
        "icon": "☀️",
        "badge_color": "orange",
    },
    {
        "id": "pkvy",
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "short_name": "PKVY",
        "category": "Soil & Organic",
        "short_description": "Promotes chemical-free organic farming through cluster-based adoption, PGS-India organic certification, bio-inputs, and direct market linkage.",
        "benefits": "Financial assistance of ₹50,000 per hectare over 3 years (₹31,000/ha directly disbursed for organic seeds, bio-fertilizers, bio-pesticides, plus ₹19,000/ha for certification, branding, and packaging).",
        "basic_eligibility": "Farmers willing to form organic farming clusters of 20 or more members covering a contiguous area of 20-50 hectares for certified organic cultivation.",
        "required_documents": [
            "Aadhaar Card",
            "Land Holding Certificate (RoR / Khatauni)",
            "Bank Account Details",
            "Cluster Member Group Agreement",
            "Initial Soil Test Baseline Record",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["Pulses", "Millets", "Vegetables", "Fruits", "Spices", "Wheat", "Rice", "All Crops"],
        "min_land_acres": 0.5,
        "max_land_acres": 5.0,
        "priority_categories": ["Small / Marginal", "All Categories"],
        "official_url": "https://pgsindia-ncof.gov.in",
        "icon": "🌱",
        "badge_color": "emerald",
    },
    {
        "id": "soil-health-card",
        "name": "Soil Health Card Scheme",
        "short_name": "Soil Health Card",
        "category": "Soil & Organic",
        "short_description": "Issues soil health report cards assessing 12 macro/micro-nutrient parameters with customized dosage advisory to improve soil productivity and reduce excessive chemical fertilizer costs.",
        "benefits": "Free soil sample collection, laboratory analysis across 12 parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC), and personalized crop-specific nutrient recommendations issued every 2 years.",
        "basic_eligibility": "All farmers across all Indian states holding or cultivating agricultural land.",
        "required_documents": [
            "Aadhaar Card",
            "Farm Plot Identification (Khasra / Survey Number / GPS coordinates)",
            "Active Mobile Number",
        ],
        "applicable_states": ["All States & UTs"],
        "applicable_crops": ["All Agricultural & Horticultural Crops"],
        "min_land_acres": 0.0,
        "max_land_acres": None,
        "priority_categories": ["All Categories"],
        "official_url": "https://soilhealth.dac.gov.in",
        "icon": "🧪",
        "badge_color": "purple",
    },
]

LEGAL_DISCLAIMER = (
    "This scheme finder and eligibility evaluation provides automated recommendations and relevance estimates "
    "based on public guidelines of Government of India agricultural schemes. It does NOT constitute a legally binding "
    "eligibility decision, sanction, or official entitlement. Final eligibility and grant disbursements are determined "
    "exclusively by designated government departments and nodal banks upon document verification."
)


# ------------------------------------------------------------------
# Request / Response Schemas
# ------------------------------------------------------------------
class EligibilityRequest(BaseModel):
    state: str | None = Field(default=None, description="State of the farmer or farm")
    crop: str | None = Field(default=None, description="Primary crop cultivated")
    land_acres: float | None = Field(default=None, ge=0, le=10000, description="Total cultivable landholding in acres")
    farmer_category: str | None = Field(
        default=None,
        description="Farmer category, e.g. 'Small / Marginal', 'Medium / Large', 'Women Farmer', 'SC/ST', 'Tenant Farmer'"
    )


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@router.get("/")
def get_schemes(
    category: str | None = Query(default=None, description="Filter by category (e.g. Direct Income Support, Crop Insurance, Irrigation & Solar, Credit & Finance, Farm Machinery, Soil & Organic)"),
    state: str | None = Query(default=None, description="Filter by state (e.g. Punjab, Maharashtra, All)"),
    crop: str | None = Query(default=None, description="Filter by crop (e.g. Wheat, Rice, Cotton, All)"),
    search: str | None = Query(default=None, description="Keyword search in name, description, and benefits"),
):
    """
    Retrieve government schemes with optional filters.
    """
    results = SCHEMES_CATALOG

    if category and category.strip() and category.strip().lower() != "all":
        cat_lower = category.strip().lower()
        results = [s for s in results if cat_lower in s["category"].lower()]

    if crop and crop.strip() and crop.strip().lower() != "all":
        crop_clean = crop.strip().lower()
        results = [
            s for s in results
            if any(crop_clean in c.lower() or "all" in c.lower() for c in s["applicable_crops"])
        ]

    if state and state.strip() and state.strip().lower() not in ("all", "all states & uts"):
        state_clean = state.strip().lower()
        results = [
            s for s in results
            if any(state_clean in st.lower() or "all" in st.lower() for st in s["applicable_states"])
        ]

    if search and search.strip():
        term = search.strip().lower()
        results = [
            s for s in results
            if term in s["name"].lower()
            or term in s["short_name"].lower()
            or term in s["short_description"].lower()
            or term in s["benefits"].lower()
            or term in s["category"].lower()
            or any(term in doc.lower() for doc in s["required_documents"])
        ]

    return {
        "status": "success",
        "total": len(results),
        "disclaimer": LEGAL_DISCLAIMER,
        "schemes": results,
    }


@router.post("/check-eligibility")
def check_scheme_eligibility(payload: EligibilityRequest):
    """
    Evaluate farmer criteria (state, crop, land size, category) against scheme conditions
    and return prioritized relevance recommendations with matching explanations.
    """
    evaluated: list[dict[str, Any]] = []

    user_state = payload.state.strip() if payload.state and payload.state.strip() else None
    user_crop = payload.crop.strip() if payload.crop and payload.crop.strip() else None
    user_acres = payload.land_acres
    user_cat = payload.farmer_category.strip() if payload.farmer_category and payload.farmer_category.strip() else None

    for scheme in SCHEMES_CATALOG:
        score = 70  # Baseline score for universal schemes
        reasons: list[str] = []

        # 1. State check
        if user_state and user_state.lower() not in ("all", "all states & uts"):
            applicable_st = scheme["applicable_states"]
            if any(user_state.lower() in st.lower() or "all" in st.lower() for st in applicable_st):
                score += 10
                reasons.append(f"Available and operational in {user_state}")
            else:
                score -= 30
        else:
            reasons.append("Applicable across Indian States & UTs")

        # 2. Crop check
        if user_crop and user_crop.lower() not in ("all", "all crops"):
            applicable_cr = scheme["applicable_crops"]
            if any(user_crop.lower() in c.lower() or "all" in c.lower() for c in applicable_cr):
                score += 10
                reasons.append(f"Tailored support for {user_crop} cultivation")
            else:
                score -= 10
        else:
            reasons.append("Supports all major agricultural crops")

        # 3. Landholding check
        if user_acres is not None:
            min_land = scheme.get("min_land_acres", 0.0)
            max_land = scheme.get("max_land_acres")

            if min_land and user_acres < min_land:
                score -= 15
                reasons.append(f"Minimum recommended land requirement is {min_land} acres")
            elif max_land and user_acres > max_land:
                score -= 10
                reasons.append(f"Targeted primarily for holdings up to {max_land} acres")
            else:
                score += 10
                reasons.append(f"Your farm size ({user_acres} acres) satisfies holding guidelines")

        # 4. Farmer Category check
        if user_cat and user_cat.lower() != "all categories":
            priority_cats = [c.lower() for c in scheme.get("priority_categories", [])]
            if any(user_cat.lower() in c or "all categories" in c for c in priority_cats):
                score += 10
                reasons.append(f"Special priority & enhanced provisions for {user_cat}")
            else:
                reasons.append("Open for general agricultural applicant category")

        # Cap score between 30 and 98
        final_score = max(30, min(98, score))

        if final_score >= 85:
            match_level = "High Match"
            badge_text = "Strong Recommendation"
            is_recommended = True
        elif final_score >= 70:
            match_level = "Moderate Match"
            badge_text = "Eligible Scheme"
            is_recommended = True
        else:
            match_level = "General Match"
            badge_text = "General Applicability"
            is_recommended = False

        evaluated.append({
            **scheme,
            "relevance_score": final_score,
            "match_level": match_level,
            "badge_text": badge_text,
            "is_recommended": is_recommended,
            "match_reasons": reasons,
        })

    # Sort schemes by descending relevance score
    evaluated.sort(key=lambda x: x["relevance_score"], reverse=True)

    recommended_count = sum(1 for s in evaluated if s["is_recommended"])

    return {
        "status": "success",
        "disclaimer": LEGAL_DISCLAIMER,
        "input_profile": {
            "state": user_state or "All States",
            "crop": user_crop or "All Crops",
            "land_acres": user_acres,
            "farmer_category": user_cat or "All Categories",
        },
        "total_schemes": len(evaluated),
        "recommended_count": recommended_count,
        "schemes": evaluated,
    }
