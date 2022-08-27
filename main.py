from io import BytesIO
import os
import typer
import requests
from datetime import datetime
from PIL import Image

from helpers import url_query_params,get_image,save_image_to_filesystem
from config import API_URL,IMAGE_DIR

app= typer.Typer()

default_date = typer.Argument(
    datetime.now().strftime('%Y-%m-%d'),
formats=['%Y-%m-%d']
)


@app.command()
def fetch_image(date:datetime = default_date,
      save:bool=False,
      start: datetime= typer.Option(None),
      end:datetime = typer.Option(None),
):
    print("Sending API request...")
    query_params= url_query_params(datetime, start, end)

    #add the 'date' query parameter to the NASA API call
    response=requests.get(API_URL,params=query_params)

    #raise error if request fails 
    response.raise_for_status()

    #extract url and title from JSON response
    data = response.json()

    if isinstance(data,dict):
        data = [data]
    
    for resp in data:
        url=resp['url']
        title =resp['title']

        print("Fetching Image...")
        image=get_image(url)

        image.show()

        if save:
          save_image_to_filesystem(image, title)
      

        image.close()


if __name__ == '__main__':
    app()