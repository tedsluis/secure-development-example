# Secure Development Example

## Persoonlijke encrypted secrets 

Je wilt personnlijke secrets (zoals GITHUB_TOKEN, VAULTPASS) niet unencrypted op systemen laten staan (of het nu je laptop of een server in de cloud is). Ook wil je deze secrets niet elke keer handmatig uit een kluis kopieren als je ze nodig hebt. Deze instructie zorgt er voor dat je secrets encrypted op het systeem staan en dat ze decrypted worden wanneer in op het systeem inlogt, zodat je ze kunt gebruiken als environment variabelen. 

### Encrypt je persoonlijke secrets met openssl

Encrypt éénmalig je secrets met openssl met een passphrase. Later moet je deze passphrase elke keer intypen als je een nieuwe shell opent.

```bash
echo 'ZET HIER GITHUB_TOKEN' | openssl enc -aes-256-cbc -a -salt -pbkdf2 -iter 100000
enter AES-256-CBC encryption password:
Verifying - enter AES-256-CBC encryption password:
U2FsdGVkX1+H8IIliYBv9Az6GZ+jnOjIxcwEJ/hfc3iPhfhJE/RVmZ9MZdXWpEFQ

echo 'ZET HIER JE ANSIBLE VAULT TOKEN' | openssl enc -aes-256-cbc -a -salt -pbkdf2 -iter 100000
enter AES-256-CBC encryption password:
Verifying - enter AES-256-CBC encryption password:
U2FsdGVkX1/w9E3+KVIoq0S9RrgrOSO6DZuDYAg/eXzTiX2zwtogDmT/unb2Pj9KuW4yRD5E81P0b36jTssPoQ==
```
Gebruik beide hashes in de volgende stap.

### Hashes opnemen in je .bashrc

Voeg onderstaande toe aan je ~/.bashrc met de hier boven gegenereerde hashes.

```bash
# Get pass phrase
function get_pass {
  if [ -z $pass ]; then
    echo -n 'Passphrase: '
    read -s pass
    echo
  fi
}

# Github  GITHUB_TOKEN
if [ -z $GITHUB_TOKEN ]; then
        get_pass
        echo "set GITHUB_TOKEN"
        export GITHUB_TOKEN=$(echo 'HIER JE GITHUB HASH' | openssl enc -aes-256-cbc -d -a -pbkdf2 -iter 100000 -pass pass:"$pass" 2>/dev/null)
fi

# decrypt ansible-vault password:
if [ -z $VAULTPASS ]; then
        get_pass
        echo "set VAULTPASS"
        export VAULTPASS=$(echo 'HIER JE VAULT PASSWORD HASH'| openssl enc -aes-256-cbc -d -a -pbkdf2 -iter 100000 -pass pass:"$pass" 2>/dev/null)
fi

# Pass phrase weer vergeten!
unset pass

# Locatie ansible-vault-pass.sh
export ANSIBLE_VAULT_PASSWORD_FILE=${HOME}/bin/ansible-vault-pass.sh
```
Als je voortaan een nieuwe shell start, wordt door bovenstaande GITHUB_TOKEN en VAULTPASS als environment variabelen geladen.

Je kunt .bashrc ook opnieuw laden door onderstaande uit te voeren:
```bash
source ~/.bashrc

Passphrase: 
set GITHUB_TOKEN
set VAULTPASS
```
De beide environment variabelen zijn nu geladen.

### Voeg je GITHUB_TOKEN toe aan je ~/.gitconfig

```bash
$ cat .gitconfig
[user]
    name = Ted Sluis
    email = ted.sluis@gmail.com
[credential "https://github.com"]
    helper = "!f() { echo username=tedsluis; echo \"password=$GITHUB_TOKEN\"; }; f"
[pull]
    rebase = false
[push]
    autoSetupRemote = true
    default = current
[http "https://github.com"]
[includeIf "hasconfig:remote.*.url:https://github.com/**"]
    path = ~/.gitconfig-github
[init]
                defaultBranch = main
[core]
        editor = vim
```

## Encrypt en decrypt met ansible-vault

### Installeer ansible

