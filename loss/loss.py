from torch.nn import funtional as F
import numpy as np
import torch

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 

def MSELoss(ground_truth, prediction):
    """
    This function will return MSELoss between ground_truth and prediction
    """
    return F.mse_loss(ground_truth, prediction)

def SmoothL1Loss(ground_truth, prediction):
    """
    This function will return SmoothL1Loss in pytorch.
    It seems to be ess sensitive to outliers than the MSELoss
    and in some cases prevents exploding gradients.
    https://pytorch.org/docs/stable/nn.html#torch.nn.SmoothL1Loss
    """
    return F.smooth_l1_loss(ground_truth, prediction)

def EdgeLoss(ground_truth, prediction):
    """
    Calculate GDL(gradient difference loss) between GT and prediction.
    """
    assert ground_truth.shape == prediction.shape
    # Define channel of input and output
    channel_in = prediction.shape[2]
    channel_out = channel_in

    # Define two filters
    x_filter = np.array([
        [1, -1],
        [1, -1]
    ])
    y_filter = np.array([
        [1, 1],
        [-1, -1]
    ])

    # Create tensors from numpy and reshape to desired shape of tensor
    # (out_channel, in_channel, H, W)
    x_filter = torch.from_numpy(x_filter).float().view(1, 1, 2, 2)
    x_filter = x_filter.repeat(channel_out, channel_in, 1, 1).to(DEVICE)
    y_filter = torch.from_numpy(y_filter).float().view(1, 1, 2, 2)
    y_filter = y_filter.repeat(channel_out, channel_in, 1, 1).to(DEVICE)

    # Use convolution to get difference maps of prediction and GT.
    gt_x = F.conv2d(ground_truth, x_filter)
    gt_y = F.conv2d(ground_truth, y_filter)
    pred_x = F.conv2d(ground_truth, x_filter)
    pred_y = F.conv2d(ground_truth, y_filter)

    # Use L1Loss to calculate loss between two difference maps
    total_loss = F.l1_loss(gt_x, pred_x) + F.l1_loss(pred_x, pred_y)
    return total_loss