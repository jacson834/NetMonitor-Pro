import uvicorn
import sys
import os

# Adiciona a pasta backend ao path para os imports funcionarem corretamente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)