from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO,emit
from SeaM_main.src.binary_class.run_model_reengineering import run_model_reengineering
from SeaM_main.src.binary_class.run_calculate_flop import run_calculate_flop_bc
from SeaM_main.src.multi_class.run_calculate_flop import run_calculate_flop_mc

import threading

app = Flask(__name__)
CORS(app, origins='*')

# create a SocketIO instance
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# @app.route('/')
# def index():
#     return "Hello, World!"

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
                    # run_model_reengineering(model=model_file, dataset=dataset_file, 
                    #                 target_class=target_class,
                    #                 lr_mask=learning_rate, alpha=alpha)
                    socketio.emit('message','\nModel is ready, waiting for calculating flops......')
                    run_calculate_flop_bc(model="vgg16", dataset="cifar10", 
                                target_class=0, lr_mask=0.01, alpha=1.0,
                                callback=callback)
                elif direct_model_reuse=='Multi-Class Classification':
                    socketio.emit('message','\nModel is ready, waiting for calculating flops......')
                    run_calculate_flop_mc(model="resnet20", dataset="cifar100", 
                                target_superclass_idx=0, lr_mask=0.1, alpha=2.0,
                                callback=callback)
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

if __name__ == '__main__':
    socketio.run(debug=True)
