import torch

checkpoint = torch.load('flask_project/SeaM_main/data/binary_classification/vgg16_cifar10/tc_0/lr_head_mask_0.1_0.01_alpha_1.0.pth')

for key in checkpoint.keys():
    # print(f'\n{key}')
    if "mask" in key:
        mask_tensor = checkpoint[key]
        print(f"Key: {key}")
        print(f"Shape: {mask_tensor.shape}")
        print(f"Average: {torch.mean(mask_tensor.float()):.4f}")
        print(f"Max: {torch.max(mask_tensor):.4f}")
        print(f"Min: {torch.min(mask_tensor):.4f}")