# Super-Copa-Eleva
[🇧🇷 Português](#versão-em-português) | [🇺🇸 English](#english-version)<br>
Site para o campeonato de futebol da Super Copa Eleva<br>
Website for the Super Copa Eleva Football championship in PT-BR

🚧Projeto ainda em progresso/Project still in progress🚧

# Versão em Português
**Como fazer o setup (beginner friendly)**<br>
Se você quer rodar o Site da Super Copa Eleva localmente no seu pc é só seguir essas etapas

abra seu terminal e escreva<br>
```bash
git clone https://github.com/not-dromo/Super-Copa-Eleva.git
```

Depois entre na pasta criada usando o seguinte comando<br>
```bash
cd Super-Copa-Eleva
```

Agora você tem que criar um ambiente virtual e iniciá-lo

**Linux/MacOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Powershell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Depois disso as dependências necessárias usando requirements.txt

```bash
pip install -r requirements.txt
```

Por último crie o seu .env e adicione essas informações dentro dele com as suas senhas do banco de dados e do cloudnary

```
DATABASE_URL=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

Agora ta tudo pronto e é só rodar o site

**Linux/MacOS:**
```bash
python3 app.py
```

**Windows (PowerShell)**
```powershell
python app.py
``` 


# English Version
**How to setup (beginner friendly)**<br>
If you desire to set up the Super-Copa-Eleva website locally in your laptop/PC here is how you do it:

open your terminal and type<br>
```bash
git clone https://github.com/not-dromo/Super-Copa-Eleva.git
```

Then, enter the newly created folder:<br>
```bash
cd Super-Copa-Eleva
```

Now you need to create and activate a virtual environment:

**Linux/MacOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Powershell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Now, install the project's dependencies using requirements.txt

```bash
pip install -r requirements.txt
```

lastly just create the file .env in the project root (i.e. outside of all folders and inside Super-Copa-Eleva) with the following content:

```
DATABASE_URL=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

and you are good to go! Just run the app with

**Linux/MacOS:**
```bash
python3 app.py
```

**Windows (PowerShell)**
```powershell
python app.py
``` 
