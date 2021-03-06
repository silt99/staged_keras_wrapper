from keras_wrapper.dataset import Dataset, saveDataset, loadDataset
from keras_wrapper.cnn_model import CNN_Model, saveModel, loadModel

from keras.layers import Dense
from keras.engine.training import Model

import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


def main_test():
    
    #loadFlickr8k() # load Flickr8k dataset for Image Description
    
    #loadMSVD() # load MSVD dataset for Video Description

    loadFood101() # load Food101 dataset for Image Classification

    
    
    # Build basic model for image classification
    classifyFood101()
    

    
    
#################################
#
#    Model building functions
#
#################################
    
def classifyFood101():
    
    logging.info('Defining CNN model and training it.')
    
    # Load food classification dataset
    dataset_name = 'Food101'
    ds = loadDataset('Datasets/Dataset_'+dataset_name+'.pkl')
    # The network we are going to use needs an image input size of [224,224,3]
    # for this reason we have to communicate this to the dataset instance in charge of loading the data
    ds.img_size_crop['images'] = [224,224,3]
    
    
    # Create VGG model and load weights
    model_name = 'VGG_16_FunctionalAPI'
    net = CNN_Model(type='VGG_16_FunctionalAPI', model_name=model_name, input_shape=[224, 224, 3],
                    weights_path='/media/HDD_2TB/CNN_MODELS/VGG/vgg16_weights.h5', 
                    seq_to_functional=True) # we are setting the weights of a Sequential model into a FunctionalAPI one
    
    
    # Reformat net output layer for the number of classes in our dataset
    n_classes = len(ds.classes['labels'])
    vis_input = net.model.get_layer('vis_input').output # input layer
    drop = net.model.get_layer('last_dropout').output   # layer before final FC
    output = Dense(n_classes, activation='softmax', name='output')(drop)  # redefine FC-softmax layer
    net.model = Model(input=vis_input, output=output) # define inputs and outputs
    
    # Compile
    net.setOptimizer(lr=0.001, metrics=['accuracy'])
    
                    
    # Define the inputs and outputs mapping from our Dataset instance to our CNN_Model instance
    # set input and output mappings from dataset to network
    pos_images = ds.types_inputs.index('image')
    pos_labels = ds.types_outputs.index('categorical')
    
    # the first input of our dataset (pos_images) will also be the first input of our model (named vis_input)
    inputMapping = {'vis_input': pos_images}
    net.setInputsMapping(inputMapping)
    
    # the first output of our dataset (pos_labels) will also be the first output of our model (named output)
    outputMapping = {'output': pos_labels}
    net.setOutputsMapping(outputMapping, acc_output='output')

    
    # Save model
    saveModel(net, 0)
    
    # Load model
    net = loadModel('Models/'+model_name, 0)
    # the model must be compiled again when loaded
    net.setOptimizer(lr=0.001, metrics=['accuracy'])
    
    
    # Apply short training (1 epoch)
    training_params = {'n_epochs': 1, 'batch_size': 50, 
                       'lr_decay': 2, 'lr_gamma': 0.8, 
                       'epochs_for_save': 1, 'verbose': 1, 'eval_on_sets': ['val']}
    #net.trainNet(ds, training_params)
    
    
    # Test network on test set
    test_params = {'batch_size': 50}
    #net.testNet(ds, test_params)
    
    # Predict network on all sets
    test_params['predict_on_sets'] = ['val']
    predictions = net.predictNet(ds, test_params)
    
    logging.info("Done")
    
    
    
#################################
#
#    Data loading functions
#
#################################

def loadFlickr8k():
    
    logging.info('Loading Flickr8k dataset')
    
    # Build basic dataset structure
    #    we assign it a name and the path were the images are stored
    
    base_path = '/media/HDD_2TB/DATASETS/Flickr8k/'
    name = 'Flickr8k_ImageDescription'
    ds = Dataset(name, base_path+'Flicker8k_Dataset')
    max_text_len = 35
    
    # Let's load the train, val and test splits of the descriptions (outputs)
    #    the files include a description per line 
    #    and a set of 5 consecutive descriptions correspond to a single input image
    
    ds.setOutput(base_path+'text/train_descriptions.txt', 'train',
               type='text', id='descriptions',
               tokenization='tokenize_basic', build_vocabulary=True, max_text_len=max_text_len)
    ds.setOutput(base_path+'text/val_descriptions.txt', 'val',
               type='text', id='descriptions',
               tokenization='tokenize_basic', max_text_len=max_text_len)
    ds.setOutput(base_path+'text/test_descriptions.txt', 'test',
               type='text', id='descriptions',
               tokenization='tokenize_basic', max_text_len=max_text_len)
    
    
    # Let's load the associated images (inputs)
    #    we must take into account that in this dataset we have 5 sentences per image, 
    #    for this reason we introduce the parameter 'repeat_set'=5
    
    ds.setInput(base_path+'text/Flickr_8k.trainImages.txt', 'train',
               type='image', id='images', repeat_set=5)
    ds.setInput(base_path+'text/Flickr_8k.devImages.txt', 'val',
               type='image', id='images', repeat_set=5)
    ds.setInput(base_path+'text/Flickr_8k.testImages.txt', 'test',
               type='image', id='images', repeat_set=5)
    
    # Now let's set the dataset mean image for preprocessing the data
    ds.setTrainMean(mean_image=[122.6795, 116.6690, 104.0067], id='images')
    
    # We have finished loading the dataset, now we can store it for using it in the future
    saveDataset(ds, 'Datasets')
    
    
    # We can easily recover it with a single line
    ds = loadDataset('Datasets/Dataset_'+name+'.pkl')
    

    
    # Lets recover the first batch of data
    [X, Y] = ds.getXY('train', 10)
    logging.info('Sample data loaded correctly.')
    print
    
    
