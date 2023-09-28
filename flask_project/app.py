from datetime import timedelta
from flask import Flask, request, render_template, send_from_directory,session,jsonify
from flask_session import Session
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
# Golbal config for SeaM
from SeaM_main.src.global_config import global_config as global_config_SeaM

from GradSplitter_main.src.script.run_train import run_train_script
from GradSplitter_main.src.script.run_splitter import run_splitter_script
from GradSplitter_main.src.script.select_modules import run_select_modules_script
from GradSplitter_main.src.script.run_evaluate_modules import run_evaluate_modules_script
from GradSplitter_main.src.script.run_module_reuse_for_accurate_model import run_ensemble_modules_script

import threading

app = Flask(__name__)
CORS(app,expose_headers=['Content-Disposition'])

# create a SocketIO instance
app.config['SECRET_KEY'] = 'session:'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False,\
                    expose_headers=['Content-Disposition'])
# 初始化session
Session(app)


@app.route('/')
def index():
    return "哈喽，沃德！"

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('message', 'Successfully connected to the server!')


# Given name of algorithm, find the directory of it
# ================后面想办法把路径抽象出来======================
def dir_convert(algorithm, direct_model_reuse, model_file, dataset_file,
            target_class_str, target_superclass_idx_str,lr_mask,alpha,lr_head=0.1):
    # print(algorithm)
    if algorithm == "SEAM":
        # This is the real data dir in project!!!!!!!!!!!!!!!!!
        # algorithm_path = f"{global_config_SeaM.data_dir}/flask_project"
        algorithm_path = "/data/bixh/ToolDemo_GS/SeaM_main/data"
        file_name = f"lr_head_mask_{lr_head}_{lr_mask}_alpha_{alpha}.pth"
        # algorithm_path = "flask_project/SeaM_main/data"
        if direct_model_reuse == "Binary Classification":
            model_reuse_path = f"/binary_classification/{model_file}_{dataset_file}/tc_{target_class_str}/"
        elif direct_model_reuse == "Multi-Class Classification":
            model_reuse_path = f"/multi_class_classification/{model_file}_{dataset_file}/tsc_{target_superclass_idx_str}/"
        return f"{algorithm_path}{model_reuse_path}",file_name
    # =====================================TO BE CONTINUED============================
    elif algorithm == "GradSplitter":
        algorithm_path = "/GradSplitter_main/data/"


@app.route('/benchmark', methods=['POST'])
def benchmark():
    data = request.get_json()
    print(data)
    model_file = data.get('modelFile')
    dataset_file = data.get('datasetFile')
    algorithm = data.get('algorithm')
    learning_rate = data.get('learningRate')
    direct_model_reuse = data.get('directModelReuse')
    target_class = 0
    alpha = float(data.get('alpha'))
    if algorithm=='SEAM':
        try:
            def callback(m_total_flop_dense, m_total_flop_sparse, 
                        perc_sparse_dense, acc_reeng, acc_pre):
                socketio.emit('model_result', f'FLOPs Dense: {m_total_flop_dense:.2f}M')
                socketio.emit('model_result', f'FLOPs Sparse: {m_total_flop_sparse:.2f}M')
                socketio.emit('model_result', f'FLOPs % (Sparse / Dense): {perc_sparse_dense:.2%}')
                socketio.emit('model_result', f'Pretrained Model ACC: {acc_pre:.2%}')
                socketio.emit('model_result', f'Reengineered Model ACC: {acc_reeng:.2%}')
            def run():
                try:
                    print("Run function started.")  # Debug line
                    if direct_model_reuse=='Binary Classification':
                        # model_file="vgg16"
                        # dataset_file="cifar10"
                        # target_class=0
                        # learning_rate=0.01
                        # alpha=1.0
                        socketio.emit('message','\nReengineering Model, Please Wait!!!')
                        print("\nReengineering Model, Please Wait!!!")
                        # run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
                        #                 target_class=target_class,lr_mask=learning_rate, alpha=alpha)
                        socketio.emit('message','\nModel is ready, waiting for calculating flops......')
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
                socketio.emit('model_result', f'Best Module: {best_modules}')
                socketio.emit('model_result', f'Best_epoch: {best_epoch}')
                socketio.emit('model_result', f'Best_acc: {best_acc * 100:.2f}%')
                socketio.emit('model_result', f'Best_avg_kernel: {best_avg_kernel:.2f}')
            def run():
                socketio.emit('message','\n Reengineering Model, Please Wait!!!')
                run_splitter_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Reengineering Done!')
                socketio.emit('message','\n Selecting Modules, Please Wait!!!')
                run_select_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Modules Selected!!!')
                socketio.emit('message','\n Evaluating Modules......')
                run_evaluate_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Trying to ensemble a more accurate model......')
                run_ensemble_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n New accuate model ensembled!!!')

            # start a new thread to run the model
            threading.Thread(target=run).start()
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
    return jsonify({'message': 'Benchmark completed'})


