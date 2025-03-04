import torch
import torchvision
import torch.nn as nn

# dataset loading

transform = torchvision.transforms.Compose([
  torchvision.transforms.ToTensor(),
  torchvision.transforms.Resize((224, 224)),
  torchvision.transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
  ])
dataset = torchvision.datasets.ImageFolder(root="dataset", transform=transform)
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
trainset, testset = torch.utils.data.random_split(dataset, [train_size, test_size])
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
testloader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=True)


# model
class residual_block(nn.Module):
    def __init__(self, width):
      super(residual_block, self).__init__()

      self.width = width
      self.block = nn.Sequential(
          nn.Conv2d(width, width, 3, padding = 1),
          nn.ReLU(),
          nn.Conv2d(width, width, 3, padding = 1),
          nn.ReLU(),
          nn.Conv2d(width, width, 3, padding = 1)
      )
    def forward(self, x):
      return x + self.block(x)

class convnet(nn.Module):
    def __init__(self):
      super(convnet, self).__init__()

      # input channels, output channels, conv size, padding, (etc.)
      self.layer1 = nn.Conv2d(3, 16, 3, padding = 1)
      self.layer2 = nn.Conv2d(16, 32, 3, padding = 1)
      self.layer3 = residual_block(32)
      self.layer4 = nn.Linear(32 * 56 * 56, 6)

      self.pool = nn.MaxPool2d(2)
      self.relu = nn.ReLU()
      self.softmax = nn.Softmax(dim = 1)

      self.batchnorm1 = nn.BatchNorm2d(16)
      self.batchnorm2 = nn.BatchNorm2d(32)

    def forward(self, x):
      # layer 1
      x = self.layer1(x)
      x = self.batchnorm1(x)
      x = self.pool(x)
      x = self.relu(x)

      # layer 2
      x = self.layer2(x)
      x = self.pool(x)
      x = self.relu(x)

      # layer 3
      x = self.layer3(x)
      x = self.batchnorm2(x)
      x = self.relu(x)

      # layer 4
      x = x.view(x.size(0), -1)
      x = self.layer4(x)
      x = self.softmax(x)
      return x
    
# training
print("training...")
model = convnet()
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 0.0001)
for epoch in range(10):
  for i, (x, y) in enumerate(trainloader):
    y_pred = model(x)
    loss = loss_fn(y_pred, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if i % 100 == 0:
      print(f"epoch: {epoch}, batch: {i}, loss: {loss.item()}")

# testing
correct = 0
total = 0
with torch.no_grad():
  for x, y in testloader:
    y_pred = model(x)
    _, predicted = torch.max(y_pred.data, 1)
    total += y.size(0)
    correct += (predicted == y).sum().item()
print(f"accuracy: {correct / total}")