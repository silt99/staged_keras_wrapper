from Dataset import Dataset, saveDataset, loadDataset
from CNN_Model import CNN_Model, loadModel, saveModel
from ECOC_Classifier import ECOC_Classifier
from Stage import Stage
from Staged_Network import Staged_Network, saveStagedModel, loadStagedModel

#from Food101 import Food101Dataset, loadFood101

from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.layers.advanced_activations import PReLU
from keras.models import Sequential, Graph

import numpy as np

import copy
import itertools
import time
import logging

def build_OneVsOneECOC_Stage(n_classes_ecoc, input_shape, ds, stage1_lr=0.01, ecoc_version=2):
    
    n_classes = len(ds.classes)
    labels_list = [str(l) for l in range(n_classes)]
    
    combs = tuple(itertools.combinations(labels_list, n_classes_ecoc))
    stage = list()
    outputs_list = list()
    
    count = 0
    n_combs = len(combs)
    for c in combs:
        t = time.time()
        
        # Create each one_vs_one classifier of the intermediate stage
        if(ecoc_version == 1):
            s = Stage(nInput=n_classes, nOutput=n_classes_ecoc, input_shape=input_shape, output_shape=[1, 2], type='One_vs_One_Inception', silence=True)
        elif(ecoc_version == 2):
            s = Stage(nInput=n_classes, nOutput=n_classes_ecoc, input_shape=input_shape, output_shape=[1, 2], type='One_vs_One_Inception_v2', silence=True)
        # Build input mapping
        input_mapping = dict()
        for i in range(n_classes):
            i_str = str(i) 
            if(i_str in c):
                input_mapping[i] = c.index(i_str)
            else:
                input_mapping[i] = None
        # Build output mask
        #output_mask = {'[0]': [0], '[1]': None}
        s.defineClassMapping(input_mapping)
        #s.defineOutputMask(output_mask)
        s.setOptimizer(lr=stage1_lr)
        s.silence = False
        stage.append(s)
        
        outputs_list.append('loss_OnevsOne/output')
        
        logging.info('Built model %s/%s for classes %s in %0.5s seconds.'%(str(count+1), str(n_combs), c, str(time.time()-t)))
        count +=1
               
    return [stage, outputs_list]
    
    
def build_OneVsAllECOC_Stage(n_classes_ecoc, input_shape, ds, stage1_lr):
    
    n_classes = len(ds.classes)
    
    stage = list()
    outputs_list = list()
    
    count = 0
    for c in range(n_classes):
        t = time.time()
        
        # Create each one_vs_one classifier of the intermediate stage
        s = Stage(nInput=n_classes, nOutput=n_classes_ecoc, input_shape=input_shape, output_shape=[1], type='One_vs_One_Inception', silence=True)
        # Build input mapping
        input_mapping = dict()
        for i in range(n_classes):
            if(i == c):
                input_mapping[i] = 0
            else:
                input_mapping[i] = 1
        # Build output mask
        output_mask = {'[0]': [0], '[1]': None}
        s.defineClassMapping(input_mapping)
        s.defineOutputMask(output_mask)
        s.setOptimizer(lr=stage1_lr)
        s.silence = False
        stage.append(s)
        
        outputs_list.append('loss_OnevsOne/output')
        
        logging.info('Built model %s/%s for classes %s in %0.5s seconds.'%(str(count+1), str(n_classes), '('+str(c) +' vs All)', str(time.time()-t)))
        count +=1
               
    return [stage, outputs_list]
    
    
def build_Specific_OneVsOneECOC_Stage(pairs, input_shape, ds, lr, ecoc_version=2):
    
    n_classes = len(ds.classes)

    stage = list()
    outputs_list = list()
    
    count = 0
    n_pairs = len(pairs)
    logging.info("Building " + str(n_pairs) +" classifiers...")
    
    for c in pairs:
        t = time.time()
        
        # Create each one_vs_one classifier of the intermediate stage
        if(ecoc_version == 1):
            s = Stage(nInput=n_classes, nOutput=2, input_shape=input_shape, output_shape=[2], type='One_vs_One_Inception', silence=True)
        elif(ecoc_version == 2):
            s = Stage(nInput=n_classes, nOutput=2, input_shape=input_shape, output_shape=[2], type='One_vs_One_Inception_v2', silence=True)
        # Build input mapping
        input_mapping = dict()
        for i in range(n_classes):
            if(i in c):
                input_mapping[i] = c.index(i)
            else:
                input_mapping[i] = None
        # Build output mask
        #output_mask = {'[0]': [0], '[1]': None}
        s.defineClassMapping(input_mapping)
        #s.defineOutputMask(output_mask)
        s.setOptimizer(lr=lr)
        s.silence = False
        stage.append(s)
        
        outputs_list.append('loss_OnevsOne/output')
        
        logging.info('Built model %s/%s for classes %s = %s in %0.5s seconds.'%(str(count+1), str(n_pairs), c, (ds.classes[c[0]], ds.classes[c[1]]), str(time.time()-t)))
        count +=1
               
    return [stage, outputs_list]
	
	
