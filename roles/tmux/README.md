# tmux and iTerm2

iTerm2 should be configured to work together with `tmux`, sending the proper keys.

- Configure hex codes with `hexdump`, as suggested by this article:
  [How to set up iTerm2 profile to override key mappings to trigger analogue tmux actions](https://www.freecodecamp.org/news/tmux-in-practice-iterm2-and-tmux-integration-7fb0991c6c01/)
- [Keys to move words back/forward](https://stackoverflow.com/questions/81272/how-to-move-the-cursor-word-by-word-in-the-os-x-terminal)
  Configure iTerm2 to send escape codes plus the letter:
  - Word back: `Esc+B`
  - Word forward: `Esc+F`

# hexdump

- Run it outside `tmux`, otherwise `Ctrl` keys might be intercepted
- Either open a new iTerm2 tab or detach `tmux` with `Ctrl-a` (prefix) + d
- Run `hexdump -n <number>` to limit the number of keystrokes needed to display hex codes.
- Keep pressing ENTER (`0a`) or space (`20`) until `hexdump` shows some code.
  Then ignore these codes you know.

```
$ hexdump -n 8
^A^B





0000000 01 02 0a 0a 0a 0a 0a 0a
0000008
$ hexdump -n 8
^A^B
0000000 01 02 20 20 20 20 20 20
0000008
```
