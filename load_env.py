from dotenv import load_dotenv

dotenv_path = './.env'

if load_dotenv(dotenv_path):
    print("The .env file has been loaded.")
else:
    print("Failed to load the .env file.")