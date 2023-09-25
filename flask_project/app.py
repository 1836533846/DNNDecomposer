from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO,emit
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

import threading

app = Flask(__name__)
CORS(app)

# create a SocketIO instance
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


# @app.route('/')
# def index():
#     return "Hello, World!"

# Given name of algorithm, find the directory of it
# ================后面想办法把路径抽象出来======================
def dir_convert(algorithm, direct_model_reuse, model_file, dataset_file,
                target_class_str, target_superclass_idx_str):
    if algorithm == "SEAM":
        algorithm_path = global_config_SeaM.data_dir
        # algorithm_path = "flask_project/SeaM_main/data"
        if direct_model_reuse == "Binary Classification":
            model_reuse_path = f"/binary_classification/tc_{target_class_str}"
        elif direct_model_reuse == "Multi-Class Classification":
            model_reuse_path = f"/multi_class_classification/tsc_{target_superclass_idx_str}"

    # elif algorithm == "GradSplitter":
    #     algorithm_path = "flask_project/GradSplitter_main/data/"
        
        return f"{algorithm_path}{model_reuse_path}{model_file}_{dataset_file}"

# 下载模块
@app.route('/download')
# 需要一个传参
def download_file():
    directory = 'D:/ToolDemo_GS/flask_project/SeaM_main/data/binary_classification/vgg16_cifar10/tc_0/'
    # directory = "/path/to/folder"
    filename = "lr_head_mask_0.1_0.01_alpha_1.0.pth"
    return send_from_directory(directory, filename, as_attachment=True)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('my response', json)

@app.route('/run_model', methods=['POST'])

# def get_args(model, dataset, superclass_type='predefined', target_superclass_idx=-1, 
#              n_classes=-1, shots= -1, seed=0, n_epochs=300, lr_head=0.1, lr_mask=0.1, 
#              alpha=1, early_stop=-1):

def run_model():
    # Get data from requests
    data = request.get_json()
    model_file = data.get('modelFile')
    dataset_file = data.get('datasetFile')
    algorithm = data.get('algorithm')
    epoch = data.get('epoch')
    learning_rate = data.get('learningRate')
    direct_model_reuse = data.get('directModelReuse')
    target_class_str = data.get('targetClass')
    # if data.get('targetClass') is not '-1' else data.get('targetSuperclassIdx')
    if target_class_str is None or target_class_str.strip() == '':
        target_class = 0  # Default value
    else:
        try:
            target_class = int(target_class_str)
        except ValueError:
            print(f"Error: 'targetClass' value '{target_class_str}' is not a valid integer")
            target_class = 0  # Or some other default value in case of error
    target_superclass_idx_str = data.get('targetSuperclassIdx')
    if target_superclass_idx_str is None or target_superclass_idx_str.strip() == '':
        target_superclass_idx = 0  # Default value
    else:
        try:
            target_superclass_idx = int(target_superclass_idx_str)
        except ValueError:
            print(f"Error: 'targetSuperclassIdx' value '{target_superclass_idx_str}' is not a valid integer")
            target_superclass_idx = 0  # Or some other default value in case of error
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
                # socketio.emit('model_result', {'status': 'error', 'error': error})
            def run():
                if direct_model_reuse=='Binary Classification':
                    # model_file="vgg16"
                    # dataset_file="cifar10"
                    # target_class=0
                    # learning_rate=0.01
                    # alpha=1.0
                    socketio.emit('message','\nReengineering Model, Please Wait!!!')
                    run_model_reengineering_bc(model=model_file, dataset=dataset_file, 
                                    target_class=target_class,lr_mask=learning_rate, alpha=alpha)
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
            # if the model runs successfully, return the logs and model status
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            # if the model runs fails, return the error
            return {'logs': str(e), 'isModelReady': False}, 500
    elif algorithm=='GradSplitter':
        try:
            def callback(m_total_flop_dense, m_total_flop_sparse, 
                        perc_sparse_dense, acc_reeng, acc_pre):
                socketio.emit('model_result', f'FLOPs Dense: {m_total_flop_dense:.2f}M')
                socketio.emit('model_result', f'FLOPs Sparse: {m_total_flop_sparse:.2f}M')
                socketio.emit('model_result', f'FLOPs % (Sparse / Dense): {perc_sparse_dense:.2%}')
                socketio.emit('model_result', f'Pretrained Model ACC: {acc_pre:.2%}')
                socketio.emit('model_result', f'Reengineered Model ACC: {acc_reeng:.2%}')
                # socketio.emit('model_result', {'status': 'error', 'error': error})
            def run():
                socketio.emit('message','\nReengineering Model, Please Wait!!!')
                run_splitter_script(model=model_file,dataset=dataset_file)
                socketio.emit('message','\nReengineering Done!')
                socketio.emit('message','\nSelecting Modules, Please Wait!!!')
                run_select_modules_script(model=model_file,dataset=dataset_file)

                return
            # start a new thread to run the model
            threading.Thread(target=run).start()
            # if the model runs successfully, return the logs and model status
            return {'logs': "Model run successfully", 'isModelReady': True}, 200
        except Exception as e:
            # if the model runs fails, return the error
            return {'logs': str(e), 'isModelReady': False}, 500
        return

if __name__ == '__main__':
    socketio.run(app, debug=True)
