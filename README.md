# Tourism_Experience_Analytics
# 🗺️ Tourism Experience Analytics

This repository contains the implementation of the **Tourism Experience Analytics** project, focused on enhancing user experiences in the tourism domain through data-driven techniques.

---

## 📌 Objectives

- **Regression**: Predict user ratings for tourist attractions.
- **Classification**: Predict visit modes (e.g., Family, Friends, Business).
- **Recommendation System**: Suggest attractions based on preferences and history.

---

## 🧩 Dataset Details

The project uses structured datasets with the following key components:

- **Transaction Data**: User ratings and visit details.
- **User Data**: Demographic information.
- **Attraction Data**: Types and locations.
- **Supporting Tables**: Region, Continent, Visit Mode, Attraction Type.

---

## 🧠 Key Technologies

- **Python**
- **Pandas, NumPy, Scikit-learn**
- **LightGBM/XGBoost**
- **Matplotlib, Seaborn**
- **Streamlit** for web app deployment

---

## 🔍 Project Workflow

1. **Data Cleaning & Preprocessing**
   - Handle missing values, duplicates
   - Feature encoding and normalization

2. **EDA**
   - Visual insights into user behavior and travel patterns

3. **Modeling**
   - Regression: Predict attraction ratings
   - Classification: Predict visit mode
   - Recommendation: Collaborative filtering

4. **Evaluation**
   - Regression: R² Score, RMSE
   - Classification: Accuracy, F1-score
   - Recommendation: MAP, RMSE

5. **Deployment**
   - Streamlit app for user inputs and real-time predictions

---

## 🚀 How to Use

```bash
git clone https://github.com/yourusername/tourism-experience-analytics.git
cd tourism-experience-analytics
pip install -r requirements.txt
streamlit run app.py
