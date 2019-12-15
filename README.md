# Desktop Docker Lab System
Python/Flask webapp that spins up docker desktops


## Step 1: Install docker
```
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
Make sure to add your user to the docker group!!
```
sudo usermod -aG docker your-user
```
## Step 2: Install python3
```
sudo apt-get install python3
sudo apt-get install python3-pip
```
## Step 3: Install pip requirments. 
```
sudo pip3 install -r requirments
```
## Step 4: Run the app
```
python3 app.py
```
## Step 5: Access the webpage
```
http://host.ip.goes.here:5000
```

### Issues:
Make sure when you are running the app to use a user in the docker group. This will not work if you are not in the docker group. You could run this as root with the ```sudo``` command but I would not recommend that. 
