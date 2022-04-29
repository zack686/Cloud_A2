import requests
import os
import json

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


bearer_token = "AAAAAAAAAAAAAAAAAAAAAEsNbgEAAAAA1X6WSK4PEKbw82NXCWGKCgD%2Bjt4%3DjXHskBEH0Fbt2ipcW79cwjZ1ScACNLrz6kTeCHylMkyn2b6Aks"

def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream"
consumer_key = "UG5SdYVvFUllQjGmbaujH1sjE"
consumer_secret = "ZNTk1vEgLplByLIosOkJo7011a4OeTR9yeQsnS5hUFLawQnYsx"
access_token = "1513036168199553031-pdsr3Bip4XwELmSre9P7uck1pl3xl5"
access_token_secret = "9cOIV9rHndNov8QD4GSbjS0QUjls03KJuEhCR4bt5STnX"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth, stream=True)
    print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json_response)
            print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def main():
    url = create_url()
    timeout = 0
    while True:
        connect_to_endpoint(url)
        timeout += 1


if __name__ == "__main__":
    main()