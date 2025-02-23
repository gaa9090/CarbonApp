import base64
import random
from .models import Tracker, Category
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def get_plot_image(filename):
    _, the_image = filename.split(';base64')
    decode_image = base64.b64decode(the_image)
    plot_name = str(uuid.uuid4())[:8].replace('-', '').upper() + '.png'
    data = ContentFile(decode_image, name=plot_name)
    return data

def get_name_from_id(value):
    name = Tracker.objects.get(id=value)
    return name

def setup_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    the_graph = buffer.getvalue()
    graph = base64.b64encode(the_graph)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(type_chart, result_by, data):
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(10,4))
    plt.xticks(rotation = 45)
    plt.title("The CO2 Tracker")
    key = get_key(result_by)
    data = data.groupby(key, as_index=False)['Amount'].agg('sum')
    print(key)
    if type_chart == '#1':
        labels = data[key].values
        plt.pie(data=data, x='Amount', labels=labels, shadow=True, startangle=90, autopct='%1.1f%%',wedgeprops={'edgecolor': 'black'})
    elif type_chart == '#2':
        sns.barplot(x=key, y='Amount', data=data, ci=None)
    else:
        plt.xlabel(key)
        plt.ylabel('Date')
        color = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#ff6700', '#4169E1', '#0FFF50']
        plt.plot(data[key], data['Amount'], color=random.choice(color), linestyle="--", marker='o')
    plt.tight_layout()
    graph = setup_graph()
    return graph

# def get_category_name_from_id(value):
#     return Category.objects.get(id = value)

def get_category_name_from_id(value):
    try:
        # Retrieve only the category title or any other attribute you need.
        category = Category.objects.get(id=value)
        return category.title  # Or another field like category.name, if needed
    except Category.DoesNotExist:
        return None  # R

def get_key(result_by):
    if result_by == '#1':
        key = 'Year'
    else:
        key = 'Category'
    return key