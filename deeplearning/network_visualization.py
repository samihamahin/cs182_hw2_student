import random

import numpy as np

import torch
import torch.nn.functional as F


def compute_saliency_maps(X, y, model):
    """
    Compute a class saliency map using the model for images X and labels y.

    Input:
    - X: Input images; Tensor of shape (N, 3, H, W)
    - y: Labels for X; LongTensor of shape (N,)
    - model: A pretrained CNN that will be used to compute the saliency map.

    Returns:
    - saliency: A Tensor of shape (N, H, W) giving the saliency maps for the input
    images.
    """
    # Make sure the model is in "test" mode
    model.eval()

    # Construct new tensor that requires gradient computation
    X = X.clone().detach().requires_grad_(True)
    saliency = None
    ##############################################################################
    # TODO: Implement this function. Perform a forward and backward pass through #
    # the model to compute the gradient of the correct class score with respect  #
    # to each input image. You first want to compute the loss over the correct   #
    # scores, and then compute the gradients with torch.autograd.gard.           #
    ##############################################################################
    N = y.shape
    
    #foward pass through model
    model = model(X)
    
    #corected class score 
    model = model.gather(1, y.view(-1, 1)).squeeze()
    
    #backward pass through model
    score_tensor = torch.FloatTensor([1.0,1.0,1.0,1.0,1.0])
    model.backward(score_tensor)
    
    #compute gradient 
    grad = X.grad.data.abs()
    saliency, _ = torch.max(grad, dim=1)
    saliency = saliency.squeeze()
    
    ##############################################################################
    #                             END OF YOUR CODE                               #
    ##############################################################################
    return saliency


def make_fooling_image(X, target_y, model):
    """
    Generate a fooling image that is close to X, but that the model classifies
    as target_y.

    Inputs:
    - X: Input image; Tensor of shape (1, 3, 224, 224)
    - target_y: An integer in the range [0, 1000)
    - model: A pretrained CNN

    Returns:
    - X_fooling: An image that is close to X, but that is classifed as target_y
    by the model.
    """
    # Initialize our fooling image to the input image.
    X_fooling = X.clone().detach().requires_grad_(True)

    learning_rate = 1
    ##############################################################################
    # TODO: Generate a fooling image X_fooling that the model will classify as   #
    # the class target_y. You should perform gradient ascent on the score of the #
    # target class, stopping when the model is fooled.                           #
    # When computing an update step, first normalize the gradient:               #
    #   dX = learning_rate * g / ||g||_2                                         #
    #                                                                            #
    # You should write a training loop.                                          #
    #                                                                            #
    # HINT: For most examples, you should be able to generate a fooling image    #
    # in fewer than 100 iterations of gradient ascent.                           #
    # You can print your progress over iterations to check your algorithm.       #
    ##############################################################################
    
    #perform gradient ascent on score of target class
    
    #normalize the gradient
        
    #iterations of at most 100 iterations for gradient ascent
    for i in range(100):
        #run the model to see the scores
        scores = model(X_fooling)
        _, score_ind = scores.data.max(dim=1)
        
        #keep running if model is not fooled
        if score_ind != target_y:
            scores[:,target_y].backward()
            
            #gradient
            grad = X_fooling.grad.data
            
            #normalized gradient
            n_grad = torch.norm(grad, 2)
            
            #update image with normalized gradient
            X_fooling.data += learning_rate * grad / n_grad
            
            #zero out gradient 
            X_fooling.grad.data.zero_()
        
        #stop running the model if fooled
        else:
            break
    
    
    ##############################################################################
    #                             END OF YOUR CODE                               #
    ##############################################################################
    return X_fooling.detach()


def update_class_visulization(model, target_y, l2_reg, learning_rate, img):
    """
    Perform one step of update on a image to maximize the score of target_y
    under a pretrained model.

    Inputs:
    - model: A pretrained CNN that will be used to generate the image
    - target_y: Integer in the range [0, 1000) giving the index of the class
    - l2_reg: Strength of L2 regularization on the image
    - learning_rate: How big of a step to take
    - img: the image tensor (1, C, H, W) to start from
    """

    # Create a copy of image tensor with gradient support
    img = img.clone().detach().requires_grad_(True)
    ########################################################################
    # TODO: Use the model to compute the gradient of the score for the     #
    # class target_y with respect to the pixels of the image, and make a   #
    # gradient step on the image using the learning rate. Don't forget the #
    # L2 regularization term!                                              #
    # Be very careful about the signs of elements in your code.            #
    ########################################################################
    
    model.eval()
    scores = model(img)
    
    scores_y = scores[:, target_y]
    
    loss_scores = scores_y - l2_reg * torch.sum(img**2)
    
    loss_scores.backward()
    
    
    with torch.no_grad():
        
        img += learning_rate * img.grad
    
    
    ########################################################################
    #                             END OF YOUR CODE                         #
    ########################################################################
    return img.detach()
