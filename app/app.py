import time
import redis
from flask import Flask, render_template, url_for
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt 

load_dotenv() 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)


@app.route('/titanic.csv')
def titanic():
    # Load the Titanic dataset using Pandas
    df = pd.read_csv('titanic.csv')

    # Calculate the number of survivors based on gender
    gender_survivors = df[df['survived'] == 1].groupby('sex').size()

    # Generate the bar chart
    plt.figure(figsize=(8, 6))
    gender_survivors.plot(kind='bar', color=['skyblue', 'lightgreen'])
    plt.title('Survivors by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Number of Survivors')
    plt.xticks(rotation=0)
    
    # Save the bar chart as an image
    chart_path = os.path.join(app.static_folder, 'survivors_chart.png')
    plt.savefig(chart_path)
    plt.close()

    # Convert the first 5 rows of DataFrame to HTML format
    table_html = df.head().to_html()

    # Pass the HTML table and chart path to titanic.html template
    return render_template('titanic.html', table=table_html, chart_path='survivors_chart.png')

# Here static image file
@app.route('/static/HWR_Logo.png')
def serve_image():
    return app.send_static_file('HWR_Logo.png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)