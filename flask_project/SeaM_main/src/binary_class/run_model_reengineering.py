import argparse
import os.path
import sys
import torch
from torch.utils.data import DataLoader
# sys.path.append('../')
# sys.path.append('../..')
# 添加本文件所在的目录到 sys.path
# print(sys.path)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# print(sys.path)

from reengineer import Reengineer
from datasets.dataset_loader_bc import load_dataset
from config import load_config
from tqdm import tqdm
from models.vgg import cifar10_vgg16_bn as cifar10_vgg16
from models.vgg import cifar100_vgg16_bn as cifar100_vgg16
from models.resnet import cifar10_resnet20, cifar100_resnet20

# Converted from model_regineering.py
# Get parameters from function inputs rather than command
# Run model_reengineering for binary class.

def get_args(model, dataset, target_class, lr_mask=0.1, alpha=1, shots= -1, 
             seed=0, n_epochs=300, lr_head=0.1, early_stop=-1, tuning_param=False):
    args = argparse.Namespace()
    args.model = model
    args.dataset = dataset
    args.target_class = target_class
    args.lr_mask = lr_mask
    args.alpha = alpha
    args.shots = shots
    args.seed = seed
    args.n_epochs = n_epochs
    args.lr_head = lr_head
    args.early_stop = early_stop
    args.tuning_param = tuning_param
    return args

def reengineering(model, train_loader, test_loader, lr_mask, lr_head, n_epochs, 
                  alpha, early_stop, acc_pre_model, config, args, get_epochs):
    save_dir = f'{config.project_data_save_dir}/{args.model}_{args.dataset}/tc_{args.target_class}'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = f'{save_dir}/lr_head_mask_{args.lr_head}_{args.lr_mask}_alpha_{args.alpha}.pth'

    reengineer = Reengineer(model, train_loader, test_loader, 
                            acc_pre_model=acc_pre_model)
    reengineered_model = reengineer.alter(lr_mask=lr_mask, lr_head=lr_head,
                              n_epochs=n_epochs, alpha=alpha, get_epochs=get_epochs,
                              early_stop=early_stop)


    masks = reengineered_model.get_masks()
    module_head = reengineered_model.get_module_head()
    masks.update(module_head)
    torch.save(masks, save_path)

    # check
    model_static = model.state_dict()
    reengineered_model_static = reengineered_model.state_dict()
    for k in model_static:
        if 'mask' not in k and 'module_head' not in k:
            model_weight = model_static[k]
            reengineered_model_weight = reengineered_model_static[k]
            assert (model_weight == reengineered_model_weight).all()


@torch.no_grad()
def evaluate(model, test_loader, args):
    model.eval()
    n_corrects = 0
    n_samples = 0

    for batch_inputs, batch_labels in tqdm(test_loader, ncols=80, desc=f'Eval '):
        batch_inputs, batch_labels = batch_inputs.to('cuda'), batch_labels.to('cuda')
        batch_outputs = model(batch_inputs)
        n_samples += batch_labels.shape[0]
        batch_preds = torch.argmax(batch_outputs, dim=1)

        if args.target_class >= 0:
            # Transfer the multiclass classification into the binary classification.
            batch_preds = batch_preds == args.target_class
            batch_labels = batch_labels == args.target_class

        n_corrects += torch.sum(batch_preds == batch_labels).item()

    acc = float(n_corrects) / n_samples
    return acc


def eval_pretrained_model(args, num_workers, pin_memory):
    model = eval(f'{args.dataset}_{args.model}')(pretrained=True).to('cuda')
    dataset_test = load_dataset(args.dataset, is_train=False, target_class=args.target_class, reorganize=False)
    test_loader = DataLoader(dataset_test, batch_size=64, shuffle=True, num_workers=num_workers, pin_memory=pin_memory)
    acc = evaluate(model, test_loader, args)
    return acc


def main_func(args, num_workers, pin_memory,config,get_epochs):
    acc_pre_model = eval_pretrained_model(args, num_workers, pin_memory)
    print(f'\nPretrained Model Test Acc: {acc_pre_model:.2%}\n\n')
    # eval把输入的模型名和数据名拼成一个模型名
    model = eval(f'{args.dataset}_{args.model}')\
            (pretrained=True, is_reengineering=True).to('cuda')
    dataset_train = load_dataset(args.dataset, is_train=True, shots=args.shots,
                                 target_class=args.target_class, reorganize=True)
    dataset_test = load_dataset(args.dataset, is_train=False, 
                                target_class=args.target_class, reorganize=True)
    train_loader = DataLoader(dataset_train, batch_size=64, shuffle=True, 
                              num_workers=num_workers, pin_memory=pin_memory)
    test_loader = DataLoader(dataset_test, batch_size=64, shuffle=False, 
                             num_workers=num_workers, pin_memory=pin_memory)

    reengineering(model, train_loader, test_loader, args.lr_mask, args.lr_head,
                  args.n_epochs, args.alpha, args.early_stop, acc_pre_model,
                  config,args,get_epochs=get_epochs)

    print(f'\nPretrained Model Test Acc: {acc_pre_model:.2%}\n\n')

def run_model_reengineering_bc(model, dataset, target_class, lr_mask, alpha, 
                               n_epochs, shots= -1, seed=0, lr_head=0.1, 
                            early_stop=-1, tuning_param=False,get_epochs="debug"):
    print(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
    print(torch.cuda.is_available())

    args = get_args(model, dataset, target_class, lr_mask, alpha, shots, 
                    seed, n_epochs, lr_head, early_stop, tuning_param)
    print(args)
    config = load_config()

    num_workers = 8
    pin_memory = True

    # model_name = args.model
    main_func(args,num_workers,pin_memory,config,get_epochs)


# if __name__ == '__main__':

#     run_model_reengineering(model='vgg16', dataset='cifar10', target_class=0,
#                             lr_mask=0.01, alpha=1)