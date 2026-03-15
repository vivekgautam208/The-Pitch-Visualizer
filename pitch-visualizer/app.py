import os
import requests
import nltk
from flask import Flask, render_template, request

# download tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = Flask(__name__)

API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = os.environ.get("HF_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ensure static folder exists
os.makedirs("static", exist_ok=True)


# ------------------------------
# 1. Narrative Segmentation
# ------------------------------
def segment_story(text):

    sentences = nltk.sent_tokenize(text)

    # ensure at least 3 scenes
    return sentences[:5]


# ------------------------------
# 2. Prompt Engineering
# ------------------------------
def create_visual_prompt(sentence, style):

    prompt = (
        f"{style} illustration, cinematic scene, dramatic lighting, "
        f"detailed environment, storytelling moment: {sentence}"
    )

    return prompt


# ------------------------------
# 3. Image Generation
# ------------------------------
def generate_image(prompt, filename):

    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt}
    )

    if response.status_code == 200:

        path = f"static/{filename}.png"

        with open(path, "wb") as f:
            f.write(response.content)

        return path

    else:
        print("API Error:", response.text)
        return None


# ------------------------------
# 4. Flask Route
# ------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    images = []
    captions = []

    if request.method == "POST":

        story = request.form.get("story")
        style = request.form.get("style")

        scenes = segment_story(story)

        for i, scene in enumerate(scenes):

            prompt = create_visual_prompt(scene, style)

            image = generate_image(prompt, f"scene_{i}")

            if image:
                images.append(image)
                captions.append(scene)

    return render_template("index.html", images=images, captions=captions)


# ------------------------------
# Run Server
# ------------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=True)
