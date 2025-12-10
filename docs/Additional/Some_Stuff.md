Write package in requirements-dev.in, then run the following command to generate the requirements-dev.txt file

pip-compile requirements-dev.in -o requirements-dev.txt


Activating the virtual environment
source .venv/Scripts/activate

Uvicorn server start, run this from root directory, after venv
uvicorn src.app.main:app --reload

Added the dataset to the evidently AI dasboards
The dashboard is now live on the localhost:7000
To view the dashboard go into the evidently dashboard branch and download the data drift html file and then you can view it

First Run, to update main branch
git checkout main
git pull origin main

Then to checkout a new branch
git checkout -b new-branch-name
