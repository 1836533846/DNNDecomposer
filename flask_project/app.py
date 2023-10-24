from datetime import timedelta
from flask import Flask, request, render_template, send_from_directory,jsonify
from flask_cors import CORS
from flask_socketio import SocketIO,emit
import os
# from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop
from SeaM_main.src.multi_class.run_model_reengineering import run_model_reengineering_mc
from SeaM_main.src.multi_class.run_calculate_flop import run_calculate_flop_mc
from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop_bc
from SeaM_main.src.binary_class.run_model_reengineering import run_model_reengineering_bc
# from SeaM_main.src.binary_class.run_calculate_time_cost import run_calculate_time_cost_bc
from SeaM_main.src.defect_inherit.run_reengineering_finetune import run_reengineering_finetune
from SeaM_main.src.defect_inherit.run_eval_robustness import run_eval_robustness
from SeaM_main.src.defect_inherit.run_standard_finetune import run_standard_finetune
from SeaM_main.src.binary_class.SeaM_reasoning import cifar10_inference
# cifar10_inference.predict('image/cat.jpg')
# Golbal config for SeaM
from SeaM_main.src.global_config import global_config as global_config_SeaM

from GradSplitter_main.src.script.run_train import run_train_script
from GradSplitter_main.src.script.run_splitter import run_splitter_script
from GradSplitter_main.src.script.select_modules import run_select_modules_script
from GradSplitter_main.src.script.run_evaluate_modules import run_evaluate_modules_script
from GradSplitter_main.src.script.run_module_reuse_for_accurate_model import run_ensemble_modules_script
from GradSplitter_main.src.script.run_module_reuse_for_new_task import run_reuse_modules_script_pair
# Golbal config for Grad
from GradSplitter_main.src.global_configure import global_config as global_config_Grad


import threading

app = Flask(__name__)
CORS(app,expose_headers=['Content-Disposition'])


app.config['UPLOAD_FOLDER'] = 'uploads'
# create a SocketIO instance
socketio = SocketIO(app, cors_allowed_origins="*",allow_unsafe_werkzeug=True,\
                    expose_headers=['Content-Disposition'])

@app.route('/')
def index():
    return "Welcome!"

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    socketio.emit('message', 'Successfully connected to the server!')

# Given name of algorithm, find the directory of it
# ================后面想办法把路径抽象出来======================
def dir_convert(algorithm, direct_model_reuse, model_file, dataset_file,
            target_class_str, target_superclass_idx_str,lr_mask,alpha,lr_head=0.1):
    if algorithm == "SEAM":
        # This is the real data dir in project!!!!!!!!!!!!!!!!!
        # algorithm_path = f"{global_config_SeaM.data_dir}/flask_project"
        algorithm_path = "/data/bixh/ToolDemo_GS/SeaM_main/data"
        if direct_model_reuse == "Binary Classification":
            file_name = f"lr_head_mask_{lr_head}_{lr_mask}_alpha_{alpha}.pth"
            model_reuse_path = f"/binary_classification/{model_file}_{dataset_file}/tc_{target_class_str}/"
        elif direct_model_reuse == "Multi-Class Classification":
            file_name = f"lr_head_mask_{lr_head}_{lr_mask}_alpha_{alpha}.pth"
            model_reuse_path = f"/multi_class_classification/{model_file}_{dataset_file}/predefined/tsc_{target_superclass_idx_str}/"
        elif direct_model_reuse == "Defect Inheritance":
            file_name = "step_3_seam_ft.pth"
            model_reuse_path = f"/defect_inheritance/seam_ft/resnet18_mit67_dropout_0.0/lr_mask_{lr_mask}_alpha_{alpha}_thres_0.6/"
        return f"{algorithm_path}{model_reuse_path}",file_name
    # =====================================TO BE CONTINUED============================
    elif algorithm == "GradSplitter":
        # algorithm_path = f"{global_config_Grad.data_dir}"
        algorithm_path = "/data/bixh/ToolDemo_GS/GradSplitter_main/data"
        model_reuse_path = f"/{model_file}_{dataset_file}/modules/estimator_1/"
        file_name = "estimator_1.pth"
        return f"{algorithm_path}{model_reuse_path}",file_name
    
