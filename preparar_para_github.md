# 📁 Guía para Subir Proyecto a GitHub (Sin Git)

## 🎯 **Paso 1: Crear Repositorio en GitHub**

1. **Ir a GitHub.com** y iniciar sesión
2. **Crear nuevo repositorio**:
   - Nombre: `sistema-inversiones`
   - Descripción: `Sistema de inversiones con aprendizaje automático`
   - **IMPORTANTE**: Seleccionar **"Public"**
   - **NO marcar** "Add a README file"
   - **NO marcar** "Add .gitignore"
   - **NO marcar** "Choose a license"
3. **Hacer clic en "Create repository"**

## 📂 **Paso 2: Archivos a Subir**

### **Archivos Principales** (subir estos primero):
- ✅ `README.md`
- ✅ `requirements.txt`
- ✅ `render.yaml`
- ✅ `.gitignore`

### **Carpeta Backend** (subir completa):
- ✅ `backend/` (toda la carpeta)

### **Carpeta Frontend** (subir completa):
- ✅ `frontend/` (toda la carpeta)

### **Carpeta App Móvil** (subir completa):
- ✅ `app_movil/` (toda la carpeta)

### **Scripts y Documentación**:
- ✅ `monitoreo_remoto.py`
- ✅ `DEPLOYMENT.md`
- ✅ `DOCUMENTACION_COMPLETA.md`

## 🚀 **Paso 3: Subir Archivos**

### **3.1 Subir README.md**
1. En tu repositorio GitHub, haz clic en **"Add file"** → **"Create new file"**
2. Nombre del archivo: `README.md`
3. Copiar y pegar el contenido del archivo `README.md`
4. Hacer clic en **"Commit new file"**

### **3.2 Subir requirements.txt**
1. **"Add file"** → **"Create new file"**
2. Nombre: `requirements.txt`
3. Copiar contenido del archivo `requirements.txt`
4. **"Commit new file"**

### **3.3 Subir render.yaml**
1. **"Add file"** → **"Create new file"**
2. Nombre: `render.yaml`
3. Copiar contenido del archivo `render.yaml`
4. **"Commit new file"**

### **3.4 Subir .gitignore**
1. **"Add file"** → **"Create new file"**
2. Nombre: `.gitignore`
3. Copiar contenido del archivo `.gitignore`
4. **"Commit new file"**

### **3.5 Subir Carpeta Backend**
1. **"Add file"** → **"Upload files"**
2. Arrastrar toda la carpeta `backend/` desde tu computadora
3. **"Commit changes"**

### **3.6 Subir Carpeta Frontend**
1. **"Add file"** → **"Upload files"**
2. Arrastrar toda la carpeta `frontend/` desde tu computadora
3. **"Commit changes"**

### **3.7 Subir Carpeta App Móvil**
1. **"Add file"** → **"Upload files"**
2. Arrastrar toda la carpeta `app_movil/` desde tu computadora
3. **"Commit changes"**

### **3.8 Subir Scripts Restantes**
1. **"Add file"** → **"Upload files"**
2. Arrastrar los archivos:
   - `monitoreo_remoto.py`
   - `DEPLOYMENT.md`
   - `DOCUMENTACION_COMPLETA.md`
3. **"Commit changes"**

## ✅ **Verificación Final**

Tu repositorio debería tener esta estructura:
```
sistema-inversiones/
├── README.md
├── requirements.txt
├── render.yaml
├── .gitignore
├── backend/
│   ├── main.py
│   ├── services/
│   ├── models/
│   └── ...
├── frontend/
│   ├── src/
│   ├── public/
│   └── ...
├── app_movil/
│   ├── lib/
│   ├── pubspec.yaml
│   └── ...
├── monitoreo_remoto.py
├── DEPLOYMENT.md
└── DOCUMENTACION_COMPLETA.md
```

## 🎉 **¡Listo!**

Una vez que hayas subido todos los archivos, tu repositorio estará disponible en:
```
https://github.com/Lbernardoni77/sistema-inversiones
```

## 🚀 **Próximo Paso: Desplegar en Render**

Ahora puedes proceder con el despliegue en Render siguiendo la guía en `DEPLOYMENT.md`.

---

**💡 Consejo**: Si tienes problemas con algún archivo, puedes subirlo uno por uno usando "Create new file" y copiando el contenido. 