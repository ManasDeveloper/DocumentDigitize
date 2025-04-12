import streamlit as st
import requests
from PIL import Image


# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

st.title("OCR Document Search")

# Sidebar navigation
menu = st.sidebar.selectbox("Select an Option", ["Upload Document", "Search Documents"])

if menu == "Upload Document":
    st.header("Upload Document for OCR")

    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Upload to backend
        if st.button("Extract and Index Text"):
            files = {"file": uploaded_file.getvalue()}
            try:
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.success("File uploaded and indexed successfully!")
                    st.text_area("Extracted Text", data["text"], height=200)
                else:
                    st.error(f"Error: {response.json()['detail']}")
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")

elif menu == "Search Documents":
    st.header("Search Indexed Documents")

    # Search input
    query = st.text_input("Enter search query")

    if st.button("Search"):
        try:
            response = requests.get(f"{BACKEND_URL}/search", params={"q": query})
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    for result in data["results"]:
                        st.write(f"**Filename**: {result['filename']}")
                        st.write(f"**Extracted Text**: {result['text'][:200]}...")  # Show snippet
                        st.write("---")
                else:
                    st.warning(data["message"])
            else:
                st.error(f"Error: {response.json()['detail']}")
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")
