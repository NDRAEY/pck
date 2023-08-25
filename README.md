# pck
.pck sound extractor written in pure Python (based on open-source BMS scripts)

`pck.py` does not need any dependcies, it uses built-in modules.

It creates two folders: `sounds` and `banks`, then extracts sound files into these folders.

# Usage

```
python pck.py MyFile.pck
```

Result: new folders named `sounds` and `banks` that contain extracted files.

NOTE: If you prefer older Python versions (<3.9), you should remove type annotations in code.
