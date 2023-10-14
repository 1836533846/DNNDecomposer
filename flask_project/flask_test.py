# from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop
from SeaM_main.src.multi_class.run_model_reengineering import run_model_reengineering_mc
from SeaM_main.src.multi_class.run_calculate_flop import run_calculate_flop_mc
from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop_bc
from SeaM_main.src.binary_class.run_model_reengineering import run_model_reengineering_bc
# from SeaM_main.src.binary_class.run_calculate_time_cost import run_calculate_time_cost_bc
from SeaM_main.src.defect_inherit.run_reengineering_finetune import run_reengineering_finetune
from SeaM_main.src.defect_inherit.run_eval_robustness import run_eval_robustness
from SeaM_main.src.defect_inherit.run_standard_finetune import run_standard_finetune

from SeaM_main.src.global_config import global_config as global_config_SeaM
from GradSplitter_main.src.global_configure import global_config as global_config_Grad

from GradSplitter_main.src.script.run_train import run_train_script
from GradSplitter_main.src.script.run_splitter import run_splitter_script
from GradSplitter_main.src.script.run_module_reuse_for_accurate_model import run_ensemble_modules_script
from GradSplitter_main.src.script.run_module_reuse_for_new_task import run_reuse_modules_script
import os
from GradSplitter_main.src.train import run_train
from GradSplitter_main.src.grad_splitter import run_grad_splitter
from GradSplitter_main.src.global_configure import global_config as global_config_Grad

print(global_config_Grad.data_dir)

# run_calculate_flop测试ok，但是
# No such file or directory: 
# 'YourDir/SeaM/data/binary_classification/vgg16_cifar10
# /tc_0/lr_head_mask_0.01_1_alpha_1.pth'
# 后面配置一下训练好的模型

# run_calculate_flop(model="vgg16", dataset="cifar10", 
#                    target_class=0, lr_mask=0.01, alpha=1)


# from SeaM_main.src.binary_class.SeaM_reasoning import cifar10_inference
# label = cifar10_inference.predict('image/cat.png')
# print(f"LABEL:{label}")

model_file="vgg16"
dataset_file="cifar10"
target_class=0
learning_rate=0.01
alpha=1.0

if __name__ == "__main__":
    def callback(best_modules,best_epoch,best_acc,best_avg_kernel):
        print(f'Best Module: {best_modules}')
        print(f'best_epoch: {best_epoch}')
        print(f'best_acc: {best_acc * 100:.2f}%')
        print(f'best_avg_kernel: {best_avg_kernel:.2f}')

    # def dir_convert(algorithm, direct_model_reuse, model_file, dataset_file,
    #             target_class_str, target_superclass_idx_str,lr_mask,alpha,lr_head=0.1):
    #     alpha = float(alpha)
    #     if algorithm == "SEAM":
    #         algorithm_path = f"{global_config_SeaM.data_dir}/flask_project"
    #         file_name = f"lr_head_mask_{lr_head}_{lr_mask}_alpha_{alpha}.pth"
    #         # algorithm_path = "flask_project/SeaM_main/data"
    #         if direct_model_reuse == "Binary Classification":
    #             model_reuse_path = f"/binary_classification/{model_file}_{dataset_file}/tc_{target_class_str}/"
    #         elif direct_model_reuse == "Multi-Class Classification":
    #             model_reuse_path = f"/multi_class_classification/{model_file}_{dataset_file}/tsc_{target_superclass_idx_str}/"
    #         return f"{algorithm_path}{model_reuse_path}",file_name
    #     # =====================================TO BE CONTINUED============================
    #     elif algorithm == "GradSplitter":
    #         algorithm_path = "/GradSplitter_main/data/"
        
    # dir,filename = dir_convert(algorithm="SEAM", direct_model_reuse="Binary Classification", model_file="vgg16", \
    #             dataset_file="cifar10",target_class_str="0", target_superclass_idx_str="0",lr_mask="0.01",alpha=1)
    # print(dir)
    # print(filename)
    

    # model = 'simcnn'
    # dataset = 'cifar10'
    # run_ensemble_modules_script(model,dataset)


    # run_grad_splitter(model='simcnn',dataset='cifar10',estimator_idx=1,callback=callback)
    # run_splitter_script(model='simcnn',dataset='cifar10')
    # run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
    #                             target_class=target_class,
    #                             lr_mask=learning_rate, alpha=alpha)
    run_calculate_flop_bc(model="vgg16", dataset="cifar10", 
                          target_class=0, lr_mask=0.01, alpha=1, 
                          callback="debug")
    
    # run_reengineering_finetune(model="resnet18", dataset="mit67",
    #                            lr_mask=0.05, alpha=0.5, prune_threshold=0.6)

    # run_eval_robustness(model="resnet18", dataset="mit67", eval_method="seam", lr_mask=0.05, alpha=0.5, prune_threshold=0.6)
    # run_standard_finetune(model="resnet18", dataset="mit67")
    # run_calculate_time_cost_bc(model=model_file, dataset=dataset_file, 
    #                            target_class=target_class, lr_mask=learning_rate, alpha=alpha)

    
    # run_calculate_flop_mc(model="resnet20", dataset="cifar100", 
    #                target_superclass_idx=0, lr_mask=0.1, alpha=2.0,
    #                callback="debug")
    # print("run_reuse_modules_script")
    # run_reuse_modules_script()

    # run_calculate_flop(model="vgg16", dataset="cifar10", 
    #                target_class=0, lr_mask=0.01, alpha=1.0)
    # model_file="resnet20"
    # dataset_file="cifar100"
    # target_superclass_idx=0
    # learning_rate=0.01
    # alpha=1.0
    # run_model_reengineering_mc(model=model_file, dataset=dataset_file, 
    #                         target_superclass_idx=target_superclass_idx,
    #                         lr_mask=learning_rate, alpha=alpha)
    
    # model = 'simcnn'
    # dataset = 'cifar10'
    # execute = 'train_estimator'
    # run_train_script(model,dataset,execute)