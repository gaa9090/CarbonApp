# leafZer0
leafZer0 is a project made over the Rochester Institute of Technology Hackathon BrickHack 11.
We aim to provide insightful information and predictions based on an orginizations consumption
data. This project uses a website to map user data onto different graphs and uses AI to generate 
predictions for what is to come.

## Tech Stack
Frontend: HTML, CSS, Javascript, Bootstrap
Backend: Django, Python
Database: SQL
ML/AI: Python, TensorFlow/Keras, 
Visualization/Processing: Python, Seaborn, NumPy, Pandas,   

## Installation

1. Install and initialize Django
    Use this to install Django
        '''pip install django'''

    Use this to initialize your project
        '''django-admin startproject leafZer0'''
    
2. Install Machine Learnig Dependencies
    '''pip install tensorflow numpy pandas matplotlib scikit-learn'''

## Usage

1. The website has users create an account to process and save their information
    - used a SQL database to manage users and their information
    - offer users the ability to save their emissions data and create new results forms

2. Users upload their carbon footprint data (energy usage, transportation, waste) via csv.
    - Any csv file size can be used, but needs to follow the conventions of
    ''' | Year | Catagory1 | Catagory2 | ... | CatagoryN | Total |'''

3. The data is cleaned, normalized, and scaled using Min-Max Scaling.

4. We implemented a Long Short-Term Memory (LSTM) neural network to forecast future emissions:
    - Business-As-Usual (BAU) trends
    - Optimized Reduction Strategies that suggest how to lower emissions

5. We generate data based on our ML model and return predictions and analysis back to the website.

6. We use linear regression to compute expected trends for each sector and a gradient-based sensitivity analysis identifies    which sector reductions will have the greatest impact.


## Contributing

Cloning and Pull requests are welcome. Form major changes, please open and issue first to discuss with the team what and why you'd like to change and contribute to this codebase.

Please be mindful of the project.

## License

[MIT](https://choosealicense.com/licenses/mit/)

