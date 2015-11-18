'''
Created on Nov 16, 2015

@author: niko
'''

import tensorflow as tf

import input_data

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')

def runSimpleNN(mnist):
    sess = tf.InteractiveSession()

    x = tf.placeholder("float", shape=[None, 784])
    y_ = tf.placeholder("float", shape=[None, 10])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))
    
    sess.run(tf.initialize_all_variables())
    
    y = tf.nn.softmax(tf.matmul(x, W) + b)
    cross_entropy = -tf.reduce_sum(y_*tf.log(y))
    
    train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)
    
    for _ in range(1000):
        batch = mnist.train.next_batch(50)
        train_step.run(feed_dict={x: batch[0], y_: batch[1]})
        
    correct_prediction = tf.equal(tf.argmax(y,1), tf.arg_max(y_, 1))
    
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    print accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels})
    
def runCNN(mnist):
    sess = tf.InteractiveSession()

    x = tf.placeholder("float", shape=[None, 784])
    y_ = tf.placeholder("float", shape=[None, 10])
    
    '''
    weight_variable([n1, n2, n3, n4])
    n1, n2 = patch size (n1xn2)
    n3 = number of input channels
    n4 = number of output channels
    '''
    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])
    
    '''
    reshape the image to 4d tensor [n1, n2, n3, n4]
    n2, n3 = image size (n2xn3)
    n4 = number of color channels
    '''
    x_image = tf.reshape(x, [-1,28,28,1])
    
    #FIRST CONVOLUTION LAYER
    #convolve x_image with weight tensor, add the bias, apply ReLU function, and finally add max pool
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)
    
    #SECOND CONVOLUTION LAYER
    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])
    
    #convolve the output of first convolution layer with weights of second convolution layer
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)
    
    #DENSELY CONNECTED LAYER
    #The image has been reduced to size 7x7: the first pooling reduced the image to 14x14 as it applied 2x2 max pooling and the second pooling layer further reduced the image size from 14x14 to 7x7 due to 2x2 pooling
    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    
    #Dropout
    keep_prob = tf.placeholder("float")
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    
    #readout layer
    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])

    y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    
    #train and evaluate the model
    cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    sess.run(tf.initialize_all_variables())
    for i in range(20000):
        batch = mnist.train.next_batch(50)
        if i%100 == 0:
            train_accuracy = accuracy.eval(feed_dict={
                x:batch[0], y_: batch[1], keep_prob: 1.0})
            print "step %d, training accuracy %g"%(i, train_accuracy)
            train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
    
    print "test accuracy %g" % accuracy.eval(feed_dict={
        x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})
    

mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
#change bellow to runSimpleNN(mnist) if you want to try simple NN
runCNN(mnist)

