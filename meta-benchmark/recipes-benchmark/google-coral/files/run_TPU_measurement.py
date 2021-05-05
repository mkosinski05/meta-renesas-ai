#!/usr/bin/env python2

'''
Copyright (C) 2020 Renesas Electronics Corp.
This file is licensed under the terms of the MIT License
This program is licensed "as is" without any warranty of any
kind, whether express or implied.

Script based on
meta-benchmark/recipes-benchmark/tensorflow-lite/run_TF_measurement.py

Model list files (parameter 1) should contain a list of model names and their
corresponding labels file name. E.g.
mobilenet_v2_1.0_224_inat_insect_quant_edgetpu.tflite inat_insect_labels.txt
mobilenet_v2_1.0_224_inat_plant_quant_edgetpu.tflite inat_plant_labels.txt
mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite inat_bird_labels.txt

Model and label files should be in the same directory
'''

import sys
import os
import commands
import subprocess
from subprocess import call
import numpy as np

def main():
	print("Google Coral TPU Benchmark App")

	if len(sys.argv) != 4:
		print("Invalid parameters")
		print("Example python run_TPU_measurement.py test_file_list_Resnet.txt /home/root/models/google-coral/Resnet 30")
		sys.exit(1)

	filepath = sys.argv[1]
	if not filepath:
		print("Need to provide model list file")
		sys.exit(1)

	if not os.path.isfile(filepath):
		print("File path {} does not exist. Exiting...".format(filepath))
		sys.exit(1)

	base_directory_path = sys.argv[2]+"/"

	number_of_iteration = int(sys.argv[3])

	with open(filepath) as fp:
		for line in fp:
			if not len(line.strip()) == 0:
				model_details = line.split()
				list = []
				list_tmp = []

				if len(model_details) != 3:
					print("Invalid line: " + line)
					sys.exit(1)

				model_name = model_details[0]
				label_file = model_details[1]
				model_type = model_details[2]

				if not os.path.isfile(base_directory_path + model_name):
					print("Model {} does not exist. Exiting...".format(base_directory_path + model_name))
					sys.exit(1)

				if not os.path.isfile(base_directory_path + label_file):
					print("Label file {} does not exist. Exiting...".format(base_directory_path + label_file))
					sys.exit(1)

				run_label_image(model_name, base_directory_path, label_file, number_of_iteration, list_tmp, list)

				print("Average Time" + " at Model " + model_name + " "+ str(Average(list_tmp)) + " ms ")
				print("Standard Deviation" + " at Model " + model_name + " " + str(Average(list)))

				print("AI_BENCHMARK_MARKER,Google Coral TPU frogfish: TensorFlow Lite," + model_name.rstrip() + "," + model_type.rstrip() + "," + str(Average(list_tmp)) + "," + str(Average(list)) + ",")
				print('')

def Average(lst):
	return sum(lst) / len(lst)

def run_label_image(model_file_name, base_directory, label_file_name, times_to_run, list, list_dev):
	command = "/usr/bin/google-coral-benchmark/google-coral-tpu-benchmark -i /usr/bin/google-coral/images/grace_hopper_224_224.bmp -c %s -l %s -m %s" % (times_to_run, label_file_name, base_directory+model_file_name)

	for line in run_command(command):
		count = 0
		if line.find("Average Time") != -1:
			line = line.split(" ")
			list.insert(count, float(line[3]))
			count = count + 1
		elif line.find("Standard Deviation") != -1:
			line = line.split(" ")
			list_dev.insert(count, float(line[2]))


def run_command(command):
	p = subprocess.Popen(command,shell=True,
			     stdout=subprocess.PIPE,
			     stderr=subprocess.STDOUT)
	return iter(p.stdout.readline, b'')

if __name__ == '__main__':
	main()
