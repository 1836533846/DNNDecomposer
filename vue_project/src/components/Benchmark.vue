<template>

    <el-container>
        <el-header style="height: 85px;">
        <span style="margin-top: 0;margin-left: 5%;" @click="jumptohome"> SEAMGrad Tool Demo</span>
        </el-header>
        <el-main>
            <h2 style="text-align: left;margin-left: 15%;">
                Run Benchmark</h2>

            <div class="main-body" style="margin-left: 10%;margin-right: 10%;margin-top: 50px;">
                <el-divider></el-divider>
                <el-row>
                    <!-- SEAM -->
                    <el-col :span="12"><div>
                        <h3 style="margin-left: 10%;margin-right: 10%;margin-top: 20px;float:left;width:100px">
                            SEAM</h3>
                        <el-button style="float:right;margin-top: 10px;margin-right: 10%;width: 200px;" type="success"> RUN Benchmark </el-button>


                        <div class="tableBody" style="width: 95%;margin-left: 5%;" >
                            <el-table :data="tableDataSEAM" stripe style="width: 100%;" :span-method="objectSpanMethod" :header-cell-style="{textAlign: 'center', height: '100px'}" :cell-style="{'text-align':'center'}">
                                <el-table-column :render-header="renderheader" 
                                    prop="targetProblem" :label="'Target // Problem'" width="175">
                                </el-table-column>
                                <el-table-column :render-header="renderheader" 
                                    prop="modelName" :label="'Model // Name'" width="160">
                                </el-table-column>
                                <el-table-column :render-header="renderheader" 
                                    prop="learningRate" :label="'Learning // Rate'" >
                                </el-table-column>
                                <el-table-column :render-header="renderheader" 
                                    prop="alpha" :label="'Alpha'" >
                                </el-table-column>
                            </el-table>

                        </div>
                    </div></el-col>

                    <!-- GRAD-->
                    <el-col :span="12"><div >
                        <h3 style="margin-left: 10%;margin-right: 10%;margin-top: 20px;float:left;width:100px">
                            GradSplitter</h3>
                        <el-button style="float:right;margin-top: 10px;margin-right: 10%;width: 200px;" type="success"> RUN Benchmark </el-button>
                        
                        <div class="tableBody" style="width: 95%;margin-left: 5%;" >
                            <el-table :data="tableDataGrad" stripe style="width: 100%"  :header-cell-style="{textAlign: 'center', height: '100px'}" :cell-style="{'text-align':'center'}">
                                <el-table-column 
                                    prop="modelName" label="Model Name" width="150">
                                </el-table-column>
                                <el-table-column :render-header="renderheader" 
                                    prop="learningRate_head" :label="'Learning Rate // (head)'">
                                </el-table-column>
                                <el-table-column  :render-header="renderheader" width="90"
                                    prop="learningRate_modularity" :label="'Learning Rate // (modular)'">
                                </el-table-column>
                                <el-table-column :render-header="renderheader"
                                    prop="epochs_head" :label="'Epochs // (head)'">
                                </el-table-column>
                                <el-table-column :render-header="renderheader"
                                    prop="epochs_modularity" :label="'Epochs // (modular)'">
                                </el-table-column>
                            </el-table>

                        </div>
                    </div></el-col>
                </el-row>
            </div>
            
            

        </el-main>
    </el-container>
 
</template>


<script>
export default {
    data () {
        return{
            dataTable:{modelName:'SimCNN', dataset:'CIFAR-10', epochs:'100',lr:'0.01', alogrithm:'GradSplitter'},
            tableDataSEAM: [{
                targetProblem: 'Binary Classification',
                modelName: 'VGG16-CIFAR10',
                learningRate: '0.01',
                alpha:'1.00',
            }, {
                targetProblem: 'Binary Classification',
                modelName: 'VGG16-CIFAR100',
                learningRate: '0.05',
                alpha:'1.50',
            }, {
                targetProblem: 'Binary Classification',
                modelName: 'ResNet20-CIFAR10',
                learningRate: '0.05',
                alpha:'1.00',
            }, {
                targetProblem: 'Binary Classification',
                modelName: 'ResNet20-CIFAR100',
                learningRate: '0.12',
                alpha:'1.50',
            }, {
                targetProblem: 'Multi-class Classification',
                modelName: 'ResNet20-CIFAR100',
                learningRate: '0.10',
                alpha:'2.00',
            }, {
                targetProblem: 'Multi-class Classification',
                modelName: 'ResNet20-ImageNet',
                learningRate: '0.05',
                alpha:'2.00',
            }],
            tableDataGrad:[{
                modelName: 'SimCNN-CIFAR10',
                learningRate_head: '0.01',
                learningRate_modularity: '0.001',
                epochs_head:'5',
                epochs_modularity: '140',
            },{
                modelName: 'SimCNN-SVHN',
                learningRate_head: '0.01',
                learningRate_modularity: '0.001',
                epochs_head:'5',
                epochs_modularity: '140',
            },{
                modelName: 'ResCNN-CIFAR10',
                learningRate_head: '0.01',
                learningRate_modularity: '0.001',
                epochs_head:'5',
                epochs_modularity: '140',
            },{
                modelName: 'ResCNN-SVHN',
                learningRate_head: '0.01',
                learningRate_modularity: '0.001',
                epochs_head:'5',
                epochs_modularity: '140',
            } ,{
                modelName: 'InceCNN-CIFAR10',
                learningRate_head: '0.01',
                learningRate_modularity: '0.001',
                epochs_head:'5',
                epochs_modularity: '140',
            },{
                modelName: 'InceCNN-SVHN',
                learningRate_head: '0.01',
                learningRate_modularity: '0.001',
                epochs_head:'5',
                epochs_modularity: '140',
            }],
        
        }

    },
    methods: {
        objectSpanMethod({ row, column, rowIndex, columnIndex }) {
            if (columnIndex === 0) {
                if(rowIndex == 0){return {rowspan:4, colspan:1}}
                else if(rowIndex == 4){return {rowspan:2, colspan:1}}
                return  {rowspan:0, colspan:0}
            }
        },
        renderheader(h, { column }) { // renderheader函数得用到el-table-column上，而不是el-table
            return h("span", {}, [
                h("span", {}, column.label.split("//")[0]), // 其中//也可以用其他符号替代
                h("br"),
                h("span", {}, column.label.split("//")[1]),
            ]);
        },
        jumptohome(){
            this.$router.push('/modularization')
        },

    }


}



</script>

<style scoped>
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

.tableBody .el-table .cell {
  white-space: pre-line;
}
</style>