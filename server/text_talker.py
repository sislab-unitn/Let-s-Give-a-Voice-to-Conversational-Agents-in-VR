import requests

if __name__ == "__main__":
    url = "http://localhost:8080/text_converse?bot=anamnesis_bot"
    while True:
        text = input("Enter text: ")
        response = requests.post(url, json={"sender":"123","message": text})
        dc = response.json()
        print(dc["response"])
    
    
    