Ansible kan zoals als pip package als via de systeem package manager geinstaleerd worden.
Installatie met pip:
```bash
$ python3 -m pip install --user ansible
Collecting ansible
  Downloading ansible-12.2.0-py3-none-any.whl.metadata (8.0 kB)
Collecting ansible-core~=2.19.4 (from ansible)
  Downloading ansible_core-2.19.4-py3-none-any.whl.metadata (7.7 kB)
Collecting jinja2>=3.1.0 (from ansible-core~=2.19.4->ansible)
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Requirement already satisfied: PyYAML>=5.1 in ./.pyenv/versions/3.11.9/lib/python3.11/site-packages (from ansible-core~=2.19.4->ansible) (6.0.2)
Collecting cryptography (from ansible-core~=2.19.4->ansible)
  Downloading cryptography-46.0.3-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (5.7 kB)
Requirement already satisfied: packaging in ./.pyenv/versions/3.11.9/lib/python3.11/site-packages (from ansible-core~=2.19.4->ansible) (25.0)
Collecting resolvelib<2.0.0,>=0.5.3 (from ansible-core~=2.19.4->ansible)
  Downloading resolvelib-1.2.1-py3-none-any.whl.metadata (3.7 kB)
Collecting MarkupSafe>=2.0 (from jinja2>=3.1.0->ansible-core~=2.19.4->ansible)
  Downloading markupsafe-3.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Collecting cffi>=2.0.0 (from cryptography->ansible-core~=2.19.4->ansible)
  Downloading cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography->ansible-core~=2.19.4->ansible)
  Downloading pycparser-2.23-py3-none-any.whl.metadata (993 bytes)
Downloading ansible-12.2.0-py3-none-any.whl (53.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 53.6/53.6 MB 11.1 MB/s eta 0:00:00
Downloading ansible_core-2.19.4-py3-none-any.whl (2.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.4/2.4 MB 11.3 MB/s eta 0:00:00
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Downloading resolvelib-1.2.1-py3-none-any.whl (18 kB)
Downloading cryptography-46.0.3-cp311-abi3-manylinux_2_34_x86_64.whl (4.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 11.4 MB/s eta 0:00:00
Downloading cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (215 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 215.6/215.6 kB 10.9 MB/s eta 0:00:00
Downloading markupsafe-3.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Downloading pycparser-2.23-py3-none-any.whl (118 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 118.1/118.1 kB 11.3 MB/s eta 0:00:00
Installing collected packages: resolvelib, pycparser, MarkupSafe, jinja2, cffi, cryptography, ansible-core, ansible
Successfully installed MarkupSafe-3.0.3 ansible-12.2.0 ansible-core-2.19.4 cffi-2.0.0 cryptography-46.0.3 jinja2-3.1.6 pycparser-2.23 resolvelib-1.2.1

[notice] A new release of pip is available: 24.0 -> 25.3
[notice] To update, run: pip install --upgrade pip
```

Controleer of ansible werkt:
```bash
$ ansible --version
ansible [core 2.19.4]
  config file = None
  configured module search path = ['/home/tedsluis/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/tedsluis/.local/lib/python3.11/site-packages/ansible
  ansible collection location = /home/tedsluis/.ansible/collections:/usr/share/ansible/collections
  executable location = /home/tedsluis/.local/bin/ansible
  python version = 3.11.9 (main, Nov 19 2025, 21:54:26) [GCC 15.2.1 20251022 (Red Hat 15.2.1-3)] (/home/tedsluis/.pyenv/versions/3.11.9/bin/python3)
  jinja version = 3.1.6
  pyyaml version = 6.0.3 (with libyaml v0.2.5)
```

### Creeer een ~/bin/ansible-vault-pass.sh file

```bash
mkdir -p ~/bin

cat > ~/bin/ansible-vault-pass.sh << 'EOF'
#!/usr/bin/env bash

if [ -z "$VAULTPASS" ]; then
  echo "VAULTPASS is not set" >&2
  exit 1
fi

printf '%s\n' "$VAULTPASS"
EOF

chmod 700 ~/bin/ansible-vault-pass.sh
```

