"""Vendors brand logos from Simple Icons (CC0) into tools/icons.json.

Run once, or after adding a technology to TECH:  python tools/fetch_icons.py
"""
import json
import re
import urllib.request
from pathlib import Path

LATEST = "16.33.0"
LEGACY = "9.21.0"  # a few brands were removed from newer releases

# name: (simple-icons slug, version, brand hex)   or   name: (None, monogram, brand hex)
TECH = {
    "Python": ("python", LATEST, "3776AB"),
    "TypeScript": ("typescript", LATEST, "3178C6"),
    "JavaScript": ("javascript", LATEST, "F7DF1E"),
    "Java": ("openjdk", LATEST, "E76F00"),
    "Kotlin": ("kotlin", LATEST, "7F52FF"),
    "C": ("c", LATEST, "A8B9CC"),
    "C++": ("cplusplus", LATEST, "00599C"),
    "Dart": ("dart", LATEST, "0175C2"),
    "Swift": ("swift", LATEST, "F05138"),
    "Bash": ("gnubash", LATEST, "4EAA25"),
    "React": ("react", LATEST, "61DAFB"),
    "Next.js": ("nextdotjs", LATEST, "000000"),
    "Vue": ("vuedotjs", LATEST, "4FC08D"),
    "Tailwind CSS": ("tailwindcss", LATEST, "06B6D4"),
    "Vite": ("vite", LATEST, "9135FF"),
    "Redux": ("redux", LATEST, "764ABC"),
    "Three.js": ("threedotjs", LATEST, "000000"),
    "Flutter": ("flutter", LATEST, "02569B"),
    "Android": ("android", LATEST, "3DDC84"),
    "Node.js": ("nodedotjs", LATEST, "5FA04E"),
    "Express": ("express", LATEST, "000000"),
    "FastAPI": ("fastapi", LATEST, "009688"),
    "Django": ("django", LATEST, "092E20"),
    "Flask": ("flask", LATEST, "3BABC3"),
    "Spring Boot": ("springboot", LATEST, "6DB33F"),
    "GraphQL": ("graphql", LATEST, "E10098"),
    "Socket.IO": ("socketdotio", LATEST, "000000"),
    "pandas": ("pandas", LATEST, "150458"),
    "NumPy": ("numpy", LATEST, "4DABCF"),
    "SciPy": ("scipy", LATEST, "8CAAE6"),
    "Polars": ("polars", LATEST, "0075FF"),
    "Matplotlib": (None, "Mpl", "11557C"),
    "Seaborn": (None, "sns", "4C72B0"),
    "Plotly": ("plotly", LATEST, "7A76FF"),
    "Jupyter": ("jupyter", LATEST, "F37626"),
    "Power BI": ("powerbi", LEGACY, "F2C811"),
    "PyTorch": ("pytorch", LATEST, "EE4C2C"),
    "TensorFlow": ("tensorflow", LATEST, "FF6F00"),
    "Keras": ("keras", LATEST, "D00000"),
    "scikit-learn": ("scikitlearn", LATEST, "F7931E"),
    "XGBoost": (None, "XG", "189FDD"),
    "LightGBM": (None, "LG", "3FA34D"),
    "Hugging Face": ("huggingface", LATEST, "FFD21E"),
    "OpenCV": ("opencv", LATEST, "5C3EE8"),
    "LangChain": ("langchain", LATEST, "1C3C3C"),
    "MLflow": ("mlflow", LATEST, "0194E2"),
    "DVC": ("dvc", LATEST, "13ADC7"),
    "Airflow": ("apacheairflow", LATEST, "017CEE"),
    "Kubeflow": (None, "KF", "4279F4"),
    "Weights & Biases": ("weightsandbiases", LATEST, "FFBE00"),
    "BentoML": ("bentoml", LATEST, "000000"),
    "ONNX": ("onnx", LATEST, "005CED"),
    "PostgreSQL": ("postgresql", LATEST, "4169E1"),
    "MySQL": ("mysql", LATEST, "4479A1"),
    "MongoDB": ("mongodb", LATEST, "47A248"),
    "Redis": ("redis", LATEST, "FF4438"),
    "SQLite": ("sqlite", LATEST, "003B57"),
    "Supabase": ("supabase", LATEST, "3FCF8E"),
    "Firebase": ("firebase", LATEST, "DD2C00"),
    "Prisma": ("prisma", LATEST, "2D3748"),
    "AWS": ("amazonaws", LEGACY, "232F3E"),
    "Google Cloud": ("googlecloud", LATEST, "4285F4"),
    "Azure": ("microsoftazure", LEGACY, "0078D4"),
    "Vercel": ("vercel", LATEST, "000000"),
    "Cloudflare": ("cloudflare", LATEST, "F38020"),
    "Docker": ("docker", LATEST, "2496ED"),
    "Kubernetes": ("kubernetes", LATEST, "326CE5"),
    "GitHub Actions": ("githubactions", LATEST, "2088FF"),
    "Linux": ("linux", LATEST, "FCC624"),
    "Git": ("git", LATEST, "F03C2E"),
    "GitHub": ("github", LATEST, "181717"),
    "VS Code": ("visualstudiocode", LEGACY, "007ACC"),
    "IntelliJ IDEA": ("intellijidea", LATEST, "000000"),
    "Postman": ("postman", LATEST, "FF6C37"),
    "Figma": ("figma", LATEST, "F24E1E"),
    "Notion": ("notion", LATEST, "000000"),
}


def main():
    out = {}
    for name, (slug, version, hex_) in TECH.items():
        if slug is None:
            out[name] = {"monogram": version, "hex": hex_}
            continue
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@{version}/icons/{slug}.svg"
        with urllib.request.urlopen(url, timeout=30) as r:
            path = re.search(r'<path d="([^"]+)"', r.read().decode()).group(1)
        out[name] = {"path": path, "hex": hex_}
    target = Path(__file__).with_name("icons.json")
    target.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"Wrote {len(out)} icons to {target}")


if __name__ == "__main__":
    main()
