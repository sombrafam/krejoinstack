krejoinstack
============

Graphical version of the ./rejoin-stack.sh script of devstack. This uses a
graphical terminal to connect to a devstack host and run Openstack services.

Using a graphical terminal has some advantages over the default screen
provided in devstack:

::
  # unlimited scrollback (needs konsole configuration)
  # no need of 'Ctrl+A + Command' to move between screens
  # easier search with regular expression and other facilities provided by
    konsole
  # session bell on window activity or silence
  # scrollback clearing, that enable debug only what is important


How to use
==========

1 - Install konsole in you desktop:

In Ubuntu:
::
  sudo apt-get install konsole python-pip python-setuptools

Or Fedora:
::
  sudo yum install konsole

2 - Upgrade pip:
::
  sudo pip install --upgrade pip

3 - Install the python requirements:
::
  sudo pip install -r requirements.txt

4 - Configure SSH keys to the Openstack VM
::
  ssh-keygen
  ssh-copy-id <stack-host>

5 - Run:

::
  krejoin [-h] [--juju | --devstack | --custom-yaml] <remote host>
    Juju Cloud options:
      --model: The model to search for the units/machines
      --open-regex: Open only units matching this regex
      --no-open-regex: Open only units not mathiching this regex
      --open-template: Load shell mode from yaml
      --num-services: Opens N tabs for each service
      --group-services: Group similar services into distict windows
      --machines: Also logs into the listed machines
      --template: Loads Juju shells based on this template
    Custom YAML options:
      --template: Load all shells based on this template

