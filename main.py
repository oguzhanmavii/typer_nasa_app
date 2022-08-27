from io import BytesIO
import asyncio
import os
import typer
import httpx
import requests
from datetime import datetime,date
from PIL import Image

from helpers import url_query_params,get_image,save_image_to_filesystem
from config import API_URL

app= typer.Typer()

default_date = typer.Argument(
    datetime.now().strftime('%Y-%m-%d'),
formats=['%Y-%m-%d']
)

async def get_images(urls):
    async with httpx.AsyncClient() as client:
        tasks = []
        for url in urls:
            tasks.append(
                asyncio.create_task(get_image(client,url))
            )
        images= await asyncio.gather(*tasks)
        return images


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

    urls= [d['url'] for d in data if d['media_type']== 'image']
    titles = [d['title'] for d in data if d['media_type']== 'image']
    
    for resp in data:
        if resp['media_type'] != 'image':
            print(f"No image avaible for {resp['date']}")
    
    
    images= asyncio.run( get_images(urls))

    print(images)
    
    for i,image, in enumerate(images):
        image.show()

        if save:
          save_image_to_filesystem(image, titles[i])
      

        image.close()


if __name__ == '__main__':
    app()