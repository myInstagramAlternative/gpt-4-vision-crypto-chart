import base64
import requests
import base64
from PIL import ImageGrab
from io import BytesIO

# OpenAI API Key
api_key = ""

class Conversation:
    def __init__(self, api_key, model="gpt-4-vision-preview", max_tokens=500):
        """
        Initializes the API client with the provided API key, model name, and maximum number of tokens. 

        Parameters:
            - api_key (str): The API key used to authenticate the client.
            - model (str, optional): The name of the model to use. Defaults to "gpt-4-vision-preview".
            - max_tokens (int, optional): The maximum number of tokens allowed in the generated output. Defaults to 500.

        Returns:
            None
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.model = model
        self.max_tokens = max_tokens
        self.system_instruction = "You are a helpful crypto trader assistant. You will be given a chart and asked to perform technical analysis. On image you will have chart with 50 and 200 MA, under chart you will have volume and bellow it RSI. Try to recognize patterns which can tell where price will go. Keep it short, concise and to the point. Short term should I short or long futures or not enter at the moment?"
        self.initial_payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_instruction,
                },
            ],
            "max_tokens": self.max_tokens,
        }
        self.payload = self.initial_payload

    def get_encoded_image_from_clipboard(self):
        

        # Grab the image from the clipboard
        image = ImageGrab.grabclipboard()

        # Check if there is an image in the clipboard
        if isinstance(image, ImageGrab.Image.Image):
            # Create a BytesIO object to hold the image data
            buffered = BytesIO()

            # Save the image to the BytesIO object in PNG format
            image.save(buffered, format="PNG")

            # Retrieve the binary image data from the BytesIO object
            img_byte = buffered.getvalue()

            # Convert the binary data to a base64-encoded string
            img_base64 = base64.b64encode(img_byte)

            # Convert the base64 bytes to a string
            img_base64_str = img_base64.decode("utf-8")

            # Output the Base64 string
            return img_base64_str
        else:
            raise Exception("No image data is found in the clipboard.")

    def submit_chart(self, instruction="Perform Technical analysis based off of this chart."):
        self.payload["messages"].append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": instruction,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self.get_encoded_image_from_clipboard()}",
                            "detail": "high",
                        },
                    },
                ],
            }
        )

    def handler(self):
        if len(self.payload["messages"]) == 1:
            self.submit_chart()

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self.headers,
            json=self.payload,
        )

        response.raise_for_status()
        response_json = response.json()

        if response_json.get("choices"):
            msg = response_json["choices"][0]["message"]["content"]
            self.payload["messages"].append(
                {
                    "role": "assistant",
                    "content": msg,
                }
            )
            print(msg + "\n")
            new_msg = input("Enter your response: ")
            if new_msg == "chart":
                new_msg = input("Chart instruction: ")
                self.submit_chart(new_msg)
            else:
                self.payload["messages"].append(
                    {
                        "role": "user",
                        "content": new_msg,
                    }
                )
            print("\n")
            self.handler()


conversation = Conversation(api_key)
conversation.handler()
