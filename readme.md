# Modularization

### GradSplitter PART

1. #### Training CNN model

   modify `root_dir` in `src/global_configure.py`.

   run `python run_train.py` in `script/` to train a set of CNN models.

2. #### Modularizing trained CNN models

   run `python run_splitter.py` in `script/` to modularize the trained CNN models.

   run `python select_modules.py` in `script/` to select modules.

3. #### Reusing modules to build more accurate CNN models

   run `python run_evaluate_modules.py` in `script/` to evaluate all modules.

   run `python run_module_reuse_for_accurate_model.py` in `script/` to reuse modules to build a more accurate CNN model.

4. #### Reusing modules to build new CNN models for new tasks

   run `python run_module_reuse_for_new_task.py` in `script/` to build a composed CNN model for the new task.

   run `python run_train_model_for_new_task.py` in `script/` to train a new CNN model from scratch for the new task.

    

