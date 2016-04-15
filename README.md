There are mini projects here,
[a tiny SQL-based swiss pairing tournament served using Python's `wsgiref` library](#).
And also [a Flask Python web framework SQLAlchemy using menu app.](#)
Neither is styled at this point but are created as an exercise to get acquainted
with backend development.

## View Projects

In order to view these projects, you have to set up a virtual machine that has
all the necessary resources installed on it. This machine already exists in this
repository, here's how you get it working:

Alternatively, if you just want to view the files relevant to the projects you
can find more information in these READMEs:

* [Tournament README](#)
* [Menu App README](#)

* Clone this repository:

```
git clone https://github.com/AndreiCommunication/SQL-Python-Tournament.git thisvm
cd thisvm
```

* Enter the `vagrant` directory and boot the virtual machine. Note that for this
step to work you need
[vagrant](https://www.vagrantup.com/) and
[VirtualBox](https://www.virtualbox.org/)
to be correctly installed.

```
cd vagrant
vagrant up
```

The `vagrant up` step will take up to about a minute to run as the virtual
machine boots up.

* Enter the virtual machine:

```
vagrant ssh
```

Now you can follow particular instructures to view either project:

* [View Tournament](#)
* [View Menu App](#)
