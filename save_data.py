import os
import shutil
import json

#arg 1 is string of name
#arg 2 is string of json


def addImageInfoToDatabase(image_name, json_data):
	arg_name = image_name
	arg_json = json_data
	current_dir = os.path.dirname(os.path.realpath(__file__))
	data_path = os.path.join(current_dir, "database")
	image_path = os.path.join(data_path, "images")
	json_path = os.path.join(data_path, "json")

	name_list = os.listdir(image_path)
	name_numbers = []
	for i in name_list:
		if i == ".DS_Store":
			continue
		j = i.split("image")[1]
		k = j.split(".")[0]
		name_numbers.append(k)

	next_number = 0
	while True:
		if str(next_number) not in name_numbers:
			break
		next_number += 1

	new_image_path = os.path.join(image_path, "image" + str(next_number) + ".jpg")
	new_json_path = os.path.join(json_path, "json" + str(next_number) + ".txt")

	#save json file
	text_file = open(new_json_path, "w")
	text_file.write(str(arg_json))
	text_file.close()

	#copy image file
	shutil.copyfile(os.path.join(current_dir, arg_name), new_image_path)

addImageInfoToDatabase("image0.jpg", {"some":"json", "file":"lol"})