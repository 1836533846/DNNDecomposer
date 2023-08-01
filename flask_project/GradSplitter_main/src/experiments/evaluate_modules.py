import argparse
import sys
import torch
# sys.path.append('')
# sys.path.append('..')
from GradSplitter_main.src.utils.configure_loader import load_configure
from GradSplitter_main.src.utils.model_loader import load_trained_model
from GradSplitter_main.src.utils.module_tools import load_module, module_predict
from GradSplitter_main.src.utils.dataset_loader import get_dataset_loader
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def evaluate_module_f1(module, dataset, target_class):
    outputs, labels = module_predict(module, dataset)
    predicts = (outputs > 0.5).int().squeeze(-1)
    labels = (labels == target_class).int()

    precision = torch.sum(predicts * labels) / torch.sum(predicts)
    recall = torch.sum(predicts * labels) / torch.sum(labels)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1


def main_func(args):
    estimator_idx = args.estimator_idx
    print(f'Estimator {estimator_idx}')
    print('-' * 80)

    configs = load_configure(args.model, args.dataset)
    configs.set_estimator_idx(estimator_idx)

    dataset_dir = configs.dataset_dir
    load_dataset = get_dataset_loader(args.dataset)
    trained_model = load_trained_model(configs.model_name, configs.num_classes, configs.trained_model_path)
    module_path = configs.best_module_path

    # evaluate each module
    for i in range(configs.num_classes):
        module = load_module(module_path, trained_model, i)
        module_eval_dataset, _ = load_dataset(dataset_dir, is_train=False, shuffle_seed=None, is_random=None)
        result = evaluate_module_f1(module, module_eval_dataset, i)
        print(f'{result:.4f}')

def get_args(model,dataset,estimator_idx):
    args = argparse.Namespace()
    args.model = model
    args.dataset = dataset
    args.estimator_idx = int(estimator_idx)
    return args

def run_evaluate_modules(model,dataset,estimator_idx):
    args = get_args(model,dataset,estimator_idx)
    # args = args.parse_args()
    print(args)
    main_func(args)
    return

# if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--model', choices=['simcnn', 'rescnn', 'incecnn'])
    # parser.add_argument('--dataset', choices=['cifar10', 'svhn'])
    # parser.add_argument('--estimator_idx', type=int)
    # args = parser.parse_args()
    # print(args)
    # main_func()
