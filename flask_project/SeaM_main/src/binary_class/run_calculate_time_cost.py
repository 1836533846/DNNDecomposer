import argparse
from deepsparse import compile_model
from deepsparse.utils import generate_random_inputs
import torch.onnx
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from sparseml.pytorch.utils import ModuleExporter
from utils.reengineered_model_loader import load_reengineered_model
from config import load_config
from models.vgg import cifar10_vgg16_bn as cifar10_vgg16
from models.vgg import cifar100_vgg16_bn as cifar100_vgg16
from models.resnet import cifar10_resnet20, cifar100_resnet20

# def get_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--model', type=str, choices=['vgg16', 'resnet20'], required=True)
#     parser.add_argument('--dataset', type=str, choices=['cifar10', 'cifar100'], required=True)
#     parser.add_argument('--target_class', type=int, required=True)

#     parser.add_argument('--lr_head', type=float, default=0.1)
#     parser.add_argument('--lr_mask', type=float, default=0.1)
#     parser.add_argument('--alpha', type=float, default=1,
#                         help='the weight for the weighted sum of two losses in re-engineering.')

#     parser.add_argument('--shots', default=-1, type=int, help='how many samples for each classes.')
#     parser.add_argument('--seed', type=int, default=0,
#                         help='the random seed for sampling ``num_superclasses'' classes as target classes.')

#     args = parser.parse_args()
#     return args

def get_args(model, dataset, target_class, lr_head=0.1, lr_mask=0.1, 
             alpha=1.0, shots=-1, seed=0):
    args = argparse.Namespace()
    args.model = model
    args.dataset = dataset
    args.target_class = int(target_class)
    args.lr_head = float(lr_head)
    args.lr_mask = float(lr_mask)
    args.alpha = float(alpha)
    args.shots = int(shots)
    args.seed = int(seed)
    return args

def compile_sparse_model(sparse_model_path, batch_size):
    batch_size = batch_size

    # Generate random sample input
    inputs = generate_random_inputs(sparse_model_path, batch_size)

    # Compile and run
    engine = compile_model(sparse_model_path, batch_size)
    return engine


def main_func(args, config):
    save_dir = f'{config.project_data_save_dir}/{args.model}_{args.dataset}/tc_{args.target_class}'
    mask_path = f'{save_dir}/lr_head_mask_{args.lr_head}_{args.lr_mask}_alpha_{args.alpha}.pth'

    # convert model and reengineered model from pytorch to onnx.
    model = eval(f'{args.dataset}_{args.model}')(pretrained=True)
    exporter = ModuleExporter(model, './')
    exporter.export_onnx(torch.randn(16, 3, 32, 32), name=f'{args.model}_{args.dataset}_init_model.onnx')

    reengineered_model = load_reengineered_model(model, mask_path)
    exporter = ModuleExporter(reengineered_model, './')
    exporter.export_onnx(torch.randn(16, 3, 32, 32), name=f'{args.model}_{args.dataset}_reengineered.onnx')

    # use deepsaprse to compile and run the onnx model and onnx reengineered model.
    np.random.seed(0)
    inputs = [np.random.rand(16, 3, 32, 32).astype(np.float32)]

    model = compile_sparse_model(f'./{args.model}_{args.dataset}_init_model.onnx', batch_size=16)
    model_costs = []
    for i in range(2):
        result = model.benchmark(inputs, num_iterations=100, num_warmup_iterations=20)
        ms_per_batch = result.ms_per_batch
        model_costs.append(ms_per_batch)

    reengineered_model = compile_sparse_model(f'./{args.model}_{args.dataset}_reengineered.onnx', batch_size=16)
    reengineered_model_cost = []
    for i in range(2):
        result = reengineered_model.benchmark(inputs, num_iterations=100, num_warmup_iterations=20)
        ms_per_batch = result.ms_per_batch
        reengineered_model_cost.append(ms_per_batch)

    model_cost = sum(model_costs) / len(model_costs)
    reengineered_model_cost = sum(reengineered_model_cost) / len(reengineered_model_cost)

    # print(f'Model  Time Cost: {model_cost:.2f}ms')
    # print(f'Reengineered Model Time Cost: {reengineered_model_cost:.2f}ms')
    # print(f'Reduction (original - reengineering) / model: {(model_cost - reengineered_model_cost) / model_cost:.2%}\n')

    ms_model_cost = model_cost
    ms_reengineered_model_cost = reengineered_model_cost
    reduction = (model_cost - reengineered_model_cost) / model_cost

    return ms_model_cost, ms_reengineered_model_cost, reduction

def run_calculate_time_cost_bc(model, dataset, target_class, lr_mask, alpha):
    # print("aaaaaaaassssssssssssssssdddddddddddddddddddddddd")
    args = get_args(model=model, dataset=dataset, target_class=target_class, 
                    lr_mask=lr_mask, alpha=alpha)
    print(args)
    config = load_config()
    num_workers = 4
    pin_memory = False
    
    ms_model_cost, ms_reengineered_model_cost, reduction = main_func(args, config)
    
    print(f'Model  Time Cost: {ms_model_cost:.2f}ms')
    print(f'Reengineered Model Time Cost: {ms_reengineered_model_cost:.2f}ms')
    print(f'Reduction (original - reengineering) / model: {reduction:.2%}\n')
