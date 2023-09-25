<template>

    <el-container>
        <el-header style="height: 85px;">
        <span style="margin-top: 0;margin-left: 5%;"> SEAMGrad Tool Demo</span>
        </el-header>
        <el-main>
            <h2 style="text-align: left;margin-left: 15%;float: left;margin-top: 2%;margin-bottom: 3%;">
                Model Modularization</h2>
            <el-button style="float:right;margin-right: 24%;margin-top: 2%;font-size: larger;width:220px;margin-bottom: 10px;" type="success" @click="JumpToBenchmark">
              Run Benchmark</el-button>

            <div class="form-body" style="margin-left: 20%;margin-right: 10%;">
                <el-form  label-width="220px" label-position="left" 
                ref="form" :model="form" id="selectForm" :inline="true" >
                    <!-- Algorithm Select-->
                    <el-form-item label="Algorithm:" class="selectItem" style="width: 100%;"> 
                        <el-select v-model="algorithm" placeholder="Please select an algorithm" @change="ResetModelandDataset">
                            <el-option label="SeaM" value="SEAM">  </el-option>
                            <el-option label="GradSplitter" value="GradSplitter">  </el-option>
                        </el-select>
                    </el-form-item>
                    
                    <!-- ModelReuseMethod(SEAM ONLY) -->
                    <el-form-item v-if="algorithm === 'SEAM'" 
                    label="Model Reuse Method:" class="selectItem" style="width: 100%;">  
                        <div class="chooseFromCards" style="width: 600px"> 
                          <el-row >
                            <el-col :span="12"><div >
                              <el-card style="width: 90%;height: 120px;" :body-style="{ padding: '0px 20px' } " 
                              :shadow="(directModelReuse === 'Multi-Class Classification' || directModelReuse === 'Binary Classification' )? 'always' : 'hover'">
                              <p style="font-weight: bolder;margin-top: 0;margin-bottom:15px;color:#606266;">Direct Model Reuse</p>
                              <el-radio-group v-model="directModelReuse" @change="ResetModelandDataset">
                                <el-radio label="Binary Classification" size="medium" style="margin-bottom: 15px;"> Binary Classification</el-radio>
                                <el-radio label="Multi-Class Classification" size="medium" style="margin-bottom: 15px;"> Multi-Class Classification</el-radio>
                              </el-radio-group>

                              </el-card>
                            </div></el-col>
                            <el-col :span="12"><div >
                              <el-card style="width: 90%;height: 120px;" :body-style="{ padding: '0px 20px' }"  
                              :shadow="(this.directModelReuse === 'Defect Inheritance')? 'always' : 'hover'">
                              <p style="font-weight: bolder;margin-top: 0;margin-bottom:15px;color:#606266">Indirect Model Reuse</p>
                              <el-radio-group v-model="directModelReuse" @change="ResetModelandDataset">
                                <el-radio label="Defect Inheritance" size="medium" style="margin-bottom: 15px;">Defect Inheritance</el-radio>
                              </el-radio-group>
                              </el-card>
                            </div></el-col>
                          </el-row>
                        </div>
                    </el-form-item>
                    
                    <!-- targetSuperclassIdx(SEAM+Multi-Class Classification ONLY) -->
                    <el-form-item v-if="algorithm === 'SEAM' && directModelReuse === 'Multi-Class Classification'" 
                    label="Target Superclass Idx:" class="selectItem" style="width: 100%;"> 
                        <el-select v-model="targetSuperclassIdx" 
                        placeholder="Please select a target superclass index">
                            <el-option  v-for="item in targetSuperclassIdxOptions" 
                            :key="item.value" :label="item.label" :value="item.value">
                            </el-option>
                        </el-select>
                    </el-form-item>
                    

                    <!-- targetClass(SEAM+Binary Classification) ONLY -->
                    <el-form-item v-if="algorithm === 'SEAM' && directModelReuse === 'Binary Classification'" 
                    label="Target Class Idx:" class="selectItem" style="width: 100%;">
                        <el-select v-model="targetClass" 
                        placeholder="Please select a target class">
                            <el-option  v-for="item in targetClassIdxOptions" 
                            :key="item.value" :label="item.label" :value="item.value">
                            </el-option>
                        </el-select>
                    </el-form-item> 

                    <!-- Epoch \ LearningRate \ alpha -->
                    <!-- EPOCH(GradSplitter) -->
                    <el-form-item v-if="algorithm !== 'SEAM'" label="Epochs:" class="selectItem" style="margin-right: 5%;">  
                      <el-tooltip class="item" effect="dark" content="The number of epochs must be an integer." placement="bottom-start">     
                      <el-input-number :disabled="algorithm===''"
                      v-model="epoch" :step="1" :min=1 :max="500" step-strictly></el-input-number></el-tooltip>
                    </el-form-item>
                    <!-- ALPHA(SEAM) -->
                    <el-form-item v-if="algorithm === 'SEAM'" label="Alpha:" class="selectItem"  style="margin-right: 5%;"> 
                      <el-tooltip class="item" effect="dark" content="Alpha must be non-negative." placement="bottom-start">                   
                      <el-input-number :disabled="algorithm===''"
                      v-model="alpha" :precision=2 :step="0.01" :min=0 :max="2" step-strictly></el-input-number> 
                    </el-tooltip>  
                    </el-form-item>

                    <!-- LEARNING RATE(SEAM) -->
                    <el-form-item v-if="algorithm === 'SEAM' " label="Learning Rate" class="selectItem" > 
                      <el-tooltip class="item" effect="dark" content="Learning rate is usually in the range of (0,1). " placement="bottom-start">     
                      <el-input-number :disabled="algorithm===''"
                      v-model="learningRate" :precision=3 :step="0.001" :min=0.001 :max="1" step-strictly></el-input-number></el-tooltip>
                    </el-form-item>
                

                    <!-- Model Selectionc-->
                    <el-form-item label="Model File:" class="selectItem" style="width: 100%;">
                      <el-select v-model="modelFile"
                        :disabled="modelFileUploadMode === '0' || algorithm === ''" placeholder="Please select a model">
                          <el-option  v-for="item in modelFileOptionsForMultiClass" 
                            :key="item.value" :label="item.label" :value="item.value">
                            </el-option>
                        </el-select>
                    </el-form-item>

                    <!-- Dataset Selection -->
                    <el-form-item label="Dataset File:" class="selectItem" style="width: 100%;">
                      <el-select v-model="datasetFile"
                        :disabled="datasetFileUploadMode === '0'|| algorithm === ''" placeholder="Please select a dataset">
                          <el-option  v-for="item in datasetFileOptionsForMultiClass" 
                            :key="item" :label="item" :value="item">
                            </el-option>
                        </el-select>
                    </el-form-item>

                </el-form>

                <!-- Upload -->
                <div style="width: 80%;margin-top: 40px;">
                  <el-button style="width:220px;font-size: larger;margin-bottom: 10px;" type="primary" @click="runModularization">
                  RUN</el-button>
                  <el-button style="float: right;font-size: larger;margin-bottom: 10px;" type="warning" @click="download"> 
                  Download Process Model</el-button>
                  <el-button style="float: right;font-size: larger;margin-bottom: 10px;" type="primary" @click="JumpToDeployment"> 
                  Module Deployment </el-button>
                </div>

                <!-- Result -->
                  <el-input readonly resize="none"
                    type="textarea"
                    rows="7"
                    v-model="logs"
                    style="width: 80%;margin-top: 40px;">
                  </el-input>
                <div v-if="modelResult">
                  Model Result: {{ modelResult.status }}
                </div>

                </div>
        </el-main>
    </el-container>
 
