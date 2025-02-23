from lib import main


def run_ai(file_path, start_year, go_up_year):
    file_name_1 = None
    try:
        main_object = main.root(file_path, start_year, go_up_year)
        file_name_1 = main_object.generate_predictions()
        print("Calling generate_predictions()...")
    except AttributeError as e:
        print(f"AttributeError occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return file_name_1


# def run_ai(file_path, start_year, go_up_year):
#     _image = None
#     try:
#         main_object = main.root(file_path, start_year, go_up_year)
#         _image = main_object.generate_predictions()
#         print("Calling generate_predictions()...")
#     except AttributeError as e:
#         print(f"AttributeError occurred: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     # print(f"{file_name} ---- file_name - Test")
#     return _image
    



    

