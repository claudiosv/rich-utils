# Records scripts/run_all_demos.py into assets/demo.gif.
# Run from the repo root: vhs scripts/demo.tape

Output assets/demo.gif

Require uv

Set Shell "bash"
Set FontSize 16
Set Width 1000
Set Height 680
Set Padding 15
Set Theme "Dracula"

Hide
Type "clear"
Enter
Show

Type "uv run python scripts/run_all_demos.py"
Enter
Sleep 13s
