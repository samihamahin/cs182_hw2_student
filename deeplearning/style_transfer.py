import numpy as np

import torch
import torch.nn.functional as F


def content_loss(content_weight, content_current, content_target):
    """
    Compute the content loss for style transfer.

    Inputs:
    - content_weight: Scalar giving the weighting for the content loss.
    - content_current: features of the current image; this is a PyTorch Tensor of shape
      (1, C_l, H_l, W_l).
    - content_target: features of the content image, Tensor with shape (1, C_l, H_l, W_l).

    Returns:
    - scalar content loss
    """
    ##############################################################################
    #                               YOUR CODE HERE                               #
    ##############################################################################
    
    sq_diff = torch.pow(content_current - content_target, 2)
    
    sum_sq_diff = torch.sum(sq_diff)
    
    return content_weight * sum_sq_diff
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################


def gram_matrix(features, normalize=True):
    """
    Compute the Gram matrix from features.

    Inputs:
    - features: PyTorch Variable of shape (N, C, H, W) giving features for
      a batch of N images.
    - normalize: optional, whether to normalize the Gram matrix
        If True, divide the Gram matrix by the number of neurons (H * W * C)

    Returns:
    - gram: PyTorch Variable of shape (N, C, C) giving the
      (optionally normalized) Gram matrices for the N input images.
    """
    ##############################################################################
    #                               YOUR CODE HERE                               #
    ##############################################################################
    
    N, C, H, W = features.shape
    
    reshape_features = features.view(N, C, -1)
    
    trans_features = reshape_features.transpose(1,2)
    
    batch_mult = torch.bmm(reshape_features, trans_features)
    
    batch_mult_norm = batch_mult/(H*W*C)
    
    if normalize:
        return batch_mult_norm
    else:
        return batch_mult
    
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################


def style_loss(feats, style_layers, style_targets, style_weights):
    """
    Computes the style loss at a set of layers.

    Inputs:
    - feats: list of the features at every layer of the current image, as produced by
      the extract_features function.
    - style_layers: List of layer indices into feats giving the layers to include in the
      style loss.
    - style_targets: List of the same length as style_layers, where style_targets[i] is
      a PyTorch Variable giving the Gram matrix the source style image computed at
      layer style_layers[i].
    - style_weights: List of the same length as style_layers, where style_weights[i]
      is a scalar giving the weight for the style loss at layer style_layers[i].

    Returns:
    - style_loss: A PyTorch Variable holding a scalar giving the style loss.
    """
    # Hint: you can do this with one for loop over the style layers, and should
    # not be very much code (~5 lines). You will need to use your gram_matrix function.
    ##############################################################################
    #                               YOUR CODE HERE                               #
    ##############################################################################
    loss = 0
    
    for l in range(len(style_layers)):
        
        layer = style_layers[l]
        
        g = gram_matrix(feats[layer])
        
        t_diff = torch.pow(g - style_targets[l], 2)
        
        t_sum = torch.sum(t_diff)
        
        loss += style_weights[l] * t_sum
    
    return loss
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################


def tv_loss(img, tv_weight):
    """
    Compute total variation loss.

    Inputs:
    - img: PyTorch Variable of shape (1, 3, H, W) holding an input image.
    - tv_weight: Scalar giving the weight w_t to use for the TV loss.

    Returns:
    - loss: PyTorch Variable holding a scalar giving the total variation loss
      for img weighted by tv_weight.
    """
    # Your implementation should be vectorized and not require any loops!
    ##############################################################################
    #                               YOUR CODE HERE                               #
    ##############################################################################
    
    row_before = img[:,:,:,:-1] 
    
    row_after =  img[:,:,:,1:]
    
    col_before = img[:,:,:-1,:]
    
    col_after =  img[:,:,1:,:]
    
    w_sq_diff = torch.sum(torch.pow(row_before - row_after, 2))
    
    h_sq_diff = torch.sum(torch.pow(col_before - col_after, 2))
    
    return tv_weight * (w_sq_diff + h_sq_diff)
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
