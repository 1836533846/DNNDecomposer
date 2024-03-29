# DNNDecomposer

A Tool for DNN Modularization to Support On-demand Model Reuse

MORE RESULTS can be seen in :

```bash
/results/README.md
```

Docker images can be found in:

https://hub.docker.com/repository/docker/bxh1/dnndecomposer/general

To launch docker images and save logs, use:

```bas
docker-compose up >logs.txt
```

## Abstract

Several DNN modularization methods have been proposed to decompose a DNN model into a set of modules that can be reused independently or by composition. However, existing studies mainly focus on algorithm design and experimental evaluation. There lacks a tool supporting the modularization process. To fill in the gap, we present DNNDecomposer, a tool for providing integrated support for realizing model decomposition and module reuse. DNNDecomposer is implemented based on two DNN modularization approaches proposed by us previously. With DNNDecomposer, one can easily decompose trained model to modules on demand, and reuse modules for inference, building more accurate model or composing modules across models. Evaluations on widely-adopted models demonstrate that DNNDecomposer significantly curtails the overhead associated with model reuse. Impressively, it achieves model decomposition while improving classification accuracy in the target task through out-of-the-box operation. 

## Requirements
**This tool should be deployed on Linux with Nvidia GPU**

**For WebUI:**

- node v16.20.2
- npm v8.19.4
- vue v2.6.11

**For server:**

- Python v3.8.10
- Pytorch v1.8.1
- Argparse v1.4.0
- Flask v3.0.0
- Werkzeug v3.0.0
- GPU with CUDA support

## Structure of the directories

```
[todo]
```

## How to use

The tool is divided into two parts.

###  For WebUI:

```bash
cd vue_project
```

To install requirements, please run:

```bash
npm install
```

And for running the web UI:

```bash
npm run serve
```

### For server:

```bash
cd flask_project
```

Python 3.8 and GPU with CUDA is required.

To install requirements, run

```ba
pip install -r requirements.txt
```

And start the server:

```ba
flask run
```

## Data

Move [Data](https://mega.nz/file/tX91ACpR#CSbQ2Xariha7_HLavE_6pKg4FoO5axOPemlv5J0JYwY) to:

```bash
DNNDecomposer/flask_project/GradSplitter_main/data
```

Move [Data](https://mega.nz/folder/ADMjESyC#LkCOzE0qVHs8DOXkN3l_WA) to:

```bash
DNNDecomposer/flask_project/SeaM_main/data
```

## Architecture

![image-20231024170713770](img/image-20231024170713770.png)

## UI design

Users first specify the model that needs to be decomposed, and then select the corresponding dataset. DNNDecomposer will provide the model trained on the corresponding dataset. Next, select the target task and click the “Modularize” button to send the task configurations to the server to execute the corresponding pipeline. The results will be sent back to the log box of the web interface, showing the evaluation of the decomposition. The decomposed modules can be downloaded by clicking “download”, or by clicking “reuse” to perform the reuse function we offer.

![image-20231024171105367](img/image-20231024171105367.png)
