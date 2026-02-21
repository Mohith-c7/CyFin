# Installation Guide

## The Error You're Seeing

The error `ModuleNotFoundError: No module named 'yfinance'` means the required Python packages haven't been installed yet.

## Fix: Install Dependencies

Run this command in your terminal:

```cmd
pip install -r requirements.txt
```

This will install all required packages:
- pandas
- numpy
- yfinance
- scikit-learn
- streamlit
- plotly

## Step-by-Step Installation

### 1. Make sure your virtual environment is activated

You should see `(venv)` at the start of your command prompt. If not:

```cmd
venv\Scripts\activate
```

### 2. Install all dependencies

```cmd
pip install -r requirements.txt
```

This may take 1-2 minutes to download and install everything.

### 3. Verify installation

```cmd
python check_setup.py
```

This will check if all packages are installed correctly.

### 4. Run the system

Once all packages show ✓, you can run:

```cmd
python main_stream_test.py
```

## Troubleshooting

### "pip is not recognized"

Make sure Python is installed and added to PATH. Try:
```cmd
python -m pip install -r requirements.txt
```

### "Permission denied" or "Access denied"

Run your terminal as Administrator, or use:
```cmd
pip install --user -r requirements.txt
```

### Slow installation

Some packages are large. Be patient, it can take a few minutes.

### Still having issues?

Install packages one by one:
```cmd
pip install pandas
pip install numpy
pip install yfinance
pip install scikit-learn
pip install streamlit
pip install plotly
```

## After Installation

Once installed, you can run:

1. **Check setup**: `python check_setup.py`
2. **Test stream**: `python main_stream_test.py`
3. **Full demo**: `python main_system_demo.py`
4. **Dashboard**: `streamlit run dashboard/dashboard_app.py`

## Quick Test

To verify everything works without waiting for the full demo:

```cmd
python check_setup.py
```

All items should show ✓ (checkmark).
