# ⚽ FPL Prediction Pipeline

This repository contains a pipeline for **merging datasets, predicting xPoints, and generating starting lineup predictions** for Fantasy Premier League players.
```
notebook/
│
├── merge-gw-season/
│ ├── merge_dataset.py
│ └── combine_players_info.py
│
├── predict-xpoints/
│ ├── predict_xpoints_general.py
│ ├── predict_xpoints_goalkeeper.py
│ ├── predict_xpoints_defender.py
│ ├── predict_xpoints_midfielder.py
│ └── predict_xpoints_forward.py
│
└── starting-lineup/
├── predict_lineup_general.py
└── predict_lineup_per_position.py
```


## 🛠️ Notes

- Run the scripts **in order** for consistent results.
- The output of each step is used as the input for the next stage.

## 🛠️ Setup
```bash
pip install -r requirements.txt
```


## 🚀 Execution Order

Run the scripts in the following order to ensure the pipeline works correctly:

### 1. Merge Dataset

```bash
python notebook/merge-gw-season/merge_dataset.py
```


### 2. Combine Player Information
```bash
python notebook/merge-gw-season/combine_players_info.py
```

### 3. Predict xPoints
Run the following five scripts to predict xPoints based on player positions:
```bash
python notebook/predict-xpoints/predict_xpoints_general.py
python notebook/predict-xpoints/predict_xpoints_goalkeeper.py
python notebook/predict-xpoints/predict_xpoints_defender.py
python notebook/predict-xpoints/predict_xpoints_midfielder.py
python notebook/predict-xpoints/predict_xpoints_forward.py
```

### 4. Predict Starting Lineup
Finally, run the two scripts below to generate starting lineup predictions:
```bash
python notebook/starting-lineup/predict_lineup_general.py
python notebook/starting-lineup/predict_lineup_per_position.py
```

