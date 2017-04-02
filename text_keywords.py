import json
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1, AlchemyLanguageV1

def speech_to_text(speech_file):

	make_into_text = SpeechToTextV1(
	    username='f87dd316-ab7c-4725-8df2-92756da072bb',
	    password='2Q4ovf33Quzp',
	    x_watson_learning_opt_out=False
	)

	with open(join(dirname(__file__), speech_file),
	          'rb') as audio_file:
		json_form = json.dumps(make_into_text.recognize(
	        audio_file, content_type='audio/wav', continuous=True, timestamps=True,
	        word_confidence=True),
	        indent=2)
		print(json_form)
		json_data = json.loads(json_form)
		json_results = json_data["results"]
		if len(json_results) == 0:
			return None
		text = ''
		for i in range(len(json_results)):
			text += json_results[i]["alternatives"][0]["transcript"]
		return text

def keywords(speech_text):

	if speech_text is None:
		return []

	alchemy_language = AlchemyLanguageV1(api_key='13789e5c96c9a0aecfaa20c4e4dd2731e60e026a')
	url = 'https://gateway-a.watsonplatform.net/calls'

	json_form = json.dumps(alchemy_language.keywords(max_items=6, text=speech_text))
	json_data = json.loads(json_form)
	if len(json_data["keywords"]) == 0:
		return []
	json_keywords = json_data["keywords"]
	keywords = []
	for i in json_keywords:
		keywords.append(i['text'])
	return keywords


if __name__ == '__main__':

	speech_wav = 'averywav.wav' #change
	text = speech_to_text(speech_wav)
	print(text)
	keyword_list = keywords(text)
	print(keyword_list)