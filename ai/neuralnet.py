from torch import nn
import torch

class ResidualLayer(nn.Module):
    def __init__(self, filters, size, stride):
        super(ResidualLayer, self).__init__()
        self.conv1 = nn.Conv2d(filters, filters, size, stride, padding='same')
        self.norm1 = nn.BatchNorm2d(filters)

        self.conv2 = nn.Conv2d(filters, filters, size, stride, padding='same')
        self.norm2 = nn.BatchNorm2d(filters)
        self.activation = nn.ReLU()

    def forward(self, x):
        skip_connection = x
        output = self.conv1(x)
        output = self.norm1(output)
        output = self.activation(output)
        output = self.conv2(output)
        outputs = x + skip_connection
        return self.activation(outputs)


class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.conv1 = nn.Conv2d(2, 256, (3, 3), 1, padding='same')
        self.norm1 = nn.BatchNorm2d(256)

        self.res1 = ResidualLayer(256, (3, 3), 1)
        self.res2 = ResidualLayer(256, (3, 3), 1)
        self.res3 = ResidualLayer(256, (3, 3), 1)

        self.value_conv1 = nn.Conv2d(256, 1, (3, 3), 1, padding='same')
        self.value_linear1 = nn.Linear(81, 81)
        self.value_linear2 = nn.Linear(81, 1)

        self.policy_conv1 = nn.Conv2d(256, 2, (3, 3), 1, padding='same')
        self.policy_linear1 = nn.Linear(81 * 2, 256)
        self.policy_linear2 = nn.Linear(256, 256)
        self.policy_linear3 = nn.Linear(256, 81)
        self.flatten = nn.Flatten()

        self.drop = nn.Dropout(p=0.2)

        self.activation = nn.ReLU()
        self.logit_activation = nn.Tanh()
        self.policy_activation = nn.Softmax()

    def forward(self, x):
        x = self.conv1(x)
        x = self.norm1(x)
        x = self.activation(x)

        x = self.res1(x)
        x = self.res2(x)
        x = self.res3(x)

        value = self.value_conv1(x)
        value = self.flatten(value)

        value = self.value_linear1(value)
        value = self.activation(value)
        value = self.value_linear2(value)
        value = self.logit_activation(value)

        policy = self.policy_conv1(x)
        policy = self.flatten(policy)
        policy = self.policy_linear1(policy)
        policy = self.drop(policy)
        policy = self.activation(policy)

        policy = self.policy_linear2(policy)
        policy = self.drop(policy)
        policy = self.activation(policy)

        policy = self.policy_linear3(policy)
        policy = self.policy_activation(policy)

        return value, policy

