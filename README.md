# ACEest Fitness & Gym – CI/CD Assignment

A small Flask API for managing gym programs and clients. It's based on the logic of the earlier Tkinter versions (the three programs – Fat Loss, Muscle Gain, Beginner – and calorie targets), rebuilt as a web service so it can be containerised and run through a pipeline.

## Endpoints

| Method | Path | What it does |
|--------|------|--------------|
| GET | `/` , `/health` | status checks |
| GET | `/programs` | list programs |
| GET | `/programs/<FL\|MG\|BG>` | workout + diet plan |
| GET/POST | `/clients` | list / add client (name, program, weight, height) |
| GET/DELETE | `/clients/<id>` | fetch / remove a client |

Adding a client returns the BMI and a daily calorie target. Data is kept in memory only.

## Run locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py                # http://localhost:5000
```

On Linux/macOS, activate the environment with `source venv/bin/activate`.

Example (in a second PowerShell window while the app is running):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/clients `
  -ContentType "application/json" `
  -Body '{"name":"Ravi","program":"FL","weight":80,"height":175}'
```

## Run tests manually

```bash
python -m pytest -v
python -m flake8 .
```

## With Docker

```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
docker run --rm aceest-fitness python -m pytest -v
```

The image uses `python:3.12-slim`, installs deps with no pip cache, and runs gunicorn as a non-root user.

## CI/CD overview

**GitHub Actions** (`.github/workflows/main.yml`) runs on every push and pull request:
1. Install dependencies, byte-compile `app.py` and lint with flake8
2. Build the Docker image
3. Run pytest inside the built container

**Jenkins** (`Jenkinsfile`) is a pipeline job pointed at this GitHub repo (SCM = Git, script path `Jenkinsfile`). A build does a fresh checkout, creates a clean venv, lints, rebuilds the image with `--no-cache`, and runs the tests in the container. It acts as a second check in a clean environment. Jenkins needs Python 3 and Docker available on the agent. Trigger it manually, by polling SCM, or with a GitHub webhook.

### Jenkins setup

Use a Linux agent with Git, Python 3 (including the `venv` module), and Docker.
The Jenkins agent user must have permission to run Docker commands. The
`Jenkinsfile` uses `sh`, so it is not intended for a native Windows agent.

1. In Jenkins, select **New Item**, enter `aceest-fitness`, and choose **Pipeline**.
2. Under **Pipeline**, choose **Pipeline script from SCM**, then **Git**.
3. Enter `https://github.com/himanshujaidka/access-fitness-assignment.git`.
4. Set the branch specifier to `*/main` and the script path to `Jenkinsfile`.
5. To check for changes automatically, enable **Poll SCM** with `H/5 * * * *`.
6. Save, select **Build Now**, and check that all stages finish successfully.

GitHub Actions and Jenkins are independent quality gates; neither pipeline
deploys the app to a hosting service. To demonstrate completion, capture the
successful Actions run and the Jenkins stage view/console output after running
them. A committed Jenkinsfile alone is not evidence of a successful Jenkins build.

## Git workflow

For future changes, create a branch such as `feature/client-validation` or
`ci/pipeline-update`, commit the actual changes, and open a pull request into
`main`. Both pushes and pull requests trigger GitHub Actions.
