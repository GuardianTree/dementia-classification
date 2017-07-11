from os import path
import os
import pickle
import re
import argparse
import sys
import nibabel as nb
import subprocess
import math

from pathos.multiprocessing import ProcessPool
from dementia_prediction.config_wrapper import Config
from dementia_prediction.data_input_new import DataInput
from dementia_prediction.cnn_baseline.baseline_balanced import CNN

# Parse the parameter file
config = Config()
parser = argparse.ArgumentParser(description="Run the Baseline model")
parser.add_argument("paramfile", type=str, help='Path to the parameter file')
args = parser.parse_args()
config.parse(path.abspath(args.paramfile))
params = config.config.get('parameters')
paths = config.config.get('data_paths')

IMG_SIZE = params['cnn']['depth']*params['cnn']['height']*params['cnn'][
            'width']

# All patients class labels dictionary and list of validation patient codes
patients_dict = pickle.load(open(paths['class_labels'], 'rb'))
valid_patients = pickle.load(open(paths['valid_data'], 'rb'))
train_patients = pickle.load(open(paths['train_data'], 'rb'))
print("Total number of patients:",  len(patients_dict),
      "Validation patients count: ", len(valid_patients),
      "Train patients count:", len(train_patients))
print(len(train_patients), len(valid_patients), len(set(train_patients+valid_patients)))
# If data is not normalized, we can normalize it on-the-fly
# Mean and Variance of the training data
global_mean = [0 for i in range(0, IMG_SIZE)]
global_variance = [0 for i in range(0, IMG_SIZE)]

# Paths to store the mean and variance
mean_path = paths['norm_mean_var']+'./'+params['cnn']['mode']+\
            '_train_mean_path.pkl'
var_path = paths['norm_mean_var']+'./'+params['cnn']['mode']+\
            '_train_var_path.pkl'

# Parallel processing functions for pathos client
def mean_fun(filenames):
    mean = [0 for x in range(0, IMG_SIZE)]
    for file in filenames:
        image = nb.load(file).get_data().flatten()
        for i in range(0, IMG_SIZE):
            mean[i] += image[i]
    return mean

def var_fun(filenames):
    variance = [0 for i in range(0, IMG_SIZE)]
    with open(mean_path, 'rb') as filep:
        global_mean = pickle.load(filep)
    for file in filenames:
        image = nb.load(file).get_data().flatten()
        for i in range(0, IMG_SIZE):
            variance[i] += math.pow((image[i] - global_mean[i]), 2)
    return variance

def normalize(train):
    train_data = train[0] + train[1]
    mean = [0 for i in range(0, IMG_SIZE)]
    var = [0 for i in range(0, IMG_SIZE)]
    num_parallel = 15
    split = int(len(train_data) / num_parallel)
    pool = ProcessPool(num_parallel)
    train_splits = []
    for par in range(0, num_parallel - 1):
        train_splits.append(train_data[par * split:(par + 1) * split])
    train_splits.append(train_data[(num_parallel - 1) * split:])

    if not os.path.exists(mean_path):
        mean_arrays = pool.map(mean_fun, train_splits)
        for i in range(0, IMG_SIZE):
            for j in range(0, len(mean_arrays)):
                mean[i] += mean_arrays[j][i]
        global_mean = [i/len(train_data) for i in mean]
        with open(mean_path, 'wb') as filep:
            pickle.dump(global_mean, filep)

    with open(mean_path, 'rb') as filep:
        global_mean = pickle.load(filep)

    if not os.path.exists(var_path):
        var_arrays = pool.map(var_fun, train_splits)
        for i in range(0, IMG_SIZE):
            for j in range(0, len(var_arrays)):
                var[i] += var_arrays[j][i]
        global_variance = [math.sqrt(x/(len(train_data)-1)) for x in var]
        with open(var_path, 'wb') as filep:
            pickle.dump(global_variance, filep)

    with open(var_path, 'rb') as filep:
        global_variance = pickle.load(filep)

    return global_mean, global_variance

s_train_filenames = []
p_train_filenames = []
s_valid_filenames = []
p_valid_filenames = []

"""
# Add Data Augmented with rotations and translations
for directory in os.walk(paths['datadir']):
    # Walk inside the directory
    for file in directory[2]:
        # Match all files ending with 'regex'
        input_file = os.path.join(directory[0], file)
        for rotation in ['x', 'y', 'z']:
            regex = r"-T1_translated_{0}_affine_corrected\.nii\.gz$".format(rotation)
            split_on = ''
            if re.search(regex, input_file):
                split_on = '-T1_translated_{0}_affine_corrected.nii.gz'.format(rotation)
            regex = r"-T1_brain_sub_rotation5_{0}\.nii\.gz$".format(rotation)
            if re.search(regex, input_file):
                split_on = '-T1_brain_sub_rotation5_{0}.nii.gz'.format(rotation)
            '''
            regex = r"-T1_brain_subsampled\.nii\.gz_sub_rot3_trans3_{0}\.nii\.gz$".format(
                rotation)
            if re.search(regex, input_file):
                split_on = '-T1_brain_subsampled.nii.gz_sub_rot3_trans3_{0}.nii.gz'.format(rotation)
            '''
            if split_on != '': # if input file matches any regex
                pat_code = input_file.rsplit(split_on)
                patient_code = pat_code[0].rsplit('/', 1)[1]
                if patient_code in patients_dict and patient_code not in \
                        valid_patients:
                    if patients_dict[patient_code] == 0:
                        s_train_filenames.append(input_file)
                    if patients_dict[patient_code] == 1:
                        p_train_filenames.append(input_file)
print("Stable:", len(s_train_filenames),
      "Progressive:", len(p_train_filenames))
# For Example: 166*6 stable and 180*6 progressive patients
"""

for directory in os.walk(paths['datadir']):
    # Walk inside the directory
    for file in directory[2]:
        # Match all files ending with 'regex'
        input_file = os.path.join(directory[0], file)
        regex = r""+params['regex']+"$"
        if re.search(regex, input_file):
            pat_code = input_file.rsplit(params['split_on'])
            patient_code = pat_code[0].rsplit('/', 1)[1]
            if patient_code in patients_dict and patient_code in train_patients:
                if patients_dict[patient_code] == 0:
                    s_train_filenames.append(input_file)
                if patients_dict[patient_code] == 1:
                    p_train_filenames.append(input_file)
            if patient_code in patients_dict and patient_code in valid_patients:
                if patients_dict[patient_code] == 0:
                    s_valid_filenames.append(input_file)
                    print(input_file)
                if patients_dict[patient_code] == 1:
                    p_valid_filenames.append(input_file)

print("Train Data: S: ", len(s_train_filenames), "P: ", len(p_train_filenames))
print("Validation Data: S: ", len(s_valid_filenames), "P: ", len(p_valid_filenames))

train = (s_train_filenames, p_train_filenames)
validation = (s_valid_filenames, p_valid_filenames)
'''
# Generate the normalized data on-fly
mean_norm, var_norm = normalize(train)
train_data = DataInput(params=config.config.get('parameters'), data=train,
                       name='train', mean=mean_norm, var=var_norm)
validation_data = DataInput(params=config.config.get('parameters'),
                            data=validation, name='valid', mean=mean_norm,
                            var=var_norm)
'''
train_data = DataInput(params=config.config.get('parameters'), data=train,
                       name='train', mean=0, var=0)
validation_data = DataInput(params=config.config.get('parameters'),
                            data=validation, name='valid', mean=0,
                            var=0)
# T1 baseline CNN model
cnn_model = CNN(params=config.config.get('parameters'))
cnn_model.train(train_data, validation_data, True)

