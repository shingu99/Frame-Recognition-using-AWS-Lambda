import csv
import os
import urllib
#
import face_recognition
import pickle
import numpy as np
import boto3
from boto3 import client as boto3_client
import pickle
#
input_bucket = "546proj2inputtrinity"
output_bucket = "546proj2outputtrinity"
AWS_ACCESS_KEY = "AKIAY6MI7NBZ6EVPEWOD"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
#
# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data
#
def face_recognition_handler(event, context):

	print("Inside face_recognition_handler")
	image_file_Path = DownloadFromS3AndStoreInTemp(event,context)
	#data = open_encoding('encoding.dat')
	charRecognized = recognizeImage(image_file_Path)
	print("char Recognized is " + charRecognized)
	dataFromDynamoDB = ExtractDataFromDynamoDB(charRecognized)
	print("data year: ",dataFromDynamoDB['year']," data major: ", dataFromDynamoDB['major'])

	CreateCSV(urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8') , dataFromDynamoDB['name'], dataFromDynamoDB['major'] , dataFromDynamoDB['year'])
	print("The END!")


def recognizeImage(image_file_Path):
	print("Inside recognizeImage")
	filename = image_file_Path
	# Load face encodings
	with open("encoding.dat", 'rb') as f:
		all_face_encodings = pickle.load(f)
	print("Pickle File Loaded")
	face_names = list(all_face_encodings.keys())
	face_encodings = np.array(list(all_face_encodings.values()))

	face_names = face_encodings[0]
	face_encodings = all_face_encodings['encoding']
	unknown_image = face_recognition.load_image_file(filename)
	print("after unknown image")
	unknown_image_encoding = face_recognition.face_encodings(unknown_image)[0]
	# unknown_face = face_recognition.face_encodings(unknown_image)
	print("after unknown face")
	result = face_recognition.compare_faces(face_encodings, unknown_image_encoding)
	print("after result")
	print("result",result)
	# Print the result as a list of names with True/False
	names_with_result = list(zip(face_names, result))
	for i in names_with_result:
		if i[1] == True:
			return i[0]
	print("Nothing is true here",names_with_result)

def DownloadFromS3AndStoreInTemp(event, context):
	print("Inside DownloadFromS3AndStoreInTemp")
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')


	s3_client = boto3.client('s3', region_name=AWS_REGION)
	print("S3 Client Created")
	path = "/tmp/"
	video_file_path = path + key
	print("Video File Path"+video_file_path)

	response = s3_client.get_object(Bucket=bucket, Key=key)
	print("Got Response from s3 client")
	s3_client.download_file(bucket, key, video_file_path)
	print("Downloaded files ", os.listdir(path))
	os.system(
		"ffmpeg -i " + str(video_file_path) + " -vframes 1 " + str(path) + "image-%03d.jpeg")
	image_file_Path = path +"image-001.jpeg"
	return image_file_Path
	print("Frames stored in"+os.listdir(path))

	return response

def ExtractDataFromDynamoDB(charRecognized):

	dynamodb_resource = boto3.resource('dynamodb')
	dynamodb_table_name = 'trinityTable2'
	print("entering data get in dynamodb")
	table = dynamodb_resource.Table(dynamodb_table_name)
	data = table.get_item(
		Key={
			'name': charRecognized
		}
	)
	z = data['Item']
	print("DynamoDB result: " + str(z['year']))
	return z

def CreateCSV(videoName, name, major, year):
	videoName = videoName[:-4]
	print("VideoName: ", videoName)
	path = '/tmp/' + videoName+'.csv'
	print("path: ", path)
	print("opening")
	with open(path,"w") as csvfile:
		temp_csv_file = csv.writer(csvfile, delimiter=',', quoting = csv.QUOTE_MINIMAL)
		temp_csv_file.writerow(['Name','Major','Year'])
		temp_csv_file.writerow([name,major,year])
	print("after opening")
	s3_client = boto3.client('s3', region_name=AWS_REGION)
	s3_client.upload_file(
		Bucket = output_bucket,
		Filename = path,
		Key = videoName+'.csv'
	)

	os.remove(path)

# if __name__ == "__main__":
# 	CreateCSV("test_0", "Kartik","CSE","1996")