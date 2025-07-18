import streamlit as st
from github import Github
import os
import zipfile
import io
import tempfile
import requests
import pandas as pd
import glob

token = os.getenv('GITHUB_TOKEN')
g = Github(token)

st.set_page_config(
    page_title="Immo Scraper",
    page_icon=":house:",
)

repo = g.get_repo("slevin48/immo-versailles")
st.write(repo.get_contents("README.md").decoded_content.decode("utf-8"))

# Fetch successful workflow runs from the repository
successful_runs = repo.get_workflow_runs(status="success")

# Build a list of the names and IDs of the successful runs
runs_list = [run.id for run in successful_runs]

# Get artifacts for each successful run
artifacts_info = []
for run_id in runs_list:
    artifacts = repo.get_workflow_run(run_id).get_artifacts()
    for artifact in artifacts:
        artifacts_info.append({
            "run_id": run_id,
            "artifact_id": artifact.id,
            "name": artifact.name,
            "size_in_bytes": artifact.size_in_bytes,
            "created_at": artifact.created_at,
            "expired": artifact.expired,
            "artifact_obj": artifact  # Store the artifact object itself
        })

# Display artifacts info in Streamlit
if st.sidebar.toggle("Show Artifacts Info", False):
    st.table(artifacts_info)

st.sidebar.write("Artifacts:")
# Option to download and unzip artifacts
for artifact_info in artifacts_info:
    artifact = artifact_info["artifact_obj"]
    # Display only the date part (YYYY-MM-DD) in the button
    created_date = str(artifact_info['created_at'])[:10]
    if st.sidebar.button(f"{created_date}", key=f"artifact_btn_{artifact_info['artifact_id']}"):
        # Download the artifact as a zip file using requests
        download_url = artifact.archive_download_url
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        response = requests.get(download_url, headers=headers)
        if response.status_code == 200:
            zip_bytes = response.content
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                    # st.write(f"Extracted files for artifact {artifact_info['name']}:")
                    # st.write(zip_ref.namelist())
                    csv_files = glob.glob(f"{tmpdir}/**/*.csv", recursive=True)
                    if csv_files:
                        csv_file = csv_files[0]
                        st.write(f"Displaying: {os.path.basename(csv_file)}")
                        df = pd.read_csv(csv_file, index_col=0)
                        
                        # Display each row with the requested fields and image
                        for idx, row in df.iterrows():
                            st.markdown("---")
                            cols = st.columns([2, 3])
                            with cols[0]:
                                # Render image from the extracted tmpdir, only .jpg
                                ref = str(row.get('ref', ''))
                                img_path_jpg = os.path.join(tmpdir, f"img/{ref}.jpg")
                                if os.path.exists(img_path_jpg):
                                    st.image(img_path_jpg)
                                else:
                                    st.write("No image available.")
                            with cols[1]:
                                title = row.get('title', '')
                                link = row.get('link', '')
                                price = row.get('price_eur', '')
                                rooms = row.get('rooms', '')
                                surface = row.get('surface_m2', '')
                                description = row.get('description', '')
                                st.markdown(f"**Title:** {title}")
                                if link:
                                    st.markdown(f"[Link]({link})")
                                # st.markdown(f"**Ref:** {ref}")
                                st.markdown(f"**Price:** {price} € - **Rooms:** {rooms} - **Surface:** {surface} m²")
                                # st.markdown(f"**Description:** {description}")
                        st.markdown("---")
                        st.dataframe(df)
                    else:
                        st.warning("No CSV files found in the artifact.")
        else:
            st.error(f"Failed to download artifact: {response.status_code}")