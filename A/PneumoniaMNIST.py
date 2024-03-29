# ### Read data

# In[1]:


import numpy as np
from sklearn.metrics import accuracy_score,confusion_matrix,recall_score,f1_score

from medmnist import PneumoniaMNIST

train_dt=PneumoniaMNIST(split="train",download=True)
test_dt=PneumoniaMNIST(split="test",download=True)
val_dt=PneumoniaMNIST(split="val",download=True)

train_img,train_lbl=train_dt.imgs,train_dt.labels
test_img,test_lbl=test_dt.imgs,test_dt.labels
val_img,val_lbl=val_dt.imgs,val_dt.labels


# In[2]:


# Convert image data to a two-dimensional array
train_images = train_img.reshape((4708, 28*28))
test_images = test_img.reshape((624, 28*28))
val_images = val_img.reshape((524, 28*28))

# Convert labels to 1D array
train_labels = train_lbl.ravel()
test_labels = test_lbl.ravel()
val_labels = val_lbl.ravel()


# ### Build MLP model

# In[3]:


from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV


mlp = MLPClassifier(max_iter=1000)
parameter_space = {
    'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)],
    'activation': ['tanh', 'relu'],
    'solver': ['sgd', 'adam'],
    'alpha': [0.0001, 0.05],
    'learning_rate': ['constant','adaptive'],
}

clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
clf.fit(train_images, train_labels)


# In[4]:

# Retrain the model on the full training set using optimal parameters
best_params = clf.best_params_
mlp_best = MLPClassifier(max_iter=1000, **best_params)
mlp_best.fit(train_images, train_labels)


#  Evaluate the model on an independent validation set

val_predictions = mlp_best.predict(val_images)
val_accuracy = accuracy_score(val_labels, val_predictions)
print("Validation Accuracy:", val_accuracy)


#  Evaluate the final selected model on the test set
test_predictions = mlp_best.predict(test_images)
test_accuracy = accuracy_score(test_labels, test_predictions)
print("Test Accuracy:", test_accuracy)


# In[5]:


print(f"The confusion matrix is:{confusion_matrix(test_labels,test_predictions)}")
print(f"The F1 score is {f1_score(test_labels,test_predictions):.2%}")
print(f"The Recall Rate is {recall_score(test_labels,test_predictions):.2%}")


# draw confusion matrix

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(test_labels, test_predictions):
    conf_matrix = confusion_matrix(test_labels, test_predictions)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='g', cmap='Blues',
                xticklabels=['Category 1', 'Category 2'],
                yticklabels=['Category 1', 'Category 2'])
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.title('Confusion Matrix')
    plt.show()



# In[6]:


print(f"The best parameters are: {best_params}")

# ### Convolutional Neural NetworkCNN

# In[40]:


import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset,DataLoader
from torchvision import transforms, models
import numpy as np
import torch.nn.functional as F
from sklearn.metrics import accuracy_score,confusion_matrix,recall_score,f1_score
517
train_dt=PneumoniaMNIST(split="train",download=True)
test_dt=PneumoniaMNIST(split="test",download=True)
val_dt=PneumoniaMNIST(split="val",download=True)


# In[13]:


class CustomDataset(Dataset):
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        image = torch.tensor(image, dtype=torch.float32).unsqueeze(0)
        label = torch.tensor(label, dtype=torch.long).squeeze()  # remove extra dimensions
        return image, label


# In[14]:


train_images,train_labels=train_dt.imgs,train_dt.labels
test_images,test_labels=test_dt.imgs,test_dt.labels
val_images,val_labels=val_dt.imgs,val_dt.labels

train_dataset = CustomDataset(train_images, train_labels)
val_dataset = CustomDataset(val_images, val_labels)
test_dataset = CustomDataset(test_images, test_labels)


# In[15]:


train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)


# In[16]:


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# In[17]:


# Define the CNN model
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 2)
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
        images, labels=images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)

# Evaluate the model

def evaluate(model, loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels=images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    return 100 * correct / total

def plot_pr_curve(model,loader):
    model.eval()
    correct = 0
    total = 0
    y_test=[]
    y_pred=[]
    y_proba=[]
    with torch.no_grad():
        for images, labels in loader:
            images, labels=images.to(device), labels.to(device)
            outputs = model(images)
            
            _, predicted = torch.max(outputs.data, 1)
            y_test.append(labels)
            y_pred.append(predicted)
            y_proba.append(F.softmax(outputs,dim=1))
        y_test=torch.cat(y_test).cpu().numpy()
        y_pred=torch.cat(y_pred).cpu().numpy()
        y_proba=torch.cat()
def cal_other_metrics(model,loader):
    model.eval()
    correct = 0
    total = 0
    y_test=[]
    y_pred=[]
    with torch.no_grad():
        for images, labels in loader:
            images, labels=images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            y_test.append(labels)
            y_pred.append(predicted)
        y_test=torch.cat(y_test).cpu().numpy()
        y_pred=torch.cat(y_pred).cpu().numpy()
        
        # Calculate confusion matrix
        conf_matrix = confusion_matrix(y_test, y_pred)
        print("Confusion Matrix:")
        print(conf_matrix)
        
        # Calculate recall
        recall = recall_score(y_test, y_pred)
        print(f"Recall:{recall:.2%}")

        # Calculate F1 score
        f1 = f1_score(y_test, y_pred)
        print(f"F1 Score:{f1:.2%}")
        return conf_matrix,recall,f1
#  Training and Evaluation
for epoch in range(100):  # let's train for 10 epochs
    train_loss = train(model, criterion, optimizer, train_loader)
    train_accuracy=evaluate(model,train_loader)
    val_accuracy = evaluate(model, val_loader)
    
    print(f'Epoch {epoch+1:02d}, Train Loss: {train_loss:.4f}, Train Accuracy:{train_accuracy:.2f}%, Validation Accuracy: {val_accuracy:.2f}%')

# Test the model
test_accuracy = evaluate(model, test_loader)
print(f'Test Accuracy: {test_accuracy:.2f}%')


cm,recall,F1score=cal_other_metrics(model,test_loader)

# Save the state dictionary of the model

torch.save(model.state_dict(), 'CNN_PneumoniaMNIST.pth')

#Draw the confusion matrix

import matplotlib.pyplot as plt;
import seaborn as sns
import matplotlib.pyplot as plt;
# Using Seaborn to draw heat maps
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", annot_kws={"size": 16})

plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.show()


def plot_pr_curve(model,loader):
    from sklearn.metrics import precision_recall_curve, average_precision_score,roc_auc_score
    model.eval()
    correct = 0
    total = 0
    y_test=[]
    y_proba=[]
    with torch.no_grad():
        for images, labels in loader:
            images, labels=images.to(device), labels.to(device)
            outputs = model(images)

    #         break
            y_test.append(labels)
            y_proba.append(F.softmax(outputs,dim=1))
        y_test=torch.cat(y_test).cpu().numpy()
        y_proba=torch.cat(y_proba).cpu().numpy()[:,1]
    # Calculate precision and recall
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    
    # Calculate average accuracy
    average_precision = average_precision_score(y_test, y_proba)
    plt.plot(recall, precision, label=f'PR Curve (AP = {average_precision:.2f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.show()
    auc = roc_auc_score(y_test, y_proba)
    print(f"the AUC is: {auc:.2}")


plot_pr_curve(model,test_loader)




