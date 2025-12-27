# Gebruik van UV

## Wat is UV?
UV is een snelle Python package manager die helpt bij het beheren van afhankelijkheden, virtuele omgevingen en Python-versies. Het is ontworpen voor snelheid en eenvoud, met compatibiliteit met pip en ondersteuning voor moderne Python-workflows.

## Vereisten
- Linux-systeem (bijv. Fedora).
- `curl` geïnstalleerd voor de installatiescript.
- Internetverbinding voor downloads.

## Installatie van UV
Installeer UV met het officiële script:
```bash
tedsluis@fedora:~$ curl -LsSf https://astral.sh/uv/install.sh | sh                                                                                                                                 Sun21 [1247/1501]
downloading uv 0.9.18 x86_64-unknown-linux-gnu
no checksums to verify
installing to /home/tedsluis/.local/bin
  uv
  uvx
everything's installed!
tedsluis@fedora:~$ uv --help
An extremely fast Python package manager.

Usage: uv [OPTIONS] <COMMAND>

Commands:
  auth     Manage authentication
  run      Run a command or script
  init     Create a new project
  add      Add dependencies to the project
  remove   Remove dependencies from the project
  version  Read or update the project's version
  sync     Update the project's environment
  lock     Update the project's lockfile
  export   Export the project's lockfile to an alternate format
  tree     Display the project's dependency tree
  format   Format Python code in the project
  tool     Run and install commands provided by Python packages
  python   Manage Python versions and installations
  pip      Manage Python packages with a pip-compatible interface
  venv     Create a virtual environment
  build    Build Python packages into source distributions and wheels
  publish  Upload distributions to an index
  cache    Manage uv's cache
  self     Manage the uv executable
  help     Display documentation for a command

Cache options:
  -n, --no-cache               Avoid reading from or writing to the cache, instead using a temporary directory for the duration of the operation [env: UV_NO_CACHE=]
      --cache-dir <CACHE_DIR>  Path to the cache directory [env: UV_CACHE_DIR=]

Python options:
      --managed-python       Require use of uv-managed Python versions [env: UV_MANAGED_PYTHON=]
      --no-managed-python    Disable use of uv-managed Python versions [env: UV_NO_MANAGED_PYTHON=]
      --no-python-downloads  Disable automatic downloads of Python. [env: "UV_PYTHON_DOWNLOADS=never"]

Global options:
  -q, --quiet...                                   Use quiet output
  -v, --verbose...                                 Use verbose output
      --color <COLOR_CHOICE>                       Control the use of color in output [possible values: auto, always, never]
      --native-tls                                 Whether to load TLS certificates from the platform's native certificate store [env: UV_NATIVE_TLS=]
      --offline                                    Disable network access [env: UV_OFFLINE=]
      --allow-insecure-host <ALLOW_INSECURE_HOST>  Allow insecure connections to a host [env: UV_INSECURE_HOST=]
      --no-progress                                Hide all progress outputs [env: UV_NO_PROGRESS=]
      --directory <DIRECTORY>                      Change to the given directory prior to running the command [env: UV_WORKING_DIR=]
      --project <PROJECT>                          Discover a project in the given directory [env: UV_PROJECT=]
      --config-file <CONFIG_FILE>                  The path to a `uv.toml` file to use for configuration [env: UV_CONFIG_FILE=]
      --no-config                                  Avoid discovering configuration files (`pyproject.toml`, `uv.toml`) [env: UV_NO_CONFIG=]
  -h, --help                                       Display the concise help for this command
  -V, --version                                    Display the uv version

Use `uv help` for more details.
```

Controleer UV versie:
```bash
$ uv --version
uv 0.9.18
```

## Python Versies Installeren
Installeer specifieke Python-versies met UV:
```bash
tedsluis@fedora:~$ uv python install 3.12 3.13
Installed 2 versions in 54.29s
 + cpython-3.12.12-linux-x86_64-gnu (python3.12)
 + cpython-3.13.11-linux-x86_64-gnu (python3.13)

 tedsluis@fedora:~$ uv python list
cpython-3.15.0a2-linux-x86_64-gnu                 <download available>
cpython-3.15.0a2+freethreaded-linux-x86_64-gnu    <download available>
cpython-3.14.2-linux-x86_64-gnu                   /usr/bin/python3.14
cpython-3.14.2-linux-x86_64-gnu                   /usr/bin/python3 -> python3.14
cpython-3.14.2-linux-x86_64-gnu                   /usr/bin/python -> ./python3
cpython-3.14.2-linux-x86_64-gnu                   <download available>
cpython-3.14.2+freethreaded-linux-x86_64-gnu      <download available>
cpython-3.13.11-linux-x86_64-gnu                  .local/bin/python3.13 -> .local/share/uv/python/cpython-3.13.11-linux-x86_64-gnu/bin/python3.13
cpython-3.13.11-linux-x86_64-gnu                  .local/share/uv/python/cpython-3.13.11-linux-x86_64-gnu/bin/python3.13
cpython-3.13.11+freethreaded-linux-x86_64-gnu     <download available>
cpython-3.12.12-linux-x86_64-gnu                  .local/bin/python3.12 -> .local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin/python3.12
cpython-3.12.12-linux-x86_64-gnu                  .local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/bin/python3.12
cpython-3.11.14-linux-x86_64-gnu                  <download available>
cpython-3.10.19-linux-x86_64-gnu                  <download available>
cpython-3.9.25-linux-x86_64-gnu                   <download available>
cpython-3.8.20-linux-x86_64-gnu                   <download available>
pypy-3.11.13-linux-x86_64-gnu                     <download available>
pypy-3.10.16-linux-x86_64-gnu                     <download available>
pypy-3.9.19-linux-x86_64-gnu                      <download available>
pypy-3.8.16-linux-x86_64-gnu                      <download available>
graalpy-3.12.0-linux-x86_64-gnu                   <download available>
graalpy-3.11.0-linux-x86_64-gnu                   <download available>
graalpy-3.10.0-linux-x86_64-gnu                   <download available>
graalpy-3.8.5-linux-x86_64-gnu                    <download available>
```
UV beheert Python-versies zonder systeemwijzigingen.

