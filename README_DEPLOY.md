Render deployment instructions

1) Create a GitHub repository and push this project to it
   - cd d:\website
   - git init
   - git add .
   - git commit -m "Initial commit: prepare project for deployment\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
   - Create repo on GitHub and push (or use gh cli)

2) Create the Render web service
   - On https://dashboard.render.com create a new Web Service
   - Connect to your GitHub repo
   - Select branch: main
   - Render will detect render.yaml and dockerfile and build using Docker
   - If you prefer, set up the service manually with env: Docker and DockerfilePath: Dockerfile

3) Configure GitHub repository secrets
   - In your GitHub repository: Settings -> Secrets -> Actions
   - Add RENDER_API_KEY with a Render account API key (Account -> API Keys -> Create Key)
   - Add RENDER_SERVICE_ID with the Render Service ID for your web service (found in Render service settings)

4) Automatic deploys
   - On each push to main the GitHub Actions workflow will trigger and call the Render API to start a deploy.

Notes & troubleshooting
- If you prefer to let Render build from source without using Docker, you can remove render.yaml and configure the service to use "Environment: Python" and build command "pip install -r requirements.txt" and start command "gunicorn app:app".
- Ensure you do not commit your venv directory or any secrets. .gitignore was added.
- If Render reports build errors, check the build logs in the Render dashboard. Common issues: missing system packages for building native wheels (install via apt in Dockerfile) or package version conflicts.

Security / Legal
- This app scrapes external movie sites. Verify compliance with those sites' terms and applicable law before deploying publicly.
