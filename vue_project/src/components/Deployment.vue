<template>

    <el-container>
        <el-header style="height: 85px;">
        <span style="margin-top: 0;margin-left: 5%;"  @click="jumptohome"> SeaMGrad Tool Demo</span>
        </el-header>
        <el-main>
            <h2 style="text-align: left;margin-left: 15%;margin-top: 2%;margin-bottom: 3%;">
                <i class="el-icon-arrow-left" style="margin-right: 5px;" @click="jumptohome"></i>
                Model Deployment</h2>
            <div style="text-align: center;">
                <div class="DatatTable" style="margin-left: 20%;margin-right: 20%;margin-top: 40px;">
                <el-descriptions title="Model Modularization Information" border>
                    <!-- Algo, model and dataset-->
                    <el-descriptions-item label="Algortihm" labelStyle="width:15%" contentStyle="width:15%">
                        <el-tag effect="dark" :hit="true" :color="dataTable.algorithm === 'SEAM' ?'#00bcd4':'#ffc107'" 
                        style="font-weight: bolder;" >
                            {{ dataTable.algorithm }}</el-tag></el-descriptions-item>
                    <el-descriptions-item label="Model" labelStyle="width:13%" contentStyle="width:17%">{{dataTable.modelFile}}</el-descriptions-item>
                    <el-descriptions-item label="Dataset" labelStyle="width:13%" contentStyle="width:17%">{{ dataTable.datasetFile }}</el-descriptions-item>
                    
                   
                    <!-- Epoch(Grad) -->
                    <el-descriptions-item v-if="dataTable.algorithm === 'GradSplitter'" 
                        label="Epochs">{{ dataTable.epoch }}</el-descriptions-item>
                    
                    <!-- Target Class(SEAM) -->
                    <el-descriptions-item v-if="dataTable.algorithm === 'SEAM'" span="6"
                        label="Model Reuse Method">{{ dataTable.directModelReuse }}</el-descriptions-item>
                    <el-descriptions-item v-if="dataTable.algorithm === 'SEAM' && dataTable.directModelReuse === 'Multi-Class Classification'"
                        label="Target Superclass Idx">{{ dataTable.targetSuperclassIdx }}</el-descriptions-item>
                    <el-descriptions-item v-if="dataTable.algorithm === 'SEAM' && dataTable.directModelReuse === 'Binary Classification'"
                        label="Target Class Idx">{{ dataTable.targetClass }}</el-descriptions-item>
                    
                    <!-- learningRate(Both) -->
                    <el-descriptions-item label="Learning rate">{{ dataTable.learningRate }}</el-descriptions-item>
                    
                    <!-- alpha(SEAM) -->
                    <el-descriptions-item v-if="dataTable.algorithm === 'SEAM'" 
                        label="Alpha">{{ dataTable.alpha }}</el-descriptions-item>
                </el-descriptions>
            </div>
            
            <h4 style="text-align: left;margin-left: 20%;margin-right: 20%;margin-top: 80px;">
                Model Deployment</h4>
            
            <div style="margin-left: 20%;margin-right: 20%;margin-top: 20px;text-align: left;">
                <el-row>
                    <el-col :span="8">
                    <div class="uploadFig" >
                        <el-upload
                            class="uploadSinglePicture"
                            action="#" 
                            accept="image/jpg, image/jpeg, image/png"
                            :limit="1"
                            :on-preview="handlePreview"
                            :on-remove="handleRemove"
                            :before-remove="beforeRemove"
                            :on-exceed="handleExceed"
                            :file-list="fileList"   
                        >
                            <el-button type="primary"  slot="trigger" style="margin-bottom: 10px;"> 
                                Browse... </el-button>
                            <el-button style="margin-left: 10px;margin-bottom: 10px;" type="warning" 
                                @click="submitUpload">Run</el-button>
                            <div slot="tip" class="el-upload__tip">※Upload jpg/jpeg/png files with a size less than 5MB.</div>
                            <img v-if="imageUrl" :src="imageUrl" style="width:90%;max-height: 217px;">
                        </el-upload>
                    </div> </el-col>


                    <!-- result -->
                    <el-col :span="16"><div style="text-align: right;">
                        <el-input readonly resize="none"
                            type="textarea"
                            rows="12"
                            v-model="logs"
                            style="width: 96%;margin-right: 0px;">
                        </el-input>
                        <div v-if="modelResult">
                            Model Result: {{ modelResult.status }}
                        </div>
                    
                    </div></el-col>
                </el-row>
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
    created (){
        var modelFile = sessionStorage.getItem("modelFile");
        var datasetFile = sessionStorage.getItem("datasetFile");
        var algorithm = sessionStorage.getItem("algorithm");
        var epoch = sessionStorage.getItem("epoch");
        var learningRate = sessionStorage.getItem("learningRate");
        var directModelReuse = sessionStorage.getItem("directModelReuse");
        var targetClass = sessionStorage.getItem("targetClass");
        var alpha = sessionStorage.getItem("alpha");
        var targetSuperclassIdx = sessionStorage.getItem("targetSuperclassIdx");
        this.dataTable.modelFile = modelFile
        this.dataTable.datasetFile = datasetFile
        this.dataTable.algorithm = algorithm
        this.dataTable.epoch = epoch
        this.dataTable.learningRate = learningRate
        this.dataTable.directModelReuse = directModelReuse
        this.dataTable.targetClass = targetClass
        this.dataTable.alpha = alpha
        this.dataTable.targetSuperclassIdx = targetSuperclassIdx

        
        console.log(this.dataTable)
    },
    data () {
        return{
            // dataTable:
            //     {algorithm:'GradSplitter', //test Data Grad
            //     modelFile:'SimCNN', datasetFile:'CIFAR-10',learningRate:'0.01',
            //     epoch:'100', },
            dataTable:
                {algorithm:'SEAM', //test Data SEAM
                modelFile:'ResNet20', datasetFile:'CIFAR-10', learningRate:'0.01',
                directModelReuse:'Multi-Class Classification', alpha:'1.00' ,targetSuperclassIdx:'2'},
            // dataTable:
            //     {algorithm:'SEAM', //test Data SEAM
            //     modelFile:'ResNet20', datasetFile:'CIFAR-10', learningRate:'0.01',
            //     directModelReuse:'Defect Inheritance', alpha:'1.00' },
            fileList:[],
            modelResult: null,
            logs: '',  // Running logs 
            imageUrl: 'https://t7.baidu.com/it/u=4162611394,4275913936&fm=193&f=GIF'     

        }

    },
    methods: {
        setParam(){},
        // Upload single picture
        handleRemove(file, fileList) {
            console.log(file, fileList);
        },
        handlePreview(file) {
            console.log('__file:');
            console.log(file)
            this.fileList.push(file)
            console.log(this.fileList)
        },
        handleExceed(files, fileList) {
            this.$message.warning(`Limit one picture only.`);
            console.log(fileList)
        },
        beforeRemove(file, fileList) {
            return this.$confirm(`Cancel the transfert of ${ file.name } ？`);
        },
        submitUpload(file){
            console.log('file:'+file)
            console.log('filelist:'+this.fileList)
        },
        handleChange(file, fileList){
            console.log('handle change')
            this.fileList = fileList
            console.log(this.fileList)
        },
        jumptohome(){
            this.$router.push('/modularization')
        },
    },


}



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
.el-tag--dark.is-hit {
    border:0;
}
.el-upload --text {
    align-items: left;
}
</style>