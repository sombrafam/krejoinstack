# krejoinstack (nutshell)

krejoinstack is an application that uses KDE Konsole terminals to connect and
open terminal connections to multiple systems at the same time, making possible
to debug or working on a system automatically loggin into jump hosts and target
hosts and them running commands (like opening a log file) on each of then.  

Using the Konsole graphical terminal has some advantages:

- Unlimited scrollback (needs konsole configuration);
- No need for wrist painfull shortcuts ('Ctrl+A + Command' to move between
  screens);
- Easier search with regular expression and other facilities provided by
  konsole;
- Session bell on window activity or silence. Leave commands running and get
  notified when something changes or stops;
- Scrollback reset clears any previous printed message allowing to search,
  focus on what you actually is searching;
- Many other features and desktop integration;


# # How to use

1. Install konsole in you desktop (tested on Ubuntu systems only):

```bash
snap install krejoinstack
```

2. Configure password less access to your bastion or other host: 

```bash
thehost=""
ssh-keygen
ssh-copy-id ${thehost}
```
3. Run it:

krejoin [-h] <plugin> [plugin-options] <host>
Host:
  The host might be 'localhost' or any hostname or IP. If <host> is not
  'localhost', SSH key-based authentication must be configured from this
  machine to the host. 
Available Plugins:
   --juju
   --docker
   --custom-yaml
PLugin Options:
    Juju Cloud options (--juju):
      --model: The model to search for the units/machines. Defaults to the model 
        that is logged.
      --machines: Open one shell terminal for each machine. **Excludes all the
        other options.**
    
      --group-applications: Group similar services into distict windows
      --template: Loads Juju shells based on this template
      --export-template: Dumps the current template into a file so you can edit and
        add whathever you need.
      --include-applications: Only will open from these applications
      --exclude-applications: Will not open from this applications (by default will
        open from all applications so, with this you can exclude what you don't
        want).
      --include-units: Same but for units.
      --exclude-units: Same but for units;
      --open-logs: Open 1 shell with the logs for the application. If no option is
        added this is default.
      --open-shell: Open 1 shell on sudo for each unit of the application.
    Docker deplyment option (--docker):
      --include-pods:
      --exclude-pods:
      --open-logs:
      --open-shell:
    Custom YAML options (--custom-yaml):
      --custom-template: Load all shells based on this template.
      --print-skell: Prints a sample template example.

