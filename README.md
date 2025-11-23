# Secure Development Example

## Inhoud

1. **Encrypt en decrypt persoonlijke secrets met openssl**
  * 1.1 Encrypt je persoonlijke secrets met openssl
  * 1.2 Hashes opnemen in je .bashrc
  * 1.3 Voeg je GITHUB_TOKEN toe aan je ~/.gitconfig
2. **Encrypt en decrypt met ansible-vault**
  * 2.1 Installeer ansible
  * 2.2 Creëer een ~/bin/ansible-vault-pass.sh file met je VAULTPASS
  * 2.3 env-file encrypten
  * 2.4 “sourcen” van secrets.env file in je shell
  * 2.5 Voorkom dat een .env file unencrypted gecommit kan worden
  * 2.6 Test pre-commit webhook
  * 2.7 Ansible Vault encrypted strings opnemen in shell file
  * 2.8 Ansible Vault lezen vanuit python
  * 2.9 Geef Ansible Vault encrypted secrets door aan een container
3. **Podman**
  * 3.1 Podman vs Docker
  * 3.2 Beperkingen van Podman op Windows
  * 3.3 Beperkingen van Podman op macOS
  * 3.4 Wanneer is Podman wel bruikbaar op Windows/macOS?
  * 3.5 Installatie Podman
  * 3.6 Podman desktop
  * 3.7 


## 1. Encrypt en decrypt persoonlijke secrets met openssl

Je wilt persoonlijke secrets (zoals GITHUB_TOKEN, VAULTPASS) niet unencrypted op systemen laten staan (of het nu je laptop of een server in de cloud is). Ook wil je deze secrets niet elke keer handmatig uit een kluis kopiëren als je ze nodig hebt. Deze instructie zorgt ervoor dat je secrets encrypted op het systeem staan en dat ze decrypted worden je op het systeem inlogt, zodat je ze kunt gebruiken als environment-variabelen. 

