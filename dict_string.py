import ast

def dict_to_string(json_dict):
	json_dict = ast.literal_eval(json_dict)
	string = ''
	for i in json_dict:
		string += i
		string += ':'
		if type(json_dict[i]) is list:
			string += '['
			for j in json_dict[i]:
				string += j
				string += ','
			string = string[:-1]
			string += ']'
		elif type (json_dict[i]) is str:
			string += json_dict[i]
		string += ';'
	string = string[:-1]
	return string

#x = dict_to_string('{"name": ["Ahaha","yup"], "date": "April 2nd", "location": "Princeton, NJ", "image_name": "image0.jpg", "tags": ["AHAHDUD", "afds", "asdfasd"]}')
#print(x)

def string_to_dict(json_string):
	diction = {}
	elements = json_string.split(';')
	for i in elements:
		keys_values = i.split(':')
		if keys_values[1][0] == '[':
			temp = keys_values[1][1:-1]
			objs = temp.split(',')
			diction[keys_values[0]] = objs
		else:
			diction[keys_values[0]] = keys_values[1]
	return str(diction)

#y = string_to_dict(x)
#print(y)



