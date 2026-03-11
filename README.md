
Requirements: Python 3.10+

## 1. Clone the repo
git clone https://github.com/SetuG/object-detection.git

cd object-detection

## 2. Create and activate virtual environment
python -m venv venv

venv\Scripts\activate        # Windows

source venv/bin/activate     # Mac/Linux

## 3. Install dependencies
pip install -r requirements.txt

## 4. Start the server
uvicorn app:app --reload --port 8000