def build_Specific_OneVsOneVsRestECOC_Stage(pairs, input_shape, ds, lr, ecoc_version=2):
    
    n_classes = len(ds.classes)

    stage = list()
    outputs_list = list()
    
    count = 0
    n_pairs = len(pairs)
    for c in pairs:
        t = time.time()
        
        # Create each one_vs_one classifier of the intermediate stage
        if(ecoc_version == 1):
            s = Stage(nInput=n_classes, nOutput=3, input_shape=input_shape, output_shape=[3], type='One_vs_One_Inception', silence=True)
        elif(ecoc_version == 2):
            s = Stage(nInput=n_classes, nOutput=3, input_shape=input_shape, output_shape=[3], type='One_vs_One_Inception_v2', silence=True)
        # Build input mapping
        input_mapping = dict()
        for i in range(n_classes):
            if(i in c):
                input_mapping[i] = c.index(i)
            else:
                input_mapping[i] = 2
        # Build output mask
        #output_mask = {'[0]': [0], '[1]': None}
        s.defineClassMapping(input_mapping)
        #s.defineOutputMask(output_mask)
        s.setOptimizer(lr=lr)
        s.silence = False
        stage.append(s)
        
        outputs_list.append('loss_OnevsOne/output')
        
        logging.info('Built model %s/%s for classes %s = %s in %0.5s seconds.'%(str(count+1), str(n_pairs), c, (ds.classes[c[0]], ds.classes[c[1]]), str(time.time()-t)))
        count +=1
               
    return [stage, outputs_list]



def loadGoogleNetForFood101(nClasses=101, load_path='/media/HDD_2TB/CNN_MODELS/GoogleNet'):
    
    logging.info('Loading GoogLeNet...')
    
    # Build model (loading the previously converted Caffe's model)
    googLeNet = Stage(nClasses, nClasses, [224, 224, 3], [nClasses], type='GoogleNet', model_name='GoogleNet_Food101_retrained',
                    structure_path=load_path+'/Keras_model_structure.json', 
                    weights_path=load_path+'/Keras_model_weights.h5')
    
    return googLeNet



def prepareGoogleNet_Food101(model_wrapper):
    """    Prepares the GoogleNet model after its conversion from Caffe    """
    # Remove unnecessary intermediate optimizers
    layers_to_delete = ['loss2/ave_pool', 'loss2/conv', 'loss2/relu_conv', 'loss2/fc_flatten', 'loss2/fc', 
                        'loss2/relu_fc', 'loss2/drop_fc', 'loss2/classifier', 'output_loss2/loss', 
                        'loss1/ave_pool', 'loss1/conv', 'loss1/relu_conv', 'loss1/fc_flatten', 'loss1/fc', 
                        'loss1/relu_fc', 'loss1/drop_fc', 'loss1/classifier', 'output_loss1/loss']
    model_wrapper.removeLayers(layers_to_delete)
    model_wrapper.removeOutputs(['loss1/loss', 'loss2/loss'])


def prepareGoogleNet_Food101_Stage1(model_wrapper):
    """    Prepares the GoogleNet model for serving as the first Stage of a Staged_Netork    """
    # Adds a new output after the layer 'pool4/3x3_s2'
    model_wrapper.model.add_output(name='pool4', input='pool4/3x3_s2')


