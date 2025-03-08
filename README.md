# 🚦 Intelligent Traffic Signal Control System (SMARTFLOW)

## 📝 Project Overview

The **Intelligent Traffic Signal Control System** (SMARTFLOW) aims to optimize urban traffic flow using AI-based real-time traffic density analysis. The system dynamically adjusts signal timings based on live vehicle counts and density, ensuring smoother traffic management and reduced congestion at intersections.

## 🔧 Features

- **Real-time Traffic Detection**: Utilizes computer vision to detect vehicles and calculate traffic density in real time.
- **Adaptive Signal Control**: Dynamically adjusts traffic signal timings to minimize delays and optimize flow.
- **Vehicle Prioritization**: Prioritizes emergency vehicles and public transport for efficient traffic management.
- **Web-based Dashboard**: Provides a Streamlit-based interface for real-time visualization and monitoring.
- **Multi-Camera Support**: Handles data from multiple intersections for scalable deployment.

## 📌 Tech Stack

| Component         | Technology                  |
|-------------------|-----------------------------|
| **Frontend**      | React                   |
| **Backend**       | FastAPI                     |
| **ML Model**      | YOLOv8                      |
| **Database**      | Firestore                   |
| **Networking**    | WebSockets                  |

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

Clone the SMARTFLOW repository to your local machine:
```bash
git clone https://github.com/YourOrg/SMARTFLOW.git
cd SMARTFLOW && pip install -r requirements.txt
```

## 🖥️ Usage

1. **Run the application** and allow camera access.
2. **Monitor live traffic density** on the Streamlit dashboard.
3. **Traffic lights adjust dynamically** based on detected vehicle count.

## 🛠️ How It Works

1. **Live Video Input** → Captured from a camera at an intersection.
2. **Vehicle Detection & Counting** → YOLOv8 detects cars, bikes, and buses.
3. **Traffic Density Estimation** → `area_counter.py` calculates the percentage.
4. **Signal Adjustment** → The backend dynamically modifies timings.
5. **Data Logging & Analytics** → Historical trends stored in Firestore.

## 🏆 Future Enhancements
- 🚀 **Reinforcement Learning (RL)** for better traffic predictions.
- 🌍 **Edge Computing** for real-time processing on IoT devices.
- 📊 **Historical Data Insights** to improve urban traffic planning.

## 📜 License
This project is licensed under the MIT License.

## 🤝 Contributing
Pull requests are welcome! Feel free to open an issue or suggest improvements.

## 📧 Contact
For inquiries, reach out to **your-email@example.com** or visit our [GitHub](https://github.com/Karush2807/SMARTFLOW).