</template>

<script>
import axios from 'axios';
export default {
  sockets:{
  connect: function(){
    console.log('socket connected')
  },
  model_result: function(data){
    console.log('received model result: ' + JSON.stringify(data));
    this.modelResult = data;
    this.logs += 'Model Result: ' + JSON.stringify(data) + '\n';
  },
  message: function(data){
    console.log('received message: ' + data);
    this.logs += 'Message: ' + data + '\n';
  }
},
data() {
    return {
      form:{},

      activeTab: 'modularization',  // Currently active tab
      modelFile: null,  // The model file selected by the user
      datasetFile: null,  // The dataset file selected by the user
      algorithm: '',  // The algorithm selected by the user
      epoch: '1',  // The epoch entered by the user
      learningRate: '0.01',  // The learning rate entered by the user
      logs: '',  // Running logs
      isModelReady: false,  // Whether the model is ready to be downloaded
      modelFileUploadMode: '1',  // The upload mode for the model file (0: file upload, 1: select from list)
      datasetFileUploadMode: '1',  // The upload mode for the dataset file (0: file upload, 1: select from list)
      directModelReuse: '', //To save the choose of Direct model reuse
      targetClass: '',  // The target class selected by the user
      alpha: '1',  // The alpha value entered by the user, default to 1
      targetSuperclassIdx: '',  // The target superclass index selected by the user

      message: '',
      modelStatus: '',
      modelResult: null,


      targetSuperclassIdxOptions:[
        {value:"0", label:"0"},{value:"1", label:"1"},{value:"2", label:"2"},{value:"3", label:"3"},{value:"4", label:"4"},
      ],
      targetClassIdxOptions:[
        {value:"0", label:"0"},{value:"1", label:"1"}
      ]
    };
  },


  computed: {
    // To make sure multi-class has the two model
    modelFileOptionsForMultiClass() {
      switch(this.directModelReuse){
        case 'Multi-Class Classification': 
          // return ['ResNet20', 'ResNet50'] 
          return [{
            value:'resnet20', label:'ResNet20'
          },{
            value:'resnet50', label:'ResNet50'
          }]
        case 'Defect Inheritance':
          // return ['resnet18']
          return[{value:'resnet18', label:'ResNet18'}]
        default:
            return this.modelFileOptions
      }
    },
    // To make sure models corresponds to their datasets
    datasetFileOptionsForMultiClass() {
      if (this.directModelReuse === 'Multi-Class Classification') {
        if (this.modelFile === 'ResNet20') {
          return ['cifar100'];
        } else if (this.modelFile === 'ResNet50') {
            return ['ImageNet'];
          }
        }
      else if (this.directModelReuse === 'Defect Inheritance'){
        return ['mit67']
      }
      return this.datasetFileOptions;
    },

    isEpochValid() {
      const epochNumber = Number(this.epoch);
      return Number.isInteger(epochNumber) && this.epoch > 0;
    },
    isLearningRateValid() {
      return this.learningRate > 0;
    },
    modelFileOptions() {
    // return this.algorithm === 'SEAM' ? ['vgg16', 'resnet20'] : ['simcnn', 'rescnn', 'incecnn'];
      return this.algorithm === 'SEAM' ? 
        [{value:'vgg16', label:'VGG16'}, {value:'resnet20', label:'ResNet20'}] 
        : [{value:'simmcnn', label:'SimCNN'}, {value:'rescnn', label:'ResCNN'}, {value:'incecee', label:'InceCNN'}]
    },
    datasetFileOptions() {
      return this.algorithm === 'SEAM' ? ['cifar10', 'cifar100'] : ['cifar10', 'svhn'];
    },
    isAlphaValid() {
      return this.alpha >= 0;
    },

  },
  methods: {
    JumpToDeployment(){      this.$router.push('/deployment')    },
    JumpToBenchmark(){      this.$router.push('/benchmark')    },
    ResetModelandDataset(){
      if(this.datasetFileUploadMode === '1' ){this.datasetFile = null;};
      if(this.modelFileUploadMode === '1'){this.modelFile = null}

    },

    // The handler function when the user selects a model file
    onModelFileChange(event) {
      this.modelFile = event.target.files[0];
    },
    // The handler function when the user selects a dataset file
    onDatasetFileChange(event) {
      this.datasetFile = event.target.files[0];
    },
    // The handler function when the user clicks the run button
    run() {
      if (!this.modelFile) {
        window.alert('Please select a model file.');
        return;
      }

      if (!this.datasetFile) {
        window.alert('Please select a dataset file.');
        return;
      }

      if (!this.algorithm) {
        window.alert('Please select an algorithm.');
        return;
      }

      if (!this.isEpochValid) {
        window.alert('Integer');
        return;
      }

      if (!this.isLearningRateValid) {
        window.alert('Non-negative.');
        return;
      }

      // If all conditions are satisfied, continue running the model...
      window.alert('Running...');
      // Here execute the running code of the model, you may need to use Axios or other HTTP libraries to interact with the back-end server
      // When the server returns logs, you can add them to this.logs

      // If all conditions are satisfied, continue running the model...
        // After running the model, set isModelReady to true
        this.isModelReady = true;

        const data = {
        modelFile: this.modelFile,
        datasetFile: this.datasetFile,
        algorithm: this.algorithm,
        epoch: this.epoch,
        learningRate: this.learningRate,
        directModelReuse: this.directModelReuse,
        targetClass: this.targetClass,
        alpha: this.alpha,
        targetSuperclassIdx: this.targetSuperclassIdx,
      };

      // Send POST requests to Flask
      axios.post('http://localhost:5000/run_model', data)
        .then(response => {
          // success, return results
          this.logs = response.data.logs;
          this.isModelReady = response.data.isModelReady;
        })
        .catch(error => {
          // return errors
          console.error(error);
          this.logs = 'An error occurred while running the model.';
        });

    },
    runModularization(){
      this.$message('RUNNING...', {center:true, showConfirmButton:false})
      this.checkRunInformation()
      const data = {
        modelFile: this.modelFile,
        datasetFile: this.datasetFile,
        algorithm: this.algorithm,
        epoch: this.epoch,
        learningRate: this.learningRate,
        directModelReuse: this.directModelReuse,
        targetClass: this.targetClass,
        alpha: this.alpha,
        targetSuperclassIdx: this.targetSuperclassIdx,
      };
      console.log(data)


      // Send POST requests to Flask
      axios.post('http://localhost:5000/run_model', data)
        .then(response => {
          // success, return results
          this.logs = response.data.logs;
          this.isModelReady = response.data.isModelReady;
        })
        .catch(error => {
          // return errors
          console.error(error);
          this.logs = 'An error occurred while running the model.';
        });
    },
    download() {
      axios({
        method: 'GET',
        url: 'http://localhost:5000/download',  // Flask后端下载路由
        responseType: 'blob'  // 表明返回类型是 Blob
      })
      .then(response => {
        // 创建一个不可见的 'a' 标签用于下载
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'lr_head_mask_0.1_0.01_alpha_1.0.pth');  // 你的文件名
        document.body.appendChild(link);
        link.click();
      })
      .catch(err => {
        console.log(err);
      });
    },  
    checkRunInformation(){
      console.log('form:'+this.form)
      console.log('algorithm:'+this.algorithm)
      console.log('directModelReuse:'+this.directModelReuse)
      console.log('targetSuperclassIdx:'+this.targetSuperclassIdx)
      console.log('targetClass:'+this.targetClass)
      console.log('epoch:'+this.epoch)
      console.log('alpha:'+this.alpha)
      console.log('learningRate:'+this.learningRate)
      console.log('modelFile:'+this.modelFile)
      console.log('datasetFile:'+this.datasetFile)
    },
  },
};

</script>

<style>
.el-container {
    height: 100%; 
    width: 100%;
    font-family: Arial, sans-serif;
}
.el-header, .el-footer {
    background-color: #b2dfdb;
    color: #333;

    text-align: left;
    font-size: x-large;
    font-weight: bolder;
    line-height: 90px;
}
.el-main {
    /* background-color: #E9EEF3; */
    color: #333;
    /* line-height: 20px; */

}
.el-form-item {
    margin-right: 100px;
}
.form-body {
    margin-top: 60px;
}
.selectItem .el-form-item__label{
    font-size: large;
    font-weight: bold;
}
.direct-model-reuse .el-form-item__content{
    font-size: large;
}
.direct-model-reuse .el-radio{
    font-size: large;
}
.modelDataset .el-radio /deep/ .el-radio__label{
  min-width: 100px;
}

</style>