def prepareGoogleNet_Stage2(stage1, stage2):
    """    Removes the second part of the GoogleNet for inserting it into the second stage.    """
    
    # Remove all last layers (from 'inception_5a' included)
    layers_to_delete = ['inception_5a/1x1','inception_5a/relu_1x1','inception_5a/3x3_reduce','inception_5a/relu_3x3_reduce',
                    'inception_5a/3x3_zeropadding','inception_5a/3x3','inception_5a/relu_3x3','inception_5a/5x5_reduce',
                    'inception_5a/relu_5x5_reduce','inception_5a/5x5_zeropadding','inception_5a/5x5','inception_5a/relu_5x5',
                    'inception_5a/pool_zeropadding','inception_5a/pool','inception_5a/pool_proj','inception_5a/relu_pool_proj',
                    'inception_5a/output','inception_5b/1x1','inception_5b/relu_1x1','inception_5b/3x3_reduce','inception_5b/relu_3x3_reduce',
                    'inception_5b/3x3_zeropadding','inception_5b/3x3','inception_5b/relu_3x3','inception_5b/5x5_reduce',
                    'inception_5b/relu_5x5_reduce','inception_5b/5x5_zeropadding','inception_5b/5x5','inception_5b/relu_5x5',
                    'inception_5b/pool_zeropadding','inception_5b/pool','inception_5b/pool_proj','inception_5b/relu_pool_proj',
                    'inception_5b/output','pool5/7x7_s1','pool5/drop_7x7_s1','loss3/classifier_foodrecognition_flatten',
                    'loss3/classifier_foodrecognition','output_loss3/loss3']
    [layers, params] = stage1.removeLayers(copy.copy(layers_to_delete))
    # Remove softmax output
    stage1.removeOutputs(['loss3/loss3'])



    layers_to_delete_2 = ["conv1/7x7_s2_zeropadding", "conv1/7x7_s2", "conv1/relu_7x7", "pool1/3x3_s2_zeropadding", "pool1/3x3_s2", "pool1/norm1", "conv2/3x3_reduce", "conv2/relu_3x3_reduce", "conv2/3x3_zeropadding", "conv2/3x3", "conv2/relu_3x3", "conv2/norm2", "pool2/3x3_s2_zeropadding", "pool2/3x3_s2", "inception_3a/1x1", "inception_3a/relu_1x1", "inception_3a/3x3_reduce", "inception_3a/relu_3x3_reduce", "inception_3a/3x3_zeropadding", "inception_3a/3x3", "inception_3a/relu_3x3", "inception_3a/5x5_reduce", "inception_3a/relu_5x5_reduce", "inception_3a/5x5_zeropadding", "inception_3a/5x5", "inception_3a/relu_5x5", "inception_3a/pool_zeropadding", "inception_3a/pool", "inception_3a/pool_proj", "inception_3a/relu_pool_proj", "inception_3a/output", "inception_3b/1x1", "inception_3b/relu_1x1", "inception_3b/3x3_reduce", "inception_3b/relu_3x3_reduce", "inception_3b/3x3_zeropadding", "inception_3b/3x3", "inception_3b/relu_3x3", "inception_3b/5x5_reduce", "inception_3b/relu_5x5_reduce", "inception_3b/5x5_zeropadding", "inception_3b/5x5", "inception_3b/relu_5x5", "inception_3b/pool_zeropadding", "inception_3b/pool", "inception_3b/pool_proj", "inception_3b/relu_pool_proj", "inception_3b/output", "pool3/3x3_s2_zeropadding", "pool3/3x3_s2", "inception_4a/1x1", "inception_4a/relu_1x1", "inception_4a/3x3_reduce", "inception_4a/relu_3x3_reduce", "inception_4a/3x3_zeropadding", "inception_4a/3x3", "inception_4a/relu_3x3", "inception_4a/5x5_reduce", "inception_4a/relu_5x5_reduce", "inception_4a/5x5_zeropadding", "inception_4a/5x5", "inception_4a/relu_5x5", "inception_4a/pool_zeropadding", "inception_4a/pool", "inception_4a/pool_proj", "inception_4a/relu_pool_proj", "inception_4a/output", "inception_4b/1x1", "inception_4b/relu_1x1", "inception_4b/3x3_reduce", "inception_4b/relu_3x3_reduce", "inception_4b/3x3_zeropadding", "inception_4b/3x3", "inception_4b/relu_3x3", "inception_4b/5x5_reduce", "inception_4b/relu_5x5_reduce", "inception_4b/5x5_zeropadding", "inception_4b/5x5", "inception_4b/relu_5x5", "inception_4b/pool_zeropadding", "inception_4b/pool", "inception_4b/pool_proj", "inception_4b/relu_pool_proj", "inception_4b/output", "inception_4c/1x1", "inception_4c/relu_1x1", "inception_4c/3x3_reduce", "inception_4c/relu_3x3_reduce", "inception_4c/3x3_zeropadding", "inception_4c/3x3", "inception_4c/relu_3x3", "inception_4c/5x5_reduce", "inception_4c/relu_5x5_reduce", "inception_4c/5x5_zeropadding", "inception_4c/5x5", "inception_4c/relu_5x5", "inception_4c/pool_zeropadding", "inception_4c/pool", "inception_4c/pool_proj", "inception_4c/relu_pool_proj", "inception_4c/output", "inception_4d/1x1", "inception_4d/relu_1x1", "inception_4d/3x3_reduce", "inception_4d/relu_3x3_reduce", "inception_4d/3x3_zeropadding", "inception_4d/3x3", "inception_4d/relu_3x3", "inception_4d/5x5_reduce", "inception_4d/relu_5x5_reduce", "inception_4d/5x5_zeropadding", "inception_4d/5x5", "inception_4d/relu_5x5", "inception_4d/pool_zeropadding", "inception_4d/pool", "inception_4d/pool_proj", "inception_4d/relu_pool_proj", "inception_4d/output", "inception_4e/1x1", "inception_4e/relu_1x1", "inception_4e/3x3_reduce", "inception_4e/relu_3x3_reduce", "inception_4e/3x3_zeropadding", "inception_4e/3x3", "inception_4e/relu_3x3", "inception_4e/5x5_reduce", "inception_4e/relu_5x5_reduce", "inception_4e/5x5_zeropadding", "inception_4e/5x5", "inception_4e/relu_5x5", "inception_4e/pool_zeropadding", "inception_4e/pool", "inception_4e/pool_proj", "inception_4e/relu_pool_proj", "inception_4e/output", "pool4/3x3_s2_zeropadding", "pool4/3x3_s2"]


    # Remove initial layers
    [layers_, params_] = stage2.removeLayers(copy.copy(layers_to_delete_2))
    # Remove previous input
    stage2.removeInputs(['input_data'])
    # Add new input
    stage2.model.add_input(name='input_data', input_shape=(832,7,7))
    stage2.model.nodes[layers_to_delete[0]].previous = stage2.model.inputs['input_data']


    ## Insert layers into stage
    #stage2.model = Graph()
    ## Input
    #stage2.model.add_input(name='input_data', input_shape=(832,7,7))
    #for l_name,l,p in zip(layers_to_delete, layers, params):
    #    stage2.model.namespace.add(l_name)
    #    stage2.model.nodes[l_name] = l
    #    stage2.model.node_config.append(p)
    ##input = stage2.model.input # keep input
    ## Connect first layer with input
    #stage2.model.node_config[0]['input'] = 'input_data'
    #stage2.model.nodes[layers_to_delete[0]].previous = stage2.model.inputs['input_data']
    #stage2.model.input_config[0]['input_shape'] = [832,7,7]
    #    
    ## Output
    #stage2.model.add_output(name='loss3/loss3', input=layers_to_delete[-1])
    ##stage2.model.add_output(name='loss3/loss3_', input=layers_to_delete[-1])
    ##stage2.model.input = input # recover input


