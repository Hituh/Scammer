import requests
from time import sleep


def find_player(name):
    base_url = "https://murderledger.com/api/player-search/"
    max_tries = 5

    for attempt in range(max_tries):
        try:
            request = requests.get(base_url + name, timeout=30)
            status_code = request.status_code

            if status_code == 200:
                data = request.json()
                results = data['results']
                if len(results) > 0:
                    return True
                else:
                    return False
            else:
                print(f"Request failed with status code: {status_code}")
                print(request.text)  # Print the response text for debugging

        except requests.Timeout:
            print("Request timed out. Trying again in 10 seconds")
            sleep(10)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    print("Max retries reached. Something failed during the request.")
    return None  # Or raise an exception if you prefer


# Example usage:
# result = find_player("Hitu3h")
# if result:
#     print('Found player')
# elif not result:
#     print('Player not found')
# elif result is None:
#     print("Error occurred during the request.")
