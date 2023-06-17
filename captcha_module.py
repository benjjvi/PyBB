import random

from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha

import bbcrypto


def create_audio_and_image_captcha():
    # Create a random string of 5 characters:
    captchaString = ""
    for i in range(5):
        captchaString += random.choice("abcdefghijklmnopqrstuvwxyz0123456789")

    # Initialise the audio and image captcha devices:
    audio = AudioCaptcha(voicedir="./captcha_voice/en")
    image = ImageCaptcha(fonts=["./static/NunitoSans.ttf"])

    # Write the captcha to the files corresponding with their names:
    audio.write(captchaString, f"./static/captchas/{captchaString}.wav")
    image.write(captchaString, f"./static/captchas/{captchaString}.png")

    # Make a token for the captcha, by storing the captcha string in a file with the format:
    # captcha:hashed_caption

    # Create the token:
    token = f"{captchaString}:{bbcrypto.get_hashed_password(captchaString).decode('utf-8')}"

    # Write the token to the file:
    with open("./db/captchas", "a") as f:
        f.write(token + "\n")

    # Return the token:
    return token


def check_captcha(captchaHashed, captchaResponse):
    # Get all captchas from the captcha file.
    # The format of the file is:
    # captcha:hashed_captcha:expiry_time
    with open("./db/captchas", "r") as f:
        captchas = f.read().split("\n")

    # To check if the captcha is found, we can go through this process;
    # 1. Check if the hashed captcha is in the list of captchas.
    # 2. If it is, check if the captcha string matches index zero of the captcha.
    # 3. If it does, return True, else return False.

    returnval = False

    # Go through each captcha in the list of captchas:
    for captcha in captchas:
        # Split the captcha into its components:
        captchaComponents = captcha.split(":")
        if len(captchaComponents) != 2:
            continue

        # Check if the hashed captcha matches the hashed captcha in the list:
        if captchaHashed == captchaComponents[1]:
            # Check if the captcha string matches the captcha string in the list:
            if captchaResponse == captchaComponents[0]:
                # Return True if it does:
                returnval = True

    return returnval
