# wishlists

[![Build Status](https://travis-ci.org/NYU-Wishlists/wishlists.svg?branch=master)](https://travis-ci.org/NYU-Wishlists/wishlists)
[![codecov](https://codecov.io/gh/NYU-Wishlists/wishlists/branch/master/graph/badge.svg)](https://codecov.io/gh/NYU-Wishlists/wishlists)

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

Alternatively you can also start by using ` honcho `

```sh
    vagrant ssh
    cd /vagrant
    honcho start
```
__Honcho__ makes use of the ` Procfile ` to start the service using __Gunicorn__ similar to how one would start the server in production.


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

Run the test using ` behave `

``` sh
    cd /vagrant
    python run.py &
    behave
```

Note that the `&` runs the server in the background. To stop the server, you must bring it to the foreground and then press `Ctrl+C`

Stop the server with

```sh
    fg
    <ctrl+c>
```

This repo also has a unit test that you can run with

```sh
    cd /vagrant
    nosetests
```

You should see all of the tests passing with a code coverage report at the end. This is controlled by the `setup.cfg` file in the repo.

## Services

- **HealthCheck** 
Check that the api is up and running.

  ```
  GET /healthcheck
  ```
  
- **Create** a wishlist
  ```
  POST /wishlists
  ```
  
  Body example/format 
  ```
  {
  "user": "Mikey", 
  "entries": 
    [{"id": 0, "name": "Mackbook"}, 
     {"id": 1, "name": " Iphone"}], 
  "name": "Mikes"
  }
  ```

- **Retrieve all wishlists**
  ```
  GET /wishlists
  
  GET /
  ```
  
With a specific wishlist ID, you can perform the following action:

- **Read** a wishlist with id, list all items in it

  ```
  GET /wishlists/<int:wishtlist_id>
  ```
    
- **Update** a wishlist with id

  ```
  PUT /wishlists/<int:wishlist_id>
  ```

- **Delete** a wishlist with id

  ```
  DELETE /wishlists/<int:id>
  ```

Other actions that can be performed:
  
- **Query** with username, list all wishlists of a user

  ```
  GET /wishlists?wishlist_user=username
  ```

- **Action** delete all wishlists of a user

  ```
  DELETE /wishlists/<string:user_name>/delete_all
  ```

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