@app.route('/benchmark', methods=['POST'])
def benchmark():
    data = request.get_json()
    print(data)
    model_file = data.get('modelFile')
    dataset_file = data.get('datasetFile')
    algorithm = data.get('algorithm')
    learning_rate = float(data.get('learningRate'))
    direct_model_reuse = data.get('directModelReuse')
    target_class = 0
    alpha = float(data.get('alpha')) if data.get('alpha') != '' else ''
    if algorithm=='SEAM':
        try:
            def callback(m_total_flop_dense, m_total_flop_sparse, 
                        perc_sparse_dense, acc_reeng, acc_pre):
                socketio.emit('seam_result', f'FLOPs Dense: {m_total_flop_dense:.2f}M')
                socketio.emit('seam_result', f'FLOPs Sparse: {m_total_flop_sparse:.2f}M')
                socketio.emit('seam_result', f'FLOPs % (Sparse / Dense): {perc_sparse_dense:.2%}')
                socketio.emit('seam_result', f'Pretrained Model ACC: {acc_pre:.2%}')
                socketio.emit('seam_result', f'Reengineered Model ACC: {acc_reeng:.2%}')
            def run():
                try:
                    if direct_model_reuse=='Binary Classification':
                        socketio.emit('seam_message','\nDecomposing Model, Please Wait!!!')
                        print("\nDecomposing Model, Please Wait!!!")
                        run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
                                        target_class=target_class,lr_mask=learning_rate, alpha=alpha)
                        socketio.emit('seam_message','\nModel is ready, waiting for calculating flops......')
                        run_calculate_flop_bc(model=model_file, dataset=dataset_file, 
                                    target_class=target_class, lr_mask=learning_rate, alpha=alpha,
                                    callback=callback)
                        print("Run function finished.")  # Debug line    
                    else:
                        print("Model reuse type error!!")
                        return ValueError
                except Exception as e:
                    print(f"Exception in run function: {e}")
                
            # start a new thread to run the model
            print("About to start the run thread.")  # Debug line
            threading.Thread(target=run).start()
            print("Run thread started.")  # Debug line
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
    elif algorithm=='GradSplitter':
        try:
            def callback(best_modules,best_epoch,best_acc,best_avg_kernel):
                socketio.emit('grad_result', f'Best Module: {best_modules}')
                socketio.emit('grad_result', f'Best Epoch: {best_epoch}')
                socketio.emit('grad_result', f'Best Acc: {best_acc * 100:.2f}%')
                socketio.emit('grad_result', f'Best_avg_kernel: {best_avg_kernel:.2f}')
            def run():
                socketio.emit('grad_message','\n Decomposing Model, Please Wait!!!')
                run_splitter_script(model=model_file,dataset=dataset_file)
                socketio.emit('grad_message','\n Decomposing Done!')
                socketio.emit('grad_message','\n Selecting Modules, Please Wait!!!')
                run_select_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('grad_message','\n Modules Selected!!!')
                socketio.emit('grad_message','\n Evaluating Modules......')
                run_evaluate_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('grad_message','\n Trying to ensemble a more accurate model......')
                run_ensemble_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('grad_message','\n New accuate model ensembled!!!')

            # start a new thread to run the model
            threading.Thread(target=run).start()
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
    return jsonify({'message': 'Benchmark completed'})


def tc_legal(target_class_str):
    if target_class_str is None or target_class_str.strip() == '':
        target_class = 0 
    else:
        try:
            target_class = int(target_class_str)
        except ValueError:
            print(f"Error: 'targetClass' value '{target_class_str}' is not a valid integer")
            target_class = 0 
    return target_class