def simplifyDataset(ds, n_classes=50):
    
    logging.info("Simplifying %s from %d to %d classes." % (str(ds.name), len(ds.classes), n_classes))
    ds.classes = ds.classes[:n_classes]
    
    # reduce training
    kept_Y = list()
    kept_X = list()
    for i, y in enumerate(ds.Y_train):
        if(y < n_classes):
            kept_Y.append(y)
            kept_X.append(ds.X_train[i])
    ds.X_train = copy.copy(kept_X)
    ds.Y_train = copy.copy(kept_Y)
    ds.len_train = len(kept_X)
    
    # reduce validation
    kept_Y = list()
    kept_X = list()
    for i, y in enumerate(ds.Y_val):
        if(y < n_classes):
            kept_Y.append(y)
            kept_X.append(ds.X_val[i])
    ds.X_val = copy.copy(kept_X)
    ds.Y_val = copy.copy(kept_Y)
    ds.len_val = len(kept_X)
    
    # reduce test
    kept_Y = list()
    kept_X = list()
    for i, y in enumerate(ds.Y_test):
        if(y < n_classes):
            kept_Y.append(y)
            kept_X.append(ds.X_test[i])
    ds.X_test = copy.copy(kept_X)
    ds.Y_test = copy.copy(kept_Y)
    ds.len_test = len(kept_X)
