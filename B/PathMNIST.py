# CNN model


from medmnist import PathMNIST
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
import matplotlib.pyplot as plt
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score,confusion_matrix,recall_score,f1_score


# In[2]:


# 1. Load and preprocess the data
train_data = PathMNIST(split='train', download=True)
test_data = PathMNIST(split='test', download=True)
val_data = PathMNIST(split='val', download=True)


# In[3]:


class CustomDataset(Dataset):
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        image = torch.tensor(image, dtype=torch.float32).permute(2, 0, 1)
        label = torch.tensor(label, dtype=torch.long).squeeze()  # remove extra dimensions
        return image, label


# In[4]:


train_images = train_data.imgs
train_labels = train_data.labels

val_images = val_data.imgs
val_labels = val_data.labels

test_images = test_data.imgs
test_labels = test_data.labels

train_dataset = CustomDataset(train_images, train_labels)
val_dataset = CustomDataset(val_images, val_labels)
test_dataset = CustomDataset(test_images, test_labels)

# In[5]:


transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),  # adjust figure size to suitble for  ResNet
    transforms.ToTensor(),
])

# In[6]:


train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
val_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# In[7]:


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# In[8]:


# Define the CNN model
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 9)
        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


model = CNN().to(device)

# Define a loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)


# Train the network
def train(model, criterion, optimizer, loader):
    model.train()
    total_loss = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)



class evaluate_ret:
    def __init__(self):
        self.accuracy = []
        self.all_labels = []
        self.all_preds = []


def evaluate(model, loader):
    model.eval()
    correct = 0
    total = 0
    evaluate_ret_instance = evaluate_ret()
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            evaluate_ret_instance.all_labels.extend(labels.cpu().numpy())
            evaluate_ret_instance.all_preds.extend(predicted.cpu().numpy())
    accuracy = 100 * correct / total
    evaluate_ret_instance.accuracy = accuracy
    return evaluate_ret_instance

train_losses = []
train_accuracies = []
val_accuracies = []

# Training and Evaluation
for epoch in range(100):  # let's train for 100 epochs
    train_loss = train(model, criterion, optimizer, train_loader)
    train_accuracy = evaluate(model, train_loader)
    val_accuracy = evaluate(model, val_loader)

    # Append metrics to lists
    train_losses.append(train_loss)
    train_accuracies.append(train_accuracy.accuracy)
    val_accuracies.append(val_accuracy.accuracy)

    print(
        f'Epoch {epoch + 1:02d}, Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy.accuracy:.2f}%, Validation Accuracy: {val_accuracy.accuracy:.2f}%')

# Save the state dictionary of the model
torch.save(model.state_dict(), 'CNN_PathMNIST.pth')

# Test the model
test_accuracy = evaluate(model, test_loader)
print(f'Test Accuracy: {test_accuracy.accuracy:.2f}%')

# Plotting
plt.figure(figsize=(12, 6))

# Plot training and validation accuracy
plt.subplot(1, 2, 1)
plt.plot(train_accuracies, label='Training Accuracy')
plt.plot(val_accuracies, label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Plot training loss
plt.subplot(1, 2, 2)
plt.plot(train_losses, label='Training Loss')
plt.title('Training Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Get predictions and true labels
test_result = evaluate(model, test_loader)
true_labels = test_result.all_labels
predictions = test_result.all_preds
#true_labels, predictions = evaluate(model, test_loader)

# Calculate recall and F1 score
recall = recall_score(true_labels, predictions, average='weighted')
f1 = f1_score(true_labels, predictions, average='weighted')
print(f'Recall: {recall:.2f}, F1 Score: {f1:.2f}')

# Generate and plot the confusion matrix
conf_matrix = confusion_matrix(true_labels, predictions)
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, fmt='g', cmap='Blues')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.title('Confusion Matrix')
plt.show()

########RF

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


print("This process is a bit slow, please wait for a while, thanks!")

# 1. Load and preprocess the data
train_data = PathMNIST(split='train', download=True)
test_data = PathMNIST(split='test', download=True)
val_data = PathMNIST(split='val', download=True)

train_images = train_data.imgs
train_labels = train_data.labels.ravel()


val_images = val_data.imgs
val_labels = val_data.labels.ravel()

test_images = test_data.imgs
test_labels = test_data.labels.ravel()


train_images = train_images.reshape((-1, 3*28*28))
test_images = test_images.reshape((-1, 3*28*28))
val_images = val_images.reshape((-1, 3*28*28))


from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier()
param_grid = {
    'n_estimators': [20, 25, 30],
    'max_features': [ 'sqrt', 'log2'],
    'max_depth' : [8,9,10,11,12],
    'criterion' :['gini', 'entropy']
}

rf_clf = GridSearchCV(estimator=rf, param_grid=param_grid, cv= 3)
rf_clf.fit(train_images, train_labels)

#

best_params = rf_clf.best_params_
rf_best = RandomForestClassifier(**best_params)
rf_best.fit(train_images, train_labels)


val_predictions = rf_best.predict(val_images)
val_accuracy = accuracy_score(val_labels, val_predictions)
print("Validation Accuracy:", val_accuracy)


# Save the state dictionary of the model
torch.save(model.state_dict(), 'RF_PathMNIST.pth')

test_predictions = rf_best.predict(test_images)
test_accuracy = accuracy_score(test_labels, test_predictions)
print("Test Accuracy:", test_accuracy)


print(f"The best parameters are {best_params}")



print(f"The confusion matrix is:{confusion_matrix(test_labels,test_predictions)}")


# Function to plot the learning curve


def plot_learning_curve(train_sizes, train_scores, val_scores):
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    val_scores_mean = np.mean(val_scores, axis=1)
    val_scores_std = np.std(val_scores, axis=1)

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, val_scores_mean - val_scores_std,
                     val_scores_mean + val_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, val_scores_mean, 'o-', color="g", label="Validation score")

    plt.title("Learning Curve")
    plt.xlabel("Number of Trees")
    plt.ylabel("Accuracy")
    plt.legend(loc="best")
    plt.grid()
    plt.show()

# draw Confusion Matrix

    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import confusion_matrix

    def plot_confusion_matrix(test_labels, test_predictions, classes):
        # Compute confusion matrix
        cm = confusion_matrix(test_labels, test_predictions)

        # Create a heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
        plt.title("Confusion Matrix")
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.show()

