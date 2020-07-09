# ableton-presence
## This project is no longer recieving updates, however it will still recieve support for the time being.

Uses pypresence to display what you're working on in Ableton to everyone on Discord.

Use FL Studio? Check out [fl-presence](https://github.com/Discord-ian/fl-presence)

## Example

![example](https://pbs.twimg.com/media/EMYPx8-XkAAQZWG?format=png&name=small)

## Adding to Startup

To add to startup, hit the Windows Key + R at the same time

Enter 

```
shell:startup
```

and put AbletonPresence.exe in there.

You'll also need to do this for updates

## Running from source

Make sure you're using Python 3.5 or greater.

Navigate to the src folder and install all requirements with
```python
python -m pip install -U -r requirements.txt
```

Then, you can eithr run the program with 
```
python presence.py
```

or by opening the batch file