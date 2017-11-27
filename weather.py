import urllib2, urllib, json

def getWeather():
  baseWeatherUrl = "https://query.yahooapis.com/v1/public/yql?"
  query = "select wind from weather.forecast where woeid=124162"
  weatherUrl = baseWeatherUrl + urllib.urlencode({'q':query}) + "&format=json"
  try:
    result = urllib2.urlopen(weatherUrl).read()
    data = json.loads(result)
    return data
  except Exception as e:
    print e
    return None