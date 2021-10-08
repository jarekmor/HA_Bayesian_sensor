from requests import get
import json

IP = '192.168.1.5:8123'  #IP address of your HA server
END_POINT = "states"
url = "http://{}/api/{}".format(IP ,END_POINT)

HA_API_KEY = "Bearer XXXXXXXXXXXXXXXXXXXXX"  #Long-Lived Access Tokens from HA

headers={"Authorization": HA_API_KEY,
        "content-type": "application/json"
        }
response = get(url, headers=headers)
response_json = response.json()

#search of HA's entities and their states or attributes for defined observations
for i in range(len(list(response_json))):
    if response_json[i]['entity_id'] == 'sun.sun':
        output_sun = response_json[i]['state']
    if response_json[i]['entity_id'] == 'weather.home':
        output_weather = response_json[i]['state']
    if response_json[i]['entity_id'] == "sensor.airly_pressure_2":
        output_airly_pressure = float(response_json[i]['state'])
    if response_json[i]['entity_id'] == "sensor.airly_humidity_2":
        output_airly_humid = float(response_json[i]['state'])

#main function based on Bayesian rule
def update_probability(prior, prob_true, prob_false=0.):
    numerator = prob_true * prior
    denominator = numerator + prob_false * (1 - prior)
    probability = numerator / denominator
    return probability

#initial parameters for Bayesian function
prior = 0.1
threshold = 0.9
posterior = 0

#observations for Bayesian function with prob_true and prob_false propabilities
#entity_id: weather_home
prob_true_1 = 0.6
prob_false_1 = 0.2
sensor_cloudy = output_weather
try:
    if sensor_cloudy == 'cloudy':
        posterior = update_probability(prior, prob_true_1, prob_false_1)
        prior = posterior
except:
    prior = prior

#entity_id: weather_home
prob_true_2 = 0.6
prob_false_2 = 0.1
sensor_snowy = output_weather
try:
    if sensor_snowy == 'snowy':
        posterior = update_probability(prior, prob_true_2, prob_false_2)
        prior = posterior
except:
    prior = prior

#entiry_id: weather_home
prob_true_3 = 0.9
prob_false_3 = 0.1
sensor_rainy = "rainy"
try:
    if sensor_rainy == 'rainy':
        posterior = update_probability(prior, prob_true_3, prob_false_3)
        prior = posterior
except:
    prior = prior

#entity_id: sun.sun
prob_true_4 = 0.5
prob_false_4 = 0.5
sensor_sun_state = output_sun
try:
    if sensor_sun_state == 'above':
        posterior = update_probability(prior, prob_true_4, prob_false_4)
        prior = posterior
except:
    prior = prior    

#entity_id: sensor.airly_pressure
prob_true_5 = 0.65
prob_false_5 = 0.1
sensor_pressure = output_airly_pressure
try:
    if sensor_pressure <= 1000:
        posterior = update_probability(prior, prob_true_5)
        prior = posterior
except:
    prior = prior

#entity_id: sensor.airly_humidity
prob_true_6 = 0.5
prob_false_6 = 0.1
sensor_humid = output_airly_humid
try:
    if sensor_humid >= 70:
        posterior = update_probability(prior, prob_true_6, prob_false_6)
        prior = posterior
except:
    prior = prior

if posterior > 0 and posterior >= threshold:
    print('On')
else:
    print('Off')