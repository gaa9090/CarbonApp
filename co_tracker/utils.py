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

# def get_plot(type_chart, result_by, data):
#     plt.switch_backend('AGG')
#     fig = plt.figure(figsize=(10,4))
#     plt.xticks(rotation = 45)
#     plt.title("The CO2 Tracker")
#     key = get_key(result_by)
#     data = data.groupby([key], as_index=False)['Amount'].agg('sum')
#     print(key)
#     if type_chart == '#1':
#         labels = data[key].values
#         plt.pie(data=data, x='Amount', labels=labels, shadow=True, startangle=90, autopct='%1.1f%%',wedgeprops={'edgecolor': 'black'})
#     elif type_chart == '#2':
#         sns.barplot(x=key, y='Amount', data=data, ci=None, palette='pastel')

#     else:  # Line chart
#             plt.xlabel(key)
#             plt.ylabel('Amount')
#             color = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#ff6700', '#4169E1', '#0FFF50']
#             plt.plot(data[key], data['Amount'], color=random.choice(color), linestyle="--", marker='o')

#     plt.tight_layout()
#     graph = setup_graph()
#     return graph





import matplotlib.pyplot as plt
import seaborn as sns
import random

def get_plot(type_chart, result_by, data):
    plt.switch_backend('AGG')
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))  # Two side-by-side plots
    plt.subplots_adjust(wspace=0.4)

    key = get_key(result_by)

    # Ensure 'New' column exists and contains boolean values
    if "New" not in data.columns:
        print("Error: 'New' column not found in data")
        return None

    # Convert to boolean in case of data type mismatch
    data["New"] = data["New"].astype(bool)

    # Split data into new and old
    new_data = data[data["New"] == True].groupby([key], as_index=False)['Amount'].sum()
    
    old_data = data[data["New"] == False].groupby([key], as_index=False)['Amount'].sum()

    # Debugging prints
    print("New Data:\n", new_data)
    print("Old Data:\n", old_data)

    color_palette = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#ff6700', '#4169E1', '#0FFF50']

    # Plot New Data
    ax = axes[0]
    ax.set_title("New CO2 Data")
    if new_data.empty:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=12, color='red')
    elif type_chart == '#1':
        ax.pie(new_data['Amount'], labels=new_data[key], shadow=True, startangle=90, autopct='%1.1f%%',
               wedgeprops={'edgecolor': 'black'})
    elif type_chart == '#2':
        sns.barplot(x=key, y='Amount', data=new_data, ci=None, palette='pastel', ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    else:  # Line chart
        ax.set_xlabel(key)
        ax.set_ylabel('Amount')
        ax.plot(new_data[key], new_data['Amount'], color=random.choice(color_palette), linestyle="--", marker='o')

    # Plot Old Data
    ax = axes[1]
    ax.set_title("Old CO2 Data")
    if old_data.empty:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=12, color='red')
    elif type_chart == '#1':
        ax.pie(old_data['Amount'], labels=old_data[key], shadow=True, startangle=90, autopct='%1.1f%%',
               wedgeprops={'edgecolor': 'black'})
    elif type_chart == '#2':
        sns.barplot(x=key, y='Amount', data=old_data, ci=None, palette='pastel', ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    else:  # Line chart
        ax.set_xlabel(key)
        ax.set_ylabel('Amount')
        ax.plot(old_data[key], old_data['Amount'], color=random.choice(color_palette), linestyle="--", marker='o')

    plt.tight_layout()
    graph = setup_graph()
    return graph





# def get_plot(type_chart, result_by, data):
#     plt.switch_backend('AGG')
#     fig, axes = plt.subplots(1, 2, figsize=(12, 4))  # Two side-by-side plots
#     plt.subplots_adjust(wspace=0.4)

#     key = get_key(result_by)

#     # Split data into new and old
#     new_data = data[data["New"] == True].groupby([key], as_index=False)['Amount'].agg('sum')
#     old_data = data[data["New"] == False].groupby([key], as_index=False)['Amount'].agg('sum')

#     color_palette = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#ff6700', '#4169E1', '#0FFF50']

#     # New Data Chart
#     ax = axes[0]
#     ax.set_title("New CO2 Data")
#     if type_chart == '#1':
#         ax.pie(new_data['Amount'], labels=new_data[key], shadow=True, startangle=90, autopct='%1.1f%%',
#                wedgeprops={'edgecolor': 'black'})
#     elif type_chart == '#2':
#         sns.barplot(x=key, y='Amount', data=new_data, ci=None, palette='pastel', ax=ax)
#         ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
#     else:  # Line chart
#         ax.set_xlabel(key)
#         ax.set_ylabel('Amount')
#         ax.plot(new_data[key], new_data['Amount'], color=random.choice(color_palette), linestyle="--", marker='o')

#     # Old Data Chart
#     ax = axes[1]
#     ax.set_title("Old CO2 Data")
#     if type_chart == '#1':
#         ax.pie(old_data['Amount'], labels=old_data[key], shadow=True, startangle=90, autopct='%1.1f%%',
#                wedgeprops={'edgecolor': 'black'})
#     elif type_chart == '#2':
#         sns.barplot(x=key, y='Amount', data=old_data, ci=None, palette='pastel', ax=ax)
#         ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
#     else:  # Line chart
#         ax.set_xlabel(key)
#         ax.set_ylabel('Amount')
#         ax.plot(old_data[key], old_data['Amount'], color=random.choice(color_palette), linestyle="--", marker='o')

#     plt.tight_layout()
#     graph = setup_graph()
#     return graph





# def get_plot(type_chart, result_by, data):
#     plt.switch_backend('AGG')
#     fig = plt.figure(figsize=(10, 4))
#     plt.xticks(rotation=45)
#     plt.title("The CO2 Tracker")

#     # Group the data by the appropriate column
#     key = get_key(result_by)
#     data = data.groupby([key, 'is_new'], as_index=False)['Amount'].agg('sum')

#     # Check the chart type
#     if type_chart == '#1':  # Pie chart
#         labels = data[key].values
#         isnew_groups = data['is_new'].unique()
        
#         # Create pie chart with separate legends for `isnew` categories
#         for group in isnew_groups:
#             group_data = data[data['is_new'] == group]
#             plt.pie(group_data['Amount'], labels=group_data[key], 
#                     shadow=True, startangle=90, autopct='%1.1f%%', 
#                     wedgeprops={'edgecolor': 'black'}, labeldistance=1.15)
        
#         plt.legend(isnew_groups, title='is_new', loc='best')
        
#     elif type_chart == '#2':  # Bar chart
#         sns.barplot(x=key, y='Amount', hue='is_new', data=data, ci=None)
#         plt.legend(title='is_new')
        
#     else:  # Line chart
#         color = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#ff6700', '#4169E1', '#0FFF50']
#         is_new_groups = data['is_new'].unique()
        
#         for group in is_new_groups:
#             group_data = data[data['is_new'] == group]
#             plt.plot(group_data[key], group_data['Amount'], 
#                     color=random.choice(color), linestyle="--", marker='o', label=str(group))
        
#         plt.legend(title='isnew')

#     plt.tight_layout()
#     graph = setup_graph()  # Assuming this function is defined elsewhere
#     return graph



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