# wishlists

Wishlists RESTful service allows customers to create a collection of products that they wish they had the money to purchase.

Team: Hu Jianyuan, Omer Katz, Sakada Lim, Minh Lai, Doyeon Kong


## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

```sh
    git clone https://github.com/NYU-Wishlists/wishlists.git
    cd wishlists
    vagrant up
```

Once the VM is up you can use it with:

```sh
    vagrant ssh
    cd /vagrant
    python run.py
```

You should now be able to see the service running in your browser by going to
[http://localhost:5000](http://localhost:5000). You will see a message about the
service which looks something like this:

```
{
    name: "Wishlist Demo REST API Service",
    url: "http://localhost:5000/wishlists",
    version: "1.0"
}
```

When you are done, you can use `Ctrl+C` within the VM to stop the server.

## Testing

Run the tests suite with:

```sh
    nosetests
```

You should see all of the tests passing with a code coverage report at the end. this is controlled by the `setup.cfg` file in the repo.

## Shutdown

When you are done, you can use the `exit` command to get out of the virtual machine just as if it were a remote server and shut down the vm with the following:

```sh
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with from your computer to free up disk space with:

```sh
    vagrant destroy
```