We gebruiken [openssl encryption](https://docs.openssl.org/master/man1/openssl-enc/), omdat het zeer betrouwbaar en overal inzetbaar is.

### 1.1 Encrypt je persoonlijke secrets met openssl

Encrypt éénmalig je secrets met openssl met een passphrase. Later moet je deze passphrase elke keer intypen als je een nieuwe shell opent.

```bash
echo 'ZET HIER GITHUB_TOKEN' | openssl enc -aes-256-cbc -a -salt -pbkdf2 -iter 100000
enter AES-256-CBC encryption password:
Verifying - enter AES-256-CBC encryption password:
U2FsdGVkX19ByHvXvi1QnFYmdO/GnT7OP/WG7rRlNtUCxT4sjYhFsbQ8hTTbr5HF

echo 'ZET HIER JE ANSIBLE VAULT PASSWORD' | openssl enc -aes-256-cbc -a -salt -pbkdf2 -iter 100000
enter AES-256-CBC encryption password:
Verifying - enter AES-256-CBC encryption password:
U2FsdGVkX18EbdzXTzzeiTjCbn3R2nmZQ4okG7JNd16xaKQ+TVGaPTTuPixPzoWZ
nE8xqfQ2V2g149IBc5VfMkYxHtagOzhG4dxr0gBZH9I=
  # Maak hier één regel van!
```
Gebruik beide hashes in de volgende stap.

**Belangrijk:** Openssl en Ansible Vault gebruiken beide **AES-256** encryptie. Dit is extreem sterk en wanneer het wachtwoord lang genoeg is (35+ karakters) ook geschikt om publiek op internet te tonen. Met 35 willekeurige tekens zit je ver boven de grens van wat nodig is. Je bent veilig, zelfs tegen inlichtingendiensten, toekomstige supercomputers en het is niet te kraken voordat de zon opgebrand is (voor brute-force zijn in totaal combinaties $94^{35}$ mogelijk). Je zou met 25 tekens ook al volkomen veilig zijn geweest.

| Type encryptie         | Aantal karakters password | Toepassing                                                         |
|------------------------|---------------------------|--------------------------------------------------------------------|
| Openssl passphrase     | 8+                        | Een passphrase die je kunt onthouden, geschikt voor lokaal gebruik.|
| Ansible Vault Password | 35+                       | Een passphrase die gegenereerd is, geschikt voor publiek internet. |

Zo genereer je een veilig ansible vault wachtwoord van 35 karakters:
```bash
$ openssl rand -base64 35
fpErh3+M69VXiZYZ4ZfzNYBkUQFkZichpkRCH2VOEpWxRJQ=
```

### 1.2 Hashes opnemen in je .bashrc

Voeg onderstaande toe aan je ~/.bashrc met de hierboven gegenereerde hashes.

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
        export VAULTPASS=$(echo 'HIER JE ANSIBLE VAULT PASSWORD HASH'| openssl enc -aes-256-cbc -d -a -pbkdf2 -iter 100000 -pass pass:"$pass" 2>/dev/null)
fi

# Pass phrase weer vergeten!
unset pass

# Locatie ansible-vault-pass.sh
export ANSIBLE_VAULT_PASSWORD_FILE=${HOME}/bin/ansible-vault-pass.sh
```
Als je voortaan een nieuwe shell start, zul je altijd je passphrase moeten opgeven. Daarna worden de hashes gedecrypt en zijn **GITHUB_TOKEN** en **VAULTPASS** als environment-variabelen geladen.

Je kunt .bashrc ook opnieuw laden door onderstaande uit te voeren:
```bash
source ~/.bashrc

Passphrase: 
set GITHUB_TOKEN
set VAULTPASS
```
De beide environment-variabelen zijn nu geladen.

### 1.3 Voeg je GITHUB_TOKEN toe aan je ~/.gitconfig

Nu je **GITHUB_TOKEN** een environment-variabele is, kun je die gebruiken in de ~/.gitconfig:
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

## 2. Encrypt en decrypt met ansible-vault

Je wilt secrets veilig in git repo's op internet bewaren door ze met Ansible Vault (AES-256) met een lang wachtwoord (35+ karakters) te encrypten. 

### 2.1 Installeer Ansible

**ansible-vault** is onderdeel van Ansible. Ansible kan zowel via pip als via de systeempackage manager geïnstalleerd worden, zie:

* https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html
* https://docs.ansible.com/projects/ansible/latest/installation_guide/installation_distros.html

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

Installatie met package manager Ubuntu:
```bash
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo add-apt-repository --yes --update ppa:ansible/ansible
$ sudo apt install ansible
```

Controleer of Ansible werkt:
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

Algemene informatie over Ansible Vault: https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html

### 2.2 Creëer een ~/bin/ansible-vault-pass.sh file met je VAULTPASS

Maak een **ansible-vault-pass.sh** aan, die je **VAULTPASS** environment-variabele doorgeeft aan ansible-vault:
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
De locatie van je **ansible-vault-pass.sh** file staat in **ANSIBLE_VAULT_PASSWORD_FILE** (die in je .bashrc ingesteld is).

### 2.3 env-file encrypten

Creëer een secrets.env file met secrets:
```bash
# secrets.env
export DB_USER="appuser"
export DB_PASS="super-geheim"
export API_TOKEN="abc123"
```
Let op: deze file moet je nooit unencrypted naar git pushen!

Encrypt de secrets.env file met ansible-vault:
(het vault wachtwoord komt uit ANSIBLE_VAULT_PASSWORD_FILE)
```bash
$ ansible-vault encrypt secrets.env

Encryption successful
```

secrets.env bevat nu zoiets als:
```bash
$ cat secrets.env 
$ANSIBLE_VAULT;1.1;AES256
37343636643236363466623666333934613165636139303164623965643163666466393461383032
3435616162633437343938666138343431666261316136380a653666313539363838313163386536
62326664376139633539323534653335326566313431336238356266336231323165323061313535
3062633737396239340a343464346432623331373835353438363234393065613633663239663036
30373533363432643934366163353563323235333334363731643363663635666566653566313266
66636539393339323439303435333361303266653765643162666239633362323064393134343665
32366664383061356666393964376163323833646336333764366366356330333133626532356634
32626666663039393533313765373261626430303939373330303061323364363039613463333734
6538
```
Dit is veilig om naar git te pushen.


### 2.4 “sourcen” van secrets.env file in je shell

(het vault wachtwoord komt uit ANSIBLE_VAULT_PASSWORD_FILE)
```bash
$ source <(ansible-vault view secrets.env)
```
Bewijs dat de environment-variabelen in je shell geladen zijn:
```bash
$ env | grep -P '(DB_USER|DB_PASS|API_TOKEN)'
API_TOKEN=abc123
DB_USER=appuser
DB_PASS=super-geheim
```

### 2.5 Voorkom dat een .env file unencrypted gecommit kan worden

Wat je NOOIT wilt, is dat je de secrets.env file unencrypted commit in je repo. Een pre-commit hook kan testen of je .env file ansible vault encrypted is. Als dat niet het geval is, wordt de commit afgebroken.

Om een pre-commit webhook te creeeren, voer onderstaande uit in elke repo waar je .env files gebruikt:
```bash
cd /pad/naar/jouw/repo

mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# extensie(s) die niet plain-text gecommit mogen worden
EXTENSIONS=("env")

# functie: check of bestand een vault-header heeft
is_vault_file() {
  local file="$1"
  # alleen gewone files checken
  [ -f "$file" ] || return 0

  if grep -q '\$ANSIBLE_VAULT;' "$file"; then
    return 0   # OK, is vaulted
  else
    return 1   # NIET vaulted
  fi
}

# krijg lijst van gestagede bestanden (A/M/C/R) met matching extensie
files_to_check=$(git diff --cached --name-only --diff-filter=ACMR | grep -E "\.($(IFS='|'; echo "${EXTENSIONS[*]}"))$" || true)

[ -z "$files_to_check" ] && exit 0

failed=0

for f in $files_to_check; do
  if ! is_vault_file "$f"; then
    echo "ERROR: File '$f' heeft extensie .env maar lijkt NIET ansible-vault encrypted (geen \$ANSIBLE_VAULT header)." >&2
    failed=1
  fi
done

if [ "$failed" -ne 0 ]; then
  echo
  echo "Commit afgebroken. Encrypt deze files eerst, bijvoorbeeld met:"
  echo "  ansible-vault encrypt <bestand>"
  echo
  exit 1
fi

exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### 2.6 Test pre-commit webhook

Decrypt de secrets.env file:
```bash
$ ansible-vault decrypt secrets.env 
Decryption successful

$ cat secrets.env 
export DB_USER="appuser"
export DB_PASS="super-geheim"
export API_TOKEN="abc123"
```
Voer een commit uit en stel vast dat deze wordt afgebroken:
```bash
$ git add secrets.env
$ git commit -m "test"
ERROR: File 'secrets.env' heeft extensie .env maar lijkt NIET ansible-vault encrypted (geen $ANSIBLE_VAULT header).

Commit afgebroken. Encrypt deze files eerst, bijvoorbeeld met:
  ansible-vault encrypt <bestand>
```
Encrypt de secrets.env file:
```bash
$ ansible-vault encrypt secrets.env 
Encryption successful
```
Voer een commit uit en stel vast dat dit lukt:
```bash
$ git add secrets.env
$ git commit -m "test"
[main 8832004] test
 1 file changed, 9 insertions(+), 10 deletions(-)
```

### 2.7 Ansible Vault encrypted strings opnemen in shell file

Een andere methode om environment variabelen te sourcen is met een shell script. Het voordeel is dat je kunt zien welke environment variabelen voorkomen in het script, zonder dat je de file hoeft te decrypten.

Voer onderstaande commando uit en plak een wachtwoord dat je wilt encrypten. Druk 2x op ctrl-d na het invoeren van het wachtwoord:
(het vault wachtwoord komt uit ANSIBLE_VAULT_PASSWORD_FILE)
```bash
$ ansible-vault encrypt_string 
Reading plaintext input from stdin. (ctrl-d to end input, twice if your content does not already have a newline)
export DB_USER="appuser"
Encryption successful
!vault |
          $ANSIBLE_VAULT;1.1;AES256
          65313130666636636334333664623337346636333036386366653037333038376336366563333732
          3464633332366638396533393037336565356465323438330a343365343261346238356666646239
          34366662623562356435613664363134353066383732326432353165383664386263366334343565
          3033333765626332660a363865646566386264663766323161656333636536326133306637336135
          32383235666233303363363462623864313937656233333838653031616534643661

```
Kopieer de output naar een file, zoals hieronder. Herhaal dit voor al je wachtwoorden
```bash
#!/usr/bin/env bash
# Dit script kun je 'source'en.
# Zorg dat ANSIBLE_VAULT_PASSWORD_FILE of vault_password_file goed staat.

# Helper functie: leest vaulted string van stdin en echo’t de plaintext
vault_decrypt() {
  ansible-vault decrypt 2>/dev/null
}

# --------- VAR 1 ---------
export DB2_USER="$(
vault_decrypt << 'EOF'
$ANSIBLE_VAULT;1.1;AES256
65313130666636636334333664623337346636333036386366653037333038376336366563333732
3464633332366638396533393037336565356465323438330a343365343261346238356666646239
34366662623562356435613664363134353066383732326432353165383664386263366334343565
3033333765626332660a363865646566386264663766323161656333636536326133306637336135
32383235666233303363363462623864313937656233333838653031616534643661
EOF
)"

# --------- VAR 2 ---------
export DB2_PASS="$(
vault_decrypt << 'EOF'
$ANSIBLE_VAULT;1.1;AES256
35323865653431346562656238303562396264386662343964613934343665353739663039613738
6136633233646537316531323130306436356464636661640a623237643861666238653236663166
36383465376461373565313139303839303262373265363433346263633164313533333135303366
3638373330343866310a353739646461383332633362323062393437373139333138333261346266
3036
EOF
)"

# --------- VAR 3 ---------
export API2_TOKEN="$(
vault_decrypt << 'EOF'
$ANSIBLE_VAULT;1.1;AES256
36326236613836306361303239323737383162353866326530303431376239613933663766646336
3161333363326635636137346166323466653366626661360a376266636235313866306561343334
61336134376263306330653063393161623631636333663362303161666639613733376365373765
6533373663623135620a666230636531666463306637623933326435663864623264663965363739
6136
EOF
)"
```
Test het resultaat:
(het vault wachtwoord komt uit ANSIBLE_VAULT_PASSWORD_FILE)
```bash
$ source ./vault_env.sh
```
Toon de inhoud van de enviroment variabelen:
```bash
$ env | grep -P '(DB2_USER|DB2_PASS|API2_TOKEN)'
DB2_PASS=super-geheim
DB2_USER=export DB_USER="appuser"
API2_TOKEN=abc123
```

### 2.8 Ansible Vault lezen vanuit python

Voorbeeld hoe je een secrets.env file leest vanuit python:
```python
import os
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH

# Vault-wachtwoord uit environment variabele VAULTPASS
vaultpass = os.getenv("VAULTPASS")
if not vaultpass:
    raise RuntimeError("Environment variabele VAULTPASS is niet gezet")

password = vaultpass.encode("utf-8")  # bytes maken

# VaultLib initialiseren met één vault-id 'default'
vault = VaultLib(secrets={DEFAULT_VAULT_ID_MATCH: VaultSecret(password)})

# Vault-file inlezen
with open("secrets.env", "rb") as f:
    ciphertext = f.read()

# Decrypten
plaintext_bytes = vault.decrypt(ciphertext)
plaintext = plaintext_bytes.decode("utf-8")

print("Inhoud van secrets.env:")
print(plaintext)
```

### 2.9. Geef Ansible Vault encrypted secrets door aan een container

Voer het voorbeeld uit met de files in deze repo:

* [Dockerfile](./Dockerfile)
* [docker-compose.yml](./docker-compose.yml)
* [app.py](./app.py)
* [secrets.env](./secrets.env)    # ansible-vault encrypted file

Build & run met Docker of Podman Compose. In het voorbeeld hieronder wordt podman gebruikt. Je kunt podman vervangen door docker.
```bash
 $ podman compose up --build
>>>> Executing external compose provider "/usr/bin/podman-compose". Please see podman-compose(1) for how to disable this message. <<<<

STEP 1/6: FROM python:3.12-slim
STEP 2/6: ENV PYTHONUNBUFFERED=1
--> Using cache 560ff49a9564438592428b363fa45e93711984309138c4d1873b417a74a3fc49
--> 560ff49a9564
STEP 3/6: WORKDIR /app
--> Using cache bffeea1e6b726e075b8f9c7f6612c0c9d0930b5994e4416257ffcc9df5fcdd9e
--> bffeea1e6b72
STEP 4/6: COPY app.py /app/
--> Using cache 9bebc07daf2629ca1aa0a9c7bee5ea40182fadf9d9fc319cc03d30eb516ef090
--> 9bebc07daf26
STEP 5/6: RUN pip install --no-cache-dir --root-user-action=ignore ansible-core
--> Using cache 813290975be729a186368ce7762c3609fdc2f3122779bd208ff40bb608497400
--> 813290975be7
STEP 6/6: CMD ["python", "app.py"]
--> Using cache 1560f33e60c86181531e1ad7d29020e29ab20e58780982b4159cd98617af2f13
COMMIT secure-development-example_vault-demo
--> 1560f33e60c8
Successfully tagged localhost/secure-development-example_vault-demo:latest
1560f33e60c86181531e1ad7d29020e29ab20e58780982b4159cd98617af2f13
[vault-demo] | === Inhoud van secrets.env (decrypted) ===
[vault-demo] | export DB_USER="appuser"
[vault-demo] | export DB_PASS="super-geheim"
[vault-demo] | export API_TOKEN="abc123"
[vault-demo] | 
```
In dit voorbeeld wordt de environment variabele **VAULTPASS** van de huidige shell doorgegeven aan de container en gebruikt om de **secrets.env** file te decrypten.

## 3. Podman

### Podman vs Docker

| Onderdeel                             | **Docker**                                                                                                      | **Podman**                                                                                                   |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Architectuur**                      | *Client–server model* met een centrale daemon (`dockerd`) die root-privileges heeft.                            | *Daemonless*: werkt zonder centrale service; elke container is een eigen proces.                             |
| **Rootless container support**        | Ondersteund, maar minder volwassen en niet standaard.                                                           | Ontworpen voor rootless gebruik. Geen extra permissies nodig voor standaard gebruikers      |
| **Security model**                    | Docker daemon draait meestal als root → grotere aanvalsvector.                                                  | Containers draaien als normale gebruiker zonder speciale daemon → **veiliger by design**.                    |
| **Compatibiliteit**                   | De facto standaard, breed ondersteund door tooling, tutorials, CI/CD.                                           | 100% CLI-compatibel met Docker, zelfde container images en Dockerfile format.                                         |
| **Images & registries**               | Gebruikt containerd en Docker Hub als standaard registry.                                                       | Gebruikt eigen storage (libcontainers). Kan met alle OCI-images werken.                                      |
| **Secrets**                           | Volwaardige secrets alleen in **Swarm mode**. In Compose: secrets via files. BuildKit heeft build-time secrets. | **Host-level Podman secrets** beschikbaar voor zowel runtime (mount/env) als voor Kube-play. |
| **Pods support**                      | Geen pods-concept, containers zijn individueel.                                                                 | **Native pods**, vergelijkbaar met Kubernetes pods → meerdere containers, gedeeld netwerk/IPC.               |
| **Systemd integratie**                | Mogelijk via `docker run` + handmatige units.                                                                   | **Out-of-the-box integratie** via *Quadlet* → declaratieve `.container`/`.pod` files.                            |
| **Compose support**                   | Officiële Docker Compose (V2).                                                                                  | `podman compose` is compatibel, maar iets beperkter; goed genoeg voor de meeste use-cases.                   |
| **Kubernetes integratie**             | `docker stack deploy` en Swarm zijn alternatief, geen native K8s YAML.                                          | `podman kube generate / play` → direct containers ↔ K8s YAML.                                                |
| **Daemon overhead**                   | Vereist een draaiende daemon → meer memory/CPU footprint.                                                       | Geen daemon → lichter en efficiënter.                                                                        |
| **Logging**                           | Via Docker daemon (json-file, syslog, etc.).                                                                    | Standaard via journald (systemd) + Podman zelf.                                                              |
| **Auto-updates**                      | Geen ingebouwd systeem; rely via compose of scripts.                                                            | **podman auto-update** met image labels.                                                                     |
| **Init systeem integratie (systemd)** | Normaal zelf systemd units maken of `docker start` via scripts.                                                 | Quadlet genereert automatisch systemd services → veel cleaner.                                               |
| **OS voorkeuren**                     | Zeer populair op Windows, macOS en Linux (via Docker Desktop).                                                          | Draait op elke Linux distro. Minder geschikt voor Windows/macOS vanwege beperkingen, zie hieronder.  |


### 3.2 Beperkingen van Podman op Windows

Podman draait niet native op Windows. Je hebt altijd één van deze nodig:

* WSL2 (Windows Subsystem for Linux) met een Linux-distro
* Een VM via Podman Machine (met QEMU of Hyper-V)

❌ 1. Geen native containers op Windows

* Podman kan geen Windows-containers draaien.
* Alleen Linux-containers werken, via een Linux-omgeving.

❌ 2. Beperktere integratie met Windows filesystems

* File mounting (bind mounts) vanuit Windows kan problemen geven:
    * bestandsrechten/ownership niet correct overgenomen
    * performance issues bij grote mounts
    * SELinux/AppArmor contexten ontbreken
* In WSL2:
    * Mounts vanuit /mnt/c/... zijn stuk trager dan mounts in de Linux-filesystemruimte.

❌ 3. Podman Machine verplicht voor system-level functies

* Dingen zoals systemd, pods, cgroups, rootless-mode werken alleen goed in een Linux VM.
* Dit betekent extra overhead t.o.v. Docker Desktop, dat hier beter geoptimaliseerd voor is.

❌ 4. Networking is beperkt / anders dan op Linux

* Containers kunnen geen Windows-poorten direct claimen.
* Poorten worden ge-forward via WSL2/VM → vertraagt en kan conflicten geven.
* Multi-container pods werken wel, maar soms met afwijkende netwerknamespaces.

❌ 5. Minder tooling-support

* Minder IDE-integraties op Windows (t.o.v. Docker Desktop).
* Sommige tools verwachten Docker socket (/var/run/docker.sock) — Podman ondersteunt dit via een compatibiliteitslaag, maar niet altijd perfect.

❌ 6. Geen Podman Quadlet / systemd integratie op Windows zelf

* systemd werkt alleen binnen de Linux VM, niet op Windows.

### 3.3 Beperkingen van Podman op macOS

macOS is Unix-achtig, maar Podman werkt niet native omdat het Docker/Podman-kernel-features mist. Je hebt altijd een VM nodig (Podman Machine met QEMU/Apple HVF).

❌ 1. Geen native containers

* Net als op Windows werkt Podman altijd via een Linux-VM.
* Er zijn geen macOS containers.

❌ 2. Filesystem overhead & beperkingen

* Bind mounts tussen macOS host en VM zijn ong. 10× langzamer dan native Linux.
* Bestandsrechten / permissies vertalen niet 1-op-1.
* Performance voor databases of veel I/O is slecht op gedeelde mounts.

❌ 3. Networking niet gelijk aan Linux

* Containers draaien in een VM-netwerk, niet in macOS zelf.
* Poorten moeten geforward worden; host-to-container networking werkt, container-to-host is beperkt.

❌ 4. Geen systemd integratie op macOS

* Quadlet/systemd werkt enkel in de VM.
* Kan niet als macOS service draaien.

❌ 5. Minder geïntegreerde UX dan Docker Desktop

* Docker Desktop biedt:
* UI voor images/containers
* Kubernetes ingebouwd
* File sharing UI
* Networking optimalisaties
* Podman heeft dit op macOS niet.

❌ 6. Geen virtuele GPU / hardware acceleration

* GPU passthrough → niet ondersteund.
* Sommige AI workloads zijn daardoor niet bruikbaar.

### 3.4 Wanneer is Podman wel bruikbaar op Windows/macOS?

Goed te doen voor:

✔ Backend development
✔ Gebruiken als Docker replacement (CLI compatibel)
✔ Testen van pods + images
✔ CI/CD pipelines op laptop
✔ Security testing in een Linux-VM

Niet ideaal voor:

✘ High-performance workloads
✘ Database development met veel disk I/O
✘ Productie-achtige setups (networking/mounts anders dan Linux)
✘ Heavy tooling die Docker Desktop features verwacht


https://podman.io/features