from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
import os

app = FastAPI(title="LEGO Predictor API",
              description="API для предсказания категорий LEGO наборов")

# Модель входных данных
class LegoInput(BaseModel):
    parts_count: int
    theme: str

    # Примеры для Swagger
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "parts_count": 500,
                    "theme": "space"
                },
                {
                    "parts_count": 1200,
                    "theme": "city"
                }
            ]
        }

# Загрузка модели при старте
model = None
try:
    model_path = os.path.join('models', 'model.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("Модель успешно загружена")
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")

@app.post("/predict/", summary="Предсказание категории LEGO")
async def predict(input_data: LegoInput):
    """
    Предсказывает категорию LEGO набора на основе:
    - Количества деталей (parts_count)
    - Тематики набора (theme)
    """
    if not model:
        raise HTTPException(status_code=500, detail="Модель не загружена")
    
    try:
        # Преобразование входных данных
        features = np.array([[input_data.parts_count, input_data.theme]])
        
        # Получение предсказания
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        return {
            "prediction": str(prediction),
            "probabilities": {str(cls): float(prob) for cls, prob in zip(model.classes_, probabilities)},
            "input_data": input_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Перейдите на /docs для работы с API"}