## Python Testen
Test een geïnstalleerde Python-versie met een tool zoals `pycowsay`:
```bash
tedsluis@fedora:~$ uvx pycowsay 'hello world!'
Installed 1 package in 15ms

  ------------
< hello world! >
  ------------
   \   ^__^
    \  (oo)\_______
       (__)\       )\/\
           ||----w |
           ||     ||
```
Gebruik `uvx` voor snelle tests zonder permanente installatie.

## Ansible en Ansible Vault Installeren
Installeer Ansible en gerelateerde tools met UV:
```
tedsluis@fedora:~/git$ uv tool install --with-executables-from ansible-core,ansible-lint --with ansible-vault ansible
Resolved 32 packages in 17ms
Installed 21 packages in 18ms
 + ansible-compat==25.12.0
 + ansible-lint==25.12.2
 + attrs==25.4.0
 + black==25.12.0
 + bracex==2.6
 + click==8.3.1
 + distro==1.9.0
 + filelock==3.20.1
 + jsonschema==4.25.1
 + jsonschema-specifications==2025.9.1
 + mypy-extensions==1.1.0
 + pathspec==0.12.1
 + platformdirs==4.5.1
 + pytokens==0.3.0
 + referencing==0.37.0
 + rpds-py==0.30.0
 + ruamel-yaml==0.18.17
 + ruamel-yaml-clib==0.2.15
 + subprocess-tee==0.4.2
 + wcmatch==10.1
 + yamllint==1.37.1
Installed 10 executables from `ansible-core`: ansible, ansible-config, ansible-console, ansible-doc, ansible-galaxy, ansible-inventory, ansible-playbook, ansible-pull, ansible-test, ansible-vault
Installed 1 executable from `ansible-lint`: ansible-lint
Installed 1 executable: ansible-community
```

Dit installeert Ansible, ansible-lint en ansible-vault in een geïsoleerde omgeving. Controleer de versie:
```bash
tedsluis@fedora:~$ ansible-vault --version
ansible-vault [core 2.20.1]
  config file = /home/tedsluis/.ansible.cfg
  configured module search path = ['/home/tedsluis/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/tedsluis/.local/share/uv/tools/ansible/lib/python3.13/site-packages/ansible
  ansible collection location = /home/tedsluis/.ansible/collections:/usr/share/ansible/collections
  executable location = /home/tedsluis/.local/bin/ansible-vault
  python version = 3.13.11 (main, Dec  9 2025, 19:04:10) [Clang 21.1.4 ] (/home/tedsluis/.local/share/uv/tools/ansible/bin/python)
  jinja version = 3.1.6
  pyyaml version = 6.0.3 (with libyaml v0.2.5)
```

## Ansible Vault Configureren
1. Maak een default `.ansible.cfg` bestand in je $HOME directory:
```bash
tedsluis@fedora:~$ ansible-config init --disabled -t all > $HOME/.ansible.cfg
```
Bewerk *.ansible.cfg* om het vault-wachtwoordbestand in te stellen:
`vault_password_file=${HOME}/ansible-vault-pass.sh`
```bash
tedsluis@fedora:~$ vi .ansible.cfg
```
Test Ansible Vault en creeer een encrypted string:
```bash
tedsluis@fedora:~$ ansible-vault encrypt_string test -n test
Encryption successful
test: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          34666631323737336330396631353635623531306262643235376563356565646331316365336135
          3036393465343138366236326538393239346462383561650a363733333830303336366533383965
          39613030383463626564643030343237663562663064636539316462303664393764653933346461
          3666323437323064350a383238626134313433366336666535313430623132303237366265653263
          3564
```
Controleer het pad van Ansible:
```bash
tedsluis@fedora:~$ which ansible
~/.local/bin/ansible
```