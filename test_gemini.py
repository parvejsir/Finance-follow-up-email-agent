# backend/test_gemini.py

import google.generativeai as genai


# =========================
# CONFIGURE API KEY
# =========================
GEMINI_API_KEY ="AIzaSyBDCsGj2n9o5fIxXwzZf15SUVlwPJ0WsRA"


genai.configure(
    api_key=GEMINI_API_KEY
)


# =========================
# LIST AVAILABLE MODELS
# =========================
print("\n🚀 AVAILABLE MODELS:\n")

try:

    for MODEL in genai.list_models():

        print(MODEL.name)

except Exception as ERROR:

    print(
        "\n❌ LIST MODELS ERROR:\n"
    )

    print(ERROR)

    exit()


# =========================
# TEST MODEL
# =========================
TEST_MODEL_NAME = "models/gemini-2.5-flash-lite"


print(
    f"\n🚀 TESTING MODEL: {TEST_MODEL_NAME}\n"
)

try:

    MODEL = genai.GenerativeModel(
        TEST_MODEL_NAME
    )

    RESPONSE = MODEL.generate_content(
        "Say hello in one sentence."
    )

    print(
        "\n✅ MODEL RESPONSE:\n"
    )

    print(RESPONSE.text)

except Exception as ERROR:

    print(
        "\n❌ GENERATION ERROR:\n"
    )

    print(ERROR)