# 🚗 CarIQ — India's Smart Used Car Advisor

## What Is CarIQ?
CarIQ is an AI-powered used car advisor that helps Indian buyers find 
the best value car and avoid overpaying.

## Features
- **Smart Car Finder** — Top 5 cars ranked by personalized CarIQ Score
- **Personalized Weights** — User adjusts Safety, Performance, Reliability, 
  Maintenance, Value priorities
- **Radar Charts** — Visual 5-dimension car analysis
- **Price Checker** — ML model predicts fair market price
- **Why This Car?** — Plain English explanation for every recommendation

## Tech Stack
- Python, Pandas, Scikit-learn
- Random Forest Regressor (R² = 92.19%)
- Streamlit
- Plotly

## Dataset
- 15,399 real used car transactions
- Combined from CarDekho + Global NCAP safety ratings + Real service cost data

## How To Run
pip install -r requirements.txt
streamlit run app.py

## Results
- Model Accuracy: R² = 92.19%
- Average Price Prediction Error: ₹93,068