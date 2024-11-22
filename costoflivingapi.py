import requests

url = "https://cost-of-living-and-prices.p.rapidapi.com/prices"

querystring = {"city_name":"Bratislava","country_name":"Slovakia"}

headers = {
	"x-rapidapi-key": "4fcef64a24msh32ef70a7879494fp1e1fa5jsn5562c6363608",
	"x-rapidapi-host": "cost-of-living-and-prices.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())