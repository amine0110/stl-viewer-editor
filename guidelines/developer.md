# Developer Guidelines
This guidelines is for developers who can run the app using code.

## Clone the repository
```bash
git clone https://github.com/amine0110/stl-viewer-editor
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run the app
```bash
python main.py
```

## Change the background color
```python
self.renderer.SetBackground(0, 0, 0) # values are between 0 and 1, where 0 is black and 1 is white
```