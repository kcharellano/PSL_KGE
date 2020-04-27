#!bin/usr/env python3

import json
import os
import shutil
import sys

from rule_generation import generate_rules

PSL = "psl"
DATA = "data"
CLI = "cli"
KGE = "kge"
DATA_FILE = "data.txt"
ENTITY_MAP = "entity_map.txt"
RELATION_MAP = "relation_map.txt"
TRAIN = "train.txt"
TEST = "test.txt"
NEG_TRAIN = "_negative_train.txt"
TRUE_BLOCK = "trueblock_obs.txt"
FALSE_BLOCK = "falseblock_obs.txt"
ENTITYDIM = "entitydim"
RELATIONDIM = "relationdim"
TARGET = "_target.txt"
RULES_PSL = "kge.psl"
DATA_PSL = "kge.data"
EVAL = "eval"
LEARN = "learn"

ENTITY_1 = 0
ENTITY_2 = 2
RELATION = 1
SIGN = 3

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), DATA)
PSL_DIR = os.path.join(os.path.dirname(BASE_DIR), PSL)
PSL_DATA_DIR = os.path.join(PSL_DIR, DATA)
CLI_DIR = os.path.join(PSL_DIR, CLI)
DATA_KGE_DIR = os.path.join(PSL_DATA_DIR, KGE)

def main(dataset_name, dim_num, split_num):
    dataset_dir = os.path.join(os.path.dirname(BASE_DIR), dataset_name)
    dataset_splits_dir = os.path.join(RAW_DATA_DIR, dataset_name)

    # Create mapping files and return mappings
    entity_map, relation_map = create_mapping_files(dataset_dir)

    # Loop through data splits
    for split_num in range(0, split_num):
        mapped_split_dir = os.path.join(DATA_KGE_DIR, str(split_num))
        raw_split_dir = os.path.join(dataset_splits_dir, str(split_num))
        split_eval_dir = os.path.join(mapped_split_dir, EVAL)
        split_learn_dir = os.path.join(mapped_split_dir, LEARN)

        # Create/replace directories
        makedir(mapped_split_dir)
        makedir(split_eval_dir)
        makedir(split_learn_dir)

        # Separate positive and negative triples from train file
        mapped_pos_train_triples, mapped_neg_train_triples = separate_triples(raw_split_dir, entity_map, relation_map)

        # Create trueblock_obs & falseblock_obs
        write_data(mapped_pos_train_triples, os.path.join(split_eval_dir, TRUE_BLOCK))
        write_data(mapped_neg_train_triples, os.path.join(split_eval_dir, FALSE_BLOCK))

        # Target files contain only entities and relations present in current split
        create_target_files(mapped_pos_train_triples, split_eval_dir)

        # Generate and write rules
        psl_rules_target = os.path.join(CLI_DIR, RULES_PSL)
        psl_predicates_target = os.path.join(CLI_DIR, DATA_PSL)
        rules, predicates = generate_rules(dim_num)
        write_data(rules, psl_rules_target)
        write_data(predicates, psl_predicates_target)

# Create mapping files and return entity map and relation map
def create_mapping_files(dataset_dir):
    all_triples = load_helper(os.path.join(dataset_dir, DATA_FILE))
    ent_mapping, rel_mapping = map_constituents(all_triples)
    makedir(DATA_KGE_DIR)
    # Key = raw_ent/raw_rel
    # Val = mapping
    write_data([[ent_mapping[entity], entity] for entity in ent_mapping], os.path.join(DATA_KGE_DIR, ENTITY_MAP))
    write_data([[rel_mapping[relation], relation] for relation in rel_mapping], os.path.join(DATA_KGE_DIR, RELATION_MAP))

    return ent_mapping, rel_mapping

def separate_triples(raw_split_dir, entity_map, relation_map):
    triple_list = load_helper(os.path.join(raw_split_dir, TRAIN))

    true_triples = []
    false_triples = []
    for triple in triple_list:
        if int(triple[SIGN]):
            true_triples.append(map_raw_triple(triple, entity_map, relation_map))
        else:
            false_triples.append(map_raw_triple(triple, entity_map, relation_map))
    return true_triples, false_triples

def create_target_files(mapped_triple_list, split_eval_dir):
    target_entities = set()
    target_relations = set()

    # Set target entites and target relations
    for triple in mapped_triple_list:
        if not triple[ENTITY_1] in target_entities:
            target_entities.add(triple[ENTITY_1])
        if not triple[ENTITY_2] in target_entities:
            target_entities.add(triple[ENTITY_2])
        if not triple[RELATION] in target_relations:
            target_relations.add(triple[RELATION])

    target_entities = list(target_entities)
    target_relations = list(target_relations)

    # Create dimension target files
    for dimension in range(1, dim_num + 1):
        entity_dim_target_file = os.path.join(split_eval_dir, ENTITYDIM + str(dimension) + TARGET)
        relation_dim_target_file = os.path.join(split_eval_dir, RELATIONDIM + str(dimension) + TARGET)
        write_data(target_entities, entity_dim_target_file)
        write_data(target_relations, relation_dim_target_file)

# Writes a list of data to a file
def write_data(data, file_path):
    with open(file_path, 'w+') as out_file:
        # if list is empty
        if not data:
            return
        # if list of lists
        elif isinstance(data[0], list):
            out_file.write('\n'.join(["\t".join(current_list) for current_list in data]))
        # else regular list
        else:
            out_file.write('\n'.join(data))

# Return list of triples from filename
def load_helper(data_file):
    helper = []
    with open(data_file, 'r') as file_ptr:
        for line in file_ptr:
            helper.append(line.strip('\n').split('\t'))

    return helper

# Map entities and relations to integers
def map_constituents(triple_list):
    entity_map = {}
    relation_map = {}
    entity_count = 0
    relation_count = 0
    for triple in triple_list:
        if not triple[ENTITY_1] in entity_map:
            entity_map[triple[ENTITY_1]] = str(entity_count)
            entity_count += 1
        if not triple[RELATION] in relation_map:
            relation_map[triple[RELATION]] = str(relation_count)
            relation_count += 1
        if not triple[ENTITY_2] in entity_map:
            entity_map[triple[ENTITY_2]] = str(entity_count)
            entity_count += 1

    return entity_map, relation_map

def makedir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

# Helper methods create a list for write_data()
def map_raw_triple(raw_triple, ent_map, rel_map):
    return [ent_map[raw_triple[ENTITY_1]], rel_map[raw_triple[RELATION]], ent_map[raw_triple[ENTITY_2]]]

# Return positive and negative triples in separate lists
# Note: SIGN==0 means false triple


def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h','help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <config.json>" % executable, file = sys.stderr)
        sys.exit(1)

    config_file = args.pop(0)
    with open(config_file, 'r') as config_fd:
        config = json.load(config_fd)

    dataset_name = config["dataset"]
    dim_num = config["dimensions"]
    split_num = config["splits"]

    return dataset_name, dim_num, split_num

if __name__ == '__main__':
    dataset_name, dim_num, split_num = _load_args(sys.argv)
    main(dataset_name, dim_num, split_num)
