# Exambot QEC readme

# 1. Installation
Install `pipenv` using `pip install pipenv`. Clone this GitHub repository with a method of choice, e.g. using the HTTP link to clone it in Visual Studio Code with little effort. 

Run `pipenv install` in the directory of the cloned repository to install all necessary packages from `Pipfile`. Afterwards, run `pipenv shell` to activate the virtual environment. 

# 2. Setting up the API key
## 2.1 Create a Google Project with Drive API access
Access [Google Cloud console](https://code.google.com/apis/console) with your Google account. Create a new project called **Exambot**. Via the hamburger menu, navigate to **APIs and services**, followed by **Enabled APIs and services**. Select **Enable API** and search for the Google Drive API, toggle it and select **ENABLE** in the information page.

## 2.2 Create API credentials
In the menu of **APIs and services**, select **Credentials**. Select **Create Credentials** and create an **OAuth Client ID**. Select **Desktop app** as the application type and choose an arbitrary name for the credentials. A window will open, use the **Download JSON** option and save the file as `credentials.json` in the directory of your local version of this repository.

## 2.3 Create an access token
Run `drive_api_quickstart.py` and follow through the authentication in the newly opened browser window. Select the Google account that has access to the QEC drive. This will create `token.json`, if completed successfully. This token is only valid 7 days since you are not the owner of the QEC drive.

# 3. Generate Protocols
## 3.1 Set up the ini-file
Before you can start generating protocols, download the ini-file from the confluence documentation on exam protocols to your local repository folder. Change the variable `filepath_local` to your directory containing the code.

## 3.2 Run exambot.py
If you have strictly followed all of the steps described above, you can now start generating exam protocols by running `exambot.py`. Monitor the logger output in the terminal.

# 4. Developing yourself
## 4.1 Setting up your own branch
Create your own dev branch using `git checkout -b dev/your_name`. 

## 4.2 Pushing and pulling etc.
You might worry that you push a lot of documents since you just created a lot of documents but these and the credentials will simply be ignored due to the settings in the `.gitignore` file.

