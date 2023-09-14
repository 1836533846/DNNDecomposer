# from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop
# from SeaM_main.src.multi_class.run_model_reengineering import run_model_reengineering
from SeaM_main.src.multi_class.run_calculate_flop import run_calculate_flop_mc
from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop_bc
from SeaM_main.src.binary_class.run_model_reengineering import run_model_reengineering_bc
# from SeaM_main.src.binary_class.run_calculate_time_cost import run_calculate_time_cost_bc
import os
# run_calculate_flop测试ok，但是
# No such file or directory: 
# 'YourDir/SeaM/data/binary_classification/vgg16_cifar10
# /tc_0/lr_head_mask_0.01_1_alpha_1.pth'
# 后面配置一下训练好的模型

# run_calculate_flop(model="vgg16", dataset="cifar10", 
#                    target_class=0, lr_mask=0.01, alpha=1)

model_file="vgg16"
dataset_file="cifar10"
target_class=0
learning_rate=0.01
alpha=1.0

if __name__ == "__main__":
    # run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
    #                             target_class=target_class,
    #                             lr_mask=learning_rate, alpha=alpha)
    run_calculate_flop_bc(model="vgg16", dataset="cifar10", 
                          target_class=0, lr_mask=0.01, alpha=1, 
                          callback="debug")
    
    # run_calculate_time_cost_bc(model=model_file, dataset=dataset_file, 
    #                            target_class=target_class, lr_mask=learning_rate, alpha=alpha)
    
    
    # run_calculate_flop_mc(model="resnet20", dataset="cifar100", 
    #                target_superclass_idx=0, lr_mask=0.1, alpha=2.0,
    #                callback="debug")

    # run_calculate_flop(model="vgg16", dataset="cifar10", 
    #                target_class=0, lr_mask=0.01, alpha=1.0)