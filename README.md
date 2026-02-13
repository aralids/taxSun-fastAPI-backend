# taxSun Metagenomic Visualization

<p align="center"><img src="./assets/taxsun_demo.png" width="70%"></p>

taxSun is an interactive web application for visualizing metagenomic classification results based on the NCBI taxonomy database. It allows users to upload TSV files and explore abundance distributions across taxonomic ranks in a radial visualization.

You can access the live app [here](https://taxsun-frontend-production-ed00.up.railway.app/).

## How to download and run locally

Occasionally, especially if your TSV file contains > 10,000 unique taxIDs, the remote backend might give up on it and fail to load your data. In this case, you can run the program locally and avoid a time-out. Please note that the processing of your file might still need a couple of minutes depending on how diverse your metagenome is.

> [!NOTE]
> This guide assumes that you already have Python and Node.js/npm installed on your machine.

> [!IMPORTANT]
> The NCBI taxonomy database gets regularly updated and is unusable for a couple of hours.

1. Download and unzip the code from [the frontend repository](https://github.com/aralids/taxSun-frontend) (referred to as "frontend folder" from now on)
2. Download and unzip the code from [the backend repository](https://github.com/aralids/taxSun-fastAPI-backend) into another folder (referred to as "backend folder" from now on)

3. Open a terminal in the backend folder and run the following commands:
   - `python -m venv venv` (to create a virtual environment)
   - `source venv/bin/activate` for Linux/MacOS or `venv\Scripts\activate` for Windows (to start the virtual environment)
   - `python -m pip install -r requirements.txt` (to install all dependencies within the environment)
   - `python -m uvicorn main:app` (to run the backend)

   It might take a few minutes to load the NCBI taxonomy database, after which the backend will be running at http://localhost:8000.

4. Open a second terminal in the frontend folder and run the following commands:
   - `npm install`
   - `npm run build`
   - `npm run preview`
     The frontend will usually be hosted at http://localhost:4173, or on another port if this one is not available. Open it and use taxSun like you would the deployed version.
