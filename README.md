# 🌍 Tourism Experience Analytics — Streamlit App

## 📌 Overview
This project is an interactive **Streamlit application** designed to analyze a <mark>tourism dataset</mark> and provide **data-driven insights**.  
The app integrates **EDA, machine learning models, and a recommendation system** to help understand tourist behavior and predict preferences.  

It includes:  
- 📊 **Exploratory Data Analysis (EDA)** with visual insights  
- 🎯 **Regression** model to predict tourist ratings  
- 🧭 **Classification** model to predict visit modes  
- 💡 **Recommendation Engine** for personalized attraction suggestions  

---

## ⚙️ Installation
Clone the repository:
```bash
git clone https://github.com/AishuS1812/Tourism_Experience_Analytics.git
cd Tourism_Experience_Analytics
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ▶️ Usage
Run the **Streamlit app** locally:
```bash
streamlit run Tourism_Analysis_app.py
```

- Upload your **Tourism Dataset.xlsx** via the sidebar  
- Or let the app auto-load the dataset if it is placed locally in the repo  

---

## 📂 Repository Structure
```
📦 Tourism_Experience_Analytics
 ┣ 📜 Tourism_Analysis_app.py        # Main Streamlit application
 ┣ 📜 requirements.txt               # Python dependencies
 ┣ 📜 README.md                      # Project documentation
 ┣ 📜 LICENSE                        # Open-source license (MIT)
 ┣ 📜 .gitignore                     # Ignore unnecessary files
 ┣ 📂 screenshots/                   # (Optional) App preview images
 ┗ 📊 Tourism_Analytics_Presentation.pptx  # Project presentation
```

---

## ✨ Features
- **Data Preparation:**  
  - <mark>Automatic merging</mark> of multiple sheets from the dataset  
  - Normalization and <mark>column renaming</mark>  
  - Handles **missing values** gracefully  

- **EDA Visualizations:**  
  - **Ratings distribution**  
  - **Top attractions** by ratings  
  - **Visit mode distribution**  
  - **Correlation heatmap**  

- **Machine Learning Models:**  
  - **Regression** → Predict tourist ratings with **Random Forest**  
  - **Classification** → Predict visit mode with **Random Forest**  
  - Model performance metrics: **MSE, RMSE, R², Accuracy, F1-score**  

- **Recommendation System:**  
  - Collaborative filtering using **SVD (Surprise library)**  
  - <mark>Popularity-based fallback recommender</mark>  

- **Interactive Streamlit UI:**  
  - Sidebar navigation (**EDA, Regression, Classification, Recommendation**)  
  - Upload custom datasets or use default  

---

## 📊 Example Outputs
- **EDA:** <mark>Histograms, bar charts, heatmaps</mark>  
- **Regression:** **RMSE**, **MSE**, and **R²** values for rating prediction  
- **Classification:** **Accuracy** & **F1-score**  
- **Recommendation:** <mark>Top-5 personalized attraction suggestions</mark>  

---

## 📂 Data
The application expects an **Excel dataset** (multi-sheet). Example sheets include:  
- Transactions  
- Users  
- Cities  
- Types  
- Visit Modes  
- Countries / Regions / Continents  
- Items (Attractions)  

👉 You can test with your own dataset by uploading via the sidebar.  

---

## 📜 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.  

---

## 🙌 Acknowledgements
- Built with [**Streamlit**](https://streamlit.io/) for interactive dashboards  
- Machine learning powered by [**scikit-learn**](https://scikit-learn.org/)  
- Recommendation system supported by [**Surprise library**](http://surpriselib.com/)  

---

## 👩‍💻 Author
**Aishwarya S**  
Project: *Tourism Experience Analytics*  
