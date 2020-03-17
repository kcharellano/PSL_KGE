#!bin/usr/env python3

import os
import sys
import json
import math
import random


# Get command line arguments
# datafile contains all data to be split
data_file = sys.argv[1]
config_file = sys.argv[2]

# Read datafile and config file
with open(data_file, 'r') as df, open(config_file, 'r') as cf:
    config = json.load(cf)
    data = []
    entities = set()
    for line in df:
        # todo: split on tab or space?
        data.append(line.strip('\n').split('\t'))
        entities.add(line.strip('\n').split('\t')[2])
    entity_list = list(entities)

# Extract necessary variables to be able to create k splits
split_num = config["splits"]
seed = config["seed"]
percent_train = config["percent_train"]/100
percent_test = round(1 - percent_train, 2)
data_len = len(data)
train_bound = math.floor(percent_train * data_len)
false_triple_ratio =  config["false_triples_ratio"]

# Create splits directory
current_dir = os.path.dirname(os.path.realpath(__file__))
sub_dir = os.path.join(current_dir, "../splits")
os.mkdir(sub_dir)

# Set seed
random.seed(seed)
# Split data and write into data directory
for i in range(1, split_num+1):
    random.shuffle(data)
    train_file = 'split' + str(i) + '_' + 'train' + '.txt'
    test_file = 'split' + str(i) + '_' + 'test' + '.txt'
    neg_test_file = 'split' + str(i) + '_' + 'negative_test' + '.txt'
    neg_train_file = 'split' + str(i) + '_' + 'negative_train' + '.txt'
    train_path = os.path.join(sub_dir, train_file)
    test_path = os.path.join(sub_dir, test_file)
    neg_test_path = os.path.join(sub_dir, neg_test_file)
    neg_train_path = os.path.join(sub_dir, neg_train_file)
    with open(train_path, 'w+') as train, open(test_path, 'w+') as test, open(
    neg_test_path, 'w+') as neg_test,  open(neg_train_path, 'w+') as neg_train:
        # Fill train data
        for line in range(0, train_bound):
            train.write(data[line][0] + '\t' + data[line][1] + '\t' + data[line][2] + '\n')
            #Generate Negative Triples
            current_negative_triples = [data[line][2]]
            for _ in range(0, false_triple_ratio):
                negative_entity = random.choices(entity_list)
                while negative_entity[0] in current_negative_triples:
                    negative_entity = random.choices(entity_list)
                current_negative_triples.append(negative_entity[0])
                neg_train.write(data[line][0] + '\t' + data[line][1] + '\t'+ negative_entity[0] + '\n')

        for line in range(train_bound, data_len):
            test.write(data[line][0] + '\t' + data[line][1] + '\t' + data[line][2] + '\n')
            current_negative_triples = [data[line][2]]
            for _ in range(0, false_triple_ratio):
                negative_entity = random.choices(entity_list)
                while negative_entity[0] in current_negative_triples:
                    negative_entity = random.choices(entity_list)
                current_negative_triples.append(negative_entity[0])
                neg_test.write(data[line][0] + '\t' + data[line][1] + '\t'+ negative_entity[0] + '\n')
