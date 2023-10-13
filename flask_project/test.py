import torch
from GradSplitter_main.src.utils.model_loader import load_model
from GradSplitter_main.src.utils.splitter_loader import load_splitter

def load_model_from_pth(model_name, path):

    base_model = load_model(model_name)
    GradSplitterClass = load_splitter(model_name,None)
    model = GradSplitterClass(base_model,"ones")
    state_dict = torch.load(path)
    model.model.load_state_dict(state_dict)
    return model

def print_model_structure(model, prefix=""):
    for name, module in model.named_children():
        new_prefix = prefix + "." + name if prefix else name
        print(new_prefix)
        print_model_structure(module, new_prefix)
    for name, param in model.named_parameters():
        print(prefix + "." + name if prefix else name)

MODEL_PATH = "GradSplitter_main/data/simcnn_cifar10/trained_models/estimator_1.pth"
MASK_PATH = "GradSplitter_main/data/simcnn_cifar10/modules/estimator_1/estimator_1.pth"
original_model = load_model_from_pth("simcnn", MODEL_PATH)
masks = load_model_from_pth("simcnn", MASK_PATH)
print("=== Original Model Structure ===")
print_model_structure(original_model)
print("\n=== Masks Structure ===")
print_model_structure(masks)
