# Food Zone
Food Zone is an web application that provides a list of Various Fooditems within a variety of categories.Each Category contains list of Fooditems. It provides google oAuth2 for user registration and authentication system.Registered users will have the ability to add, edit and delete their own Fooditems and categories of Fooditems.
###### By Ramya
### To run this project we need : 
* Python3
* Vagrant 2.2.1
* VirtualBox 5.1.30
* Git 2.19.2
### Steps to run this project:
*  **step-1**
    1. Install python 3 ,if you don't know how to do? refer [this link](https://realpython.com/installing-python/)
        * Along with python we need to install few dependencies.For this run below command as administrator in cmd
            `pip  install  -r  Requirements.txt`
    2. Install Vagrant and VirtualBox softwares  that are downloaded in your system.If you need more information about installation click [here](https://github.com/udacity/fullstack-nanodegree-vm)
    3. clone or download [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm)
    4. save the FoodZone project folder in vagrant folder 
*  **step-2**
    1. Open git bash from the vagrant folder 
    2. Run the virtual-machine from vagrant by giving the command as `vagrant up` inside the **FSND-Virtual-Machine\vagrant**
    3. Login into the Linux VM with command as `vagrant ssh`.If you need more about vagrant commands refer [here](https://www.vagrantup.com/docs/cli/)
    4. After login to linux vm change  to shared directory by giving command as `cd /vagrant`
    5. Now change directory to FoodZone by command as `cd FoodZone`
* **step-3**
    1. run FoodZone project by giving command as `python3 itemcatalog.py`
    2. Open **http://localhost:5000/** in any Browser (Recommended Chrome)
##### JSON endpoints:
`http://localhost:5000/all_json`
`http://localhost:5000/category/1/items.json`
   














   