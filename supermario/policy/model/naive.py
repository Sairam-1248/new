"""
Implementation of Naive MODQN - Multi-Objective Deep Q Network

The algorithm is developed with Pytorch

Author: Runzhe Yang
"""


import torch
import torch.nn as nn
import torch.nn.functional as F


class NaiveCnnCQN(torch.nn.Module):
    '''
        Convolutional Controllable Q-Network, Naive Version
    '''

    def __init__(self, state_size, action_size, reward_size):
        super(NaiveCnnCQN, self).__init__()

        self.state_size = state_size
        self.action_size = action_size
        self.reward_size = reward_size

        in_channel = self.state_size[2]
        wi = int((((self.state_size[0] - 4) / 4 - 2) / 2 - 2) / 2)
        hi = int((((self.state_size[1] - 4) / 4 - 2) / 2 - 2) / 2)
        feature_size = int(wi * hi * 64)

        # S x A -> (W -> R). =>. S x W -> (A -> R)
        self.conv1 = nn.Conv2d(in_channel, 32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=4, stride=2)
        
        self.affine1 = nn.Linear(feature_size + reward_size,
                                 256)
        self.affine2 = nn.Linear(256,
                                 128)
        self.affine3 = nn.Linear(128,
                                 action_size)

    def forward(self, state, preference, execmask=None):
        state = state.transpose(1, -1).transpose(-2,-1)
        feat = F.tanh(self.conv1(state))
        feat = F.tanh(self.conv2(feat))
        feat = F.tanh(self.conv3(feat))
        # feat = self.pool3(F.tanh(self.conv2(feat)))
        feat = feat.view(feat.size(0), -1)
        x = torch.cat((feat, preference), dim=1)
        x = x.view(x.size(0), -1)
        x = F.relu(self.affine1(x))
        x = F.relu(self.affine2(x))
        q = self.affine3(x)
        if execmask is not None:
            q = torch.add(q, execmask)
        hq = q.detach().max(dim=1)[0]
        return hq, q