def tc_legal(target_class_str):
    # target_class_str判断合法+默认值
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
    # Get data from requests
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
    alpha = float(data.get('alpha'))
    target_class = tc_legal(target_class_str)
    target_superclass_idx = tc_legal(target_superclass_idx_str)
    # session["model_file"]=model_file
    # session["dataset_file"]=dataset_file
    # session["algorithm"]=algorithm
    # session["epoch"]=epoch
    # session["learning_rate"]=learning_rate
    # session["direct_model_reuse"]=direct_model_reuse
    # session["target_class"]=target_class
    # session["alpha"]=alpha
    # print(f"Setting session: {session}")
    if algorithm=='SEAM':
        try:
            def callback(m_total_flop_dense, m_total_flop_sparse, 
                        perc_sparse_dense, acc_reeng, acc_pre):
                socketio.emit('model_result', f'FLOPs Dense: {m_total_flop_dense:.2f}M')
                socketio.emit('model_result', f'FLOPs Sparse: {m_total_flop_sparse:.2f}M')
                socketio.emit('model_result', f'FLOPs % (Sparse / Dense): {perc_sparse_dense:.2%}')
                socketio.emit('model_result', f'Pretrained Model ACC: {acc_pre:.2%}')
                socketio.emit('model_result', f'Reengineered Model ACC: {acc_reeng:.2%}')
            def run():
                if direct_model_reuse=='Binary Classification':
                    socketio.emit('message','\nReengineering Model, Please Wait!!!')
                    # run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
                    #                 target_class=target_class,lr_mask=learning_rate, alpha=alpha)
                    socketio.emit('message','\nModel is ready, waiting for calculating flops......')
                    run_calculate_flop_bc(model=model_file, dataset=dataset_file, 
                                target_class=target_class, lr_mask=learning_rate, alpha=alpha,
                                callback=callback)
                    
                elif direct_model_reuse=='Multi-Class Classification':
                    socketio.emit('message','\nReengineering Model, Please Wait!!!')    
                    run_model_reengineering_mc(model=model_file, dataset=dataset_file, 
                                target_superclass_idx=target_superclass_idx,
                                lr_mask=learning_rate, alpha=alpha, callback=callback)
                    socketio.emit('message','\nModel is ready, waiting for calculating flops......')
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
                    run_reengineering_finetune(model=model_file, dataset=model_file,
                           lr_mask=0.05, alpha=0.5, prune_threshold=0.6)
                    run_eval_robustness(model=model_file, dataset=model_file, 
                            eval_method="seam", lr_mask=0.05, alpha=0.5, prune_threshold=0.6)
                    run_standard_finetune(model=model_file, dataset=model_file)
                    run_eval_robustness(model=model_file, dataset=model_file, eval_method="standard")
                        
                else:
                    print("Model reuse type error!!")
                    return ValueError
                
            # start a new thread to run the model
            threading.Thread(target=run).start()
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
    elif algorithm=='GradSplitter':
        try:
            def callback(best_modules,best_epoch,best_acc,best_avg_kernel):
                socketio.emit('model_result', f'Best Module: {best_modules}')
                socketio.emit('model_result', f'Best_epoch: {best_epoch}')
                socketio.emit('model_result', f'Best_acc: {best_acc * 100:.2f}%')
                socketio.emit('model_result', f'Best_avg_kernel: {best_avg_kernel:.2f}')
            def run():
                socketio.emit('message','\n Reengineering Model, Please Wait!!!')
                run_splitter_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Reengineering Done!')
                socketio.emit('message','\n Selecting Modules, Please Wait!!!')
                run_select_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Modules Selected!!!')
                socketio.emit('message','\n Evaluating Modules......')
                run_evaluate_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n Trying to ensemble a more accurate model......')
                run_ensemble_modules_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\n New accuate model ensembled!!!')

            # start a new thread to run the model
            threading.Thread(target=run).start()
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            return {'logs': str(e), 'isModelReady': False}, 500
        return
# Download module
# Requires parameters
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
    alpha = float(data.get('alpha'))
    target_class = tc_legal(target_class_str)
    target_superclass_idx = tc_legal(target_superclass_idx_str)

    try:
        directory,filename = dir_convert(algorithm=algorithm, direct_model_reuse=direct_model_reuse, \
                                   model_file=model_file, dataset_file=dataset_file,target_class_str=target_class, \
                                   target_superclass_idx_str=target_class,lr_mask=learning_rate,alpha=alpha)
        print(directory)
        print(filename)
        # directory,filename = dir_convert(algorithm="SEAM", direct_model_reuse="Binary Classification", \
        #                            model_file="vgg16", dataset_file="cifar10",target_class_str="0", \
        #                            target_superclass_idx_str="0",lr_mask="0.01",alpha=1)
        # directory = '/data/bixh/ToolDemo_GS/SeaM_main/data/binary_classification/vgg16_cifar10/tc_0'
        # filename = "lr_head_mask_0.1_0.01_alpha_1.0.pth"
        print(f"Attempting to send from directory: {directory}, filename: {filename}")  # Debug line
        response = send_from_directory(directory, filename, as_attachment=True)
        response.headers["content-disposition"] = filename
        return response
    except Exception as e:
        print(f"An error occurred: {e}")  # Debug line
        return str(e), 400


if __name__ == '__main__':
    socketio.run(app, debug=True)
