from twython.api import Twython

CUSTOMER_KEY = "502po8P3Mzlr5fTFV2K2gft32"
CUSTOMER_SECRET= "dShuEIHqjOe9St4A19rjAP7KnXAjlYkBAn69NNz7CevddVKIRR"
ACCESS_TOKEN = "933002021027942400-9CL1zWPwNufeWbm1yOv8yHn971cMjmW"
ACCESS_TOKEN_SECRET = "Ue4PMvIZtVJg5HkI6plynnvoPvafSzaMUpK4oQ2oGsilc"

def postTwitter(tweet):  
  try:
    twitter = Twython(CUSTOMER_KEY, CUSTOMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    twitter.update_status(status=tweet)
    return 'Tweet posted!'
  except Exception as e:
    print e
    return 'Check your internet connection.'
  