@app.route('/run_model', methods=['POST'])
def run_model():
    data = request.get_json()
    print(data)
    model_file = data.get('modelFile')
    dataset_file = data.get('datasetFile')
    algorithm = data.get('algorithm')
    epoch = float(tc_legal(data.get("epoch")))
    learning_rate = float(data.get('learningRate'))
    direct_model_reuse = data.get('directModelReuse')
    target_class_str = data.get('targetClass')
    target_superclass_idx_str = data.get('targetSuperclassIdx')
    alpha = float(data.get('alpha')) if data.get('alpha') != '' else ''
    target_class = tc_legal(target_class_str)
    target_superclass_idx = tc_legal(target_superclass_idx_str)
    if algorithm=='SEAM':
        try:
            def callback(**kwargs):
                messages = {
                    'm_total_flop_dense': 'FLOPs Dense: {:.2f}M',
                    'm_total_flop_sparse': 'FLOPs Sparse: {:.2f}M',
                    'perc_sparse_dense': 'FLOPs % (Sparse / Dense): {:.2%}',
                    'acc_pre': 'Pretrained Model ACC: {:.2%}',
                    'acc_reeng': 'Reengineered Model ACC: {:.2%}',
                    'sum_masks':'Weights of original model:{:.2f}million',
                    'sum_mask_ones':'Weights of reengineered module:{:.2f}million',
                    'weight_retain_rate':"Weight retain rate:{:.2%}",
                    # For Defect Inheritance reengineering
                    'best_epoch_step1': 'Best epoch in step 1:{}',
                    'best_acc_step1': 'Best acc in step 1:{:.2%}',
                    'best_epoch_step3': 'Best epoch in step 3:{}',
                    'best_acc_step3': 'Best acc in step 3:{:.2%}',
                    # For evaluate robustness
                    'clean_top1' : 'Clean Top-1: {:.2f}',
                    'adv_sr': 'Attack Success Rate: {:.2f}',
                    'step_1': 'Step 1:Finetuning the output layer......',
                    'step_2': 'Step 2:Reengineering the fine-tuned model obtained in Step 1......',
                    'step_3': 'Step 3:Finetune according to reengineering results......',
                }
                for key, message in messages.items():
                    if key in kwargs:
                        socketio.emit('model_result', message.format(kwargs[key]))
            def get_epochs(epoch,n_epoch=300):
                epoch_percentage = (epoch/n_epoch)*100
                socketio.emit('get_progress_percentage', epoch_percentage)
                print(f"Epoch percentage:{epoch_percentage:.2f}%")
                return epoch_percentage
            def run():
                if direct_model_reuse=='Binary Classification':
                    socketio.emit('message','\n Decomposing Model, Please Wait!!!')
                    run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
                                    target_class=target_class,lr_mask=learning_rate, alpha=alpha, 
                                    n_epochs=300,get_epochs=get_epochs)
                    socketio.emit('message','\n Model is ready, waiting for calculating flops......')
                    run_calculate_flop_bc(model=model_file, dataset=dataset_file, 
                                target_class=target_class, lr_mask=learning_rate, alpha=alpha,
                                callback=callback)
                    
                elif direct_model_reuse=='Multi-Class Classification':
                    socketio.emit('message','\n Decomposing Model, Please Wait!!!')  
                    run_model_reengineering_mc(model=model_file, dataset=dataset_file, 
                                target_superclass_idx=target_superclass_idx,
                                lr_mask=learning_rate, alpha=alpha, get_epochs=get_epochs)
                    socketio.emit('message','\n Model is ready, waiting for calculating flops......')
                    run_calculate_flop_mc(model=model_file, dataset=dataset_file, 
                                target_superclass_idx=target_superclass_idx, 
                                lr_mask=learning_rate, alpha=alpha,callback=callback)
                elif direct_model_reuse == 'Defect Inheritance':
                    # 1.Re-engineer ResNet18-ImageNet and then fine-tune 
                    # the re-engineered model on the target dataset Scenes.
                    # 
                    # 2. Compute the defect inheritance rate of fine-tuned 
                    # re-engineered ResNet18-Scenes.
                    # 
                    # 3. Fine-tune the original ResNet18-ImageNet on the 
                    # target dataset Scenes.
                    # 
                    # 4. Compute the defect inheritance rate of fine-tuned 
                    # original ResNet18-Scenes.
                    socketio.emit('message','\n ## Decomposing Model...... ##')
                    socketio.emit('message','\n ## Process might be stopped before 100% when it fits the target! ##')
                    run_reengineering_finetune(model=model_file, dataset=dataset_file,
                           lr_mask=0.05, alpha=0.5, prune_threshold=0.6, callback=callback,get_epochs=get_epochs)
                    socketio.emit('message','\n ## Evaluating robustness...... ##')
                    run_eval_robustness(model=model_file, dataset=dataset_file, 
                            eval_method="seam", lr_mask=0.05, alpha=0.5, prune_threshold=0.6,callback=callback)
                    socketio.emit('message','\n ## Start Fine-tuning. ##')
                    run_standard_finetune(model=model_file, dataset=dataset_file)
                    socketio.emit('message','\n ## Finish Fine-tuning. ##')
                    socketio.emit('message','\n ## Evaluating robustness...... ##')
                    run_eval_robustness(model=model_file, dataset=dataset_file, eval_method="standard")
                    socketio.emit('message','\n ## Evaluate Done! ##')
                else:
                    print("Model reuse type error!!")
                    return ValueError
            # start a new thread to run the model
            threading.Thread(target=run).start()
            return {'logs': "Model is decomposing......\n", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
    elif algorithm=='GradSplitter':
        try:
            def callback(best_modules,best_epoch,best_acc,best_avg_kernel):
                socketio.emit('model_result', f'Best Module: {best_modules}')
                socketio.emit('model_result', f'Best Epoch: {best_epoch}')
                socketio.emit('model_result', f'Best Acc: {best_acc * 100:.2f}%')
                socketio.emit('model_result', f'Best Averag Kernel: {best_avg_kernel:.2f}')
            def get_epochs(epoch,n_epoch=145):
                epoch_percentage = (epoch/n_epoch)*100
                socketio.emit('get_progress_percentage', epoch_percentage)
                print(f"Epoch percentage:{epoch_percentage:.2f}%")
                return epoch_percentage
            def run():
                socketio.emit('message','\n Decomposing Model, Please Wait!!!')
                run_splitter_script(model=model_file,dataset=dataset_file,callback=callback, get_epochs=get_epochs)
                socketio.emit('message','\n Decomposing Done!')
                socketio.emit('message','\n Selecting Modules, Please Wait!!!')
                run_select_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Modules Selected!!!')
            threading.Thread(target=run).start()
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
        return
# Reuse module
@app.route('/run_reuse', methods=['POST'])
def run_reuse():
    data = request.get_json()
    print(data)
    model_file = data.get('modelFile')
    dataset_file = data.get('datasetFile')
    algorithm = data.get('algorithm')
    epoch = data.get('epoch')
    reuseMethod = data.get('reuseMethod')
    cifarclass = data.get('cifarclass')
    svhnclass = data.get('svhnclass')
    if reuseMethod == "More Accurate":
        try:
            def callback(acc):
                socketio.emit('reuse_result', f'Best acc: {acc * 100:.2f}%')
            def run():
                socketio.emit('reuse_message','\n Evaluating Modules......')
                run_evaluate_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('reuse_message','\n Trying to ensemble a more accurate model......')
                run_ensemble_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('reuse_message','\n New accuate model ensembled!!!')
            threading.Thread(target=run).start()
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
    elif reuseMethod == "For New Task":
        print("Model reuse for new task......")
        try:
            def callback(acc):
                socketio.emit('reuse_result', f'ACC: {acc:.2f}')
            def run():
                socketio.emit('reuse_message',f'\n Evaluating and selecting modules......')
                run_reuse_modules_script_pair(model_file,cifarclass,svhnclass,callback=callback)
                socketio.emit('reuse_message',f'\n Select module {cifarclass} for CIFAR, {svhnclass} for SVHN!')
            threading.Thread(target=run).start()
            return {'reuse_message': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'reuse_message': str(e), 'isModelReady': False}, 500
    return
# Download module
@app.route('/download', methods=['POST'])
def download_file():
    data = request.get_json()
    print(data)
    model_file = data.get('modelFile')
    dataset_file = data.get('datasetFile')
    algorithm = data.get('algorithm')
    epoch = data.get('epoch')
    learning_rate = data.get('learningRate')
    direct_model_reuse = data.get('directModelReuse')
    target_class_str = data.get('targetClass')
    target_superclass_idx_str = data.get('targetSuperclassIdx')
    alpha = float(data.get('alpha')) if data.get('alpha') != '' else ''
    target_class = tc_legal(target_class_str)
    target_superclass_idx = tc_legal(target_superclass_idx_str)
    try:
        directory,filename = dir_convert(algorithm=algorithm, direct_model_reuse=direct_model_reuse, \
                                   model_file=model_file, dataset_file=dataset_file,target_class_str=target_class, \
                                   target_superclass_idx_str=target_class,lr_mask=learning_rate,alpha=alpha)
        # print(directory)
        # print(filename)
        print(f"Attempting to send from directory: {directory}, filename: {filename}")  # Debug line
        response = send_from_directory(directory, filename, as_attachment=True)
        response.headers["content-disposition"] = filename
        return response
    except Exception as e:
        print(f"An error occurred: {e}")  # Debug line
        return str(e), 400

@app.route('/run_deployment', methods=['POST'])
def run_deployment():
    data = request.get_json()
    img_name = data.get('image')
    class_name,class_num = cifar10_inference.predict(f'image/{img_name}.png')
    print(class_name)
    result = class_name if class_num!=0 else f"Not cat"
    socketio.emit('deployment_result',f'{result}')
    return class_name

if __name__ == '__main__':
    socketio.run(app, debug=True)