def loadMSVD():
    
    logging.info('Loading MSVD dataset')
    
    # Build basic dataset structure
    #    we assign it a name and the path were the images are stored
    
    base_path = '/media/HDD_2TB/DATASETS/MSVD/'
    name = 'MSVD_VideoDescription'
    ds = Dataset(name, base_path)
    max_text_len = 35
    

    # Let's load the train, val and test splits of the descriptions (outputs)
    #    the files include a description per line. In this dataset a variable number
    #    of descriptions per video are provided.
    
    ds.setOutput(base_path+'train_descriptions.txt', 'train',
               type='text', id='descriptions',
               tokenization='tokenize_basic', build_vocabulary=True, max_text_len=max_text_len)
    ds.setOutput(base_path+'val_descriptions.txt', 'val',
               type='text', id='descriptions',
               tokenization='tokenize_basic', max_text_len=max_text_len)
    ds.setOutput(base_path+'test_descriptions.txt', 'test',
               type='text', id='descriptions',
               tokenization='tokenize_basic', max_text_len=max_text_len)
    
    
    # Let's load the associated videos (inputs)
    #    we must take into account that in this dataset we have a different number of sentences per video, 
    #    for this reason we introduce the parameter 'repeat_set'=num_captions, where num_captions is a list
    #    containing the number of captions in each video.
    
    num_captions_train = np.load(base_path+'train_descriptions_counts.npy')
    num_captions_val = np.load(base_path+'val_descriptions_counts.npy')
    num_captions_test = np.load(base_path+'test_descriptions_counts.npy')
    
    ds.setInput([base_path+'train_imgs_list.txt', base_path+'train_imgs_counts.txt'],
                'train', type='video', id='videos', 
                repeat_set=num_captions_train)
    ds.setInput([base_path+'val_imgs_list.txt', base_path+'val_imgs_counts.txt'], 
                'val', type='video', id='videos', 
                repeat_set=num_captions_val)
    ds.setInput([base_path+'test_imgs_list.txt', base_path+'test_imgs_counts.txt'], 
                'test', type='video', id='videos', 
                repeat_set=num_captions_test)
    
    
    # Now let's set the dataset mean image for preprocessing the data
    ds.setTrainMean(mean_image=[122.6795, 116.6690, 104.0067], id='videos')
    
    # We have finished loading the dataset, now we can store it for using it in the future
    saveDataset(ds, 'Datasets')
    
    
    # We can easily recover it with a single line
    ds = loadDataset('Datasets/Dataset_'+name+'.pkl')
    

    
    # Lets recover the first batch of data
    [X, Y] = ds.getXY('train', 10)
    logging.info('Sample data loaded correctly.')
    print
    
    
def loadFood101():
    
    logging.info('Loading Food101 dataset')
    logging.info('INFO: in order to load this dataset it must be placed in ../data/Food101/images/ after downloading it form https://www.vision.ee.ethz.ch/datasets_extra/food-101/')
    
    base_path = '../data/Food101/'
    name = 'Food101'
    ds = Dataset(name, base_path+'images')
    
    # Insert inputs (images)
    ds.setInput(base_path+'meta/train_split.txt', 'train',
               type='image', id='images', img_size_crop=[227, 227, 3])
    ds.setInput(base_path+'meta/val_split.txt', 'val',
               type='image', id='images')
    ds.setInput(base_path+'meta/test.txt', 'test',
               type='image', id='images')
    
    # Insert outputs (labels)
    ds.setOutput(base_path+'meta/train_labels.txt', 'train',
               type='categorical', id='labels')
    ds.setOutput(base_path+'meta/val_labels.txt', 'val',
               type='categorical', id='labels')
    ds.setOutput(base_path+'meta/test_labels.txt', 'test',
               type='categorical', id='labels')
    
    # Set list of classes (strings)
    ds.setClasses(base_path+'meta/classes.txt', 'labels')
    
    # Now let's set the dataset mean image for preprocessing the data
    ds.setTrainMean(mean_image=[122.6795, 116.6690, 104.0067], id='images')
    
    
    # We have finished loading the dataset, now we can store it for using it in the future
    saveDataset(ds, 'Datasets')
    
    
    # We can easily recover it with a single line
    ds = loadDataset('Datasets/Dataset_'+name+'.pkl')
    
    
    # Lets recover the first batch of data
    [X, Y] = ds.getXY('train', 10)
    logging.info('Sample data loaded correctly.')
    print
    
    
    
main_test()
