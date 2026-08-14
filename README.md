# Super-Copa-Eleva
Website for the Super Copa Eleva Football championship in PT-BR

# How to setup (nood friendly)
If you desire to set up the Super-Copa-Eleva website locally in your laptop/PC here is how you do it;

open your terminal and type<br>
```bash
git clone https://github.com/not-dromo/Super-Copa-Eleva.git
```

then go to the Super-Copa-Eleva folder that it will be created with<br>
```bash
cd Super-Copa-Eleva
```

now you need to create and activate a virtual environment:

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

after that, you will install the programs that are necessary so that the website will run

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
