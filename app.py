# app.py
import streamlit as st
from pathlib import Path
import time
import base64
from model_handler import generate_from_text

st.set_page_config(page_title="Text → 3D (Shap-E) Demo", layout="wide")
st.title("Text → 3D Model Generator")

col1, col2 = st.columns([1, 2])

with col1:
    prompt = st.text_area("Enter a text prompt", value="a small wooden chair with four legs", height=120)
    out_format = st.selectbox("Output format", ["glb", "obj"], index=0)
    steps = st.slider("Generation steps (affects quality / time)", 16, 256, 64)
    generate_btn = st.button("Generate 3D Model")

with col2:
    viewer_placeholder = st.empty()
    download_placeholder = st.empty()
    status = st.empty()

if generate_btn:
    status.info("Starting generation...")
    try:
        t0 = time.time()
        result_path = generate_from_text(prompt, out_format=out_format, steps=steps)
        dt = time.time() - t0
        status.success(f"Model generated: {result_path} (took {dt:.1f}s)")
    except Exception as e:
        status.error(f"Generation failed: {e}")
        raise

    # Display model
    result_path = Path(result_path)
    if out_format == "glb":
        # Try to use streamlit_3d if available
        try:
            import streamlit_3d as st3d  # type: ignore
            with viewer_placeholder.container():
                st.write("Preview (streamlit_3d)")
                st3d.display(result_path.open("rb").read())
        except Exception:
            # Fallback: embed a small Three.js viewer
            st.write("Preview (fallback Three.js)")
            with open(result_path, "rb") as f:
                b = f.read()
            b64 = base64.b64encode(b).decode()
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8" />
            </head>
            <body>
            <div id="container"></div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r146/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/examples/js/loaders/GLTFLoader.js"></script>
            <script>
            const data = "{b64}";
            const bytes = atob(data);
            const arr = new Uint8Array(bytes.length);
            for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
            const blob = new Blob([arr], {{ type: 'model/gltf-binary' }});
            const url = URL.createObjectURL(blob);

            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(40, window.innerWidth/window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth*0.6, window.innerHeight*0.6);
            document.body.appendChild(renderer.domElement);
            const light = new THREE.HemisphereLight(0xffffff, 0x444444);
            light.position.set(0, 20, 0);
            scene.add(light);
            const dir = new THREE.DirectionalLight(0xffffff);
            dir.position.set(0, 20, 10);
            scene.add(dir);

            const loader = new THREE.GLTFLoader();
            loader.load(url, function (gltf) {{
                scene.add(gltf.scene);
                // center camera
                const box = new THREE.Box3().setFromObject(gltf.scene);
                const size = box.getSize(new THREE.Vector3()).length();
                const center = box.getCenter(new THREE.Vector3());
                camera.position.copy(center);
                camera.position.x += size;
                camera.position.y += size/2;
                camera.position.z += size;
                camera.lookAt(center);
                function animate() {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }}
                animate();
            }}, undefined, function (e) {{
                console.error(e);
            }});
            </script>
            </body>
            </html>
            """
            viewer_placeholder.components.v1.html(html, height=600)
    else:
        # For OBJ, just provide download and a notice (no inline viewer)
        viewer_placeholder.info(f"Model saved as {result_path}. Download below.")

    # Download link
    with open(result_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{result_path.name}">Download {result_path.name}</a>'
    download_placeholder.markdown(href, unsafe_allow_html=True)
