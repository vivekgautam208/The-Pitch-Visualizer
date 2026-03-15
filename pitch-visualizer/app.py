from flask import Flask, render_template, request
import nltk
import requests
import os

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

app = Flask(__name__)

API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

API_KEY = os.environ.get("HF_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def generate_image(prompt, filename):

    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt}
    )

    if response.status_code == 200:

        image_path = f"static/{filename}.png"

        with open(image_path, "wb") as f:
            f.write(response.content)

        return image_path

    else:
        print("Error:", response.text)
        return None


def create_prompt(sentence):
    return f"cinematic digital illustration, storytelling scene, high quality concept art, {sentence}"


@app.route("/", methods=["GET", "POST"])
def index():

    images = []
    captions = []

    if request.method == "POST":

        story = request.form["story"]

        sentences = nltk.sent_tokenize(story)

        for i, sentence in enumerate(sentences):

            prompt = create_prompt(sentence)

            image_file = generate_image(prompt, f"scene_{i}")

            images.append(image_file)
            captions.append(sentence)

    return render_template("index.html", images=images, captions=captions)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
