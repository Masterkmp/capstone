import argparse
import json
from os.path import join

import numpy as np
import torch
from torch.utils.data import DataLoader

from dataset import NewsDataset, train_path, test_path, dev_path, device
from model import *
from train_eval import *

seed = 1
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)


def parse():
    parse = argparse.ArgumentParser()
    parse.add_argument('--config', type=str, required=True,
                       help='The path of configuration file')
    args = parse.parse_args()
    with open(args.config, 'r') as f:
        args = json.load(f)
    return args


def main():
    args = parse()

    model_path = join(args['output_path'], 'model.pkl')
    for_bert = False

    if args['type'] == "TextCNN":
        net = TextCNN(args['embedding_len'])
    elif args['type'] == "FastText":
        net = FastText(args['embedding_len'], args['padding_len'])
    elif args['type'] == "TextRCNN":
        net = TextRCNN(args['embedding_len'])
    elif args['type'] == "TextRNN":
        net = TextRNN(args['embedding_len'])
    elif args['type'] == "DPCNN":
        net = DPCNN(args['embedding_len'])
    elif args['type'] == "BERT":
        net = BERT()
        for_bert = True
    else:
        raise ValueError

    net.to(device)

    if args['load'] == 1:
        net.load_state_dict(torch.load(model_path))

    if args['num_epochs'] > 0:
        train_set = NewsDataset(train_path, args['padding_len'], for_bert)
        dev_set = NewsDataset(dev_path, args['padding_len'], for_bert)
        train_data_loader = DataLoader(
            train_set, batch_size=args['batch_size'], shuffle=True)
        dev_data_loader = DataLoader(
            dev_set, batch_size=args['batch_size'], shuffle=False)

        best_net = train(args, net, train_data_loader, dev_data_loader)

        torch.save(best_net, model_path)
        net.load_state_dict(best_net)

    test_data = NewsDataset(test_path, args['padding_len'], for_bert)
    test_data_loader = DataLoader(
        dataset=test_data, batch_size=args['batch_size'], shuffle=False)
    test(net, test_data_loader)


if __name__ == '__main__':
    main()
