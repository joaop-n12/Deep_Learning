
import streamlit as st
import pandas as pd
import cv2
import os
from PIL import Image, ImageDraw
from deepface import DeepFace
import json


def load_image(image_file):
	img = Image.open(image_file)
	return img

def deep_face_find(file, json_data):
	dfs = DeepFace.find(img_path=file, db_path='rosto-conhecido')
	if len(dfs):
		df = dfs[0]
		if len(df):
			identity = df.loc[0, 'identity']
			name, ext = os.path.splitext(os.path.basename(identity))
			if name in json_data:
				st.write("Rosto encontrado:", json_data[name])
				return True
	return False


def deep_face_extract(file, json_data):
	face_objs = DeepFace.extract_faces(img_path=file, detector_backend='opencv', align=True, enforce_detection=True)
	image = Image.open(file)
	st.write('Rostos reconhecidos:', len(face_objs))
	for face in face_objs:
		draw = ImageDraw.Draw(image)
		top_left = (face['facial_area']['x'], face['facial_area']['y'])
		bottom_right = (
		face['facial_area']['x'] + face['facial_area']['w'], face['facial_area']['y'] + face['facial_area']['h'])
		draw.rectangle([top_left, bottom_right], outline="red", width=2)

		name, extension = os.path.splitext(file)
		index = next_index('rosto-desconhecido')
		new_file_name = os.path.join('rosto-desconhecido', f"{index}{extension}")

		cropped_image = image.crop([*top_left, *bottom_right])
		cropped_image.save(new_file_name)

		if deep_face_find(new_file_name, json_data):
			os.remove(new_file_name)

def next_index(folder):
	files = os.listdir(folder)
	indexes = [0]
	for file in files:
		name, extension = os.path.splitext(file)
		if extension != '.pkl':
			indexes.append(int(name))
	return max(indexes) + 1


def save_js(json_file, data):
	json_data = json.dumps(data)
	with open(json_file, 'w') as f:
		f.write(json_data)

def main():
	# Initialize a session state variable
	# if 'file' not in st.session_state:
	# 	st.session_state.counter = 0

	json_file = 'data.json'
	with open(json_file, 'r') as file:
		json_data = json.load(file)
	save_js(json_file, json_data)

	menu = ["Nova Imagem","Ver album","Rotular rosto", "Outros"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Nova Imagem":
		image_file = st.file_uploader("Upload Files",type=['png','webp','jpeg'])
		if image_file is not None:
			name, extension = os.path.splitext(image_file.name)
			index = next_index('album')
			new_file_name = os.path.join('album', str(index) + str(extension))
			st.image(load_image(image_file), width=250)
			with open(new_file_name,"wb") as f:
				f.write((image_file).getbuffer())
			st.success("File Saved")

			deep_face_extract(new_file_name, json_data)

	elif choice == "Ver album":
		images = []
		for filename in os.listdir("album"):
			filename = os.path.join("album",filename)
			img = Image.open(filename)
			if img is not None:
				st.image(img, width=250)
				st.write(filename)

	elif choice == "Rotular rosto":
		files = os.listdir('rosto-desconhecido')
		if len(files) == 0:
			st.write("Sem novos rostos para rotular")
		for filename in files:
			filename = os.path.join("rosto-desconhecido",filename)
			img = Image.open(filename)
			if img is not None:
				st.image(img, width=250)
				name, ext = os.path.splitext(os.path.basename(filename))
				rotulo = st.text_input("Rótulo", key=name)
				if len(rotulo):
					index = next_index('rosto-conhecido')
					new_file_name = os.path.join('rosto-conhecido', str(index) + str(ext))
					os.rename(filename, new_file_name)
					json_data[str(index)] = rotulo
					save_js(json_file, json_data)
					st.rerun()

	elif choice == "Outros":
			st.subheader("Ver Imagens")
			st.title("Hello World!!")
			# Header
			st.header("Hello World!! (small)")

			# Subheader
			st.subheader("Hello World!! (smaller)")
			st.text("Simple Text")

			# Status messages
			st.success("Success")
			st.info("Information")
			st.warning("Warning")
			st.error("Error")
			st.checkbox('Yes')
			if st.button('Click Me'):
				st.success("Uia!")

			title = st.text_input("Movie title")
			st.write("The current movie title is", title)

			st.radio('Pick your gender', ['Male', 'Female'])
			st.selectbox('Pick a fruit', ['Apple', 'Banana', 'Orange'])
			st.multiselect('Choose a planet', ['Jupiter', 'Mars', 'Neptune'])
			st.select_slider('Pick a mark', ['Bad', 'Good', 'Excellent'])
			number = st.slider('Pick a number', 0, 50)
			if number:
				st.success(number)

			if st.checkbox("Show/Hide"):
				st.text("something")

			status = st.radio("Select Gender: ", ('Male', 'Female'))
			if (status == 'Male'):
				st.success("Male")
			else:
				st.success("Female")

			hobby = st.selectbox("Hobbies: ", ['Dancing', 'Reading', 'Sports'])
			st.write("Your hobby is: ", hobby)

			name = st.text_input("Enter Your name", "Type Here ...")
			if(st.button('Submit')):
				result = name.title()
				st.success(result)


main()
